"""
Call Orchestrator — the central component that connects all parts.

Flow per call:
  Incoming audio -> STT -> State Machine + LLM -> Yclients API -> TTS -> Outgoing audio
"""

import asyncio
import json
import logging
from datetime import date
from typing import AsyncGenerator, Optional

from app.core.state_machine import StateMachine, SessionContext, State, Intent
from app.llm.agent import DialogAgent
from app.booking.yclients import YclientsClient
from app.stt.yandex_stt import YandexSTTStream
from app.tts.fish_tts import FishTTSStream
from app.tts.yandex_tts import YandexTTSStream
from app.telephony.sip_handler import IncomingCall
from config.settings import settings

logger = logging.getLogger(__name__)


class CallOrchestrator:
    """Orchestrates phone calls. Creates per-call STT/TTS streams."""

    def __init__(self, salon_config: dict):
        self.salon_config = salon_config
        self.agent = DialogAgent(salon_config)
        self.yclients = YclientsClient()

        # Active sessions: call_id -> (session, state_machine)
        self._sessions: dict[str, tuple[SessionContext, StateMachine]] = {}

        # Audio queues: call_id -> asyncio.Queue for incoming audio chunks
        self._audio_queues: dict[str, asyncio.Queue] = {}

        # TTS output callback: call_id -> callback to send audio to caller
        self._audio_senders: dict[str, callable] = {}

        # Event fired when WebSocket registers its send_audio
        self._ws_ready: dict[str, asyncio.Event] = {}

        # Track running tasks for graceful shutdown
        self._tasks: dict[str, asyncio.Task] = {}

    async def start(self):
        logger.info("Orchestrator started")

    async def stop(self):
        for task in self._tasks.values():
            task.cancel()
        await self.yclients.close()
        logger.info("Orchestrator stopped")

    async def handle_new_call(self, call: IncomingCall) -> str:
        """Register a new incoming call. Waits for WebSocket before greeting."""
        session = SessionContext(
            call_id=call.call_id,
            caller_phone=call.caller_number,
        )
        sm = StateMachine(session)

        self._sessions[call.call_id] = (session, sm)
        self._audio_queues[call.call_id] = asyncio.Queue()
        self._ws_ready[call.call_id] = asyncio.Event()

        task = asyncio.create_task(self._process_call(call.call_id))
        self._tasks[call.call_id] = task
        task.add_done_callback(lambda t: self._tasks.pop(call.call_id, None))

        logger.info(f"New call: {call.call_id} from {call.caller_number}")
        return call.call_id

    async def register_audio_sender(self, call_id: str, send_fn: callable):
        """Called by WebSocket endpoint when connection is established."""
        self._audio_senders[call_id] = send_fn
        event = self._ws_ready.get(call_id)
        if event:
            event.set()

    async def feed_audio(self, call_id: str, chunk: bytes):
        queue = self._audio_queues.get(call_id)
        if queue:
            await queue.put(chunk)

    async def end_call(self, call_id: str):
        queue = self._audio_queues.get(call_id)
        if queue:
            await queue.put(None)  # signal end to STT

        task = self._tasks.get(call_id)
        if task and not task.done():
            # Let the task finish gracefully via the None sentinel
            try:
                await asyncio.wait_for(task, timeout=5.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                task.cancel()

        self._sessions.pop(call_id, None)
        self._audio_queues.pop(call_id, None)
        self._audio_senders.pop(call_id, None)
        self._ws_ready.pop(call_id, None)
        logger.info(f"Call ended: {call_id}")

    async def _process_call(self, call_id: str):
        """Main call processing loop."""
        session, sm = self._sessions.get(call_id, (None, None))
        if not session:
            return

        # Create per-call STT and TTS streams
        stt = YandexSTTStream()
        if settings.tts_provider == "fish":
            tts = FishTTSStream()
        else:
            tts = YandexTTSStream()

        try:
            await stt.connect()
            await tts.connect()

            # Wait for WebSocket to be ready (max 10 sec)
            event = self._ws_ready.get(call_id)
            if event:
                try:
                    await asyncio.wait_for(event.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    logger.error(f"[{call_id}] WebSocket not connected in time")
                    return

            # Look up client by phone number before greeting
            if session.caller_phone:
                client_info = await self.yclients.lookup_client(session.caller_phone)
                if client_info and client_info.get("name"):
                    session.client_name = client_info["name"]
                    session.client_info = client_info
                    self.agent.set_client_info(client_info)
                    logger.info(
                        f"[{call_id}] Known client: {client_info['name']} "
                        f"({client_info.get('visits_count', 0)} visits, "
                        f"fav: {client_info.get('favorite_service')})"
                    )

            # Send greeting
            greeting = await self.agent.generate_greeting(session)
            await self._speak(call_id, tts, greeting)

            # Main dialog loop
            async for user_text in self._listen(call_id, stt):
                if sm.is_terminal():
                    break

                reply, intent, data = await self.agent.process_message(session, user_text)
                self._update_session_data(session, data)

                # Handle function calls
                fn_calls = data.get("_function_calls", [])
                for fn_call in fn_calls:
                    fn_result = await self._execute_function(session, fn_call)
                    # Add tool result to LLM context
                    session.messages.append({
                        "role": "tool",
                        "tool_call_id": fn_call["tool_call_id"],
                        "content": json.dumps(fn_result or {"status": "ok"}),
                    })
                    if isinstance(fn_result, dict) and fn_result.get("reply"):
                        reply = fn_result["reply"]

                sm.transition(intent)

                if reply:
                    await self._speak(call_id, tts, reply)

                if session.state == State.FALLBACK:
                    await self._speak(
                        call_id, tts,
                        "Одну секунду, соединяю с администратором."
                    )
                    break

        except asyncio.CancelledError:
            logger.info(f"[{call_id}] Call task cancelled")
        except Exception as e:
            logger.error(f"[{call_id}] Error: {e}", exc_info=True)
            try:
                await self._speak(
                    call_id, tts,
                    "Извините, произошла техническая ошибка. Соединяю с администратором."
                )
            except Exception:
                pass
        finally:
            await stt.close()
            await tts.close()

    async def _listen(self, call_id: str, stt: YandexSTTStream) -> AsyncGenerator[str, None]:
        queue = self._audio_queues.get(call_id)
        if not queue:
            return

        async def audio_generator():
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                yield chunk

        async for text in stt.recognize_stream(audio_generator()):
            if text.strip():
                logger.info(f"[{call_id}] Client: {text}")
                yield text

    async def _speak(self, call_id: str, tts: YandexTTSStream, text: str):
        if not text:
            return
        send_audio = self._audio_senders.get(call_id)
        if not send_audio:
            return
        logger.info(f"[{call_id}] Agent: {text}")
        async for audio_chunk in tts.synthesize_stream(text):
            await send_audio(audio_chunk)

    async def _execute_function(self, session: SessionContext, fn_call: dict) -> Optional[dict]:
        name = fn_call["name"]
        args = fn_call["arguments"]

        try:
            if name == "check_slots":
                target_date = None
                if args.get("date"):
                    target_date = date.fromisoformat(args["date"])
                slots = await self.yclients.get_available_slots(
                    staff_id=args["staff_id"],
                    service_id=args["service_id"],
                    target_date=target_date,
                )
                session.available_slots = slots
                if slots:
                    slots_text = ", ".join(slots[:3])
                    return {"slots": slots[:3], "reply": f"Свободное время: {slots_text}. Какое удобнее?"}
                return {"slots": [], "reply": "К сожалению, на эту дату нет свободных слотов. Хотите посмотреть другой день?"}

            elif name == "create_booking":
                result = await self.yclients.create_booking(
                    staff_id=args["staff_id"],
                    service_id=args["service_id"],
                    booking_datetime=args["datetime"],
                    client_name=args["client_name"],
                    client_phone=args.get("client_phone", session.caller_phone),
                )
                session.booking_id = result.get("id")
                return {"status": "ok", "booking_id": session.booking_id}

            elif name == "lookup_client":
                phone = args.get("phone", session.caller_phone)
                client_info = await self.yclients.lookup_client(phone)
                if client_info:
                    session.client_name = client_info.get("name", "")
                    session.client_info = client_info
                    return {
                        "status": "ok",
                        "name": client_info.get("name"),
                        "visits_count": client_info.get("visits_count", 0),
                        "favorite_service": client_info.get("favorite_service"),
                        "service_history": client_info.get("service_history", {}),
                    }
                return {"status": "not_found"}

            elif name == "cancel_booking":
                record_id = args.get("record_id") or session.booking_id
                if record_id:
                    await self.yclients.cancel_booking(record_id)
                    return {"status": "ok", "reply": "Запись отменена."}
                return {"status": "error", "reply": "Не удалось найти запись для отмены."}

        except Exception as e:
            logger.error(f"Function {name} failed: {e}")
            return {"status": "error", "reply": "Произошла ошибка при работе с расписанием. Попробуем ещё раз."}

        return None

    def _update_session_data(self, session: SessionContext, data: dict):
        if "service_name" in data:
            session.service_name = data["service_name"]
        if "master_name" in data:
            session.master_name = data["master_name"]
        if "client_name" in data:
            session.client_name = data["client_name"]
        if "preferred_date" in data:
            session.slot_datetime = data["preferred_date"]
        if "preferred_time" in data:
            dt = session.slot_datetime or ""
            session.slot_datetime = f"{dt} {data['preferred_time']}".strip()

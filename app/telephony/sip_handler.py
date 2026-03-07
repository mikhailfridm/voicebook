"""
SIP telephony handler for Zadarma.

Handles incoming calls via Zadarma webhook + WebSocket audio stream.
Zadarma sends audio over WebSocket when configured for real-time streaming.

Docs: https://zadarma.com/ru/support/api/
"""

import asyncio
import logging
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IncomingCall:
    call_id: str
    caller_number: str
    called_number: str


class SIPHandler:
    """
    Manages SIP call lifecycle with Zadarma.

    Flow:
    1. Zadarma sends webhook on incoming call
    2. We accept and get WebSocket URL for audio stream
    3. Audio is streamed bidirectionally (receive client audio, send agent audio)
    """

    def __init__(
        self,
        on_call_start: Optional[Callable[[IncomingCall], Awaitable[None]]] = None,
        on_audio_chunk: Optional[Callable[[str, bytes], Awaitable[None]]] = None,
        on_call_end: Optional[Callable[[str], Awaitable[None]]] = None,
    ):
        self.on_call_start = on_call_start
        self.on_audio_chunk = on_audio_chunk
        self.on_call_end = on_call_end
        self._active_calls: dict[str, dict] = {}

    async def handle_webhook(self, event: str, data: dict) -> dict:
        """
        Handle Zadarma webhook events.

        Events:
          NOTIFY_START — incoming call started
          NOTIFY_INTERNAL — call routed internally
          NOTIFY_ANSWER — call answered
          NOTIFY_END — call ended
        """
        if event == "NOTIFY_START":
            call = IncomingCall(
                call_id=data.get("pbx_call_id", ""),
                caller_number=data.get("caller_id", ""),
                called_number=data.get("called_did", ""),
            )
            self._active_calls[call.call_id] = {"call": call, "active": True}
            logger.info(f"Incoming call: {call.caller_number} -> {call.called_number}")

            if self.on_call_start:
                await self.on_call_start(call)

            return {"status": "ok"}

        elif event == "NOTIFY_END":
            call_id = data.get("pbx_call_id", "")
            if call_id in self._active_calls:
                del self._active_calls[call_id]
            logger.info(f"Call ended: {call_id}")

            if self.on_call_end:
                await self.on_call_end(call_id)

            return {"status": "ok"}

        return {"status": "ok"}

    async def handle_audio_websocket(self, call_id: str, ws):
        """
        Handle bidirectional audio WebSocket for a call.

        Receives client audio chunks and forwards to STT.
        Receives TTS audio and sends to client.
        """
        logger.info(f"Audio WebSocket connected for call {call_id}")

        try:
            async for message in ws:
                if isinstance(message, bytes) and self.on_audio_chunk:
                    await self.on_audio_chunk(call_id, message)
        except Exception as e:
            logger.error(f"Audio WebSocket error for {call_id}: {e}")
        finally:
            logger.info(f"Audio WebSocket closed for {call_id}")

    async def send_audio(self, call_id: str, audio_data: bytes, ws):
        """Send audio data back to the caller via WebSocket."""
        try:
            await ws.send_bytes(audio_data)
        except Exception as e:
            logger.error(f"Failed to send audio for {call_id}: {e}")

    def is_call_active(self, call_id: str) -> bool:
        return call_id in self._active_calls

"""
VoiceBook — FastAPI application entry point.

Endpoints:
  POST /webhook/zadarma    — Zadarma call event webhooks
  WS   /ws/audio/{call_id} — Bidirectional audio stream per call
  GET  /health             — Health check
"""

import hashlib
import hmac
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.orchestrator import CallOrchestrator
from app.telephony.sip_handler import SIPHandler, IncomingCall
from config.settings import settings

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Default salon config — will be loaded from DB/config per client later
DEFAULT_SALON_CONFIG = {
    "name": "Барбершоп",
    "services": ["Мужская стрижка", "Стрижка бороды", "Комплекс стрижка + борода"],
    "masters": ["Денис", "Артур", "Максим"],
    "hours": "10:00–21:00",
}

orchestrator = CallOrchestrator(DEFAULT_SALON_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await orchestrator.start()
    yield
    await orchestrator.stop()


app = FastAPI(title="VoiceBook", version="0.1.0", lifespan=lifespan)


# --- SIP Handler setup ---
sip = SIPHandler(
    on_call_start=lambda call: orchestrator.handle_new_call(call),
    on_audio_chunk=lambda call_id, chunk: orchestrator.feed_audio(call_id, chunk),
    on_call_end=lambda call_id: orchestrator.end_call(call_id),
)


def _verify_zadarma_signature(body: bytes, signature: str) -> bool:
    """Verify Zadarma webhook HMAC signature."""
    if not settings.zadarma_api_secret:
        return True  # skip in dev if no secret configured
    expected = hmac.new(
        settings.zadarma_api_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook/zadarma")
async def zadarma_webhook(request: Request):
    """Handle Zadarma PBX webhook events."""
    body = await request.body()
    signature = request.headers.get("Sign", "")

    if not _verify_zadarma_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = data.get("event", "")
    logger.info(f"Webhook event: {event}")
    result = await sip.handle_webhook(event, data)
    return JSONResponse(result)


@app.websocket("/ws/audio/{call_id}")
async def audio_websocket(websocket: WebSocket, call_id: str):
    """Bidirectional audio WebSocket for a call."""
    await websocket.accept()
    logger.info(f"WebSocket connected: {call_id}")

    async def send_audio(audio_data: bytes):
        await websocket.send_bytes(audio_data)

    # Register sender and signal orchestrator that WS is ready
    await orchestrator.register_audio_sender(call_id, send_audio)

    try:
        while True:
            data = await websocket.receive_bytes()
            await orchestrator.feed_audio(call_id, data)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {call_id}")
        await orchestrator.end_call(call_id)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level,
    )

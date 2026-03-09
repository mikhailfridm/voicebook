"""
Chatterbox TTS client with streaming support.

Self-hosted, MIT-licensed TTS with voice cloning.
Uses OpenAI-compatible API (travisvn/chatterbox-tts-api).
"""

import logging
from typing import AsyncGenerator, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class ChatterboxTTSStream:
    """Streaming TTS client using Chatterbox TTS API server."""

    def __init__(
        self,
        base_url: str = "",
        voice: str = "",
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
    ):
        self.base_url = (base_url or settings.chatterbox_tts_base_url).rstrip("/")
        self.voice = voice or settings.chatterbox_tts_voice
        self.exaggeration = exaggeration
        self.cfg_weight = cfg_weight
        self.temperature = temperature
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self):
        """Create HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Chatterbox TTS connected to {self.base_url}")

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to speech and yield audio chunks.

        Args:
            text: Text to synthesize

        Yields:
            Raw audio bytes (WAV)
        """
        if not self._client:
            logger.error("Chatterbox TTS not connected")
            return

        payload = {
            "model": "chatterbox",
            "input": text,
            "voice": self.voice,
            "response_format": "wav",
            "exaggeration": self.exaggeration,
            "cfg_weight": self.cfg_weight,
            "temperature": self.temperature,
        }

        try:
            async with self._client.stream(
                "POST",
                f"{self.base_url}/v1/audio/speech/stream",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    if chunk:
                        yield chunk
        except httpx.HTTPStatusError as e:
            logger.error(f"Chatterbox TTS HTTP error: {e.response.status_code} {e.response.text}")
        except httpx.ConnectError:
            logger.error(f"Chatterbox TTS connection failed: {self.base_url}")
        except Exception as e:
            logger.error(f"Chatterbox TTS error: {e}", exc_info=True)

    async def close(self):
        if self._client:
            await self._client.aclose()
            logger.info("Chatterbox TTS disconnected")

"""
Fish Speech TTS client with streaming support.

Self-hosted, open-source TTS with voice cloning.
API docs: https://docs.fish.audio/developer-guide/self-hosting/running-inference
"""

import logging
from typing import AsyncGenerator, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class FishTTSStream:
    """Streaming TTS client using Fish Speech API server."""

    def __init__(
        self,
        base_url: str = "",
        reference_id: str = "",
        reference_audio: Optional[bytes] = None,
        reference_text: str = "",
        sample_rate: int = 8000,
    ):
        self.base_url = (base_url or settings.fish_tts_base_url).rstrip("/")
        self.reference_id = reference_id or settings.fish_tts_reference_id
        self.reference_audio = reference_audio
        self.reference_text = reference_text
        self.sample_rate = sample_rate
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self):
        """Create HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Fish TTS connected to {self.base_url}")

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to speech and yield audio chunks.

        Args:
            text: Text to synthesize

        Yields:
            Raw audio bytes (WAV/PCM)
        """
        if not self._client:
            logger.error("Fish TTS not connected")
            return

        payload = {
            "text": text,
            "format": "pcm",
            "latency": "balanced",
            "temperature": 0.7,
            "top_p": 0.7,
            "normalize": True,
            "prosody": {
                "speed": 1.0,
            },
        }

        if self.reference_id:
            payload["reference_id"] = self.reference_id
        elif self.reference_audio:
            import base64
            payload["references"] = [{
                "audio": base64.b64encode(self.reference_audio).decode(),
                "text": self.reference_text,
            }]

        try:
            async with self._client.stream(
                "POST",
                f"{self.base_url}/v1/tts",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    if chunk:
                        yield chunk
        except httpx.HTTPStatusError as e:
            logger.error(f"Fish TTS HTTP error: {e.response.status_code} {e.response.text}")
        except httpx.ConnectError:
            logger.error(f"Fish TTS connection failed: {self.base_url}")
        except Exception as e:
            logger.error(f"Fish TTS error: {e}", exc_info=True)

    async def close(self):
        if self._client:
            await self._client.aclose()
            logger.info("Fish TTS disconnected")

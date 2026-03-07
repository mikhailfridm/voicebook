"""
Yandex SpeechKit TTS client with streaming support.

Docs: https://cloud.yandex.ru/docs/speechkit/tts/api/tts-v3
"""

import logging
from typing import AsyncGenerator, Optional

import grpc

from config.settings import settings

logger = logging.getLogger(__name__)

TTS_ENDPOINT = "tts.api.cloud.yandex.net:443"

try:
    from yandex.cloud.ai.tts.v3 import tts_pb2, tts_service_pb2_grpc
    TTS_PROTO_AVAILABLE = True
except ImportError:
    TTS_PROTO_AVAILABLE = False
    logger.warning(
        "Yandex TTS proto files not found. "
        "Run `make proto` to generate them."
    )


class YandexTTSStream:
    """Streaming TTS client using Yandex SpeechKit v3 API."""

    def __init__(
        self,
        api_key: str = "",
        folder_id: str = "",
        voice: str = "alexander",
        sample_rate: int = 8000,
    ):
        self.api_key = api_key or settings.yandex_cloud_api_key
        self.folder_id = folder_id or settings.yandex_cloud_folder_id
        self.voice = voice
        self.sample_rate = sample_rate
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub = None

    async def connect(self):
        """Establish gRPC channel."""
        creds = grpc.ssl_channel_credentials()
        self._channel = grpc.aio.secure_channel(TTS_ENDPOINT, creds)

        if TTS_PROTO_AVAILABLE:
            self._stub = tts_service_pb2_grpc.SynthesizerStub(self._channel)
        logger.info("Yandex TTS connected")

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to speech and yield audio chunks (PCM 8kHz).

        Args:
            text: Text to synthesize

        Yields:
            Raw audio bytes (LINEAR16 PCM)
        """
        if not TTS_PROTO_AVAILABLE:
            logger.error("Proto files not available, cannot run TTS")
            return

        request = tts_pb2.UtteranceSynthesisRequest(
            text=text,
            output_audio_spec=tts_pb2.AudioFormatOptions(
                raw_audio=tts_pb2.RawAudio(
                    audio_encoding=tts_pb2.RawAudio.LINEAR16_PCM,
                    sample_rate_hertz=self.sample_rate,
                    audio_channel_count=1,
                )
            ),
            hints=[
                tts_pb2.Hints(voice=self.voice),
                tts_pb2.Hints(speed=1.1),
            ],
            loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS,
        )

        metadata = [
            ("authorization", f"Api-Key {self.api_key}"),
            ("x-folder-id", self.folder_id),
        ]

        responses = self._stub.UtteranceSynthesis(
            request,
            metadata=metadata,
        )

        async for response in responses:
            yield response.audio_chunk.data

    async def close(self):
        if self._channel:
            await self._channel.close()
            logger.info("Yandex TTS disconnected")

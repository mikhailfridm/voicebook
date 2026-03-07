"""
Yandex SpeechKit Streaming STT client.

Uses gRPC streaming API for real-time speech recognition.
Docs: https://cloud.yandex.ru/docs/speechkit/stt/api/streaming-api
"""

import asyncio
import logging
from typing import AsyncGenerator, Callable, Optional

import grpc

from config.settings import settings

logger = logging.getLogger(__name__)

# Yandex SpeechKit gRPC endpoint
STT_ENDPOINT = "stt.api.cloud.yandex.net:443"

# Proto imports will be generated from Yandex proto files.
# For now, we define the interface and will add proto compilation in setup.
# See: https://github.com/yandex-cloud/cloudapi

try:
    from yandex.cloud.ai.stt.v3 import stt_pb2, stt_service_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    logger.warning(
        "Yandex SpeechKit proto files not found. "
        "Run `make proto` to generate them."
    )


class YandexSTTStream:
    """Streaming STT client using Yandex SpeechKit v3 API."""

    def __init__(
        self,
        api_key: str = "",
        folder_id: str = "",
        language_code: str = "ru-RU",
        sample_rate: int = 8000,
    ):
        self.api_key = api_key or settings.yandex_cloud_api_key
        self.folder_id = folder_id or settings.yandex_cloud_folder_id
        self.language_code = language_code
        self.sample_rate = sample_rate
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub = None

    async def connect(self):
        """Establish gRPC channel."""
        creds = grpc.ssl_channel_credentials()
        self._channel = grpc.aio.secure_channel(STT_ENDPOINT, creds)

        if PROTO_AVAILABLE:
            self._stub = stt_service_pb2_grpc.RecognizerStub(self._channel)
        logger.info("Yandex STT connected")

    async def recognize_stream(
        self,
        audio_chunks: AsyncGenerator[bytes, None],
        on_partial: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream audio chunks and yield recognized text.

        Args:
            audio_chunks: Async generator yielding raw PCM audio bytes
            on_partial: Callback for partial (intermediate) results
            on_final: Callback for final results

        Yields:
            Final recognized text segments
        """
        if not PROTO_AVAILABLE:
            logger.error("Proto files not available, cannot run STT")
            return

        async def request_iterator():
            # First message: recognition config
            recognize_options = stt_pb2.StreamingOptions(
                recognition_model=stt_pb2.RecognitionModelOptions(
                    language_restriction=stt_pb2.LanguageRestrictionOptions(
                        restriction_type=stt_pb2.LanguageRestrictionOptions.WHITELIST,
                        language_code=[self.language_code],
                    ),
                    audio_format=stt_pb2.AudioFormatOptions(
                        raw_audio=stt_pb2.RawAudio(
                            audio_encoding=stt_pb2.RawAudio.LINEAR16_PCM,
                            sample_rate_hertz=self.sample_rate,
                            audio_channel_count=1,
                        )
                    ),
                    text_normalization=stt_pb2.TextNormalizationOptions(
                        text_normalization=stt_pb2.TextNormalizationOptions.TEXT_NORMALIZATION_ENABLED,
                    ),
                ),
            )

            yield stt_pb2.StreamingRequest(
                session_options=recognize_options
            )

            # Stream audio chunks
            async for chunk in audio_chunks:
                yield stt_pb2.StreamingRequest(
                    chunk=stt_pb2.AudioChunk(data=chunk)
                )

        metadata = [
            ("authorization", f"Api-Key {self.api_key}"),
            ("x-folder-id", self.folder_id),
        ]

        responses = self._stub.RecognizeStreaming(
            request_iterator(),
            metadata=metadata,
        )

        async for response in responses:
            event_type = response.WhichOneof("Event")

            if event_type == "partial":
                text = response.partial.alternatives[0].text if response.partial.alternatives else ""
                if text and on_partial:
                    on_partial(text)

            elif event_type == "final":
                text = response.final.alternatives[0].text if response.final.alternatives else ""
                if text:
                    if on_final:
                        on_final(text)
                    yield text

    async def close(self):
        if self._channel:
            await self._channel.close()
            logger.info("Yandex STT disconnected")

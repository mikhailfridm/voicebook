#!/usr/bin/env python3
"""Bark TTS server — natural speech with pauses and hesitations."""
import io
import numpy as np
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from scipy.io.wavfile import write as wav_write

app = FastAPI(title="Bark TTS")

model_loaded = False


class TTSRequest(BaseModel):
    text: str
    speaker: str = "v2/ru_speaker_5"  # Russian female


def numpy_to_wav_bytes(audio_array, sample_rate):
    """Convert numpy array to WAV bytes."""
    buf = io.BytesIO()
    audio_int16 = (audio_array * 32767).astype(np.int16)
    wav_write(buf, sample_rate, audio_int16)
    buf.seek(0)
    return buf.read()


@app.on_event("startup")
async def startup():
    global model_loaded
    print("Preloading Bark models (first run downloads ~5GB)...")
    from bark import preload_models
    preload_models()
    model_loaded = True
    print("Bark models loaded!")


@app.get("/health")
async def health():
    return {"status": "ok" if model_loaded else "loading"}


@app.post("/api/tts")
async def tts(req: TTSRequest):
    """Generate natural speech from text."""
    from bark import generate_audio, SAMPLE_RATE

    # Bark works best with short sentences
    audio = generate_audio(
        req.text,
        history_prompt=req.speaker,
    )

    wav_bytes = numpy_to_wav_bytes(audio, SAMPLE_RATE)

    return StreamingResponse(
        io.BytesIO(wav_bytes),
        media_type="audio/wav",
    )


@app.post("/v1/audio/speech")
async def tts_openai_compat(req: TTSRequest):
    """OpenAI-compatible endpoint."""
    return await tts(req)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=50000)

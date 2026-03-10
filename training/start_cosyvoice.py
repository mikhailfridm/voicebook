#!/usr/bin/env python3
"""
Minimal CosyVoice 2 API server.
Avoids the complex repo setup — uses pip package directly.
"""
import io
import sys
import subprocess
import os

# Install if needed
try:
    from cosyvoice.cli.cosyvoice import CosyVoice2
except ImportError:
    print("Installing cosyvoice package...")
    subprocess.run([sys.executable, "-m", "pip", "install", "cosyvoice", "modelscope"], check=True)
    from cosyvoice.cli.cosyvoice import CosyVoice2

import torch
import torchaudio
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="CosyVoice 2 TTS")

# Global model
model = None
reference_audio = None
reference_text = None


class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    mode: str = "sft"  # "sft", "zero_shot", "cross_lingual"
    speaker: str = ""
    reference_text: Optional[str] = None


def audio_to_wav_bytes(audio_tensor, sample_rate=22050):
    """Convert audio tensor to WAV bytes."""
    buf = io.BytesIO()
    torchaudio.save(buf, audio_tensor, sample_rate, format="wav")
    buf.seek(0)
    return buf.read()


@app.on_event("startup")
async def startup():
    global model
    print("Loading CosyVoice2-0.5B model...")
    model = CosyVoice2("iic/CosyVoice2-0.5B", load_jit=False, load_trt=False)
    print(f"Model loaded! Available speakers: {model.list_available_spks()}")


@app.get("/health")
async def health():
    return {"status": "ok", "model": "CosyVoice2-0.5B"}


@app.get("/speakers")
async def speakers():
    return {"speakers": model.list_available_spks()}


@app.post("/api/tts")
async def tts(req: TTSRequest):
    """Generate speech from text."""
    global model, reference_audio, reference_text

    audio_chunks = []

    if req.mode == "zero_shot" and reference_audio is not None:
        # Voice cloning mode
        for chunk in model.inference_zero_shot(
            req.text,
            reference_text or "参考文本",
            reference_audio,
            stream=False,
            speed=req.speed,
        ):
            audio_chunks.append(chunk["tts_speech"])
    elif req.mode == "cross_lingual" and reference_audio is not None:
        # Cross-lingual mode (reference voice, different language)
        for chunk in model.inference_cross_lingual(
            req.text,
            reference_audio,
            stream=False,
            speed=req.speed,
        ):
            audio_chunks.append(chunk["tts_speech"])
    else:
        # SFT mode with built-in speaker
        spk = req.speaker or (model.list_available_spks()[0] if model.list_available_spks() else "")
        for chunk in model.inference_sft(
            req.text,
            spk,
            stream=False,
            speed=req.speed,
        ):
            audio_chunks.append(chunk["tts_speech"])

    if not audio_chunks:
        return {"error": "No audio generated"}

    audio = torch.cat(audio_chunks, dim=1)
    wav_bytes = audio_to_wav_bytes(audio, 22050)

    return StreamingResponse(
        io.BytesIO(wav_bytes),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=speech.wav"},
    )


@app.post("/api/set_reference")
async def set_reference(
    text: str = "",
    audio: UploadFile = File(...),
):
    """Upload reference audio for voice cloning."""
    global reference_audio, reference_text
    audio_bytes = await audio.read()

    # Load and resample to 22050
    buf = io.BytesIO(audio_bytes)
    waveform, sr = torchaudio.load(buf)
    if sr != 22050:
        waveform = torchaudio.functional.resample(waveform, sr, 22050)

    reference_audio = waveform
    reference_text = text or ""
    return {"status": "ok", "duration_sec": waveform.shape[1] / 22050}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=50000)

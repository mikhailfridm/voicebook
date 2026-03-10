#!/usr/bin/env python3
"""
Download Russian female voice samples from open sources and upload to Chatterbox.
Generates samples with each voice so user can compare and choose.
"""
import asyncio
import requests
import os
import sys
import subprocess

BASE_URL = "http://localhost:4123"
VOICES_DIR = "/workspace/voice_samples"


async def download_edge_voices():
    """Download multiple Russian female voices from Edge TTS."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"],
                      capture_output=True, check=True)
    except Exception:
        pass

    import edge_tts

    text = (
        "Здравствуйте, добро пожаловать в наш салон. "
        "Меня зовут Анна, я администратор. "
        "Чем могу вам помочь? "
        "Давайте подберём удобное время для записи. "
        "У нас работают отличные мастера. "
        "Свободные слоты есть на сегодня и на завтра."
    )

    voices = [
        ("ru-RU-SvetlanaNeural", "svetlana", "Светлана — спокойный, профессиональный"),
        ("ru-RU-DariyaNeural", "dariya", "Дария — мягкий, тёплый"),
    ]

    results = []
    for voice_id, name, desc in voices:
        mp3_path = os.path.join(VOICES_DIR, f"{name}.mp3")
        wav_path = os.path.join(VOICES_DIR, f"{name}.wav")
        print(f"   Скачиваю {desc}...")
        try:
            communicate = edge_tts.Communicate(text, voice_id, rate="-5%")
            await communicate.save(mp3_path)
            # Convert to WAV 24kHz mono
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-ar", "24000", "-ac", "1", wav_path],
                capture_output=True,
            )
            if os.path.exists(wav_path):
                results.append((name, desc, wav_path))
            elif os.path.exists(mp3_path):
                results.append((name, desc, mp3_path))
        except Exception as e:
            print(f"   Ошибка {name}: {e}")
    return results


def download_silero_sample():
    """Download Silero TTS Russian female sample."""
    print("   Генерирую через Silero TTS...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "silero-tts", "omegaconf"],
            capture_output=True,
        )
    except Exception:
        pass

    script = f"""
import torch
import os

model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v4_ru'
)
model.to('cpu')

text = "Здравствуйте, добро пожаловать в наш салон. Меня зовут Анна, я администратор. Чем могу вам помочь? Давайте подберём удобное время для записи."

speakers = ['aidar', 'baya', 'kseniya', 'xenia']
for speaker in speakers:
    try:
        audio = model.apply_tts(text=text, speaker=speaker, sample_rate=24000)
        path = os.path.join("{VOICES_DIR}", f"silero_{{speaker}}.wav")
        import torchaudio
        torchaudio.save(path, audio.unsqueeze(0), 24000)
        print(f"OK:{{speaker}}:{{path}}")
    except Exception as e:
        print(f"FAIL:{{speaker}}:{{e}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=120,
    )

    results = []
    descs = {
        "baya": "Baya (Silero) — молодой женский, мягкий",
        "kseniya": "Ксения (Silero) — женский, спокойный",
        "xenia": "Xenia (Silero) — женский, профессиональный",
    }
    for line in result.stdout.strip().split("\n"):
        if line.startswith("OK:"):
            _, speaker, path = line.split(":", 2)
            if speaker in descs:
                results.append((f"silero_{speaker}", descs[speaker], path))

    if result.stderr and not results:
        print(f"   Silero ошибка: {result.stderr[:200]}")

    return results


def delete_voice(name):
    """Delete voice if exists."""
    try:
        requests.delete(f"{BASE_URL}/voices/{name}", timeout=5)
    except Exception:
        pass


def upload_and_test(name, desc, filepath):
    """Upload voice to Chatterbox and generate test phrase."""
    print(f"\n--- {desc} ---")

    # Upload
    delete_voice(name)
    ext = os.path.splitext(filepath)[1]
    content_type = "audio/wav" if ext == ".wav" else "audio/mpeg"

    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/voices",
            files={"voice_file": (f"{name}{ext}", f, content_type)},
            data={"voice_name": name, "language": "ru"},
            timeout=30,
        )

    if resp.status_code not in (200, 201):
        print(f"   Ошибка загрузки: {resp.status_code} {resp.text[:100]}")
        return

    print(f"   Загружен: {name} (language=ru)")

    # Generate test phrase
    test_text = "Здравствуйте! Добро пожаловать. Чем могу вам помочь? Давайте подберём удобное время."
    out_path = f"/workspace/voice_test_{name}.wav"

    resp = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        json={
            "input": test_text,
            "voice": name,
            "response_format": "wav",
            "exaggeration": 0.3,
            "cfg_weight": 0.5,
            "temperature": 0.5,
        },
        timeout=120,
    )
    if resp.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(resp.content)
        size_kb = len(resp.content) / 1024
        print(f"   Тест: {out_path} ({size_kb:.0f} KB)")
    else:
        print(f"   Ошибка синтеза: {resp.status_code}")


def main():
    os.makedirs(VOICES_DIR, exist_ok=True)

    print("=== Скачиваем русские женские голоса ===\n")

    all_voices = []

    # 1. Edge TTS voices
    print("1. Edge TTS (Microsoft)...")
    edge_voices = asyncio.run(download_edge_voices())
    all_voices.extend(edge_voices)
    print(f"   Скачано: {len(edge_voices)} голосов")

    # 2. Silero TTS voices
    print("\n2. Silero TTS (русские голоса)...")
    silero_voices = download_silero_sample()
    all_voices.extend(silero_voices)
    print(f"   Скачано: {len(silero_voices)} голосов")

    if not all_voices:
        print("\nНе удалось скачать ни одного голоса!")
        sys.exit(1)

    # Upload and test each
    print(f"\n=== Загружаем {len(all_voices)} голосов в Chatterbox и тестируем ===")

    for name, desc, filepath in all_voices:
        upload_and_test(name, desc, filepath)

    # Summary
    print(f"\n{'='*60}")
    print("=== ИТОГО — послушай и выбери: ===")
    print(f"{'='*60}")
    for name, desc, _ in all_voices:
        print(f"  /workspace/voice_test_{name}.wav  —  {desc}")
    print(f"\nОбразцы голосов: {VOICES_DIR}/")
    print("Скачай файлы voice_test_*.wav и послушай!")


if __name__ == "__main__":
    main()

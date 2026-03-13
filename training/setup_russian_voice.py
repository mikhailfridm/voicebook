#!/usr/bin/env python3
"""
Upload a high-quality Russian voice to Chatterbox TTS.

Uses Edge TTS (Microsoft) to generate a natural Russian reference sample,
then uploads it to Chatterbox with language=ru for voice cloning.
"""
import asyncio
import requests
import os
import sys
import subprocess

BASE_URL = "http://localhost:4123"
SAMPLE_PATH = "/workspace/russian_voice_sample.wav"
SAMPLE_MP3 = "/workspace/russian_voice_sample.mp3"


async def generate_edge_sample():
    """Generate high-quality Russian sample via Edge TTS."""
    import edge_tts

    text = (
        "Здравствуйте, добро пожаловать в наш салон. "
        "Меня зовут Анна, я администратор. Чем могу вам помочь? "
        "Давайте подберём удобное время для записи. "
        "У нас работают отличные мастера. "
        "Свободные слоты есть на сегодня и на завтра. "
        "Стрижка занимает примерно сорок минут. "
        "Подскажите, какой день вам удобен?"
    )

    # Russian female voices from Edge TTS
    voices = [
        "ru-RU-SvetlanaNeural",  # Female, natural
        "ru-RU-DariyaNeural",     # Female, warm
    ]

    for voice in voices:
        print(f"   Пробуем голос: {voice}...")
        try:
            communicate = edge_tts.Communicate(text, voice, rate="-5%")
            await communicate.save(SAMPLE_MP3)
            if os.path.exists(SAMPLE_MP3):
                # Convert to WAV
                subprocess.run(
                    ["ffmpeg", "-y", "-i", SAMPLE_MP3, "-ar", "24000", "-ac", "1", SAMPLE_PATH],
                    capture_output=True,
                )
                if os.path.exists(SAMPLE_PATH):
                    size_kb = os.path.getsize(SAMPLE_PATH) / 1024
                    print(f"   Создан: {SAMPLE_PATH} ({size_kb:.0f} KB)")
                    return True
                # If no ffmpeg, use mp3 directly
                print("   ffmpeg не найден, используем mp3...")
                return True
        except Exception as e:
            print(f"   Ошибка с {voice}: {e}")
            continue

    return False


def delete_old_voice(voice_name):
    """Delete existing voice if present."""
    try:
        resp = requests.delete(f"{BASE_URL}/voices/{voice_name}", timeout=10)
        if resp.status_code == 200:
            print(f"   Удалён старый голос: {voice_name}")
    except Exception:
        pass


def upload_voice(voice_name, language="ru"):
    """Upload voice with language tag."""
    print(f"\n2. Загружаем голос '{voice_name}' с language={language}...")

    # Delete old version first
    delete_old_voice(voice_name)

    # Determine which file to upload
    upload_path = SAMPLE_PATH if os.path.exists(SAMPLE_PATH) else SAMPLE_MP3
    content_type = "audio/wav" if upload_path.endswith(".wav") else "audio/mpeg"

    with open(upload_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/voices",
            files={"voice_file": (os.path.basename(upload_path), f, content_type)},
            data={"voice_name": voice_name, "language": language},
            timeout=30,
        )
    print(f"   Статус: {resp.status_code}")
    try:
        print(f"   Ответ: {resp.json()}")
    except Exception:
        print(f"   Ответ: {resp.text[:200]}")
    return resp.status_code in (200, 201)


def test_russian(voice_name):
    """Test Russian synthesis."""
    print(f"\n3. Тест синтеза с голосом '{voice_name}'...")
    phrases = [
        "Здравствуйте! Добро пожаловать в наш салон. Чем могу помочь?",
        "Конечно, давайте запишем вас на стрижку. На какой день удобно?",
        "Свободное время: десять тридцать, двенадцать ноль ноль и четырнадцать тридцать. Какое удобнее?",
    ]

    for i, text in enumerate(phrases, 1):
        out_path = f"/workspace/test_russian_{i}.wav"
        resp = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json={
                "input": text,
                "voice": voice_name,
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
            print(f"   [{i}] OK — {size_kb:.1f} KB — {out_path}")
        else:
            print(f"   [{i}] Ошибка: {resp.status_code} {resp.text[:200]}")


def main():
    voice_name = "russian_anna"

    print("=== Настройка русского голоса для Chatterbox ===\n")

    # Step 1: Generate reference sample
    print("1. Генерация качественного русского образца (Edge TTS)...")

    # Remove old sample to force regeneration
    for f in [SAMPLE_PATH, SAMPLE_MP3]:
        if os.path.exists(f):
            os.remove(f)

    ok = asyncio.run(generate_edge_sample())
    if not ok:
        print("   Не удалось создать образец!")
        sys.exit(1)

    # Step 2: Upload
    upload_voice(voice_name)

    # Step 3: Test
    test_russian(voice_name)

    print(f"\n=== Готово! ===")
    print(f"Голос: '{voice_name}' (language=ru)")
    print(f"Тестовые файлы: /workspace/test_russian_1..3.wav")


if __name__ == "__main__":
    main()

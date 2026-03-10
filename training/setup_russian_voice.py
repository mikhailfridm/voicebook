#!/usr/bin/env python3
"""
Upload a Russian voice to Chatterbox TTS and test it.

Steps:
1. Generate a Russian voice sample using the default model (or use provided file)
2. Upload it with language=ru
3. Test synthesis with the Russian voice
"""
import requests
import subprocess
import os
import sys

BASE_URL = "http://localhost:4123"
VOICE_NAME = "russian_admin"
SAMPLE_PATH = "/workspace/russian_voice_sample.wav"


def generate_sample():
    """Generate a Russian voice sample using espeak if no file exists."""
    if os.path.exists(SAMPLE_PATH):
        print(f"   Файл уже есть: {SAMPLE_PATH}")
        return True

    print("   Создаём образец через Chatterbox...")
    # Use Chatterbox itself to generate a sample, then re-upload with language
    resp = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        json={
            "input": text,
            "voice": "default",
            "response_format": "wav",
        },
        timeout=120,
    )
    if resp.status_code == 200:
        with open(SAMPLE_PATH, "wb") as f:
            f.write(resp.content)
        print(f"   Создан через Chatterbox: {SAMPLE_PATH}")
        return True

    print("   Не удалось создать образец!")
    return False


def upload_voice():
    """Upload voice with Russian language tag."""
    print(f"\n2. Загружаем голос '{VOICE_NAME}' с language=ru...")
    with open(SAMPLE_PATH, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/voices",
            files={"voice_file": ("sample.wav", f, "audio/wav")},
            data={"voice_name": VOICE_NAME, "language": "ru"},
            timeout=30,
        )
    print(f"   Статус: {resp.status_code}")
    print(f"   Ответ: {resp.json()}")
    return resp.status_code == 200


def list_voices():
    """List all voices."""
    print("\n3. Список голосов...")
    resp = requests.get(f"{BASE_URL}/voices", timeout=10)
    if resp.status_code == 200:
        print(f"   Голоса: {resp.json()}")
    else:
        print(f"   Ошибка: {resp.status_code} {resp.text[:200]}")


def test_russian():
    """Test Russian synthesis with uploaded voice."""
    print(f"\n4. Тест синтеза с голосом '{VOICE_NAME}'...")
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
                "voice": VOICE_NAME,
                "response_format": "wav",
                "exaggeration": 0.35,
                "cfg_weight": 0.5,
                "temperature": 0.6,
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


if __name__ == "__main__":
    print("=== Настройка русского голоса для Chatterbox ===\n")
    print("1. Подготовка образца голоса...")

    if not generate_sample():
        sys.exit(1)

    upload_voice()
    list_voices()
    test_russian()

    print("\n=== Готово! ===")
    print(f"Используйте voice='{VOICE_NAME}' в запросах к API")

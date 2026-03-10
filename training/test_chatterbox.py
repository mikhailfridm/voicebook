#!/usr/bin/env python3
"""Test Chatterbox TTS server."""
import requests
import os
import sys

BASE_URL = "http://localhost:4123"

def test_health():
    """Check if server is running."""
    print("1. Проверка сервера...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Статус: {r.status_code}")
        return True
    except Exception as e:
        print(f"   Сервер не доступен: {e}")
        return False

def test_voices():
    """List available voices."""
    print("\n2. Доступные голоса...")
    try:
        r = requests.get(f"{BASE_URL}/v1/audio/voices", timeout=5)
        voices = r.json()
        print(f"   Голоса: {voices}")
        return voices
    except Exception as e:
        print(f"   Ошибка: {e}")
        return []

def test_synthesize():
    """Test speech synthesis."""
    print("\n3. Синтез речи...")
    payload = {
        "input": "Здравствуйте! Добро пожаловать в наш салон. Чем могу помочь?",
        "voice": "default",
        "response_format": "wav",
        "exaggeration": 0.35,
        "cfg_weight": 0.5,
        "temperature": 0.6,
    }
    try:
        r = requests.post(
            f"{BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=120,
        )
        if r.status_code == 200:
            out_path = "/workspace/test_chatterbox.wav"
            with open(out_path, "wb") as f:
                f.write(r.content)
            size_kb = len(r.content) / 1024
            print(f"   Успешно! Размер: {size_kb:.1f} KB")
            print(f"   Файл: {out_path}")
        else:
            print(f"   Ошибка {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"   Ошибка: {e}")

def test_stream():
    """Test streaming synthesis."""
    print("\n4. Стриминг синтеза...")
    payload = {
        "input": "Конечно, давайте подберём удобное время для записи.",
        "voice": "default",
        "response_format": "wav",
        "exaggeration": 0.35,
        "cfg_weight": 0.5,
        "temperature": 0.6,
    }
    try:
        r = requests.post(
            f"{BASE_URL}/v1/audio/speech/stream",
            json=payload,
            timeout=120,
            stream=True,
        )
        total = 0
        chunks = 0
        for chunk in r.iter_content(chunk_size=4096):
            total += len(chunk)
            chunks += 1
        print(f"   Получено: {chunks} чанков, {total/1024:.1f} KB")
    except Exception as e:
        print(f"   Ошибка: {e}")

if __name__ == "__main__":
    if not test_health():
        print("\nСервер не запущен. Запустите:")
        print("  cd /workspace/chatterbox-api && USE_MULTILINGUAL_MODEL=true python main.py")
        sys.exit(1)
    test_voices()
    test_synthesize()
    test_stream()
    print("\n=== Тесты завершены ===")

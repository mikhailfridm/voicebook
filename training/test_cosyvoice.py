#!/usr/bin/env python3
"""Test CosyVoice 2 server with Russian speech."""
import requests
import os
import sys

BASE_URL = "http://localhost:50000"


def test_health():
    """Check server."""
    print("1. Проверка сервера...")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Статус: {r.status_code}")
        return True
    except Exception as e:
        print(f"   Сервер не доступен: {e}")
        return False


def test_sft_voices():
    """Test with built-in SFT voices (no reference needed)."""
    print("\n2. Тест встроенных голосов (SFT)...")

    phrases = [
        "Здравствуйте! Добро пожаловать в наш салон. Чем могу помочь?",
        "Конечно, давайте запишем вас на стрижку. На какой день удобно?",
        "Свободное время: десять тридцать и четырнадцать тридцать.",
    ]

    for i, text in enumerate(phrases, 1):
        out_path = f"/workspace/cosyvoice_test_{i}.wav"
        try:
            resp = requests.post(
                f"{BASE_URL}/api/tts",
                json={
                    "text": text,
                    "speed": 1.0,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) / 1024
                print(f"   [{i}] OK — {size_kb:.0f} KB — {out_path}")
            else:
                print(f"   [{i}] Ошибка: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"   [{i}] Ошибка: {e}")


def test_zero_shot(reference_path=None):
    """Test zero-shot voice cloning."""
    if not reference_path or not os.path.exists(reference_path):
        print("\n3. Zero-shot: пропущен (нет референсного файла)")
        return

    print(f"\n3. Zero-shot voice cloning с {reference_path}...")
    text = "Здравствуйте, добро пожаловать. Чем могу вам помочь?"

    try:
        with open(reference_path, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/api/tts",
                data={
                    "text": text,
                    "reference_text": "Пример референсной речи.",
                    "speed": 1.0,
                },
                files={"reference_audio": ("ref.wav", f, "audio/wav")},
                timeout=120,
            )
        if resp.status_code == 200:
            out_path = "/workspace/cosyvoice_clone_test.wav"
            with open(out_path, "wb") as f:
                f.write(resp.content)
            size_kb = len(resp.content) / 1024
            print(f"   OK — {size_kb:.0f} KB — {out_path}")
        else:
            print(f"   Ошибка: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"   Ошибка: {e}")


if __name__ == "__main__":
    if not test_health():
        print("\nСервер не запущен. Запустите:")
        print("  cd /workspace/CosyVoice/runtime/python/fastapi")
        print("  python3 server.py --port 50000 --model_dir iic/CosyVoice2-0.5B")
        sys.exit(1)

    test_sft_voices()

    # Test with reference if available
    ref = "/workspace/voice_samples/svetlana.wav"
    if os.path.exists(ref):
        test_zero_shot(ref)

    print("\n=== Тесты завершены ===")

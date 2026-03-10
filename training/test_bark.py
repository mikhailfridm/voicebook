#!/usr/bin/env python3
"""Test Bark TTS — generate Russian speech samples (CPU mode, long timeout)."""
import requests
import sys

BASE_URL = "http://localhost:50000"

# Test 3 most distinct Russian speakers
SPEAKERS = [
    ("v2/ru_speaker_0", "Голос 0"),
    ("v2/ru_speaker_5", "Голос 5"),
    ("v2/ru_speaker_9", "Голос 9"),
]

# Short text for faster generation on CPU
TEXT = "Здравствуйте! Чем могу помочь?"


def main():
    print("Проверяем сервер...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Статус: {r.json()}\n")
    except Exception as e:
        print(f"Сервер не доступен: {e}")
        sys.exit(1)

    print(f"Генерируем {len(SPEAKERS)} голосов (CPU — ~3-5 мин каждый)...\n")

    for speaker_id, desc in SPEAKERS:
        out_path = f"/workspace/bark_test_{speaker_id.replace('/', '_')}.wav"
        print(f"  {desc} ({speaker_id})...", end=" ", flush=True)
        try:
            resp = requests.post(
                f"{BASE_URL}/api/tts",
                json={"text": TEXT, "speaker": speaker_id},
                timeout=600,  # 10 min timeout for CPU
            )
            if resp.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) / 1024
                print(f"OK ({size_kb:.0f} KB) — {out_path}")
            else:
                print(f"Ошибка {resp.status_code}")
        except Exception as e:
            print(f"Ошибка: {e}")

    print("\n=== Готово! Послушай файлы bark_test_*.wav ===")


if __name__ == "__main__":
    main()

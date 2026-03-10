#!/usr/bin/env python3
"""Test Bark TTS — generate Russian speech samples with different speakers."""
import requests
import sys

BASE_URL = "http://localhost:50000"

# Russian speakers in Bark (v2/ru_speaker_0 to v2/ru_speaker_9)
# Each has a different voice character
SPEAKERS = [
    ("v2/ru_speaker_0", "Голос 0 — женский"),
    ("v2/ru_speaker_1", "Голос 1"),
    ("v2/ru_speaker_2", "Голос 2"),
    ("v2/ru_speaker_3", "Голос 3"),
    ("v2/ru_speaker_4", "Голос 4"),
    ("v2/ru_speaker_5", "Голос 5 — женский мягкий"),
    ("v2/ru_speaker_6", "Голос 6"),
    ("v2/ru_speaker_7", "Голос 7"),
    ("v2/ru_speaker_8", "Голос 8"),
    ("v2/ru_speaker_9", "Голос 9"),
]

TEXT = "Здравствуйте! Добро пожаловать в наш салон. Чем могу вам помочь? Давайте подберём удобное время."


def main():
    # Check health
    print("Проверяем сервер...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Статус: {r.json()}\n")
    except Exception as e:
        print(f"Сервер не доступен: {e}")
        print("Запустите: python /workspace/voicebook/training/start_bark.py")
        sys.exit(1)

    print(f"Генерируем {len(SPEAKERS)} голосов...\n")
    print("(Bark генерирует ~10-15 сек на фразу, подождите)\n")

    for speaker_id, desc in SPEAKERS:
        out_path = f"/workspace/bark_test_{speaker_id.replace('/', '_')}.wav"
        print(f"  {desc} ({speaker_id})...", end=" ", flush=True)
        try:
            resp = requests.post(
                f"{BASE_URL}/api/tts",
                json={"text": TEXT, "speaker": speaker_id},
                timeout=120,
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

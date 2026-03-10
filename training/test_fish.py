#!/usr/bin/env python3
"""Test Fish Speech TTS with Russian phrases."""
import requests
import sys

BASE_URL = "http://localhost:50000"

PHRASES = [
    "Здравствуйте! Чем могу помочь?",
    "Конечно, давайте запишем вас на стрижку.",
    "Свободное время: десять тридцать и четырнадцать тридцать. Какое удобнее?",
]


def main():
    print("Проверяем сервер...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Статус: {r.status_code}\n")
    except Exception:
        # Try docs endpoint
        try:
            r = requests.get(f"{BASE_URL}/docs", timeout=10)
            print(f"Docs: {r.status_code}\n")
        except Exception as e:
            print(f"Сервер не доступен: {e}")
            sys.exit(1)

    # Try OpenAI-compatible endpoint
    print("Тестируем синтез...\n")
    for i, text in enumerate(PHRASES, 1):
        out_path = f"/workspace/fish_test_{i}.wav"
        print(f"  [{i}] {text[:40]}...", end=" ", flush=True)

        # Try different API formats
        for endpoint, payload in [
            (f"{BASE_URL}/v1/audio/speech", {
                "input": text,
                "voice": "default",
                "response_format": "wav",
            }),
            (f"{BASE_URL}/api/tts", {
                "text": text,
                "format": "wav",
            }),
        ]:
            try:
                resp = requests.post(endpoint, json=payload, timeout=120)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(out_path, "wb") as f:
                        f.write(resp.content)
                    size_kb = len(resp.content) / 1024
                    print(f"OK ({size_kb:.0f} KB) — {out_path}")
                    break
            except Exception:
                continue
        else:
            print("Ошибка — ни один эндпоинт не сработал")

    print("\n=== Готово! ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install all CosyVoice 2 dependencies and start the server."""
import subprocess
import sys
import os

def run(cmd, check=False):
    print(f"\n>>> {cmd}")
    return subprocess.run(cmd, shell=True, check=check).returncode == 0

def main():
    print("=== Setting up CosyVoice 2 ===\n")
    pip = f"{sys.executable} -m pip install"

    # Step 1: Clone repo
    cosyvoice_dir = "/workspace/CosyVoice"
    if not os.path.exists(cosyvoice_dir):
        print("1. Cloning CosyVoice repo...")
        run(f"git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git {cosyvoice_dir}")
    else:
        print("1. CosyVoice repo exists.")

    # Step 2: Install ALL dependencies
    print("\n2. Installing all dependencies...")
    run(f"{pip} -r {cosyvoice_dir}/requirements.txt")

    # Extra deps that requirements.txt misses
    extras = [
        "hyperpyyaml",
        "onnxruntime-gpu",
        "openai-whisper",
        "modelscope",
        "conformer",
        "diffusers",
        "gradio",
        "inflect",
        "librosa",
        "lightning",
        "matplotlib",
        "pydub",
        "WeTextProcessing",
    ]
    run(f"{pip} {' '.join(extras)}")

    # Add CosyVoice to Python path
    print("\n3. Setup PYTHONPATH...")
    third_party = os.path.join(cosyvoice_dir, "third_party", "Matcha-TTS")
    print(f"   CosyVoice: {cosyvoice_dir}")
    print(f"   Matcha-TTS: {third_party}")

    print("\n=== Setup complete! ===")
    print(f"\nTo start, run:")
    print(f"  python /workspace/voicebook/training/start_cosyvoice.py")

if __name__ == "__main__":
    main()

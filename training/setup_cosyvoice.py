#!/usr/bin/env python3
"""Install and run CosyVoice 2 on RunPod."""
import subprocess
import sys
import os

def run(cmd, check=False):
    print(f"\n>>> {cmd}")
    return subprocess.run(cmd, shell=True, check=check).returncode == 0

def main():
    print("=== Setting up CosyVoice 2 ===\n")

    # Step 1: Clone repo
    cosyvoice_dir = "/workspace/CosyVoice"
    if not os.path.exists(cosyvoice_dir):
        print("1. Cloning CosyVoice repo...")
        run(f"git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git {cosyvoice_dir}")
    else:
        print("1. CosyVoice repo already exists, pulling latest...")
        run(f"cd {cosyvoice_dir} && git pull")

    # Step 2: Install dependencies
    print("\n2. Installing dependencies...")
    run(f"{sys.executable} -m pip install -r {cosyvoice_dir}/requirements.txt")

    # Install pynini for text normalization
    run("conda install -y -c conda-forge pynini==2.1.5 2>/dev/null || pip install pynini 2>/dev/null || true")

    # Step 3: Install modelscope for model download
    run(f"{sys.executable} -m pip install modelscope")

    print("\n=== Setup complete! ===")
    print(f"\nTo start the server:")
    print(f"  cd {cosyvoice_dir}/runtime/python/fastapi")
    print(f"  python3 server.py --port 50000 --model_dir iic/CosyVoice2-0.5B")
    print(f"\nServer will run on port 50000")

if __name__ == "__main__":
    main()

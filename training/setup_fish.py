#!/usr/bin/env python3
"""Install and start Fish Speech TTS on RunPod."""
import subprocess
import sys
import os

def run(cmd, check=False):
    print(f"\n>>> {cmd}")
    return subprocess.run(cmd, shell=True, check=check).returncode == 0

def main():
    print("=== Setting up Fish Speech ===\n")
    pip = f"{sys.executable} -m pip install"

    # Step 1: Clone repo
    fish_dir = "/workspace/fish-speech"
    if not os.path.exists(fish_dir):
        print("1. Cloning Fish Speech...")
        run(f"git clone https://github.com/fishaudio/fish-speech.git {fish_dir}")
    else:
        print("1. Fish Speech repo exists.")

    # Step 2: Install
    print("\n2. Installing Fish Speech...")
    run(f"{pip} -e {fish_dir}")

    # Step 3: Install API server deps
    print("\n3. Installing API deps...")
    run(f"{pip} cachetools")

    print("\n=== Setup complete! ===")
    print(f"\nTo start:")
    print(f"  python /workspace/voicebook/training/start_fish.py")

if __name__ == "__main__":
    main()

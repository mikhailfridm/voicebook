#!/usr/bin/env python3
"""Install and run Chatterbox TTS on RunPod."""
import subprocess
import sys
import os

def run(cmd, check=True):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def main():
    print("=== Setting up Chatterbox TTS ===\n")

    # Install chatterbox-tts
    print("1. Installing chatterbox-tts...")
    run(f"{sys.executable} -m pip install chatterbox-tts", check=False)

    # Install API server
    print("\n2. Installing API server...")
    api_dir = "/workspace/chatterbox-api"
    if not os.path.exists(api_dir):
        run(f"git clone https://github.com/travisvn/chatterbox-tts-api.git {api_dir}")
    else:
        run(f"cd {api_dir} && git pull")

    run(f"{sys.executable} -m pip install -r {api_dir}/requirements.txt", check=False)

    print("\n=== Setup complete! ===")
    print(f"\nTo start the server:")
    print(f"  cd {api_dir} && USE_MULTILINGUAL_MODEL=true python main.py")
    print(f"\nServer will run on port 4123")

if __name__ == "__main__":
    main()

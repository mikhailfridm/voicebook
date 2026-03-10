#!/usr/bin/env python3
"""Fix broken dependencies: revert torch to 2.6.0 and align all packages."""
import subprocess
import sys

def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=False)

# Step 1: Revert to torch 2.6.0 ecosystem
run(f"{sys.executable} -m pip install torch==2.6.0 torchaudio==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124")

# Step 2: Reinstall chatterbox-tts (needs torch 2.6.0)
run(f"{sys.executable} -m pip install chatterbox-tts --no-deps")

# Step 3: Check
print("\n=== Checking versions ===")
run(f"{sys.executable} -c \"import torch; print(f'torch: {{torch.__version__}}')\"")
run(f"{sys.executable} -c \"import torchaudio; print(f'torchaudio: {{torchaudio.__version__}}')\"")
run(f"{sys.executable} -c \"import torchvision; print(f'torchvision: {{torchvision.__version__}}')\"")
run(f"{sys.executable} -c \"from chatterbox.tts import ChatterboxTTS; print('chatterbox: OK')\"")

print("\n=== Done! Now run: ===")
print("cd /workspace/chatterbox-api && USE_MULTILINGUAL_MODEL=true python main.py")

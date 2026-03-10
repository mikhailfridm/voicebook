#!/usr/bin/env python3
"""Fix broken dependencies: torch 2.6.0 + compatible vLLM + chatterbox."""
import subprocess
import sys

def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=False)

# Step 1: Pin torch 2.6.0 ecosystem
run(f"{sys.executable} -m pip install torch==2.6.0 torchaudio==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124")

# Step 2: Install vLLM compatible with torch 2.6.0
run(f"{sys.executable} -m pip install vllm==0.7.3")

# Step 3: Reinstall chatterbox-tts
run(f"{sys.executable} -m pip install chatterbox-tts --no-deps")

# Step 4: Check
print("\n=== Checking versions ===")
run(f"{sys.executable} -c \"import torch; print(f'torch: {{torch.__version__}}')\"")
run(f"{sys.executable} -c \"import vllm; print(f'vllm: {{vllm.__version__}}')\"")
run(f"{sys.executable} -c \"from chatterbox.tts import ChatterboxTTS; print('chatterbox: OK')\"")

print("\n=== Done! ===")
print("Terminal 1: python training/serve.py")
print("Terminal 2: cd /workspace/chatterbox-api && USE_MULTILINGUAL_MODEL=true python main.py")

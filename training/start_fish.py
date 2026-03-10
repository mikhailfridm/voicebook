#!/usr/bin/env python3
"""Download model and start Fish Speech API server."""
import subprocess
import sys
import os

fish_dir = "/workspace/fish-speech"
ckpt_dir = os.path.join(fish_dir, "checkpoints", "openaudio-s1-mini")

# Step 1: Download model if not exists
if not os.path.exists(ckpt_dir):
    print("Downloading OpenAudio S1 Mini model...")
    subprocess.run([
        "huggingface-cli", "download",
        "fishaudio/openaudio-s1-mini",
        "--local-dir", ckpt_dir,
    ], check=True)
    print("Model downloaded!")
else:
    print(f"Model already exists: {ckpt_dir}")

# Step 2: Start API server
os.chdir(fish_dir)
env = os.environ.copy()
env["PYTHONPATH"] = fish_dir

cmd = [
    sys.executable, "tools/api_server.py",
    "--listen", "0.0.0.0:50000",
    "--llama-checkpoint-path", ckpt_dir,
    "--decoder-checkpoint-path", ckpt_dir,
    "--half",
]

print(f"\nStarting Fish Speech on port 50000...")
subprocess.run(cmd, env=env)

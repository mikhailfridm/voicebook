#!/usr/bin/env python3
"""Start CosyVoice 2 server. Run this instead of server.py directly."""
import subprocess
import sys
import os

cosyvoice_dir = "/workspace/CosyVoice"
matcha_dir = os.path.join(cosyvoice_dir, "third_party", "Matcha-TTS")
server_py = os.path.join(cosyvoice_dir, "runtime", "python", "fastapi", "server.py")

# Set PYTHONPATH so all imports work
env = os.environ.copy()
paths = [cosyvoice_dir, matcha_dir]
existing = env.get("PYTHONPATH", "")
if existing:
    paths.append(existing)
env["PYTHONPATH"] = ":".join(paths)

cmd = [
    sys.executable, server_py,
    "--port", "50000",
    "--model_dir", "iic/CosyVoice2-0.5B",
]

print(f"Starting CosyVoice 2 server on port 50000...")
print(f"PYTHONPATH={env['PYTHONPATH']}")
print(f"Command: {' '.join(cmd)}")
subprocess.run(cmd, env=env)

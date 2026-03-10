#!/usr/bin/env python3
"""Start Fish Speech API server."""
import subprocess
import sys
import os

fish_dir = "/workspace/fish-speech"
api_server = os.path.join(fish_dir, "tools", "api_server.py")

if not os.path.exists(api_server):
    # Try alternative paths
    for alt in ["tools/run_webui.py", "fish_speech/server.py"]:
        alt_path = os.path.join(fish_dir, alt)
        if os.path.exists(alt_path):
            api_server = alt_path
            break

env = os.environ.copy()
env["PYTHONPATH"] = fish_dir

cmd = [
    sys.executable, "-m", "fish_speech.entry", "serve",
    "--listen", "0.0.0.0:50000",
]

# Try the module entry point first, fall back to api_server.py
print(f"Starting Fish Speech on port 50000...")
result = subprocess.run(cmd, env=env)

if result.returncode != 0:
    print("Module entry failed, trying api_server.py...")
    cmd = [sys.executable, api_server, "--listen", "0.0.0.0:50000"]
    subprocess.run(cmd, env=env)

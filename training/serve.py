#!/usr/bin/env python3
"""Start vLLM server for voicebook model."""
import subprocess
import sys

model = "/workspace/voicebook/models/voicebook-qwen2.5-14b"
cmd = [
    sys.executable, "-m", "vllm.entrypoints.openai.api_server",
    "--model", model,
    "--dtype", "bfloat16",
    "--max-model-len", "4096",
    "--gpu-memory-utilization", "0.60",
    "--port", "8100",
]
print(f"Starting vLLM: {' '.join(cmd)}")
subprocess.run(cmd)

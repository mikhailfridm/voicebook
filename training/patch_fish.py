#!/usr/bin/env python3
"""Patch Fish Speech tokenizer bug and start server."""
import os
import sys

fish_llama = "/workspace/fish-speech/fish_speech/models/text2semantic/llama.py"

# Read the file
with open(fish_llama, "r") as f:
    content = f.read()

# Patch: initialize tokenizer = None before the try block
# The bug is that tokenizer is only assigned inside try, but used after except
if "model.tokenizer = tokenizer" in content and "tokenizer = None  # patch" not in content:
    # Find the line "Failed to load tokenizer" warning and add tokenizer = None before the try
    content = content.replace(
        "        try:\n            tokenizer = AutoTokenizer.from_pretrained",
        "        tokenizer = None  # patch: ensure variable exists\n        try:\n            tokenizer = AutoTokenizer.from_pretrained",
    )

    # Also handle the case where tokenizer is None at assignment
    content = content.replace(
        "        model.tokenizer = tokenizer\n",
        "        if tokenizer is not None:\n            model.tokenizer = tokenizer\n",
    )

    with open(fish_llama, "w") as f:
        f.write(content)
    print("Patched Fish Speech tokenizer bug!")
else:
    print("Already patched or different code structure.")

# Now start the server
print("\nStarting Fish Speech...")
os.execv(sys.executable, [sys.executable, "/workspace/voicebook/training/start_fish.py"])

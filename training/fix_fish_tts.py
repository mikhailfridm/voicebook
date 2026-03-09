"""Fix torchaudio compatibility in Fish Speech."""
import re

path = "/workspace/fish-speech-repo/fish_speech/inference_engine/reference_loader.py"
with open(path, "r") as f:
    content = f.read()

content = content.replace(
    "backends = torchaudio.list_audio_backends()",
    'backends = ["soundfile"]',
)

with open(path, "w") as f:
    f.write(content)

print("Fixed!")

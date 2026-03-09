#!/bin/bash
# Upload a Russian reference voice to Chatterbox TTS for voice cloning.
#
# Usage:
#   ./upload_voice.sh <voice_file.wav> [voice_name]
#
# Example:
#   ./upload_voice.sh reference_voice.wav russian_receptionist

CHATTERBOX_URL="${CHATTERBOX_TTS_BASE_URL:-http://localhost:8150}"
VOICE_FILE="${1:?Usage: $0 <voice_file.wav> [voice_name]}"
VOICE_NAME="${2:-russian_default}"

echo "Uploading voice '${VOICE_NAME}' from ${VOICE_FILE}..."

curl -X POST "${CHATTERBOX_URL}/voices" \
  -F "voice_name=${VOICE_NAME}" \
  -F "language=ru" \
  -F "voice_file=@${VOICE_FILE}"

echo ""
echo "Done. Set CHATTERBOX_TTS_VOICE=${VOICE_NAME} in .env to use this voice."

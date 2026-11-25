#!/bin/sh
# usage: KOKORO_TTS_URL=... audition_voices.sh OUT_DIR SPEED "LINE" VOICE...
set -eu
OUT=$1; SPEED=$2; TEXT=$3; shift 3
mkdir -p "$OUT"
for v in "$@"; do
  name=$(printf '%s' "$v" | tr '+()' '___')
  body=$(python3 -I -c 'import json,sys; print(json.dumps({"model":"kokoro","voice":sys.argv[1],"input":sys.argv[2],"speed":float(sys.argv[3]),"response_format":"mp3"}))' "$v" "$TEXT" "$SPEED")
  curl -sf -A 'Mozilla/5.0' -H 'Content-Type: application/json' "$KOKORO_TTS_URL/v1/audio/speech" -d "$body" -o "$OUT/$name.mp3" || { echo "FAILED $v"; continue; }
  printf '%s %s s\n' "$name" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$name.mp3")"
done

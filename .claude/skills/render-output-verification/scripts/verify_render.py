#!/usr/bin/env python3
"""Probe a render, compare its narration with the approved script, and dump review frames.

Usage: python3 -I scripts/verify_render.py <final.mp4> <script.json> <out_dir>
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path


def main():
    video, script_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)

    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)],
        check=True, capture_output=True, text=True).stdout)
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    duration = float(probe["format"]["duration"])
    print("duration_s", round(duration, 2), "size", f'{video_stream["width"]}x{video_stream["height"]}',
          "codec", video_stream["codec_name"], "bytes", probe["format"]["size"])

    audio = out / "_audio.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
                    "-vn", "-ac", "1", "-ar", "16000", str(audio)], check=True)
    from faster_whisper import WhisperModel
    segments, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(
        str(audio), language="en", beam_size=5)
    heard = " ".join(s.text.strip() for s in segments)
    audio.unlink()

    script = json.loads(script_path.read_text())
    said = " ".join(section["text"] for section in script["sections"])
    words = lambda text: re.sub(r"[^a-z' ]", " ", text.lower()).split()
    ratio = difflib.SequenceMatcher(None, words(said), words(heard)).ratio()
    print("transcript_similarity", round(ratio, 3))

    for fraction in (0.05, 0.5, 0.95):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss",
                        f"{duration * fraction:.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=540:-1", str(out / f"frame_{fraction:.2f}.jpg")], check=True)
    print("frames", out)


if __name__ == "__main__":
    main()

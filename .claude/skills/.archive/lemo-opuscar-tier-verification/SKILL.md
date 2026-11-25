---
name: lemo-opuscar-tier-verification
description: Use when verifying lemo-opuscar voice or sample packs.
category: video-production
---

# Verify lemo-opuscar tiers by their files, then by one real run

A tier counts as installed only when its files exist on disk and one real run succeeds. A filtered download log is not proof.

- **Check disk before fetching.** Run `df -h ~` first. The five sample packs are about 1.4 GB and the Whisper model about 145 MB. Renders write every frame to disk, so keep several GB free.
- **Check files, not log lines.** After each `fetch.sh` call, `ls core/audio/instruments/` (or the HDRI folder). A grep that keeps only status lines can hide a pack that installed.
- **Voice round trip.** Synthesize one line with `core/tts/tts.py`, transcribe it with `core/tts/asr_check.py`, and expect `mismatches: 0` and exit 0. Use the project's `.venv/bin/python` for every call.
- **Markers and commands.** Tier markers, the install and fetch commands, and the voice check script are in `references/tier-commands.md`.

Report each tier as verified or missing, with the file or run that proved it.

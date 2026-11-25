# lemo-opuscar tier commands and markers (verified 2026-11-02)

Library clone: ~/lemo-opuscar (sparse clone). The plugin cache holds the setup script under skills/lemo-opuscar/scripts/setup.sh inside the plugin's hashed cache folder.

## Markers
- .venv/.lemo-core, .venv/.lemo-voice, .venv/.lemo-music (Python tiers)
- node_modules/.lemo-ok (Node packages)
- core/tts/kokoro-v1.0.onnx and core/tts/voices-v1.0.bin (voice model; the glob core/tts/*.onnx errors in zsh when nothing matches, so list the exact names)
- core/audio/instruments/{freepats,vcsl,salamander,karoryfer,vsco2ce}
- core/assets/polyhaven/ (HDRIs)
- ~/.cache/ms-playwright (headless Chromium), ~/.cache/huggingface (Whisper base.en, about 145 MB)

## Install and fetch
- Python tiers: run the setup script's `deps voice music` action (uv fetches Python 3.12 for Kokoro, which needs Python below 3.14).
- HDRIs: `sh tools/fetch.sh hdri` (about 13 MB)
- One pack: `sh tools/fetch.sh instruments LIB` where LIB is one of freepats, vcsl, salamander, karoryfer, vsco2ce
- All packs: `sh tools/fetch.sh instruments all` (about 1.4 GB)

## Voice round trip
1. Write a one-line lines.json with id and text.
2. `.venv/bin/python core/tts/tts.py lines.json out_dir`
3. `.venv/bin/python core/tts/asr_check.py lines.json out_dir` and expect `mismatches: 0`.

## Known noise
- Playwright warns that the OS is unsupported and uses the Ubuntu build. It works.
- The HF Hub warns about unauthenticated requests. It is harmless.

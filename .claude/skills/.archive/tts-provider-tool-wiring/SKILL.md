---
name: tts-provider-tool-wiring
description: Use when adding a TTS provider tool to OpenMontage.
category: video-production
---

# Wire a new TTS provider into OpenMontage in one pass

A TTS provider is a tool in `tools/audio/` plus every place that routes to it. Missing one leaves it unselectable or untested. Work through this list:

1. Probe the live API's real JSON response before writing the parser.
2. Write the tool file `tools/audio/<name>_tts.py` with its provider name, zero cost for free services, and a fallback chain.
3. In `tools/audio/tts_selector.py`, if the tool's control names differ from the generic ones (`voice_id`, `speaking_rate`, `output_format`), add an adapter block before the shared `if tool.name not in {...}` early return. Add the tool name to that set only if it needs the shared handling.
4. Document env vars in `.env.example`, then set the live values in `.env`.
5. Add a row and a section in `docs/PROVIDERS.md`.
6. Add the provider name to the hardcoded provider set in `tests/contracts/test_phase3_contracts.py`. Its failure before this edit is expected.
7. Write mocked tests in `tests/tools/test_<name>.py`, then run one live call through `tts_selector` with `preferred_provider`.
8. Clear new Pyright hints such as unused variables before reporting done.

Voice syntax, blends and word timestamps for Kokoro are in `references/kokoro-blends-and-timestamps.md`.

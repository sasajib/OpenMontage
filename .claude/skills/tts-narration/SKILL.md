---
name: tts-narration
description: Use when adding a TTS tool or picking a Kokoro voice.
category: video-production
---

# TTS narration: wire every routing point, audition voices raw, never pick from memory

Never choose a narration voice from memory or from a processed recipe. Render one raw line in each candidate, let the user pick, and tune speed only after the pick. A new TTS provider is a tool plus every routing point; missing one leaves it unselectable or untested.

## Wiring a new TTS provider

1. Probe the live API's real JSON response before writing the parser.
2. Write `tools/audio/NAME_tts.py` with its provider name, zero cost for free services, and a fallback chain.
3. In `tools/audio/tts_selector.py`, if the tool's controls differ from `voice_id`, `speaking_rate` and `output_format`, add an adapter block before the shared `if tool.name not in {...}` early return. Add the tool name to that set only if it needs the shared handling.
4. Document env vars in `.env.example`, then set the live values in `.env`.
5. Add a row and a section in `docs/PROVIDERS.md`.
6. Add the provider name to the hardcoded set in `tests/contracts/test_phase3_contracts.py`. Its failure before this edit is expected.
7. Write mocked tests in `tests/tools/test_NAME.py`, then run one live call through `tts_selector` with `preferred_provider`.
8. Clear new Pyright hints, such as unused variables, before reporting done.

## Auditioning voices (Kokoro)

- Run `scripts/audition_voices.sh OUT_DIR SPEED "LINE" VOICE...`. It needs `KOKORO_TTS_URL` from the project `.env`, and it sends a browser User-Agent. Use a folder in the session scratchpad for OUT_DIR. A `FAILED` line means that render did not happen.
- Report the full absolute paths of the files. Ask which voice is closest, and whether the problem is the voice, the speed or the processing.
- Blends such as `am_onyx+bm_george` are averaged by the server. Syntax, weights and word timestamps: `references/kokoro-blends-and-timestamps.md`.
- Once a voice is chosen, re-render the episode narration with it and update the episode brief.

## Sharing Kokoro access

- Before handing Kokoro to another agent, check it live: `GET /health`, then one short `POST /v1/audio/speech`. Report what you measured, not what the notes say.
- Derive endpoints from `tools/audio/kokoro_tts.py`, not from memory. Full endpoint notes: `references/kokoro-access.md`.
- State plainly that the public URL has no authentication and must not be posted publicly.
- Put the paste-ready handoff in a file in the session scratchpad, and give the user its path.

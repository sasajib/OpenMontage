---
name: kokoro-voice-audition
description: Use when picking Kokoro voices or sharing Kokoro access.
category: video-production
---

# Audition Kokoro voices before choosing narration

Never pick or keep a narration voice from memory or from a processed recipe. Render one line raw (no pitch or EQ) in every candidate voice at the target speed, confirm each file decodes, then give the user the folder and let them pick. Tune speed and pitch only after the pick.

- Endpoint: `KOKORO_TTS_URL` from the project `.env`. Send a browser User-Agent header.
- Voices: `GET $KOKORO_TTS_URL/v1/audio/voices` lists them (67 on the server). English male candidates: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa, bm_daniel, bm_fable, bm_george, bm_lewis.
- Blends: a voice name like `am_onyx+bm_george` is accepted and averaged by the server.
- Run `scripts/audition_voices.sh OUT_DIR SPEED "LINE" VOICE...` with OUT_DIR in the session scratchpad. It prints each file's name and duration; a `FAILED` line means that render did not happen.
- Report the full absolute paths of the files. Ask which voice is closest and whether the problem is the voice, the speed, or the processing.
- Once a voice is chosen, re-render the episode narration with it and update the episode brief.

## Access and handoff

- Before handing Kokoro to another agent, check it live: `GET /health` and one short `POST /v1/audio/speech` (`{"model":"kokoro","input":"...","voice":"af_heart","response_format":"wav"}`). Report what you measured, not what the notes say.
- Derive endpoints from the tool code in `tools/audio/kokoro_tts.py`, not memory. Word timings come from `/dev/captioned_speech` with `return_timestamps: true`.
- State plainly that the public URL has no authentication and must not be posted publicly.
- Put the paste-ready handoff in a file in the session scratchpad, then give the user its path. Full endpoint notes: [references/kokoro-access.md](references/kokoro-access.md).

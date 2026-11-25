# Kokoro-FastAPI: voice blends and word timestamps

Verified 2026-11-03 against the self-hosted server on bee (OpenAI-style speech API).

## Voice syntax
- Single voice: `am_adam`, `af_heart`, `bf_emma`, `bm_george` (67 shipped voices).
- Blend: `voice(weight)+voice(weight)`, for example `am_adam(2)+am_michael(1)` or `af_sarah(1)+af_bella(1)`. Each blend took about 4 to 5 s for a short line.
- Aliases: heart, bella, sarah, adam, michael, emma, george.
- Speed range 0.25 to 4.0.

## Word timestamps
- The captioned endpoint is `POST /dev/captioned_speech` with `return_timestamps: true`.
- Response keys: `audio`, `audio_format`, `timestamps`. Each timestamp is `{word, start_time, end_time}` in seconds.
- The tool writes these to `<output>.words.json` as `{words: [{word, start, end}]}`.

## Operational notes
- Kokoro has no voice cloning. Use a cloning provider for a user's own voice.
- The public tunnel had no auth at the time of writing. Set `KOKORO_TTS_API_KEY` if an auth proxy is added.

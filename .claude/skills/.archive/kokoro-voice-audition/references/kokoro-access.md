# Kokoro TTS access notes

Base URL: the value of KOKORO_TTS_URL in the project .env (currently the public tunnel host, voice.mindshare.website). Auth: none on the public URL.

- GET /health -> 200 when the server is up.
- GET /v1/audio/voices -> {"voices": [...]} (67 voices).
- POST /v1/audio/speech, JSON: model "kokoro", input, voice (id or blend such as af_bella(2)+af_sky(1)), response_format "wav" (24 kHz mono) or "mp3", optional speed 0.25-4.0. Response body is the audio.
- POST /dev/captioned_speech, same JSON plus return_timestamps true. Response is JSON with base64 audio and a timestamps list of {word, start_time, end_time}.

Voice prefixes: af/am US female/male, bf/bm UK, ef/em Spanish, ff French, hf/hm Hindi, if/im Italian, jf/jm Japanese, pf/pm Portuguese, zf/zm Chinese.

Throughput: CPU only, about 2x real time on the owner's 8-thread server. Queue requests rather than sending dozens at once.

In OpenMontage: tool kokoro_tts (tools/audio/kokoro_tts.py), selected with tts_selector preferred_provider "kokoro". Fallbacks: edge_tts, piper_tts.

Owner-only ops: the server is reached over ssh alias bee; container kokoro-tts; tunnel cloudflared-voice. Do not touch the separate openreader-kokoro container on that host.

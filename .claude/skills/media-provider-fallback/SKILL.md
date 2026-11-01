---
name: media-provider-fallback
description: Use when OpenMontage TTS or image call fails (403/429).
category: video-production
---

# Media provider fallback (OpenMontage)

When a paid asset call fails, switch to the fallback the approved plan names, or drop an optional asset. Do not retry the same provider with the same key.

- **403 from a Google Cloud API** (for example Cloud Text-to-Speech): the Gemini API key does not cover Cloud services. Use the Gemini-backed tool `gemini_tts` instead.
- **"Retired" or model-not-found**: use the replacement model the error names. Do not retry the old id.
- **429 with `limit: 0`** on the free tier: the key has no quota for that model. Retrying is pointless. Switch provider or skip the asset.
- **`gemini_tts`**: `output_path` must end in `.wav`.
- **Google AI Pro account (user-owned)**: when the user says they have it, images and Veo video can come from the Gemini app driven through BrowserOS, at no per-call cost. Use the `browser-media-generation` skill for the click-path. Images take about 5 s, video about 90 s. Record the source as `provided (Gemini app via BrowserOS)`, not as an API call.
- **Gemini TTS quota exhausted (429, free tier)**: when the user names Deepgram as the fallback voice, switch narration to Deepgram Aura-2 and record the swap as a `fallback_decision`. Pick the voice the user approves (for example `aura-2-draco-en`). Narration runs at the voice's native speed. Do not time-stretch or slow the audio to fit a scene.
- **MiniMax key expired**: the user's instruction was "use deepgram, minimax api expire". Switch narration to Deepgram Aura-2 the same way. If the user calls the voice unnatural, choose a deeper Aura-2 voice at native speed and re-render the narration. Do not tune pitch or speed to fix it.
- **`pixabay_music`**: needs no key. It returns the track title, artist, duration, and license. Check the duration against the video length.

Calling a tool from Python: `registry.get(name)` then `tool.execute(inputs)`. Check `result.success` and `result.error`. There is no `run` method on these tools.

Before any paid call, state the expected cost. After a fallback or a skipped asset, record it in `artifacts/decision_log.json` as a `fallback_decision` with `user_approved: false`, then save the stage checkpoint.

Stop at the approval gate. Do not generate the remaining narration or scenes until the user approves the sample.

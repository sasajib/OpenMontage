---
name: hf-space-tts-demo-quota
description: Use when a Hugging Face Space TTS demo hits ZeroGPU quota.
category: video-production
---

# Hugging Face Space TTS demos are a one-take budget

Treat a free Hugging Face Space (ZeroGPU) as a budget of about one generation per quota window. Do not plan a multi-voice comparison on it.

- Before the single call, fix the final text, the seed, and the reference clip so the one take counts.
- After a `ZeroGPU runs limit` error, stop calling that Space for the session and tell the user the quota blocked it.
- For a multi-voice audition, use a local or owned endpoint (the Kokoro server, or an owned RunPod endpoint) instead of stacking demo calls.
- Report a single take as one sample, not as proof the voice is best.

Error text and the call pattern are in [references/zerogpu-quota-error.md](references/zerogpu-quota-error.md).

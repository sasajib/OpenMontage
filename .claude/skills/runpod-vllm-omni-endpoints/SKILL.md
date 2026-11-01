---
name: runpod-vllm-omni-endpoints
description: The user's own RunPod serverless endpoints for OpenMontage generation (WAN 2.2 image-to-video, Qwen-Image-2512 text-to-image, Qwen-Image-Edit-2511 image-to-image, Z-Image-Turbo bulk stills), all deployed from the RunPod "Deploy a model" catalog on the vLLM-Omni worker. Use whenever a video or image needs generating on RunPod, before touching RUNPOD_* ids in .env, before creating or deleting any RunPod resource, or when the user asks about generation cost. Covers the release/park procedure (workers 0 ↔ 1), the exact request bodies that work, measured timings and costs, audio/STT providers, and the mistakes already made.
---

# RunPod vLLM-Omni endpoints (OpenMontage)

Status as of 2026-11-01. Four endpoints exist, all **parked at max workers = 0**, which costs nothing.
Idle endpoints are free; only running workers bill (per second, including cold start and idle timeout).

## 1. The endpoints

| Role | Name | Endpoint id (.env key) | Model (`MODEL_NAME`) | GPU pool | $/hr |
|---|---|---|---|---|---|
| Image → video (hero clips) | openmontage-wan22-i2v | `RUNPOD_WAN_I2V_ENDPOINT_ID` (value in .env) | magespace/Wan2.2-I2V-A14B-Lightning-Diffusers | BLACKWELL_96 (RTX PRO 6000) | 3.49 |
| Text → image (hero frames, faces, text) | openmontage-qwen-image-2512 | `RUNPOD_QWEN_IMAGE_ENDPOINT_ID` (value in .env) | Qwen/Qwen-Image-2512 | BLACKWELL_96 | 3.49 |
| Image → image (character consistency, restyle) | openmontage-qwen-image-edit | `RUNPOD_QWEN_EDIT_ENDPOINT_ID` (value in .env) | Qwen/Qwen-Image-Edit-2511 | BLACKWELL_96 | 3.49 |
| Text → image (bulk plates, maps, textures) | openmontage-zimage-turbo | `RUNPOD_ZIMAGE_ENDPOINT_ID` (value in .env) | Tongyi-MAI/Z-Image-Turbo | AMPERE_48 (A40/A6000) | 1.22 |

All licences are Apache 2.0. Worker image: `registry.runpod.net/runpod-workers-worker-vllm-omni-main-dockerfile:714c23fa1` (vLLM-Omni 0.1.6). RunPod caches the catalog weights, so cold starts are 70–280 s, not a 60 GB download.

The three 96 GB endpoints still list `ADA_80_PRO` ($5.39/hr) as a fallback pool. Narrow them to BLACKWELL_96 in the console (endpoint → Manage → Edit endpoint → Previous generation → untick 80 GB → Save) before a heavy batch. The REST PATCH for `gpu.pools` is rejected (allowedCudaVersions/minCudaVersion clash).

No text-to-video endpoint on purpose: every clip starts from an approved still (still-first rule). No LTX endpoints (two cold starts aborted, untested).

## 2. Money rules (binding)

1. **Quote before spending.** Before releasing any endpoint, tell the user: endpoint, number of jobs, expected per-job time, cold-start cost, total ceiling. Wait for "go".
2. **Release only for the batch, park right after.** `workers.max` 0 → 1 before, 1 → 0 after. Never leave max ≥ 1 between sessions.
3. **Batch, don't trickle.** One cold start per batch (~$0.10–0.30). Queue all jobs for an endpoint together while the worker is warm.
4. **Max 1 worker per endpoint.** Account quota is 5 workers across endpoints.
5. **"Stop" means park, never delete.** Set max=0 on every endpoint and cancel jobs. Deleting loses the endpoint; recreating needs the console. (Deleting was done once by mistake on 2026-11-01 and the user objected.)
6. Verify spend with the console balance, not the REST health flag (it lags) and not the billing API (hours behind).

```bash
# release / park (REST v2; key in .env, never print it)
set -a; . ./.env; set +a; H="Authorization: Bearer $RUNPOD_API_KEY"
curl -s -X PATCH -H "$H" -H "Content-Type: application/json" https://api.runpod.io/v2/serverless/$EP \
  -d '{"workers":{"min":0,"max":1,"idleTimeout":20}}'     # release
curl -s -X PATCH -H "$H" -H "Content-Type: application/json" https://api.runpod.io/v2/serverless/$EP \
  -d '{"workers":{"min":0,"max":0,"idleTimeout":5}}'      # park
curl -s -H "$H" https://api.runpod.ai/v2/$EP/health         # workers/jobs (lags a few minutes)
curl -s -X POST -H "$H" https://api.runpod.ai/v2/$EP/cancel/$JOB_ID
```

Job API host is `api.runpod.ai` (run/status/health/cancel); management host is `api.runpod.io` (serverless CRUD).

## 3. Request bodies that work (verified 2026-11-01)

Submit `POST https://api.runpod.ai/v2/<EP>/run` with `{"input": ...}`, poll `GET .../status/<id>` every 8–10 s until COMPLETED. Runner scripts in `scripts/` do this.

**Image → video (WAN)** — multipart route; image goes as a `_b64` file part. 720p, 81 frames @ 16 fps = 5 s.
```json
{"input": {"task": "video", "prompt": "...", "negative_prompt": "people, person, face, hands, text, watermark, logo, blurry, distorted, jittery, flicker",
  "width": 1280, "height": 720, "num_frames": 81, "fps": 16, "seed": 901,
  "num_inference_steps": 4, "guidance_scale": 1.0, "input_reference_b64": "<base64 png>"}}
```
Output: `output.data_b64` (mp4), `content_type`, `size_bytes`. The console's sample body (`image_reference.image_url` data URL) returns a bare `{"status":400}`; do not use it.

**Text → image (Qwen-Image-2512, Z-Image-Turbo)**
```json
{"input": {"prompt": "...", "size": "1664x928", "seed": 7}}
```
Output: `output.data[0].b64_json` (png) plus `output.metrics` (stage durations, peak VRAM). Z-Image: 8–9 steps are the model default; 16:9 sizes such as 1664x928 or 1920x1088 work.

**Image → image (Qwen-Image-Edit-2511)** — generic proxy to the edits route; output keeps the input size.
```json
{"input": {"route": "/v1/images/edits", "body": {"prompt": "...", "image_b64": "<base64 png>", "seed": 7}}}
```

## 4. Measured timings and costs (RTX PRO 6000 unless noted)

| Job | Warm time | Cold start seen | Cost warm | Note |
|---|---|---|---|---|
| WAN 720p 5 s clip | 81 s | 106 s | ~$0.08 | invents people sometimes; change seed, keep negatives |
| Qwen-Image-2512 1664x928 | 18 s | 71–274 s | ~$0.02 | peak VRAM 61 GB (does not fit 48 GB) |
| Qwen-Image-Edit-2511 1280x720 | 14 s | 71 s | ~$0.013 | peak VRAM 60.5 GB; excellent scene preservation |
| Z-Image-Turbo 1080x1920 (24 GB tier, Oct 31) | ~20 s | ~37 s | ~$0.006 | not yet re-measured on the 48 GB tier |

Rule of thumb per 10-minute episode: 30 Z-Image stills + 5 Qwen stills + 5 edits + 5 WAN clips ≈ $0.80–1.10 warm, plus one cold start per endpoint used.

## 5. Audio and transcription (no RunPod needed)

- Narration: ElevenLabs (`ELEVENLABS_API_KEY`, free tier = non-commercial, ~10 min/month) with v3 audio tags for expression; fallback Deepgram (`DEEPGRAM_API_KEY`, used on the Facebook projects); second fallback Azure TTS.
- Sound effects / music: ElevenLabs SFX and Music APIs, Freesound tool for real recordings, ACE-Step skill for open music.
- Audio → text: local faster-whisper (`transcriber` tool, installed), Azure STT, Mistral STT.
- Open-source TTS later (Chatterbox MIT or Qwen3-TTS Apache via vLLM-Omni "Other model") only once a channel voice is fixed.

## 6. Real people and licences

Generated footage of a real public figure is synthetic media: YouTube requires disclosure, defamation applies, and several model AUPs forbid it. Default: archive photos/footage for real figures, generated humans for reenactments, a visible "dramatization" label when a real face is generated. Models rejected for this stack: FLUX.2-klein-9B (non-commercial), HunyuanVideo-1.5 and HunyuanVideo-Foley (licence excludes EU/UK/South Korea), Higgs Audio v3 (non-commercial), MiniMax H3 (needs a 160 GB volume plus ~$2 first boot, adult-tuned community worker).

## 7. Recreating an endpoint (only if one is lost)

Console → Serverless → New endpoint → "Deploy image or video API" → tab → model → "Deploy with vLLM Omni" → Next → generation toggle → tick the tier → Create Endpoint. Then PATCH name + workers max 0. Gated models (LTX, FLUX, Krea) need `HF_TOKEN` from `.env` pasted into the form; the LTX-2.5 licence is already accepted on the user's HF account. BrowserOS gotchas: snapshot tab lines read `tab "X" [selected] [ref=eN]`, so match with `[^\n]*` before `[ref=`; the `?source=model` URL sometimes lands on a chooser page; keep each browser call under ~60 s or it times out even though the clicks go through (check the endpoint list afterwards to avoid duplicates).

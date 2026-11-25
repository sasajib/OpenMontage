---
name: remote-gpu-deploy
description: Use when renting a GPU, RunPod pod, or Runware serverless.
category: gpu-compute
---

# Remote GPU: serverless first, a pod only for persistent weights

For open models, run a serverless endpoint first (RunPod or Runware). Rent a pod only when weights or training need a persistent disk that no worker image covers. State the GPU, the $/hour and the expected total before creating anything.

## Serverless first

- Use serverless for every model class, video included (WAN 2.2 image-to-video, images, transcription). The user objected mid-task: "we have runpod serverless - why do we need pod?"
- Serverless bills only while a job runs plus its idle timeout, and needs no teardown. Create RunPod endpoints with REST v2 (`api.runpod.io/v2/serverless`). The recipe is in the global `runpod-serverless-endpoints` skill. Check that `/health` shows zero running workers before reporting it idle.
- Before promising a pod or endpoint, check the provider is connected: RunPod MCP (OAuth or `RUNPOD_API_KEY` in `.env`), or the console through BrowserOS when logged in. If it is logged in through BrowserOS, do the console work yourself.

## Renting a pod (only when needed)

- Pick the newest GPU generation with stock that fits the model's VRAM (Blackwell, then Ada/Hopper, before Ampere), then the lowest price in that generation. The user rejected an old Ampere card when newer stock existed.
- Take the model file list from the repo's model metadata, for example `tools/_comfyui/metadata.py`. Never guess filenames.
- Download weights detached and resumable with `templates/pod-model-download.sh`. Poll with short bounded SSH calls, and never block one foreground call on a long download.
- Before any generation job, confirm every expected file exists at full size.
- Terminate the pod when done, not just stop it: a stopped pod still bills its disk. Checks, the scripted terminate pass and measured costs: `references/pod-operations.md`.

## Runware serverless

- Read the exact status first. 403 means the org has no Serverless access yet. 401 means the key is rejected. 402 `insufficient-credit` means the serverless balance is short, and the `shortfall` field is the amount to add.
- Probe both APIs with the same key before touching anything. If only serverless fails, stop and ask the user to confirm the access request. Do not create keys or re-login.
- Serverless has its own prepaid balance, separate from inference. Check which balance a top-up lands in before paying. Deploy sequence, billing and fixed rules: `references/runware-deploy-sequence.md`.
- Never print the API key or HF token. Mask command output.

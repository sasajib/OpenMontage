---
name: remote-gpu-pod-generation
description: Use when renting a RunPod GPU pod for open-source models.
category: gpu-compute
---

# Remote GPU pod generation

Rent the cheapest GPU that fits the model, pull weights detached, generate, then terminate the pod. State the cost before creating it.

## Rules

- Before creating a pod, state the GPU, the $/hour, and the expected total. Pick the newest GPU generation with stock that fits the model's VRAM (Blackwell, then Ada/Hopper, before Ampere), then the lowest price within that generation. Do not default to an old Ampere card when newer generations have stock; the user rejected exactly that.
- Get the model file list from the repo's model metadata (for example `tools/_comfyui/metadata.py`). Never guess filenames.
- Download weights detached on the pod with `nohup setsid <script> > log 2>&1 < /dev/null &`. Use `templates/pod-model-download.sh`. It writes `.part` then `mv`s on success, resumes with `wget -c`, and skips files that already exist.
- Poll with short bounded SSH calls (`timeout 25 ssh ... 'tail -3 <log>'`) inside a loop with `sleep`. Never block one foreground call on a long download, because it hits the tool timeout.
- Before any generation job, confirm every expected file exists and has its full size.
- When generation finishes, terminate the pod, not just stop it. A stopped pod still bills its disk. Report the final spend.
- Creating or terminating a pod needs the RunPod MCP connected (OAuth, or `RUNPOD_API_KEY` in `.env`), or the console through BrowserOS when it is logged in. Check that before promising a pod.
- Serverless first, for every model class, video included (WAN 2.2 image-to-video as well as images and transcription). Do not propose a pod while the account can serve the job from a serverless endpoint. The user objected mid-task: "we have runpod serverless - why do we need pod?" Rent a pod only when weights or training need a persistent disk that no worker image covers. A serverless endpoint bills only while a job runs plus its idle timeout, and needs no pod teardown. Create it with REST v2 (`api.runpod.io/v2/serverless`); recipe, existing endpoints and wrappers are in the global `runpod-serverless-endpoints` skill. Check `/health` shows zero running workers before reporting it idle.
- If the user has RunPod logged in through BrowserOS, do the console work yourself. Do not hand the clicks back to the user.
- The deploy form can silently reset container disk to 15 GB when a template is saved. Check the "Total disk" line in the `Deploying ... Total / hour` block before clicking Deploy Pod. If it reverted, save the disk size as a template override and recheck.
- Terminate in one scripted pass: open the pod's page, Stop, confirm Stop Pod, then Terminate, then confirm Terminate Pod. Verify the pod id is gone from the page text and read the balance. A stopped pod still bills its disk.
- Measured 2026-10-31: A40 48 GB at $0.59/hr plus $0.021/hr for 150 GB disk. Two test pods plus downloads cost about $0.32 in total.

Detailed download script: `templates/pod-model-download.sh`.

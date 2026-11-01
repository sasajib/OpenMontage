"""WAN 2.2 Lightning image-to-video on the user's RunPod endpoint.
Usage: PYTHONPATH=. .venv/bin/python wan_i2v.py <image.png> "<prompt>" <out.mp4> [seed]
Release the endpoint first (workers.max=1), park it after. Env from .env: RUNPOD_API_KEY, RUNPOD_WAN_I2V_ENDPOINT_ID."""
import sys
import base64, json, os, time, requests
from pathlib import Path
if len(sys.argv) < 4:
    sys.exit('Usage: wan_i2v.py <image.png> "<prompt>" <out.mp4> [seed]')

EP = os.environ["RUNPOD_WAN_I2V_ENDPOINT_ID"]
KEY = os.environ["RUNPOD_API_KEY"]
RATE = 3.49  # $/hr BLACKWELL_96
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
here = Path(__file__).parent
image_path, prompt_text, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 901
img = base64.b64encode(Path(image_path).read_bytes()).decode()
body = {"input": {"task": "video",
    "prompt": prompt_text,
    "negative_prompt": "people, person, face, hands, text, watermark, logo, blurry, distorted, jittery, flicker",
    "width": 1280, "height": 720, "num_frames": 81, "fps": 16, "seed": seed,
    "num_inference_steps": 4, "guidance_scale": 1.0,
    "input_reference_b64": img,
}}
t0 = time.time()
r = requests.post(f"https://api.runpod.ai/v2/{EP}/run", headers=H, json=body, timeout=60)
r.raise_for_status(); jid = r.json()["id"]; print("job", jid, flush=True)
last = None
while True:
    time.sleep(10)
    s = requests.get(f"https://api.runpod.ai/v2/{EP}/status/{jid}", headers=H, timeout=30).json()
    st = s.get("status")
    if st != last:
        print(f"{time.time()-t0:6.0f}s {st}", flush=True); last = st
    if st in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"): break
    if time.time() - t0 > 1800: print("giving up"); break
meta = {k: s.get(k) for k in ("status", "executionTime", "delayTime", "workerId")}
out = s.get("output")
if st == "COMPLETED" and isinstance(out, dict) and out.get("data_b64"):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True); Path(out_path).write_bytes(base64.b64decode(out["data_b64"]))
    meta["content_type"] = out.get("content_type"); meta["size_bytes"] = out.get("size_bytes")
    meta["saved"] = out_path
else:
    meta["output_head"] = json.dumps(out)[:1500] if out is not None else None
    meta["error"] = str(s.get("error"))[:1500]
meta["wall_s"] = round(time.time() - t0, 1)
meta["est_cost_usd"] = round(((s.get("executionTime") or 0) + (s.get("delayTime") or 0)) / 3.6e6 * RATE, 4)
print(json.dumps(meta, indent=1))

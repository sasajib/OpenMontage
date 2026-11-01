"""Qwen image endpoints on RunPod.
Usage: t2i:  qwen_image.py t2i "<prompt>" <out.png> [size WxH] [seed]
       edit: qwen_image.py edit "<prompt>" <out.png> <input.png> [seed]
Release the endpoint first (workers.max=1), park it after. Env: RUNPOD_API_KEY, RUNPOD_QWEN_IMAGE_ENDPOINT_ID / RUNPOD_QWEN_EDIT_ENDPOINT_ID."""
import base64, json, os, sys, time, requests
from pathlib import Path
if len(sys.argv) < 4:
    sys.exit('Usage: qwen_image.py t2i "<prompt>" <out.png> [WxH] [seed]  |  qwen_image.py edit "<prompt>" <out.png> <input.png> [seed]')
mode, prompt_text, out_file = sys.argv[1], sys.argv[2], sys.argv[3]; here = Path(__file__).parent
KEY = os.environ["RUNPOD_API_KEY"]; RATE = 3.49
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
if mode == "t2i":
    EP = os.environ["RUNPOD_QWEN_IMAGE_ENDPOINT_ID"]
    size = sys.argv[4] if len(sys.argv) > 4 else "1664x928"; seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    body = {"input": {"prompt": prompt_text, "size": size, "seed": seed}}
    out_path = Path(out_file)
else:
    EP = os.environ["RUNPOD_QWEN_EDIT_ENDPOINT_ID"]
    img = base64.b64encode(Path(sys.argv[4]).read_bytes()).decode(); seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    body = {"input": {"route": "/v1/images/edits", "body": {"prompt": prompt_text, "image_b64": img, "seed": seed}}}
    out_path = Path(out_file)
t0 = time.time()
r = requests.post(f"https://api.runpod.ai/v2/{EP}/run", headers=H, json=body, timeout=60); r.raise_for_status()
jid = r.json()["id"]; print(mode, "job", jid, flush=True); last = None
while True:
    time.sleep(8)
    s = requests.get(f"https://api.runpod.ai/v2/{EP}/status/{jid}", headers=H, timeout=30).json(); st = s.get("status")
    if st != last: print(f"{time.time()-t0:6.0f}s {st}", flush=True); last = st
    if st in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT") or time.time() - t0 > 1500: break
meta = {k: s.get(k) for k in ("status", "executionTime", "delayTime", "workerId")}
out = s.get("output")
b64 = None
if isinstance(out, dict):
    if out.get("data") and isinstance(out["data"], list): b64 = out["data"][0].get("b64_json")
    b64 = b64 or out.get("data_b64")
    meta["metrics"] = out.get("metrics")
if st == "COMPLETED" and b64:
    out_path.parent.mkdir(parents=True, exist_ok=True); out_path.write_bytes(base64.b64decode(b64)); meta["saved"] = str(out_path)
else:
    meta["output_head"] = json.dumps(out)[:1500]; meta["error"] = str(s.get("error"))[:800]
meta["wall_s"] = round(time.time() - t0, 1)
meta["est_cost_usd"] = round(((s.get("executionTime") or 0) + (s.get("delayTime") or 0)) / 3.6e6 * RATE, 4)
print(json.dumps(meta, indent=1, default=str))

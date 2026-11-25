"""Reality check for AI-generated stills and clips (the hard gate before any paid downstream step).

Runs independent local checks and merges them into one PASS / REVIEW / REJECT report:

  anatomy     MediaPipe pose + hands per frame: people count, hand count, limbs leaving the frame
  identity    InsightFace embedding of every detected face vs a reference image (drift = different person)
  continuity  dominant wardrobe colour of the main person across frames (a suit that changes colour fails)
  camera      optical-flow magnitude per second: static / slow / fast, so "static" prompts can be verified
  vlm         optional: a vision model reads sampled frames against the reality checklist (gear geometry,
              prop provenance, environment, cast count, framing) and the scene prompt

Everything is CPU-only. The VLM pass needs OPENAI_API_KEY and costs a few cents per clip.

Usage:  reality_check.execute({"input_path": clip_or_still, "reference_face": sheet.png, "scene_prompt": "...",
                               "expect": {"people": 1, "camera": "static"}, "vlm": true})
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, Determinism, ExecutionMode, ResourceProfile, ToolResult, ToolStability, ToolStatus, ToolTier

MODELS = Path(__file__).resolve().parents[2] / "models" / "reality_check"
IMAGE = {".png", ".jpg", ".jpeg", ".webp"}

CHECKLIST = """You are the reality-check reviewer for AI-generated film footage. Judge ONLY what is physically or logically wrong, not taste.
Check every frame for:
1. Anatomy: exactly the expected number of people; each with two arms, two hands, two legs; no fused, extra or melting limbs; eyes natural.
2. Gear geometry: every rope, strap, cable, tool works the way the real thing does (rope passes THROUGH a carabiner, a screw is seated, an axe is held by the shaft, crampons on boots). Trace each rope end to end.
3. Prop provenance: first list EVERY object in the frame (held, worn, planted in the ground, lying around). For each one ask: could this character have carried it here, or would it exist in this place? Anything that fails is CRITICAL. Examples: a flagpole or flag on a pole on a mountain summit (nobody carries a pole up a mountain; a real climber ties the flag to an ice axe or holds it), furniture in a desert, a lit lantern nobody packed, a rope that comes from nowhere.
4. Environment consistency: surfaces and clothing show the stated conditions (frost at -30 C, dust in a desert, wet in rain).
5. Cast count: only the planned people are present.
6. Framing: the subject is fully inside the frame when the body matters; shot size and angle match the scene prompt.
7. Physics: weight, tension, direction of forces (a taut rope on a hanging climber, snow falling down, flags blowing with the wind).
8. Continuity across frames: same wardrobe, gear, light and face from first to last frame; no object appearing, vanishing or changing.
9. Camera: did the camera do the move the prompt asked for (static means static)?
Respond ONLY with JSON: {"verdict": "PASS"|"REVIEW"|"REJECT", "findings": [{"frame": <index>, "category": <one of anatomy|gear|prop|environment|cast|framing|physics|continuity|camera>, "severity": "critical"|"major"|"minor", "note": "<one sentence>"}]}.
A critical finding is one a viewer would notice as fake. Be strict: beautiful-but-wrong is REJECT."""


class RealityCheck(BaseTool):
    name = "reality_check"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "mediapipe"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    dependencies = ["cmd:ffmpeg", "cmd:ffprobe", "python:mediapipe", "python:cv2", "python:insightface", "python:onnxruntime"]
    install_instructions = (
        "pip install mediapipe insightface onnxruntime opencv-python-headless; then download the MediaPipe task files into models/reality_check/: "
        "pose_landmarker_lite.task, hand_landmarker.task (https://storage.googleapis.com/mediapipe-models/...). "
        "InsightFace downloads buffalo_sc on first use. Set OPENAI_API_KEY for the optional VLM pass."
    )
    agent_skills = ["video-reality-check", "generated-visual-anatomy-qa"]
    best_for = ["gate generated stills before image-to-video", "gate generated clips before the edit", "post-render spot check"]
    capabilities = ["anatomy_check", "identity_drift", "wardrobe_continuity", "camera_motion", "vlm_reality_review"]
    input_schema = {
        "type": "object",
        "required": ["input_path"],
        "properties": {
            "input_path": {"type": "string", "description": "still (png/jpg/webp) or clip (mp4/mov/webm)"},
            "reference_face": {"type": "string", "description": "image of the character for identity drift (optional)"},
            "scene_prompt": {"type": "string", "description": "the still/clip prompt, given to the VLM pass"},
            "expect": {"type": "object", "description": "{'people': int, 'camera': 'static'|'slow'|'moving', 'hands_visible': bool}"},
            "fps": {"type": "number", "default": 2, "description": "frames per second to sample from a clip"},
            "vlm": {"type": "boolean", "default": False, "description": "run the vision-model checklist pass (needs OPENAI_API_KEY)"},
            "vlm_model": {"type": "string", "description": "default: REALITY_CHECK_VLM_MODEL or glm-5.3-flash on z.ai / gpt-4.1-mini on OpenAI"},
            "output_dir": {"type": "string", "description": "where frames + report go (default: <input>.reality/)"},
        },
    }
    output_schema = {"type": "object", "properties": {"verdict": {"type": "string"}, "report_path": {"type": "string"}, "findings": {"type": "array"}}}
    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=2048, vram_mb=0, disk_mb=500)
    idempotency_key_fields = ["input_path", "reference_face", "fps", "vlm"]
    side_effects = ["writes frames and report.json to output_dir"]
    user_visible_verification = ["open report.md; open any frame listed under findings at full size"]

    # thresholds (tuned on the Everest v2 takes)
    FACE_SIM_MIN = 0.20        # cosine vs reference below this = different person (frost, goggles, masks lower it)
    FACE_DROP = 0.6            # a frame below FACE_DROP * best frame similarity = the face drifted during the clip
    FACE_STEP_MIN = 0.55       # cosine between consecutive detected faces below this = morph
    COLOUR_JUMP = 28.0         # mean |dH,dS,dV| of the person's torso between consecutive frames
    FLOW_STATIC = 0.6          # px/frame mean magnitude at 320 px width
    FLOW_FAST = 4.0

    def get_status(self) -> ToolStatus:
        base = super().get_status()
        if base != ToolStatus.AVAILABLE:
            return base
        if not (MODELS / "pose_landmarker_lite.task").exists() or not (MODELS / "hand_landmarker.task").exists():
            self._status_reason = f"MediaPipe task files missing in {MODELS}. {self.install_instructions}"
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.03 if inputs.get("vlm") else 0.0

    # ---------------------------------------------------------------- main
    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        src = Path(inputs["input_path"])
        if not src.exists():
            return ToolResult(success=False, error=f"Input not found: {src}")
        out = Path(inputs.get("output_dir") or (src.parent / f"{src.stem}.reality"))
        out.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        try:
            frames = self._frames(src, out, float(inputs.get("fps", 2)))
            expect = inputs.get("expect") or {}
            findings: list[dict] = []
            anatomy = self._anatomy(frames, expect, findings)
            identity = self._identity(frames, inputs.get("reference_face"), findings)
            continuity = self._continuity(frames, findings) if len(frames) > 1 else {}
            camera = self._camera(src, expect, findings) if len(frames) > 1 and src.suffix.lower() not in IMAGE else {}
            vlm = self._vlm(frames, inputs, findings) if inputs.get("vlm") else {"skipped": True}
            verdict = self._verdict(findings)
            report = {"input": str(src), "frames": len(frames), "verdict": verdict, "findings": findings,
                      "anatomy": anatomy, "identity": identity, "continuity": continuity, "camera": camera, "vlm": vlm,
                      "seconds": round(time.time() - t0, 1)}
            (out / "report.json").write_text(json.dumps(report, indent=1))
            (out / "report.md").write_text(self._markdown(report))
            return ToolResult(success=True, data={"verdict": verdict, "report_path": str(out / "report.md"), "findings": findings,
                                                  "frames_dir": str(out), "summary": {"anatomy": anatomy, "identity": identity, "continuity": continuity, "camera": camera}})
        except Exception as e:  # noqa: BLE001
            return ToolResult(success=False, error=f"{type(e).__name__}: {e}")

    # ---------------------------------------------------------------- frames
    def _frames(self, src: Path, out: Path, fps: float) -> list[Path]:
        for f in out.glob("f_*.png"):
            f.unlink()
        if src.suffix.lower() in IMAGE:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), str(out / "f_000.png")], check=True)
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"fps={fps}", str(out / "f_%03d.png")], check=True)
        return sorted(out.glob("f_*.png"))

    # ---------------------------------------------------------------- anatomy
    def _anatomy(self, frames: list[Path], expect: dict, findings: list) -> dict:
        import cv2
        import mediapipe as mp
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision
        pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=str(MODELS / "pose_landmarker_lite.task")), num_poses=4, min_pose_detection_confidence=0.4))
        hands = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=str(MODELS / "hand_landmarker.task")), num_hands=6, min_hand_detection_confidence=0.4))
        want_people = expect.get("people")
        per = []
        for i, f in enumerate(frames):
            img = cv2.imread(str(f)); rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mimg = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            p = pose.detect(mimg); h = hands.detect(mimg)
            # keep only confident, non-duplicate poses (close-ups spawn phantom second people)
            kept = []
            for lm in p.pose_landmarks:
                vis = sum(1 for j in range(33) if getattr(lm[j], "visibility", 1.0) > 0.5)
                if vis < 8:
                    continue
                if any(abs(lm[0].x - k[0].x) < 0.12 and abs(lm[0].y - k[0].y) < 0.12 for k in kept):
                    continue
                kept.append(lm)
            n_people = len(kept); n_hands = len(h.hand_landmarks)
            edge = 0
            for lm in kept:
                # ankles (27, 28) and wrists (15, 16) outside the frame while the hip is inside = limb cut by the frame
                hip_in = 0 <= lm[23].y <= 1 and 0 <= lm[24].y <= 1
                if hip_in and any(not (0 <= lm[j].y <= 1 and 0 <= lm[j].x <= 1) for j in (27, 28)):
                    edge += 1
            rec = {"frame": i, "people": n_people, "hands": n_hands, "legs_cut": edge}
            per.append(rec)
            if n_people and n_hands > 2 * n_people:
                findings.append({"frame": i, "category": "anatomy", "severity": "critical", "note": f"{n_hands} hands for {n_people} person(s)"})
        pose.close(); hands.close()
        people = [r["people"] for r in per]
        hands_max = max((r["hands"] for r in per), default=0)
        if want_people is not None:
            over = [r["frame"] for r in per if r["people"] > want_people]
            if over:
                sev = "critical" if len(over) >= max(2, len(per) // 4) else "minor"
                findings.append({"frame": over[0], "category": "cast", "severity": sev, "note": f"more people than expected ({want_people}) in {len(over)}/{len(per)} frames"})
        return {"people_per_frame": people, "max_hands": hands_max, "legs_cut_frames": [r["frame"] for r in per if r["legs_cut"]]}

    # ---------------------------------------------------------------- identity
    def _identity(self, frames: list[Path], ref: str | None, findings: list) -> dict:
        import cv2
        import numpy as np
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(name="buffalo_sc", providers=["CPUExecutionProvider"], allowed_modules=["detection", "recognition"])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        cos = lambda a, b: float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        ref_emb = None
        if ref and Path(ref).exists():
            rf = app.get(cv2.imread(ref))
            if rf:
                ref_emb = max(rf, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])).embedding
        sims, steps, prev, faces_seen = [], [], None, 0
        for i, f in enumerate(frames):
            det = app.get(cv2.imread(str(f)))
            if not det:
                sims.append(None); continue
            faces_seen += 1
            emb = max(det, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])).embedding
            if ref_emb is not None:
                s = cos(emb, ref_emb); sims.append(round(s, 3))
            else:
                sims.append(None)
            if prev is not None:
                st = cos(emb, prev); steps.append(round(st, 3))
                if st < self.FACE_STEP_MIN:
                    findings.append({"frame": i, "category": "continuity", "severity": "critical", "note": f"face morphs between frames (cos {st:.2f})"})
            prev = emb
        valid = [x for x in sims if x is not None]
        if valid:
            best = max(valid)
            if best < self.FACE_SIM_MIN:
                findings.append({"frame": sims.index(best), "category": "continuity", "severity": "critical", "note": f"no frame matches the reference face (best cos {best:.2f})"})
            else:
                bad = [i for i, x in enumerate(sims) if x is not None and (x < self.FACE_SIM_MIN or x < self.FACE_DROP * best)]
                if bad:
                    findings.append({"frame": bad[0], "category": "continuity", "severity": "critical", "note": f"face drifts from the reference in {len(bad)}/{len(valid)} frames (best cos {best:.2f}, worst {min(valid):.2f})"})
        return {"reference_used": ref_emb is not None, "faces_detected": faces_seen, "similarity_to_reference": sims, "frame_to_frame": steps}

    # ---------------------------------------------------------------- continuity (wardrobe colour)
    def _continuity(self, frames: list[Path], findings: list) -> dict:
        import cv2
        import numpy as np
        means, prev = [], None
        for i, f in enumerate(frames):
            img = cv2.imread(str(f)); h, w = img.shape[:2]
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
            # the most saturated 15 % of pixels = wardrobe / key object (works for any coloured subject on a neutral scene)
            sat = hsv[:, :, 1]; thr = np.percentile(sat, 85)
            m = sat >= thr
            if m.sum() < 200:
                means.append(None); continue
            mean = hsv[m].mean(axis=0); means.append([round(float(x), 1) for x in mean])
            if prev is not None:
                d = np.abs(mean - prev); d[0] = min(d[0], 180 - d[0])
                jump = float(d.mean())
                if jump > self.COLOUR_JUMP:
                    findings.append({"frame": i, "category": "continuity", "severity": "major", "note": f"dominant colour jumps (HSV delta {jump:.0f}) - wardrobe or light changed"})
            prev = mean
        return {"dominant_hsv_per_frame": means}

    # ---------------------------------------------------------------- camera (optical flow)
    def _camera(self, src: Path, expect: dict, findings: list) -> dict:
        import cv2
        import numpy as np
        cap = cv2.VideoCapture(str(src)); fps = cap.get(cv2.CAP_PROP_FPS) or 24
        prev = None; mags = []; sec = []
        n = 0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            g = cv2.cvtColor(cv2.resize(fr, (320, int(320 * fr.shape[0] / fr.shape[1]))), cv2.COLOR_BGR2GRAY)
            if prev is not None:
                flow = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                # global motion = median flow (subject motion is local, camera motion moves everything)
                mags.append(float(np.median(np.linalg.norm(flow, axis=2))))
            prev = g; n += 1
            if len(mags) >= fps:
                sec.append(round(float(np.mean(mags)), 2)); mags = []
        if mags:
            sec.append(round(float(np.mean(mags)), 2))
        cap.release()
        mean = float(np.mean(sec)) if sec else 0.0
        cls = "static" if mean < self.FLOW_STATIC else ("slow" if mean < self.FLOW_FAST else "fast")
        want = expect.get("camera")
        if want == "static" and cls != "static":
            findings.append({"frame": int(np.argmax(sec)) if sec else 0, "category": "camera", "severity": "major", "note": f"camera is {cls} (median flow {mean:.1f} px/frame) but a static shot was asked for"})
        if want == "slow" and cls == "fast":
            findings.append({"frame": int(np.argmax(sec)) if sec else 0, "category": "camera", "severity": "minor", "note": f"camera move is fast ({mean:.1f} px/frame); plan to use a short window"})
        return {"per_second_flow": sec, "class": cls}

    # ---------------------------------------------------------------- VLM
    def _vlm(self, frames: list[Path], inputs: dict, findings: list) -> dict:
        pick = frames if len(frames) <= 6 else [frames[int(i * (len(frames) - 1) / 5)] for i in range(6)]
        idx = [frames.index(p) for p in pick]
        key = os.environ.get("REALITY_CHECK_VLM_KEY") or os.environ.get("GLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base = os.environ.get("REALITY_CHECK_VLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4" if os.environ.get("GLM_API_KEY") and not os.environ.get("REALITY_CHECK_VLM_KEY") else "https://api.openai.com/v1")
        model = inputs.get("vlm_model") or os.environ.get("REALITY_CHECK_VLM_MODEL", "glm-5.3-flash" if "z.ai" in base else "gpt-4.1-mini")
        if not key:
            # agent pass: no vision API configured, so the agent (Claude) reads the frames itself with the same checklist
            prompt = CHECKLIST + "\n\nScene prompt:\n" + (inputs.get("scene_prompt") or "(none)") + f"\nExpectations: {json.dumps(inputs.get('expect') or {})}"
            pf = pick[0].parent / "agent_pass.md"
            pf.write_text(prompt + "\n\nFrames to open at full size (index = frame number in the report):\n" + "\n".join(f"{i}: {p}" for i, p in zip(idx, pick)) +
                          "\n\nWrite your findings into report.json under 'findings' with source 'agent', then recompute the verdict (any critical = REJECT).\n")
            findings.append({"frame": idx[0], "category": "vlm", "severity": "major", "note": "agent pass pending: no vision API key; open agent_pass.md and the listed frames", "source": "agent-pending"})
            return {"mode": "agent", "prompt_file": str(pf), "frames": idx}
        import urllib.request
        content = [{"type": "text", "text": CHECKLIST + "\n\nScene prompt the footage was generated from:\n" + (inputs.get("scene_prompt") or "(none given)") +
                    f"\n\nExpectations: {json.dumps(inputs.get('expect') or {})}\nFrames are in time order, index 0..{len(pick) - 1}."}]
        for p in pick:
            b = base64.b64encode(p.read_bytes()).decode()
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b}", "detail": "high"}})
        payload = {"model": model, "messages": [{"role": "user", "content": content}], "temperature": 0, "max_tokens": 1500}
        if "z.ai" in base:
            payload["thinking"] = {"type": "disabled"}
        else:
            payload["response_format"] = {"type": "json_object"}
        body = json.dumps(payload).encode()
        req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        raw = json.loads(urllib.request.urlopen(req, timeout=120).read())
        txt = raw["choices"][0]["message"]["content"] or ""
        try:
            res = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        except (json.JSONDecodeError, ValueError):
            return {"error": "non-JSON reply", "raw": txt[:500]}
        for f in res.get("findings", []):
            fi = f.get("frame", 0)
            f["frame"] = idx[fi] if isinstance(fi, int) and 0 <= fi < len(idx) else fi
            f["source"] = "vlm"
            findings.append(f)
        if res.get("verdict") == "REJECT" and not any(f.get("severity") == "critical" for f in findings):
            findings.append({"frame": idx[0], "category": "vlm", "severity": "critical", "note": "vision model verdict REJECT", "source": "vlm"})
        elif res.get("verdict") == "REVIEW" and not any(f.get("severity") in ("critical", "major") for f in findings):
            findings.append({"frame": idx[0], "category": "vlm", "severity": "major", "note": "vision model verdict REVIEW", "source": "vlm"})
        return {"model": model, "base": base, "verdict": res.get("verdict"), "frames_sent": idx, "usage": raw.get("usage")}

    # ---------------------------------------------------------------- verdict + report
    @staticmethod
    def _verdict(findings: list) -> str:
        if any(f.get("severity") == "critical" for f in findings):
            return "REJECT"
        if any(f.get("severity") == "major" for f in findings):
            return "REVIEW"
        return "PASS"

    @staticmethod
    def _markdown(r: dict) -> str:
        lines = [f"# Reality check: {Path(r['input']).name}", "", f"**Verdict: {r['verdict']}**  ({r['frames']} frames, {r['seconds']} s)", ""]
        if r["findings"]:
            lines += ["| frame | category | severity | note |", "|---|---|---|---|"]
            lines += [f"| {f.get('frame')} | {f.get('category')} | {f.get('severity')} | {f.get('note')} |" for f in r["findings"]]
        else:
            lines.append("No findings.")
        a, i, c, cam = r["anatomy"], r["identity"], r["continuity"], r["camera"]
        lines += ["", f"- people per frame: {a.get('people_per_frame')}; max hands: {a.get('max_hands')}; legs cut: {a.get('legs_cut_frames')}",
                  f"- identity: reference={i.get('reference_used')}, faces={i.get('faces_detected')}, sim={i.get('similarity_to_reference')}, step={i.get('frame_to_frame')}",
                  f"- camera: {cam.get('class')} flow/s={cam.get('per_second_flow')}" if cam else "- camera: n/a (still)",
                  f"- vlm: {r['vlm']}"]
        return "\n".join(lines) + "\n"

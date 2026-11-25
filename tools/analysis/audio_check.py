"""Audio reality check for generated voice lines, music cues and the final mix (the audio half of the reality-check gate).

Modes
  lines  one TTS/dialogue file per script section: round-trip transcription (faster-whisper) -> word error rate, truncation
         (missing tail words), hallucinated words, leading/trailing silence, clipping; pace in words/min vs the script's
         delivery cue; a prosody profile (pitch range, energy variance, pauses) as the emotion proxy vs the cue's energy word.
  music  one cue: duration vs required, abrupt ending (no fade), clipping, loudness curve checked against a music plan
         (silence windows must be quiet, 'build' sections louder than what precedes them), tempo estimate.
  mix    the final render: integrated LUFS / true peak vs the platform target, clipping, dropouts and unexpected gaps,
         dialogue intelligibility by re-transcribing each line window from the mix, music-under-dialogue depth (ducking).

Sources: ITU-R BS.1770 / EBU R128 loudness via ffmpeg ebur128; YouTube ~-14 LUFS, -1 dBTP; music under speech 10-20 dB below
dialogue (mixing guides); round-trip ASR + WER is the standard TTS validation (NVIDIA Riva docs, 2026 TTS papers); emotion
recognition proper needs emotion2vec/funasr which is not installed, so the prosody profile is an explicit proxy, not a verdict.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, Determinism, ExecutionMode, ResourceProfile, ToolResult, ToolStability, ToolTier

PACE_WPM = {"slow": (0, 135), "measured": (110, 160), "conversational": (140, 180), "brisk": (160, 200), "fast": (180, 320)}
TARGETS = {"youtube": (-14.0, -1.0), "broadcast": (-23.0, -1.0), "streaming_film": (-27.0, -2.0), "podcast": (-16.0, -1.0)}


class AudioCheck(BaseTool):
    name = "audio_check"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "ffmpeg"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    dependencies = ["cmd:ffmpeg", "cmd:ffprobe", "python:librosa", "python:soundfile", "python:jiwer", "python:faster_whisper"]
    install_instructions = "pip install librosa soundfile jiwer faster-whisper (the whisper model downloads on first use)"
    agent_skills = ["video-reality-check"]
    best_for = ["gate TTS lines before the edit", "gate a generated music cue before compose", "check the final mix before publish"]
    capabilities = ["round_trip_wer", "truncation_detection", "pace_vs_cue", "prosody_profile", "loudness_r128", "clipping", "dropouts", "music_plan_check", "ducking_depth"]
    input_schema = {
        "type": "object",
        "required": ["mode", "input_path"],
        "properties": {
            "mode": {"type": "string", "enum": ["lines", "music", "mix"]},
            "input_path": {"type": "string", "description": "lines: directory of line files or one file; music: the cue; mix: the final mp4/wav"},
            "script_path": {"type": "string", "description": "script.json (sections with text, start_seconds, delivery_cues); lines + mix"},
            "line_map": {"type": "object", "description": "lines: {section_id: file path}. Default: files named <section_id>*.mp3|wav in input_path"},
            "music_plan": {"type": "object", "description": "music: {'required_seconds': 65, 'silence_windows': [[21,24]], 'builds': [[38,54]], 'fade_out_seconds': 2}"},
            "platform": {"type": "string", "enum": list(TARGETS), "default": "youtube"},
            "names": {"type": "array", "items": {"type": "string"}, "description": "proper names the ASR may misspell (default: the script's pronunciation_guides words)"},
            "expected_silence_windows": {"type": "array", "items": {"type": "array"}, "description": "mix: [[start, end]] windows where silence is intentional (no dropout findings there)"},
            "whisper_model": {"type": "string", "default": "base.en"},
            "output_dir": {"type": "string"},
        },
    }
    output_schema = {"type": "object", "properties": {"verdict": {"type": "string"}, "report_path": {"type": "string"}, "findings": {"type": "array"}}}
    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=2048, vram_mb=0, disk_mb=300)
    idempotency_key_fields = ["mode", "input_path", "script_path"]
    side_effects = ["writes report.json/report.md and temp wavs to output_dir"]
    user_visible_verification = ["listen to every line or window named in the findings"]

    WER_MAJOR, WER_CRIT = 0.15, 0.35
    CLIP_FRAC = 0.0005          # fraction of samples at full scale
    END_CUT_DB = -20.0          # last 50 ms louder than this relative to the body = abrupt cut
    DUCK_MIN_DB = 6.0           # music must sit at least this far under dialogue (guides say 10-20)
    SILENCE_WINDOW_DB = -35.0   # a planned silence must be below this (RMS dBFS)
    DROPOUT_DB = -30.0

    # ----------------------------------------------------------------- main
    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        mode = inputs["mode"]; src = Path(inputs["input_path"])
        if not src.exists():
            return ToolResult(success=False, error=f"Input not found: {src}")
        out = Path(inputs.get("output_dir") or (src.parent / f"{src.stem}.audiocheck" if src.is_file() else src / ".audiocheck"))
        out.mkdir(parents=True, exist_ok=True)
        t0 = time.time(); findings: list[dict] = []
        try:
            if mode == "lines":
                detail = self._lines(src, inputs, out, findings)
            elif mode == "music":
                detail = self._music(src, inputs, out, findings)
            else:
                detail = self._mix(src, inputs, out, findings)
            verdict = "REJECT" if any(f["severity"] == "critical" for f in findings) else ("REVIEW" if any(f["severity"] == "major" for f in findings) else "PASS")
            report = {"input": str(src), "mode": mode, "verdict": verdict, "findings": findings, "detail": detail, "seconds": round(time.time() - t0, 1)}
            (out / "report.json").write_text(json.dumps(report, indent=1, default=str))
            (out / "report.md").write_text(self._markdown(report))
            return ToolResult(success=True, data={"verdict": verdict, "report_path": str(out / "report.md"), "findings": findings, "detail": detail})
        except Exception as e:  # noqa: BLE001
            return ToolResult(success=False, error=f"{type(e).__name__}: {e}")

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _wav(src: Path, out: Path, sr: int = 16000):
        import soundfile as sf
        w = out / (src.stem + f".{sr}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(sr), str(w)], check=True)
        y, _ = sf.read(str(w), dtype="float32")
        return y, sr, w

    @staticmethod
    def _rms_db(y, sr, win=0.05):
        import numpy as np
        n = max(1, int(sr * win)); k = len(y) // n
        if k == 0:
            return np.array([-120.0])
        blocks = y[: k * n].reshape(k, n)
        return 20 * np.log10(np.sqrt((blocks ** 2).mean(axis=1)) + 1e-9)

    def _technical(self, y, sr, label: str, findings: list) -> dict:
        import numpy as np
        peak = float(np.abs(y).max()) if len(y) else 0.0
        clip = float((np.abs(y) >= 0.999).mean()) if len(y) else 0.0
        db = self._rms_db(y, sr); body = float(np.percentile(db, 75))
        lead = float(np.argmax(db > body - 30) * 0.05) if (db > body - 30).any() else len(y) / sr
        rev = db[::-1]; trail = float(np.argmax(rev > body - 30) * 0.05) if (rev > body - 30).any() else 0.0
        end_level = float(db[-1]) - body if len(db) else -99.0
        if clip > self.CLIP_FRAC:
            findings.append({"where": label, "category": "clipping", "severity": "major", "note": f"{clip * 100:.2f} % of samples at full scale"})
        end_abs = float(db[-1]) if len(db) else -120.0
        if end_level > self.END_CUT_DB and trail < 0.1 and end_abs > -25.0:
            findings.append({"where": label, "category": "cutoff", "severity": "major", "note": f"ends abruptly at {end_abs:.0f} dBFS, no tail or fade"})
        return {"peak_dbfs": round(20 * np.log10(peak + 1e-9), 1), "clip_fraction": clip, "lead_silence_s": round(lead, 2), "trail_silence_s": round(trail, 2), "end_level_rel_db": round(end_level, 1), "duration_s": round(len(y) / sr, 2)}

    def _transcribe(self, wav: Path, model_size: str):
        from faster_whisper import WhisperModel
        if not hasattr(self, "_wm") or self._wm_size != model_size:
            self._wm = WhisperModel(model_size, device="cpu", compute_type="int8"); self._wm_size = model_size
        segs, _ = self._wm.transcribe(str(wav), beam_size=5, word_timestamps=True, condition_on_previous_text=False)
        words = [w for s in segs for w in (s.words or [])]
        return " ".join(w.word.strip() for w in words), words

    _NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen", "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen", "19": "nineteen", "20": "twenty", "30": "thirty", "40": "forty", "50": "fifty", "60": "sixty", "90": "ninety", "100": "hundred"}
    _CONTR = {"'s": " is", "'m": " am", "'re": " are", "'ve": " have", "'ll": " will", "'d": " would", "n't": " not"}

    @classmethod
    def _norm(cls, t: str) -> list[str]:
        """lowercase, expand contractions and small numbers, strip punctuation: 'Anchor's gone, 20 seconds' == 'anchor is gone twenty seconds'."""
        t = t.lower()
        for k, v in cls._CONTR.items():
            t = t.replace(k, v)
        t = re.sub(r"[^a-z0-9 ]+", " ", t)
        return [cls._NUM.get(w, w) for w in t.split()]

    def _wer(self, ref: str, hyp: str, names: list[str] | None = None) -> dict:
        """Word error rate with two forgivenesses: proper names (ASR spells 'Shakil' as 'Shaquille') map to the name when the
        edit distance is small, and compound/spacing differences ('base camp' vs 'Basecamp') are forgiven via a spaceless CER."""
        import jiwer
        rw, hw = self._norm(ref), self._norm(hyp)
        for n in [x.lower() for x in (names or [])]:
            hw = [n if (w != n and abs(len(w) - len(n)) <= 4 and w[:3] == n[:3]) else w for w in hw]
        r, h = " ".join(rw), " ".join(hw)
        if not r:
            return {"wer": 0.0}
        o = jiwer.process_words(r, h or "<empty>")
        cer = jiwer.cer(r.replace(" ", ""), h.replace(" ", "") or "x")
        wer = 0.0 if cer < 0.06 else round(o.wer, 3)
        return {"wer": wer, "cer_spaceless": round(cer, 3), "subs": o.substitutions, "dels": o.deletions, "ins": o.insertions, "ref": r, "hyp": h}

    def _prosody(self, y, sr) -> dict:
        import librosa
        import numpy as np
        f0, vf, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr, frame_length=1024)
        f0v = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        db = self._rms_db(y, sr, 0.02); body = np.percentile(db, 75)
        pauses = int(((db < body - 25).astype(int)[1:] - (db < body - 25).astype(int)[:-1] == 1).sum())
        return {"f0_median_hz": round(float(np.median(f0v)), 1) if len(f0v) else None, "f0_range_st": round(float(12 * np.log2(np.percentile(f0v, 95) / np.percentile(f0v, 5))), 1) if len(f0v) > 10 else None,
                "energy_var_db": round(float(np.std(db[db > body - 25])), 1) if (db > body - 25).any() else None, "pauses": pauses}

    # ----------------------------------------------------------------- lines
    def _lines(self, src: Path, inputs: dict, out: Path, findings: list) -> dict:
        script = json.load(open(inputs["script_path"])) if inputs.get("script_path") else {"sections": []}
        lm = inputs.get("line_map") or {}
        if not lm and src.is_dir():
            for s in script["sections"]:
                m = sorted(list(src.glob(f"{s['id']}*.wav")) + list(src.glob(f"{s['id']}*.mp3")))
                if m:
                    lm[s["id"]] = str(m[0])
        if not lm and src.is_file():
            lm = {s["id"]: str(src) for s in script["sections"][:1]} or {"line": str(src)}
        names = inputs.get("names") or [g["word"] for sec in script["sections"] for g in sec.get("pronunciation_guides", [])] or []
        res = {}
        for sec in script["sections"] or [{"id": k, "text": ""} for k in lm]:
            sid = sec["id"]
            if sid not in lm:
                findings.append({"where": sid, "category": "missing", "severity": "critical", "note": "no audio file for this script line"}); continue
            y, sr, w = self._wav(Path(lm[sid]), out)
            tech = self._technical(y, sr, sid, findings)
            hyp, words = self._transcribe(w, inputs.get("whisper_model", "base.en"))
            wer = self._wer(sec.get("text", ""), hyp, names)
            ref_w = self._norm(sec.get("text", "")); hyp_w = self._norm(wer.get("hyp", hyp))
            if wer["wer"] >= self.WER_CRIT:
                findings.append({"where": sid, "category": "intelligibility", "severity": "critical", "note": f"WER {wer['wer']:.2f}: heard '{hyp}'"})
            elif wer["wer"] >= self.WER_MAJOR:
                findings.append({"where": sid, "category": "intelligibility", "severity": "major", "note": f"WER {wer['wer']:.2f}: heard '{hyp}'"})
            if ref_w and len(hyp_w) >= 2 and ref_w[-1] not in hyp_w[-2:]:
                findings.append({"where": sid, "category": "truncation", "severity": "critical", "note": f"last word '{ref_w[-1]}' not heard at the end (heard '...{' '.join(hyp_w[-3:])}')"})
            if wer.get("ins", 0) >= 2:
                findings.append({"where": sid, "category": "hallucination", "severity": "major", "note": f"{wer['ins']} extra words heard"})
            speech_s = (words[-1].end - words[0].start) if words else tech["duration_s"]
            wpm = round(len(ref_w) / max(speech_s, 0.3) * 60) if ref_w else None
            cue = (sec.get("delivery_cues") or {}).get("pace")
            if wpm and cue in PACE_WPM and len(ref_w) >= 7:  # wpm is meaningless on short lines (count after contraction expansion)
                lo, hi = PACE_WPM[cue]
                if not (lo <= wpm <= hi):
                    findings.append({"where": sid, "category": "pace", "severity": "major", "note": f"{wpm} wpm but the cue is '{cue}' ({lo}-{hi})"})
            pro = self._prosody(y, sr)
            energy_word = ((sec.get("delivery_cues") or {}).get("energy") or sec.get("speaker_directions") or "").lower()
            if pro["f0_range_st"] is not None:
                if any(k in energy_word for k in ("panic", "shout", "urgent", "sharp", "rising")) and pro["f0_range_st"] < 6:
                    findings.append({"where": sid, "category": "emotion_proxy", "severity": "major", "note": f"flat delivery (pitch range {pro['f0_range_st']} st) for a '{energy_word[:40]}' cue"})
                if any(k in energy_word for k in ("calm", "quiet", "exhausted", "whisper", "flat")) and pro["f0_range_st"] > 14:
                    findings.append({"where": sid, "category": "emotion_proxy", "severity": "minor", "note": f"very animated (pitch range {pro['f0_range_st']} st) for a '{energy_word[:40]}' cue"})
            slot = (sec.get("end_seconds", 0) - sec.get("start_seconds", 0)) if sec.get("end_seconds") else None
            if slot and tech["duration_s"] > slot + 0.3:
                findings.append({"where": sid, "category": "timing", "severity": "major", "note": f"line is {tech['duration_s']} s, slot is {slot} s"})
            res[sid] = {"file": lm[sid], **tech, "transcript": hyp, "wer": wer["wer"], "wpm": wpm, "pace_cue": cue, "prosody": pro}
        return res

    # ----------------------------------------------------------------- music
    def _music(self, src: Path, inputs: dict, out: Path, findings: list) -> dict:
        import librosa
        import numpy as np
        y, sr, w = self._wav(src, out, 22050)
        tech = self._technical(y, sr, "music", findings)
        plan = inputs.get("music_plan") or {}
        db = self._rms_db(y, sr, 1.0)  # 1 s blocks
        need = plan.get("required_seconds")
        if need and tech["duration_s"] < need - 0.5:
            findings.append({"where": "music", "category": "duration", "severity": "critical", "note": f"cue is {tech['duration_s']} s, {need} s required"})
        fade = plan.get("fade_out_seconds", 1.5)
        tail = db[-max(1, int(fade)):] if len(db) else []
        if len(db) > 3 and tail.max() > np.percentile(db, 75) - 6 and tech["end_level_rel_db"] > -15:
            findings.append({"where": "music", "category": "cutoff", "severity": "major", "note": "no fade-out: the cue ends at full level"})
        for a, b in plan.get("silence_windows", []):
            seg = db[int(a): int(b)]
            if len(seg) and seg.max() > self.SILENCE_WINDOW_DB:
                findings.append({"where": f"{a}-{b}s", "category": "music_plan", "severity": "major", "note": f"planned silence is not silent (max {seg.max():.0f} dBFS); duck it in the mix or regenerate"})
        for a, b in plan.get("builds", []):
            before = db[max(0, int(a) - 5): int(a)]; during = db[int(a): int(b)]
            if len(before) and len(during) and during.mean() <= before.mean() + 2:
                findings.append({"where": f"{a}-{b}s", "category": "music_plan", "severity": "major", "note": f"'build' section is not louder than what precedes it ({during.mean():.0f} vs {before.mean():.0f} dBFS)"})
        tempo = librosa.beat.beat_track(y=y, sr=sr)[0]
        tempo = float(np.atleast_1d(tempo)[0])
        return {**tech, "tempo_bpm": round(tempo, 1), "rms_db_per_second": [round(float(x), 1) for x in db]}

    # ----------------------------------------------------------------- mix
    def _mix(self, src: Path, inputs: dict, out: Path, findings: list) -> dict:
        import numpy as np
        y, sr, w = self._wav(src, out, 16000)
        tech = self._technical(y, sr, "mix", findings)
        ebu = subprocess.run(["ffmpeg", "-v", "info", "-i", str(src), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", ebu)[-1]); tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", ebu)[-1])
        lra = float(re.findall(r"LRA:\s+([\d.]+) LU", ebu)[-1])
        target, tp_max = TARGETS[inputs.get("platform", "youtube")]
        if abs(lufs - target) > 3:
            findings.append({"where": "mix", "category": "loudness", "severity": "major", "note": f"{lufs} LUFS vs {target} target ({inputs.get('platform', 'youtube')}); normalise before publish"})
        if tp > tp_max:
            findings.append({"where": "mix", "category": "loudness", "severity": "major", "note": f"true peak {tp} dBTP above {tp_max}"})
        db = self._rms_db(y, sr, 0.1); body = np.percentile(db, 75)
        # dropouts: < 300 ms holes more than 30 dB under the body, not at the very start/end
        low = db < body + self.DROPOUT_DB
        i = 0; holes = []
        while i < len(low):
            if low[i]:
                j = i
                while j < len(low) and low[j]:
                    j += 1
                t_s = i * 0.1
                if 1 <= (j - i) <= 3 and 5 < i < len(low) - 5 and not any(a - 0.5 <= t_s <= b + 0.5 for a, b in inputs.get("expected_silence_windows", [])):
                    holes.append(round(t_s, 1))
                i = j
            else:
                i += 1
        if holes:
            findings.append({"where": "mix", "category": "dropout", "severity": "major", "note": f"{len(holes)} sub-300 ms holes at {holes[:8]} s"})
        lines = {}
        if inputs.get("script_path"):
            script = json.load(open(inputs["script_path"]))
            names = inputs.get("names") or [g["word"] for sec in script["sections"] for g in sec.get("pronunciation_guides", [])] or []
            for sec in script["sections"]:
                a = float(sec["start_seconds"]); b = float(sec.get("end_seconds", a + 3)) + 0.4
                seg = out / f"win_{sec['id']}.wav"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, a - 0.2):.2f}", "-t", f"{b - a + 0.2:.2f}", "-i", str(w), str(seg)], check=True)
                hyp, _ = self._transcribe(seg, inputs.get("whisper_model", "base.en"))
                wer = self._wer(sec["text"], hyp, names)
                sev = "critical" if wer["wer"] >= self.WER_CRIT else ("major" if wer["wer"] >= self.WER_MAJOR else None)
                if sev:
                    findings.append({"where": sec["id"], "category": "intelligibility_in_mix", "severity": sev, "note": f"WER {wer['wer']:.2f} in the mix: heard '{hyp}' (music too loud or line cut?)"})
                # ducking: how far the bed drops under the line = median level of the 1.5 s before the line minus the
                # quietest 10th percentile during it (speech gaps expose the ducked bed). Intelligibility is the WER above;
                # a line is only flagged for ducking when it is both hard to hear and the bed did not drop.
                i0, i1 = int(a * 10), int(b * 10); pre = db[max(0, i0 - 15): i0]; dur = db[i0:i1]
                drop = float(np.median(pre) - np.percentile(dur, 10)) if len(pre) and len(dur) else None
                lines[sec["id"]] = {"transcript_in_mix": hyp, "wer": wer["wer"], "bed_drop_db": round(drop, 1) if drop is not None else None}
                if drop is not None and drop < 3.0 and wer["wer"] >= self.WER_MAJOR:
                    findings.append({"where": sec["id"], "category": "ducking", "severity": "major", "note": f"line hard to hear (WER {wer['wer']:.2f}) and the bed drops only {drop:.1f} dB under it; duck music 10-20 dB under speech"})
                elif drop is not None and drop < 3.0:
                    findings.append({"where": sec["id"], "category": "ducking", "severity": "minor", "note": f"bed drops only {drop:.1f} dB under the line (intelligible, but check on phone speakers)"})
        return {**tech, "integrated_lufs": lufs, "true_peak_dbtp": tp, "lra_lu": lra, "target": target, "lines": lines}

    # ----------------------------------------------------------------- report
    @staticmethod
    def _markdown(r: dict) -> str:
        lines = [f"# Audio check ({r['mode']}): {Path(r['input']).name}", "", f"**Verdict: {r['verdict']}**  ({r['seconds']} s)", ""]
        if r["findings"]:
            lines += ["| where | category | severity | note |", "|---|---|---|---|"] + [f"| {f['where']} | {f['category']} | {f['severity']} | {f['note']} |" for f in r["findings"]]
        else:
            lines.append("No findings.")
        d = r["detail"]
        if r["mode"] == "lines":
            lines += ["", "| line | WER | wpm | cue | f0 range st | transcript |", "|---|---|---|---|---|---|"]
            lines += [f"| {k} | {v['wer']} | {v['wpm']} | {v['pace_cue']} | {v['prosody'].get('f0_range_st')} | {v['transcript']} |" for k, v in d.items()]
        elif r["mode"] == "mix":
            lines += ["", f"- {d['integrated_lufs']} LUFS (target {d['target']}), true peak {d['true_peak_dbtp']} dBTP, LRA {d['lra_lu']} LU, clip {d['clip_fraction']}",
                      "", "| line | WER in mix | bed drop dB | heard |", "|---|---|---|---|"] + [f"| {k} | {v['wer']} | {v['bed_drop_db']} | {v['transcript_in_mix']} |" for k, v in d["lines"].items()]
        else:
            lines += ["", f"- {d['duration_s']} s, tempo ~{d['tempo_bpm']} bpm, peak {d['peak_dbfs']} dBFS, end level {d['end_level_rel_db']} dB rel body"]
        return "\n".join(lines) + "\n"

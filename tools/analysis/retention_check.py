"""Hook and retention check: measures a script or a rendered video against skills/creative/hook-and-retention.md.

Modes
  script  script.json: sentence length, banned filler phrases, digits in spoken text, total word budget, and the
          `promise` + `retention_map` metadata the gate requires.
  render  the final mp4: an empty or frozen opening, the longest stretch with no visual change (ffmpeg freezedetect),
          shot-length contrast and how many scene changes replace the whole frame (nothing carried over), and (with word timings) voice start and dead air between words.

The limits are the skill's numbers. A drifting background is not a freeze for ffmpeg, so a PASS on stillness is a
floor, not proof of pacing: the cold watch in the skill still applies.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from tools.base_tool import BaseTool, Determinism, ExecutionMode, ResourceProfile, ToolResult, ToolStability, ToolTier

LIMITS = {  # format: (sentence min, sentence max, longest still stretch in seconds)
    "short": (6, 14, 2.0),
    "long": (8, 18, 3.0),
}
HARD_MAX_WORDS = 22
FREEZE_MIN = 0.45   # seconds of identical picture that a viewer notices as a stall
BANNED = ["let's dive in", "lets dive in", "stay tuned", "in this video", "without further ado", "hey guys"]
FILLER = {"just", "simply", "really", "actually", "basically"}
MAP_BEATS = {"short": ["hook", "promise", "second_hook", "hero_moment", "payoff", "ending"],
             "long": ["cold_open", "re_hooks", "hero_moment", "turn", "close"]}


def _f(sev: str, cat: str, msg: str, at: float | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"severity": sev, "category": cat, "message": msg}
    if at is not None:
        d["at_seconds"] = round(at, 2)
    return d


class RetentionCheck(BaseTool):
    name = "retention_check"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "ffmpeg"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    dependencies = ["cmd:ffmpeg", "cmd:ffprobe"]
    install_instructions = "Install ffmpeg (ffprobe ships with it)."
    agent_skills: list[str] = []
    best_for = ["gate a script before the human approval", "measure hook and pacing on the final render"]
    capabilities = ["line_lint", "retention_map_check", "opening_check", "still_stretch_detection", "frozen_frame_detection", "shot_length_contrast", "carry_estimate", "voice_start", "dead_air"]
    input_schema = {
        "type": "object",
        "required": ["mode", "input_path"],
        "properties": {
            "mode": {"type": "string", "enum": ["script", "render"]},
            "input_path": {"type": "string", "description": "script: script.json; render: the final mp4"},
            "format": {"type": "string", "enum": ["short", "long"], "default": "short", "description": "short = under 90 s social; long = explainer or documentary"},
            "explainer_lint": {"type": "boolean", "default": True, "description": "script: apply the banned-phrase and filler list (turn off for story and comedy)"},
            "words_path": {"type": "string", "description": "render: JSON list of {word, start, end} from the transcriber"},
            "planned_stills": {"type": "array", "items": {"type": "array"}, "description": "render: [[start, end]] windows where a pause in the voice is intended. It never excuses a frozen picture."},
            "output_dir": {"type": "string"},
        },
    }
    output_schema = {"type": "object", "properties": {"verdict": {"type": "string"}, "report_path": {"type": "string"}, "findings": {"type": "array"}, "detail": {"type": "object"}}}
    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=512, vram_mb=0, disk_mb=10)
    idempotency_key_fields = ["mode", "input_path", "format"]
    side_effects = ["writes retention_report.json to output_dir"]
    user_visible_verification = ["watch each timestamp named in the findings at full speed with sound"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        src = Path(inputs["input_path"])
        if not src.exists():
            return ToolResult(success=False, error=f"Input not found: {src}")
        fmt = inputs.get("format", "short")
        try:
            if inputs["mode"] == "script":
                findings, detail = self.check_script(json.loads(src.read_text()), fmt, inputs.get("explainer_lint", True))
            else:
                words = json.loads(Path(inputs["words_path"]).read_text()) if inputs.get("words_path") else None
                findings, detail = self.check_render(src, fmt, words, inputs.get("planned_stills") or [])
        except Exception as e:  # noqa: BLE001
            return ToolResult(success=False, error=f"{type(e).__name__}: {e}")
        verdict = "REJECT" if any(f["severity"] == "critical" for f in findings) else ("REVIEW" if findings else "PASS")
        out = Path(inputs.get("output_dir") or src.parent)
        out.mkdir(parents=True, exist_ok=True)
        report = out / f"{src.stem}.retention_report.json"
        report.write_text(json.dumps({"input": str(src), "mode": inputs["mode"], "format": fmt, "verdict": verdict, "findings": findings, "detail": detail}, indent=1))
        return ToolResult(success=True, data={"verdict": verdict, "report_path": str(report), "findings": findings, "detail": detail})

    # ----------------------------------------------------------------- script
    @staticmethod
    def sentences(text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if re.search(r"\w", s)]

    def check_script(self, script: dict, fmt: str, explainer_lint: bool = True) -> tuple[list[dict], dict]:
        lo, hi, _ = LIMITS[fmt]
        findings: list[dict] = []
        sents = [(sec.get("id", "?"), s) for sec in script.get("sections", []) for s in self.sentences(sec.get("text", ""))]
        counts = [len(re.findall(r"[\w'’-]+", s)) for _, s in sents]
        over = 0
        for (sid, s), n in zip(sents, counts):
            if n > HARD_MAX_WORDS:
                findings.append(_f("major", "line_too_long", f"{sid}: {n} words (max {HARD_MAX_WORDS}): {s[:70]}"))
                over += 1
            elif n > hi:
                findings.append(_f("minor", "line_long", f"{sid}: {n} words (target {lo}-{hi}): {s[:70]}"))
                over += 1
            if re.search(r"\d", s):
                findings.append(_f("minor", "digits_in_speech", f"{sid}: write numbers as words: {s[:70]}"))
            if explainer_lint:
                low = s.lower()
                for b in BANNED:
                    if b in low:
                        findings.append(_f("major", "banned_phrase", f"{sid}: '{b}'"))
                fill = sorted(FILLER & set(re.findall(r"[a-z]+", low)))
                if fill:
                    findings.append(_f("minor", "filler", f"{sid}: {', '.join(fill)}"))
        if sents and over / len(sents) > 0.2:
            findings.append(_f("critical", "line_lint", f"{over} of {len(sents)} sentences are over length"))

        first = script.get("sections", [{}])[0] if script.get("sections") else {}
        if first.get("start_seconds", 0) > 0.5:
            findings.append(_f("critical", "voice_start", f"first line starts at {first['start_seconds']} s (max 0.5)"))

        meta = script.get("metadata") or {}
        if not meta.get("promise"):
            findings.append(_f("critical", "promise", "metadata.promise is missing"))
        rmap = meta.get("retention_map") or {}
        missing = [b for b in MAP_BEATS[fmt] if b not in rmap]
        if missing:
            findings.append(_f("critical", "retention_map", f"metadata.retention_map is missing: {', '.join(missing)}"))

        total = sum(counts); dur = script.get("total_duration_seconds") or 0
        wpm = round(total / dur * 60) if dur else None
        if wpm and wpm > 210:
            findings.append(_f("major", "word_budget", f"{total} words in {dur} s = {wpm} wpm (over 210)"))
        return findings, {"sentences": len(sents), "words": total, "wpm": wpm, "longest_sentence_words": max(counts, default=0)}

    # ----------------------------------------------------------------- render
    @staticmethod
    def _ff(args: list[str]) -> str:
        return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args, "-f", "null", "-"], capture_output=True, text=True).stderr

    @staticmethod
    def parse_freezes(log: str, duration: float) -> list[tuple[float, float]]:
        starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
        ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
        return [(s, ends[i] if i < len(ends) else duration) for i, s in enumerate(starts)]

    @staticmethod
    def shot_stats(cuts: list[float], duration: float) -> dict:
        edges = [0.0, *sorted(c for c in cuts if 0 < c < duration), duration]
        shots = [round(b - a, 2) for a, b in zip(edges, edges[1:]) if b - a > 0.1]
        ratio = round(max(shots) / min(shots), 1) if shots else 0
        return {"shots": len(shots), "shortest": min(shots, default=0), "longest": max(shots, default=0), "length_ratio": ratio}

    @staticmethod
    def _inside(t0: float, t1: float, windows: list) -> bool:
        return any(w[0] - 0.2 <= t0 and t1 <= w[1] + 0.2 for w in windows)

    @staticmethod
    def parse_scores(log: str) -> list[tuple[float, float]]:
        """(time, scene score 0-1) per frame from ffmpeg metadata=print output."""
        times = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
        scores = [float(x) for x in re.findall(r"lavfi\.scene_score=([\d.]+)", log)]
        return list(zip(times, scores))

    @staticmethod
    def rhythm(scores: list[tuple[float, float]]) -> dict:
        """Cuts, how many of them replace the whole frame, and how much of the video is dead still.

        A cut is a frame-to-frame change over 0.3; over 0.6 almost nothing on screen survived it (a slide change
        rather than a carry). Both thresholds are working values, to be tuned against videos we accept and reject.
        """
        cuts: list[tuple[float, float]] = []
        for t, sc in scores:
            if sc > 0.3 and (not cuts or t - cuts[-1][0] > 0.1):
                cuts.append((t, sc))
        hard = [t for t, sc in cuts if sc > 0.6]
        still = sum(1 for _, sc in scores[1:] if sc < 0.0005)
        return {"cuts": [t for t, _ in cuts], "hard_replaces": len(hard),
                "hard_replace_ratio": round(len(hard) / len(cuts), 2) if cuts else 0.0,
                "still_ratio": round(still / max(1, len(scores) - 1), 2)}

    def check_words(self, words: list[dict], planned: list) -> tuple[list[dict], dict]:
        findings: list[dict] = []
        if not words:
            return findings, {}
        first = float(words[0]["start"])
        if first > 0.5:
            findings.append(_f("critical", "voice_start", f"first word at {first:.2f} s (max 0.5)", first))
        gaps = [(float(a["end"]), float(b["start"])) for a, b in zip(words, words[1:])]
        dead = [(a, b) for a, b in gaps if b - a > 0.6 and not self._inside(a, b, planned)]
        for a, b in dead:
            findings.append(_f("major", "dead_air", f"{b - a:.2f} s without speech", a))
        return findings, {"first_word": round(first, 2), "dead_air_gaps": len(dead), "longest_gap": round(max((b - a for a, b in gaps), default=0), 2)}

    def check_render(self, src: Path, fmt: str, words: list[dict] | None, planned: list) -> tuple[list[dict], dict]:
        limit = LIMITS[fmt][2]
        duration = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip())
        findings: list[dict] = []

        log = self._ff(["-i", str(src), "-an", "-vf", "freezedetect=n=-55dB:d=0.3,blackdetect=d=0.1:pix_th=0.08"])
        freezes = self.parse_freezes(log, duration)
        if any(s < 0.05 for s, _ in freezes):
            findings.append(_f("critical", "static_open", "nothing moves in the first 0.3 s", 0))
        if re.search(r"black_start:0(\.0+)?\s", log):
            findings.append(_f("critical", "empty_open", "the video opens on a black frame", 0))
        # A held frame inside moving footage reads as the edit stalling, however deliberate it was. It is reported
        # even inside a planned still: `planned_stills` excuses silence in the voice, never a frozen picture.
        for s, e in freezes:
            if s >= 0.05 and FREEZE_MIN <= e - s <= limit:
                findings.append(_f("major", "frozen_frame", f"the picture freezes for {e - s:.2f} s; keep the footage moving through a quiet beat", s))
        long_still = [(s, e) for s, e in freezes if e - s > limit]
        for s, e in long_still:
            findings.append(_f("critical" if fmt == "short" else "major", "still_stretch", f"{e - s:.1f} s with no visual change (max {limit})", s))

        raw = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "error", "-i", str(src), "-an", "-vf", "select='gte(scene,0)',metadata=print:file=-", "-f", "null", "-"], capture_output=True, text=True).stdout
        rhythm = self.rhythm(self.parse_scores(raw))
        cuts = rhythm.pop("cuts")
        stats = {**self.shot_stats(cuts, duration), **rhythm}
        if len(cuts) >= 4 and stats["hard_replace_ratio"] > 0.5:
            findings.append(_f("minor", "no_carry", f"{stats['hard_replaces']} of {len(cuts)} scene changes replace the whole frame; name what carries from one beat into the next"))
        if stats["shots"] >= 4 and stats["length_ratio"] < 4:
            findings.append(_f("minor", "even_rhythm", f"shot lengths vary only {stats['length_ratio']}x (aim for 4x): shortest {stats['shortest']} s, longest {stats['longest']} s"))
        if fmt == "short" and stats["longest"] > 6:
            findings.append(_f("major", "long_shot", f"one shot runs {stats['longest']} s without a cut"))

        wf, wd = self.check_words(words or [], planned)
        findings += wf
        detail = {"duration": round(duration, 2), "longest_still": round(max((e - s for s, e in freezes), default=0), 2), "still_stretches_over_limit": len(long_still), **stats, **wd}
        if not words:
            detail["note"] = "no word timings given: voice start and dead air were not checked"
        return findings, detail

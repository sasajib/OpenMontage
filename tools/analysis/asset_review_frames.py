"""Build the full-resolution review set for the asset-stage Generated-Visual QA gate.

usage: python tools/analysis/asset_review_frames.py <project_dir> [asset_manifest.json]

For every image/video asset in the manifest (default <project_dir>/artifacts/asset_manifest.json)
it lists the still itself, or extracts first / middle / last frames of a clip, into
<project_dir>/renders/.asset_review/ and prints a JSON list of {id, path, frames}.
The agent MUST open every listed frame at full size before any downstream video job
(image-to-video, lip-sync) and before the assets checkpoint. See
skills/pipelines/animation/asset-director.md -> "Generated-Visual QA Gate".
"""
import json
import subprocess
import sys
from pathlib import Path

VIDEO = {".mp4", ".mov", ".webm", ".mkv"}
IMAGE = {".png", ".jpg", ".jpeg", ".webp"}


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def main() -> None:
    project = Path(sys.argv[1])
    manifest = Path(sys.argv[2]) if len(sys.argv) > 2 else project / "artifacts" / "asset_manifest.json"
    out_dir = project / "renders" / ".asset_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for a in json.loads(manifest.read_text()).get("assets", []):
        p = Path(a["path"])
        if not p.is_absolute():
            p = (project / p) if (project / p).exists() else Path.cwd() / p
        ext = p.suffix.lower()
        if ext in IMAGE and p.exists():
            rows.append({"id": a["id"], "path": str(p), "frames": [str(p)]})
        elif ext in VIDEO and p.exists():
            d = duration(p)
            frames = []
            for tag, ts in (("first", 0.0), ("mid", d / 2), ("last", max(d - 0.1, 0))):
                f = out_dir / f"{a['id']}_{tag}.png"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.2f}", "-i", str(p), "-frames:v", "1", str(f)],
                               capture_output=True)
                if f.exists():
                    frames.append(str(f))
            rows.append({"id": a["id"], "path": str(p), "frames": frames})
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()

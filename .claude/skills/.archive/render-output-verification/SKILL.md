---
name: render-output-verification
description: Use when checking a finished render video before export.
category: video-production
---

# Render output verification

Verify the rendered file itself before packaging. The automated final review is one input, not the verdict.

- Probe duration, resolution, codec, size, and frame rate (`ffprobe -show_entries stream=r_frame_rate`). They must match the composition and the approved fps. The compose step can silently output 30 fps when the rate is not passed explicitly. A 30 fps file for a 24 fps approval is re-rendered before export, not shipped.
- Transcribe the narration and compare it with the approved script. A ratio near 0.98 means the narration landed. A much lower ratio means missing, reordered, or wrong lines.
- Extract frames at the opening, middle, and ending, then look at them.
- A "subtitles expected but not found" issue is a known false negative when captions are rendered inside the composition. Record it in the verification notes. Do not re-render for it.

Run [scripts/verify_render.py](scripts/verify_render.py) with the video path, the script JSON (expects a `sections` list with `text`), and an output folder.

---
name: animate-piece-review-loop
description: Use when reviewing an animate piece with review.mjs gates.
category: video-production
---

# Animate piece: build, export, review, and fix until every gate passes

Run the gates in order after every change: build, textcheck, close-up stills, export, review. Do not report a piece as done while any gate is WARN or FAIL.

Resolve the plugin tools with `SKILL=$(ls -d ~/.claude/plugins/cache/animate/animate/*/skills/animate | tail -1)`, then run `node $SKILL/tools/<tool>.mjs <piece>`.

1. `build.mjs` → `textcheck.mjs` → `still.mjs <piece> <t>` or `tile.mjs` for close-up checks.
2. `export.mjs <piece> --share`, then `review.mjs <piece> > <piece>/review.txt 2>&1`.
3. Grep the verdict lines: cuts on grid, MORPHS, narration, text, story arc, SOUND, dead beats.
4. Read `review/phone.jpg` (one frame a second at 360 px). Every caption must be readable at that size.

Fixing WARNs:
- **Dead beats** (a stretch over 3 s with nothing new on screen): add a physical move, such as a gesture, a hop, an ear flick, or a slow camera push. Hairline-only changes did not clear the warning in this piece. Rebuild and re-review.
- **Story arc**: keep the loudest act at 0.5 cuts/s or below, and make the goodbye decay at least 6 dB below the gift act's median.
- **Sound**: the review gives loudness and silence numbers only. Report them as numbers. Do not say the sound was checked by ear.

When done: delete the piece's `frames/` dir and scratch stills (see `animate-export-troubleshooting`). Report what passed, the weakest shot, and what was not verified.
---
name: animate-export-troubleshooting
description: Use when animate export fails with ENOSPC or disk-full.
category: video-production
---

# Animate export: check disk space before rendering, and find ENOSPC first

Run `df -h /` before `node tools/export.mjs <piece> --share`. One ~47-second animate piece writes about 800 PNG frames (about 1.3 GB). Start the export only with clear headroom above that.

- If the export log shows `ENOSPC` or `errno: -28`, that is the root cause. A later "no render at .../renders/final.mp4 - run export.mjs first" is only a symptom.
- Do not filter progress lines in a way that hides errors. Grep the full log for `ENOSPC|errno|Error` before reading the tail.
- Free space by deleting only the failed run's partial `frames/` dir for that piece. Never delete finished renders, checkpoints, or other project artifacts without asking the user.
- `npm cache clean` and `pip cache purge` are a last resort. Tell the user before running them.
- After freeing space, rerun the export, wait for its exit code, and only then run the review.
- Once `review.mjs` passes and `share.mp4` exists, the piece's `frames/` dir (about 96 MB per piece) and the scratch `review-still-*.png` files are intermediates. Delete them to keep `/` from filling again. Keep `renders/share.mp4`, `storyboard.png`, `review.txt`, and `review/phone.jpg`.
- Once export and review have both finished and the renders are verified, delete the piece's `frames/` dir right away. Keep the render outputs. A 224 GB root disk at 95% used had only 12 GB free after a run, so frames left behind eat the headroom for the next piece.
- Chain the whole job in one background run: `export.mjs --share` → `review.mjs` → `rm -rf <piece>/frames`. Once `review.txt` shows the gates, the frame dump is disposable intermediate output and can go. The finished `renders/` stay. On a disk already near 95%, this is what restores headroom (one run went from 12 GB free after cleanup on a 224 GB disk).

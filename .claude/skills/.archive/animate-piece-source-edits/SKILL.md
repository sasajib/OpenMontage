---
name: animate-piece-source-edits
description: Use when animate scene edits break or a scene draws blank.
category: video-production
---

# Animate piece source edits: comments and clips break silently

Edit an animate piece's `src/*.js` parts with an exact-match edit tool, not a one-line `sed` that touches code. Build concatenates the parts into one `index.html`, so a `//` comment placed after code on a line comments out everything after it on that line.

- Use `/* ... */` for inline notes inside a line of drawing code. Never put `//` after code on the same line.
- Any `ctx.clip()` must sit between a `ctx.save()` and its `ctx.restore()`. If a save/restore pair loses its restore, the clip leaks into later shots and they go blank or cut off.
- After every edit: rebuild, then `grep` the built `index.html` for the exact line you changed, and confirm the line still ends in the code you expect.
- If a scene draws blank, probe the page in-browser: log `ctx.getTransform()` and the clip state around the suspect draw before changing art.
- Passing gates (textcheck, storyboard, tile) do not prove a scene draws correctly. Look at the tile frames of the affected shot.
- Run the gate chain in order (build, storyboard, textcheck, tile, export, review). Start it in the background and read its output file only when it completes; do not poll.

Worked example and the exact failure: see [references/commented-clip-incident.md](references/commented-clip-incident.md).

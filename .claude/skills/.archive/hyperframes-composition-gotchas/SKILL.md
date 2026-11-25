---
name: hyperframes-composition-gotchas
description: Use when HyperFrames fonts render wrong or cards overlap.
category: video-production
---

# HyperFrames composition gotchas

Every custom `font-family` in a HyperFrames composition must end in a generic fallback (`sans-serif`, `serif`, or `monospace`). A bare family such as `font-family:"Anton";` can render in the wrong face when the font is not available at render time.

## Rules

1. When a builder writes CSS, emit `font-family:"Anton",sans-serif;` for every custom family. Grep the generated `index.html` for family values without a generic fallback before rendering.
2. Verify typography from rendered frames, not from source. If a fallback variant renders correctly and the primary does not, keep the fallback in the builder.
3. Before the final render, check that title and caption cards do not overlap in time or space. Fix them in the builder, rebuild, and re-check the frames.
4. Place overlay readouts (stat or altitude boxes) by the card start times the builder already computes. Show a readout only after the opening card has finished, and hide it before a death-zone or blackout card, then re-show it after. Verify with frames at each card boundary, not from source.

## Evidence

In the great-emu-war build, a sans-serif fallback variant rendered Anton correctly. The builder was patched to add `,sans-serif` (and `,monospace` for Typewriter) to each custom family. The rebuild then reported `index.html 38515 chars; 113 tweens; 46 captions`.

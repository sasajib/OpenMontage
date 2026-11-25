# Incident: a `//` comment disabled a donkey draw and leaked a clip

A `sed` edit turned a line in `src/scenes-c.js` into this (after build the code followed the comment on the same line):

```
ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, 1000); ctx.clip();   // hidden behind the half door until it pops up ctx.translate(0, (1 - up) * 420 + kick * -12); donkeyS(360, 860, 1.5, { key: 'dkB'
```

Effects: `ctx.translate` and `donkeyS(...)` were commented out, and the matching `ctx.restore()` was lost. The clip leaked, the bray shot went blank below the door, and the donkey was missing.

Fix that worked: replace the inline `//` with a block comment so the code stays live:

```
ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, 1000); ctx.clip(); /* hidden behind the half door until it pops up */ ctx.translate(0, (1 - up) * 420 + kick * -12); donkeyS(360, 860, 1.5, { key: 'dkB'
```

Verification that caught it: `grep -c` on the exact changed text, then an in-page save/restore probe. The gate chain (textcheck, storyboard, tile) passed before the bug was seen, so passing gates did not prove the scene drew correctly.

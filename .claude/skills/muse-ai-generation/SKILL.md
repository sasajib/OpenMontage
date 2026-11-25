---
name: muse-ai-generation
description: Use when generating images or video clips with Meta Muse (muse.ai) through BrowserOS for an OpenMontage project — limits, prompt shapes, batch messages, download, and the mistakes it makes.
category: video-production
---

# Muse (Meta) image + video generation via BrowserOS

Muse is a chat assistant at https://muse.ai/ (the user's account, signed in inside BrowserOS). It wraps **Muse Image** and **Muse Video** (Meta). There is no API; everything is a chat message. Verified 2026-11-07 on the Everest v2 film (30 stills, 27 clips).

## Facts (measured)

| | Image | Video |
|---|---|---|
| Output | 2048x1152 webp for "wide landscape 16:9" | 1248x704, 24 fps, 10.0 s, h264 + AAC sound (wind, breath, foley), ~4-8 MB |
| Per message | max 4 images | max 6 clips (~6-8 min for 6) |
| Control | aspect by words only ("wide landscape 16:9"); no seed, no size, no model choice | none: duration fixed at 10 s, aspect follows the first frame, no fps |
| Reference | attach a photo: likeness holds well for a bearded face; "same face as the attached photo" | first frame = any image from the chat ("the second SC20 you made"); a reference sheet can be attached too and helps identity |
| Account | free weekly limit (Power USD 16/mo, Maximum USD 80/mo); 57 generations used about 70 % of a week in practice | |

Muse's own "Checked it: matches the description" note is **not a review**. It cannot watch video and it misreads images. Every output goes through `video-reality-check` and the full-size look.

## Click path

1. `tabs new https://muse.ai/`, wait ~6 s, `snapshot` → textbox "Message" (ref `e48` in a fresh session; re-snapshot if it changes).
2. **Attach a reference** (for face shots): no visible button works from automation; set the hidden input with CDP from `run`:
   `DOM.getDocument` → `DOM.querySelector(root, 'input[type=file]')` → `DOM.setFileInputFiles({nodeId, files:[abs path]})`. A full-res PNG attaches fine; the snapshot then shows `button "ref.png Remove attachment ..."`. The attachment is consumed by the next message only.
3. `act fill` the textbox with the whole batch message, then `act press Enter`.
4. **Poll** with `run`: read `document.querySelector('[role=log]').innerText` after the last occurrence of a unique phrase from your message; done when Muse's reply ("Here are your N images" / "All N clips are done") appears. Images take ~60-90 s per 4; clips ~6-8 min per 6.
5. **Download**: the chat list virtualises media, so `img`/`video` elements only exist for what is scrolled into view. From `run`: scroll the log container (the ancestor with `overflow-y: auto`) to the bottom, step up 450 px at a time collecting `video.currentSrc` / `img.src` (blob URLs) that sit *below* your message's text node, then `fetch(blob)` → `a.download = name` → click. Set `Page.setDownloadBehavior {allow, downloadPath}` first so files land in the project. **Always md5-compare** against earlier downloads: a stale blob is the most common failure (two "new" files that are the same image).
6. The same chat has Slack / Discord / WhatsApp send actions connected. Never phrase anything there that could be read as "send".

## Prompt shapes that work

**Images (batch of 4):**
```
Please generate exactly 4 separate images, all wide landscape 16:9 photoreal cinematic film stills, one per description, in this order, passing each description as written.
IMAGE SC02: <still prompt>  IMAGE SC03: <still prompt> ...
```
With a reference: prefix "The attached photo is me; use it as the identity reference for every image in this request." and start each face prompt with "the man from the attached photo, same face, same full black beard".

**Clips (batch of 6):**
```
Please generate exactly 6 separate 10-second video clips, one per item, in this order. For each clip use the named image as the first frame and pass the clip's camera movement and scene action as written. For EVERY clip, add this to the prompt: Mood and style: ... Sound: ... Model notes: Use the image as the first frame. Preserve the subject, framing, lighting, depth, lens feel and screen direction from that image while applying only the selected camera movement. Keep exactly two arms and two legs, the whole body inside the frame, no extra limbs, no morphing.
CLIP SC02: first frame = the corrected redo of SC02 (second SC02, tiny figure). Camera movement: Camera: <library prompt verbatim>. Scene action: <one simple action>.
```
Name first frames unambiguously ("the second SC21, NOT the first one with the flagpole"). Camera prompts come from `.agents/skills/camera-movement-prompts/SKILL.md`; shot size and angle belong in the still, not the clip.

## What Muse gets wrong (plan for it)

- **Every camera move is exaggerated.** "Slow dolly in" goes wide-to-close in 10 s; "static" drifts; "arc" orbits. Use the first 2-5 s of each clip (`trims.json` in the project) and ask for the gentlest wording. Inserts (feet, hands, objects) must be locked-off or the camera invents impossible geometry.
- **The first second and last 1-2 s of a clip are often junk** (identity settles in, then dissolves). Keep the middle.
- **Expressions re-draw faces.** A smile turned the user into another man twice. Ask for small expressions on identity shots and attach the sheet to the clip request.
- **Invariants revert.** A still with the mask off produced a clip that put it back on. Pin what must not change: "mask stays at his neck, face stays visible".
- **Props appear from nowhere** (a flagpole on a summit, a second climber) and **mechanisms are wrong** (rope beside the carabiner, screw threads out of the ice). Redesign after two takes; show the force, not the hardware.
- **Suit colour can drift mid-clip** (orange to dark red after 2.5 s). The continuity check catches it; trim or redo.
- **Extreme wides come back as mediums** unless the size is numeric: "about one tenth of the frame height".

## Logging in OpenMontage

Each output is a `provided` asset (`source_tool: "provided (Muse Image/Video via BrowserOS)"`, `provider: "muse_ai"`, `cost_usd: 0`). Keep every take (`sc19_t1`, `sc19_t3`) and record the chosen take and the reason the others failed in `generation_summary`. Log the per-message batches in `artifacts/still_batches.json` / `clip_batches.json` so a rerun is reproducible. See `projects/everest-summit-v2/scripts/` for the working runner shape.

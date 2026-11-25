---
name: generated-visual-qa
description: Use when a still feeds a video job: check it at full size.
category: video-production
---

# Generated-visual QA before any video spend

No generated still or clip may feed a paid video job (image-to-video, lip-sync, upscale) or be registered in the asset manifest until it has been looked at, at full resolution, and passed. A contact sheet or downscaled preview does not count.

## Procedure

1. Build the review set from the manifest: every still, plus the first, middle and last frame of every clip. Open each frame at full size.
2. Reject, regardless of score, on any of:
   - an object drawn across the face (planks, poles, hands over eyes);
   - eyes mismatched, doubled, or merged with a background edge;
   - a character cut off by the frame edge or torso in a dialogue shot, or a peeking pose that reads as hanging off something;
   - extra or missing limbs, melted hands, text or watermarks;
   - for lip-sync source frames: not frontal, not centred, mouth not fully visible.
3. Record a `quality_score` (0-1) per generated asset. Under 0.7 means regenerate, not patch in the edit.
4. For character stills, generate 2-3 candidates and keep the best.
5. The checkpoint summary states how many assets were viewed and how many were regenerated, and why.

## Final review must cover every cut

Four fixed sample points miss short shots. A 0.8 s eye shot with a broken face passed a four-frame review and shipped. Sample a frame shortly after every hard cut (ffprobe scene filter, threshold 0.3) in addition to the fixed points, and confirm the sampled count covers all cuts before a render passes.

## Why

Downstream checks only test that frames exist, are not black, and have readable text. Nothing else looks at faces. A bad still caught here costs a regeneration; caught later it costs a video job and a re-render.

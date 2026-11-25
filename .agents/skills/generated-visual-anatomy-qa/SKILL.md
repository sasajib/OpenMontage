---
name: generated-visual-anatomy-qa
description: Use when reviewing AI stills or clips before video: anatomy, blinks, identity, and real-world logic (gear, environment, extra people, framing).
category: video-production
---

# Generated visual QA: anatomy + real-world logic

Reject any generated still or clip that fails a check below. Regenerate it with a corrected prompt; never patch it in the edit. Review every still at full size **before** it becomes a first frame, because the video model inherits every mistake in it.

**Cost-ladder order (user rule, 2026-11-07):** still -> check -> clip -> check -> edit -> render -> final check. Run the reality check at the cheapest point that can catch the defect: a bad still costs one image, a bad clip costs one generation, a bad render costs the whole compose. Never request a clip from an unchecked still, and never start a render with an unchecked clip in the timeline. The post-render review is a last net, not the gate. When the user asks to check clips and stills before rendering, do that first; do not kick off the render and check afterwards.

## A. Anatomy and identity

Automate the counting with the `reality_check` tool first (`.claude/skills/video-reality-check/SKILL.md`), then do the full-size look; the tool cannot see gear geometry or props.

- Open every still at full size. Count arms, hands and legs. Pass only with exactly two arms, two hands and two legs in view. Hidden limbs are fine; fused or extra ones are a fail.
- For clips, check frames at 2 per second (`ffmpeg -vf fps=2`), not just first/middle/last; `tools/analysis/asset_review_frames.py <project_dir>` builds the minimum set.
- When eyes are visible, require a blink or natural eye movement in the clip. A frozen, unblinking face is a fail.
- Compare every face-visible shot to the reference sheet. Visible identity drift is a fail.
- Never use one contact sheet in place of full-size review. The full procedure and `quality_score` threshold are in `skills/pipelines/animation/asset-director.md` under "Generated-Visual QA Gate".

## B. Real-world logic (user rule, 2026-11-07)

Image models compose things that look right at a glance and are physically wrong. Check each still against how the real thing works:

| Check | Fail example | Fix in the prompt |
|---|---|---|
| **Gear geometry** — does every piece of equipment do its real job? | Rope looped around a carabiner instead of through it; ice screw standing loose on the ice; axe held by the pick; crampons on the wrong way | Describe the mechanism explicitly: "rope passing through the carabiner and running up out of frame under tension", "screw driven fully in, only the hanger showing" |
| **Environment consistency** — do surfaces and clothing show the conditions? | Clean dry suit at -30 C on a snow ridge; no breath vapour; no frost on metal | Put the condition on the objects: "rime ice and frost crusted on the suit, hood, mask and goggle rims" |
| **Cast count** — only the people the plan names | A second climber far below in a "lone mountaineer" shot | "one single person, no other people anywhere in the frame" |
| **Scale and framing** — matches the planned shot size and angle | "Extreme wide, tiny figure" comes back as a medium shot; "bird's-eye" comes back as a 45° high angle | Give a size: "the figure about one tenth of the frame height"; name the geometry: "looking straight down, map-like" |
| **Frame edges** — subject fully inside the frame when the body matters | Legs cut by the bottom edge, which the video model then "completes" | "whole body fully inside the frame" |
| **Physics of the moment** — weight, tension, direction | Slack rope on a hanging climber; snow falling upward; flag blowing against the wind direction of the spindrift | State the force: "rope taut under his weight" |
| **Prop provenance** — where did every object come from? | A flagpole on a summit (nobody carries one up Everest); a lantern nobody packed; a chair in a desert | Only props the character would carry or find there; name the real substitute: "flag tied to the shaft of his raised ice axe", "flag stretched between both hands" |
| **Continuity** — same wardrobe, gear and light as the neighbouring shots | Hood up in one shot, down in the next; sunrise behind, then night | Repeat the same gear sentence verbatim in every prompt |

A still that fails any row is regenerated even if it is beautiful. Beautiful-but-wrong is what makes a video read as fake.

### Hard rule: mechanism shots (SC09 lesson, 2026-11-07)

Any shot whose point is a **mechanism** — a rope through a carabiner, a knot, a buckle, a screw in a wall, a lock, a chain link, a cable on a pulley — is a known image-model failure. Three takes of "rope through a carabiner on an ice screw" all failed in different ways (rope looped around the gate; screw threads standing out of the ice; rope passing beside the carabiner). Treat these shots as follows:

1. **Trace the path.** Follow the rope / cable / strap with your eye from where it enters the frame to where it leaves. It must pass *through* the hardware, not behind, beside or around it. Every piece of hardware must be seated the way the real thing is (screw fully in, hanger flush, carabiner gate closed). The provider's own "checked, matches" note counts for nothing; only your trace counts.
2. **Two takes maximum.** If the second take still fails, stop regenerating. The model does not understand the mechanism and more takes waste quota.
3. **Redesign the shot to remove the mechanism.** Show the *force* instead of the hardware: a rope snapping bar-tight against the sky with snow bursting off it says "the anchor held" with nothing to get wrong. Other swaps: a hand on a rope instead of the knot; the wheel turning instead of the chain; a door swinging instead of the lock.
4. **Record it.** Note the redesign in the scene plan and the gen log so the edit does not expect the original shot.

## B2. Clip-specific hard rules (Muse Video lessons, 2026-11-07)

- **Pin the invariants in the clip prompt.** State what must NOT change: "mask stays at his neck, face stays visible", "same person as the first frame, same face shape, skin tone, beard". A video model given a still with the mask off put it back on; a smile turned the user's face into a different man. Attach the character sheet to face clips when the provider accepts a reference.
- **Expressions drift identity.** Ask for small expressions (eyes soften, slight breath) on identity shots; a wide smile or laugh re-draws the face. Check a full-size frame from the END of every face clip against the reference, not just the start.
- **"Static" and "slow" are not honoured.** Muse turns every move into a big push, pull-out or orbit over 10 s. Plan on using the first 2-5 s of each clip and say so in the trims; a close-up tracking move around legs or hands produces impossible geometry (boots stepping into the void): keep inserts locked-off.
- **A pole, a second figure, a changed suit colour in the clip usually comes from the still.** Trace the still again before blaming the video model.

## C. Design to avoid failures in the first place

- Prefer framings that hide hands (mittens, gloves, gear) and eyes (goggles, masks) when the story allows it; show a bare face only in a few checked close-ups.
- Object inserts with no person (a rope, a crack, a tool) carry tension with zero anatomy risk, but they are where gear-geometry errors hide, so check them hardest.
- Give the video model one simple action per clip; complex actions make it drop limbs.

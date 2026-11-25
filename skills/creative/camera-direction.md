# Camera Direction — Shot Size, Angle and Movement

## When to Use

Whenever a scene will be made by an image or video generation model and you must decide **how the camera sees it**. Three separate choices per shot:

1. **Shot size** — how much of the subject is visible.
2. **Camera angle** — where the camera sits.
3. **Camera movement** — how the camera travels during the clip.

Use it at `scene_plan` (choose all three per scene) and at `assets` (write the prompts).

For code-rendered motion (Remotion, HyperFrames, animate, opuscar) use `skills/creative/virtual-camera.md` — those build the camera in code. The shot-size and angle tables here still help when framing those scenes.

## Prerequisites

| Resource | Path | Purpose |
|---|---|---|
| Movement prompts (Layer 3) | `.agents/skills/camera-movement-prompts/SKILL.md` | 46 verbatim movement prompts + video prompt template |
| Shots and angles (Layer 3) | `.agents/skills/camera-movement-prompts/references/shots-and-angles.md` | 10 shot sizes, 17 angles, example prompts, still prompt formula |
| Universal vocabulary | `skills/creative/video-gen-prompting.md` | 5-aspect spec, camera height, word budgets |
| Model guide | `skills/creative/prompting/<model>-prompting.md` | Model-specific structure and limits |
| Scene plan schema | `schemas/artifacts/scene_plan.schema.json` → `shot_language` | Where the choices are recorded |

## Where each choice goes

| Choice | Still → video (image-to-video) | Text-to-video |
|---|---|---|
| Shot size + angle | **Still prompt.** They define the first frame. | Opening of the prompt |
| Movement | **Video prompt.** Nothing else about the camera. | `Camera:` line |

Do not restate shot size or angle in the image-to-video prompt — the first frame already fixes them, and a mismatch makes the model fight the image.

## Process

### Step 1: Pick the shot size

| The shot must… | Shot size |
|---|---|
| Open a scene; show where we are; make the subject small in a big world | Extreme wide / establishing |
| Show action, body language, the subject in its space | Wide |
| Carry dialogue or everyday action (neutral default) | Medium |
| Present, explain, or hold a personal but calm moment | Medium close-up |
| Show emotion, a reaction, a reveal | Close-up |
| Force attention on one detail; build suspense | Extreme close-up |
| Show a relationship or conflict in one frame | Two-shot |
| Put the viewer inside a conversation | Over-the-shoulder |
| Make the viewer the character | POV |
| Make the viewer notice an object | Insert |

**Sequence rule:** start wide to set the stage, go medium for interaction, push to close for emotion. Never run three shots of the same size in a row.

### Step 2: Pick the angle

Default is **eye-level**. Leave it only for a reason:

| The viewer should feel the subject is… | Angle |
|---|---|
| An equal; natural and relatable | Eye-level (or shoulder-level for a softer variant) |
| Small, weak, vulnerable, watched | High angle |
| Powerful, heroic, threatening | Low angle |
| Overwhelming in height or scale | Worm's-eye |
| Part of a pattern, map or crowd | Bird's-eye |
| Fragile, fated, seen from far away | Overhead / God's eye |
| Unstable, tense, dreamlike | Dutch angle (extreme tilt for breakdown or horror) |
| In a standoff, about to act | Over-the-hip / over-the-weapon |
| On a journey we follow | Over-the-back |
| Being spied on | Shoulder peek / behind-the-object |
| Moving, grounded, arriving | Knee-level |

Common pairs: close-up + high angle = fear; close-up + low angle = power; medium + Dutch = unease; wide + bird's-eye = scale; extreme wide + worm's-eye = overwhelming. Over-the-shoulder, over-the-hip and over-the-weapon need medium or close framing; overhead needs wide framing.

### Step 3: Pick the movement

One move per clip. IDs refer to the movement library.

| The shot must… | Use | ID |
|---|---|---|
| Let the action or dialogue speak; calm, observational | Static shot | 01 |
| Show the width of a place; connect two things side by side | Pan | 02 / 02B |
| Snap energy between two subjects; comic or action beat | Whip pan | 03 / 03B |
| Reveal height or scale; reveal what is at someone's feet | Tilt | 04 / 04B |
| Draw attention gently to a detail or thought | Slow zoom in | 05 |
| Place the subject in a bigger context, slowly | Slow zoom out | 05B |
| Punch a reaction, joke or shock | Fast / crash zoom | 06 / 07A / 07B |
| Build intimacy or tension; "this matters" | Dolly in | 08 |
| Leave the subject alone, end a scene, show isolation | Dolly out | 09 |
| Scan a row of things; travel along a wall or crowd | Truck | 10 / 10B |
| Rise over an obstacle or sink to a subject's level, lens kept level | Pedestal | 11A / 11B |
| Add quiet depth to a product, portrait or still life | Slider | 12 / 12B |
| Enter a space; pass a doorway, window or foreground object | Push past | 13 |
| Add life to a hero shot without a full circle | Arc | 14 / 14B |
| Showcase a subject from all sides; a "hero moment" | Orbit | 15 / 15B |
| Travel with a moving subject | Tracking (general / side / low) | 16 / 19 / 20 |
| See the journey through the subject's eyes, subject in frame | Follow from behind | 17 |
| Walking character talks or reacts, face visible | Reverse tracking | 18 |
| Car, bike, train in motion | Vehicle tracking | 21 |
| Urgency, pursuit, danger | Chase | 22 |
| Raw, documentary, nervous or real feel | Handheld | 23 |
| Disorientation, panic, drunk or dream state | Snorricam | 24 |
| Open or close a sequence with scale | Crane up / down | 25 / 25B |
| Arrive at, or leave, a location from the air | Drone push in / pull back | 26 / 26B |
| Epic landscape establishing shot | Helicopter | 27 |
| Put the viewer inside the character | First-person view | S1 |
| Make a real place look like a toy model | Tilt-shift | S2 |
| Transition into another world or scene | Infinite zoom / pass-through | S3 / S6 |
| "From here to the whole planet" scale reveal | Earth zoom out | S4 |
| Show time passing in one place | Time-lapse | S5 |

Default when unsure: **slow dolly in (08)** for people, **static (01)** for dialogue, **slider (12)** for objects.

### Step 4: Check the three choices fit each other

The model can only move through what the first frame makes believable.

| Movement | Needs in the still |
|---|---|
| Orbit, arc | Subject with clear space around it, medium or wide. Not a subject against a wall. |
| Dolly in, zoom in | Room to get closer — start one size wider than the framing you want to end on. |
| Dolly out, zoom out, crane up, drone pull back, earth zoom out | Accept invented scenery outside the frame. Avoid when surroundings must be accurate. |
| Tracking, follow, chase, vehicle | Subject already in motion (mid-stride, wheels turning). Follow → over-the-back angle; side tracking → profile. |
| Push past, pass-through | A visible foreground object or opening (behind-the-object angle works well). |
| Tilt up / down | A tall subject that continues beyond the frame; low or high angle helps. |
| Any big move | Not an extreme close-up — there is no space to travel. Use slow zoom, slider or static. |
| Any move | Avoid Dutch and extreme-tilt stills unless the tilt is the point; the model tends to level the horizon mid-clip. |

If they do not fit, change the move or regenerate the still. Do not hope the model fixes it.

### Step 5: Vary across the sequence

- Do not repeat the same size, angle or move on consecutive shots unless it is a deliberate motif.
- Keep screen direction: after travelling right, do not travel left without a reason.
- Match energy to the beat: slow moves (05, 08, 12, 25) for calm and emotion; fast moves (03, 07, 22) for peaks only.
- Special angles (Dutch, worm's-eye, God's eye) lose power when repeated. Use each once or twice per video.
- Include static shots. The eye needs rest.

### Step 5b: Plan the scene as coverage, not single shots

Shots in one location must look like one place filmed by a few cameras.

**Camera setups.** List the setups for the scene first (A = wide master, B = close on the hodja, C = reverse on the neighbour), then assign each shot to a setup. Reuse a setup before inventing a new one; add one only when size, angle or focus really differ. After a setup makes a big move, treat it as a new setup.

**Order.**
- The first shot of a location is the widest: it shows where everyone stands.
- Do not jump from a long shot straight to a close-up; pass through a medium, unless the jump is the point.
- No two consecutive shots share location + size + lens. A repeat must be a deliberate motif.
- Alternate moving and static shots.
- Every cut has a reason you can say in one sentence (new information, reaction, reveal, time skip, emphasis).

**Screen direction (the line).** Draw a line between the two main subjects and keep every camera on one side of it. Write it into every still prompt: "hodja on the left of frame facing right; neighbour on the right facing left". A character who faces right in the wide faces right in the close-up.

**Each shot's still prompt states:** where each subject sits in the frame (left / centre / right, near / far), which way each faces, and what is visible — as a frozen snapshot. "He is sitting, leaning slightly forward", never "he is about to stand".

**Derive, don't regenerate.** A new angle in the same location is made by **editing the master still** (Qwen-Image-Edit: "same scene, camera now close on the old man's face, do not change the background"), not by a fresh text-to-image call. Pass the character sheet plus the nearest earlier frame from the same setup as references, and say which image is which ("the man references image 1; the courtyard references image 2"). Use at most one sheet view per character, matched to the facing (front / side / back).

**Lens and depth** (`shot_language.lens_mm`, `depth_of_field`): 24 mm for space and scale, 35–50 mm for natural scenes, 85 mm and up to isolate a face. Keep two or three lenses per video. For real parallax in a moving shot, put a soft out-of-focus object in the foreground of the still and name a large near-background object.

**First and last frame.** For a shot with big change — camera travel, a prop changing hands, a character landing somewhere — make the end frame too, as an **edit of the start frame** changing only the intended action, and give both to the video model (only on models with a first-last-frame mode; check the tool's `supports` — our WAN 2.2 endpoint is image-to-video from one frame as of 2026-11, so there the end frame is a review target, not an input). Small-change shots use the first frame only. Pinning both ends does not control the middle, so still review the clip. For a locked-off shot, passing the same image as first and last frame stops lighting drift. A continuing shot starts from the previous clip's last frame.

**Camera block for the video prompt.** When a move needs more than its library line, add: `from` (start framing), `to` (end framing), `timing` ("hold 0.5 s, push 0.5–3 s, settle before the cut"), `focus` (what stays sharp). If the model inserts a cut, add "one continuous take with no cuts and no change of shot".

**Two takes, pick one.** For hero shots generate two candidates and choose by, in order: character matches the sheet; left/right positions not flipped; matches the description; no borders or black edges.

**Continuity check at the join.** Compare the last frame of each clip with the first frame of the next: feet, hands, props, who holds what, light direction.

### Step 6: Record it in the scene plan

`shot_language` uses fixed values. Map your choice, and put the exact name and library ID in the scene's `framing` text (e.g. "low angle two-shot; move 14B arc left").

| Schema `shot_size` | Use for |
|---|---|
| `extreme_wide`, `establishing` | Extreme wide shot |
| `wide`, `medium_wide` | Wide shot |
| `medium` | Medium shot, most two-shots |
| `medium_close` | Medium close-up |
| `close_up` / `extreme_close_up` | Close-up / extreme close-up |
| `over_shoulder` | Over-the-shoulder |
| `insert` | Insert |

| Schema `camera_movement` | Library IDs |
|---|---|
| `static` | 01, S2, S5 |
| `pan_left` / `pan_right` | 02B / 02 |
| `whip_pan` | 03, 03B |
| `tilt_up` / `tilt_down` | 04 / 04B |
| `zoom_in` / `zoom_out` | 05, 06, 07A, S3 / 05B, 06B, 07B |
| `dolly_in` / `dolly_out` | 08, 13, 26, S1, S6 / 09, 26B, S4 |
| `tracking_left` / `tracking_right` | 10B, 12B / 10, 12, 19 |
| `crane_up` / `crane_down` | 11A, 25 / 11B, 25B |
| `orbital` | 14, 14B, 15, 15B, 27 |
| `steadicam` | 16, 17, 18, 20, 21, 24 |
| `handheld` | 22, 23 |

Angle, two-shot and POV have no schema field — write them in `framing`.

### Step 7: Write the prompts

**Still prompt** (shot size + angle), using the formula in the shots-and-angles reference:

```
[Shot type] of [subject] from [camera angle], [action / expression], in [environment], with [lighting], [color palette], [emotional tone], in [style].
```

**Video prompt** (movement only):

1. Copy the move's prompt **verbatim** from the movement library.
2. Build the full prompt with the library template (camera movement / reference image context / scene action / mood and style / model notes).
3. Keep scene action **simple** — one readable action. A complex action competes with the camera move and the model drops one.
4. Fit the target model's word budget (`skills/creative/prompting/<model>-prompting.md`). On short-budget models, send the camera line plus one sentence of action.

Example — a hodja and his donkey, gentle beat:

```
STILL
Medium shot of an old man in a turban standing beside a grey donkey from eye level, stroking the donkey's neck, in a sunlit stone courtyard, with soft golden-hour light, warm earthy tones, gentle and peaceful, in storybook 3D animation style.

VIDEO
Camera movement:
Camera: slider right. Movement: slide the camera a small distance to the right. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new right-side angle visible.

Reference image context:
An old man in a turban stands beside a grey donkey in a sunlit courtyard, medium shot.

Scene action:
The old man slowly strokes the donkey's neck. The donkey flicks one ear.

Mood and style:
warm, gentle, storybook.

Model notes:
Use the uploaded image as the first frame. Preserve the subject, framing, lighting, depth, lens feel and screen direction from that image while applying only the selected camera movement.
```

### Step 8: Sample, then review

Review the **still at full resolution before any video job** — a wrong size or angle cannot be fixed by the video model. Then, per the Decision Communication Contract, generate **one sample clip** before a batch.

| Check | Question | Pass |
|---|---|---|
| Size | Does the still show the amount of subject the plan asked for? | yes |
| Real-world logic | Does every piece of gear work the way it really does, do surfaces show the conditions, are only the planned people present? (see `.claude/skills/generated-visual-anatomy-qa/SKILL.md` section B) | yes |
| Angle | Is the camera position right (not eye-level when low angle was asked)? | yes |
| Movement | Did the camera do the named move, not a look-alike (zoom for dolly, pan for truck)? | yes |
| Speed | Does the pace match the prompt? | yes |
| Framing | Did the subject stay readable, with no warping or identity drift? | yes |
| End | Does the clip settle on a usable final frame for the cut? | yes |

If a movement check fails: simplify the scene action first, then try the nearest simpler move (orbit → arc → slider; crane → pedestal; chase → tracking). If two tries fail, fall back to static (01) and add the move in the composition runtime instead.

## Common Pitfalls

- **Everything at eye-level medium.** The default for every shot gives a flat video. Vary size first, angle second.
- **Angle or size words in the image-to-video prompt.** They belong in the still. In the video prompt they fight the first frame.
- **Two moves in one prompt** ("dolly in while orbiting"). Models do one, badly. One move per clip; cut between clips.
- **Rewording the movement prompt.** The fixed Movement / Speed / Framing / End wording is what makes it reliable. Change nouns only.
- **Zoom when you mean dolly** (and pan/truck, tilt/pedestal). They look different; use the exact name.
- **Bird's-eye vs aerial.** Bird's-eye is strictly straight down. A drone looking down at 45° is a high angle from aerial height.
- **Over-the-shoulder in a wide shot.** The shoulder disappears. Use medium or close.
- **Assuming every model obeys equally.** The movement prompts were written for Kling, Seedance, Higgsfield and Runway; the shot and angle examples for image models in general. Untested on our own Qwen / Z-Image / WAN 2.2 / LTX endpoints — sample first, and note what worked in the model's prompting guide.
- **Moving camera on a lip-sync shot.** Keep talking shots static or slow dolly; big moves break mouth sync.

---
name: camera-movement-prompts
description: |
  Library of 46 copy-ready camera movement prompts for AI video generation (pan, tilt, zoom, dolly, truck, pedestal, slider, arc, orbit, tracking, handheld, crane, drone, FPV, time-lapse and more), plus a reference of 10 shot sizes and 17 camera angles with example prompts for image generation. Use when: (0) framing a still or first frame (shot size, camera angle), (1) writing the camera part of any text-to-video or image-to-video prompt, (2) a scene plan names a camera move and you need exact wording, (3) a generated clip ignored or confused the camera move and you need a cleaner instruction. Works with Kling, Seedance, Higgsfield, Runway, VEO, WAN, LTX and similar models.
---

# Camera Movement Prompts

Source: [aicameramovements.com](https://aicameramovements.com/) (free reference library by Dan Kieft, copied 2026-11-07). Prompts below are verbatim.

For **which shot size, angle and move to pick**, read the Layer 2 skill first: `skills/creative/camera-direction.md`. This file is only the movement wording.

Shot sizes (wide, medium, close-up…) and camera angles (low, high, Dutch, bird's-eye…) with example prompts and the still-image prompt formula: `references/shots-and-angles.md`. Those describe the frame and go in the still / first-frame prompt; the prompts below go in the video prompt.

## How every prompt is built

Each prompt has the same five parts. Keep all five when you adapt one:

```
<move name>. Movement: <what the camera physically does>. Speed: <pace>. Framing: <what stays readable>. End: <how the clip finishes>.
```

The site's "Copy prompt" button puts `Camera: ` in front (e.g. `Camera: dolly in. Movement: ...`). Use that prefix when the camera line sits inside a longer prompt.

The camera instruction contains **no scene content**. That is the point: it stays reusable when the first frame or subject changes. Put the scene in separate blocks.

## Full prompt template

Use this layout (it is the site's prompt builder output). Fill the bracketed parts; keep the "Model notes" block for image-to-video.

```
Camera movement:
<one prompt from the library below, verbatim>

Reference image context:
<what the first frame shows — or "No image uploaded. Use the scene details as the main visual reference.">

Scene action:
<subject> in <location>. <one simple, readable action>.

Mood and style:
<mood / look, e.g. "cinematic, natural and focused on the camera movement">

Model notes:
Use the uploaded image as the first frame when available. Preserve the subject, framing, lighting, depth, lens feel and screen direction from that image while applying only the selected camera movement.
```

For models with a short word budget, send only the `Camera movement` line plus one sentence of scene action.

## Library

### Pan / Tilt (camera rotates from a fixed point)

| ID | Move | Prompt |
|---|---|---|
| 01 | Static shot | locked-off static shot. Movement: hold one fixed camera position for the full clip. Speed: still and steady. Framing: keep the same angle, height, lens distance and composition. End: finish with the same framing and camera position. |
| 02 | Pan right | pan right. Movement: rotate the camera horizontally from left to right from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the right side of the frame. End: settle on a clear final composition. |
| 02B | Pan left | pan left. Movement: rotate the camera horizontally from right to left from one fixed point. Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the left side of the frame. End: settle on a clear final composition. |
| 03 | Whip pan right | whip pan right. Movement: rotate rapidly from the starting direction toward a new target on the right. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame. |
| 03B | Whip pan left | whip pan left. Movement: rotate rapidly from the starting direction toward a new target on the left. Speed: fast snap with brief motion blur during the rotation. Framing: begin on one readable composition and land on a second readable target. End: settle into a sharp final frame. |
| 04 | Tilt up | tilt up. Movement: rotate the camera upward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels upward. End: land on the upper target. |
| 04B | Tilt down | tilt down. Movement: rotate the camera downward from one fixed point. Speed: smooth constant tilt. Framing: keep the vertical subject or architecture centered as the frame travels downward. End: land on the lower target. |

### Zoom / Lens (lens changes, camera does not move)

| ID | Move | Prompt |
|---|---|---|
| 05 | Slow zoom in | slow zoom in. Movement: slowly increase lens focal length toward a tighter frame. Speed: gradual and even. Framing: keep the main visual target readable as it becomes larger in frame. End: finish on a stable tighter composition. |
| 05B | Slow zoom out | slow zoom out. Movement: slowly decrease lens focal length toward a wider frame. Speed: gradual and even. Framing: keep the main visual target readable as more surrounding space appears. End: finish on a stable wider composition. |
| 06 | Fast zoom in | fast zoom in. Movement: quickly increase lens focal length toward the main visual target. Speed: quick decisive zoom. Framing: keep the target centered or clearly readable during the scale change. End: finish on a stable tighter composition. |
| 06B | Fast zoom out | fast zoom out. Movement: quickly decrease lens focal length away from the main visual target. Speed: quick decisive zoom. Framing: keep the target readable as the surrounding space appears. End: finish on a stable wider composition. |
| 07A | Crash zoom in | crash zoom in. Movement: snap the lens rapidly toward the main visual target. Speed: very fast and punchy. Framing: keep the target readable through the sudden scale change. End: land on a bold tighter composition. |
| 07B | Crash zoom out | crash zoom out. Movement: snap the lens rapidly away from the main visual target. Speed: very fast and punchy. Framing: keep the target readable as the surrounding space appears. End: land on a bold wider composition. |

### Dolly / Track (camera travels toward, away from, or with the subject)

| ID | Move | Prompt |
|---|---|---|
| 08 | Dolly in | dolly in. Movement: move the camera physically forward in a straight line toward the main subject. Speed: smooth controlled push. Framing: keep camera height, lens direction and subject position consistent while distance closes. End: finish in a tighter composition. |
| 09 | Dolly out | dolly out. Movement: move the camera physically backward in a straight line away from the main subject. Speed: smooth controlled retreat. Framing: keep lens direction and camera height consistent while more environment enters frame. End: finish in a wider composition. |
| 16 | Tracking shot | tracking shot. Movement: move through the scene with the main subject. Speed: match the subject's pace. Framing: keep the subject consistently readable while the environment moves around them. End: maintain a clear moving composition. |
| 17 | Follow shot / over-the-shoulder | follow shot from behind. Movement: move behind the subject along their route at shoulder height. Speed: match the subject's pace. Framing: keep the back, shoulder or head as the foreground guide while the route ahead stays readable. End: continue following with the subject leading the frame. |
| 18 | Reverse tracking / walk-and-talk | reverse tracking shot. Movement: move backward in front of the walking subject. Speed: match the subject's forward pace. Framing: keep front-facing face and body framing stable as the background moves behind them. End: hold a clear front-facing moving composition. |
| 19 | Side tracking | side tracking shot. Movement: move parallel beside the subject along their direction of travel. Speed: match the subject's motion. Framing: keep the subject in side profile or three-quarter profile at a stable distance. End: continue the parallel movement with clear horizontal motion. |
| 20 | Low tracking | low tracking shot. Movement: move at ground or below-waist height alongside the subject's movement path. Speed: match the subject, footsteps or wheels. Framing: keep the low detail readable while the ground plane moves through frame. End: finish with the low perspective clearly maintained. |
| 21 | Vehicle tracking | vehicle tracking shot. Movement: move with the vehicle along its route. Speed: match the vehicle's pace. Framing: keep the vehicle stable in frame while the road or environment moves past. End: maintain a clear moving vehicle composition. |
| 22 | Chase shot | chase shot. Movement: follow a moving subject quickly along the action route. Speed: fast, reactive and physically close. Framing: keep the subject visible while allowing energetic reframing. End: stay connected to the subject in motion. |

### Physical Moves (camera body travels sideways, vertically, or around)

| ID | Move | Prompt |
|---|---|---|
| 10 | Truck right | truck right. Movement: move the camera physically to the right on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition. |
| 10B | Truck left | truck left. Movement: move the camera physically to the left on a straight horizontal path. Speed: smooth constant lateral travel. Framing: keep the lens facing the same direction while the scene slides across frame. End: finish on a clean lateral composition. |
| 11A | Pedestal up | pedestal up. Movement: move the entire camera vertically upward in a straight line. Speed: smooth constant lift. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the higher framing clearly readable. |
| 11B | Pedestal down | pedestal down. Movement: move the entire camera vertically downward in a straight line. Speed: smooth constant descent. Framing: keep the lens level and pointed in the same direction during the vertical move. End: finish with the lower framing clearly readable. |
| 12 | Slider right | slider right. Movement: slide the camera a small distance to the right. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new right-side angle visible. |
| 12B | Slider left | slider left. Movement: slide the camera a small distance to the left. Speed: slow controlled constant motion. Framing: keep foreground, subject and background layers readable as parallax shifts. End: finish on a refined composition with the new left-side angle visible. |
| 13 | Push past / pass-by shot | push past. Movement: move forward past a visible foreground object, edge or opening. Speed: smooth forward glide. Framing: let the foreground pass close to the lens while the space beyond becomes clearer. End: arrive inside or beyond the foreground layer. |
| 14 | Arc right | arc right. Movement: move on a shallow curved path around the main subject toward the right side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new right-side angle. |
| 14B | Arc left | arc left. Movement: move on a shallow curved path around the main subject toward the left side. Speed: smooth measured curve. Framing: keep distance, height and subject readability consistent while the angle changes. End: finish from a new left-side angle. |
| 15 | Orbit clockwise | clockwise orbit. Movement: circle clockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing. |
| 15B | Orbit counterclockwise | counterclockwise orbit. Movement: circle counterclockwise around the main subject at a consistent radius. Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates around them. End: complete the intended arc or full circle with stable framing. |

### Human Camera (operator feel)

| ID | Move | Prompt |
|---|---|---|
| 23 | Handheld shot | handheld shot. Movement: hold the camera at human operator height with natural body movement. Speed: responsive and organic. Framing: keep the subject readable while the frame has subtle sway and micro-adjustments. End: finish with a natural handheld composition. |
| 24 | Body-mounted camera / Snorricam | body-mounted Snorricam. Movement: keep the camera fixed relative to the subject's torso or face while the subject moves. Speed: match the subject's body motion. Framing: keep the subject close, centered and facing the camera as the background moves around them. End: finish with the subject still locked in frame. |

### Drone / Crane (large vertical or aerial moves)

| ID | Move | Prompt |
|---|---|---|
| 25 | Crane up | crane up. Movement: travel smoothly upward through open space. Speed: slow controlled vertical lift. Framing: keep the subject or location readable as the camera rises. End: finish with the higher scale clearly visible. |
| 25B | Crane down | crane down. Movement: travel smoothly downward through open space. Speed: slow controlled vertical descent. Framing: keep the subject or location readable as the camera descends. End: finish with the lower subject or destination clearly visible. |
| 26 | Drone push in | drone push in. Movement: fly smoothly forward through open space toward the subject or destination. Speed: controlled aerial glide. Framing: keep the route and destination readable as the camera approaches. End: arrive at a closer aerial composition. |
| 26B | Drone pull back | drone pull back. Movement: fly smoothly backward away from the subject or destination. Speed: controlled aerial retreat. Framing: keep the subject readable as more landscape appears. End: finish on a wider aerial composition. |
| 27 | Helicopter shot | helicopter-style aerial shot. Movement: move from high altitude along a broad gradual flight path. Speed: steady controlled aerial motion. Framing: keep the landscape or distant moving subject readable at wide scale. End: finish on a stable high-altitude composition. |

### Specials

| ID | Move | Prompt |
|---|---|---|
| S1 | First-person view | first-person view. Movement: move forward at human eye height from the character's perspective. Speed: natural walking or reaching pace. Framing: use visible hands, arms or body edges as the viewer's physical reference. End: arrive at the next point of action from the same point of view. |
| S2 | Tilt-shift | tilt-shift miniature view. Movement: hold or glide from a high angled view over the scene. Speed: small precise movement. Framing: keep a narrow band of sharp focus across the key subject area with soft blur above and below. End: finish with the miniature-scale view intact. |
| S3 | Infinite zoom | infinite zoom. Movement: zoom continuously inward toward the exact center target. Speed: smooth accelerating zoom. Framing: keep the circular target centered as it expands. End: finish when the next visual world fills the frame. |
| S4 | Earth zoom out | earth zoom out. Movement: pull upward from the starting point through street, city, landscape and planet scale. Speed: rapid expanding zoom out. Framing: keep the original location centered as scale grows. End: finish on a planet-scale view with the starting point still implied at center. |
| S5 | Time-lapse | locked-camera time-lapse. Movement: hold one fixed camera position while time moves rapidly forward. Speed: fast time compression with a stable camera. Framing: keep the same composition and horizon as motion passes through the frame. End: finish from the same camera angle with visible passage of time. |
| S6 | Pass-through objects | pass-through movement. Movement: move forward toward a visible object, surface or barrier and continue into the space beyond. Speed: smooth centered glide. Framing: keep the opening or surface centered as the transition point. End: arrive inside the revealed space beyond. |

## Rules when adapting

- **Change the nouns, keep the structure.** Replace "the main subject" with the real subject if it helps; keep Movement / Speed / Framing / End.
- **One move per clip.** Do not join two library prompts in one generation. Need two moves? Generate two clips and cut.
- **Do not mix look-alike moves.** Zoom (lens) vs dolly (camera travels); pan (rotates) vs truck (travels sideways); tilt (rotates) vs pedestal/crane (travels vertically). Use the exact library name so the model gets one clear signal.
- **Static means static.** If anything moves the frame, do not use prompt 01.
- **Watch each move's preview** on the source site if unsure what it looks like — every card has a looping example clip.

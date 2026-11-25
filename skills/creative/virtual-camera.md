# Virtual Camera — Camera Work for Code-Rendered Scenes

## When to Use

Any scene rendered by code: HyperFrames, Remotion, the animate and lemo-opuscar plugins, Three.js. `camera-direction.md` covers cameras inside AI-generated clips; this skill covers the camera **you build**.

Use it at `scene_plan` (one camera line per scene) and at `compose` (author the move, then check it).

A code-rendered video with no camera is a slideshow with nicer fonts. Every scene gets a camera line, even if the line is "locked off, because the action is the motion".

## Prerequisites

| Resource | Path | Purpose |
|---|---|---|
| World wrapper, zoom, pan, focus-lock | `.agents/skills/hyperframes-animation/rules/viewport-change.md` | The mechanics every move here is built on |
| Phased zoom + drift | `.agents/skills/hyperframes-animation/rules/multi-phase-camera.md` | Pull-back / focus / push |
| Zoom to an off-centre target | `.agents/skills/hyperframes-animation/rules/coordinate-target-zoom.md` | Counter-translate maths |
| Rack focus | `.agents/skills/hyperframes-animation/rules/depth-of-field-blur.md` | Focus shifts between planes |
| Speed blur | `.agents/skills/hyperframes-animation/rules/motion-blur-streak.md` | Blur on fast moves |
| Easing | `.agents/skills/gsap-core`, `gsap-plugins` (CustomEase) | Custom curves |
| Hits on words | `skills/creative/hook-and-retention.md` | What the camera must land on |

## Process

### Step 1: Build the scene in depth

A camera move over a flat page shows nothing. Before any move, split the scene into **at least three planes** inside one `.world` wrapper:

| Plane | Moves at | Holds |
|---|---|---|
| Foreground | 1.0× (or more) | Soft, partly out-of-frame shapes that the camera passes |
| Subject | 0.5–0.7× | The thing the line is about |
| Background | 0.2× | Texture, sky, far detail |

- When the subject moves, the background counter-moves 20–30% of that distance.
- Build every plane at ≥ 105% of the frame (≥ 110% for pans) so edges never show.
- Captions, titles and logos sit **outside** the camera wrapper. They never move with it.

### Step 2: Write one camera line per scene

Format: **move, seconds, speed, target — reason.**

```
push in, 3 s, slow, onto the cracked screen — the problem becomes personal
```

Pick the move by what the beat needs:

| The beat must… | Move |
|---|---|
| Raise tension, say "this matters" | Push in |
| Reveal context or scale | Pull back |
| Travel, show sequence, compare things in a row | Track / truck (planes slide at different rates) |
| Jump energy to a new subject | Whip (0.2–0.35 s) |
| Hit a word hard (shorts) | Punch-in: zoom to 1.35 in 0.24 s, hold, release in 0.5 s |
| Move attention without moving the frame | Rack focus (0.5–1.5 s) |
| Feel present, human, unsteady | Handheld drift |
| Show an object from more than one side | Arc (Three.js / 3D transforms only) |
| Let fast action read | Locked off |

Rules:

- One main move per scene, plus at most one small secondary (drift or focus).
- Consecutive scenes differ in move, size or direction.
- Big tricks — dolly zoom, freeze, speed ramp — once per video.
- The camera notices: it **lands on the subject about 0.3 s after the subject appears**, and starts moving 0.3 s before a new element enters.
- A constant slow push of 3–5% across a scene is the floor. The exception is the quiet beat before the hero moment (`hook-and-retention.md` Step 5): there the camera stops, but the footage itself keeps moving. Never hold a frozen frame of live footage.
- **Chase, don't follow.** To follow a moving subject, key the camera slightly ahead of it (about 0.1 s). For a snap, the camera reaches the landing point before the subject does.
- Declare what must never leave the frame (the subject, the product) and check every frame of the move for it.
- Do not reframe on every beat — the camera becomes the metronome. Hold one direction of travel across a sequence and let speed carry the beat; alternating sides flips screen direction.
- An empty background gives the eye nothing to measure the move against. Add faint far texture (a dot grid, grain, distant shapes).

### Step 3: Speed has numbers

| Word | Subject size change | Time to cross the frame |
|---|---|---|
| Slow | ≤ 10% per second | ≥ 6 s |
| Medium | 10–25% per second | 3–6 s |
| Fast | > 25% per second | < 3 s |

Typical lengths: push or pull 3–6 s; push onto a detail 2–4 s; whip 0.2–0.35 s; rack focus 0.5–1.5 s.

For a move from zoom `z1` to `z2` over normalised distance `d`, a good default length is `clamp(0.9 + 0.5·|ln(z2/z1)| + 0.6·d, 0.95, 1.7)` s.

Limits: maximum zoom 2.2; the subject fills about 70% of the frame at rest; at least 2.2 s between moves; ignore changes under 8%; push in only if the result is ≥ 1.3× closer and the viewer gets ≥ 1.5 s to look.

### Step 4: Easing

- **First scene:** never ease in. Start already moving; ease out.
- **Scenes inside a sequence:** use an inertia curve so the camera is moving at frame 0 and still moving at the cut: `0.35·k + 0.65·k²·(3 − 2k)` (register it as a CustomEase or apply it in `onUpdate`).
- **Last scene, or a hold:** ease out to rest, then hold 4–6 frames.
- **Zoom:** tween `ln(zoom)`, not zoom. Linear zoom looks like it slows down as it gets closer.
- Equal spacing between frames means linear motion. Linear camera moves read as machine-made — only a constant drift may be linear.

### Step 5: Cuts between moving shots

- Cut at the move's fastest moment, not at rest.
- Keep direction and speed the same on both sides. A zoom keeps its sign across the cut.
- The subject sits within a tenth of the frame of where it was.
- Never use the same designed transition twice in a row.
- Every cut adds information. If it does not, move the camera instead.

### Step 6: Handheld, shake, blur

All must be pure functions of timeline time so they survive seeking. No `Math.random`, no per-frame jitter.

- **Handheld:** sum of sines at unrelated rates, e.g. `x = 3.5·sin(0.83t + 1.3) + 2·sin(1.71t + 0.2) + 1.2·sin(3.3t)` px at 1080p, roll `0.12·sin(0.51t)`°. Divide the amplitude by the current zoom.
- **Impact shake:** `amp·(1 − u)²·sin(60u)`, `u` from 0 to 1 over 0.3–0.35 s, `amp` 5–7 px at 1080p. Fire it on the contact frame, with the sound.
- **Hit-stop:** freeze the scene 2–3 frames on contact (up to 0.3 s for the final hit) while sparks and shake continue.
- **Speed blur:** add `motion-blur-streak` when the camera moves faster than about 3 px per frame at 1080p; add a whoosh above about 45 px per frame.
- **Spotlight:** a soft radial dim that follows the camera target keeps the eye where the camera is going (strength 0.15–0.3 on wide framings).

### Step 7: Record it

In `scene_plan`: `shot_language.camera_movement` takes the nearest schema value (`dolly_in`, `tracking_right`, `rack_focus`, `handheld`, `static`…). Put the full camera line in `framing`, and the reason in `shot_intent`.

### Step 8: Check the move

Render, then look. Do not trust the code.

1. **Contact sheet:** first, middle and last frame of every scene. Is the subject lit and readable? Is anything cut by the frame edge? Is any frame empty mid-move?
2. **Strip:** every frame of each key move, side by side.

| Check | Pass |
|---|---|
| One thing leads the eye | yes |
| Gaps between frames change (not equal) | yes — equal gaps = linear = redo |
| No pop or jump at the start, end or cut | yes |
| Planes separate (parallax visible) | yes |
| No plane edge enters the frame | yes |
| Subject never leaves the frame | yes, on every frame |
| Overlays stayed fixed | yes |
| Move lands on its word (±0.1 s) | yes |
| Hold after landing | 4–6 frames |
| At most a third of elements move at once | yes |

Write each preview to a new filename; a cached preview hides the fix.

## Common Pitfalls

- **Scaling a flat page.** With one plane there is no parallax; it reads as a zoomed slide. Split the planes first.
- **Ease-in-out on every shot.** The camera stops at each cut and the video stutters. Use the inertia curve inside a sequence.
- **Drift counted as a move.** Constant drift is the floor, not the camera line.
- **Camera moves the captions.** Overlays belong outside the wrapper.
- **Random shake.** It changes on every render and breaks frame seeking. Use sine sums.
- **Moving everything.** If the camera and all elements move together, nothing leads. Camera moves, or the subject moves — rarely both at full strength.
- **Push-in with nowhere to go.** Starting at the final framing leaves no room. Start one size wider.
- **A new move every second.** Leave 2.2 s between moves, 1.5 s between punches.

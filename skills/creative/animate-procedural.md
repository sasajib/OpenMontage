# Animate — procedural canvas animation in a printed / hand-made style (creative skill)

> Style id: `animate-<style>` (e.g. `animate-riso`) · Engine: the `animate` Claude Code plugin (cth9191/animate, MIT) · Runtime: **ffmpeg** (the engine renders its own MP4; OpenMontage ingests it as a clip)

**What it is:** a single `<canvas>` drawn and scored procedurally, deterministic frame by frame, rendered with Playwright Chromium + ffmpeg. Seven shipped looks — **cut paper, crosshatch ink, riso print, sketchbook, math (manim-style), pixel, isometric** — plus a procedure for matching a new look from the user's references. Shape-morph transitions, a synthesized score or a beat-mapped user track, and a measured review (cuts on grid, story arc, text safety, LUFS).

Like Ink Theater it is a **style + engine on the `animation` pipeline, NOT a new pipeline**. Don't look for an `animate.yaml`. OpenMontage keeps research, proposal, script, checkpoints, reviewer and publish; animate replaces the *scene authoring + rendering* step only.

## When to pick it (vs HyperFrames / Remotion / Ink Theater)

| Brief wants | Pick |
|---|---|
| Risograph / cut-paper / crosshatch / sketchbook / pixel / isometric look; "feels printed or hand-made"; a short history, explainer or little story with morph transitions | **animate** |
| A look matched from the user's reference stills or video, in code | **animate** (`new-style.md` procedure) |
| Black-ink-on-white doodle with a mascot operating a contraption | Ink Theater |
| Kinetic type, product promo, UI-driven motion, data charts, captions | HyperFrames / Remotion |

Present it at proposal as one of the runtime options (the HARD RULE in `AGENT_GUIDE.md` still applies: list Remotion and HyperFrames too, recommend one, wait for approval). Log it as `render_runtime: "ffmpeg"` with `reason` naming the animate engine and style, and set `selected_concept.animation_mode: "illustrative"` with the engine + style in `reuse_strategy`.

## Locate the engine

```bash
SKILL=$(ls -d ~/.claude/plugins/cache/animate/animate/*/skills/animate | tail -1)
node -e "require('$(npm root -g)/playwright')" && ffmpeg -version | head -1   # both must work
```

If the plugin is missing: `claude plugin marketplace add cth9191/animate && claude plugin install animate@animate`, then `npm i -g playwright && npx playwright install chromium`. Escalate instead of substituting another engine if that fails.

Read `$SKILL/SKILL.md` and `$SKILL/craft.md` before authoring, and the chosen style's `$SKILL/styles/<style>/STYLE.md` (its rules + frame checklist). The style gallery for the user: `node $SKILL/tools/gallery.mjs <out.png>`.

## Where things live

The piece is part of the OpenMontage project directory, never the repo root:

```
projects/<name>/animate/pieces/<piece>/     piece.json, brief.md, LOG.md, src/, voice/, audio/, assets/
projects/<name>/animate/pieces/<piece>/renders/share.mp4   ← the asset OpenMontage ingests
projects/<name>/animate/styles/<custom>/    a look matched from references (only if made)
```

Start a piece by copying the style's demo: `cp -r $SKILL/styles/<style>/demo projects/<name>/animate/pieces/<piece>` (or `$SKILL/templates/beat-cut/` for hard cuts on the beat).

## Stage mapping

| OpenMontage stage | What animate contributes | What OpenMontage still owns |
|---|---|---|
| research / proposal | style gallery, format choice from `grammar/FORMATS.md` | concepts, cost, runtime decision, approval gate |
| script | one line per beat ≤ 3.5 words/s, written as spoken | `script` artifact, voice performance plan |
| scene_plan | the **storyboard**: `TIMELINE.board` → `node $SKILL/tools/storyboard.mjs` → show panels, thumbs up/down by number | `scene_plan` artifact; each scene = one beat/panel, `animation_mode: illustrative`, N/A camera aspects explicit |
| assets | narration via `tts_selector` (see Voice), music via `music_gen` or the user's track, then **build + export** (below) | `asset_manifest`: one entry `type: "animation"`, `source_tool: "animate"`, `path: animate/pieces/<piece>/renders/share.mp4`, plus narration/music entries |
| edit | nothing (timing already lives in the piece) | `edit_decisions`: `render_runtime: "ffmpeg"`, one cut per exported clip |
| compose | `tools/review.mjs` numbers go into `final_review` | `video_compose` ffmpeg pass (see Compose) + post-render self-review |

The animate check-ins (story → look → storyboard) sit inside OpenMontage's `proposal` → `scene_plan` checkpoints. Do not animate before the storyboard checkpoint passes; a wrong look costs a full build.

## Voice (narration): OpenMontage TTS feeds animate's clock

Animate wants **one audio file per script line** in `<piece>/voice/<id>.mp3`, referenced from `voice/script.json`. Generate them with `tts_selector` (the approved provider/voice from the proposal), not animate's ElevenLabs-connector flow. Then:

```bash
node $SKILL/tools/voice.mjs <piece>          # voice.wav + voice.json (word times via faster-whisper; estimated if not installed)
```

Set `"voice": { "file": "voice/voice.wav", "music": -12 }` in `piece.json`. Export mixes voice over the score at −14 LUFS, so the exported MP4 already carries narration + score. Re-takes re-time the picture: rerun `voice.mjs`, rebuild.

No narration → skip this; the composed score (or the user's track via `tools/beats.mjs`) is the soundtrack.

## Build, export, review

```bash
node $SKILL/tools/build.mjs <piece>                        # one index.html; refuses external URLs/assets
node $SKILL/tools/tile.mjs <piece> tile.png 24 48 96       # look at tiles across every morph/cut
node $SKILL/tools/export.mjs <piece> --share [--formats 9:16,1:1,16:9] [--blur 4]
node $SKILL/tools/review.mjs <piece> [--format 16:9]       # must PASS; read the contact sheets + phone.jpg
```

Record the review's numbers (cut-grid result, story-arc PASS count, text warnings, LUFS, true peak) in the piece's `LOG.md` and carry them into `final_review`. Riso demo benchmark on this machine: 144 frames at 1080×1920 in ~27 s.

## Compose (ffmpeg pass-through)

`edit_decisions` for a single exported piece:

```json
{ "version": "1.0", "render_runtime": "ffmpeg",
  "cuts": [{ "id": "piece", "source": "projects/<name>/animate/pieces/<piece>/renders/share.mp4",
             "in_seconds": 0, "out_seconds": <duration> }],
  "metadata": { "compose_target": { "width": 1080, "height": 1920, "fit": "pad" } } }
```

Call `video_compose` with `operation: "compose"`. Omit `audio_path` when the export already mixed narration + score (the usual case); pass it only to lay a separately produced track over a silent piece. Several pieces or formats → one cut each; subtitles via `subtitle_path` as usual. Then the mandatory post-render self-review from `compose-director.md`.

## Non-negotiables

- **Deterministic:** seeded `RNG(...)` only, never `Math.random()` or wall-clock. Build enforces single-file, no URLs, no web fonts.
- **Every on-screen factual claim is web-checked and sourced** in `brief.md` (animate rule 3) — this is in addition to OpenMontage's research brief.
- **Reference media stays local** and is never credited or copied unless the user asks.
- **Formats are laid out, not cropped:** list them in `piece.json` `"formats"`; never crop 9:16 to 16:9.
- **Decision log:** `render_runtime_selection` must list remotion + hyperframes as considered; `provider_selection` for the TTS voice as usual. If the engine is unavailable mid-run, escalate — don't fall back to HyperFrames silently.
- **Proven formats:** per the plugin author only F2 (chronology / morph chain), F4 (mission) and F5 (fixed-hero journey) have passed every check on real pieces; cut paper and crosshatch have carried full pieces, the other styles one or two. Say so at proposal when picking something else.

## Reference builds

- Riso style demo exported and reviewed 2026-11-01 (6 s, all checks PASS). Rebuild it any time: `cp -r $SKILL/styles/riso/demo /tmp/riso && node $SKILL/tools/build.mjs /tmp/riso && node $SKILL/tools/export.mjs /tmp/riso --share && node $SKILL/tools/review.mjs /tmp/riso`.

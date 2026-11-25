# Lemo-Opuscar — code-rendered film styles (creative skill)

> Style id: `opuscar-<slug>` (e.g. `opuscar-watercolor`, `opuscar-satellite-briefing`) · Engine: the `lemo-opuscar` Claude Code plugin (lemomo-ai/lemo-opuscar, MIT) · Runtime: **ffmpeg** (the engine renders and masters its own MP4; OpenMontage ingests it as a clip)

**What it is:** a library of 66 film styles, each a fixed `STYLE.md` (look, colour, type, motion, camera grammar, sound palette) plus a demo film made entirely in code — Canvas 2D, three.js or WebGL2 pages rendered frame by frame with headless Chromium, scored and mixed in Python, mastered with ffmpeg. No video model. Groups: Edit & Documentary (caption news, newsreel, visual investigation, news package…), Evidence Films (satellite briefing, LiDAR survey, teardown, archive light table…), Hand-drawn & Painting (watercolor, ink wash, impasto, chalkboard, whiteboard…), East Asian Traditions, Print & Printmaking (risograph, woodcut, engraving…), Graphic & Type (Swiss motion, art deco, blueprint, ASCII/CRT…), Information & Keynote (dataviz, iso-infographic, dark keynote, transit map…), Cartoon & Anime, Games, Cinema & Eras, Materials & 3D. Catalog: `$LIB/styles/README.md`.

Like Ink Theater and the animate plugin it is a **style + engine on the `animation` pipeline, NOT a new pipeline**. Don't look for an `opuscar.yaml`. OpenMontage keeps research, proposal, script, checkpoints, reviewer and publish; opuscar replaces the *treatment → page authoring → render → mix* step only. Everything it needs lives outside the OpenMontage repo (`~/lemo-opuscar`); nothing here changes existing tools or runtimes.

## When to pick it (vs HyperFrames / Remotion / animate / Ink Theater)

| Brief wants | Pick |
|---|---|
| A named painterly, print, era, game or documentary **film look** from the catalog ("make it look like a 1920s newsreel / ukiyo-e / satellite briefing / whiteboard explainer") | **opuscar** |
| An explainer built from real material: satellite imagery, archive footage and documents, scans, CAD, point clouds | **opuscar** (Evidence Films / Edit & Documentary groups) |
| A 3D or shader-heavy look in code (hologram HUD, brick toy, HD-2D, stained glass) | **opuscar** |
| Riso / cut paper / crosshatch / pixel as a short *morph-chain* story with the animate plugin's review gates | animate (`animate-procedural.md`) — both ship a riso and a pixel look; prefer animate for ≤ 30 s morph chains, opuscar for a longer film with narration, score and camera grammar |
| Black-ink-on-white doodle with a mascot | Ink Theater |
| Kinetic type, product promo, UI motion, data captions, website-to-video | HyperFrames / Remotion |

Present it at proposal as one of the runtime options (the HARD RULE in `AGENT_GUIDE.md` still applies: list Remotion and HyperFrames too, recommend one, wait for approval). Log `render_runtime: "ffmpeg"` with `reason` naming the opuscar engine and style slug, and set `selected_concept.animation_mode: "illustrative"` with engine + style in `reuse_strategy`. Say at proposal that an opuscar film costs **30–60 min of agent time and a large token budget** (the library's own estimate) and that its styles were tuned on Opus 5.5.

## Locate the engine

```bash
SKILL=.claude/skills/lemo-opuscar   # repo copy of the plugin skill (run from the repo root)
export LEMO_OPUSCAR_HOME=$PWD/vendor/lemo-opuscar   # upstream clone: git -C vendor/lemo-opuscar pull
LIB=$(sh "$SKILL/scripts/setup.sh" | tail -1 | sed 's/^LIB=//')    # clones/updates ~/lemo-opuscar, prints the path
node -v; ffmpeg -version | head -1                                 # Node ≥ 20, ffmpeg ≥ 7 (6.x breaks mux.sh loudnorm)
ls "$LIB/node_modules/.lemo-ok" "$LIB/.venv/.lemo-core"            # core deps present? else: sh "$SKILL/scripts/setup.sh" deps
```

If `vendor/lemo-opuscar` is missing: `git clone https://github.com/lemomo-ai/lemo-opuscar.git vendor/lemo-opuscar`; the skill folder also ships in it at `plugin/skills/lemo-opuscar`. Escalate instead of substituting another engine if that fails.

Tiers: `deps` = core (~350 MB); `deps voice` = Kokoro TTS + faster-whisper (used by the `asr_check.py` delivery gate; narration itself comes from OpenMontage, see Voice) — Kokoro needs Python < 3.14, the setup script uses `uv` to fetch 3.12; `deps music` = numba for `pluck.py`; `sh tools/fetch.sh instruments all` for the five sample packs (1.4 GB); `sh tools/fetch.sh hdri` for 3D styles. **All of these are installed on this machine as of 2026-11-02**, so no tier download is needed before a film. Style-specific packages named in a `STYLE.md` go into the project folder, never `$LIB/.venv`.

Read, in this order, before authoring: `$LIB/AGENTS.md` (workflow), `$LIB/DIRECTOR.md` (story, sound, rhythm, camera, checks, delivery), `$LIB/TECHNIQUE.md` (page contract, timeline, voice, music, mix, review loop), `$LIB/core/README.md` (every tool command), then the chosen `$LIB/styles/<slug>/STYLE.md`. Fetch the demo source **only after** the treatment is written: `sh "$SKILL/scripts/setup.sh" demo <slug>` — and use it for techniques, never its story. Exception: Edit & Documentary styles fetch the demo first for the material tools in `demo/tools/`.

## Where things live

The film is part of the OpenMontage project directory, never the repo root and never inside `$LIB/styles/`:

```
projects/<name>/opuscar/<film>/            index.html, timeline.js, mix.py, build.sh (LIB=<path> at the top), TREATMENT.md, CREDITS
projects/<name>/opuscar/<film>/voice/      <id>.wav per script line + dur.json   ← from OpenMontage TTS
projects/<name>/opuscar/<film>/out/        video.mp4 (silent), mix.wav, stills/, events.json
projects/<name>/opuscar/<film>/<film>.mp4  ← the mastered asset OpenMontage ingests (+ poster.jpg, <film>.srt)
```

Path rules from the skill: lowercase letters, digits, hyphens in the folder name; no `#` or `?`; pages reach library files by absolute URL (`/core/lib.js`, `/node_modules/three/…`); scripts and `build.sh` use `$LIB/…`, never `../..`. Run every tool **from `$LIB`** with the project's absolute path:

```bash
cd "$LIB" && node core/render/still.mjs "$PWD_PROJECT/opuscar/<film>" 1.5 3 --range 0:60:2
```

## Stage mapping

| OpenMontage stage | What opuscar contributes | What OpenMontage still owns |
|---|---|---|
| research / proposal | style catalog (`styles/README.md`), a benchmark film (DIRECTOR §2), format and duration | concepts, cost, runtime decision, approval gate |
| script | lines written as spoken, numbers spelled out for TTS and as digits for subtitles (TECHNIQUE §4) | `script` artifact, voice performance plan |
| scene_plan | **`TREATMENT.md`**: three candidate structures and the choice (DIRECTOR §4), then the look proven with stills (DIRECTOR §5) | `scene_plan` artifact; each scene = one section of `timeline.js`, `animation_mode: illustrative`, N/A camera aspects explicit |
| assets | narration via `tts_selector` (see Voice), score via `music_gen` or the library's sampler/synth, then **build** (below) | `asset_manifest`: one entry `type: "animation"`, `source_tool: "lemo-opuscar"`, `path: opuscar/<film>/<film>.mp4`, plus narration/music entries; `CREDITS` copied into the project's attribution |
| edit | nothing (timing lives in `timeline.js`) | `edit_decisions`: `render_runtime: "ffmpeg"`, one cut per film |
| compose | review-loop numbers (LUFS, blackdetect, readcheck, asr) go into `final_review` | `video_compose` ffmpeg pass (see Compose) + post-render self-review |

The opuscar check-ins (treatment → proven look stills → contact sheets) sit inside OpenMontage's `proposal` → `scene_plan` checkpoints. **Do not run `video.mjs` before the scene_plan checkpoint passes**: a full render is minutes per version and a wrong look costs a rebuild.

## Voice (narration): OpenMontage TTS feeds opuscar's clock

The library's tools expect **one WAV per script line** in a voice folder (24 kHz, mono, leading/trailing silence trimmed) and a `dur.json` of `{ "<id>": seconds }`. Generate the lines with `tts_selector` (the approved provider/voice from the proposal), not the library's Kokoro/edge-tts flow, then normalise:

```bash
for f in voice/raw/*.mp3; do id=$(basename "$f" .mp3)
  ffmpeg -y -loglevel error -i "$f" -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 24000 -ac 1 "voice/$id.wav"; done
python3 - <<'EOF'
import json, glob, soundfile as sf, os
d={os.path.basename(p)[:-4]: round(sf.info(p).duration,3) for p in glob.glob('voice/*.wav')}
json.dump(d, open('voice/dur.json','w'), indent=1)
EOF
```

`timeline.js` sections are then sized from `dur.json`. Re-takes re-time the picture: regenerate the line, rerun the snippet, rebuild. The transcription gate in DIRECTOR §11 (`asr_check.py`) needs the `voice` tier; OpenMontage's own `transcriber` tool is an acceptable substitute when that tier is not installed — log which one was used. No narration → skip this; the score is the soundtrack.

## Build, review, deliver

```bash
cd "$LIB"
node core/render/still.mjs "$P" --range 0:${DUR}:2 && .venv/bin/python core/render/sheet.py "$P/out/sheet.jpg" "$P"/stills/*.jpg   # contact sheet, review at full size
node core/render/readcheck.mjs "$P"                       # every on-screen text stays long enough; must exit 0
sh "$P/build.sh"                                          # events → video.mjs → mix.py → mux.sh (−14 LUFS, grain)
ffmpeg -i "$P/<film>.mp4" -af ebur128 -f null - 2>&1 | tail -12 ; ffmpeg -i "$P/<film>.mp4" -vf blackdetect -f null - 2>&1 | grep black
```

Deliver what DIRECTOR §11 lists in the film folder: `<film>.mp4`, `poster.jpg`, `<film>.srt` when there is speech, `TREATMENT.md`, `CREDITS`, the source with a one-command `build.sh`. Run the "not the demo again" check (at least four of six structural elements differ from the demo) and the LemoLab sign-off grep before delivery. Record LUFS, true peak, blackdetect, readcheck and asr results in `final_review`.

## Compose (ffmpeg pass-through)

`edit_decisions` for a single mastered film:

```json
{ "version": "1.0", "render_runtime": "ffmpeg",
  "cuts": [{ "id": "film", "source": "projects/<name>/opuscar/<film>/<film>.mp4",
             "in_seconds": 0, "out_seconds": <duration> }],
  "metadata": { "compose_target": { "width": 1920, "height": 1080, "fit": "pad" } } }
```

Call `video_compose` with `operation: "compose"`. Omit `audio_path`: the film already carries narration + score mastered to −14 LUFS. Subtitles via `subtitle_path` as usual if OpenMontage burns them; otherwise ship the `.srt` beside the file. Vertical: pass `--size 1080x1920` to **every** render tool and lay the page out from `innerWidth × innerHeight` (TECHNIQUE §2); never crop a landscape render.

## Non-negotiables

- **Deterministic:** seeded `mulberry`/`hash` from `core/lib.js`, never `Math.random()` or `Date.now()`; any frame renders alone, in any order.
- **`STYLE.md` is fixed, everything else is directed from the user's topic.** Never bend the topic toward the demo; never build inside `$LIB/styles/`.
- **Treatment before demo.** Write `TREATMENT.md` before fetching or reading the demo (Edit & Documentary excepted).
- **Every on-screen factual claim is sourced** in OpenMontage's research brief; maps, globes and satellite views pass DIRECTOR §13 checked enlarged.
- **Copyright red lines** (DIRECTOR §12) and `CREDITS` for every third-party asset: fonts, samples, images, the voice engine. The user owns the film; no LemoLab credit or watermark.
- **Decision log:** `render_runtime_selection` must list remotion + hyperframes as considered; `provider_selection` for the TTS voice as usual. If the engine is unavailable mid-run, escalate — don't fall back to HyperFrames silently.
- **Disk:** a full render writes every frame as JPEG then encodes; keep a few GB free (see `animate-export-troubleshooting` for the ENOSPC pattern).

## Gotchas seen on this machine (2026-11-02)

- **Demos are reference only and do not render.** Their font binaries are not in git (only the OFL licence files ship), so `video.mjs` on a fetched demo fails with `[pageerror] A network error occurred` after a font 404. Read demo code for techniques; never try to rebuild it.
- **Sampled instruments are fetched per pack.** `sampler.py` raises `its sample library "<lib>" is not downloaded` naming the pack. All five (`freepats`, `vcsl`, `salamander`, `karoryfer`, `vsco2ce`) are installed under `$LIB/core/audio/instruments/`, so this only recurs after a fresh clone.
- **Whisper for `asr_check.py` downloads `base.en` from Hugging Face on first run** (~145 MB, cached in `~/.cache/huggingface`); done once on this machine. Chinese needs `small` on its first run.
- Some demo `score.py` files import `librosa` for a maintainer self-check after writing `score.wav`; it is in `requirements-dev.txt` only. Not needed for your own films.
- Run OpenMontage tools with the project's `.venv/bin/python`; the system Python lacks `jsonschema` and the registry fails to discover.
- Playwright warns the OS is unsupported (Manjaro) and uses the Ubuntu 24.04 build; it works.

## Reference builds

- Plugin installed and library cloned 2026-11-02 at `~/lemo-opuscar` (sparse: guides, core tools, every `STYLE.md`; demos fetched on demand). Core, voice and music tiers, all five sample packs, HDRIs and the English Whisper model installed. Voice tier verified: `tts.py` spoke one line (af_bella), `asr_check.py` matched it word for word, exit 0.
- Smoke film 2026-11-02: a 6 s page against the contract (`DUR`, `render(t)`, `TEXTS`, `READY`, seeded `mulberry`) → `still.mjs` 3 stills, `readcheck.mjs` OK, `video.mjs` 144 frames in 4 s with 3 workers, `mux.sh` to −14.0 LUFS / −1.5 dBFS peak, then `video_compose` `render_runtime: "ffmpeg"` single-cut ingest → 1920×1080 with audio. The whole chain ran in under 10 s.

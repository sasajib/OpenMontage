---
name: video-reality-check
description: Use before any image-to-video job, before a generated clip enters an edit, and after a render, to run the reality_check tool (anatomy, identity drift, wardrobe continuity, camera motion, vision checklist) and act on its PASS / REVIEW / REJECT.
category: video-production
---

# Video reality check

The `reality_check` tool (`tools/analysis/reality_check.py`) is the automated half of the reality-check gate; the rules it enforces are in `generated-visual-anatomy-qa`. It is CPU-only, $0 for the local checks, and runs in 10-40 s per 10 s clip.

## When to run it (cost ladder, user rule 2026-11-07)

| Point | Input | Why here |
|---|---|---|
| **Still, before the clip is requested** | the still + character sheet + still prompt | one image is cheap; a bad still becomes 10 s of slop |
| **Clip, before the edit** | the clip + sheet + clip prompt + `expect` | a bad clip costs one generation; a bad render costs the whole compose |
| **Render, after compose** | the final file at 1 fps, no reference | last net: cuts, captions, black frames, continuity across scenes |

Never request a clip from an unchecked still. Never start a render with an unchecked clip in the timeline.

## How to call it

```python
from tools.tool_registry import registry; registry.discover()
r = registry.get("reality_check").execute({
    "input_path": "projects/<id>/assets/video/clips/sc14.mp4",
    "reference_face": "projects/<id>/assets/images/ref_face.png",   # omit for shots with no face
    "scene_prompt": "<the still or clip prompt>",
    "expect": {"people": 1, "camera": "static"},                      # camera: static | slow | moving
    "fps": 2, "vlm": True,
})
r.data["verdict"], r.data["report_path"]
```

Output: `<input>.reality/report.md` + `report.json` + the sampled frames `f_NNN.png`.

## What each check does and how to read it

| Check | Signal | Fails when |
|---|---|---|
| anatomy | MediaPipe pose + hands per frame | more people than `expect.people` in >= 25 % of frames (critical); more than 2 hands per person (critical); legs cut by the frame edge (reported) |
| identity | InsightFace embedding vs `reference_face` | best frame < 0.20 cosine (not the person), or any frame < 60 % of the best (the face drifted mid-clip). Frame-to-frame < 0.55 = morph |
| continuity | dominant saturated colour (wardrobe) per frame | HSV jump > 28 between consecutive frames (suit changes colour, light flips) |
| camera | median optical flow per second | `expect.camera: static` but the clip moves (major); `slow` but fast (minor) |
| vlm | checklist over 6 frames | gear geometry, prop provenance, environment, cast, framing, physics, continuity, camera |

Mittens and goggles hide hands and eyes from the detectors; that is fine (the design rule says to hide them) but it means the hand count cannot prove anything in those shots. The VLM/agent pass is what catches gear and prop errors; the local checks cannot.

## The VLM pass

- Default on this machine: **GLM-5.3-flash on the z.ai coding plan** (vision built in). `.env` has `GLM_API_KEY`, `REALITY_CHECK_VLM_BASE_URL=https://api.z.ai/api/coding/paas/v4`, `REALITY_CHECK_VLM_MODEL=glm-5.3-flash`; the tool disables thinking and parses the JSON out of the reply. Cost: covered by the subscription. The public z.ai endpoint (`/api/paas/v4`) returns "insufficient balance" with this key; keep the coding base URL.
- Any OpenAI-compatible vision endpoint works via `REALITY_CHECK_VLM_KEY` + `REALITY_CHECK_VLM_BASE_URL` (+ model), or `OPENAI_API_KEY` alone for OpenAI.
- Verified 2026-11-07 on the Everest stills: it flagged the rope not threaded through the carabiner (critical), the flagpole on the summit (critical), a second climber (critical) and a bird's-eye that came back oblique (major); it passed the clean takes. It also raises minor physics notes (a flag too taut) that you can ignore.
- **Without any key** the tool writes `agent_pass.md` next to the frames and adds a `major` "agent pass pending" finding. Then do the pass yourself: open every listed frame at full size, trace every rope / strap / tool end to end, check props and cast, append findings to `report.json` with `"source": "agent"`, and set the verdict. Muse's own "checked, matches" note is not a review.

## Acting on the verdict

- **REJECT** -> regenerate. Fix the prompt first (pin the invariant that broke: "mask stays at his neck", "same face as the first frame", "no pole"). Mechanism shots get two takes, then a redesign.
- **REVIEW** -> open the frames named in the findings at full size and decide; record the decision in the asset's `generation_summary`.
- **PASS** -> still look at the 1 fps sheet once; the tool does not see everything (it passed a clip where the camera "static" request became a slow drift that was acceptable only because the first 3 s were used).

Record the counts (viewed / failed / regenerated / redesigned) in the assets checkpoint; the reviewer blocks the gate without them.

## Audio: the `audio_check` tool

Same gate, same verdicts, for sound. `tools/analysis/audio_check.py` (registry `audio_check`). Research basis: round-trip ASR + WER is the standard TTS validation (NVIDIA Riva docs, 2026 TTS papers); loudness per ITU-R BS.1770 / EBU R128 via ffmpeg `ebur128`; YouTube ~-14 LUFS / -1 dBTP; mixing guides put music 10-20 dB under speech. True emotion recognition (emotion2vec/funasr) is not installed, so the emotion check is an explicit **prosody proxy** (pitch range in semitones, energy variance, pauses) compared with the cue's energy word; treat its findings as "listen to this one".

| Mode | When | Input | Fails when |
|---|---|---|---|
| `lines` | every TTS/dialogue line, before the edit | directory of `<section_id>*.mp3/wav` + `script.json` (+ `names` the ASR misspells) | WER >= 0.35 critical / 0.15 major; last script word not heard (truncation, critical); >= 2 inserted words (hallucination); clipping; abrupt end; pace outside the cue's wpm band (lines >= 6 words); flat pitch on a panic/urgent cue; line longer than its slot |
| `music` | every generated cue, before compose | the cue + `music_plan {required_seconds, silence_windows, builds, fade_out_seconds}` | shorter than required (critical); no fade-out; a planned silence window louder than -35 dBFS; a 'build' not louder than what precedes it |
| `mix` | the final render, before publish | final mp4 + `script.json` + `platform` | LUFS more than 3 off the target; true peak over the ceiling; clipping; sub-300 ms dropouts; a line re-transcribed from the mix with WER >= 0.15; line hard to hear AND the bed drops < 3 dB under it (ducking); a quiet drop alone is a minor note |

Name forgiveness: pass `names: ["Shakil"]` (or put them in the script's `pronunciation_guides`); "Shakil"→"Shaquille" and "base camp"→"Basecamp" are then not errors.

Example (Everest v2, 2026-11-07): `lines` passed all six takes but flagged the last line at 228 wpm against a "slow" cue; `music` flagged that the "silence" section of the ElevenLabs cue was not silent (fixed by automation in the composition); `mix` found two lines sitting 0 dB over the music (not ducked) — the composition was fixed and re-rendered.

## Known limits

- Thresholds were tuned on one project (Everest v2, orange suit, frosted beard). Expect to adjust `FACE_SIM_MIN` for very different lighting and `COLOUR_JUMP` for scenes whose dominant saturated colour is not the wardrobe.
- Pose does not fire on tiny figures (extreme wides) or on objects; those shots rely on the VLM/agent pass.
- Audio emotion is a prosody proxy, not a classifier; pace needs >= 6 words to mean anything; Whisper `base.en` mishears names (pass `names`).
- No physics model: foot-ground contact, rope tension and gravity are judged only by the VLM/agent pass.

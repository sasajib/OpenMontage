---
name: lemo-opuscar-film-build
description: Use when building a lemo-opuscar cartoon film or reel.
category: video-production
---

# Build lemo-opuscar films: keep native fps, gate every stage, grep before sign-off

- **Deliver a single mastered 24 fps film through `encode`, not `compose`.** `video_compose` `compose` hard-codes `fps=30` for every segment. Use `operation: "encode"` with `codec: "libx264"`, `crf: 18`, `preset: "slow"`, and record the swap in the render report. `encode` skips the proposal-vs-edit ffmpeg comparison, so check the ffmpeg versions by hand.
- **Captions already burned into the pages:** set `subtitles.enabled: false`. `edit_decisions.subtitles.style` must be a dict even though the schema says string.
- **Size cards with readcheck before writing the score.** A 3-line card needs about 4.5 s; a 2-line card fits a 2-bar hold. Add bars to the back half first, because moving bars after scoring means rescoring.
- **Titles on screen need reading time.** readcheck wants a title on screen for at least `chars/15 + 1.5` s. Check every title against that before fixing the cut length.
- **Score gates must be non-empty intervals.** An offset past a beat (for example `BEAT*1.45`) crashes the self-check. Pad foley clips to one length before mixing.
- **Drawing foley sits well under narration.** The pen scratch in `mix.py` was too loud at gain 0.11 (user: "we should reduce the volume of the dwaring ish... sound"). Gain 0.045 (about 8 dB lower, roughly 17 dB under the voice) was accepted. Set the foley level by ear on the first mix, not after delivery.
- **Audio-only fixes do not need a re-render.** Edit the mix knob, re-run the mixer, re-mux onto the existing video frames, then re-run the final compose so `renders/final.mp4` and `exports/` match. Log the level change in the decision log and the compose checkpoint.
- **Gags in wide shots die.** Add a push-in to dam and parliament style wides.
- **Fonts are not shipped with the demo.** Download the display faces into the project fonts folder before rendering.
- **Disk:** a full render writes JPEG frames to temp. Check `df -h /` first. Render time was about 2–3 min with 3 workers.
- **Check the final mix against the script before sign-off.** Transcribe `renders/review/final_audio.wav` with faster-whisper `base.en` (the lemo-opuscar venv has it). Normalise numbers and spellings (`fifteen`→`15`, `6,000`→`six thousand`, `center`→`centre`), then run `difflib.SequenceMatcher` against the section text in `artifacts/script.json`. Report the ratio and every replace. A ratio near 0.99 whose only differences are inflection or number form passed on this film.
- **Sign-off grep before delivery:** grep the film source (excluding `out/`) for branding leaks such as `lemo ?lab` and tool or model names, after deleting any reference copies of demo code. Only intended credit lines may remain.
- **After the user approves the script gate with "go autonomous":** run the remaining stages through publish without asking again. Report only the deliverable path, specs, cost, and checks.

Full script order, costs, and the stage list: see [references/film-build-detail.md](references/film-build-detail.md).

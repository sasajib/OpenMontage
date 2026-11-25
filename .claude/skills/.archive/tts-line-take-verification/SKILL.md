---
name: tts-line-take-verification
description: Use when Deepgram or TTS narration lines need re-takes.
category: video-production
---

# Verify every narration line by transcribing the whole line, and re-take the ones that fail

- **Never trust a single take.** TTS output is non-deterministic. Generate up to 4 takes per line and keep the first take whose full transcript matches the script, not only its first words. A take that kept its opening but dropped the final clause passes a first-3-words check, so check the whole line.
- **Transcribe with Whisper (medium.en)** from an environment that has it. Compare word-by-word against the script line and count dropped or added words.
- **Reword failing openings instead of re-rolling forever.** Line-initial words are the usual failures: "Round one" came out as "Wrong one", "And the winner" as "In the winter". Use fuller openings ("Round number one", "Your winner", "In the red corner") and avoid words that come out as other words (for example "gunners" → "gutters").
- **Normalise ASR output before calling a take bad.** Whisper writes spoken numbers as digits (`fifteen`→`15`) and may hear a clean word as a near-miss (`calms`→`quiets`). Map number words and numerals like `6,000` to one form before comparing, and set a per-line ASR override for a word the engine reliably mishears. Do not re-roll a take that is faithful once normalised.
- **Pick pace by voice.** Target about 150 wpm. A voice reading at 117 wpm ran too slow for the cut.
- **Re-run the whole-mix check at the end.** After mixing, transcribe the finished audio again and confirm every line.
- **Run `audio_check` `lines` mode on every take, not only the WER pass.** It also checks words-per-minute against the cue's energy band (e.g. "slow" 0-135 wpm), line length against its slot, and abrupt endings. A line can pass WER and still fail pace: a 228 wpm "slow" line passed the transcript check.
- **Slow a line by voice settings plus punctuation, then re-check.** Lower the voice `speed` (0.7 worked) and add ellipses or full stops inside the line. Confirm the new wpm and duration before using it; widen the slot if the line runs past it.
- **Ducking is a mix problem, not a take problem.** Narration sitting 0 dB over the music bed needs per-line music and wind gain drops in the composition (about -10 to -20 dB under speech), then a re-render and `audio_check mix`. Keep the unducked render as a `_v1` file for comparison.

The per-line take loop lives in the project's voice_loop script; run it instead of retyping the retry logic.

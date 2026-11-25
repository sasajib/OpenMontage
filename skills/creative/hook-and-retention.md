# Hook and Retention — Make It Hard to Scroll Away

## When to Use

Every pipeline that writes a script or beat map, at three points:

1. **`script`** — write hook variants, pick one, draw the retention map, lint the lines.
2. **`scene_plan` / `edit`** — check that the picture keeps changing and hits land on the word.
3. **`compose`** — measure the rendered file against the same numbers.

`short-form.md` and `storytelling.md` say *what* a hook is. This skill is the **gate**: numbers a draft either meets or fails. A draft that fails is revised before the human sees it.

Rules are tagged **[short]** (under 90 s, vertical or social), **[long]** (explainer, documentary) or **[all]**. Story and comedy shorts keep metaphor and punchlines; the banned-pattern list in Step 4 applies to explainers and ads only.

## Prerequisites

| Resource | Path | Purpose |
|---|---|---|
| Hook types, arcs | `skills/creative/storytelling.md`, `skills/creative/short-form.md` | Vocabulary this skill enforces |
| Research brief | `projects/<id>/artifacts/research_brief.json` | The surprising fact the hook is built from |
| Word timings | `transcriber` / RunPod Whisper output | Measure voice start, dead air, hits |
| **Gate tool** | `retention_check` (`tools/analysis/retention_check.py`) | `mode: "script"` lints the script and checks `promise` + `retention_map`; `mode: "render"` measures the opening, still stretches, shot-length contrast, whole-frame replaces, voice start and dead air |
| Pacing check | `tools/analysis/audio_check.py`, `lib/slideshow_risk.py` | Existing measurements to reuse |
| Camera | `skills/creative/camera-direction.md`, `skills/creative/virtual-camera.md` | The moves that count as a visual change |

## Process

### Step 0: The concept is a visible event, not a theme

At `idea` / `proposal`, concepts must differ in their **central picture idea**, not be the same cards with three different stories. Useful shapes: one element that transforms throughout; one camera move through scale; a chain reaction; a before/after split. Each concept comes with its hook frame.

Write what happens on screen, not what it means: "letters are posted one by one and stack into the title" beats "show the power of communication".

### Step 1: Write five hooks, score them, keep one

Never ship the first hook. Write **five**, each a different type:

| Type | Shape |
|---|---|
| Result first | Show the ending, then earn it |
| Open question | A question the viewer cannot answer but wants to |
| Contradiction | "X is true" over a picture that says otherwise |
| Stakes | What is lost or won, with a number or a name |
| Cold open | The most vivid moment, out of order, no context |

Each hook is three things together: **the first spoken line, the frame-0 picture, the on-screen title** (2–6 words, two lines at most).

Score each 0–2 on five questions. Keep the best; it must reach **8/10**, or write five more.

| Question | 0 | 2 |
|---|---|---|
| Stop | Could open any video | Only this video could open this way |
| Gap | Tells the answer | Opens one specific question the viewer wants closed |
| Speed | Needs setup first | Understood in under 2 s, muted |
| Picture | Background or title card | A subject already doing something |
| Promise | Unrelated to the payoff | The payoff answers it exactly |

Record the five, the scores and the pick in `decision_log` (`category: "concept_selection"`, `subject: "Hook"` — the schema has no hook category). Show the top two to the user at the script gate.

### Step 2: Hook rules (hard)

- **[all]** First spoken word starts by **0.5 s**. No greeting, no setup, no logo.
- **[all]** Something is on screen and **moving by 0.3 s**. Frame 0 is never empty and never mid-fade.
- **[short]** Frame 0 works as the cover image: subject and title are already there, not drawing in.
- **[all]** The first line names the stakes or the question.
- **[all]** One promise per video. Write it as one sentence in script metadata (`promise`).

### Step 3: Draw the retention map

Put timestamps on these beats in script metadata (`retention_map`). Missing beats fail the gate.

**[short] 30 s** (scale by ratio for 15–60 s):

| Beat | Time | Job |
|---|---|---|
| Hook | 0–2 s | Stop the scroll |
| Promise | 2–5 s | What the viewer gets for staying |
| First payoff | by 3–5 s | The first real piece of content lands |
| Body | 5–25 s | 3–5 beats, each raises the question or pays part of it |
| Second hook | ~50% | A fresh reason to stay ("here is the part nobody mentions") |
| Hero moment | one, timestamped | The best picture and sound in the video |
| Payoff | 25–28 s | The promise answered; the clearest frame of the video |
| End | 28–30 s | **Either** hold the last message still 1.5–2.5 s, **or** end on a frame that leads into frame 0 (loop). Choose one. |

**[long]** documentary / explainer:

| Beat | Shape |
|---|---|
| Cold open | 2–5 lines, the most vivid moment, out of order |
| Bridge | One line: "to see why, go back to…" |
| Sections | 3–6 lines each; the last line hands a question to the next section |
| Re-hook | Every 45–60 s: a new question, a reversal, or a number |
| Turn | Short lines; one beat of stillness before it |
| Close | 2 lines that pay off the cold open |

**Open loops [all]:** list every question the script opens and the timestamp where it closes. Always keep at least one open until the payoff. A question that never closes is a defect; so is a stretch with none open.

**Callback [all]:** plant one object or phrase in the hook, use it again in the middle, pay it off at the end.

**Beat density:** 5–7 beats for 20 s, 12–20 for 60 s. Each beat states: what changes, who wants what, the line or image that lands it.

### Step 4: Lint every line

| Rule | Limit |
|---|---|
| Sentence length | [short] 6–14 words; [long] 8–18; never over 22 |
| One hero per line | Each line has exactly one thing on screen to look at |
| Every line changes the picture | A line with no picture change is cut or merged |
| Key word last | Put the word the picture hits on at the end of the line, before the pause |
| No echo | Never show a phrase on screen and speak it word for word |
| Spoken numbers | Written as words in narration ("forty thousand") |
| Each line adds a fact or a turn | Delete lines that only announce ("let's look at…") |
| Banned (explainer, ad) | "Let's dive in", "stay tuned", "in this video", "not X, but Y" twists, colon reveals, three short sentences in a row, filler: just, simply, really, actually |
| Lists | Read aloud only if each item appears on screen as it is said |

Word budget: 60 s ≈ 150 words, 12–15 lines.

### Step 5: Pacing numbers (scene_plan and edit)

- **[short]** No stretch over **2 s** without a visual change. **[long]** 3 s.
- A visual change is: a new element, a new scene, a clip, a flash, a camera punch or a new camera move. A drifting background does **not** count.
- Camera punches at least 1.5 s apart.
- A picture hit lands **on the spoken word**, not at the start of the line. Start a move its own length before the word.
- On-screen text holds at least `(words / 3) + 0.5` s.
- Before a punchline or a turn: 0.3–0.6 s pause. After it: hold the reaction 0.5 s. This is the only dead air allowed.
- A line ends at least 0.5 s before the cut.
- A voice line fills its slot: on a 5 s clip, 4.0–5.0 s of speech. Measure it; TTS length varies.

**Rhythm — contrast, not a metronome:**

- Shot lengths vary at least 4× across the video (a 0.3 s shot near a 2 s shot). Even spacing reads as a slideshow however fast it is.
- Plan one **quiet beat** of 0.6–1.5 s right before the hero moment: the voice stops, the camera stops pushing, and the shot simply holds on something that is still alive (a flame flickering, smoke drifting, a hand waiting). Mark it in the `retention_map`.
- **Never freeze a frame of live footage, and never cut the music to near silence for the beat.** A held frame with the sound dropped reads as the video stalling or the editor slipping, not as stillness. This was tried on two Lit Within episodes (2026-11-17) and the user called it novice editing. In code-rendered scenes a still is fine only when the scene was never moving footage (a designed card), and even then keep a micro-motion or a continuing sound bed.
- A burst is three or more big changes inside 1.5 s, at uneven intervals. Use one or two per video.
- Never end two shots the same way in a row.

**Carry — every beat grows out of the one before:**

- For each boundary between beats, name the element that **survives and moves** into the next beat (the button pressed becomes the result; the camera pushes into a card until the card is the scene; the cast folds into the logo). Add a `carries` note per scene in the scene plan.
- A fade between unrelated scenes is a slide change. Aim for a carry on at least 7 of 10 boundaries; under half is a fail. Hard-cut bursts and declared cuts are exempt.
- The cause is visible: something on screen makes the next thing happen. A page reacting to nothing reads as a screensaver.

**The idle test:** once subject, text and background have arrived, what is the remaining time doing? If the answer is "a slow push" or "waiting", cut the time — do not add decoration. No confetti or particle bursts as filler; they read as a template.

### Step 6: Sound keeps people watching

- A quiet bed under everything beats silence. One continuous bed across scenes; a fade at every join sounds like a slideshow.
- Accents on beat starts. Sound cue = contact frame − 0.03 s.
- Riser ~1.2 s that ends exactly on the first word of a new section.
- The big hit (boom, drop) once or twice per video: on the title or the hero moment.
- Move the music so its own breaks fall on section starts.
- SFX are ducked under voice, so put a sound that matters in a pause.
- If you can follow the melody under the voice, the music is too loud.
- Fewer sound events than beats. Two sounds within 40 ms: keep one.
- The landing is louder than the move into it. Thin the mix a little just before (drop one layer, not the whole bed); a hard dip to silence sounds like a dropout.

### Step 7: Gate

**At `script`** — run `retention_check` with `mode: "script"` (`format: "short"` or `"long"`; `explainer_lint: false` for story and comedy). A `REJECT` verdict blocks the gate. Then confirm all of these before the human gate:

- [ ] Five hooks written and scored; pick ≥ 8/10; logged
- [ ] Hook rules in Step 2 met on paper
- [ ] `promise` written; payoff answers it
- [ ] `retention_map` complete with timestamps, one hero moment, second hook, ending type
- [ ] Open-loop list: each opens and closes; one stays open to the payoff
- [ ] Line lint clean

**At `compose`** — run `retention_check` with `mode: "render"`, passing `words_path` (word timings) and `planned_stills` (pauses in the voice you intend; it never excuses a frozen picture). Fix every critical finding and every `frozen_frame` finding, then write the numbers into the review. The tool cannot see a drifting background as a still, or judge whether a hook is interesting — the table and the cold watch below still apply.

| Check | How | Pass |
|---|---|---|
| Voice start | First word timestamp | ≤ 0.5 s |
| Motion start | Frames at 0.0 and 0.3 s differ | yes |
| Cover | Frame 0 shows subject + title | yes |
| Longest still stretch | Contact sheet at 2 fps, or scene-change detect | ≤ 2 s [short] / 3 s [long] |
| Hits on words | Compare cue times to word timings | within ±0.1 s |
| Dead air | Gaps in word timings | none over 0.6 s outside planned pauses |
| Hero moment | Watch it at full speed with sound | it is the best 3 s |

Then the **cold watch**: play it once at full speed with sound and answer with timestamps — Where is the hook, and is it in by 2 s? Where is the hero moment? Which frame could belong to any other video? Which are the weakest five seconds? Fix at most three things, re-render, re-measure. Stop after three rounds and report what still fails. Never claim a check you did not run.

## Common Pitfalls

- **One hook, never compared.** The first idea is the average one.
- **Hook and payoff from different videos.** The hook promises a mystery; the ending gives a summary.
- **Explaining before intriguing.** Context belongs after the hook, in the promise beat.
- **Motion that is only drift.** A slow zoom on one image for 5 s is a still.
- **Hits on the line start.** The picture arrives before the word and the moment is wasted.
- **Silence between lines.** TTS pads; trim it. The user has flagged long pauses before.
- **Every beat at the same energy.** One hero moment; let the rest be quieter so it reads.
- **Ending by fading out.** Hold or loop. Choose.
- **Fast but even.** A change every second at the same interval is still a metronome. Vary shot length and put a quiet beat before the hit.
- **A freeze frame as the pause.** The picture must keep living through the quiet beat. `retention_check` reports any frozen stretch of 0.45 s or more as `frozen_frame`.
- **Scenes that replace each other.** If nothing carries across the boundary, it is a slide deck.

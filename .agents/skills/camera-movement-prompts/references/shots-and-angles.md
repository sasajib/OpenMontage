# Shot Sizes and Camera Angles — Prompt Reference

Source: [animationguides.com — The Ultimate Guide to Camera Angles & Shots](https://www.animationguides.com/guide-camera-angles-shots-ai/) (copied 2026-11-07). Example prompts are verbatim; definitions are condensed.

Two separate choices that combine freely:

- **Shot size** = how much of the subject is visible (distance).
- **Camera angle** = where the camera sits and how it looks at the subject (perspective).

These describe the **frame**, so they belong in the **still / first-frame prompt** (or the opening of a text-to-video prompt). Camera **movement** is a third choice — see `../SKILL.md`.

## Shot sizes

| Shot | What is in frame | Effect | Example prompt |
|---|---|---|---|
| Extreme wide shot (EWS) / establishing | Environment dominates; subject tiny or absent | Scale, isolation, grandeur; sets location | A cinematic extreme wide shot of a lone traveler crossing a desert under a burning orange sunset, vast landscape, epic scale |
| Wide shot (WS) / long shot | Subject head to toe, environment visible | Action, body language, subject in its space | Wide shot of a ballerina on stage, full body visible, theater lights glowing in the dark hall |
| Medium shot (MS) | Waist up | Neutral default for dialogue; gestures plus some background | Medium shot of a detective sitting at a desk in a dimly lit office, cigarette smoke curling in the air |
| Medium close-up (MCU) | Chest or shoulders up | Personal but not intense; presenter and dialogue | Medium close-up of a scientist explaining data on a futuristic holographic screen |
| Close-up (CU) | Face, or one object | Emotion, reaction, a key object | Close-up of a young woman's face with tears reflecting neon city lights at night |
| Extreme close-up (ECU) | One tiny detail (eye, hand, object) | Intensity, symbolism, suspense | Extreme close-up of an old man's wrinkled hand holding a golden key in the dark |
| Two-shot | Two characters together | Relationship or conflict in one frame | Two-shot of a young wizard and apprentice standing in a mystical forest, cinematic lighting, fantasy atmosphere |
| Over-the-shoulder (OTS) | Past one character's shoulder at another | Puts the viewer inside a conversation or confrontation | Over-the-shoulder shot of a detective facing a mysterious figure in a dark alley, moody cinematic lighting |
| Point of view (POV) | Exactly what the character sees | Immersion, suspense | POV shot of a child looking through a keyhole into a magical, glowing room, soft lighting |
| Insert / cut-in | Close view of an object or detail in the scene | Tells story without dialogue; "notice this" | Insert shot of a glowing ancient scroll on a wooden table, cinematic shadows |

The source also lists four "shots" that are really movements. Use the movement library for exact wording:

| Source name | Example prompt | Movement library ID |
|---|---|---|
| Tracking / dolly shot | Tracking shot of a soccer player dribbling the ball across a stadium field, crowd cheering in the blurred background, dramatic stadium lights, cinematic realism with dynamic motion blur. | 16, 19 |
| Crane / high-overhead shot | Crane shot over a medieval battlefield, armies clashing, cinematic epic lighting | 25, 25B |
| Tracking extreme close-up | Extreme close-up tracking a dripping candle flame in a dark, haunted room, dramatic shadows | ECU still + 16 |
| Tilt / whip pan / swish pan | Swish pan shot of a skateboarder jumping over urban obstacles, motion blur, dynamic angle | 03, 03B, 04 |

## Camera angles

| Angle | Camera position | Effect | Example prompt |
|---|---|---|---|
| Eye-level | At the subject's eye height | Natural, neutral, equal; keeps focus on performance | Eye-level shot of a teacher talking to students in a bright classroom, cinematic lighting |
| High angle | Above, looking down | Subject small, weak, vulnerable, or watched | High-angle shot of a child standing alone in a huge empty stadium, dramatic lighting |
| Low angle | Below, looking up | Subject powerful, heroic, intimidating | Low-angle shot of a futuristic skyscraper towering into the sky, cinematic epic scale |
| Bird's-eye view (top-down) | Directly above, straight down | Scale, geography, pattern; people look insignificant | Bird's-eye view of a busy marketplace in Marrakech, colorful stalls and crowds |
| Worm's-eye view | On the ground, straight up | Exaggerated height; subject overwhelming | Worm's-eye view of a knight standing on castle walls against the sunset |
| Dutch angle (tilted) | Camera rolled so the horizon slants | Chaos, tension, instability, dream | Dutch angle shot of a detective entering a neon-lit alley, noir style |
| Overhead / God's eye | Directly above, framed as a "divine" view | Fragility, fate, detachment | God's-eye angle of a man lying in the snow, surrounded by glowing candles |
| Over-the-shoulder | Behind one character's shoulder | Intimacy; tension in confrontations | Over-the-shoulder shot of a knight facing a dragon in a smoky cave |
| Over-the-hip | Low behind the hip, often weapon visible | Standoff, anticipation | Over-the-hip shot of a cowboy ready to draw his revolver at sunset |
| Shoulder-level | At shoulder height | Subtle variation on eye-level; gestures, closeness | Shoulder-level shot of two friends laughing together at a café table |
| Knee-level | At knee height, looking up | Walking, footwear, children, small animals; entrances | Knee-level shot of boots walking down a dusty western street |
| Over-the-back | Close behind the subject's back | "Following along"; third-person game feel | Over-the-back shot of a soldier walking into a foggy battlefield |
| Shoulder peek / spying | Peeking from behind a wall, door or curtain | Voyeurism, secrecy | Shoulder peek shot from behind curtains, watching a stranger outside in the rain |
| Behind-the-object | Framed through plants, furniture, fences | Depth and layering; hidden observer | Shot framed behind bookshelves, watching a spy exchanging documents |
| Over-the-weapon | Weapon in foreground, target in distance | Intensity before action | Over-the-weapon shot of a sniper aiming through scope at city skyline |
| Extreme tilt | Very strong Dutch angle, near 90° | Breakdown, surreal, horror | Extreme tilted shot of a carnival at night, eerie atmosphere, distorted perspective |
| Tracking side angle | Beside the subject, moving parallel | Speed and energy without cutting | Tracking side shot of a runner sprinting through neon-lit cyberpunk streets |

## Combining: shot size + angle = mood

| Combination | Effect |
|---|---|
| Close-up + high angle | Fragility, fear, doubt |
| Close-up + low angle | Intimidation or admiration (villains, heroes) |
| Medium shot + Dutch angle | An ordinary scene feels unsettling |
| Wide shot + bird's-eye | Scale and geography (crowds, dance, cities) |
| Extreme wide + worm's-eye | Landscapes, buildings, giants feel overwhelming |

Pairings that do not work well:

- **Over-the-shoulder** needs medium or close framing — in a wide shot the shoulder is barely visible.
- **Over-the-hip / over-the-weapon** need mid-range framing to show body and action.
- **God's eye / overhead** needs wide framing to show layout; weak on close-ups unless stylised.

## Still prompt formula

```
[Shot type] of [subject] from [camera angle], [action / expression], in [environment / context], with [lighting], [color palette], [emotional tone], in [style].
```

Example: *A medium close-up of a young man from a low angle, nervously adjusting his tie, inside a crowded courtroom, under harsh fluorescent lighting, with muted gray and brown tones, tense atmosphere, in cinematic realism style.*

Option words for the other slots:

| Slot | Options |
|---|---|
| Time of day | dawn, morning, afternoon, golden hour, twilight, night, midnight |
| Weather | sunny, rainy, foggy, snowy, stormy, windy |
| Lighting — natural | soft daylight, harsh midday sun, cloudy diffuse light, golden sunset, moonlight, candlelight |
| Lighting — dramatic | chiaroscuro, spotlight, rim light, underlighting, silhouette, high contrast |
| Lighting — cinematic | neon glow, studio softbox, tungsten warm light, fluorescent cold light, car headlights, firelight, projector beam |
| Lighting — effects | strobe, laser, holographic glow, flickering TV light, lightning flashes |
| Color — warm | golden, red-orange, earthy tones, sepia |
| Color — cool | blue-gray, teal, icy silver, pale green |
| Color — neutral | black and white, muted gray, beige, pastel |
| Color — vibrant | neon, saturated rainbow, cyberpunk palette, high-contrast comic style |
| Color — thematic | noir (black/white, heavy shadows), retro (muted yellows, greens, browns), futuristic (metallic silver, neon blue and pink), fantasy (jewel tones, glowing accents) |
| Character emotion | cheerful, playful, melancholic, nostalgic, calm, focused, furious, defiant, anxious, shocked, mysterious, hopeful, triumphant |
| Scene atmosphere | peaceful, romantic, tense, chaotic, exciting, surreal, whimsical, gritty, epic, intimate |

Style words come from the project's playbook, not from a list here.

---
name: browser-media-generation
description: Use when generating Gemini images/video via BrowserOS.
category: video-production
---

# Browser media generation (BrowserOS)

Drive the signed-in Gemini app (or ChatGPT) with BrowserOS to make images and video that the user's paid subscription covers. Treat the result as a provided asset, never as an API call.

- **Video needs its own chat.** A plain prompt in the normal chat fails with "Something went wrong". Open "Upload & tools" and choose "Create video". This starts a new chat with a "Deselect Videos" chip.
- **Set the aspect ratio before sending.** The default is "Aspect ratio, Landscape (16:9)". Change it first, or the clip comes out 16:9 even when 9:16 was asked for.
- **Keep video prompts short, then check the text box.** The composer once dropped the first sentence of a long prompt, and the clip ran a different length than planned.
- **Wait for the result.** Video appeared after about 90 s. Poll with `wait` or a snapshot, not a fixed sleep.
- **A download timeout is not a failure.** The `download` tool may return "The operation timed out" while the file still lands. Check `~/.browseros/tool-output/download-*/` for the new `.mp4` or image before retrying. See [references/gemini-clickpath.md](references/gemini-clickpath.md) for refs and probe commands.
- **Verify the file before use.** Run `ffprobe` for duration, size, and audio, then extract a few frames to confirm the content matches the brief.
- **Send with the Enter key, not a click.** After the text box is filled, `act` with kind=press Enter sends reliably. Clicking "Send message" by ref from a `run` script, or pressing Enter inside `run`, did not send.
- **Veo has a daily allowance, about two clips per day on a Pro account.** After the limit the composer shows "You're out of videos for now" and is disabled. Plan at most two Veo clips per day. Image generation kept working (6+ in one day). When the allowance is gone, use a generated still with code-driven motion (slow pan or zoom) and say so in the handoff.
- **Generate in the final aspect ratio.** Cropping a 16:9 clip to 9:16 upscales it from 720p and looks soft beside native stills. Choose portrait before sending.
- **A video download can land as an empty `download-*` folder.** Re-open the chat and download again.
- **Images are fast and effectively unlimited.** Fill the Gemini prompt box, send with `act` kind=press Enter, then poll until a "Download full size image" button appears. A 9:16 request downloaded as 1536x2752. Several images can share one chat; take the last download button. An "I encountered an error" reply is transient: resend the prompt.
- **Log it.** Record the source as `provided (<service> via BrowserOS)` and state that no API cost was incurred. Flag the terms-of-service question once, and proceed only if the user confirms.

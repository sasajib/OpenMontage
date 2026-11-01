# Gemini app click-path (observed 2026-10-31)

- Image: plain prompt "Create an image..." in a new chat. Result offers a "Download full size image" button. Observed output 1536x2752 for a 9:16 request, in about 5 s.
- Video: "Upload & tools" -> "Create video". Composer shows "Deselect Videos" and "Aspect ratio, Landscape (16:9)". Result shows a "Download video" button and the page reads "Your video is ready". Observed output 1280x720, H.264 with AAC audio, 10.03 s, in about 90 s.
- Ready check: a `run` call reading `document.querySelectorAll('video')` returns `currentSrc` and `duration` once the clip exists.
- Download: `download` with the page and the ref of the download button. Expect a timeout message. Then run `ls -lat ~/.browseros/tool-output/` and find the new file.
- Verify: `ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height -of csv=p=0 <file>`, then `ffmpeg -ss <t> -i <file> -frames:v 1 <frame>.jpg` at a few points.
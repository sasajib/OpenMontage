  vf_parts: list[str] = [*geom, "setsar=1", "fps=30"]
# compose normalises every segment to 30 fps (fps=30 in _compose); this film is one mastered 24 fps cut, so the ffmpeg runtime is used through the encode operation, which keeps the native frame rate (crf 18)
r = vc.execute({"operation": "encode", "input_path": str(P / "opuscar/main-event/main-event.mp4"), "output_path": str(out), "codec": "libx264", "crf": 18, "preset": "slow"})
... compose True None {"operation": "encode", "codec": "libx264", "crf": 18, "profile": null, ...}
{'duration': 81.667, 'w': 1920, 'h': 1080, 'fps': 24.0, 'vcodec': 'h264', 'acodec': 'aac', 'size': 58493181}
CREDITS:11:No LemoLab credit; no watermark.
grep done
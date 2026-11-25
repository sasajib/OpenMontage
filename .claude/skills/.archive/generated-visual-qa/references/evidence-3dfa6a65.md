  # Sample at 10%, 35%, 65%, 90% of duration, plus one frame
                # shortly after every detected cut so short shots are never
                # skipped (a 0.8 s shot with a broken face passed a 4-frame
                # review once; see skills/pipelines/animation/asset-director.md).
...
11 [2.0, 4.2, 7.28, 8.64, 9.44, 12.32, 15.28, 17.84, 19.84, 23.36, 26.28]
...
Rule: **no generated still or clip may feed a video job (image-to-video,
lip-sync, upscale) or be registered in `asset_manifest` until it has been
viewed at full resolution.** A downscaled contact sheet does not count; a
0.8 s eye shot with the door plank drawn across the face passed a contact-sheet
review once and shipped.
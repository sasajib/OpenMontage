---
name: remotion-render-troubleshooting
description: Use when Remotion renders crash or need concurrency tuning.
category: video-production
---

# Remotion render troubleshooting

Check the machine before choosing render settings. Run `nproc` and set `concurrency` to at most the core count. A render that fails in under a second with 8 workers on a 4-core machine is a concurrency error, not a composition error. Drop to `nproc` and rerun.

- Run the render script from the repo root, or set `PYTHONPATH` to the repo root. Otherwise the `tools` package fails to import.
- Run renders in the background and poll the output file. Do not start a dependent checkpoint or export until the output file exists.
- If a long compose render dies, lower concurrency before retrying.

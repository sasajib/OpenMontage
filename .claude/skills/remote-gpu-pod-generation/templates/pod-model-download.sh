#!/bin/sh
# Detached, resumable model downloader for a GPU pod.
# Usage (on the pod): nohup setsid /workspace/pod-model-download.sh /workspace/ComfyUI/models > /workspace/dl.log 2>&1 < /dev/null &
# Edit the get lines to match the model stack named in the repo's model metadata. Safe to re-run.
M="${1:?models dir required}"
get() {
  d="$1"; u="$2"; f=$(basename "$u"); mkdir -p "$M/$d"
  [ -s "$M/$d/$f" ] && { echo "skip $f"; return; }
  echo "start $f"
  wget -q -c -O "$M/$d/$f.part" "$u" && mv "$M/$d/$f.part" "$M/$d/$f" && echo "done $f $(du -h "$M/$d/$f" | cut -f1)" || echo "FAIL $f"
}
get text_encoders "https://huggingface.co/<org>/<repo>/resolve/main/split_files/text_encoders/<file>.safetensors"
get diffusion_models "https://huggingface.co/<org>/<repo>/resolve/main/split_files/diffusion_models/<file>.safetensors"
echo ALL_DONE

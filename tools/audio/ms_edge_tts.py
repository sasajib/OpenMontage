"""Microsoft Edge (Read Aloud) text-to-speech provider tool.

Free, keyless neural TTS via the ``edge-tts`` package, which talks to the
same voices as Azure AI Speech through the Edge browser's Read Aloud
endpoint. No account or API key is needed — only ``pip install edge-tts``
and network access.

Caveat: this is an unofficial client. Microsoft occasionally changes the
endpoint's token scheme, which breaks the package until it is updated
(``pip install -U edge-tts``). Good for personal and draft work; for client
deliverables prefer a provider with an official API.

Docs: https://github.com/rany2/edge-tts
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

_PERCENT_RE = re.compile(r"^[+-]\d+%$")
_HZ_RE = re.compile(r"^[+-]\d+Hz$")


class EdgeTTS(BaseTool):
    name = "edge_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "edge"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = ["python:edge_tts"]
    install_instructions = (
        "Install the edge-tts package (no API key needed):\n"
        "  pip install edge-tts\n"
        "List voices with:  edge-tts --list-voices"
    )
    fallback = "piper_tts"
    fallback_tools = ["piper_tts"]
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "prosody_control",
        "word_timestamps",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
    }
    best_for = [
        "free neural narration with no API key",
        "multilingual drafts and personal projects",
        "word-level timing for captions at zero cost",
    ]
    not_good_for = [
        "client deliverables that need an officially supported API",
        "fully offline production (use piper_tts)",
        "voice cloning (use elevenlabs_tts)",
    ]

    # Same neural voices as Azure; short aliases for the common picks.
    RECOMMENDED_VOICES = {
        "andrew": "en-US-AndrewMultilingualNeural",  # warm, confident, conversational
        "brian": "en-US-BrianMultilingualNeural",  # deeper, measured
        "ava": "en-US-AvaMultilingualNeural",  # confident, bright female
        "emma": "en-US-EmmaMultilingualNeural",  # friendly, clear
        "guy": "en-US-GuyNeural",  # authoritative
        "jenny": "en-US-JennyNeural",  # friendly, clear
    }
    DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to convert to speech"},
            "voice": {
                "type": "string",
                "description": (
                    "Edge voice short name (e.g. 'en-US-AndrewMultilingualNeural') "
                    "or an alias: andrew, brian, ava, emma, guy, jenny. "
                    "Run `edge-tts --list-voices` for the full list. "
                    "Default: en-US-AndrewMultilingualNeural."
                ),
            },
            "rate": {
                "type": "string",
                "description": "Speaking rate as a signed percent, e.g. '-10%', '+0%', '+15%'.",
                "default": "+0%",
            },
            "pitch": {
                "type": "string",
                "description": "Pitch shift in Hz, e.g. '-20Hz', '+0Hz', '+10Hz'.",
                "default": "+0Hz",
            },
            "volume": {
                "type": "string",
                "description": "Volume as a signed percent, e.g. '-10%', '+0%'.",
                "default": "+0%",
            },
            "word_timestamps": {
                "type": "boolean",
                "default": False,
                "description": (
                    "Also write <output>.words.json with per-word start/end seconds "
                    "for captions and lip-sync."
                ),
            },
            "output_path": {"type": "string"},
            "output_format": {
                "type": "string",
                "enum": ["mp3", "wav"],
                "default": "mp3",
                "description": "mp3 (native, 24kHz) or wav (converted with ffmpeg).",
            },
        },
    }

    output_schema = {
        "type": "object",
        "properties": {
            "provider": {"type": "string"},
            "voice": {"type": "string"},
            "output": {"type": "string"},
            "format": {"type": "string"},
            "text_length": {"type": "integer"},
            "word_timestamps_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(
        max_retries=2,
        retryable_errors=["ConnectionError", "Timeout", "NoAudioReceived"],
    )
    idempotency_key_fields = ["text", "voice", "rate", "pitch", "volume", "output_format"]
    side_effects = ["writes audio file to output_path", "sends text to Microsoft's Edge TTS endpoint"]
    user_visible_verification = ["Listen to generated audio for natural speech quality"]

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 10.0

    def _resolve_voice(self, inputs: dict[str, Any]) -> str:
        voice = (inputs.get("voice") or "").strip()
        if not voice:
            return self.DEFAULT_VOICE
        return self.RECOMMENDED_VOICES.get(voice.lower(), voice)

    @staticmethod
    def _prosody(inputs: dict[str, Any]) -> dict[str, str]:
        """Normalise rate/pitch/volume to the exact strings edge-tts accepts."""
        rate = str(inputs.get("rate") or "+0%").strip()
        volume = str(inputs.get("volume") or "+0%").strip()
        pitch = str(inputs.get("pitch") or "+0Hz").strip()
        for name, value in (("rate", rate), ("volume", volume)):
            if value in ("0", "0%"):
                value = "+0%"
            elif value[0].isdigit():
                value = "+" + value
            if not _PERCENT_RE.match(value):
                raise ValueError(f"{name} must look like '+10%' or '-5%', got {value!r}")
            if name == "rate":
                rate = value
            else:
                volume = value
        if pitch in ("0", "0%", "0Hz"):
            pitch = "+0Hz"
        elif pitch[0].isdigit():
            pitch = "+" + pitch
        if not _HZ_RE.match(pitch):
            raise ValueError(f"pitch must look like '+10Hz' or '-20Hz', got {pitch!r}")
        return {"rate": rate, "volume": volume, "pitch": pitch}

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        try:
            self.check_dependencies()
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))

        start = time.time()
        try:
            result = self._synthesize(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"TTS generation failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = 0.0
        return result

    def _synthesize(self, inputs: dict[str, Any]) -> ToolResult:
        import edge_tts

        voice = self._resolve_voice(inputs)
        prosody = self._prosody(inputs)
        container = inputs.get("output_format", "mp3")
        ext = "wav" if container == "wav" else "mp3"
        want_words = bool(inputs.get("word_timestamps", False))

        output_path = Path(inputs.get("output_path") or f"tts_output.{ext}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if container == "wav" and shutil.which("ffmpeg") is None:
            return ToolResult(success=False, error="wav output needs ffmpeg on PATH")

        mp3_path = output_path if ext == "mp3" else output_path.with_suffix(".edge.mp3")
        meta_path = output_path.with_suffix(".words.jsonl") if want_words else None

        communicate = edge_tts.Communicate(
            inputs["text"],
            voice,
            boundary="WordBoundary" if want_words else "SentenceBoundary",
            **prosody,
        )
        communicate.save_sync(str(mp3_path), str(meta_path) if meta_path else None)

        if not mp3_path.exists() or mp3_path.stat().st_size == 0:
            return ToolResult(success=False, error="Edge TTS returned no audio")

        if container == "wav":
            proc = subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3_path),
                 "-ar", "48000", "-ac", "1", str(output_path)],
                capture_output=True, text=True, timeout=300,
            )
            mp3_path.unlink(missing_ok=True)
            if proc.returncode != 0:
                return ToolResult(success=False, error=f"ffmpeg conversion failed: {proc.stderr}")

        data: dict[str, Any] = {
            "provider": self.provider,
            "voice": voice,
            "rate": prosody["rate"],
            "pitch": prosody["pitch"],
            "text_length": len(inputs["text"]),
            "output": str(output_path),
            "format": ext,
        }
        artifacts = [str(output_path)]

        if meta_path is not None:
            words_path = self._convert_word_boundaries(meta_path)
            data["word_timestamps_path"] = str(words_path)
            artifacts.append(str(words_path))

        return ToolResult(success=True, data=data, artifacts=artifacts, model=voice)

    @staticmethod
    def _convert_word_boundaries(meta_path: Path) -> Path:
        """Turn edge-tts' 100ns-offset JSONL into a simple words JSON file."""
        words = []
        with meta_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if item.get("type") != "WordBoundary":
                    continue
                start = item["offset"] / 10_000_000
                words.append({
                    "word": item["text"],
                    "start": round(start, 3),
                    "end": round(start + item["duration"] / 10_000_000, 3),
                })
        words_path = meta_path.with_name(meta_path.name.replace(".words.jsonl", ".words.json"))
        words_path.write_text(json.dumps({"words": words}, indent=2), encoding="utf-8")
        meta_path.unlink(missing_ok=True)
        return words_path

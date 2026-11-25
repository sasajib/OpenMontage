"""Focused tests for the Microsoft Edge (edge-tts) TTS tool.

No live network calls: edge_tts.Communicate is monkeypatched. Covers the
tool contract, registry discovery, prosody normalisation, word-timestamp
conversion, and the selector's input adaptation.
"""

import json
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.base_tool import BaseTool, ToolRuntime, ToolTier
from tools.tool_registry import ToolRegistry
from tools.audio.ms_edge_tts import EdgeTTS
from tools.audio.tts_selector import TTSSelector


FAKE_MP3 = b"\xff\xfb\x90\x00" + b"\x00" * 64


class _FakeCommunicate:
    calls: list = []

    def __init__(self, text, voice, **kwargs):
        self.text, self.voice, self.kwargs = text, voice, kwargs
        _FakeCommunicate.calls.append(self)

    def save_sync(self, audio_fname, metadata_fname=None):
        Path(audio_fname).write_bytes(FAKE_MP3)
        if metadata_fname:
            lines = [
                {"type": "WordBoundary", "offset": 1_000_000, "duration": 2_625_000, "text": "Hello"},
                {"type": "WordBoundary", "offset": 3_750_000, "duration": 1_375_000, "text": "there"},
            ]
            Path(metadata_fname).write_text("\n".join(json.dumps(x) for x in lines))


@pytest.fixture
def fake_edge(monkeypatch):
    _FakeCommunicate.calls = []
    fake = types.SimpleNamespace(Communicate=_FakeCommunicate)
    monkeypatch.setitem(sys.modules, "edge_tts", fake)
    return fake


class TestContract:
    def test_identity(self):
        t = EdgeTTS()
        assert issubclass(EdgeTTS, BaseTool)
        assert t.name == "edge_tts"
        assert t.capability == "tts"
        assert t.provider == "edge"
        assert t.runtime == ToolRuntime.API
        assert t.tier == ToolTier.VOICE
        assert t.fallback == "piper_tts"
        assert t.estimate_cost({"text": "x" * 10_000}) == 0.0

    def test_discoverable(self):
        reg = ToolRegistry()
        reg.discover("tools")
        assert reg.get("edge_tts") is not None
        assert "edge_tts" in [t.name for t in reg.get_by_capability("tts")]


class TestProsody:
    def test_defaults(self):
        assert EdgeTTS._prosody({}) == {"rate": "+0%", "volume": "+0%", "pitch": "+0Hz"}

    def test_normalises_unsigned_and_zero(self):
        p = EdgeTTS._prosody({"rate": "0%", "pitch": "10Hz", "volume": "5%"})
        assert p == {"rate": "+0%", "volume": "+5%", "pitch": "+10Hz"}

    def test_rejects_bad_rate(self):
        with pytest.raises(ValueError):
            EdgeTTS._prosody({"rate": "fast"})

    def test_rejects_semitone_pitch(self):
        with pytest.raises(ValueError):
            EdgeTTS._prosody({"pitch": "+2st"})

    def test_voice_alias(self):
        t = EdgeTTS()
        assert t._resolve_voice({"voice": "jenny"}) == "en-US-JennyNeural"
        assert t._resolve_voice({"voice": "de-DE-KatjaNeural"}) == "de-DE-KatjaNeural"
        assert t._resolve_voice({}) == EdgeTTS.DEFAULT_VOICE


class TestExecute:
    def test_mp3_output(self, fake_edge, tmp_path):
        out = tmp_path / "line.mp3"
        res = EdgeTTS().execute({"text": "Hello there", "voice": "ava", "rate": "-5%", "output_path": str(out)})
        assert res.success, res.error
        assert out.read_bytes() == FAKE_MP3
        assert res.data["voice"] == "en-US-AvaMultilingualNeural"
        assert res.cost_usd == 0.0
        call = _FakeCommunicate.calls[-1]
        assert call.kwargs["rate"] == "-5%"
        assert call.kwargs["boundary"] == "SentenceBoundary"

    def test_word_timestamps(self, fake_edge, tmp_path):
        out = tmp_path / "line.mp3"
        res = EdgeTTS().execute({"text": "Hello there", "word_timestamps": True, "output_path": str(out)})
        assert res.success, res.error
        words_path = Path(res.data["word_timestamps_path"])
        assert words_path == tmp_path / "line.words.json"
        words = json.loads(words_path.read_text())["words"]
        assert words[0]["word"] == "Hello"
        assert words[0]["start"] == pytest.approx(0.1, abs=1e-3)
        assert words[0]["end"] == pytest.approx(0.3625, abs=1e-3)
        assert not (tmp_path / "line.words.jsonl").exists()
        assert _FakeCommunicate.calls[-1].kwargs["boundary"] == "WordBoundary"

    def test_bad_prosody_is_reported(self, fake_edge, tmp_path):
        res = EdgeTTS().execute({"text": "x", "rate": "fast", "output_path": str(tmp_path / "a.mp3")})
        assert not res.success
        assert "rate" in res.error

    def test_missing_package(self, monkeypatch, tmp_path):
        monkeypatch.setitem(sys.modules, "edge_tts", None)
        res = EdgeTTS().execute({"text": "x", "output_path": str(tmp_path / "a.mp3")})
        assert not res.success
        assert "edge_tts" in res.error


class TestSelectorAdaptation:
    def test_maps_capability_controls(self):
        adapted = TTSSelector._adapt_inputs(
            EdgeTTS(),
            {"text": "x", "voice_id": "jenny", "speaking_rate": 1.1, "pitch": 2, "output_format": "mp3_44100_128"},
        )
        assert adapted["voice"] == "jenny"
        assert adapted["rate"] == "+10%"
        assert "pitch" not in adapted
        assert adapted["output_format"] == "mp3"

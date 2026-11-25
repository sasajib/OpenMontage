"""Contract tests for tools.analysis.audio_check (pure helpers; no models)."""
import numpy as np

from tools.analysis.audio_check import AudioCheck


def test_wer_forgives_names_and_compounds():
    t = AudioCheck()
    assert t._wer("Shakil, this is base camp.", "Shaquille, this is Basecamp.", names=["Shakil"])["wer"] == 0.0
    assert t._wer("Still here.", "Still here.")["wer"] == 0.0
    assert t._wer("Shakil? Shakil, respond!", "Shaquille.")["wer"] > 0.5


def test_technical_flags_abrupt_end_and_clipping():
    t = AudioCheck(); sr = 16000
    tone = np.sin(np.linspace(0, 2 * np.pi * 220 * 2, sr * 2)).astype("float32") * 0.5
    f: list = []
    t._technical(tone, sr, "x", f)           # loud right to the last sample, no tail
    assert any(x["category"] == "cutoff" for x in f)
    f = []
    faded = tone * np.linspace(1, 0, len(tone)) ** 3
    t._technical(faded, sr, "x", f)
    assert not any(x["category"] == "cutoff" for x in f)
    f = []
    t._technical(np.clip(tone * 4, -1, 1), sr, "x", f)
    assert any(x["category"] == "clipping" for x in f)


def test_schema():
    t = AudioCheck()
    assert set(t.input_schema["required"]) == {"mode", "input_path"}
    assert "mix" in t.input_schema["properties"]["mode"]["enum"]

"""Tests for tools.analysis.retention_check (pure helpers plus one tiny ffmpeg render)."""
import shutil
import subprocess

import pytest

from tools.analysis.retention_check import RetentionCheck


def _script(text, meta=None, start=0.0):
    return {"total_duration_seconds": 30, "metadata": meta or {}, "sections": [{"id": "s1", "text": text, "start_seconds": start, "end_seconds": 30}]}


GOOD_META = {"promise": "why the lighthouse went dark", "retention_map": {b: 1 for b in ["hook", "promise", "second_hook", "hero_moment", "payoff", "ending"]}}


def test_script_passes_when_lines_are_short_and_map_is_complete():
    f, d = RetentionCheck().check_script(_script("The lighthouse went dark for one night. Nobody on the island could say why.", GOOD_META), "short")
    assert f == [] and d["sentences"] == 2


def test_script_flags_missing_map_late_start_and_banned_phrase():
    f, _ = RetentionCheck().check_script(_script("Let's dive in and look at 3 facts.", start=1.2), "short")
    cats = {x["category"] for x in f}
    assert {"promise", "retention_map", "voice_start", "banned_phrase", "digits_in_speech"} <= cats


def test_script_story_mode_skips_banned_list():
    f, _ = RetentionCheck().check_script(_script("He just wanted the donkey back, really.", GOOD_META), "short", explainer_lint=False)
    assert f == []


def test_long_sentences_become_critical_when_common():
    long = " ".join(["word"] * 25) + "."
    f, _ = RetentionCheck().check_script(_script(f"{long} {long}", GOOD_META), "short")
    assert any(x["category"] == "line_lint" and x["severity"] == "critical" for x in f)


def test_words_voice_start_and_dead_air_respect_planned_stills():
    t = RetentionCheck()
    words = [{"word": "a", "start": 0.9, "end": 1.2}, {"word": "b", "start": 2.5, "end": 2.8}, {"word": "c", "start": 5.0, "end": 5.2}]
    f, d = t.check_words(words, planned=[[2.8, 5.0]])
    assert [x["category"] for x in f] == ["voice_start", "dead_air"] and d["dead_air_gaps"] == 1


def test_shot_stats_and_freeze_parsing():
    t = RetentionCheck()
    assert t.shot_stats([1.0, 2.0, 3.0], 4.0)["length_ratio"] == 1.0
    assert t.shot_stats([0.5, 4.5], 5.0)["length_ratio"] == 8.0
    assert t.parse_freezes("freeze_start: 1.5\nfreeze_end: 4.0\nfreeze_start: 8", 10.0) == [(1.5, 4.0), (8.0, 10.0)]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_render_flags_a_frozen_video(tmp_path):
    still = tmp_path / "still.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=160x90:d=4:r=10", str(still)], check=True)
    r = RetentionCheck().execute({"mode": "render", "input_path": str(still)})
    cats = {x["category"] for x in r.data["findings"]}
    assert r.success and r.data["verdict"] == "REJECT" and {"static_open", "still_stretch"} <= cats

    moving = tmp_path / "moving.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=160x90:d=4:r=10", str(moving)], check=True)
    r = RetentionCheck().execute({"mode": "render", "input_path": str(moving)})
    assert not {"static_open", "still_stretch"} & {x["category"] for x in r.data["findings"]}


def test_rhythm_counts_cuts_and_whole_frame_replaces():
    scores = [(0.0, 0.0), (0.1, 0.0), (0.2, 0.9), (0.3, 0.01), (0.4, 0.4), (0.5, 0.0)]
    r = RetentionCheck().rhythm(scores)
    assert r["cuts"] == [0.2, 0.4] and r["hard_replaces"] == 1 and r["hard_replace_ratio"] == 0.5 and r["still_ratio"] == 0.4


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_render_finds_cuts_between_different_scenes(tmp_path):
    out = tmp_path / "cuts.mp4"
    src = "testsrc=s=160x90:d=1:r=10[a];smptebars=s=160x90:d=1:r=10[b];rgbtestsrc=s=160x90:d=1:r=10[c];[a][b][c]concat=n=3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src, str(out)], check=True)
    r = RetentionCheck().execute({"mode": "render", "input_path": str(out)})
    assert r.success and r.data["detail"]["shots"] == 3


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_a_held_frame_is_flagged_even_inside_a_planned_still(tmp_path):
    out = tmp_path / "hold.mp4"   # moving picture, 1 s frozen frame, moving picture
    src = "testsrc2=s=160x90:d=2:r=10,tpad=stop_mode=clone:stop_duration=1[a];testsrc2=s=160x90:d=2:r=10[b];[a][b]concat=n=2"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src, str(out)], check=True)
    r = RetentionCheck().execute({"mode": "render", "input_path": str(out), "planned_stills": [[1.8, 3.2]]})
    hits = [x for x in r.data["findings"] if x["category"] == "frozen_frame"]
    assert r.success and len(hits) == 1 and 1.5 < hits[0]["at_seconds"] < 2.3

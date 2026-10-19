"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import os
import tempfile

import pytest

from tests.settlement._builders import _ladder_map, _town


def test_place_caption_defers_to_finish_and_records_its_subject_box_for_the_gate():
    # DEFERRED on purpose: a caption seated at call time is judged against half a map (see
    # place_caption's note - Tango's north market caption landed on an execution ground that did
    # not exist yet). Nothing is in M["labels"] until finish() flushes them.
    s = _ladder_map()
    box = (400.0, 400.0, 500.0, 440.0)
    s.place_caption("market", box, 10)
    s.place_caption("ferry", (700.0, 200.0, 720.0, 600.0), 10)
    assert not [L for L in s.M["labels"] if L[5] in ("market", "ferry")]
    with tempfile.TemporaryDirectory() as d:
        s.finish(os.path.join(d, "t"), render=False)
    rec = next(L for L in s.M["labels"] if L[5] == "market")
    assert rec[6] == [400.0, 400.0, 500.0, 440.0]
    assert any(L[5] == "ferry" for L in s.M["labels"])


def test_place_caption_refuses_an_empty_subject():
    # s.frontage_box is None when the row placed nothing - captioning it is a gen-script bug
    s = _ladder_map()
    with pytest.raises(ValueError, match="no subject box"):
        s.place_caption("market", None, 10)


def test_place_caption_rot_threads_through_finish(tmp_path):
    s = _town()
    s.place_caption("caravan inn", (100, 100, 180, 160), rot=-16)
    s.finish(str(tmp_path / "t"), render=False)
    L = next(x for x in s.M["labels"] if x[5] == "caravan inn")
    assert len(L) == 8 and L[7] == -16.0 and L[6] == [100.0, 100.0, 180.0, 160.0]

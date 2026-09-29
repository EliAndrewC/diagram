"""Feature 224 FR-002 and feature 287 M6: the view is decided once, and nothing after it moves the frame.

FEATURE 287 RETIRED THE BREACH TEST (specs/287-placer-guarantees/research.md R8): every scatter a hamlet throws is thrown
within the DECIDED view's frame (`hamletgen/hinterland/frame.py:scatter_frame_for`, the marsh thrown before the decision
thrown again into it), which carries the title band's allowance above and below the view - so the one thing that grows
the view after the crop, the title's band, stays inside it by construction
(`tests/settlement/test_finish_287.py::test_a_scatter_frame_of_the_decided_view_holds_the_title_band_on_either_side`).
KEPT: the contract that no stage after the decision moves the frame, a property of every stage after it."""

from __future__ import annotations

import glob
import json
import os

import pytest

_POOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pool")


@pytest.mark.parametrize("gen", sorted(glob.glob(os.path.join(_POOL, "hamlets", "*", "*.gen.py"))), ids=os.path.basename)
def test_no_stage_after_the_view_is_decided_moves_the_frame(gen: str) -> None:
    """Feature 287, M6: the view is decided once, at the end of `stage_hinterland`, and `stage_frame` sets exactly it. The
    contract that makes that honest is that no later stage places a frame-setting feature; `stage_frame` records any
    difference between the decided view and the crop the finished map would take as `meta.view_drift`, and no shipped
    hamlet may carry one."""
    from tests.gate import _pool

    with open(_pool.obtain(gen), encoding="utf-8") as fh:
        meta = json.load(fh)["meta"]
    assert meta.get("view"), "a hamlet records its view"
    assert "view_drift" not in meta, f"a stage after the decision moved the frame by {meta.get('view_drift')} (left, top, right, bottom)"

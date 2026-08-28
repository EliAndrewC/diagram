"""The feature-class side list stays index-aligned with the record streams (feature 134, plan D1).

The class of a primitive rides beside it, never in it: every `add*()` appends to a string list and
a class list, the deferred ground / water / late-water blocks carry `cls` on their entries, and
`finish()` splices a class block beside each string block. These tests drive the streams directly
and then let `finish()` prove the alignment (it raises when the two drift), and check that the
SVG text carries no trace of a class while the page does.
"""

from __future__ import annotations

import json
import os

import pytest

from l7r.diagram.interactive.tags import Split
from l7r.diagram.settlement import Settlement

RECT = '<rect x="1" y="1" width="2" height="2" fill="#abc" stroke="#123"/>'


def _settlement() -> Settlement:
    return Settlement(400, 400, seed=3)


def test_add_tags_each_stream_and_the_explicit_class_wins_over_the_scope() -> None:
    s = _settlement()
    n0 = len(s.out)
    s.add(RECT)
    with s.feature("farmhouse"):
        s.add(RECT)
        s.add(RECT, cls="byre")
        with s.feature("garden"):
            s.add_top(RECT)
        s.add_label("<text>x</text>")
    s.add_wall(RECT, cls="-")
    assert s.out_cls[n0:] == [None, "farmhouse", "byre"]
    assert s.top_cls == ["garden"] and s.toplabels_cls == ["farmhouse"] and s.walls_cls == ["-"]
    assert s._cls is None, "the scope is restored on exit"


def test_add_parts_joins_byte_identically_and_keeps_the_pieces() -> None:
    s = _settlement()
    parts = [(None, "<g>"), ("storage shed", RECT), ("farmhouse", RECT), (None, "</g>")]
    with s.feature("garden"):
        z = s.add_parts(parts)
    assert s.out[z] == "<g>" + RECT + RECT + "</g>"
    assert s.out_cls[z] == tuple(parts), "a None piece stays None - it never inherits the scope"


def test_deferred_blocks_carry_their_class_through_the_splice(tmp_path: os.PathLike[str]) -> None:
    s = _settlement()
    s._ground(10.0, {}, "z", edge='<path d="M0,0 L1,1"/>', bed='<path d="M0,0 L1,1"/>', top='<path d="M0,0 L1,1"/>', cls="village lane")
    s._water('<path d="M0,0 L2,2"/>', {}, sheen='<path d="M0,0 L2,2"/>', cls="stream")
    s._water('<path d="M3,3 L4,4"/>', {}, late=True, cls="field ditch")
    s.add(RECT, cls=Split("paddy", "bund"))
    base = os.path.join(str(tmp_path), "t")
    s.finish(base, render=False)
    with open(base + ".json") as fh:
        m = json.load(fh)
    assert m["ink_classes"] == {"-": 1, "village lane": 3, "stream": 2, "field ditch": 1, "paddy": 1}
    assert m["unclassed_ink"] == [] and m["unregistered_classes"] == []
    with open(base + ".svg") as fh:
        svg = fh.read()
    assert "data-k" not in svg and "f-village-lane" not in svg, "the class never enters the SVG (FR-010)"
    with open(base + ".html") as fh:
        page = fh.read()
    assert page.count('data-k="village lane"') == 3 and 'data-k="stream"' in page and 'data-k="field ditch"' in page
    assert 'data-k="paddy"' in page and 'data-k="bund"' in page


def test_unclassed_ink_is_reported_in_the_manifest(tmp_path: os.PathLike[str]) -> None:
    s = _settlement()
    s.add(RECT)
    s.add(RECT, cls="flying castle")
    base = os.path.join(str(tmp_path), "t")
    s.finish(base, render=False)
    with open(base + ".json") as fh:
        m = json.load(fh)
    assert len(m["unclassed_ink"]) == 1 and m["unclassed_ink"][0].startswith("<rect>")
    assert m["unregistered_classes"] == ["flying castle"]


def test_finish_refuses_a_drifted_side_list(tmp_path: os.PathLike[str]) -> None:
    s = _settlement()
    s.out.append(RECT)  # a stream write that bypassed add()
    with pytest.raises(RuntimeError, match="out of step"):
        s.finish(os.path.join(str(tmp_path), "t"), render=False)


def test_the_frame_is_ruled_not_highlighted(tmp_path: os.PathLike[str]) -> None:
    s = _settlement()
    s.title("Testhamlet")
    base = os.path.join(str(tmp_path), "t")
    s.finish(base, render=False)
    with open(base + ".json") as fh:
        m = json.load(fh)
    assert m["unclassed_ink"] == [], "the sheet, the placard, the name and the scale bar all carry the ruling"
    assert m["ink_classes"]["-"] >= 5

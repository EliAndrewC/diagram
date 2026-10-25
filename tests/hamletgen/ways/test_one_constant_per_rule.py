"""Each lane rule the web wrote in several places with one value reads ONE constant (feature 417 T05, D13-D16; FR-006): a
later change to the rule cannot leave a copy behind."""

from __future__ import annotations

import pathlib
import re

from l7r.diagram.hamletgen import consts
from l7r.diagram.hamletgen.ways import bund, clearance, fabric, joints, knots, law, serve, sweeps, thread, touch
from l7r.diagram.hamletgen.ways.settle import shapes

WAYS = pathlib.Path(bund.__file__).parent


def _reads(mod: object, name: str, constant: str) -> bool:
    """Is `name` assigned FROM `constant` in the module's source (a float equal by value could still be a copy)?"""
    return bool(re.search(rf"^{name} = {constant}\b", pathlib.Path(mod.__file__).read_text(encoding="utf-8"), re.M))  # type: ignore[attr-defined]


def test_the_tail_past_a_meeting_is_one_constant():
    assert consts.TAIL_CUT_FT == 40.0
    for mod, name in ((sweeps, "_PAST_CONNECTOR_FT"), (bund, "_PAST_JUNCTION_FT"), (shapes, "_CROSSING_TAIL_FT"), (knots, "_TAIL_CUT_FT")):
        assert _reads(mod, name, "TAIL_CUT_FT"), f"{mod.__name__}.{name} is a copy, not the constant"
    for mod in (serve, touch):  # the bare 40.0 they carried is the constant now
        assert "TAIL_CUT_FT" in pathlib.Path(mod.__file__).read_text(encoding="utf-8")


def test_the_join_the_serve_and_the_field_reach_are_one_constant_each():
    assert _reads(fabric, "_LANE_JOIN_FT", "LANE_JOIN_FT") and _reads(joints, "_MEET_FT", "LANE_JOIN_FT")
    assert _reads(sweeps, "_SERVE_FT", "WEB_REACH_FT")
    assert _reads(thread, "SPUR_REACH_FT", "FIELD_REACH_FT") and _reads(law, "FIELD_REACH_FT", "_FIELD_REACH_FT")
    assert fabric._LANE_JOIN_FT == joints._MEET_FT == law.JOIN_REACH_FT == consts.LANE_JOIN_FT == 25.0
    assert thread.SPUR_REACH_FT == law.FIELD_REACH_FT == consts.FIELD_REACH_FT == 6.0
    assert not hasattr(knots, "_KNOT_MARGIN"), "knots asks the imported KNOT_MARGIN, not a copy"


def test_route_asks_the_bend_constants_not_literals():
    text = (WAYS / "route.py").read_text(encoding="utf-8")
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines() if not line.strip().startswith(("Research:", '"""')))
    assert not re.search(r"[<>]=\s*(?:140|50|40)\.0\b", code)
    assert (clearance._HAIRPIN_DEG, clearance._ZIGZAG_DEG, clearance._ZIGZAG_RUN_FT) == (140.0, 50.0, 40.0)

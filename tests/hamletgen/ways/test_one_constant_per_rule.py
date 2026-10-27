"""Each lane rule the web wrote in several places with one value reads ONE constant (feature 417 T05, D13-D16; FR-006): a
later change to the rule cannot leave a copy behind."""

from __future__ import annotations

import pathlib
import re

from l7r.diagram.hamletgen import consts
from l7r.diagram.hamletgen.ways import bund, clearance, fabric, knots, law, serve, sweeps
from l7r.diagram.hamletgen.ways.law import shape as law_shape
from l7r.diagram.hamletgen.ways.settle import shapes

WAYS = pathlib.Path(bund.__file__).parent


def _reads(mod: object, name: str, constant: str) -> bool:
    """Is `name` assigned FROM `constant` in the module's source (a float equal by value could still be a copy)?"""
    return bool(re.search(rf"^{name} = {constant}\b", pathlib.Path(mod.__file__).read_text(encoding="utf-8"), re.M))  # type: ignore[attr-defined]


def test_the_tail_past_a_meeting_is_one_constant():
    assert consts.TAIL_CUT_FT == 40.0
    for mod, name in ((shapes, "_CROSSING_TAIL_FT"), (knots, "_TAIL_CUT_FT")):  # sweeps' and bund's copies went with their passes (T26)
        assert _reads(mod, name, "TAIL_CUT_FT"), f"{mod.__name__}.{name} is a copy, not the constant"
    assert "TAIL_CUT_FT" in pathlib.Path(serve.__file__).read_text(encoding="utf-8")  # the bare 40.0 it carried is the constant now


def test_the_join_the_serve_and_the_field_reach_are_one_constant_each():
    assert _reads(fabric, "_LANE_JOIN_FT", "LANE_JOIN_FT")
    assert _reads(sweeps, "_SERVE_FT", "WEB_REACH_FT")
    assert _reads(law_shape, "FIELD_REACH_FT", "_FIELD_REACH_FT")  # the field spur's copy, `thread.SPUR_REACH_FT`, went with the spur (T50); the law a package since 417 T54
    assert fabric._LANE_JOIN_FT == law.JOIN_REACH_FT == consts.LANE_JOIN_FT == 25.0
    assert law.FIELD_REACH_FT == consts.FIELD_REACH_FT == 6.0
    assert not hasattr(knots, "_KNOT_MARGIN"), "knots asks the imported KNOT_MARGIN, not a copy"


def test_route_asks_the_bend_constants_not_literals():
    text = (WAYS / "route.py").read_text(encoding="utf-8")
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines() if not line.strip().startswith(("Research:", '"""')))
    assert not re.search(r"[<>]=\s*(?:140|50|40)\.0\b", code)
    assert (clearance._HAIRPIN_DEG, clearance._ZIGZAG_DEG, clearance._ZIGZAG_RUN_FT) == (140.0, 50.0, 40.0)


def test_the_bund_reach_is_the_settlement_s_one_constant():
    """Feature 417 T25 (D19): the 6 ft bund reach was two 6.0s (`water_ways._helpers.BUND_REACH_FT` and
    `consts_ways.FIELD_REACH_FT`). T25's second half - `cut_stub_ends` cutting a tail under 40 ft - went with its pass (T26)."""
    from l7r.diagram.hamletgen import consts_ways

    assert _reads(consts_ways, "FIELD_REACH_FT", "BUND_REACH_FT")

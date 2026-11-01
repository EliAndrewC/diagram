"""Lay a whole comb field in one call, for tests: the Rust stage's comb (`l7r_phases.stage_field`, feature 444 T16) turned into
the `net` the thin stage hands the free readers and the ink (`hamletgen.field_stage.comb_net`). The old engine's
`carve_comb`/`finish_comb` went with the field's port; the tests that build a comb to test what reads it call this instead.
The old arguments are taken and the ones the rebuilt comb has no use for are ignored: the canvas, the seed and the fall."""

from typing import Any

from l7r.diagram.hamletgen.consts_water import BROOK_SKIRT, BROOK_SLEW, BROOK_TAP_RUN, BROOK_WANDER, OFFTAKE_DEG, WEIR_SKEW_DEG, WEIR_THICK_FT
from l7r.diagram.hamletgen.field_stage import (
    BROOK_STATION,
    BROOK_W,
    CELL_SHARE,
    WEIR_HALF,  # the stage's own half-length, as it passes it
    comb_net,
)
from l7r.diagram.hamletgen.phases_ext import phases


def lay_comb(W: float = 1400, H: float = 1400, *_args: Any, seed: int = 4, down_deg: float = 90.0, households: int = 15, **_kw: Any) -> dict[str, Any]:
    brook = (105.0, OFFTAKE_DEG, BROOK_TAP_RUN, BROOK_SLEW, BROOK_SKIRT, BROOK_WANDER, BROOK_STATION, BROOK_W)
    knobs = [("intake", ["open"], [], "open"), ("paddy_rest", ["settled"], [], "settled"), ("winter_crop", ["none"], [], "none"), ("fan_middle", ["wild"], [], "wild")]
    out = phases().stage_field(
        seed,
        households,
        float(down_deg),
        1.0,
        (W / 2.0, H / 2.0),
        (float(W), float(H)),
        1.0,
        brook,
        ([0.30, 0.62, 0.93], [0.55]),
        (WEIR_HALF, WEIR_SKEW_DEG, dict(WEIR_THICK_FT)),
        "medium",
        48.0 * CELL_SHARE,
        knobs,
    )
    return comb_net(out["fields"][0], "test-paddies", 48.0 * CELL_SHARE, float(down_deg), "wild")

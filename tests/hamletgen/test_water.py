"""Unit tests for the water frame and the field it shapes (`hamletgen/water/`), plus the waterfields frame math it stands on.

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from ._builders import a_plan

# ---- the derivations that read the map ----------------------------------------------------------


def test_declared_knob_pins_reach_the_engine() -> None:
    """A `pins` entry is forwarded to the engine's own knob catalog, so a spec can steer a knob this
    module does not model (a land-use overlay, a field archetype)."""
    from l7r.diagram.settlement import Settlement

    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=2, households=12, pins={"land_use_overlay": "lotus"}))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    hg.stage_water_frame(s, plan)
    assert s.knob_pins["land_use_overlay"] == "lotus"


def test_the_waterward_strip_stops_at_the_dikes_face() -> None:
    """T54: no strip vertex may stand inside the drawn band, and the strip must still cover the
    ground 28 px outside the dike's extreme, which is where `polder_waterward_flanks_wet` samples."""
    plan = a_plan()
    plan.field_archetype = "polder_grid"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    band = [(500.0 + 40.0 * (i % 2), 400.0 + i * 10.0) for i in range(40)]  # a wandering west face
    band += [(1400.0, 400.0 + i * 10.0) for i in range(40)]
    s.M["dikes"] = [{"outline": [list(p) for p in band], "w_min": 14.0, "w_max": 38.0}]
    hg.stage_waterward(s, plan)
    strips = [m for m in s.M["marshes"] if m["role"] == "waterside"]
    assert strips, "no waterward strip was drawn"
    west = [m for m in strips if m["x"] < 900][0]
    assert max(p[0] for p in west["poly"]) <= 540.0  # never past the outermost face of the band
    assert hg.point_in_poly(500.0 - 28.0, 600.0, [(float(a), float(b)) for a, b in west["poly"]])  # the check's own sample is inside


# ---- feature 219: Polder 12's three lines, as unit tests of the functions that own them ----------------


# ---- the intake, and the brook that runs on past it (feature 230) --------------------------------


def test_the_ways_route_against_the_course_as_first_drawn() -> None:
    """`stream_segs` (feature 287, M2): the router's brook is the `stations` - the course before rounding - so rounding
    the brook early does not move the ways; a stream never rounded is read from its poly."""
    from l7r.diagram.hamletgen.ways.checks import stream_segs

    class _S:
        M = {"streams": [{"poly": [[0, 0], [5, 3], [10, 0]], "stations": [[0, 0], [10, 0]]}, {"poly": [[0, 50], [0, 90]]}, {"poly": []}]}

    assert stream_segs(_S()) == [((0.0, 0.0), (10.0, 0.0)), ((0.0, 50.0), (0.0, 90.0))]  # type: ignore[arg-type]


def test_a_hamlet_keeps_its_yards_wherever_grain_is_grown() -> None:
    """Feature 328 (0037: every rice and dry-field farm keeps a yard): the yards go only where no grain grows - a dike-pond
    hamlet whose leftover parcels are ponds - and a dike-pond hamlet with rice left, or a dry-field one, keeps them."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.water.skeleton import grows_grain

    assert not grows_grain(SimpleNamespace(field_archetype="mulberry_dike_fishpond", leftover="pond"))  # type: ignore[arg-type]
    assert grows_grain(SimpleNamespace(field_archetype="mulberry_dike_fishpond", leftover="rice"))  # type: ignore[arg-type]
    assert grows_grain(SimpleNamespace(field_archetype="dry_terrace", leftover="rice"))  # type: ignore[arg-type]

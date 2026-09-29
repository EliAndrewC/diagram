"""Feature 287 (water W28-W30, W33, W34, W37, plan D9): what the comb field's drawing guarantees where it decides.

Each test drives the placer - `carve_around_grave`, a grave or pond seat, `draw_comb_field` or its bead drop - on
constructed inputs that include the violating case, and asks the rule's one predicate (`waterfields/ring_rules.py`, or
the rule's own record) of what it made.
"""

import copy
import random

from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.fields.features import GRAVE_BANK_PX, carve_around_grave
from l7r.diagram.waterfields.ring_rules import RingContext, as_recorded, ring_area, ring_violations, under_island


def _comb() -> dict:
    """One small comb net, built once on disk (as `tests/settlement/test_fields.py` builds its own) and deep-copied per
    caller, because drawing and carving MUTATE the net."""
    from l7r.diagram.waterfields import build_comb

    key = "test_field_guarantees-comb:v1"
    return copy.deepcopy(rollcache.obtain(key, lambda: build_comb(1400, 1400, (700, 200), 1, down_deg=90, field_fall=400, grain=2.0, supply_banks=True))[0])


def _lattice(n: int, side: float = 40.0) -> list[dict]:
    return [{"poly": [(i * side, j * side), ((i + 1) * side, j * side), ((i + 1) * side, (j + 1) * side), (i * side, (j + 1) * side)], "fill": "#A6C398"} for j in range(n) for i in range(n)]


def _area(plots: list[dict]) -> float:
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    return float(unary_union([Polygon(p["poly"]).buffer(0) for p in plots]).area)


def test_the_paddy_is_carved_round_a_grave_on_a_four_way_junction() -> None:
    """W28: a grave seated where four basins meet - the case the design names - has every one of the four bitten back
    off its mound, and no ring runs under it; every ring left keeps every ring rule, the grave among them."""
    plots = _lattice(12)
    disc = (240.0, 240.0, 9.0 + GRAVE_BANK_PX)
    ctx = RingContext(cell=1600.0, g=2.0, graves=[disc])
    assert sum(under_island(p["poly"], disc) for p in plots) == 4
    carve_around_grave(plots, disc, None, ctx)
    assert not [p for p in plots if under_island(p["poly"], disc)]
    assert all(not ring_violations(as_recorded(p["poly"]), ctx) for p in plots)
    assert _area(plots) > 480.0 * 480.0 - 3.3 * disc[2] ** 2 - 1.0, "only the mound's own ground is taken"


def test_an_island_host_is_halved_through_its_mound_and_each_half_bitten() -> None:
    """W28: an island inside one basin would leave the basin a hole, which no ring can record - so the host is split in
    two along its long axis through the mound, and each half runs up to it."""
    plots = [{"poly": [(0.0, 0.0), (120.0, 0.0), (120.0, 60.0), (0.0, 60.0)], "fill": "#A6C398"}]
    disc = (60.0, 30.0, 10.0)
    ctx = RingContext(cell=1500.0, g=2.0, graves=[disc])
    carve_around_grave(plots, disc, None, ctx)
    assert len(plots) == 2 and not [p for p in plots if under_island(p["poly"], disc)]
    assert sorted(round(max(y for _x, y in p["poly"]) - min(y for _x, y in p["poly"])) for p in plots) == [30, 30], "halved along the long axis"


def test_a_corner_grave_has_its_basin_bund_carried_round_it_to_the_corner() -> None:
    """W28, the corner form: the bite is carried out to the corner, so the basin's bund goes round the grave and the
    basin keeps one ring; a basin carved away entirely under a mound is dropped, its ground the mound's."""
    square = [(0.0, 0.0), (60.0, 0.0), (60.0, 40.0), (0.0, 40.0)]
    crumb = [(4.0, -30.0), (8.0, -30.0), (8.0, -26.0), (4.0, -26.0)]  # wholly under a second grave's mound
    plots = [{"poly": list(square), "fill": "#A6C398"}, {"poly": list(crumb), "fill": "#A6C398"}]
    disc = (10.0, 8.0, 7.5)
    carve_around_grave(plots, disc, (0.0, 0.0), RingContext(cell=1000.0, g=2.0, graves=[disc]))
    assert len(plots) == 2 and not under_island(plots[0]["poly"], disc)
    assert (0.0, 0.0) not in plots[0]["poly"], "the corner itself is the grave's"
    other = (6.0, -28.0, 5.0)
    carve_around_grave(plots, other, None, RingContext(graves=[other]))
    assert len(plots) == 1 and ring_area(plots[0]["poly"]) > 0.9 * (2400.0 - 3.3 * 7.5**2)


def test_a_grave_seated_on_a_comb_carves_the_rings_it_stands_among() -> None:
    """W28 through the placer: an island seated on a real comb's plot leaves no recorded ring under its mound, and the
    beads the carve took the bund from are dropped at the draw (W33/W34)."""
    net = _comb()
    s = Settlement(W=1400, H=1400, seed=3)
    s.meta(name="Gr", scale="hamlet", ftpx=1, down_deg=90)
    host = max(net["plots"], key=lambda p: ring_area(p["poly"]))
    assert s._plot_grave_island(host, random.Random(1), net) is True
    disc = net["grave_discs"][0]
    assert not [p for p in net["plots"] if under_island(as_recorded(p["poly"]), disc)]
    g = s.M["field_graves"][0]
    assert (g["x"], g["y"]) == disc[:2], "the grave is recorded where it was carved"


def test_a_grave_never_stands_in_a_field_pond() -> None:
    """W28 with W29: a plot whose mound would stand in a field pond is refused - nothing drawn - and the next is taken."""
    s = Settlement(W=1400, H=1400, seed=3)
    s.meta(name="Gp", scale="hamlet", ftpx=1, down_deg=90)
    s.M["field_ponds"] = [{"x": 85.0, "y": 40.0, "rx": 60.0, "ry": 30.0}]
    plot = {"poly": [(0.0, 0.0), (120.0, 0.0), (120.0, 60.0), (0.0, 60.0)], "fill": "#A6C398"}
    assert s._plot_grave_island(plot, random.Random(1)) is False
    assert s._plot_corner_grave({"poly": [(50.0, 20.0), (120.0, 20.0), (120.0, 60.0), (50.0, 60.0)]}, random.Random(1)) is False
    assert not s.M.get("field_graves")


def test_a_rolled_field_pond_is_always_drawn() -> None:
    """Plan D9 (water W29): the pond's knob is rolled only over a field where some low plot can hold a legible pond, so
    whenever it rolls a pond one is drawn; a field whose low plots are all wedges rolls none, and the rolls after it are
    unmoved - the draws are taken and discarded."""
    roomy = [{"poly": [(float(i * 50), 0.0), (float(i * 50 + 44), 0.0), (float(i * 50 + 44), 34.0), (float(i * 50), 34.0)], "low": True, "fill": "#A6C398"} for i in range(3)]
    wedges = [{"poly": [(float(i * 50), 0.0), (float(i * 50 + 44), 0.0), (float(i * 50), 3.0)], "low": True, "fill": "#A6C398"} for i in range(3)]
    for seed in range(30):
        rolled = random.Random((seed ^ 0x9AD1) & 0xFFFFFFFF).random() < 0.55
        s = Settlement(1200, 1200, seed=seed)
        s.meta(name="P", scale="village", ftpx=1, down_deg=90, field_archetype="valley_paddy")
        s._paddy_features({"plots": copy.deepcopy(roomy)})
        assert bool(s.M.get("field_ponds")) == rolled, seed
        w = Settlement(1200, 1200, seed=seed)
        w.meta(name="W", scale="village", ftpx=1, down_deg=90, field_archetype="valley_paddy")
        w._paddy_features({"plots": copy.deepcopy(wedges)})
        assert not w.M.get("field_ponds")
        assert bool(w.M.get("field_graves")) == bool(s.M.get("field_graves")), "the grave's roll sits on the same stream"


def test_every_ditched_comb_draws_its_floor_under_its_plots_and_names_its_water() -> None:
    """W30 and W37, by construction: `draw_comb_field` lays the fan's floor before any plot is drawn, and records a field
    ditch naming the field, so every paddy shows where its water comes from."""
    net = _comb()
    net["brook"] = []
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Fl", scale="hamlet", ftpx=1, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    assert "f1" in s.M["comb_floors"]
    floor = next(i for i, e in enumerate(s.out) if "padbase" in e and "<polygon" in e)
    first_plot = next(i for i, e in enumerate(s.out) if e.startswith("<polygon") and "stroke-linejoin" in e and "stroke=\"#" in e and i != floor)
    assert floor < first_plot, "the floor is drawn under the plots"
    assert any(d.get("field") == "f1" for d in s.M["field_ditches"])


def test_the_bead_drop_leaves_no_bead_on_water_on_a_mound_or_alone() -> None:
    """W33 and W34 at the draw: a bead under a recorded ditch's stroke, or on a grave's mound, or on a stretch of bund no
    ring now has, is dropped - and a run left with one bead loses it (`bead_runs`, the one place the rule lives)."""
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Bd", scale="hamlet", ftpx=1, down_deg=90)
    s.M["field_ditches"] = [{"poly": [[100.0, 0.0], [100.0, 200.0]], "w": 3.0, "w_tail": 5.0}]
    ring = [(0.0, 0.0), (200.0, 0.0), (200.0, 100.0), (0.0, 100.0)]
    net = {
        "plots": [{"poly": ring}],
        "bund_bean_runs": [[(90.0, 0.0), (99.5, 0.0), (109.0, 0.0)], [(150.0, 0.0), (160.0, 0.0), (170.0, 0.0)], [(20.0, 40.0), (30.0, 40.0)]],
        "grave_discs": [(160.0, 5.0, 8.0)],
    }
    s._comb_drop_drowned_beads(net, {"kind": "stream"})
    assert net["bund_bean_runs"] == [], "a middle bead in the ditch leaves two singles; the mound takes one; the third run is on no bund"
    assert net["bund_beans"] == []

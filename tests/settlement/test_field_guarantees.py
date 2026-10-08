"""Feature 287 (water W28-W30, W33, W34, W37, plan D9): what the comb field's drawing guarantees where it decides.

Each test drives the placer - `carve_around_grave`, a grave or pond seat, `draw_comb_field` or its bead drop - on
constructed inputs that include the violating case, and asks the rule's one predicate (`waterfields/ring_rules.py`, or
the rule's own record) of what it made.
"""

import copy
import math
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


def test_an_intake_declares_a_stream_only_where_its_mouth_reaches_one() -> None:
    """L16 at the intake: a feed whose sluice stands within the anchor band of a stream is snapped onto its bed and declares
    it (`channel_end_on_stream`); one with no stream within reach is sourced from the sluice and declares no stream -
    never a mouth in the grass recorded as joining the brook."""
    from l7r.diagram.settlement.fields.comb import channel_end_on_stream

    far = _comb()
    far["brook"] = []
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="In", scale="hamlet", ftpx=1, down_deg=90)
    s.M["streams"].append({"poly": [[1300.0, 0.0], [1300.0, 1400.0]]})  # 600 ft off: out of reach
    s.draw_comb_field(far, "f1", {"kind": "stream"})
    feed = s.M["channels"][-1]
    assert feed["frm"] == {"kind": "sluice"} and not channel_end_on_stream(feed["poly"][0], s.M["streams"][0]["poly"], 7.0)
    near = _comb()
    near["brook"] = []
    sx, sy = near["channels"][0]["pts"][0]
    t = Settlement(W=1400, H=1400, seed=5)
    t.meta(name="In", scale="hamlet", ftpx=1, down_deg=90)
    t.M["streams"].append({"poly": [[sx - 400.0, sy - 20.0], [sx + 400.0, sy - 20.0]]})  # 20 ft off: inside the anchor band
    t.draw_comb_field(near, "f1", {"kind": "stream"})
    feed = t.M["channels"][-1]
    assert feed["frm"] == {"kind": "stream"} and channel_end_on_stream(feed["poly"][0], t.M["streams"][0]["poly"], 7.0)
    assert channel_end_on_stream((0.0, 3.4), [(-10.0, 0.0), (10.0, 0.0)], 7.0) and not channel_end_on_stream((0.0, 3.6), [(-10.0, 0.0), (10.0, 0.0)], 7.0)  # inside the drawn width (0054), feature 328


def test_a_bead_water_recorded_later_lies_over_is_dropped_from_the_ink_and_the_record() -> None:
    """W33, the later-water half: the field drops its drowned beads over the water recorded when it is drawn, and a later
    stage (the sink's drain run) can record more; `settle_beads` - run after the last water writer - drops every bead that
    water now covers, from the ink slot and the field record together, judged by the one predicate `bead_drowned`."""
    from l7r.diagram.settlement.fields.comb import bead_drowned, recorded_water

    net = _comb()
    net["brook"] = []
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Bd", scale="hamlet", ftpx=1, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    rec = s.M["fields"][-1]
    beads = [tuple(b) for b in rec["bund_beans"]]
    assert beads and s.settle_beads() == 0, "nothing new: nothing moves"
    bx, by = beads[len(beads) // 2]
    s.M["channels"].append({"poly": [[bx - 40.0, by], [bx + 40.0, by]], "frm": {"kind": "drain"}, "to": {"kind": "offmap"}, "w": 6.0})
    assert s.settle_beads() > 0
    water = recorded_water(s.M)
    assert rec["bund_beans"] and not [b for b in rec["bund_beans"] if bead_drowned((b[0], b[1]), water, [])]
    ink = next(e for e in s.out if 'r="1.4"' in e and "circle" in e)
    assert ink.count("<circle") == len(rec["bund_beans"]), "the dots and the manifest agree"


def test_the_drain_outfall_run_is_drawn_over_every_plot() -> None:
    """W38 at the comb: every channel the comb draws - the net and the drain's run off the field alike - goes to the LATE
    water block, which is spliced after the last plot, so no plot is painted over a channel."""
    net = _comb()
    end = next(c for c in net["channels"] if c["role"] == "drain")["pts"][-1]
    net["brook"] = [tuple(end), (end[0], end[1] + 40.0)]  # the collector's run on off the field
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Lt", scale="hamlet", ftpx=1, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    assert s.M["drawn_channels"] and all(r["late"] for r in s.M["drawn_channels"])
    plots = [i for i, e in enumerate(s.out) if e.startswith("<polygon") and "stroke-linejoin" in e]
    assert plots and s._late_water_idx is not None and s._late_water_idx > max(plots)
    assert not any(w == 33.0 for _, w in s.corridors), "a hamlet keeps its houses off the drain by the below-the-drain rule"


def test_the_outfall_run_keeps_33_ft_clear_on_a_town_or_city_only() -> None:
    """Feature 328 (0058's drawing page): the outfall corridor, 33 ft no-build either side of the run, on a town or city map,
    in feet at the map's own scale; a hamlet or village relies on the below-the-drain rule (the test above)."""
    net = _comb()
    end = next(c for c in net["channels"] if c["role"] == "drain")["pts"][-1]
    net["brook"] = [tuple(end), (end[0], end[1] + 40.0)]
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Ct", scale="city", ftpx=2, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    assert s.corridors[-1][1] == s.px(33.0) == 16.5


def test_finish_settles_every_bead_the_last_water_drowned_and_a_reroll_copy_keeps_its_slots(tmp_path) -> None:
    """W33, the ordering half: `finish` settles the beads first, after every water writer - so a drain recorded across a
    bund after the field (the sink's run) leaves no emitted bead within half its stroke, in the SVG and the manifest alike.
    The slots ride on the settlement, so a re-roll's deep copy settles its own."""
    import re

    from l7r.diagram.settlement.fields.comb import bead_drowned, recorded_water

    net = _comb()
    net["brook"] = []
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Bf", scale="hamlet", ftpx=1, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    bx, by = s.M["fields"][-1]["bund_beans"][len(s.M["fields"][-1]["bund_beans"]) // 2]
    s = copy.deepcopy(s)
    s.M["channels"].append({"poly": [[bx - 40.0, by], [bx + 40.0, by]], "frm": {"kind": "drain"}, "to": {"kind": "offmap"}, "w": 6.0})
    s.M["pond"] = [bx + 200.0, by + 200.0, 30.0, 20.0]
    s.finish(str(tmp_path / "b"), render=False)
    svg = (tmp_path / "b.svg").read_text()
    water = recorded_water(s.M)
    ponds = [(bx + 200.0, by + 200.0, 30.0, 20.0)]
    drawn = [(float(x), float(y)) for x, y in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="1.4"', svg)]
    assert drawn and not [q for q in drawn if bead_drowned(q, water, ponds)]
    assert not [b for b in s.M["fields"][-1]["bund_beans"] if bead_drowned((b[0], b[1]), water, ponds)]


def test_a_plot_drawn_after_the_water_is_painted_under_every_channel(tmp_path) -> None:
    """W38: a settlement that draws a channel and THEN a plot - the stage order that buried a village's ditches - emits the
    plot before the channel, because every plot goes through the paddy layer (`add_paddy`) and `finish` lifts one drawn
    after the water block's anchor to the block's front."""
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="Pl", scale="hamlet", ftpx=1, down_deg=90)
    s.field_channel([(100.0, 300.0), (500.0, 300.0)], "#6C9CBE", 3.0, 3.0)
    s.add_paddy('<polygon points="80,250 520,250 520,350 80,350" fill="#A6C398" stroke="#8FA87A" stroke-width="2"/>', cls="paddy")
    s.add_paddy('<polygon points="0,0 10,0 10,10" fill="#A6C398"/>', cls="paddy")
    s.finish(str(tmp_path / "p"), render=False)
    svg = (tmp_path / "p.svg").read_text()
    assert 0 <= svg.index("<polygon points=\"80,250") < svg.index('stroke="#6C9CBE"'), "the plot is painted before the channel"
    assert svg.index('<polygon points="0,0') < svg.index('stroke="#6C9CBE"')


def test_the_feed_runs_downhill_its_snap_refused_where_it_would_climb_and_a_climbing_feed_refused() -> None:
    """W10 at the hairline feed (`_comb_source_channel`), on the violating cases: a fan whose own fall leaves the race
    running only 20 ft down it, with a stream 25 ft DOWN the fall of the sluice - snapping the feed onto
    that stream would leave it climbing (the snap is not taken; the feed keeps the sluice), and a fall across which the race
    runs a little uphill (the feed is refused by name, never recorded as water running uphill). `runs_downhill` is the one rule."""
    import math

    import pytest

    from l7r.diagram.settlement.fields.comb import runs_downhill

    base = _comb()
    (sx, sy), fork = base["channels"][0]["pts"][0], base["channels"][0]["pts"][-1]
    th = math.atan2(fork[1] - sy, fork[0] - sx)
    run = math.hypot(fork[0] - sx, fork[1] - sy)
    phi = th + math.acos(20.0 / run)  # the fall the race descends only 20 ft along (feature 328: any net descent runs downhill)
    f = (math.cos(phi), math.sin(phi))
    net = _comb()
    net["brook"], net["down_deg"] = [], math.degrees(phi)
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="In", scale="hamlet", ftpx=1, down_deg=90)
    q = (sx + f[0] * 25.0, sy + f[1] * 25.0)  # the nearest point of the stream to the sluice, 25 ft down the fall
    s.M["streams"].append({"poly": [[q[0] - f[1] * 300.0, q[1] + f[0] * 300.0], [q[0] + f[1] * 300.0, q[1] - f[0] * 300.0]]})
    assert not runs_downhill([q, fork], f), "the case: the snapped feed would climb 5 ft"
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    feed = s.M["channels"][-1]
    assert feed["poly"][0] == [round(sx, 1), round(sy, 1)] and runs_downhill(feed["poly"], f)
    across = _comb()
    across["brook"], across["down_deg"] = [], math.degrees(th) + 95.0  # the race a little uphill of level
    t = Settlement(W=1400, H=1400, seed=5)
    t.meta(name="In", scale="hamlet", ftpx=1, down_deg=90)
    with pytest.raises(ValueError, match="runs level or uphill"):
        t.draw_comb_field(across, "f1", {"kind": "stream"})


def _turn_deg(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    h0, h1 = math.atan2(b[1] - a[1], b[0] - a[0]), math.atan2(c[1] - b[1], c[0] - b[0])
    return abs(math.degrees((h1 - h0 + math.pi) % (2 * math.pi) - math.pi))


def test_the_drain_outfall_run_runs_downhill_and_goes_straight_down_where_its_lead_would_climb() -> None:
    """W10 at the village and city comb's drain outfall (`outfall_run`): the drawn run - 70 px on along the drain's exit,
    then 520 down the fall - runs downhill even where the drain exits straight UP the fall (the worst case); and the
    violating case, a lead long enough to take back more than the reach gives, is not drawn - the run goes straight down
    the fall from the drain's end. `runs_downhill` is the one rule."""
    from l7r.diagram.settlement.fields.comb import outfall_run, runs_downhill

    fall = (0.0, 1.0)
    for b1 in [(100.0, 150.0), (150.0, 100.0), (100.0, 50.0), (50.0, 100.0), (150.0, 140.0)]:
        run = outfall_run((100.0, 100.0), b1, fall)
        assert runs_downhill(run, fall), f"the drawn run from an exit toward {b1}"
        assert max(_turn_deg(a, b, c) for a, b, c in zip(run, run[1:], run[2:], strict=False)) <= 55.0 + 1e-9, "curving out of the collector, at most 55 degrees a turn (0060, feature 328)"
    assert len(outfall_run((100.0, 100.0), (100.0, 150.0), fall)) == 3, "an exit already down the fall runs straight on"
    assert len(outfall_run((100.0, 100.0), (150.0, 100.0), fall)) == 4, "a cross-slope exit bends in two turns of 45"
    up = [(100.0, 100.0), (100.0, -500.0), (100.0, -400.0)]
    assert not runs_downhill(up, fall), "the case: a 600 px lead up the fall, 100 back down, climbs"
    run = outfall_run((100.0, 100.0), (100.0, 50.0), fall, lead=600.0, reach=100.0)
    assert run[0] == (100.0, 100.0) and len(run) == 5 and runs_downhill(run, fall), "the fallback curves out from the drain's end"
    assert max(_turn_deg(a, b, c) for a, b, c in zip([(100.0, 150.0), *run], run, run[1:], strict=False)) <= 55.0 + 1e-9, "its first turn off the exit included (feature 328)"


def test_every_grave_stone_stands_on_its_mound_and_steps_back_from_the_last() -> None:
    """Glyph check, Inashiro (feature 302): a fixed step back put the third stone's base 2 ft off a mound under 10 ft tall; a clamp
    per stone then set the third level with the second (round 2). Each base stands inside the mound's ellipse at its x, each
    stands further back than the last, and a large mound keeps the stagger as it was."""
    from l7r.diagram.settlement.fields.features import stone_dx, stone_steps

    for rx, ry in ((9.0, 6.0), (12.6, 8.3), (30.0, 20.0)):
        ups = stone_steps(3, rx, ry)
        assert all((stone_dx(i) / rx) ** 2 + (up / ry) ** 2 < 1.0 for i, up in enumerate(ups)), (rx, ry, ups)
        assert ups == sorted(ups) and len(set(ups)) == 3, f"each stone steps back from the last: {ups}"
    assert stone_steps(3, 30.0, 20.0) == [3.0, 6.5, 10.0], "a large mound keeps the stagger"
    assert stone_steps(2, 0.0, 6.0) == [0.0, 0.0], "a mound with no width has no room"


def test_the_feed_is_recorded_at_the_width_of_the_channel_it_traces() -> None:
    """0068 (feature 328 wave 41, impl-drift): the feed's record traces a drawn channel - the comb's head race, or the polder's
    main canal from the reservoir's rim - so it carries that channel's drawn width (both were recorded at the head race's 6.0)."""
    net = _comb()
    net["brook"] = []
    net["channels"][0]["w"] = 8.5
    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="In", scale="hamlet", ftpx=1, down_deg=90)
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    assert s.M["channels"][-1]["w"] == 8.5

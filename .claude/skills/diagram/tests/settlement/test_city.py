"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import math

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement, seg_dist
from tests.settlement._builders import _cap020, _crop_settlement, _inwall_settlement, _plank_bed, _town


def test_gapped_ring_merges_when_first_vertex_is_not_a_gate():
    # a closed wall ring whose FIRST vertex is not a gate: the run after the last gap must merge back
    # into the first, leaving one continuous subpath (not a spurious break at the start point)
    s = Settlement(1000, 1000, seed=1)
    ring = [(100, 100), (300, 100), (300, 300), (100, 300), (100, 100)]  # closed square
    d = s._gapped_ring(ring, [(300, 100)], gap=20, closed=True)  # one gate, at a NON-first vertex
    assert d.count("M") == 1


def test_wall_walk_crosses_multiple_edges():
    # walking further than one wall edge: the accumulate-and-step branch must carry across edges. A run
    # of short 50px edges, gate at index 4, walking 120px west crosses edges 4->3->2 to land at x=180.
    s = Settlement(1000, 1000, seed=1)
    pts = [(100, 100), (150, 100), (200, 100), (250, 100), (300, 100), (300, 150)]
    x, y, ang = s._wall_walk(pts, 4, 120, west=True)
    assert abs(x - 180) < 1e-6 and abs(y - 100) < 1e-6
    assert abs(ang - 180) < 1e-6  # the run is horizontal; walking west the edge points in -x


def test_moat_closes_into_a_ring_without_a_river():
    # the moat(river=None) branch: with no river to join, the moat closes on itself into a ring (the
    # else arm), so the recorded polyline's first and last points coincide. The river-open-arc arm is
    # covered by test_river_canal_dock_jetty_water_gate_defaults.
    import math as m

    s = _crop_settlement()
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 12)), round(700 + 300 * m.sin(2 * m.pi * i / 12))) for i in range(12)]
    s.moat(pts)  # no river -> CLOSED ring
    assert s.M["moat"][0] == s.M["moat"][-1]


def test_bridges_carries_the_ring_road_over_the_cargo_canal_but_not_over_a_buried_conduit():
    """The ring road is a carried way and the cargo canal a watercourse - the pair that used to be
    invisible here, so both cities hand-placed that deck and both went crooked (GM 2026-07-27). An
    UNDRAWN channel is a buried conduit, though: nothing on the ground to bridge."""
    s = _crop_settlement()
    s.M["ring_road"] = [[100, 300], [500, 300]]
    s.M["ring_road_width"] = 7
    s.M["canals"] = [{"poly": [[300, 150], [300, 450]], "w": 12}]
    s.M["channels"] = [{"poly": [[200, 150], [200, 450]], "frm": None, "to": None, "w": 2.5, "drawn": False}]
    assert s.bridges() == 1  # the canal only - the conduit is not a crossing
    deck = s.M["bridges"][0]
    assert abs(deck["x"] - 300) < 2 and abs(deck["y"] - 300) < 2  # ON the crossing, solved not eyeballed
    assert deck["rot"] == 0 and deck["w"] == 7  # ALONG the ring road, and as wide as the way it carries


def test_log_boom_defaults_to_a_full_holding_pen_and_records_its_box():
    s = _crop_settlement()
    z = s.log_boom(400, 300, rot=90)
    b = s.M["log_booms"][0]
    assert b["z"] == z and b["len"] == round(s.px(330), 1)  # the default pen, ~330 real ft of chained logs
    assert b["pen_w"] == round(s.px(40), 1)  # ~40 real ft of held water between chain and shore
    # the record carries TRUE unrotated dims + rot, like a building - the matrix extractor rotates
    # x/w/h by rot itself, so a rotation-folded box here would double-rotate into a phantom
    # footprint (which is exactly how the first pen landed "on" Minami's lumber yard 42px away)
    assert b["w"] == b["len"] and b["h"] == b["pen_w"] and b["rot"] == 90.0


def test_log_boom_labels_below_itself_unless_told_otherwise():
    s = _crop_settlement()
    s.log_boom(400, 300, rot=0, length=90, label="log boom")
    assert any(len(lb) > 5 and lb[5] == "log boom" for lb in s.M["labels"])
    s2 = _crop_settlement()
    s2.log_boom(400, 300, rot=0, length=90, label=None)
    assert not any(len(lb) > 5 and lb[5] == "log boom" for lb in s2.M["labels"])


def test_bridge_refuses_a_second_deck_on_a_crossing_that_already_has_one():
    """ONE DECK PER CROSSING - the guard lives in bridge() so every caller is covered.

    Minami shipped two decks over the Hayakawa 3px apart (a hand-placed one plus the automatic pass),
    and honda/hoshigaoka/kikuta each carried two footplanks at the SAME point. None was caught because
    bridges were invisible to the overlap matrix."""
    s = _crop_settlement()
    z1 = s.bridge(300, 300, 0, 60, 12)
    z2 = s.bridge(303, 301, 0, 60, 12)  # the same crossing, a few px off
    assert len(s.M["bridges"]) == 1 and z2 == z1  # returns the standing deck rather than drawing a second
    # ...but two genuinely distinct footplanks a few px apart still both draw (the tolerance scales
    # with the deck, so a narrow plank keeps a narrow exclusion)
    s2 = _crop_settlement()
    s2.bridge(300, 300, 0, 8, 2)
    s2.bridge(306, 300, 0, 8, 2)
    assert len(s2.M["bridges"]) == 2


def test_channel_footbridges_plank_each_long_ditch_perpendicular():
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 280], [50, 280]]}]  # paddy straddling the y=200 ditch (both banks cultivated)
    s.M["field_ditches"] = [
        {"poly": [[100, 200], [400, 200], [800, 200]], "w": 5, "role": "main"},  # 700px, 2 segments -> two planks at spacing 320
        {"poly": [[100, 400], [160, 400]], "w": 4, "role": "branch"},  # 60px -> below min_len, no plank
    ]
    n = s.channel_footbridges(spacing=320)
    assert n == 2 and len(s.M["bridges"]) == 2  # the short stub is stepped over, not bridged
    assert all(abs(abs(b["rot"]) - 90) < 1 for b in s.M["bridges"])  # deck runs N-S, ACROSS the E-W ditch
    assert all(190 < b["y"] < 210 for b in s.M["bridges"])  # both sit ON the ditch line


def test_channel_footbridges_slides_a_plank_clear_of_a_farmhouse():
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 220], [750, 220], [750, 380], [50, 380]]}]  # paddy straddling the y=300 ditch
    s.M["field_ditches"] = [{"poly": [[100, 300], [700, 300]], "w": 5, "role": "main"}]  # 600px E-W ditch
    s.M["houses"] = [{"x": 400, "y": 300, "w": 60, "h": 40, "kind": "plain", "rot": 0}]  # a house ON the ditch midpoint
    n = s.channel_footbridges(spacing=800)  # n=1, midway = (400,300) = on the house
    assert n == 1
    b = s.M["bridges"][0]
    assert not (365 <= b["x"] <= 435) and 190 < b["y"] < 410  # the plank slid ALONG the ditch, off the house footprint


def test_channel_footbridges_skips_a_crossing_to_uncultivated_ground():
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [750, 120], [750, 297], [50, 297]]}]  # paddy only NORTH of the ditch; the S bank is marsh/scrub
    s.M["field_ditches"] = [{"poly": [[100, 300], [700, 300]], "w": 5, "role": "main"}]  # a margin ditch: field one side, nothing the other
    n = s.channel_footbridges(spacing=800)
    assert n == 0 and not s.M["bridges"]  # no cultivated ground on the far bank -> no useful crossing -> no plank


# ---- city_wall: a mural tower BOXED IN on both sides is dropped ----------------------------


def test_inwall_drain_outfall_trims_gates_and_records_the_conduit():
    """The in-wall drain handoff (GM 2026-07-23): the drain polyline is trimmed back to half the
    ring-road width + 10px clear of the ring centerline, a sluice gate sits across the cut, and
    an UNDRAWN drain->moat conduit starts exactly at the cut (inwall_drains_gated_at_cutoff)."""
    s = _inwall_settlement()
    out = s.inwall_drain_outfall([(500, 300), (300, 150), (150, 110)])  # moat-side end LAST, ends 10px off the ring's top segment
    cut = out[-1]
    ringd = min(settlement.seg_dist(cut[0], cut[1], a, b) for a, b in [((100, 100), (900, 100)), ((100, 100), (100, 900))])
    assert ringd >= 13.9  # 8/2 + 10 clear of the centerline
    assert len(out) < 3 or out[:2] == [(500.0, 300.0), (300.0, 150.0)]  # only the tail was touched
    g = s.M["sluice_gates"][-1]
    assert math.hypot(g["x"] - cut[0], g["y"] - cut[1]) < 1.5  # the gate sits AT the cut
    c = s.M["channels"][-1]
    assert c["frm"] == {"kind": "drain"} and c["to"] == {"kind": "moat"} and c["drawn"] is False
    assert c["poly"][0] == [round(cut[0], 1), round(cut[1], 1)]  # the conduit starts at the cut


def test_navigable_canal_is_level_and_carries_no_bearing():
    s = _town()
    s.canal([(100, 100), (400, 100)])
    rec = s.M["canals"][0]
    assert rec["flow"] == "level" and rec["flow_deg"] is None


def test_moat_flow_declares_a_closed_ring_circulation():
    s = _town()
    s.moat_flow((120.44, 200.51), (800.0, 640.0))
    assert s.M["moat_flow"] == {"inlet": [120.4, 200.5], "outlet": [800.0, 640.0]}


def test_towpath_reserves_its_ground():
    s = _cap020()
    n_corr = len(s.corridors)
    s.towpath([(100, 1300), (700, 800)])
    assert len(s.corridors) == n_corr + 1  # later packs keep off the bank


def test_aqueduct_records_intake_channel_and_terminus():
    s = _cap020()
    s.aqueduct([(1300, 200), (900, 150), (500, 120)])
    assert isinstance(s.M["aqueducts"], list) and len(s.M["aqueducts"]) == 1
    rec = s.M["aqueducts"][0]
    assert rec["poly"][0] == [1300, 200] and rec["intake"] == [1300, 200]
    assert rec["to"] == [500, 120]
    assert rec["w"] > 0


def test_a_footplank_is_never_laid_across_the_hem_crop():
    """THE RATCHET for the 2026-08-11 slide condition. A plank slides clear of houses and of banks
    that open onto marsh; it must also slide clear of the DRY hem, because a deck laid on a hatake
    strip is a board lying on the barley - the same rule `groves_clear_of_dry_plots` states for trees
    and `structures_clear_of_dry_plots` for buildings."""
    s = _plank_bed()
    hem = [(560.0, 660.0), (840.0, 660.0), (840.0, 740.0), (560.0, 740.0)]  # straddles the ditch mid-run
    s.M["dry_plots"].append({"poly": [list(p) for p in hem], "crop": "barley", "theta": 0.0})
    s.dry_polys.append(hem)
    s.channel_footbridges(spacing=300)
    assert s.M["bridges"], "the fixture must actually place planks, or it proves nothing"
    for b in s.M["bridges"]:
        assert not (560.0 <= b["x"] <= 840.0 and 660.0 <= b["y"] <= 740.0), f"a plank was laid on the hem at {(round(b['x']), round(b['y']))}"


def test_a_footplank_is_never_laid_on_a_bend_its_deck_cannot_clear():
    """THE RATCHET for the corner test. `bridges_span_their_water` requires every deck CORNER to
    stand clear of the crossed water; a deck perpendicular to a STRAIGHT ditch clears by
    construction, and one at a BEND does not, because the polyline curves back toward a corner."""
    s = _plank_bed(bend=True)
    s.channel_footbridges(spacing=300)
    assert s.M["bridges"], "the fixture must actually place planks, or it proves nothing"
    for b in s.M["bridges"]:
        th = math.radians(b["rot"])
        ux, uy = math.cos(th), math.sin(th)
        for su, sv in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            cx = b["x"] + su * ux * b["span"] / 2 - sv * uy * b["w"] / 2
            cy = b["y"] + su * uy * b["span"] / 2 + sv * ux * b["w"] / 2
            gap = min(seg_dist(cx, cy, tuple(d["poly"][i]), tuple(d["poly"][i + 1])) for d in s.M["field_ditches"] for i in range(len(d["poly"]) - 1))
            assert gap >= 4.0 / 2 + 2.0, f"deck corner {round(gap, 1)}px from its own ditch - the abutment stands in the water"


# ---- feature 113: the composed CityMixin surface ------------------------------------------------
# The guard for the settlement/city.py -> settlement/city/ package split. See
# specs/113-city-package/contracts/mixin-surface.md for the contract and its red proof.

_CITY_SURFACE = frozenset(
    {
        # public entry points, called from pool gens, wip/, hamletgen, other engine modules and checks
        "aqueduct",
        "bridge",
        "bridges",
        "canal",
        "channel_footbridges",
        "city_wall",
        "dock",
        "farmland_ring",
        "governor_mansion",
        "inwall_drain_outfall",
        "jetty",
        "log_boom",
        "moat",
        "moat_flow",
        "quay",
        "ring_road",
        "sluice_gate",
        "towpath",
        "water_gate",
        # private helpers, reached through self. Two of these (_tower,
        # _plank_reaches_useful_ground) have no external consumer at all - they stay in the
        # surface precisely because a name nothing calls is the kind a careless partition drops
        # without any other test noticing.
        "_gapped_ring",
        "_plank_reaches_useful_ground",
        "_ring_upslope",
        "_tower",
        "_wall_arc_of",
        "_wall_perimeter",
        "_wall_point_at_arc",
        "_wall_walk",
    }
)


def _city_submixins():
    # Derived from the MRO rather than by importing the submodules, so this guard runs UNCHANGED
    # before and after the split: pre-split the list is empty (CityMixin is the single class and
    # assertion 2 is vacuous), post-split it is the six sub-mixins. Importing
    # settlement.city.walls et al. directly - the shape feature 112 used - cannot be written
    # before the package it imports from exists, which is what made 112's own red proof for
    # assertion 2 impossible to run in the order its task list implied.
    from l7r.diagram.settlement.city import CityMixin

    return [c for c in CityMixin.__mro__ if c is not CityMixin and c is not object]


def _own_callables(cls):
    return {k for k, v in vars(cls).items() if callable(v) or isinstance(v, staticmethod)}


def test_no_two_city_submixins_define_the_same_name():
    subs = _city_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _own_callables(a) & _own_callables(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"

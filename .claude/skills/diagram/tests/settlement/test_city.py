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
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
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


def test_channel_footbridges_lay_every_crossing_in_the_settlement_s_rolled_form():
    """269 B21 (research/water/290): a settlement's ditch crossings all take one form - a single log, logs under earth,
    or a planked deck - declared in meta and on each deck; the form changes the glyph, never the deck's box."""
    boxes = {}
    for form in settlement.city.bridges.FOOTBRIDGE_FORMS:
        s = _crop_settlement()
        s.pin_knob("footbridge_form", form)
        s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 280], [50, 280]]}]
        s.M["field_ditches"] = [{"poly": [[100, 200], [400, 200], [800, 200]], "w": 5, "role": "main"}]
        assert s.channel_footbridges(spacing=320) == 2
        assert s.M["meta"]["footbridge_form"] == form and all(b["form"] == form for b in s.M["bridges"])
        boxes[form] = [(b["x"], b["y"], b["rot"], b["span"], b["w"]) for b in s.M["bridges"]]
    assert boxes["log"] == boxes["earthen"] == boxes["plank"]
    glyphs = {f: settlement.city.bridges.deck_glyph(0, 0, 90, 20, 2, f) for f in settlement.city.bridges.FOOTBRIDGE_FORMS}
    assert 'rx="0.7"' in glyphs["log"] and "#BFA274" in glyphs["earthen"] and 'height="2.6"' in glyphs["plank"]
    assert len(set(glyphs.values())) == 3


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


# ---- SIDE-AWARE plank caps: `seg_caps` (feature 146 - the arm no live map takes) ------------


def test_channel_footbridges_honors_a_per_side_plank_cap():
    """`seg_caps` maps a ring-canal's `seg` tag to how many planks that side may carry (research
    2026-07-22: crossings cluster on the settled toe and are absent on the feeder and the drain,
    because workers cross to the fields they live beside). A cap of 0 means NO plank on that side -
    the polder gens set it, but no map in the pool rolls a ditch tagged with a zero-capped seg, so
    both the cap lookup and its refusal went unentered."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 280], [50, 280]]}]
    s.M["field_ditches"] = [
        {"poly": [[100, 200], [800, 200]], "w": 5, "role": "main", "seg": "drain"},
        {"poly": [[100, 240], [800, 240]], "w": 5, "role": "main", "seg": "toe"},
    ]
    n = s.channel_footbridges(spacing=320, seg_caps={"drain": 0, "toe": 1})
    assert n == 1, "the drain side is capped to nothing; the toe side takes its single plank"
    assert all(230 < b["y"] < 250 for b in s.M["bridges"]), "the surviving plank is on the toe"


def test_channel_footbridges_refuses_a_plank_whose_deck_would_not_clear_its_water():
    """The last of the three siting guards. `_plank_reaches_useful_ground` and the house-slide both
    have live maps behind them; this one only fires where a ditch bends back under its own deck, so
    the guard is asked directly."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 280], [50, 280]]}]
    s.M["field_ditches"] = [{"poly": [[100, 200], [800, 200]], "w": 5, "role": "main"}]
    s._deck_clears_its_water = lambda *_a, **_k: False  # type: ignore[method-assign]
    assert s.channel_footbridges(spacing=320) == 0
    assert not s.M["bridges"], "a deck that stands in its own water is not drawn at all"


# ---- seat_deck: the SKEW fallback, lifted out of bridges() (feature 146) ---------------------


def test_seat_deck_grows_a_square_crossing_and_leaves_its_rotation_alone():
    from l7r.diagram.settlement.city.bridges import seat_deck

    water = [(0.0, 300.0), (1000.0, 300.0)]
    rot, span, seated = seat_deck((500.0, 300.0), 90.0, 30.0, 8.0, water, 12.0, (water[0], water[1]))
    assert seated and rot == 90.0 and span == 30.0, "square to the stream: the first span tried clears"


def test_seat_deck_skews_toward_square_when_growth_cannot_clear_an_oblique_crossing():
    """Growth lengthens the deck ALONG THE WAY, which at a shallow crossing drives its ends further along
    the water rather than clear of it - so no ceiling on the growth could ever have worked. Only cohort
    seed 47 ever rolled a map that reached this."""
    from l7r.diagram.settlement.city.bridges import seat_deck

    water = [(0.0, 300.0), (1000.0, 300.0)]
    rot, span, seated = seat_deck((500.0, 300.0), 20.0, 30.0, 8.0, water, 12.0, (water[0], water[1]))
    assert seated
    assert rot != 20.0 and abs(rot - 20.0) <= 8.0, "skewed toward square, inside BRIDGE_ROT_TOL"
    assert span > 30.0, "and grown at the skewed heading"


def test_seat_deck_hands_back_the_original_span_when_nothing_seats():
    """An undersized deck the caller draws anyway, so `bridges_span_their_water` names it - better than a
    silent no-bridge at a crossing the road plainly makes."""
    from l7r.diagram.settlement.city.bridges import seat_deck

    water = [(0.0, 300.0), (1000.0, 300.0)]
    rot, span, seated = seat_deck((500.0, 300.0), 12.0, 30.0, 8.0, water, 12.0, (water[0], water[1]))
    assert not seated and (rot, span) == (12.0, 30.0)


def test_two_ways_crossing_one_ditch_side_by_side_share_the_plank():
    """ONE DECK PER CROSSING PLACE. A real crossing is a place, not a per-way entitlement: two tracks
    converging on the same plank use the plank. Feature 126 shipped overlapping decks on four cohort
    seeds once the lane work began drawing orphan links alongside existing ways."""
    s = _crop_settlement()
    s.M["streams"] = [{"poly": [[100, 300], [900, 300]], "w": 10}]
    s.M["lanes"] = [
        {"pts": [[500, 100], [500, 500]], "w": 6},
        {"pts": [[510, 100], [510, 500]], "w": 6},  # a second track 10 px along the same bank, inside the deck it would build
    ]
    n = s.bridges()
    assert n == 1 and len(s.M["bridges"]) == 1, "the second way uses the deck that is already there"


def test_a_footplank_is_not_laid_on_top_of_another_deck():
    """Three siting guards keep a plank off ground that is spoken for - a farmhouse, the hem crop, and
    another DECK. The last is reached only where two ditches cross near enough for their planks to collide,
    which is an accident of the roll rather than something the pool maps reliably contain."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 480], [50, 480]]}]
    s.M["field_ditches"] = [{"poly": [[100, 300], [800, 300]], "w": 5, "role": "main"}]
    alone = s.channel_footbridges(spacing=320)
    assert alone >= 1, "the ditch takes its planks when nothing is in the way"

    s2 = _crop_settlement()
    s2.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 480], [50, 480]]}]
    s2.M["field_ditches"] = [{"poly": [[100, 300], [800, 300]], "w": 5, "role": "main"}]
    for b in s.M["bridges"]:  # every deck the first map laid, already standing before this pass runs
        s2.bridge(b["x"], b["y"], b["rot"], b["span"], b["w"])
    before = [dict(b) for b in s2.M["bridges"]]
    s2.channel_footbridges(spacing=320)
    # the guard REFUSES the seat; the siter then slides along the ditch looking for another, so the honest
    # claim is not "no plank" but "no plank ON one already there"
    for b in s2.M["bridges"][len(before) :]:
        assert all(math.hypot(b["x"] - a["x"], b["y"] - a["y"]) > 1.0 for a in before), "a new plank sits clear of every standing deck"


def test_a_plank_whose_far_bank_is_the_village_reaches_useful_ground():
    """`_plank_reaches_useful_ground`: a bank a dwelling stands within a short reach of is the village - useful ground,
    as the field on the other bank is - so the plank is sited; a bank onto nothing is refused."""
    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[0, 0], [400, 0], [400, 190], [0, 190]]}]
    s.M["houses"] = [{"x": 200, "y": 225, "w": 40, "h": 24}]
    assert s._plank_reaches_useful_ground(200.0, 200.0, 90.0, 12.0), "field on one bank, the village on the other"
    s.M["houses"] = []
    assert not s._plank_reaches_useful_ground(200.0, 200.0, 90.0, 12.0), "a far bank onto nothing"


def test_the_footbridge_widening_from_its_segment_index_equals_the_scan() -> None:
    """Feature 278 (FR-003): the widening asks an index of the other watercourses' segments instead of testing every
    segment per deck candidate. Over random decks and courses - its own course among them, skipped by identity - the
    indexed widening equals the scan it replaced, restated here as it stood."""
    import random

    from l7r.diagram.settlement._geom import quad_hits_seg
    from l7r.diagram.settlement.city.bridges import water_segment_index

    def scan(s, quad, deck, own, water, span, plank_w):
        dux, duy = math.cos(math.radians(deck)), math.sin(math.radians(deck))
        under = []
        for wl, ow in water:
            if wl is own:
                continue
            for i2 in range(len(wl) - 1):
                if not quad_hits_seg(quad, tuple(wl[i2]), tuple(wl[i2 + 1]), 3.0):
                    continue
                wx, wy = wl[i2 + 1][0] - wl[i2][0], wl[i2 + 1][1] - wl[i2][1]
                w = math.hypot(wx, wy) or 1.0
                sin, cos = abs(dux * wy / w - duy * wx / w), abs(dux * wx / w + duy * wy / w)
                under.append((ow + 2.0 * (2.0 / s.ftpx) + plank_w * cos) / max(sin, 0.02) + 1.0)
        return max([span] + under)

    s = Settlement(900, 900, seed=1)
    s.meta(name="B", scale="hamlet", ftpx=1, toscale=True)
    rng = random.Random(278)
    water = []
    for _ in range(40):
        x, y = rng.uniform(0, 900), rng.uniform(0, 900)
        water.append(([(x + k * rng.uniform(-40, 40), y + k * rng.uniform(-40, 40)) for k in range(rng.randint(2, 6))], rng.uniform(2, 9)))
    idx = water_segment_index(water)
    widened = 0
    for _ in range(600):
        cx, cy, deck = rng.uniform(0, 900), rng.uniform(0, 900), rng.uniform(0, 180)
        dx, dy = math.cos(math.radians(deck)) * 12, math.sin(math.radians(deck)) * 12
        nx, ny = -dy / 4, dx / 4
        quad = [(cx - dx - nx, cy - dy - ny), (cx + dx - nx, cy + dy - ny), (cx + dx + nx, cy + dy + ny), (cx - dx + nx, cy - dy + ny)]
        own = water[rng.randrange(len(water))][0]
        want = scan(s, quad, deck, own, water, 20.0, 5.0)
        assert s._widen_for_confluence(quad, deck, own, water, 20.0, 5.0, idx) == want
        assert s._widen_for_confluence(quad, deck, own, water, 20.0, 5.0) == want
        widened += want > 20.0
    assert 20 < widened < 580, "non-vacuity: decks both over and clear of other water"


# ---- feature 287: the decks and planks guaranteed where they are laid (ways W02, W12-W15) -----------------------------


def test_a_crossing_is_decked_unless_a_standing_deck_covers_it() -> None:
    """Ways W02: `bridges()` skipped a crossing lying within half the NEW deck's span of a standing one, which left a
    crossing 12 ft along the brook from a deck that did not reach it unbridged. The skip is `deck_covers` now, and a deck
    that would stand on the first is merged into it (re-seated to reach both), so every crossing is covered."""
    from l7r.diagram.settlement.city.bridges import deck_covers

    s = _crop_settlement()
    s.M["streams"] = [{"poly": [[100, 300], [900, 300]], "w": 10}]
    s.bridge(500.0, 300.0, 90.0, 6.0, 6.0)  # a short deck already standing at x=500
    s.M["lanes"] = [{"pts": [[512, 100], [512, 500]], "w": 6}]  # a crossing 12 ft along from it, beyond its 6 ft span
    s.bridges()
    assert any(deck_covers(b, 512.0, 300.0) for b in s.M["bridges"]), "the second crossing is decked"
    assert deck_covers({"x": 0, "y": 0}, 19.0, 0.0) and not deck_covers({"x": 0, "y": 0, "span": 5}, 6.0, 0.0)
    far = _crop_settlement()
    far.M["streams"] = [{"poly": [[100, 300], [900, 300]], "w": 10}]
    far.M["lanes"] = [{"pts": [[300, 100], [300, 500]], "w": 6}, {"pts": [[700, 100], [700, 500]], "w": 6}]
    assert far.bridges() == 2, "two crossings far apart take a deck each"


def test_a_deck_is_never_drawn_undersized() -> None:
    """Ways W12 (FR-005): `seat_deck` hands back the original span when nothing seats, and `bridges()` drew it. The web's
    last pass now cuts every such crossing first, so one reaching here is an engine defect - raised, never drawn."""
    import pytest

    from l7r.diagram.settlement.city.bridges import UndeckableCrossing

    s = _crop_settlement()
    s.M["field_ditches"] = [{"poly": [[0.0, 100.0], [400.0, 110.0]], "w": 4.0}]
    s.M["lanes"] = [{"pts": [[0.0, 95.0], [400.0, 118.0]], "w": 3}]  # two degrees off the ditch's own line
    with pytest.raises(UndeckableCrossing):
        s.bridges()


def test_a_carried_deck_lands_off_the_rice_or_takes_the_footplanks_form() -> None:
    """Ways W13 (R3, the field path's canal deck 7 ft onto the paddy): a deck whose corner stands in a flooded plot is
    tried again in the footplank's form (the local width and the short abutment); failing that it is not seated."""
    from l7r.diagram.settlement import point_in_poly
    from l7r.diagram.settlement.city.bridges import _deck_quad, crossing_deck, flooded_ground

    ditch = [(0.0, 100.0), (400.0, 100.0)]
    rice = [[-50.0, 106.0], [450.0, 106.0], [450.0, 400.0], [-50.0, 400.0]]  # the rice 6 ft past the ditch's line
    wet = flooded_ground({"fields": [{"plot_rings": [rice], "outline": rice}, {"plot_rings": [[[0, 0], [1, 1]]]}]})
    p, rot, span, seated = crossing_deck((200.0, 0.0), (200.0, 300.0), 3.0, ditch[0], ditch[1], 4.0, ditch, 1.0, wet)
    assert seated and not any(point_in_poly(x, y, rice) for x, y in _deck_quad(p[0], p[1], span, 3.0, rot))
    assert crossing_deck((200.0, 0.0), (200.0, 300.0), 3.0, ditch[0], ditch[1], 4.0, ditch, 1.0)[2] > span, "the carried form, where nothing is wet"
    drowned = [[[-50.0, 101.0], [450.0, 101.0], [450.0, 400.0], [-50.0, 400.0]]]
    assert not crossing_deck((200.0, 0.0), (200.0, 300.0), 3.0, ditch[0], ditch[1], 4.0, ditch, 1.0, drowned)[3], "no dry landing at all"


def test_a_plank_is_laid_on_a_supply_ditch_only() -> None:
    """Ways W14: a plank on the collector, the drain or the feeder is never laid (`SUPPLY_ROLES`: a main, a branch, a
    lateral - research/ways/030 and archetypes/110), and a seat whose nearest ditch is a drain (a junction) is refused."""
    from l7r.diagram.settlement.city.bridges import plank_ditch, plank_on_supply

    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 480], [50, 480]]}]
    s.M["field_ditches"] = [
        {"poly": [[100, 200], [800, 200]], "w": 5, "role": "drain"},
        {"poly": [[100, 300], [800, 300]], "w": 5, "role": "lateral"},
    ]
    s.channel_footbridges(spacing=320)
    assert s.M["bridges"] and all(290 < b["y"] < 310 for b in s.M["bridges"]), "the lateral takes planks; the drain none"
    assert plank_on_supply((400.0, 300.0), s.M["field_ditches"]) and not plank_on_supply((400.0, 201.0), s.M["field_ditches"])
    assert plank_ditch((0.0, 0.0), [{"poly": [[1, 1]]}]) == (math.inf, None)
    junction = _crop_settlement()
    junction.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 480], [50, 480]]}]
    # the collector recorded first along the main's own line: every seat's nearest recorded ditch is the collector
    junction.M["field_ditches"] = [{"poly": [[100, 300], [800, 300]], "w": 5, "role": "collector"}, {"poly": [[100, 300], [800, 300]], "w": 5, "role": "main"}]
    junction.channel_footbridges(spacing=320)
    assert not junction.M.get("bridges"), "no seat whose nearest ditch is the collector"


def test_a_plank_stands_only_on_water_that_earns_one() -> None:
    """Ways W15: the width was a PREFERENCE (narrow seats sorted last, still laid), kept because a retired gate demanded a
    plank per long ditch; it is a hard filter now - a ditch whose wide seats are all blocked carries no plank."""
    from l7r.diagram.waterfields import taper_w, worth_planking

    s = _crop_settlement()
    s.M["fields"] = [{"outline": [[50, 120], [850, 120], [850, 480], [50, 480]]}]
    s.M["field_ditches"] = [{"poly": [[100, 300], [800, 300]], "w": 6.0, "w_tail": 0.5, "role": "branch"}]  # it tapers to nothing
    s.M["houses"] = [{"x": 250, "y": 300, "w": 330, "h": 60, "rot": 0}]  # a house over the whole wide head
    s.channel_footbridges(spacing=900)
    for b in s.M.get("bridges") or []:
        lw = taper_w(6.0, 0.5, (b["x"] - 100.0) / 700.0)
        assert worth_planking(lw, lw, 1.0), "every plank stands on water that earns one"


def test_a_merged_deck_is_redrawn_to_reach_both_crossings() -> None:
    s = _crop_settlement()
    s.bridge(500.0, 300.0, 90.0, 6.0, 6.0)
    deck = s.M["bridges"][0]
    s._reseat_to_cover(deck, (500.0, 320.0))
    assert deck["span"] == 42.0 and 'width="42.0"' in s.top[int(deck["z"]) - s.TOPZ]


def test_a_village_cuts_its_lanes_where_no_deck_seats_before_it_lays_its_decks() -> None:
    """Feature 287 (ways W12): `roll_village` has no web settle, and `bridges()` raises on a crossing no deck seats. So the
    village cuts its lanes by the same predicate first (`undeckable_at`): the crossing and a bank's width either side come
    out, the pieces stand, a lane with nothing left goes, and `bridges()` then decks what remains."""
    from l7r.diagram.settlement.city.bridges import cut_at, undeckable_at

    s = _crop_settlement()
    s.M["field_ditches"] = [{"poly": [[0.0, 100.0], [400.0, 110.0]], "w": 4.0}]
    grazing = [[0.0, 95.0], [400.0, 118.0]]  # two degrees off the ditch's own line: no deck seats
    square = [[200.0, 0.0], [200.0, 300.0]]  # square over it: a deck seats
    for pts in (grazing, square, [[105.0, 102.55], [108.0, 102.72]]):  # the last is all crossing: nothing of it is left
        s.lane(pts, width=3)
    waters = [([[0.0, 100.0], [400.0, 110.0]], 4.0)]
    assert undeckable_at([(0.0, 95.0), (400.0, 118.0)], 3.0, waters) and not undeckable_at([(200.0, 0.0), (200.0, 300.0)], 3.0, waters)
    assert s.cut_undeckable_lanes() >= 1
    assert all(not undeckable_at([(float(x), float(y)) for x, y in ln["pts"]], 3.0, waters) for ln in s.M["lanes"])
    assert s.bridges() >= 1, "the square crossing is decked; nothing raises"
    assert cut_at([(0.0, 0.0), (100.0, 0.0)], 0, (50.0, 0.0), 10.0) == [[(0.0, 0.0), (40.0, 0.0)], [(60.0, 0.0), (100.0, 0.0)]]
    assert cut_at([(0.0, 0.0), (10.0, 0.0), (100.0, 0.0)], 0, (5.0, 0.0), 10.0) == [[(15.0, 0.0), (100.0, 0.0)]], "a head with no length goes; the cut runs on past a vertex"
    assert cut_at([(0.0, 0.0), (0.0, 0.0)], 0, (0.0, 0.0), 1.0) == []

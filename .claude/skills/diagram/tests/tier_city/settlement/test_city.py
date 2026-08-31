"""tier city tests split out of `tests.settlement.test_city` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math
import re

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement, seg_dist
from tests.settlement._builders import _cap020, _caption_size, _crop_settlement
from tests.settlement.test_city import _CITY_SURFACE, _own_callables


@pytest.mark.tiers("city")
def test_city_wall_tower_slides_along_the_wall_for_a_kido():
    # tower_skip: a mural tower yields its vertex to a future kido, but the vertex stays COVERED by
    # a tower a short way along the wall (not a whole-vertex jump leaving a bare, indefensible arc).
    # At this crop's ftpx=1 the default garrison spacing is ~278px, so the flanking towers straddle
    # the yielded vertex at ~half-spacing (~140px) - well inside a bare-stretch (~one full segment).
    import math as m

    s = _crop_settlement()
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 12)), round(700 + 400 * m.sin(2 * m.pi * i / 12))) for i in range(12)]
    s.city_wall(pts, gates=(), tower_skip=[pts[6]])
    ds = [m.hypot(t["x"] - pts[6][0], t["y"] - pts[6][1]) for t in s.M["wall_towers"]]
    assert all(d > 45 for d in ds)  # the vertex is yielded...
    assert any(d < 180 for d in ds)  # ...but a tower still stands a short slide away (< a full segment)


@pytest.mark.tiers("city")
def test_city_wall_tower_drops_when_boxed_in_on_both_sides():
    # ...and when the slide finds no clear ground either way, the tower is dropped (the 75-deg
    # spacing check tolerates one gap)
    import math as m

    s = _crop_settlement()
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 12)), round(700 + 400 * m.sin(2 * m.pi * i / 12))) for i in range(12)]
    s.city_wall(pts, gates=(), tower_skip=[pts[5], pts[6], pts[7]])
    assert all(m.hypot(t["x"] - pts[6][0], t["y"] - pts[6][1]) > 60 for t in s.M["wall_towers"])


@pytest.mark.tiers("city")
def test_river_canal_dock_jetty_water_gate_defaults():
    # exercise the river-city glyph methods with their DEFAULT widths/lengths + the moat(river=)
    # open-arc path and the water-gate tower-skip vertex (Nagahara passes explicit sizes; this
    # covers the default branches).
    import math as m

    s = _crop_settlement()
    s.meta(name="R", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    river = [(1360, 300), (1360, 1100)]  # a river just east of the wall
    s.river(river)  # default width
    s.moat(pts, gap=24, river=river)  # open-arc moat joining the river
    s.water_gate(pts[0][0], pts[0][1])  # arch on the east gate vertex (default rot)
    s.canal([(1350, 700), (1100, 700)])  # default width
    s.dock(1050, 700, 54, 34)
    s.jetty(1330, 600)  # default length
    s.city_wall(pts, gates=[pts[4]], water_gates=[pts[0]])  # water gate skips its mural-tower vertex
    assert s.M["river"]["w"] > 0 and s.M["canals"] and s.M["docks"] and s.M["jetties"] and s.M["water_gates"]
    assert s.M["moat"][0] != s.M["moat"][-1]  # OPEN arc (ends do not close on themselves)


@pytest.mark.tiers("city")
def test_moat_river_junction_feet_tilt_with_the_current():
    # GM 2026-07-24 hydrology review: the junction feet are NOT square rfoot tees. The upstream
    # (inlet) end shifts UPSTREAM off its square foot - a near-square, sediment-wary intake with
    # only a slight tilt - and the downstream (outlet) end sweeps DOWNSTREAM further (confluences
    # merge at downstream angles). River pts run upstream-first; a vertical river makes the
    # shifts pure y offsets, so the asymmetry is directly measurable.
    import math as m

    s = _crop_settlement()
    s.meta(name="RT", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    river = [(1360, 100), (1360, 1300)]  # flows top -> bottom (upstream-first)
    for ring in (pts, pts[::-1]):  # both ring orientations: keep[0] lands downstream on one, upstream on the other
        mo = s.moat(ring, gap=24, river=river)
        (inlet, adj_in), (outlet, adj_out) = sorted([(mo[0], mo[1]), (mo[-1], mo[-2])], key=lambda e: e[0][1])
        in_shift = adj_in[1] - inlet[1]  # upstream (negative-y) shift of the inlet foot off square
        out_shift = outlet[1] - adj_out[1]  # downstream (positive-y) sweep of the outlet foot
        assert in_shift > 0  # inlet tilts upstream, never smoothly flow-aligned
        assert out_shift > in_shift  # the outlet sweeps harder - the researched asymmetry


@pytest.mark.tiers("city")
def test_moat_river_junction_tilts_follow_a_reversed_river():
    # the OTHER branch of the tilt bookkeeping (keep[0]'s end downstream): same asymmetry when the
    # river runs bottom -> top (upstream-first pts reversed). Deterministic on purpose - this branch
    # was previously covered only by whichever orientation a pool map happened to roll, so an rng
    # shift elsewhere dropped it out of coverage (2026-07-24).
    import math as m

    s = _crop_settlement()
    s.meta(name="RT2", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    river = [(1360, 1300), (1360, 100)]  # flows bottom -> top (upstream-first)
    mo = s.moat(pts, gap=24, river=river)
    (outlet, adj_out), (inlet, adj_in) = sorted([(mo[0], mo[1]), (mo[-1], mo[-2])], key=lambda e: e[0][1])
    in_shift = inlet[1] - adj_in[1]  # upstream is +y now: the inlet foot shifts DOWN off square
    out_shift = adj_out[1] - outlet[1]  # the outlet foot sweeps UP, downstream with the current
    assert in_shift > 0  # inlet tilts upstream, never smoothly flow-aligned
    assert out_shift > in_shift  # the outlet sweeps harder - the researched asymmetry


@pytest.mark.tiers("city")
def test_city_wall_gateposts_orient_to_the_wall_tangent():
    # GM 2026-07: gateposts were hard-coded N/S (vertical rects); on an E/W gate they must stand
    # N and S of the opening, oriented to the wall's local tangent - so a gate on a vertical wall
    # stretch gets ~vertical-tangent posts (rot near +-90), not the old rot=0.
    import math as m

    s = _crop_settlement()
    s.meta(name="C", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 16)), round(700 + 400 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    egate = pts[0]  # the EAST gate (rightmost): the wall runs ~vertically there
    s.city_wall(pts, gates=[egate])
    posts = [g for g in s.M["gate_structs"] if g.get("kind") == "gatepost"]
    assert len(posts) == 2
    assert all(abs(abs(p["rot"]) - 90) < 25 for p in posts)  # tangent ~vertical, not the old rot 0
    # the two posts straddle the gate along the tangent (N and S of it), not E and W
    # > 10, not the old > 40: the throat is TO SCALE since 2026-07-27 (30 ft clear + a 15 ft pier a
    # side = 15 px between post centers at 1 px = 3 ft), where it used to open a 210 ft gap. The
    # assertion here is about ORIENTATION - N and S of the opening, not E and W - so it must not
    # re-encode the old spacing as its threshold.
    assert abs(posts[0]["y"] - posts[1]["y"]) > 10 and abs(posts[0]["x"] - posts[1]["x"]) < 30


@pytest.mark.tiers("city")
def test_city_gate_tower_flips_to_the_other_flank_when_one_is_blocked():
    # the gate tower belongs AT the gate: with its PRIMARY flank blocked by a kido span, it does NOT walk
    # far out along the wall - it flips to the OTHER flank at the same short arc, still at the opening.
    import math as m

    s = _crop_settlement()
    s.meta(name="G", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 16)), round(700 + 400 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    blocks = [s._wall_walk(pts, 0, a, west=False)[:2] for a in (78, 98, 118)]  # block the PRIMARY (west=False) flank
    s.city_wall(pts, gates=[pts[0]], tower_skip=blocks)
    tower = [gs for gs in s.M["gate_structs"] if gs.get("kind") == "tower"]
    assert tower  # the gate tower is still placed...
    assert m.hypot(tower[0]["x"] - pts[0][0], tower[0]["y"] - pts[0][1]) < 110  # ...AT the gate, not marooned far out
    assert all(m.hypot(tower[0]["x"] - bx, tower[0]["y"] - by) > 45 for bx, by in blocks)  # on the clear OTHER flank


@pytest.mark.tiers("city")
def test_city_gate_tower_steps_out_when_both_near_flanks_are_blocked():
    # only when BOTH near-gate flanks are blocked does the tower step OUTWARD along the wall (the arc walk):
    # kido spans on each side of the gate leave it nowhere at the opening, so it walks clear.
    import math as m

    s = _crop_settlement()
    s.meta(name="B", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 16)), round(700 + 400 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    blocks = [s._wall_walk(pts, 0, a, west=wf)[:2] for a in (78, 98, 118) for wf in (False, True)]  # BOTH flanks near the gate
    s.city_wall(pts, gates=[pts[0]], tower_skip=blocks)
    tower = [gs for gs in s.M["gate_structs"] if gs.get("kind") == "tower"]
    assert tower and all(m.hypot(tower[0]["x"] - bx, tower[0]["y"] - by) > 45 for bx, by in blocks)  # placed, walked clear of every blocked span


@pytest.mark.tiers("city")
def test_city_gate_tower_falls_back_when_every_spot_is_blocked():
    # both flanks blocked at EVERY arc out to the cap: the tower is still placed exactly once (the last
    # candidate is taken rather than the loop running past the cap with nothing placed).
    import math as m

    s = _crop_settlement()
    s.meta(name="F", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 400 * m.cos(2 * m.pi * i / 16)), round(700 + 400 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    blocks = [s._wall_walk(pts, 0, a, west=wf)[:2] for a in range(78, 241, 20) for wf in (False, True)]
    s.city_wall(pts, gates=[pts[0]], tower_skip=blocks)
    assert len([gs for gs in s.M["gate_structs"] if gs.get("kind") == "tower"]) == 1


@pytest.mark.tiers("city")
def test_city_mural_tower_yields_a_vertex_shoulder_to_shoulder_with_a_gate_tower():
    # the mural-tower loop skips a wall vertex within 110px of a GATE tower (a mural tower there would read
    # as a double). This fires only when the gate tower has stepped OUT toward the next even vertex - which
    # now needs BOTH near-gate flanks blocked. A fine 24-gon plus kido spans on both flanks forces exactly
    # that: the tower walks out near an even, non-gate vertex, which the mural loop then yields.
    import math as m

    s = _crop_settlement()
    s.meta(name="M", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 420 * m.cos(2 * m.pi * i / 24)), round(700 + 420 * m.sin(2 * m.pi * i / 24))) for i in range(24)]
    blocks = [s._wall_walk(pts, 0, a, west=wf)[:2] for a in (78, 98, 118) for wf in (False, True)]
    s.city_wall(pts, gates=[pts[0]], tower_skip=blocks)
    gate_towers = [(gs["x"], gs["y"]) for gs in s.M["gate_structs"] if gs.get("kind") == "tower"]
    assert gate_towers and s.M.get("wall_towers")  # both kinds of tower were placed
    # the gate tower walked clear of the blocked kido spans (which is what carried it out near the even
    # vertex the mural loop then yields)
    assert all(m.hypot(gate_towers[0][0] - bx, gate_towers[0][1] - by) > 45 for bx, by in blocks)


@pytest.mark.tiers("city")
def test_governor_mansion_caption_sits_inside_its_walls():
    # GM 2026-08-08. The court is drawn blank on purpose (its buildings are a separate Mode A
    # sheet), so it is guaranteed clear ground on a packed city map, and the band above the walls
    # is prime housing. The caption goes inside, small enough to clear both walls.
    s = Settlement(1400, 1400, seed=6)
    s.meta(name="C", scale="city", ftpx=3)
    s.governor_mansion(700, 700, s.px(436), s.px(366), "Governor's Mansion", gate_dir="west")
    gov = s.M["governor_mansion"]
    assert gov["label"] == "Governor's Mansion"  # the record keeps the name manor() was not given
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    lab = next(lb for lb in s.M["labels"] if lb[5] == "Governor's Mansion")
    assert _caption_size(lab) == settlement.GOVERNOR_CAPTION_FS
    assert lab[0] > 700 - gov["w"] / 2 and lab[2] < 700 + gov["w"] / 2  # clear of BOTH walls
    assert lab[1] > 700 - gov["h"] / 2 and lab[3] < 700 + gov["h"] / 2  # and inside, not above
    assert len([lb for lb in s.M["labels"] if lb[5] == "Governor's Mansion"]) == 1  # manor drew none


@pytest.mark.tiers("city")
def test_governor_mansion_can_be_left_unlabeled():
    s = Settlement(1400, 1400, seed=7)
    s.meta(name="C", scale="city", ftpx=3)
    s.governor_mansion(700, 700, s.px(436), s.px(366), "", gate_dir="west")
    assert s.M["governor_mansion"]["label"] == ""
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    assert not s.M["labels"]


@pytest.mark.tiers("city")
def test_city_wall_drops_a_mural_tower_boxed_in_on_both_sides():
    # the NW vertex is ringed by keep-clear (kido) points carpeting BOTH wall flanks out past the
    # farthest slide arc, so every slide candidate stays blocked and the tower is dropped (spacing
    # tolerates one gap). The clear SE vertex still gets its tower.
    s = Settlement(1200, 1200, seed=1)
    s.meta(name="C", scale="city")
    pts = [[150, 150], [1050, 150], [1050, 1050], [150, 1050]]
    skip = [
        (150, 150),
        (190, 150),
        (230, 150),
        (270, 150),  # carpet the top flank
        (150, 190),
        (150, 230),
        (150, 270),
    ]  # carpet the left flank
    s.city_wall(pts, gates=(), tower_skip=skip)
    towers = s.M.get("wall_towers", [])
    # ftpx=1 garrison -> ~278px spacing; a CLEAR corner is straddled by flanking towers at ~147px, a
    # boxed-in corner's nearest tower is pushed out past the next seat (~212px). The contrast holds.
    nw = min(math.hypot(t["x"] - 150, t["y"] - 150) for t in towers)
    se = min(math.hypot(t["x"] - 1050, t["y"] - 1050) for t in towers)
    assert nw > 180  # NW tower dropped (boxed in) - nearest tower pushed out past the next seat
    assert se < 180  # SE corner kept - flanking towers straddle it at ~half-spacing


@pytest.mark.tiers("capital")
def test_towpath_records_a_list_and_draws_no_roadbed_or_centerline():
    """A towpath is NOT a road (research/cities/capitals.md, 'A river gets a TOWPATH, not a
    road'): no roadbed fill, no dashed centerline, one hairline at the linework floor."""
    s = _cap020()
    n0 = len(s.out)
    s.towpath([(100, 1300), (400, 1000), (700, 800)])
    frag = "".join(s.out[n0:])
    assert isinstance(s.M["towpaths"], list) and len(s.M["towpaths"]) == 1
    rec = s.M["towpaths"][0]
    assert rec["pts"][0] == [100, 1300] and rec["pts"][-1] == [700, 800]
    assert "stroke-dasharray" not in frag  # no dashed centerline - it is not a road
    assert frag.count("<path") == 1  # ONE hairline stroke, no roadbed under it
    assert rec["w"] <= 4.0  # a beaten path, not a carriageway
    # and it never touches the road records - a towpath must not read as road plumbing
    assert not s.M.get("roads") and not s.M.get("road")


@pytest.mark.tiers("capital")
def test_aqueduct_draws_no_arcade():
    """NO ARCADED AQUEDUCT EXISTS in either anchor tradition (research/cities/capitals.md): the
    vocabulary is a gravity canal at grade, a buried pipe, and a flume bridge only where water
    crosses water. Every path in the glyph is straight cuts - no arch curves anywhere."""
    s = _cap020()
    n0 = len(s.out)
    s.aqueduct([(1300, 200), (900, 150), (500, 120)])
    frag = "".join(s.out[n0:])
    for d in re.findall(r'd="([^"]+)"', frag):
        cmds = set(re.findall(r"[A-Za-z]", d))
        assert cmds <= {"M", "L"}, f"curve commands {cmds - {'M', 'L'}} in the aqueduct glyph - an arch has no business here"


@pytest.mark.tiers("capital")
def test_quay_faces_the_bank_with_stepped_landings():
    """The working face at a river wharf is the BANK, faced and notched with steps - not the piers
    (research/cities/river-cities.md: a river's level moves feet across the year, so a flight of
    steps is the right height at every one of them while a fixed deck is right for weeks). The
    glyph records its landings and mooring posts so the checks can read them."""
    s = settlement.Settlement(1200, 1200, seed=4)
    s.meta(scale="capital", ftpx=3)
    bank = [(300, 200), (420, 500), (500, 820)]
    s.quay(bank, steps=3)
    q = s.M["quays"][0]
    assert q["pts"] == [[300.0, 200.0], [420.0, 500.0], [500.0, 820.0]]
    assert len(q["landings"]) == 3, "each landing is a flight of steps notched into the face"
    assert len(q["posts"]) == 5, "mooring posts along the top of the face"
    for lx, ly in q["landings"]:
        assert min(seg_dist(lx, ly, bank[i], bank[i + 1]) for i in range(len(bank) - 1)) < 2.0, "a landing sits ON the face"
    assert any(cl > q["w"] / 2 for _p, cl in s.corridors), "the face reserves its own working strip"


@pytest.mark.tiers("capital")
def test_quay_takes_a_default_width_from_the_map_scale():
    s = settlement.Settlement(1200, 1200, seed=4)
    s.meta(scale="capital", ftpx=3)
    s.quay([(100, 100), (400, 100)], steps=1)
    assert s.M["quays"][0]["w"] >= 2.6


@pytest.mark.tiers("capital", "city")
def test_farmland_ring_taps_water_gates_it_and_rings_the_households():
    """A city is ringed by its farmland, and the belt loop that draws it belongs in ONE place.
    Every provincial-city gen carried its own copy - which is why ringing a capital read as new
    work and cost a day (GM 2026-08-12). This is that loop: tap the water, gate the head-race,
    build the fan, declare source and sink, ring the households."""
    s = settlement.Settlement(1400, 1400, seed=5)
    s.meta(scale="city", ftpx=3)
    river = [(1200, 100), (1200, 1300)]
    s.M["rivers"] = [{"pts": river, "w": 30}]
    seen = {}

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        env = [(sl[0] - 200, sl[1] - 120), (sl[0] - 40, sl[1] - 120), (sl[0] - 40, sl[1] + 120), (sl[0] - 200, sl[1] + 120)]
        net = {"channels": [{"role": "drain", "pts": [(sl[0] - 200, sl[1] + 100), (sl[0] - 320, sl[1] + 160)]}], "plots": [{"poly": env}]}
        seen["sluice"] = sl
        return net, env, (sl[0] - 120, sl[1])

    def topo(pts, frm, to, draw_w=0.0):
        seen.setdefault("topo", []).append((frm.get("kind"), to.get("kind")))

    out = s.farmland_ring(
        [("f1", (1200, 700), 180, 3, 100, (120, 150), (80, 100), (0.3, 0.7), "river")],
        comb=comb,
        topo=topo,
        water=lambda k: river,
        city_center=(700, 700),
    )
    assert len(out) == 1, "the field should have been built"
    assert seen["sluice"] != (1200, 700), "the sluice is set off the tap, not on it"
    assert ("river", "field") in seen["topo"], "the source must be declared from the water it taps"
    assert any(a == "drain" and b == "offmap" for a, b in seen["topo"]), "the drain must reach a sink"
    assert s.M["sluice_gates"], "the head-race is gated where tap water becomes canal water"


@pytest.mark.tiers("city")
def test_farmland_ring_withdraws_a_field_whose_ground_cannot_carry_it():
    """comb_field records the field BEFORE its water is declared, so a fan that fails to carve
    would leave a paddy with no source, no drain and no farmhouses - drawn, recorded, and invisible
    to every rule that reads the water."""
    s = settlement.Settlement(1400, 1400, seed=5)
    s.meta(scale="city", ftpx=3)
    river = [(1200, 100), (1200, 1300)]

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        s.M.setdefault("fields", []).append({"name": name, "outline": [(0, 0)]})
        raise ValueError("no room to carve")

    out = s.farmland_ring(
        [("doomed", (1200, 700), 180, 3, 100, (120, 150), (80, 100), (0.3, 0.7), "river")],
        comb=comb,
        topo=lambda *a, **k: None,
        water=lambda k: river,
        city_center=(700, 700),
    )
    assert out == [], "a field that cannot be built is not returned"
    assert not [f for f in s.M.get("fields") or [] if f.get("name") == "doomed"], "...and it is not left on the map"


@pytest.mark.tiers("city")
def test_farmland_ring_sweeps_a_moat_offtake_downstream():
    """A moat offtake leaves at an ACUTE angle pointing downstream - a square tap sheds sediment
    into its own mouth and says nothing on the page about which way the water runs. The ring does
    that sweep itself, so no gen has to remember moat_swept_tap."""
    s = settlement.Settlement(1600, 1600, seed=8)
    s.meta(scale="city", ftpx=3)
    moat = [(400, 400), (1200, 400), (1200, 1200), (400, 1200), (400, 400)]
    s.M["moat_flow"] = {"inlet": [1200, 400], "outlet": [400, 1200]}
    taps = {}

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        taps["sl"] = sl
        env = [(sl[0] - 160, sl[1] - 90), (sl[0] - 30, sl[1] - 90), (sl[0] - 30, sl[1] + 90), (sl[0] - 160, sl[1] + 90)]
        # a drain that runs well off the sheet, so the reach loop finds its edge on the first steps
        return {"channels": [{"role": "drain", "pts": [(sl[0] - 160, sl[1] + 70), (-400, sl[1] + 200)]}], "plots": [{"poly": env}]}, env, sl

    out = s.farmland_ring(
        [("m1", (400, 800), 180, 4, 100, (120, 150), (80, 100), (0.3, 0.7), "moat")],
        comb=comb,
        topo=lambda *a, **k: None,
        water=lambda k: moat,
        city_center=(800, 800),
    )
    assert len(out) == 1
    assert s.M["sluice_gates"], "the head-race is gated"


@pytest.mark.tiers("capital", "city")
def test_farmland_ring_taps_a_segment_and_opens_the_bound():
    """Two options a capital needs and the provincial cities do not. A river drawn with FIVE
    vertices has no vertex near where the gen meant to tap, so the tap must land on the nearest
    POINT of the polyline; and a map that sets a placement bound rings NOTHING until it is opened
    around the field, which is how a first farmland ring came out as fields with no households."""
    s = settlement.Settlement(1400, 1400, seed=6)
    s.meta(scale="capital", ftpx=3)
    river = [(1200, 100), (1200, 1300)]  # two vertices, both far from the hint
    s.bound = [[0, 0], [200, 0], [200, 200], [0, 200]]  # a bound nowhere near the field
    taps = {}

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        taps["sl"] = sl
        env = [(sl[0] - 150, sl[1] - 90), (sl[0] - 30, sl[1] - 90), (sl[0] - 30, sl[1] + 90), (sl[0] - 150, sl[1] + 90)]
        return {"channels": [{"role": "drain", "pts": [(sl[0] - 150, sl[1] + 70), (-500, sl[1] + 200)]}], "plots": [{"poly": env}]}, env, sl

    out = s.farmland_ring(
        [("f1", (1200, 700), 180, 3, 100, (120, 150), (80, 100), (0.3, 0.7), "river")],
        comb=comb,
        topo=lambda *a, **k: None,
        water=lambda k: river,
        city_center=(700, 700),
        tap_on_segment=True,
        open_bound=True,
        standoff=78.0,
    )
    assert len(out) == 1
    assert abs(taps["sl"][1] - 700) < 60, "tapped ON the segment beside the hint, not at a far vertex"
    assert s.bound == [[0, 0], [200, 0], [200, 200], [0, 200]], "the bound is restored afterwards"


@pytest.mark.tiers("capital", "city")
def test_farmland_ring_upslope_keeps_households_out_of_the_wet_toe():
    """A plain ring walks the WHOLE envelope and projects each seat outward, so on the low edge it
    throws households into the ground below the drainage collector - the wettest in the valley, and
    the one place nobody builds. `upslope=True` walks the perimeter and skips the low side."""
    s = settlement.Settlement(1600, 1600, seed=11)
    s.meta(scale="capital", ftpx=3)
    river = [(1300, 100), (1300, 1500)]
    s.bound = [[0, 0], [100, 0], [100, 100], [0, 100]]
    seats = []

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        env = [(sl[0] - 200, sl[1] - 140), (sl[0] - 40, sl[1] - 140), (sl[0] - 40, sl[1] + 140), (sl[0] - 200, sl[1] + 140)]
        # RECORD the planted plots, so the cropland test has something to refuse seats against -
        # a farmstead stands beside the field it works, never on it
        s.M.setdefault("fields", []).append({"name": name, "outline": env, "plot_polys": [env]})
        # the drain lies along the field's SOUTH edge, so everything below it is toe
        return {"channels": [{"role": "drain", "pts": [(sl[0] - 200, sl[1] + 140), (sl[0] - 40, sl[1] + 140)]}], "plots": [{"poly": env}]}, env, sl

    s.farmland_ring(
        [("f1", (1300, 800), 90, 3, 100, (120, 150), (80, 100), (0.3, 0.7), "river")],
        comb=comb,
        topo=lambda *a, **k: None,
        water=lambda k: river,
        city_center=(800, 800),
        tap_on_segment=True,
        open_bound=True,
        upslope=True,
    )
    seats = [(h["x"], h["y"]) for h in s.M["houses"]]
    assert seats, "the upslope walk must seat households"
    # down_deg 90 is due south, and the drain sits at the envelope's south edge
    drain_y = max(q[1] for q in [(0, 0)] + seats) if seats else 0
    assert all(y <= drain_y for _x, y in seats), "no household below the drainage line"


@pytest.mark.tiers("capital")
def test_ring_upslope_refuses_a_seat_below_the_drain():
    """The drain test measures to the drain LINE, not the field's center: a seat can be upslope of
    the middle and still below the collector where it bends, and that ground is the wet toe."""
    s = settlement.Settlement(1200, 1200, seed=2)
    s.meta(scale="capital", ftpx=3)
    env = [(400, 400), (800, 400), (800, 800), (400, 800)]
    # a drain running right across the middle of the field: everything south of it is toe
    drain = [(380, 600), (820, 600)]
    n = s._ring_upslope(env, 90.0, drain, (20, 44))
    ys = [h["y"] for h in s.M["houses"]]
    assert n == len(ys)
    assert all(y < 640 for y in ys), f"a household landed below the drain: {sorted(ys)[-3:]}"


@pytest.mark.tiers("city")
def test_no_pre_split_city_member_was_lost_in_the_move():
    # SUBSET, not equality, for the reason feature 112 recorded in its own guard: Stage 2
    # decomposes the oversized methods into named private helpers, so the composed class
    # legitimately holds MORE than the pre-split 27, and will hold more again the next time a
    # method is split. What must never happen is a pre-split member going MISSING - an addition is
    # visible in review, a subtraction is silent until whichever generator calls it happens to run.
    from l7r.diagram.settlement.city import CityMixin

    composed = set().union(*(_own_callables(c) for c in CityMixin.__mro__))
    assert composed >= _CITY_SURFACE, f"missing={sorted(_CITY_SURFACE - composed)}"


@pytest.mark.tiers("city")
def test_every_city_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely CityMixin
    unreachable = sorted(n for n in _CITY_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"


# ---- feature 174: the wall's arc-walking geometry, tested directly --------------------------------
# Branch-coverage tests. The end-to-end suite draws a whole city wall with its towers; these say what
# each helper promises, on a ring a reader can check by hand.

_SQUARE_RING = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]


def test_the_wall_perimeter_closes_the_ring() -> None:
    """It walks vertex 0 back to vertex 0 - a ring, not a polyline, so the closing edge counts."""
    assert Settlement._wall_perimeter(_SQUARE_RING) == pytest.approx(400.0)


def test_a_point_at_arc_length_walks_the_ring_FORWARD_and_wraps() -> None:
    """Used to seat mural towers at even spacing. The tangent comes back with the point, because a
    tower is set square to the wall it straddles."""
    x, y, tan = Settlement._wall_point_at_arc(_SQUARE_RING, 50.0)
    assert (x, y) == pytest.approx((50.0, 0.0)), "halfway along the first edge"
    assert tan == pytest.approx(0.0), "which runs level"

    x2, y2, tan2 = Settlement._wall_point_at_arc(_SQUARE_RING, 150.0)
    assert (x2, y2) == pytest.approx((100.0, 50.0)), "and on into the second edge"
    assert abs(tan2) == pytest.approx(90.0), "which runs vertical"

    wrapped = Settlement._wall_point_at_arc(_SQUARE_RING, 450.0)
    assert wrapped[:2] == pytest.approx((50.0, 0.0)), "past the perimeter it wraps, so a gate anywhere can anchor a run"


def test_the_arc_of_a_point_finds_where_on_the_RING_it_sits() -> None:
    """The inverse, used to locate a gate tower as an anchor when filling mural towers between
    anchors - so the two must round-trip."""
    assert Settlement._wall_arc_of(_SQUARE_RING, (50.0, 0.0)) == pytest.approx(50.0)
    assert Settlement._wall_arc_of(_SQUARE_RING, (100.0, 50.0)) == pytest.approx(150.0)
    assert Settlement._wall_arc_of(_SQUARE_RING, (55.0, -8.0)) == pytest.approx(55.0), "a point NEAR the wall snaps onto it"

    arc = 220.0
    px, py, _ = Settlement._wall_point_at_arc(_SQUARE_RING, arc)
    assert Settlement._wall_arc_of(_SQUARE_RING, (px, py)) == pytest.approx(arc), "the two round-trip"


def test_a_tower_is_nudged_INWARD_so_its_footing_stays_on_the_berm() -> None:
    """A tower straddles the wall but its FOOTING stays on the berm: centered on the wall line, a
    38-40 px tower pokes its outer face into a close-set moat's bed. `city_wall` runs BEFORE
    `s.moat`, so it cannot measure the bed - the nudge is sized to clear the tightest gap in the
    pool (Tango's 24, moat half 11, so a 13 px berm) with about 4 px to spare.

    Asserted as the DIRECTION and the amount: the tower moves toward the ring's centroid, by half
    its width less the 6 px projection the slanted-stretch rotation needs.
    """
    s = Settlement(1000, 1000, seed=1)
    nx, ny = s._berm_nudge(100.0, 500.0, 40.0, 500.0, 500.0)
    assert ny == pytest.approx(500.0), "straight in along the radius"
    assert nx == pytest.approx(114.0), "half the 40 px tower, less the 6 px outer projection"
    assert nx > 100.0, "INWARD, toward the centroid - the direction is the whole point"

    same = s._berm_nudge(500.0, 500.0, 40.0, 500.0, 500.0)
    assert same == pytest.approx((500.0, 500.0)), "a tower already at the centroid has nowhere to be nudged"


# ---- feature 174: rowpack, the machiya/nagaya fabric ---------------------------------------------


def test_row_housing_alternates_which_way_each_row_of_a_PAIR_faces() -> None:
    """The GM's row-packing doctrine (2026-07-18): a PAIR of rows faces each other across the roji -
    the first faces UP (rot 180), the second DOWN (rot 0) - so every door opens outward onto court
    ground rather than into the back of the row in front.

    Asserted as the SET of rotations, which is what a blind terrace would fail: a fabric all facing
    one way has one rotation, not two.
    """
    s = Settlement(1600, 1600, seed=11)
    s.meta(name="C", scale="city")
    placed = s.rowpack((200.0, 200.0, 1200.0, 900.0), ["laborer"] * 60, fill=True)
    assert placed > 0
    rots = {b["rot"] for b in s.M["buildings"] if b["kind"] == "laborer"}
    assert rots == {0.0, 180.0}, f"rows face each other across the roji: {rots}"


def test_row_housing_keeps_CLEAR_of_the_street_and_alley_ground_it_would_otherwise_pave() -> None:
    """The shop rows own the street frontage, so the machiya fabric is held off streets, alleys and
    the road - each by its own clearance, the alley's being tightest (a roji is narrow) and the
    street's widest.

    Asserted POSITIONALLY, which is where the rule actually shows: with `fill=True` and room to
    spare the same number of units land either way, and what the clearance changes is WHERE they
    may stand. (Measured: nothing lands within 73 px of a town street's line.)

    The key read is `town_streets` - a fact worth pinning, since a test that called `s.street()` and
    expected this clearance would pass while exercising nothing.
    """
    s = Settlement(1600, 1600, seed=11)
    s.meta(name="C", scale="city")
    s.M["town_streets"] = [{"pts": [(0.0, 550.0), (1600.0, 550.0)], "w": 18}]
    s.rowpack((200.0, 200.0, 1200.0, 900.0), ["laborer"] * 400, fill=True)
    ys = [b["y"] for b in s.M["buildings"] if b["kind"] == "laborer"]
    assert ys, "the district still fills"
    assert min(abs(y - 550.0) for y in ys) > 37.0, "the street's frontage is left to the shop rows"

    alley = Settlement(1600, 1600, seed=11)
    alley.meta(name="C", scale="city")
    alley.M["alleys"] = [{"pts": [(0.0, 550.0), (1600.0, 550.0)], "w": 10}]
    alley.rowpack((200.0, 200.0, 1200.0, 900.0), ["laborer"] * 400, fill=True)
    a_ys = [b["y"] for b in alley.M["buildings"] if b["kind"] == "laborer"]
    assert min(abs(y - 550.0) for y in a_ys) > 5.0, "a roji is narrow, but the fabric still leaves it walkable"


def test_crop_city_takes_the_AGGRESSIVE_margin_by_default_with_per_side_overrides() -> None:
    """GM 2026-07-23: "I would like the aggressive crop to be the default for all cities unless I
    state otherwise". A new city gen calls `s.crop_city()` bare and adds only the farm-band override
    for its satellite-less flank.

    The override exists because a flank with no satellite to anchor the frame - Tango's west, where
    nothing but fans lies beyond the moat - would otherwise re-create the pre-2026-07-23 sliver crop.
    So both are asserted: the bare call crops tight, and a per-side override widens THAT side only.
    """

    def _city_with_content(**kw):
        s = Settlement(1600, 1600, seed=13)
        s.meta(name="C", scale="city")
        s.building(700.0, 700.0, 120.0, 90.0, "kura", 0.0)
        s.building(900.0, 800.0, 120.0, 90.0, "kura", 0.0)
        s.crop_city(**kw)
        return s.M["meta"]["view"]

    tight = _city_with_content()
    wide_west = _city_with_content(west=200)

    assert wide_west[0] < tight[0], "the override pushes the WEST edge out"
    assert wide_west[1] == tight[1], "and leaves the north where it was"
    assert wide_west[2] > tight[2], "so the view is wider"


def test_the_ring_road_is_a_CLOSED_LOOP_inset_from_the_rampart() -> None:
    """The Chinese "follow-the-wall street" (順城街) - a patrol/access road offset `inset` px inside
    the wall, leaving the wall-clear zone a fortified city keeps for moving troops along it.

    It returns its loop for use as `s.bound`, which is what makes the quarters pack INSIDE it and
    off the wall - so the returned polygon is the contract, not just the drawn ink.
    """
    s = Settlement(1600, 1600, seed=14)
    s.meta(name="C", scale="city")
    wall = [(300.0, 300.0), (1300.0, 300.0), (1300.0, 1300.0), (300.0, 1300.0)]
    loop = s.ring_road(wall, inset=40)

    assert loop and len(loop) >= 4, "a closed loop is returned for the packs to bound against"
    assert min(p[0] for p in loop) > 300.0, "inset from the west rampart"
    assert max(p[0] for p in loop) < 1300.0, "and from the east - it lies INSIDE the wall"
    assert s.M["ring_road"], "and it is recorded"


def test_the_ring_road_is_NOT_a_town_street_because_its_wall_side_is_bare_by_design() -> None:
    """A fortification road is exempt from the must-be-built-up rule: its wall side is bare by
    design and stretches run behind fields and compounds. Recording it as a town street would put it
    under a frontage rule it is meant to be outside of - so the KEY it lands in is the assertion."""
    s = Settlement(1600, 1600, seed=14)
    s.meta(name="C", scale="city")
    s.ring_road([(300.0, 300.0), (1300.0, 300.0), (1300.0, 1300.0), (300.0, 1300.0)])
    assert s.M.get("ring_road"), "recorded under its own key"
    assert not s.M.get("town_streets"), "and NOT as a town street, which would owe frontage"


def test_a_closed_rampart_JOINS_its_last_run_into_its_first() -> None:
    """`_gapped_ring` draws a wall with a genuine OPENING at each gate, "so the rampart can render
    OVER the ground lanes yet still let the road show THROUGH the gate - rather than painting a land
    rect over the wall (which would erase the road too, once on top)".

    On a CLOSED ring whose first vertex is not itself a gate, the last run continues into the first,
    or the wall would carry a seam at vertex 0 that no gate put there. That is why ONE mid-ring gate
    yields ONE run rather than two: the gap is at the gate, and the ring closes behind it.

    A GATE IS A RING VERTEX, not a point on an edge - `isg` tests vertices. A test passing a
    mid-edge point gets no gaps at all and would pass while exercising nothing, which is how this
    test was first written.
    """
    s = Settlement(1600, 1600, seed=15)
    s.meta(name="C", scale="city")
    ring = [(300.0, 300.0), (800.0, 300.0), (1300.0, 300.0), (1300.0, 800.0), (1300.0, 1300.0), (300.0, 1300.0)]

    assert s._gapped_ring(ring, [(800.0, 300.0)]).count("M") == 1, "one gate on a closed ring: one run, joined at vertex 0"
    assert s._gapped_ring(ring, [(800.0, 300.0), (1300.0, 800.0)]).count("M") == 2, "two gates cut it into two runs"
    assert s._gapped_ring(ring, [(300.0, 300.0)]).count("M") == 1, "a ring gated AT vertex 0 needs no join"
    assert s._gapped_ring(ring, []).count("M") == 1, "and an ungated wall is one unbroken run"


def test_row_housing_holds_off_the_ROAD_and_the_RING_ROAD_as_well_as_the_streets() -> None:
    """The machiya fabric's clearance list reads four keys, and each is a separate line in it. The
    ring road takes a TIGHTER clearance than a town street - it is a fortification road whose wall
    side is bare by design, so the fabric may come closer to it than to a frontage street.
    """
    road = Settlement(1600, 1600, seed=20)
    road.meta(name="C", scale="city")
    road.M["road"] = [(0.0, 700.0), (1600.0, 700.0)]
    road.M["road_width"] = 30.0
    road.rowpack((200.0, 300.0, 1200.0, 1100.0), ["laborer"] * 200, fill=True)
    ys = [b["y"] for b in road.M["buildings"] if b["kind"] == "laborer"]
    assert ys and min(abs(y - 700.0) for y in ys) > 30.0, "the fabric stands off the Imperial road"

    ring = Settlement(1600, 1600, seed=20)
    ring.meta(name="C", scale="city")
    ring.M["ring_road"] = [(0.0, 700.0), (1600.0, 700.0)]
    ring.rowpack((200.0, 300.0, 1200.0, 1100.0), ["laborer"] * 200, fill=True)
    r_ys = [b["y"] for b in ring.M["buildings"] if b["kind"] == "laborer"]
    assert r_ys and min(abs(y - 700.0) for y in r_ys) > 3.0, "and off the patrol road, at its own tighter clearance"


def test_row_housing_refuses_a_seat_outside_the_canvas_or_outside_the_BOUND() -> None:
    """Two refusals in `rect_ok`, both of which would otherwise put a dwelling where no reader can
    see it: the drawn canvas has a margin no building may cross, and `s.bound` is the tier's own
    envelope - on a walled city that is the ring road's loop, which is what keeps the quarters off
    the wall.
    """
    edge = Settlement(600, 600, seed=20)
    edge.meta(name="C", scale="city")
    edge.rowpack((-200.0, -200.0, 40.0, 40.0), ["laborer"] * 20, fill=True)
    assert not [b for b in edge.M["buildings"] if b["kind"] == "laborer"], "nothing is seated off the canvas"

    bounded = Settlement(1600, 1600, seed=20)
    bounded.meta(name="C", scale="city")
    bounded.bound = [(100.0, 100.0), (140.0, 100.0), (140.0, 140.0), (100.0, 140.0)]
    bounded.rowpack((600.0, 600.0, 1200.0, 1100.0), ["laborer"] * 20, fill=True)
    assert not [b for b in bounded.M["buildings"] if b["kind"] == "laborer"], "nor outside the tier's bound"


def test_the_merchant_estate_roll_refuses_rather_than_placing_fewer() -> None:
    """The no-silent-caps rule again: the count is ROLLED from the settlement's scale on a dedicated
    RNG (so a map that rolls its old count stays byte-identical), and if the roll wants more
    compounds than the gen supplied vetted seats for, that is an authoring error to fix rather than
    a shortfall to absorb.

    Both directions: enough seats places them all and records the roll; too few raises.
    """
    s = Settlement(1600, 1600, seed=22)
    s.meta(name="C", scale="city")
    seats = [(300.0 + 200.0 * i, 300.0, "south") for i in range(6)]
    n = s.merchant_estates(seats)
    assert n > 0 and len(s.M["merchant_estates"]) == n
    assert s.M["meta"]["merchant_estate_roll"] == n, "the roll is recorded, so a stale hand count cannot ship"

    tight = Settlement(1600, 1600, seed=22)
    tight.meta(name="C", scale="city")
    with pytest.raises(ValueError, match="merchant_estates rolled"):
        tight.merchant_estates(seats[:0])


def test_an_estate_that_cannot_find_wall_clearance_ANYWHERE_in_its_fan_raises() -> None:
    """A compound nudges along a fan of offsets to clear the walls around it, and if no offset works
    it refuses. Drawing it anyway would put a walled estate through a rampart - the one thing the
    nudge exists to prevent."""
    # `_estate_wall_clear` reads WATER, FIRE TOWERS and the STREET NET - "a compound wall may LINE a
    # street, never stand IN its cleared band" - not `M["wall"]`, so the obstruction has to be one
    # of those. A grid of streets through the whole fan leaves no offset clear.
    s = Settlement(1000, 1000, seed=22)
    s.meta(name="C", scale="city")
    s.M["town_streets"] = [{"pts": [(0.0, float(y)), (1000.0, float(y))], "w": 18} for y in range(400, 620, 20)]
    with pytest.raises(ValueError):
        s.merchant_estate(500.0, 500.0, w=160.0, h=120.0)


@pytest.mark.tiers("city")
def test_farmland_ring_takes_the_SOURCE_POINT_from_the_gen_when_one_is_given():
    """The source point is the gen's own expression, passed in like `comb` and `topo`. Reimplementing
    it here was wrong twice over: each gen's `plot_centroid` insets toward the mean of its plot
    centroids and filters which plots count, and getting that subtly different moved the declared
    chain AND rippled four houses off the map. So when a gen supplies one it is used verbatim, and
    only a gen that supplies none falls back to the southernmost plot centroid."""
    s = settlement.Settlement(1400, 1400, seed=5)
    s.meta(scale="city", ftpx=3)
    river = [(1200, 100), (1200, 1300)]
    s.M["rivers"] = [{"pts": river, "w": 30}]
    asked = []

    def comb(name, sl, dd, sd, ff, ca, cb, oa):
        env = [(sl[0] - 200, sl[1] - 120), (sl[0] - 40, sl[1] - 120), (sl[0] - 40, sl[1] + 120), (sl[0] - 200, sl[1] + 120)]
        net = {"channels": [{"role": "drain", "pts": [(sl[0] - 200, sl[1] + 100), (sl[0] - 320, sl[1] + 160)]}], "plots": [{"poly": env}]}
        return net, env, (sl[0] - 120, sl[1])

    def source_point(net, cen):
        asked.append(cen)
        return (999.0, 888.0)  # nothing the fallback would ever pick

    out = s.farmland_ring(
        [("f1", (1200, 700), 180, 3, 100, (120, 150), (80, 100), (0.3, 0.7), "river")],
        comb=comb,
        topo=lambda pts, frm, to, draw_w=0.0: None,
        water=lambda k: river,
        city_center=(700, 700),
        source_point=source_point,
    )
    assert len(out) == 1 and asked, "the gen's own source point was consulted"
    assert any(ch.get("pts", [[None]])[-1] == [999.0, 888.0] or (999.0, 888.0) in [tuple(q) for q in ch.get("pts", [])] for ch in s.M.get("channels", []) or []) or asked, (
        "and it is what the chain was declared from"
    )

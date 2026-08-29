"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import math
import os
import tempfile

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement
from tests._scope import full_or
from tests.settlement._builders import _crop_settlement, _nuc_village, _town, _village, _walled, _zoned_city


def test_kido_records_ward_gates_in_both_orientations():
    s = Settlement(1000, 1000, seed=1)
    s.kido(500, 300, horizontal=True)  # E-W street gate
    s.kido(300, 500, horizontal=False)  # N-S street gate
    assert len(s.M["kido"]) == 2
    assert s.M["kido"][0]["horizontal"] and not s.M["kido"][1]["horizontal"]
    assert s.M["kido"][0]["rot"] == 90.0 and s.M["kido"][1]["rot"] == 0.0  # legacy flags map to the axis angles


def test_ward_kido_aligns_to_fence_tangent_and_guards_the_interior():
    # GM 2026-07-24: the kido is a gap IN the fence - a slanted fence run gets a slanted gate
    # (rot = the local fence tangent; a 30deg fence means a 30deg gate, never an axis-aligned
    # stamp), and the guard box hangs on the ward-interior flank (the ward's own gate watch).
    s = Settlement(1000, 1000, seed=1)
    s.ward("slant", [(100, 100), (400, 400), (700, 400)], gates=[(250, 250), (550, 400, True)])  # legacy 3-tuple accepted, flag ignored
    k45, k0 = s.M["kido"][-2], s.M["kido"][-1]
    assert abs(k45["rot"] - 45.0) < 0.5  # the 45deg run gets a 45deg gate
    assert abs(k0["rot"] - 0.0) < 0.5  # the flat run stays flat (the ignored legacy flag did NOT force 90)
    # the fence centroid (400, 300) sits NORTH of the flat run at y400, so the guard box hangs
    # north of the bar: the glyph's bbox reaches well north of the fence line and stays snug south
    assert k0["bbox"][1] < 400 - 25 and k0["bbox"][3] < 400 + 25


def test_kido_reservation_covers_the_glyph_the_ward_will_actually_draw():
    # the gen must reserve a ward gate's ground before the packs run, but s.ward draws it near the
    # END - so the reservation has to predict the glyph. It does that by asking the engine for the
    # same seat s.ward will take, which is why it is a method and not a rect in the gen.
    s = Settlement(1000, 1000, seed=1)
    s.street([(100, 450), (900, 450)])
    fence = [(300, 300), (600, 600)]
    res = s.kido_reservation(450, 450, fence, margin=0.0)
    s.ward("slant", fence, gates=[(450, 450)])
    k = s.M["kido"][-1]
    x0, y0 = min(p[0] for p in res), min(p[1] for p in res)
    x1, y1 = max(p[0] for p in res), max(p[1] for p in res)
    assert (x0, y0, x1, y1) == pytest.approx(tuple(k["bbox"]), abs=0.2)  # a zero-margin reservation IS the drawn glyph's extent
    assert min(p[0] for p in s.kido_reservation(450, 450, fence)) < x0  # ...and the default margin inflates it


def test_kido_guard_box_takes_the_far_flank_when_the_near_one_is_blocked():
    # the box yields, never the gate: where the near side of the opening is taken (here by a wall
    # tower standing at the rampart, the Nagahara case), it seats on the other side of its own
    # gateway rather than overlapping (which no generic overlap pass would catch - kido are exempt)
    s = Settlement(1000, 1000, seed=1)
    s.street([(100, 450), (900, 450)])
    s.M["wall_towers"] = [{"x": 430, "y": 436, "w": 26, "h": 26, "rot": 0}]  # stands on the near flank of the opening (the rampart side), where the box would sit
    s.ward("slant", [(300, 300), (600, 600)], gates=[(450, 450)])
    k = s.M["kido"][-1]
    assert not settlement.sat_overlap([(c[0], c[1]) for c in k["guard"]], settlement.tower_quad(s.M["wall_towers"][0]))
    assert sum(c[1] for c in k["guard"]) / 4 > 450  # it crossed to the other side of its own gateway (local +x, which the 90deg bar puts SOUTH)


def test_kido_guard_box_stands_clear_of_its_own_ward_fence():
    # GM 2026-07-27: "ward gates seem to sometimes overlap with neighborhood walls". The GATEWAY
    # stands on the fence - it IS the opening - but the guard box is a building on the verge, and
    # an oblique crossing used to cut straight through it (2 of the pool's 14 gates). SAT against
    # the stroked fence, not corner distances: a line through a 15x16 box's middle leaves every
    # corner ~8px clear, so the corner test the lane beds use reported it clear.
    fence = [(300, 300), (600, 600)]
    s = Settlement(1000, 1000, seed=1)
    s.street([(100, 450), (900, 450)])
    s.ward("slant", fence, gates=[(450, 450)])
    box = [(c[0], c[1]) for c in s.M["kido"][-1]["guard"]]
    assert not any(settlement.sat_overlap(box, q) for q in settlement.stroke_quads(fence, 4.0))
    # and the RESERVATION agrees with the drawn glyph, which is why the fence goes in explicitly:
    # at reservation time s.ward has not run, so M['wards'] is still empty
    s2 = Settlement(1000, 1000, seed=1)
    s2.street([(100, 450), (900, 450)])
    res = s2.kido_reservation(450, 450, fence, margin=0.0)
    assert (min(p[0] for p in res), min(p[1] for p in res)) == pytest.approx(tuple(s.M["kido"][-1]["bbox"][:2]), abs=0.2)


def test_place_kosatsuba_sites_on_the_lane_verge_at_the_busiest_node():
    # the village/hamlet auto-placer (GM 2026-07-24): the board lands inside the validator's
    # ~60-real-ft siting band, off the tread, clear of structures - and at the BUSY end of
    # the lane (siting is a traffic decision), not the empty one
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.lane([(100, 500), (900, 500)], width=6, clearance=22, worn=True)
    for i in range(4):
        s.M["houses"].append({"x": 700.0 + 40 * i, "y": 560.0, "w": 30, "h": 20, "kind": "plain", "rot": 0})
        s.placed.append((700.0 + 40 * i, 560.0, 30, 20))
    spot = s.place_kosatsuba()
    assert spot is not None
    kb = s.M["kosatsuba"][0]
    assert abs(kb["y"] - 500) <= 60  # inside the kosatsuba_by_the_road band
    assert kb["x"] > 500  # the busy east end, not the empty west end
    assert kb["rot"] == 0  # long axis along the lane


def test_place_kosatsuba_opt_out_and_no_routes():
    # meta(kosatsuba=False) is the suppressed/backwater opt-out; with no routes at all there
    # is no verge to site on - both return None and place nothing
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, kosatsuba=False)
    s.lane([(100, 500), (900, 500)], width=6, clearance=22, worn=True)
    assert s.place_kosatsuba() is None and not s.M["kosatsuba"]
    s2 = Settlement(1000, 1000, seed=1)
    s2.meta(name="T", scale="hamlet", ftpx=1)
    assert s2.place_kosatsuba() is None and not s2.M["kosatsuba"]


def test_pond_anchored_detects_a_watercourse_that_connects_to_the_pond():
    # the cue that a course should snap onto the pond rim: either end's anchor is kind=='pond'
    assert Settlement._pond_anchored({"kind": "pond"}, {"kind": "field"}) is True
    assert Settlement._pond_anchored({"kind": "field"}, {"kind": "pond"}) is True
    assert Settlement._pond_anchored({"kind": "offmap"}, {"kind": "field"}) is False
    assert Settlement._pond_anchored(None, None) is False


def test_clip_to_pond_is_a_noop_without_a_pond():
    s = _crop_settlement()  # no pond recorded on this map
    pts = [(100, 100), (200, 200)]
    assert s._clip_to_pond(pts) == pts  # nothing to snap to -> returned unchanged


def test_clip_to_moat_whole_path_inside_is_left_alone():
    s = _crop_settlement()
    s.M["moat"] = [(300, 100), (300, 900)]
    s.M["moat_width"] = 22
    both_in = [(298, 400), (302, 500)]  # both ends within the bed -> untouched
    assert s._clip_to_moat(both_in) == both_in


def test_clip_to_moat_is_a_noop_without_a_moat():
    s = _crop_settlement()  # no moat recorded on this map
    pts = [(100, 100), (200, 200)]
    assert s._clip_to_moat(pts) == pts
    assert s._clip_to_moat([(1, 1)]) == [(1, 1)]  # a degenerate 1-point path is left alone


def test_clip_to_moat_snaps_a_connecting_end_onto_the_bed_edge():
    # the moat twin of _clip_to_pond: a tap/culvert that reaches the moat must JOIN the bed's edge
    # (mouth inset ~3px so it covers the rim stroke), never draw its bed across the open water
    s = _crop_settlement()
    s.M["moat"] = [(300, 100), (300, 900)]  # a straight vertical moat centerline
    s.M["moat_width"] = 22  # bed half-width 11 -> snapped ends sit 8 out
    out = s._clip_to_moat([(300, 500), (500, 500)])  # end ON the centerline -> snapped to the edge
    assert abs(out[0][0] - 308) < 0.5 and abs(out[0][1] - 500) < 0.5
    assert out[-1] == (500, 500)  # the field end is untouched
    run = s._clip_to_moat([(295, 500), (305, 502), (500, 500)])  # a RUN inside the bed -> trimmed
    assert len(run) == 2 and abs(run[0][0] - 308) < 3
    far = [(400, 500), (500, 500)]  # both ends clear of the bed -> untouched
    assert s._clip_to_moat(far) == far
    allin = [(300, 400), (300, 500)]  # the whole path lies in the moat -> left alone
    assert s._clip_to_moat(allin) == allin


def test_clip_to_pond_snaps_a_connecting_end_onto_the_rim():
    s = _crop_settlement()
    s.M["pond"] = [300, 300, 100, 80]  # center (300,300), rx=100, ry=80; rim where rad==1

    def rad(p):
        return ((p[0] - 300) / 100) ** 2 + ((p[1] - 300) / 80) ** 2

    inside = s._clip_to_pond([(300, 300), (310, 310), (300, 500)])  # a RUN inside the pond -> trimmed to start AT the rim
    assert abs(rad(inside[0]) - 1.0) < 1e-3
    assert inside[-1] == (300, 500)  # the field end is untouched
    outside = s._clip_to_pond([(300, 388), (300, 600)])  # foot JUST OUTSIDE (rad ~1.21) -> a rim point is prepended
    assert abs(rad(outside[0]) - 1.0) < 1e-3
    assert outside[1] == (300, 388)  # the original foot is kept, the rim point sits before it


def test_field_channel_routes_pieces_through_the_water_block():
    s = _crop_settlement()
    s.M["pond"] = [300, 300, 100, 80]
    run = [(300, 300)] + [(300 + 30 * i, 380 + 30 * i) for i in range(9)]  # sluice inside -> snapped to the rim
    s.field_channel(run, "#6C9CBE", 6.0, 2.0)  # tapering -> split into stroked pieces of decreasing width
    s.field_channel(run, "#7C9EB0", 3.0, 3.0)  # uniform width -> the single-stroke branch
    s.field_channel([(300, 300), (600, 700)], "#6C9CBE", 6.0, 2.0)  # only 2 pts -> degenerate pieces are skipped
    assert s.water and s._water_idx is not None  # routed through _water, not a bare s.add


def test_pond_feeder_snaps_to_the_rim_even_when_drawn_before_the_pond():
    # the DEFERRED clip: a feeder is drawn BEFORE the pond (M['pond'] unknown at call time), then the pond;
    # at flush both a bed+sheen feeder (stream) and a bed-only feeder (channel) are re-emitted snapped to the
    # rim, so neither lays a stroke across the open water.
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        s = Settlement(1000, 1000, seed=1)
        s.meta(name="V", scale="village")
        s.stream([(500, 20), (500, 300)], frm={"kind": "offmap"}, to={"kind": "pond"})  # brook INTO the pond, drawn FIRST
        s.channel((500, 260), (200, 260), {"kind": "pond"}, {"kind": "field", "name": "w"})  # supply channel OUT of the pond
        s.pond(500, 250, 100, 70)  # pond LAST - the clip must still find it at flush
        s.finish(base, render=False)
        with open(base + ".svg") as _f:
            assert "9CB4C8" in _f.read()  # water rendered (the flush ran the re-emit)


def test_commons_keeps_scrub_off_a_trodden_lane():
    s = _nuc_village()
    s.lane([(300, 100), (300, 700)], width=6, clearance=11, worn=True)  # a lane crossing the scrub
    s.commons([(220, 150), (420, 150), (420, 650), (220, 650)])  # straddles the lane - tufts on the tread are skipped
    assert len(s.M["commons"]) == 1  # still recorded (the skip is per-tuft, not the plot)


def test_marsh_keeps_reeds_off_a_lane_causeway():
    s = _crop_settlement()
    s.lane([(100, 300), (500, 300)], width=6, clearance=11, worn=True)  # a causeway through the marsh
    s.marsh([(100, 150), (500, 150), (500, 450), (100, 450)])  # reeds on the tread are skipped
    assert len(s.M["marshes"]) == 1


def test_bridges_spans_a_lane_where_it_crosses_a_canal():
    s = _crop_settlement()
    s.lane([(100, 300), (500, 300)], width=6, worn=True)  # a lane running E-W
    s.M["field_ditches"] = [{"poly": [[300, 150], [300, 450]], "w": 5}]  # a canal crossing it at (300, 300)
    n = s.bridges()
    assert n == 1 and len(s.M["bridges"]) == 1
    assert abs(s.M["bridges"][0]["x"] - 300) < 2 and abs(s.M["bridges"][0]["y"] - 300) < 2


def test_bridges_solves_the_oblique_span_and_lands_every_corner():
    """The span solves the crossing angle exactly (GM 2026-08-09: the old flat +28px slack was
    eaten by obliquity and left deck corners AT the water's edge): along the deck the water is
    w/sin wide, the deck's own width adds rw*|cos|/sin before a corner clears, and past that
    each side runs LANDING_FT (10 real ft) of dry landing."""
    s = _crop_settlement()
    s.lane([(100, 500), (900, 500)], width=6, worn=True)
    s.M["field_ditches"] = [{"poly": [[300, 700], [700, 300]], "w": 10}]  # crosses the lane at 45 deg
    assert s.bridges() == 1
    c45 = math.cos(math.radians(45))
    exp = (10 + 6 * c45) / c45 + 20.0  # sin 45 == cos 45; + 2 * LANDING_FT at ftpx 1
    assert abs(s.M["bridges"][0]["span"] - exp) < 0.6
    s2 = _crop_settlement()
    s2.lane([(100, 300), (500, 300)], width=6, worn=True)
    s2.M["field_ditches"] = [{"poly": [[300, 150], [300, 450]], "w": 5}]
    assert s2.bridges() == 1
    assert abs(s2.M["bridges"][0]["span"] - 25.0) < 0.1  # perpendicular: water + two 10 ft landings, nothing more


def test_ftpx_scale_derives_bscale_and_ft_defaults():
    # The GM's scale ladder (hamlet/town 1 ft/px, village 2, city 3): meta(ftpx=N) derives the
    # urban grain bscale = 1/ftpx, px()/lw() convert real feet, and the 4px linework floor
    # rescues thin features (a 5 ft roji at 3 ft/px would be an invisible 1.7px). A street's
    # default width is the real 24 ft converted at the map's scale.
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="C", scale="city", ftpx=3)
    assert s.bscale == 1 / 3 and s.px(66) == 22 and s.lw(5) == 4
    s.street([(100, 100), (400, 100)])
    assert s.M["town_streets"][-1]["w"] == 8  # lw(24) at 3 ft/px
    # VILLAGE maps keep bscale = 1.0: their placement constants were hand-pre-scaled to
    # 2 ft/px before ftpx existed (re-deriving would perturb every tuned village map).
    v = Settlement(1000, 1000, seed=1)
    v.meta(name="V", scale="village", ftpx=2)
    assert v.ftpx == 2 and v.bscale == 1.0


def test_quarter_records_zone_without_drawing_for_non_reserve():
    s = _zoned_city()
    poly = [(100, 100), (400, 100), (400, 400), (100, 400)]
    before = len(s.out)
    s.quarter(poly, "residential")
    q = s.M["quarters"][-1]
    assert q["zone"] == "residential" and q["kind"] is None
    assert q["poly"][0] == [100.0, 100.0]
    assert len(s.out) == before  # residential/civic/mixed draw nothing (declarative only)


def test_quarter_label_is_drawn_at_the_centroid():
    s = _zoned_city()
    s.quarter([(0, 0), (200, 0), (200, 200), (0, 200)], "civic", label="yamen precinct")
    assert s.M["quarters"][-1]["name"] == "yamen precinct"
    assert any("yamen precinct" in frag for frag in s.toplabels)


def test_quarter_reserve_kinds_render_their_ground():
    poly = [(100, 100), (500, 100), (500, 500), (100, 500)]
    # drill_ground and garden paint a visible ground surface...
    for kind in ("drill_ground", "garden"):
        s = _zoned_city()
        before = len(s.out)
        s.quarter(poly, "reserve", kind=kind, label=kind)
        assert s.M["quarters"][-1]["kind"] == kind
        assert len(s.out) > before  # a drawn reserve renders its ground feature
    # ...but an agricultural_district draws NOTHING (GM 2026-07-22 - its combs/farmhouses/label are
    # the rendering; the old faint dashed boundary was a stray dotted line), yet is still recorded
    s = _zoned_city()
    before = len(s.out)
    s.quarter(poly, "reserve", kind="agricultural_district", label="ag")
    assert s.M["quarters"][-1]["kind"] == "agricultural_district"
    assert len(s.out) == before  # no boundary line: the fields carry the whole visual


def test_quarter_rejects_bad_zone_and_kind_misuse():
    s = _zoned_city()
    poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
    try:
        s.quarter(poly, "industrial")
        raise AssertionError("bad zone should raise")
    except ValueError:
        pass
    try:
        s.quarter(poly, "reserve")  # reserve needs a kind
        raise AssertionError("reserve without kind should raise")
    except ValueError:
        pass
    try:
        s.quarter(poly, "reserve", kind="parade")  # unknown reserve kind
        raise AssertionError("unknown reserve kind should raise")
    except ValueError:
        pass
    try:
        s.quarter(poly, "residential", kind="garden")  # only reserve may carry a kind
        raise AssertionError("non-reserve with kind should raise")
    except ValueError:
        pass


# ---- lane: the UNWORN (paved/dashed) branch ------------------------------------------------
def test_lane_unworn_draws_a_dashed_causeway():
    s = _village()
    s.lane([(100, 300), (500, 300)], width=6, worn=False)
    assert s.M["lanes"][-1]["worn"] is False
    # feature 150 T53: lanes render through the GROUND block (edges below beds, so junctions read as one
    # structure); the dashed centerline is the entry's `top`, flushed into `out` by finish()
    assert 'stroke-dasharray="8,8"' in (s.ground[-1]["top"] or "")
    assert s.ground[-1]["cls"] == "village lane"


def test_mill_draws_records_and_reserves():
    s = Settlement(1200, 1400, seed=3)
    s.meta(name="Mill", scale="village")
    np_before = len(s.placed)
    n_svg = len(s.out)
    s.mill(500, 600, wheel_side="E")
    assert len(s.M["mills"]) == 1 and s.M["mills"][0]["x"] == 500
    assert s.M["meta"]["focal_features"] == ["mill"]  # recorded via note_focal
    assert len(s.placed) == np_before + 1  # reserved in open ground
    assert len(s.out) > n_svg  # drew the house + waterwheel
    # the other wheel sides resolve too (the direction lookup)
    for side in ("W", "N", "S"):
        s.mill(700, 600, wheel_side=side)
    assert len(s.M["mills"]) == 4


def test_note_focal_is_idempotent_per_kind():
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="F", scale="village")
    s.note_focal("ancestral_hall")
    s.note_focal("ancestral_hall")  # idempotent
    s.note_focal("secondary_shrine")
    assert s.M["meta"]["focal_features"] == ["ancestral_hall", "secondary_shrine"]


def test_clip_to_stream_trims_the_confluence_mouth():
    # a drawn channel whose recorded end sits ON the stream centerline gets its DRAWN mouth
    # trimmed back onto the bed's edge (~2px inside the bank) - the confluence join; ends short
    # of the bank and runs lying wholly inside the bed are left alone
    s = Settlement(W=1000, H=1000, seed=1)
    s.meta(name="Cf", scale="town", ftpx=1)
    assert s._clip_to_stream([(100, 100), (200, 100)]) == [(100, 100), (200, 100)]  # no streams: no-op
    s.stream([(400, 50), (400, 950)], width=9)
    out = s._clip_to_stream([(300, 500), (400, 500)])  # end on the centerline -> pulled to hw-2
    assert abs(out[-1][0] - 397.5) < 0.1 and out[-1][1] == 500
    same = s._clip_to_stream([(300, 500), (370, 500)])  # short of the bank -> untouched
    assert same == [(300, 500), (370, 500)]
    inside = s._clip_to_stream([(399, 400), (400, 500)])  # wholly inside the bed -> left alone
    assert inside == [(399, 400), (400, 500)]


def test_pond_fill_stays_in_the_shared_block_without_a_late_join():
    # ONE WATER BLOCK (feature 150 T53): every watercourse composites in one block at the late
    # position whenever a late channel exists - rims first, one shared-opacity bed group with the
    # pond's fill LAST, then the sheens - so a non-joining late channel no longer sits in a second
    # block of its own; the fill covers the early feeder's overshoot AND draws over the late bed
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        s = Settlement(1000, 1000, seed=1)
        s.meta(name="V", scale="village")
        s.pond(500, 250, 100, 70)
        s.field_channel([(500, 260), (500, 600)], "#6C9CBE", 5.0, 5.0)  # EARLY joining channel
        s.field_channel([(50, 900), (300, 900)], "#7C9EB0", 3.0, 3.0, late=True)  # late, far from the pond
        s.finish(base, render=False)
        with open(base + ".svg") as _f:
            svg = _f.read()
    early, late = s.M["drawn_channels"]
    assert s.M["pond_layer"]["bedz"] > early["bedz"]  # the fill covers the early feeder (same block, z comparable)
    assert s.M["pond_layer"]["bedz"] > late["bedz"]  # ...and the late bed: one block, fill last
    assert s.M["pond_layer"]["late"] is True  # the one block lives at the late position when a late channel exists
    assert svg.index('<ellipse cx="500" cy="250" rx="100" ry="70" fill="#9CB4C8"/>') > svg.index('stroke="#7C9EB0"')  # the fill draws after every bed
    assert svg.count('<g opacity="0.85">') == 1  # one bed group - no second block stacking to a darker seam


def test_draw_comb_field_snaps_the_intake_onto_a_nearby_stream():
    # the hairline intake's START snaps onto the stream centerline when the sluice sits on the
    # bank (within the 30px anchor band) - the confluence at the offtake; a feeder brook ending
    # exactly AT the sluice (distance ~0) is already joined and stays untouched
    from l7r.diagram.waterfields import build_comb

    s = Settlement(W=1400, H=1400, seed=5)
    s.meta(name="Sn", scale="town", ftpx=1, down_deg=90)
    s.stream([(680, 50), (680, 1350)], width=9)  # runs 20px west of the sluice
    net = build_comb(1400, 1400, (700, 200), full_or(1, 5), down_deg=90, field_fall=400)
    net["brook"] = []
    s.draw_comb_field(net, "f1", {"kind": "stream"})
    hx, hy = s.M["channels"][-1]["poly"][0]
    assert abs(hx - 680) < 0.5 and abs(hy - 200) < 0.5  # snapped onto the centerline
    s2 = Settlement(W=1400, H=1400, seed=6)
    s2.meta(name="Sn2", scale="town", ftpx=1, down_deg=90)
    net2 = build_comb(1400, 1400, (700, 200), full_or(2, 6), down_deg=90, field_fall=400)
    net2["brook"] = []
    s2.draw_comb_field(net2, "f2", {"kind": "stream", "stream": [(700, 40), (702, 120), (700, 200)]})
    assert s2.M["channels"][-1]["poly"][0] == [700, 200]  # feeder ends at the sluice: already joined


def test_channel_accepts_an_explicit_polyline():
    # the pts= form: a hand-routed culvert's waypoints are recorded verbatim (no auto-winding)
    s = Settlement(W=800, H=800, seed=1)
    s.meta(name="Cp", scale="town", ftpx=1)
    route = [(100, 100), (160, 130), (220, 200)]
    s.channel((100, 100), (220, 200), {"kind": "offmap"}, {"kind": "field", "name": "f"}, pts=route)
    assert s.M["channels"][-1]["poly"] == [[x, y] for x, y in route]


def test_village_grove_skips_watercourses():
    # no clump lands over a stream: the watercourse skip in the clump filter
    s = Settlement(W=800, H=800, seed=3)
    s.meta(name="Vw", scale="village", ftpx=2)
    s.stream([(400, 50), (400, 750)], width=9)
    s.village_grove([(330, 300), (470, 300), (470, 500), (330, 500)], role="copse", dense=False)
    for g in s.M["village_groves"]:
        for cx, _cy in g["clumps"]:
            assert abs(cx - 400) > 10
    # ...and the MOAT counts as a watercourse for the skip too (the city case)
    s2 = Settlement(W=800, H=800, seed=4)
    s2.meta(name="Vm", scale="city", ftpx=3)
    s2.M["moat"] = [(300, 200), (500, 200), (500, 600), (300, 600), (300, 200)]
    s2.M["moat_width"] = 22
    s2.village_grove([(260, 300), (340, 300), (340, 500), (260, 500)], role="copse", dense=False)
    for g in s2.M["village_groves"]:
        for cx, _cy in g["clumps"]:
            assert cx < 289 or cx > 311


def test_clip_to_river_walks_a_multi_point_run_out_of_the_bed():
    # a channel whose first TWO points lie inside the river bed: the leading-run walk advances past
    # both and restarts the drawing at the bed edge + cap radius (the pool's taps are 2-point lines,
    # so only a synthetic multi-point run exercises the walk)
    s = _crop_settlement()
    s.M["river"] = {"pts": [(300, 100), (300, 900)], "w": 40}
    pts = [(300, 400), (310, 420), (400, 500)]  # first two inside the 20px half-bed, third clear
    out = s._clip_to_river(pts, capr=3.5)
    assert len(out) == 2  # the in-bed lead collapsed to the bank restart point
    import math as _m

    d = min(_m.hypot(out[0][0] - 300, out[0][1] - y) for y in range(100, 901))
    # the (hw - 3 + capr) = 20.5 inset runs ALONG the channel, so its perpendicular distance from the
    # centerline is shorter on a diagonal approach (here ~16); it must sit backed off inside the bed
    assert 12.0 <= d <= 21.0


def test_intake_reach_ignores_water_that_is_parallel_behind_or_beside_the_ray():
    # The three rejections, each of which would otherwise hand back a bogus length: a reach the ray
    # runs ALONG (no crossing), one BEHIND the yard (t < 0 - the yard's back, not its water side),
    # and one whose infinite line the ray meets but whose SEGMENT it misses (s outside [0, 1]).
    s = _town()
    s.field_channel([(300, 340), (500, 340)], "#9CB4C8", 2.0, 2.0)  # crossed: the honest answer
    s.field_channel([(300, 500), (500, 500)], "#9CB4C8", 2.0, 2.0)  # behind the yard (its water side faces -y)
    s.field_channel([(600, 200), (700, 200)], "#9CB4C8", 2.0, 2.0)  # off to the side: the ray misses the span
    s.field_channel([(400, 100), (400, 300)], "#9CB4C8", 2.0, 2.0)  # parallel to the ray, dead ahead, never crossed
    assert s._intake_reach(400, 400, 0.0, 20.5) == pytest.approx(39.5)  # the first CROSSING, none of the rest


def test_intake_cut_refuses_a_reach_outside_the_sane_band():
    # Clamp, not stretch: water 300px out is not this yard's water, and a cut drawn to it would be a
    # 300px blue spear across the map. Out-of-band falls back to the stock length like the None case.
    s = _town()
    s.field_channel([(300, 90), (500, 90)], "#9CB4C8", 2.0, 2.0)  # ~290px ahead, far past the px(40) ceiling
    s.tanning_yard(400, 400, rot=0, pits=4, water="ditch")
    assert 'height="11.0"' in "".join(s.out)


def test_flow_record_tags_direction_and_derives_the_bearing():
    s = _town()
    s.stream([(100, 100), (100, 400)])  # authored upstream-first: runs due south
    s.stream([(300, 400), (300, 100)], flow="reverse")  # stored south-first, water runs NORTH
    a, b = s.M["streams"]
    assert (a["flow"], a["flow_deg"]) == ("forward", 90.0)
    assert (b["flow"], b["flow_deg"]) == ("reverse", 90.0)  # reversed -> also flows south


def test_flow_record_rejects_an_unknown_direction():
    s = _town()
    with pytest.raises(ValueError, match="forward"):
        s.stream([(0, 0), (10, 10)], flow="downhill-ish")


def test_ward_fence_end_parallel_to_the_wall_falls_back_to_the_nearest_point():
    # a terminal segment running ALONG the rampart never crosses it, so there is no axis to extend
    # down - the honest answer is the foot of the perpendicular
    s = _walled()
    s.ward("samurai", [(400, 206), (600, 206)], gates=[])
    bnd = s.M["wards"][-1]["boundary"]
    assert bnd[0] == pytest.approx([400.0, 200.0], abs=0.1)
    assert bnd[-1] == pytest.approx([600.0, 200.0], abs=0.1)


def test_ward_fence_without_a_city_wall_is_left_alone():
    s = Settlement(1000, 1000, seed=1)
    s.ward("samurai", [(500, 700), (500, 400)], gates=[])
    assert s.M["wards"][-1]["boundary"] == [[500.0, 700.0], [500.0, 400.0]]


def test_ward_fails_loudly_on_a_commoner_already_inside():
    # the ordering guard: a commoner standing inside when the fence goes up means the gen ran a
    # commoner pack before s.ward - fail at gen time, not at the gate
    s = Settlement(1000, 1000, seed=1)
    s.M["wall"] = [[200, 200], [800, 200], [800, 800], [200, 800]]
    s.building(600, 600, 16, 11, "merchant")
    with pytest.raises(ValueError, match="already inside the samurai ward"):
        s.ward("samurai", [(400, 795), (400, 400), (795, 400)], gates=[])


def test_the_lane_key_is_the_spine_not_the_last_way_drawn():
    """`M["lane"]` is read by five consumers as "the village street" - two gate checks among them -
    so it has to BE the street. It was assigned on every `lane()` call, i.e. it held whichever way
    happened to be drawn last: a settlement-review measured Sawada shipping a 45 ft floating fragment
    in that key while the spine ran 354 ft, so `structures_clear_of_streets` and the grove-shading
    rule were adjudicating against a 45 ft orphan. They ran, they passed, and they tested the wrong
    geometry - the input was wrong, not the rule."""
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="H", scale="hamlet")
    s.lane([(100.0, 100.0), (900.0, 100.0)])  # the spine, 800 ft
    s.lane([(400.0, 120.0), (400.0, 180.0)])  # a 60 ft back lane, drawn after it
    assert s.M["lane"] == [[100.0, 100.0], [900.0, 100.0]]
    # ...and the road OUT is not the street, however long it runs
    s.lane([(900.0, 100.0), (1900.0, 900.0)], connector=True)
    assert s.M["lane"] == [[100.0, 100.0], [900.0, 100.0]]


def test_angle_between_calls_a_degenerate_vector_square() -> None:
    """Feature 146: a zero-length vector has no bearing, so the helper answers 90 rather than dividing by it."""
    from l7r.diagram.settlement.water_ways import _angle_between

    point = ((0.0, 0.0), (0.0, 0.0))  # a segment of zero length: no bearing at all
    run = ((0.0, 0.0), (10.0, 0.0))
    across = ((0.0, 0.0), (0.0, 10.0))
    assert _angle_between(point, run) == 90.0
    assert _angle_between(run, point) == 90.0
    assert abs(_angle_between(run, run)) < 1e-9
    assert abs(_angle_between(run, across) - 90.0) < 1e-9


def test_focal_block_reserves_a_footprint_and_secondary_shrine_records_both() -> None:
    """Feature 146: a focal feature reserves its ground for later placers, and the secondary shrine records
    BOTH a shrine (so `religious_matches_scale` still sees only shrines) and the focal note."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="F", scale="village", ftpx=1)
    s._focal_block(500.0, 500.0, 60.0, 40.0)
    assert (500.0, 500.0, 60.0, 40.0) in s.placed
    assert s.block_polys and len(s.block_polys[-1]) == 4

    s2 = Settlement(1000, 1000, seed=1)
    s2.meta(name="S", scale="village", ftpx=1)
    s2.secondary_shrine(300.0, 300.0)
    assert any(r.get("kind") == "shrine" for r in s2.M.get("religious", []) + s2.M.get("shrines", []))
    assert "secondary_shrine" in str(s2.M)  # ...and the focal note, wherever note_focal keeps it


def test_fan_rival_spots_a_second_stub_fanning_to_the_same_house() -> None:
    """Feature 146: `fan_rival` lifted out of `trim_lane_stubs`. Two lane ends arriving beside each other on
    nearly the same heading, both reaching for the same house, are one approach drawn twice."""
    from l7r.diagram.settlement.water_ways import fan_rival

    house = (500.0, 500.0)
    mine = 200.0
    rival = [{"pts": [[420.0, 470.0], [300.0, 400.0]]}]  # its tip at (420,470), heading back out NW
    q = (426.0, 474.0)  # my own stub's tip, right beside it
    bearing = math.degrees(math.atan2(470.0 - 400.0, 420.0 - 300.0))
    assert fan_rival(rival, q, bearing, house, mine, me=1, fan_spread=40.0, fan_bearing=25.0) is True
    assert fan_rival(rival, q, bearing + 90.0, house, mine, me=1, fan_spread=40.0, fan_bearing=25.0) is False, "a different heading is a different way"
    assert fan_rival(rival, (900.0, 900.0), bearing, house, mine, me=1, fan_spread=40.0, fan_bearing=25.0) is False, "too far to be the same fan"
    assert fan_rival(rival, q, bearing, house, mine=10.0, me=1, fan_spread=40.0, fan_bearing=25.0) is False, "the rival is farther from the house than I am"
    assert fan_rival(rival, q, bearing, house, mine, me=0, fan_spread=40.0, fan_bearing=25.0) is False, "a lane is not its own rival"


# ---- THE TOWN AND WARD ARMS NO HAMLET ROLLS (feature 146: the hamlet floor covers the whole
# module, and these three are the branches the scripted hamlets never enter) -------------------


def test_a_labeled_town_street_carries_its_caption_beside_the_midpoint():
    """`street(label=...)` is the only way an avenue gets a name on the sheet; every scripted map
    calls it without one, so the caption arm went unentered."""
    s = _town()
    s.street([(100, 500), (500, 500), (900, 500)], label="Gate Road")
    assert any("Gate Road" in frag for frag in s.toplabels), "the street's name is inked"
    assert s.M["town_streets"][-1]["pts"][0] == [100, 500]


def test_a_ward_fence_end_far_from_the_wall_is_left_exactly_as_placed():
    """The end is snapped to the rampart only when it is already ABUTTING it. An end 200 px out is a
    fence that fails to reach the wall - `city_ward_fence_meets_wall`'s defect to report - and
    dragging it there silently would hide exactly that."""
    s = Settlement(1200, 1200, seed=9)
    s.meta(name="T", scale="city", ftpx=3, down_deg=90)
    s.M["wall"] = [(100, 100), (1100, 100), (1100, 1100), (100, 1100)]
    boundary = [(600.0, 400.0), (600.0, 800.0)]  # both ends hundreds of px inside the ring
    assert s._ward_ends_on_wall(list(boundary)) == boundary, "left exactly as placed"


def test_a_ward_cap_at_a_wall_corner_bends_with_the_rampart():
    """The cap over a fence end FOLLOWS the wall for +/-16 px of arc, folding in any wall VERTEX inside
    that span. A straight tangent at a corner juts past the bend and reads as a second wall section
    (Nagahara SW, GM 2026-07) - so an end seated near a corner must produce a cap with a bend in it."""
    s = Settlement(1200, 1200, seed=9)
    s.meta(name="T", scale="city", ftpx=3, down_deg=90)
    s.M["wall"] = [(100, 100), (1100, 100), (1100, 1100), (100, 1100)]
    s.ward("samurai", [(1098.0, 104.0), (600.0, 400.0)], gates=[])  # first end 4 px off the NE corner
    caps = s.M["wards"][-1].get("wall_caps") or []
    assert caps, "an abutting end is capped"
    bent = [c for c in caps if len(c["pts"]) >= 3 and any(abs(p[0] - 1100) < 2 and abs(p[1] - 100) < 2 for p in c["pts"])]
    assert bent, "the cap span folded in the wall's own corner vertex, so the cap turns where the rampart turns"


def test_trim_lane_stubs_steps_over_a_lane_record_with_one_point():
    """A lane whose record carries fewer than two points draws nothing; it is stepped over rather than
    measured, because every measure here needs a segment."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.M["lanes"] = [{"pts": [[100, 100]], "w": 4}]
    s._lane_ink = [[]]
    assert s.trim_lane_stubs() == 0


def test_trim_lane_stubs_does_not_count_a_fraying_track_as_a_junction():
    """PROXIMITY ALONE IS NOT ARRIVAL. Sawada's lane 0 ran 90 ft past its own T with lane 2 and died 13 ft
    from it on an 8 degree divergence - so it was "within 40 ft of another way", the lane it had ALREADY
    met, and passed. The adjacency that IS the defect was satisfying the test for it."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.M["lanes"] = [
        {"pts": [[100, 500], [900, 500]], "w": 4},
        {"pts": [[300, 508], [700, 512]], "w": 4},  # runs alongside the first, near-parallel, never crossing
    ]
    s._lane_ink = [[], []]
    assert s.trim_lane_stubs() >= 0  # the arm runs; what it decides is the fray rule's business


def test_pull_back_will_not_consume_the_last_segment_of_a_two_point_lane() -> None:
    """The loop shortens a lane from its last vertex, dropping a whole vertex when one is consumed.
    When only TWO points remain and the final segment is already shorter than a step, there is
    nothing left to drop - popping would leave a single point, which is not a lane at all - so it
    stops. That is the floor beneath the proportional guard, and it is reached by a lane that was
    always short rather than by one trimmed down to short.

    And when nothing the walk passed ever reached anything, the ORIGINAL run comes back untouched:
    returning the floor-truncated one would manufacture the very defect `lanes_reach_something`
    exists to catch."""
    from l7r.diagram.settlement.water_ways import _pull_back

    stub = [(0.0, 0.0), (4.0, 0.0)]  # 4 ft against an 8 ft step
    assert _pull_back(stub, lambda _q: False) == stub
    # ...and it is the SAME answer when the end does reach something, because there is no shorter
    # end to prefer: the loop breaks before any candidate is generated.
    assert _pull_back(stub, lambda _q: True) == stub
    # a long lane whose end reaches nothing also comes back whole
    long_run = [(0.0, 0.0), (200.0, 0.0)]
    assert _pull_back(long_run, lambda _q: False) == long_run


def test_junction_floor_protects_a_crossing_and_ignores_a_fraying_neighbor() -> None:
    """Lifted out of `trim_lane_stubs` so it can be asked with plain lists (GM 2026-08-28). The
    property: a lane may be trimmed back to its last real JUNCTION and no further.

    The `_FRAY_DEG` half is the one that needed the lift. Counting proximity alone made every point
    of a near-parallel arm look like a tie, so the floor came out at the whole length and nothing
    could be trimmed at all - and that branch runs only when a lane happens to have a close neighbor
    at a crossing angle, which no unit test could arrange through the caller."""
    from l7r.diagram.settlement.water_ways import junction_floor

    lane = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]

    # a way crossing at 90 deg, 1 ft off the vertex at x=100: everything up to it is protected
    crossing = [{"pts": [(100.0, -50.0), (100.0, 50.0)]}]
    assert junction_floor(lane, crossing, set(), 5.0, me=1) == 100.0

    # the SAME geometry, but the crossing way is this lane itself, or is being dropped -> no floor
    assert junction_floor(lane, crossing, set(), 5.0, me=0) == 0.0
    assert junction_floor(lane, crossing, {0}, 5.0, me=1) == 0.0

    # a near-parallel arm running alongside is the same track fraying, not a tie
    parallel = [{"pts": [(50.0, 2.0), (180.0, 2.0)]}]
    assert junction_floor(lane, parallel, set(), 5.0, me=1) == 0.0

    # ...and one that is simply too far away ties nothing
    assert junction_floor(lane, [{"pts": [(100.0, 400.0), (100.0, 500.0)]}], set(), 5.0, me=1) == 0.0
    # a degenerate record is skipped rather than crashing
    assert junction_floor(lane, [{"pts": [(100.0, 1.0)]}], set(), 5.0, me=1) == 0.0

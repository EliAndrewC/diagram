"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import os
import random
import tempfile

import pytest

from l7r.diagram.settlement import Settlement, surface_water_dist, village_population
from l7r.diagram.waterfields import polyline_cum, supply_bank_clearance
from tests.settlement._builders import _cap020, _crop_settlement, _town, crop


@pytest.mark.renders  # a test OF rendering (feature 213): it clears the suite's skip-render default for its first half
def test_png_width_env_overrides_render_resolution(monkeypatch):
    # DIAGRAM_PNG_WIDTH renders at a lower resolution for a quick iteration eyeball (raster cost is
    # ~quadratic in width); DIAGRAM_SKIP_RENDER skips it entirely (the test suite's default since
    # feature 213 - the gate reads the JSON, never the PNG). Committed maps still render at the full default width.
    from PIL import Image

    monkeypatch.delenv("DIAGRAM_SKIP_RENDER", raising=False)
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        monkeypatch.setenv("DIAGRAM_PNG_WIDTH", "400")
        _town().finish(base)  # render=True + env width -> the int(env_w) branch
        assert Image.open(base + ".png").width == 400
        base2 = os.path.join(d, "u")
        monkeypatch.setenv("DIAGRAM_SKIP_RENDER", "1")
        _town().finish(base2)  # skip env -> no raster even though render=True
        assert os.path.exists(base2 + ".svg") and not os.path.exists(base2 + ".png")


def test_village_population_draws_from_the_weighted_distribution():
    import random
    from collections import Counter

    pops = set(village_population(random.Random(i)) for i in range(300))
    assert pops <= {200, 250, 300, 350, 400, 450, 500}  # only the seven allowed sizes
    assert village_population(random.Random(3)) == village_population(random.Random(3))  # deterministic from the seed
    c = Counter(village_population(random.Random(i)) for i in range(4000))
    assert c.most_common(1)[0][0] == 350  # 350 is the mode


def test_crop_frames_hard_features_with_margin():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 40, "h": 30}]
    crop(s, margin=20)
    assert s.view == (460, 465, 80, 70)  # house 500 +/- (20/2) +/- 20 margin


def test_crop_covers_fields_pond_and_poly_features():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 20, "h": 20}]  # w/h branch
    s.M["groves"] = [{"poly": [[430, 430], [460, 430], [460, 460], [430, 460]]}]  # poly branch (a homestead grove still sets the frame)
    s.M["village_groves"] = [{"poly": [[300, 300], [350, 300], [350, 350], [300, 350]], "role": "windbreak"}]  # must NOT set the frame (GM 2026-07-20: the windbreak clips)
    s.M["fields"] = [{"outline": [[400, 400], [600, 400], [600, 600], [400, 600]], "vis_bbox": [420, 420, 580, 580]}]  # vis_bbox branch
    s.M["pond"] = [700, 700, 50, 40]  # pond branch
    s.M["wells"] = [{"x": 410, "y": 500, "r": 8}]  # r branch (latent bug 2026-07-20: wells set the frame too)
    crop(s, margin=0)
    assert s.view == (402, 420, 348, 320)  # well W (410-8), field N, pond E/S - the windbreak at 300 is CLIPPED


def test_crop_frames_a_torii_arch():
    # a torii arch is a visible structure: its TRUE-SCALE glyph box (torii_halfbox) must be inside the frame, so
    # a torii beyond the houses pushes the crop out to contain it (matches the hard_features_within_frame check).
    # At ftpx=1 the plan-view arch's half-box is (10, 3.28, 3.28) (feature 268), so the torii at y=640 reaches
    # its S edge at ~643 (the elevation glyph reached ~649, the legacy fixed box +18).
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 20, "h": 20}]  # hard core 490..510
    s.M["torii"] = [[500, 640, 1]]  # a gateway S of the houses
    crop(s, margin=0)
    assert s.view == (490, 490, 20, 153)  # x from houses/arch (490..510), S edge = torii y 640 + 3.28 rounded


def test_crop_uses_field_outline_when_no_vis_bbox():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 20, "h": 20}]
    s.M["fields"] = [{"outline": [[400, 400], [900, 400], [900, 900], [400, 900]]}]  # no vis_bbox -> falls back to outline
    crop(s, margin=0)
    assert s.view == (400, 400, 500, 500)


def test_crop_ignores_the_commons_which_just_clips_at_the_frame():
    # the commons scrub does NOT set the frame - it is drawn and simply CLIPS at the edge, so even a huge
    # commons overhanging the hard core on every side leaves the frame tight to the hard content + margin.
    # (The GM wants the frame tight to real content - the pond, a back-slope graveyard - never held open by
    # empty grazing: the Ueda-east grazing band past the lone pond used to bloat the frame ~130px.)
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 20, "h": 20}]  # hard core 490..510
    s.M["commons"] = [{"poly": [[200, 200], [800, 200], [800, 800], [200, 800]]}]  # huge, overhangs ALL four sides
    crop(s, margin=10)
    assert s.view == (480, 480, 40, 40)  # hard 490..510 + 10 margin; commons ignored


def test_rects_overlap_detects_overlap_and_separation():
    # the gate-furniture walk-outward uses rects_overlap (SAT); its True branch stopped being covered
    # incidentally once the gate guard house/inspection went TRUE SCALE (2026-07-22) and no longer
    # overlapped at their initial walk positions - so test it directly
    from l7r.diagram.settlement import rects_overlap

    a = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert rects_overlap(a, [(5, 5), (15, 5), (15, 15), (5, 15)]) is True  # corner-overlapping
    assert rects_overlap(a, [(20, 0), (30, 0), (30, 10), (20, 10)]) is False  # separated on x
    assert rects_overlap(a, [(0, 20), (10, 20), (10, 30), (0, 30)]) is False  # separated on y


def test_rng_scope_is_isolated_from_before_and_restores_after():
    def draw(perturb):
        s = Settlement(600, 500, seed=5)  # a FRESH map: the per-key counter starts at 0 in both runs
        for _ in range(perturb):
            random.random()  # an upstream change consuming extra draws
        with s.rng_scope("t", 1, 2):
            inside = [random.random() for _ in range(3)]
        return inside, random.random()

    a_in, a_after = draw(0)
    b_in, b_after = draw(1)
    assert a_in == b_in  # the scope cannot see what happened before it
    assert a_after != b_after  # ...and the outer stream is genuinely restored, not re-seeded


def test_rng_scope_gives_repeat_calls_on_one_key_their_own_numbers():
    # Two packs over the same ground must not draw the same "random" numbers, or they twin.
    s = Settlement(600, 500, seed=5)
    with s.rng_scope("pack", 0, 0, 10, 10):
        first = [random.random() for _ in range(3)]
    with s.rng_scope("pack", 0, 0, 10, 10):
        second = [random.random() for _ in range(3)]
    assert first != second
    other = Settlement(600, 500, seed=5)
    with other.rng_scope("pack", 0, 0, 10, 10):
        assert [random.random() for _ in range(3)] == first  # ...but a fresh map reproduces them


def test_crop_includes_forest_clamped_to_canvas():
    # the forest is a big EDGE feature recorded as a POINT-LIST (not dicts). On the axis it FACES, the crop
    # frames it CLAMPED to the canvas so the view never opens past the edge (an edge feature must REACH the
    # frame edge, not stop short). On the axis it RUNS ALONG - here N-S, off BOTH canvas ends - it sets
    # nothing, so that edge stays tight to the real content instead of being pinned to the canvas.
    s = Settlement(2000, 1500, seed=1)
    s.M["houses"] = [{"x": 30, "y": 700, "w": 20, "h": 20}]
    s.M["forest"] = [[1800, -10], [1820, 750], [1800, 1510], [2012, 1510], [2012, -10]]  # fills the E to canvas+12
    crop(s, margin=40)
    assert s.view == (0, 650, 2000, 100)  # E edge clamped to the canvas; N/S tight to the house


def test_crop_frames_a_forest_that_ends_inside_the_canvas():
    # ... but a tree line that STOPS inside the canvas bounds something real, so its own span is content
    s = Settlement(2000, 1500, seed=1)
    s.M["houses"] = [{"x": 30, "y": 700, "w": 20, "h": 20}]
    s.M["forest"] = [[1800, 300], [1820, 750], [1800, 1200], [2012, 1200], [2012, 300]]
    crop(s, margin=40)
    assert s.view == (0, 260, 2000, 980)


def test_crop_boxes_keeps_a_lone_forests_own_span():
    # a map with NOTHING but the wood has no other content to take its span from, so the run-along axis
    # falls back to the forest's own clamped span
    s = Settlement(2000, 1500, seed=1)
    s.M["forest"] = [[1800, -10], [1800, 1510], [2012, 1510], [2012, -10]]
    assert s._crop_boxes(city=False) == [(1800.0, 2000.0, 0.0, 1500.0, "forest")]


def test_crop_boxes_frames_the_windbreaks_inner_face_only_across_the_wind():
    """GM 2026-08-26 (feature 133 T10): the belt's inner FACE sets the frame - one line, across the
    wind - while the belt's depth and its shoulders still clip. Amends 2026-07-20."""
    from l7r.diagram.settlement._knobs import windbreak_face

    s = Settlement(2000, 1500, seed=1)
    s.M["houses"] = [{"x": 600, "y": 700, "w": 46, "h": 28}, {"x": 640, "y": 800, "w": 46, "h": 28}]
    clumps = [[400, y] for y in range(500, 1001, 50)] + [[440, y] for y in range(500, 1001, 50)] + [[480, 750]]
    s.M["village_groves"] = [{"x": 440, "y": 750, "w": 80, "h": 500, "rot": 0, "role": "windbreak", "r": 14.0, "clumps": clumps, "poly": []}]
    # x axis, houses to the east; the front row is 440 in ten of eleven 25 px bands and 480 in one,
    # so the face is the MEDIAN front (440) + r, not the one protruding clump (480)
    assert windbreak_face(clumps, 14.0, s.M["houses"]) == (0, 1, 454.0)
    boxes = s._crop_boxes(city=False)
    face = [b for b in boxes if "windbreak face" in b[4]]
    assert face == [(454.0, 454.0, 686.0, 814.0, "village_groves[0] windbreak face")]  # a line at the face, clamped to the houses' y extent
    s.M["village_groves"][0]["role"] = "copse"
    assert not [b for b in s._crop_boxes(city=False) if "windbreak" in b[4]]  # a copse never sets the frame
    assert windbreak_face([], 14.0, s.M["houses"]) is None and windbreak_face(clumps, 14.0, []) is None
    assert windbreak_face([[600, 200], [600, 240]], 14.0, s.M["houses"]) == (1, 1, 254.0)  # a belt to the NORTH faces south


def test_commons_and_marsh_skip_the_pond_and_watercourses():
    # ground-cover (scrub, reeds) never draws OVER open water: a big commons/marsh poly covering a pond + stream
    # skips those points at scatter time (the pond-check + _on_watercourse branches). Just assert it runs + records.
    for method in ("commons", "marsh"):
        s = Settlement(600, 600, seed=1)
        s.meta(name="W", scale="hamlet")
        s.M["pond"] = [300, 300, 60, 40]
        s.M["streams"] = [{"poly": [[80, 500], [520, 500]], "w": 10}]
        getattr(s, method)([(40, 40), (560, 40), (560, 560), (40, 560)])
        assert s.M["commons"] if method == "commons" else s.M["marshes"]


def test_archetype_knob_typing_rules():
    # field_archetype + land_use_overlay honor terrain typing (research.md D4)
    s = Settlement(1800, 1800, seed=1)
    s.meta(name="A", scale="village")
    # with no declared terrain, only valley_paddy is a coherent field archetype; a hill archetype pin is rejected
    s.pin_knob("field_archetype", "contour_terraces")
    with pytest.raises(ValueError):
        s.resolve("field_archetype")
    s2 = Settlement(1800, 1800, seed=1)
    s2.meta(name="A2", scale="village", terrain="hill")
    s2.pin_knob("field_archetype", "contour_terraces")
    assert s2.resolve("field_archetype") == "contour_terraces"  # hill terrain -> terraces allowed
    # tea_fringe overlay needs hill/terrace ground; lotus is fine anywhere
    s3 = Settlement(1800, 1800, seed=1)
    s3.meta(name="A3", scale="village")
    s3.pin_knob("land_use_overlay", "tea_fringe")
    with pytest.raises(ValueError):
        s3.resolve("land_use_overlay")
    s3.knob_pins.clear()
    s3._resolved_knobs.clear()
    s3.pin_knob("land_use_overlay", "lotus")
    assert s3.resolve("land_use_overlay") == "lotus"


def test_settlement_form_water_town_is_lion_gated():
    # water_town needs a canal, which is a Lion-lands feature per GM canon; the other forms are unrestricted
    s = Settlement(1200, 1200, seed=1)
    s.meta(name="Sf", scale="village")
    for form in ("nucleated", "linear", "dispersed"):
        s.knob_pins.clear()
        s._resolved_knobs.clear()
        s.pin_knob("settlement_form", form)
        assert s.resolve("settlement_form") == form
    s.knob_pins.clear()
    s._resolved_knobs.clear()
    s.pin_knob("settlement_form", "water_town")
    with pytest.raises(ValueError):
        s.resolve("settlement_form")  # no Lion / canal declared
    lion = Settlement(1200, 1200, seed=1)
    lion.meta(name="Sl", scale="village", clan="Lion")
    lion.pin_knob("settlement_form", "water_town")
    assert lion.resolve("settlement_form") == "water_town"


def test_settlement_form_dike_top_is_low_ground_gated():
    # dike_top stands ON a polder's perimeter dike, so the form needs the polder terrain (low reclaimed
    # ground); anywhere else the typing rule rejects it (research/contents.json#field-archetypes 'Polder waterward fringe + dike-top housing').
    dry = Settlement(1200, 1200, seed=1)
    dry.meta(name="Sd", scale="village", terrain="hill")
    dry.pin_knob("settlement_form", "dike_top")
    with pytest.raises(ValueError):
        dry.resolve("settlement_form")
    low = Settlement(1200, 1200, seed=1)
    low.meta(name="Sl", scale="village", terrain="low")
    low.pin_knob("settlement_form", "dike_top")
    assert low.resolve("settlement_form") == "dike_top"


def test_sluice_gate_label_names_the_black_bar():
    """The bare sluice glyph reads as a floating black bar at fit zoom (GM 2026-08-09) - most
    of a real gate is in the water, so the word does the explaining; label only when asked, so
    every existing map is byte-identical."""
    s1 = _cap020()
    n0 = len(s1.M.get("labels", []))
    s1.sluice_gate(500, 500, rot=30)
    assert len(s1.M.get("labels", [])) == n0  # unlabeled by default
    s2 = _cap020()
    s2.sluice_gate(500, 500, rot=30, label="sluice gate")
    s2.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    lab2 = [L for L in s2.M["labels"] if len(L) > 5 and L[5] == "sluice gate"]
    assert len(lab2) == 1
    s3 = _cap020()
    s3.sluice_gate(500, 500, rot=30, label="sluice gate", label_xy=(540, 480))
    s3.place_labels()  # feature 157: the LABEL PHASE
    lab3 = [L for L in s3.M["labels"] if len(L) > 5 and L[5] == "sluice gate"]
    assert len(lab3) == 1 and abs((lab3[0][0] + lab3[0][2]) / 2 - 540) < 2  # seated at the hand point
    s4 = _cap020()
    n4 = len(s4.top)
    s4.sluice_gate(500, 500, span=26)  # a 66 ft leat: the frame spans bank to bank
    assert 'x="-13.0"' in "".join(s4.top[n4:])  # the posts stand on the abutments, not mid-water


def test_a_homestead_may_not_stand_in_a_neighbours_drying_sun():
    """THE RATCHET for the sun corridor (GM 2026-08-13, researched in research/contents.json#homesteads).

    A minka's ~20 ft ridge throws 39 ft of shadow by 9am in the threshing month, so a farmhouse
    that close south of a yard takes its drying day. Three things are pinned: the rule is OFF by
    default (the whole hand-authored pool depends on that - turning it on re-packs every nucleated
    map), it refuses a bundle in BOTH directions once on, and it lets a homestead sit clear."""

    def bed():
        s = Settlement(1400, 1400, seed=3)
        s.meta(name="Sun", scale="hamlet", ftpx=1, toscale=True, households=12, nucleated=True)
        s._nucleated = True
        return s

    off = bed()
    assert off._sun_corridor_ok({"house": (700, 700, 46, 28), "yard": (700, 745, 37, 26)}), "OFF by default - the legacy pool depends on it"

    on = bed()
    on.sun_corridor(39)
    # a yard standing 20 ft north of this candidate house: the candidate would shade it
    on.M["houses"].append({"x": 700, "y": 600, "w": 46, "h": 28, "geom": {"yard": (700, 645, 37, 26)}})
    assert not on._sun_corridor_ok({"house": (700, 700, 46, 28), "yard": (700, 745, 37, 26)}), "a house may not shade a yard already placed"
    # ...and the mirror: a house already standing, and the candidate's own yard in its shadow
    on2 = bed()
    on2.sun_corridor(39)
    on2.M["houses"].append({"x": 700, "y": 800, "w": 46, "h": 28, "geom": None})
    assert not on2._sun_corridor_ok({"house": (700, 700, 46, 28), "yard": (700, 745, 37, 26)}), "a yard may not sit in a standing house's shadow"
    # ...and a homestead well clear of both is allowed
    on3 = bed()
    on3.sun_corridor(39)
    on3.M["houses"].append({"x": 700, "y": 900, "w": 46, "h": 28, "geom": {"yard": (700, 945, 37, 26)}})
    assert on3._sun_corridor_ok({"house": (700, 700, 46, 28), "yard": (700, 745, 37, 26)}), "clear ground must still be offered"


def _flat(runs):
    return [q for run in runs for q in run]


def test_supply_bank_clearance_is_past_at_the_strokes_exact_ends():
    # THE SEED-25 HAIRLINE (2026-08-16): the placer works in unrounded floats and exempted a
    # carved corner projecting epsilon PAST a branch tail; the manifest rounds both the corner
    # and the stroke poly to 0.1 px, collapsing them onto the same coordinates - the gate then
    # computed t = 1.0 exactly, `past` came back False, and the check fired at gap 0 on a corner
    # the placer had legally exempted. `past` is now arc-based with _PAST_EPS slack, so the
    # predicate gives ONE verdict on both sides of the round-trip.
    pts = [(0.0, 0.0), (60.0, 0.0), (100.0, 0.0)]
    cum = polyline_cum(pts)
    for q, want in (
        ((100.0, 0.0), True),  # exactly AT the tail: the rounding-collapse case
        ((0.0, 0.0), True),  # exactly at the head, symmetric
        ((100.4, 0.0), True),  # genuinely past the tail (the pre-fix rule already exempted this)
        ((99.0, 0.0), False),  # 1 px inside the tail: governed, as before
        ((50.0, 2.0), False),  # mid-span: governed, as before
    ):
        assert supply_bank_clearance(q, pts, 8.0, 3.0, cum)[2] is want, q


def test_the_indexed_water_answers_as_the_distance_does():
    """Feature 314: `surface_water_within`, asked of an index of the water's segments, says what `surface_water_dist <= reach`
    says - the streams, the canals, the moat and the pond's rim; an irrigation ditch never."""
    from l7r.diagram.settlement._geom.indexes import PointGrid
    from l7r.diagram.settlement.land.wet import surface_water_within, water_lines

    M = {
        "channels": [{"poly": [[0, 0], [100, 0]]}],
        "streams": [{"poly": [[0, 200], [100, 200], [180, 260]]}],
        "canals": [{"poly": [[400, 0], [400, 100]]}],
        "moat": [[0, 300], [100, 300]],
        "pond": [500.0, 500.0, 30.0, 20.0],
    }
    grid = PointGrid()
    grid.extend((a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for ln in water_lines(M) for a, b in zip(ln, ln[1:], strict=False))
    for x in range(-50, 650, 37):
        for y in range(-50, 650, 41):
            for reach in (15.0, 60.0):
                assert surface_water_within(M, x, y, reach, grid) == (surface_water_dist(M, x, y) <= reach), (x, y, reach)
    assert surface_water_within(M, 532, 500, 5.0, grid) and not surface_water_within({}, 532, 500, 5.0, PointGrid()), "the pond's rim"


def test_surface_water_dist_reads_the_checks_own_sources():
    """DOMESTIC water only: streams, canals, the moat and the pond rim - never an irrigation ditch.

    Ruled 2026-08-18. The predicate used to count `channels` too, which made the answer depend on
    which manifest key a watercourse was recorded under rather than on what kind of water it is: on
    a comb-field map `channels` holds one intake stub while the real watercourses live in
    `drawn_channels`, so Mizuguchi's well objective had ZERO clients and was silently optimizing
    nothing. The research says the exclusion is right and only the mechanism was accidental -
    domestic water came from a well or spring, ditch water served washing at a *kawado* stand.
    """
    M = {
        "channels": [{"poly": [[0, 0], [100, 0]]}],  # an irrigation ditch - NOT domestic water
        "streams": [{"poly": [[0, 200], [100, 200]]}],
        "pond": [500.0, 500.0, 30.0, 20.0],
    }
    assert surface_water_dist(M, 50, 40) == pytest.approx(160.0)  # the ditch 40 away does not count; the stream 160 away does
    assert surface_water_dist(M, 50, 180) == pytest.approx(20.0)  # nearest is the stream
    assert surface_water_dist(M, 560, 500) == pytest.approx(30.0)  # pond RIM (60 from center - rx 30)
    assert surface_water_dist({"channels": [{"poly": [[0, 0], [100, 0]]}]}, 50, 10) == 1e9  # a ditch ALONE is no water at all
    assert surface_water_dist({"channels": [], "streams": []}, 0, 0) == 1e9  # no surface water at all
    M["moat"] = [[0, 300], [100, 300]]
    assert surface_water_dist(M, 50, 310) == pytest.approx(10.0)  # the moat counts too
    assert surface_water_dist({"canals": [{"poly": [[0, 0], [100, 0]]}]}, 50, 25) == pytest.approx(25.0)  # a town canal is an open watercourse, and does


def test_crop_takes_reserved_ground_as_content():
    """Feature 150: the title pocket a full sheet reserves OUTSIDE its content is handed to the crop as
    content, so the frame holds it in; without it the crop hugs the houses alone."""
    s = _crop_settlement()
    s.M["houses"] = [{"x": 500, "y": 500, "w": 40, "h": 30}]
    crop(s, margin=10)
    x0, y0, _w, _h = s.view
    assert y0 > 300
    crop(s, margin=10, extra=[(400.0, 200.0, 600.0, 300.0)])
    assert s.view[1] <= 190 and s.view[0] <= 390


def test_an_l_shaped_belt_has_a_face_on_each_arm():
    """Feature 261 (settlement-review of Inashiro): a belt wrapped round the north and west of the houses has two inner
    faces, one per arm; a belt on one side has one, and a belt too small to split falls back to the whole."""
    from l7r.diagram.settlement._knobs import windbreak_faces

    houses = [{"x": 500.0, "y": 500.0}, {"x": 540.0, "y": 540.0}]
    west = [[300.0, 400.0 + 20 * k] for k in range(8)]
    north = [[400.0 + 20 * k, 300.0] for k in range(8)]
    faces = windbreak_faces(west + north, 14.0, houses)
    assert sorted(f[0][0] for f in faces) == [0, 1]
    assert [f[0][0] for f in windbreak_faces(west, 14.0, houses)] == [0]
    assert len(windbreak_faces(west[:3], 14.0, houses)) == 1, "an arm too small for a face of its own: the whole belt's"
    assert windbreak_faces([], 14.0, houses) == []

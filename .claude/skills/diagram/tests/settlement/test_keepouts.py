"""Feature 139: placement measures a field against a few chords of its outline and a dike against a few chords of
its crest - and both keep-outs must CONTAIN the drawn shape they stand in for, or a seat the gate refuses could
pass placement. The GM's bar: "a small number of line segments instead of thousands or even only dozens"."""

from __future__ import annotations

import math
import random

import pytest

from l7r.diagram.settlement import Settlement, point_in_poly
from l7r.diagram.settlement._geom.primitives import FIELD_KEEPOUT_EPS, chain_distance, chain_violated, edge_dist, facing_chains, keepout_ring, ring_offset, seg_dist, simplify_ring


def _wobbly_ring(rng: random.Random, n: int = 40, r: float = 300.0, wobble: float = 0.2) -> list[tuple[float, float]]:
    """A ring that WANDERS smoothly (three low harmonics, like a drawn dike or a comb envelope), not per-vertex noise:
    an outline the engine draws is a smoothed curve, never a saw."""
    a, b, c = rng.uniform(0, math.tau), rng.uniform(0, math.tau), rng.uniform(0, math.tau)
    out = []
    for k in range(n):
        u = k / n * math.tau
        rr = r * (1 + wobble * (0.5 * math.sin(2 * u + a) + 0.3 * math.sin(3 * u + b) + 0.2 * math.sin(5 * u + c)))
        out.append((800 + math.cos(u) * rr, 800 + math.sin(u) * rr))
    return out


def test_a_field_outline_becomes_a_handful_of_chords_that_contain_it() -> None:
    rng = random.Random(139)
    for _ in range(30):
        # drawn outlines are smoothed curves: harmonics up to 12% of the radius, never a saw (the real-map containment
        # is proved at the gate on the polder's drawn dike band and field - tests/gate/hamletgen/test_water.py)
        outline = _wobbly_ring(rng, rng.randint(20, 73), wobble=rng.choice((0.03, 0.08, 0.12)))
        keep, chords = keepout_ring(outline, outline, FIELD_KEEPOUT_EPS, filled=True)
        assert len(chords) <= len(outline)
        for x, y in outline:
            assert point_in_poly(x, y, keep), (x, y)
        # ...and the chords stay CLOSE to the outline: no outline vertex is farther than eps from the chords
        n = len(chords)
        for x, y in outline:
            assert min(seg_dist(x, y, chords[i], chords[(i + 1) % n]) for i in range(n)) <= FIELD_KEEPOUT_EPS + 1e-6


def test_a_gently_curved_outline_needs_only_a_few_chords() -> None:
    """The GM's count: "three ... maybe five or six" per side - a smooth 60-vertex outline comes back well under twenty."""
    outline = _wobbly_ring(random.Random(1), 60, wobble=0.1)
    assert 4 <= len(simplify_ring(outline, 6.0)) <= len(outline) // 2  # at a 6 px tolerance; the GM's count is for the FACING chain at the engine's tolerance (the test below)


def test_the_dike_keep_out_contains_the_drawn_band_on_a_harsh_ring() -> None:
    """The crest's chords pushed out by the band's MEASURED reach: every vertex of the smoothed band inside."""
    s = Settlement(1600, 1600, seed=3)
    s.meta(name="D", scale="hamlet")
    before = len(s.block_polys)
    s.perimeter_dike(_wobbly_ring(random.Random(5), 24, 350.0, 0.08), seed=3)  # a drawn dike wanders gently; the polder's real band is proved at the gate
    keep = s.block_polys[before]
    dk = s.M["dikes"][0]
    assert dk["keepout"] == [[round(p[0], 1), round(p[1], 1)] for p in keep]
    assert dk["keepout_chords"] <= 40 and len(keep) < len(dk["outline"]) / 10, (dk["keepout_chords"], len(keep), len(dk["outline"]))
    outside = [(x, y) for x, y in dk["outline"] if not point_in_poly(x, y, keep)]
    assert not outside, f"{len(outside)} of {len(dk['outline'])} band vertices fall outside the keep-out, e.g. {outside[:3]}"


def test_ring_offset_pushes_out_and_in() -> None:
    sq = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    ring = ring_offset(sq, 10.0, 5.0)
    assert len(ring) == 10  # 4 outer, the closing pair, 4 inner
    assert point_in_poly(50.0, -5.0, ring) and point_in_poly(50.0, 3.0, ring) and not point_in_poly(50.0, 8.0, ring)


def test_simplify_ring_keeps_a_tiny_ring_and_the_fields_record_their_chords_at_finish(tmp_path) -> None:  # type: ignore[no-untyped-def]
    assert simplify_ring([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)], 2.0) == [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
    s = Settlement(600, 600, seed=1)
    s.meta(name="F", scale="hamlet")
    s.M["fields"] = [{"name": "f", "kind": "paddy", "bbox": [100, 100, 500, 500], "outline": [[100, 100], [500, 100], [500, 500], [100, 500]]}]
    s.finish(str(tmp_path / "f"), render=False)
    assert s.M["fields"][0]["keepout_chords"] == 4 and len(s.M["fields"][0]["keepout"]) == 4  # no seat: the filled ring
    s2 = Settlement(600, 600, seed=1)
    s2.meta(name="F", scale="hamlet")
    s2.field_face = (300.0, 20.0)
    s2.M["fields"] = [{"name": "f", "kind": "paddy", "bbox": [100, 100, 500, 500], "outline": [[100, 100], [500, 100], [500, 500], [100, 500]]}]
    s2.finish(str(tmp_path / "g"), render=False)
    assert s2.M["fields"][0]["keepout_chords"] == 1  # a seat: the one chord facing it (the gate reads the placer's own chains, M["field_chains"])


def test_the_facing_chains_are_few_open_and_never_looser_than_the_outline_on_the_house_side() -> None:
    """The GM's design: a few chords on the house side, open, judged by side and distance. Never looser: no vertex
    of the drawn outline is on the house side of a chord it projects onto, and every probe the chain ACCEPTS at
    the rule's gap is outside the outline and at least that gap from it (within the chain's reach)."""
    rng = random.Random(139)
    for _ in range(25):
        outline = _wobbly_ring(rng, rng.randint(30, 73), wobble=rng.choice((0.05, 0.08, 0.12)))
        ang = rng.uniform(0, math.tau)
        seat = (800 + math.cos(ang) * 600, 800 + math.sin(ang) * 600)
        chains = facing_chains(outline, seat, FIELD_KEEPOUT_EPS)
        assert 1 <= len(chains) <= 2 and 2 <= sum(len(c) for c in chains) <= 12, [len(c) for c in chains]
        for x, y in outline:
            if chain_distance(x, y, chains) <= FIELD_KEEPOUT_EPS + 1e-6:  # a vertex the chain reaches (past a chain's end the far sides are the crop plots' business)
                assert chain_violated(x, y, chains, FIELD_KEEPOUT_EPS + 1e-6), (x, y)  # never on the house side: a bay vertex fails by sign, a corner vertex by the push-out distance
        gap = 14.0

        def projects(px: float, py: float, chains: list = chains) -> bool:  # type: ignore[type-arg]  # does the probe project onto some chord? (past every chord's end the far sides are the crop plots' business)
            for chain in chains:
                for (ax, ay), (bx, by), _n in chain:
                    ex, ey = bx - ax, by - ay
                    t = ((px - ax) * ex + (py - ay) * ey) / (ex * ex + ey * ey)
                    if 0.0 <= t <= 1.0:
                        return True
            return False

        for _k in range(300):
            px, py = rng.uniform(300, 1300), rng.uniform(300, 1300)
            if not projects(px, py) or chain_violated(px, py, chains, gap):
                continue
            assert not point_in_poly(px, py, outline) and edge_dist(px, py, outline) >= gap - 1e-6, (px, py)


def test_a_field_is_measured_by_chains_when_the_seat_is_known_and_by_a_ring_when_not() -> None:
    s = Settlement(900, 900, seed=1)
    s.meta(name="F", scale="hamlet")
    field = _wobbly_ring(random.Random(2), 60, 250.0, 0.08)
    field = [(x - 350, y - 350) for x, y in field]  # centered near (450, 450)
    s.field_polys.append(field)
    chains, rings = s._field_chains()
    assert not chains and len(rings) == 1  # no seat planned: a closed simplified ring
    s.field_face = (450.0, 60.0)  # the cluster stands north of the field
    chains, rings = s._field_chains()
    assert chains and not rings and sum(len(c) for c in chains) < 10
    assert s._field_blocks_point(450.0, 450.0, 14.0)  # the middle of the field
    assert s._field_blocks_point(450.0, 120.0, 14.0) is False  # well north of it
    assert s._field_blocks_rect((450.0, 450.0, 40.0, 26.0)) and not s._field_blocks_rect((450.0, 100.0, 40.0, 26.0))


def test_field_within_measures_by_the_chains_when_the_seat_is_known() -> None:
    """`_field_within` (feature 145): with a planned seat the reach is measured to the CHORDS, not to a ring."""
    s = Settlement(900, 900, seed=1)
    s.meta(name="F", scale="hamlet")
    s.field_polys.append([(300.0, 300.0), (600.0, 300.0), (600.0, 600.0), (300.0, 600.0)])
    s.field_face = (450.0, 60.0)  # the cluster stands north of the field
    assert s._field_chains()[0], "the fixture must give chains, not a ring"
    assert s._field_within(450.0, 280.0, 40.0) is True  # 20 px north of the facing chord, inside the reach
    assert s._field_within(450.0, 100.0, 40.0) is False  # 200 px north of it


def test_a_noisy_band_takes_no_more_chords_than_the_cap_and_still_contains_every_point() -> None:
    """Feature 287, homes H27: a 400-vertex noisy ring at the dike's own tolerance simplifies to at most 24 chords for the
    keep-out and at most 12 for the facing chains, and the keep-out still contains every covered point."""
    from l7r.diagram.settlement._geom.primitives import FACING_CHORD_CAP, KEEPOUT_CHORD_CAP

    rng = random.Random(7)
    ring = [(500.0 + (300.0 + rng.uniform(-40.0, 40.0)) * math.cos(2 * math.pi * k / 400), 500.0 + (300.0 + rng.uniform(-40.0, 40.0)) * math.sin(2 * math.pi * k / 400)) for k in range(400)]
    assert len(simplify_ring(ring, 1.0)) > KEEPOUT_CHORD_CAP, "the case: the tolerance alone takes more than the cap"
    keepout, chords = keepout_ring(ring, ring, 1.0)
    assert len(chords) <= KEEPOUT_CHORD_CAP
    outer = keepout[: len(chords)]
    assert all(point_in_poly(x, y, outer) or edge_dist(x, y, outer) < 1e-6 for x, y in ring)
    chains = facing_chains(ring, (1500.0, 500.0), 1.0)
    assert 1 <= sum(len(c) for c in chains) <= FACING_CHORD_CAP


def test_a_band_the_inner_tolerance_misses_at_an_acute_corner_is_contained_all_the_same(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes wave 5 (the polder soak's `test_the_polder_dikes_keep_out_contains_its_drawn_band`): the inner
    edge's tolerance is a heuristic - at an acute corner of the crest the band's inner corner stands 38.6 px in, and the
    un-mitered inner edge reaches 19.5. The ring is asked of every covered point and pushed until it holds them all; past
    `KEEPOUT_GROWTHS` pushes the band is refused by name, never a ring that leaves part of it out."""
    from shapely.geometry import Polygon

    from l7r.diagram.settlement._geom import primitives

    crest = [(0.0, 0.0), (400.0, 0.0), (200.0, 60.0)]  # a sliver: the apex at (0, 0) turns through ~163 degrees
    inner = [(float(x), float(y)) for x, y in Polygon(crest).buffer(-6.0, join_style=2).exterior.coords[:-1]]
    band = crest + inner
    old = ring_offset(crest, 1.0, 6.0 + 3.0)
    assert not all(point_in_poly(x, y, old) for x, y in band), "the case: the heuristic ring leaves the band's inner corner out"
    keep, chords = keepout_ring(crest, band, 1.0)
    assert chords == crest and all(point_in_poly(x, y, keep) for x, y in band)
    monkeypatch.setattr(primitives, "KEEPOUT_GROWTHS", 1)
    with pytest.raises(ValueError, match="contains its band"):
        keepout_ring(crest, band, 1.0)


def test_ring_offset_takes_a_hairpin_on_its_first_edge() -> None:
    """A vertex where the ring doubles straight back has no miter: its push falls back to the first edge's normal."""
    hairpin = [(0.0, 0.0), (100.0, 0.0), (0.0, 0.0), (0.0, 100.0)]
    ring = ring_offset(hairpin, 10.0, 5.0)
    assert len(ring) >= 8 and all(math.isfinite(c) for q in ring for c in q)


# ---- feature 310: no canopy tree in a yard's or bed's sun (GM 2026-10-02) ----------------------------------------


def _sunny(seed: int = 1) -> Settlement:
    s = Settlement(1000, 1000, seed=seed)
    s.meta(name="S", scale="hamlet", ftpx=1)
    s.sun_corridor(39)
    return s


def test_the_sun_keepouts_are_every_plots_sun_ground_near_the_box_on_a_map_that_keeps_the_sun() -> None:
    """The drawn plots and every placed bundle's, as `sun_box` boxes, those meeting the box only; none where the map keeps no
    sun corridor."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT, sun_box

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1)
    s.M["threshing_yards"] = [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 20.0}]
    assert s._sun_keepouts((0.0, 0.0, 1000.0, 1000.0)) == [], "off without the sun corridor"
    s.sun_corridor(39)
    yard = sun_box((500.0, 500.0, 40.0, 20.0), CANOPY_SHADE_FT)
    assert s._sun_keepouts((0.0, 0.0, 1000.0, 1000.0)) == [yard]
    s.M["houses"].append({"x": 200.0, "y": 200.0, "w": 40.0, "h": 30.0, "geom": {"boxes": {"yard": (200.0, 240.0, 30.0, 20.0), "gardens": [(250.0, 200.0, 14.0, 20.0)]}}})
    s.M["houses"].append({"x": 900.0, "y": 900.0, "w": 40.0, "h": 30.0, "geom": {"yard": None, "gardens": [(940.0, 900.0, 14.0, 20.0)]}})
    got = s._sun_keepouts((0.0, 0.0, 1000.0, 1000.0))
    assert len(got) == 4 and sun_box((200.0, 240.0, 30.0, 20.0), CANOPY_SHADE_FT) in got, "a bundle's yard and beds, a yardless bundle's bed"
    assert s._sun_keepouts((0.0, 0.0, 100.0, 100.0)) == [], "none meets a box far off"


def test_a_planted_dikes_trees_in_a_plots_sun_are_taken_out_once_the_plots_stand() -> None:
    """`_plant_run` records the trees with the string's place; `thin_planted_trees` rewrites the string without each tree in a
    plot's sun, keeps every bush and tag, and records what it kept. A run with no tree is left as it was."""
    s = _sunny()
    near, far = (560.0, 500.0, 5.0), (900.0, 100.0, 5.0)
    pieces = ["<g>", "<circle near/>", "<circle bush/>", "<circle far/>", "</g>"]
    z = s._plant_run("willow", pieces, [None, near, None, far, None], "perimeter dike")
    bare = s._plant_run("fruit", ["<g>", "</g>"], [None, None], "fruit dike")
    assert s.M["planted_trees"][0]["trees"] == [[560.0, 500.0, 5.0], [900.0, 100.0, 5.0]]
    s.M["threshing_yards"] = [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 20.0}]
    assert s.thin_planted_trees() == 1
    assert s.out[z] == "<g><circle bush/><circle far/></g>" and s.out[bare] == "<g></g>"
    assert s.M["planted_trees"][0]["trees"] == [[900.0, 100.0, 5.0]]


def test_a_planted_tree_within_the_pad_of_a_plots_sun_is_taken_out() -> None:
    """The sun ground is fetched over the reach the crown test asks - the crown AND `CANOPY_PAD` - so a tree whose crown stops
    0.3 px short of a yard's sun box, inside the pad, is taken out (fetched over the radius alone, that box was never asked)."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT

    s = _sunny()
    s.M["threshing_yards"] = [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 20.0}]
    edge = 500.0 + 20.0 + CANOPY_SHADE_FT  # the sun box's east edge
    z = s._plant_run("willow", ["<g>", "<circle t/>", "</g>"], [None, (edge + 5.3, 500.0, 5.0), None], "perimeter dike")
    assert s.thin_planted_trees() == 1 and s.out[z] == "<g></g>"


def test_a_fixture_is_held_off_a_band_as_its_record_will_read() -> None:
    """Cohort seed 5 (2026-10-02): the check reads a fixture's turned box from its record, rounded to 0.1 - so the placer asks
    the same box (`recorded_box`), and a turn that clears at full precision but meets in the record is refused."""
    from l7r.diagram.settlement.rolling.fit import recorded_box

    x, y, w, h = recorded_box((2264.94, 1014.83, 24.0, 12.0), 13.8)
    assert (x, y) == (2264.9, 1014.8) and abs(h - (24.0 * math.sin(math.radians(13.8)) + 12.0 * math.cos(math.radians(13.8)))) < 1e-9


def test_every_crown_site_keeps_out_of_a_plots_sun() -> None:
    """A windbreak planted over a garden draws no crown in the garden's sun ground, and a wood beside a yard none in the yard's -
    the crown tests read `_sun_keepouts` (feature 310)."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT, trees_shading_plots
    from tests.settlement._builders import _nuc_village

    s = _nuc_village()
    s.sun_corridor(39)
    s.M["gardens"] = [{"x": 500.0, "y": 500.0, "w": 30.0, "h": 20.0}]
    s.village_grove([(380, 380), (620, 380), (620, 620), (380, 620)], role="windbreak")
    assert len(s.M["tree_crowns"]) > 0, "non-vacuity: the windbreak drew crowns"
    assert trees_shading_plots(s.M, CANOPY_SHADE_FT) == []
    w = _sunny(2)
    w.M["threshing_yards"] = [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 20.0}]
    w._draw_stand([(420, 420), (600, 420), (600, 600), (420, 600)], 3, True)  # drawn as at crop time
    assert len(w.M["tree_crowns"]) > 0 and trees_shading_plots(w.M, CANOPY_SHADE_FT) == []


def test_the_sun_keepouts_take_a_reach_of_their_own() -> None:
    """Feature 315: `_sun_keepouts(bbox, reach_ft)` - bamboo's reach, or any other, in place of the canopy reach."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT, sun_box

    s = _sunny()
    s.M["threshing_yards"] = [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 20.0}]
    assert s._sun_keepouts((0.0, 0.0, 1000.0, 1000.0), BAMBOO_SHADE_FT) == [sun_box((500.0, 500.0, 40.0, 20.0), BAMBOO_SHADE_FT)]
    assert s._sun_keepouts((0.0, 0.0, 1000.0, 1000.0), 10.0) == [sun_box((500.0, 500.0, 40.0, 20.0), 10.0)]


def test_a_nudged_beds_sun_ground_is_clear_of_every_standing_tree_promised_seat_and_bamboo_mark() -> None:
    """Feature 315 (cohort seed 14): a bed slid south after the groves stand may not take a drawn crown, a persimmon promised a
    seat or a bamboo mark into its sun ground."""
    from l7r.diagram.settlement.rolling.farmsteads import beds_sun_clear

    bed = [(0.0, 0.0, 20.0, 20.0)]  # sun ground x -60..60, y -10..60 at a reach of 50
    assert beds_sun_clear(bed, [], [], [], 50.0, 50.0)
    assert not beds_sun_clear(bed, [0.0, 65.0, 6.0], [], [], 50.0, 50.0), "a drawn crown south"
    assert not beds_sun_clear(bed, [], [(65.0, 0.0, 6.0)], [], 50.0, 50.0), "a promised persimmon east"
    assert not beds_sun_clear(bed, [], [], [[-62.0, 10.0, 3.0]], 50.0, 50.0), "a bamboo mark west"
    assert beds_sun_clear(bed, [0.0, -30.0, 6.0], [(80.0, 0.0, 6.0)], [[0.0, 75.0, 3.0]], 50.0, 50.0), "each clear of it"

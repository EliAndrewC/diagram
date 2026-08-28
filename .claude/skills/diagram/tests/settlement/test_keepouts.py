"""Feature 139: placement measures a field against a few chords of its outline and a dike against a few chords of
its crest - and both keep-outs must CONTAIN the drawn shape they stand in for, or a seat the gate refuses could
pass placement. The GM's bar: "a small number of line segments instead of thousands or even only dozens"."""

from __future__ import annotations

import math
import random

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

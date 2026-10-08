"""`dike_gaps_at_channels` with the ring's edges boxed once (feature 306): the same gaps, in the same order, as the scan
of every channel segment against every ring edge - kept here as the ORACLE - and shown to notice a dropped edge."""

import math
import random

import pytest

from l7r.diagram.hamletgen.water import polder as PO
from l7r.diagram.settlement import PointGrid, seg_intersect, segments_cross


def _gaps_scan(ring, channels, sluices):  # type: ignore[no-untyped-def]
    """`dike_gaps_at_channels` before feature 306, verbatim."""
    gaps = list(sluices)
    for ch in channels:
        pts = ch["pts"]
        for i in range(len(pts) - 1):
            for k in range(len(ring)):
                a, b = ring[k], ring[(k + 1) % len(ring)]
                if segments_cross(tuple(pts[i]), tuple(pts[i + 1]), a, b):
                    hit = seg_intersect(tuple(pts[i]), tuple(pts[i + 1]), a, b)
                    if hit is not None and not any(math.hypot(hit[0] - g[0], hit[1] - g[1]) < 30 for g in gaps):
                        gaps.append(hit)
    return gaps


def _rolled(seed: int):  # type: ignore[no-untyped-def]
    """A ragged 49-vertex ring and eight wandering channels that run in, out and across it - and one dead straight along
    a ring edge's own line, the degenerate case."""
    rng = random.Random(seed)
    ring = [(500 + math.cos(t) * r, 500 + math.sin(t) * r) for t, r in ((math.tau * k / 49, rng.uniform(250, 400)) for k in range(49))]
    channels = []
    for _ in range(8):
        x, y = rng.uniform(0, 1000), rng.uniform(0, 1000)
        pts = [[x, y]]
        for _ in range(13):
            x, y = x + rng.uniform(-120, 120), y + rng.uniform(-120, 120)
            pts.append([x, y])
        channels.append({"pts": pts})
    channels.append({"pts": [list(ring[3]), list(ring[4])]})
    return ring, channels, [ring[0], ring[20]]


@pytest.mark.parametrize("seed", range(8))
def test_the_boxed_ring_finds_the_gaps_the_scan_found_in_its_order(seed: int) -> None:
    ring, channels, sluices = _rolled(seed)
    want = _gaps_scan(ring, channels, sluices)
    assert len(want) > len(sluices), "non-vacuous: a channel crosses the ring"
    assert PO.dike_gaps_at_channels(ring, channels, sluices) == want


def test_the_oracle_notices_a_dropped_edge(monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparison above would fail if the grid omitted an edge a channel crosses: a grid that never returns the
    edges filed first gives a different list."""
    ring, channels, sluices = _rolled(0)

    class Short(PointGrid):
        def near(self, px, py, pad=0.0):  # type: ignore[no-untyped-def]
            return [e for e in super().near(px, py, pad) if e[0] % 2]

    monkeypatch.setattr(PO, "PointGrid", Short)
    assert PO.dike_gaps_at_channels(ring, channels, sluices) != _gaps_scan(ring, channels, sluices)

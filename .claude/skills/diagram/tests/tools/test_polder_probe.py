"""The polder probe reports the block's own numbers, and agrees with the map (feature 147, US1).

The last test is the one that matters: a diagnostic that re-implements the geometry it measures can pass
while the map fails, which is worse than no diagnostic. The probe builds through `plan_site` + `fit_polder`
- the path `stage_polder` takes - and this asserts the numbers it prints are the numbers the rolled map
carries.
"""

from __future__ import annotations

import json
import pathlib

from l7r.diagram.tools import polder_probe as pp

SKILL = pathlib.Path(__file__).resolve().parents[2]


def _ring(x0: float, y0: float, x1: float, y1: float, n: int = 8) -> list[tuple[float, float]]:
    """A rectangle's perimeter, sampled - the shape a parcel outline has."""
    return (
        [(x0 + (x1 - x0) * i / n, y0) for i in range(n)]
        + [(x1, y0 + (y1 - y0) * i / n) for i in range(n)]
        + [(x1 - (x1 - x0) * i / n, y1) for i in range(n)]
        + [(x0, y1 - (y1 - y0) * i / n) for i in range(n)]
    )


def _organic(cx: float, cy: float, rx: float, ry: float, n: int = 32) -> list[tuple[float, float]]:
    """A wandering closed outline with no square corner - what a hand-piled parcel looks like to
    `_sharp_corners` (a sampled rectangle still scores 4, which is the point of the rule)."""
    import math

    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _net(rings: list[list[tuple[float, float]]], channels: list[list[tuple[float, float]]]) -> dict[str, object]:
    return {
        "plots": [{"poly": r, "fill": "#000", "low": False} for r in rings],
        "channels": [{"pts": c, "w": 4.0, "w_tail": 3.0} for c in channels],
        "acres": 12.0,
    }


def test_measure_reports_the_blocks_own_geometry() -> None:
    net = _net(
        [_ring(100.0, 100.0, 400.0, 700.0)], [[(60.0, 60.0), (60.0, 740.0)]]
    )  # a channel 40 ft clear to the west (a ruled ring here on purpose: this test is about the measures, not the verdict)
    m = pp.measure(net, target_acres=13.0, ftpx=2.0)
    assert m["parcels"] == 1
    assert m["overlaps"] == []
    assert m["berm_min"] == 38.0  # 100 - 60 - w/2
    assert m["vertices_min"] == 32
    assert m["ring_points"][0] == 32
    assert m["acres_target"] == 13.0


def test_verdict_names_every_metric_that_would_fail_the_gate() -> None:
    through = _net([_ring(100.0, 100.0, 400.0, 700.0)], [[(200.0, 60.0), (200.0, 740.0)]])  # straight through the parcel
    bad = pp.verdict(pp.measure(through, 13.0))
    assert bad and "overlap a channel" in bad[0]

    ruled = _net([[(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]], [])  # a ruled quad: 4 vertices, 4 square corners
    bad2 = pp.verdict(pp.measure(ruled, 13.0))
    assert any("under 12 vertices" in b for b in bad2)
    assert any("square-corner mean" in b for b in bad2)

    clean = _net([_organic(250.0, 400.0, 150.0, 300.0)], [[(60.0, 60.0), (60.0, 740.0)]])
    assert pp.verdict(pp.measure(clean, 13.0)) == []


def test_the_probe_agrees_with_the_rolled_map() -> None:
    """THE GUARD AGAINST A SECOND IMPLEMENTATION. Kuwabata is seed 21, 16 households, mosaic - the probe
    builds the same block, so its parcel count and acreage must be the map's. If this ever fails, the probe
    has drifted from the engine and every number it prints is a guess."""
    man = json.loads((SKILL / "pool" / "hamlets" / "kuwabata.json").read_text())
    m, secs = pp.probe(seed=21, households=16, pond_layout="mosaic")
    assert m["parcels"] == len(man["fields"][0]["plot_rings"])
    assert m["overlaps"] == [], "the shipped map has no parcel across a channel; the probe must agree"
    # A LOOSE CEILING ON PURPOSE. SC-001's bar (about a second) is measured by hand and recorded in the
    # skill's command map; asserting it here failed at 3.09 s the first time the gate ran the suite 16-way
    # parallel, because a stopwatch inside a loaded test run measures the load. This catches only a
    # catastrophe - the probe having quietly become a map roll.
    assert secs < 20.0, f"the probe is the FAST path and took {secs:.1f}s - has it started rolling a map?"

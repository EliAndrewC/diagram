"""Feature 287 (water W13-W15): the comb holds its trunks - the collector and the main canals - to the rules the
finished-map tests used to measure, by construction (`comb._comb_drain`) and by repair (`trunks.anchor_trunk_ends`). Each
test drives the placer on constructed inputs that include the violating case and asks the rule's one predicate in
`waterfields/trunks.py`."""

from __future__ import annotations

from types import SimpleNamespace

from l7r.diagram.waterfields.comb import _comb_drain
from l7r.diagram.waterfields.frame import _Frame
from l7r.diagram.waterfields.trunks import (
    DRAIN_MIN_LEG,
    SHARP_TURN_DEG,
    UPHILL_SLACK,
    anchor_trunk_ends,
    end_anchored,
    outfall_rise,
    sharpest_turn,
)


class _Scripted:
    """A random stream whose draws are scripted per (low, high) range, in order; an unscripted draw returns the top of
    its range - the worst case for a jitter."""

    def __init__(self, script: dict[tuple[float, float], list[float]]) -> None:
        self.script = {k: list(v) for k, v in script.items()}

    def uniform(self, a: float, b: float) -> float:
        queue = self.script.get((a, b))
        return queue.pop(0) if queue else b


def _thread(u: float, bottom: float) -> SimpleNamespace:
    """A delivery column at contour `u` whose ditch is dug to fall `bottom` (on a 90 deg fall, u is x and f is y)."""
    return SimpleNamespace(pts=[(u, 0.0), (u, bottom), (u, bottom + 400.0)], ditch_f=bottom, f0=0.0)


def test_the_predicates_read_the_fall_and_the_turn() -> None:
    assert abs(outfall_rise([(0.0, 0.0), (100.0, 5.0)], 90.0) - 5.0) < 1e-9
    assert abs(outfall_rise([(0.0, 5.0), (100.0, 0.0)], 90.0) + 5.0) < 1e-9
    assert sharpest_turn([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]) == 90.0
    assert sharpest_turn([(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)]) == 0.0, "a leg with no length turns nothing"


def test_a_collector_never_runs_uphill_even_where_its_head_draws_the_worst_jitter() -> None:
    """W13: one ditch bottom puts the outfall only 40 px on at the fitted line's least slope (0.06) - 2.4 px down the
    fall - and every jitter here draws +6, the most. The head takes none: it sits on the fitted line, so the outfall is
    down the fall of it by construction. (It used to take the +6, and the collector ran 3.6 px uphill.)"""
    dpts = _comb_drain(_Scripted({}), _Frame(90.0), [_thread(500.0, 300.0)], 3200.0, 2600.0, 2.0, [])
    assert outfall_rise(dpts, 90.0) >= -UPHILL_SLACK
    assert abs(outfall_rise(dpts, 90.0) - 0.06 * 40.0) < 1e-6


def test_the_collector_draws_no_hook_into_its_outfall() -> None:
    """W14: the samples step 150, 150 and then 138 px - the last landing 2 px short of the outfall, where its +6 jitter
    turned the final leg back on itself. No sample is drawn within `DRAIN_MIN_LEG` of the outfall, so every leg is long
    and no vertex turns hard."""
    R = _Scripted({(120, 170): [150.0, 150.0, 138.0, 150.0]})
    threads = [_thread(100.0, 300.0), _thread(500.0, 320.0)]  # ditch bottoms 400 px apart: the outfall at u = 540
    dpts = _comb_drain(R, _Frame(90.0), threads, 3200.0, 2600.0, 2.0, [])
    assert sharpest_turn(dpts) < SHARP_TURN_DEG
    assert dpts[-1][0] - dpts[-2][0] >= DRAIN_MIN_LEG
    assert [round(p[0]) for p in dpts] == [100, 250, 400, 540], "the sample at 538 is drawn and discarded"
    assert all(outfall_rise([p, dpts[-1]], 90.0) >= -UPHILL_SLACK for p in dpts), "and no point of it sits below the outfall"


def test_every_trunk_end_is_left_where_its_water_goes() -> None:
    """W15: a main canal's tail running on past the field into bare ground is walked back to where it reaches the crop;
    a head doing the same is walked back to where it meets another channel; a trunk with no anchored point at all is
    dropped; the sluice (the head race's first point) and the collector's outfall are the source's and the sink's."""
    env = [(100.0, 100.0), (300.0, 100.0), (300.0, 300.0), (100.0, 300.0)]
    channels = [
        {"pts": [(50.0, 50.0), (150.0, 150.0)], "role": "main"},  # the head race, from the sluice outside the fan
        {"pts": [(150.0, 150.0), (250.0, 150.0), (400.0, 150.0)], "role": "main"},  # its tail runs 100 px past the fan
        {"pts": [(120.0, 290.0), (500.0, 290.0)], "role": "drain"},  # the outfall is the sink's
        {"pts": [(600.0, 600.0), (700.0, 600.0)], "role": "main"},  # water from nowhere to nowhere
        {"pts": [(700.0, 200.0), (250.0, 200.0)], "role": "main"},  # a head in bare ground, a tail in the crop
        {"pts": [(0.5, 400.0), (0.5, 450.0)], "role": "main"},  # off the frame at both ends
        {"pts": [(900.0, 900.0), (950.0, 900.0)], "role": "branch"},  # not a trunk
        {"pts": [(120.0, 120.0)], "role": "main"},  # no course
    ]
    anchor_trunk_ends(channels, env, 1000.0, 1000.0)
    assert len(channels) == 7, "the trunk from nowhere to nowhere is dropped"
    assert channels[0]["pts"][0] == (50.0, 50.0), "the sluice is left to the source"
    assert abs(channels[1]["pts"][-1][0] - 302.0) < 1e-9, "the tail stops where it reaches the crop"
    assert channels[2]["pts"][-1] == (500.0, 290.0), "the outfall is left to the sink"
    assert abs(channels[3]["pts"][0][0] - 302.0) < 1e-9, "a head walked back the same way, to the crop"
    others = [c["pts"] for c in channels]
    for k, c in enumerate(channels[:5]):  # the trunks; the branch and the pointless record are not judged
        for at in (c["pts"][-1],) if k == 0 else (c["pts"][0],) if c["role"] == "drain" else (c["pts"][0], c["pts"][-1]):
            assert end_anchored(at, [env], [o for j, o in enumerate(others) if j != k], 1000.0, 1000.0), (k, at)


def test_the_floor_stops_where_the_command_area_does() -> None:
    """W31, by construction (`_comb_floor_and_winding`): an envelope whose outer thread runs 40 px down the fall past the
    flat-extended collector line is pulled back onto it, so the floor overhangs the collector by no more than half a px
    (`banks.floor_overhang`, the finished-map test's own predicate)."""
    from l7r.diagram.waterfields.banks import floor_overhang
    from l7r.diagram.waterfields.comb import _comb_floor_and_winding

    dpts = [(100.0, 300.0), (400.0, 300.0)]
    threads = [SimpleNamespace(pts=[(100.0, 0.0), (60.0, 340.0)]), SimpleNamespace(pts=[(400.0, 0.0), (400.0, 300.0)])]
    raw = [(100.0, 0.0), (400.0, 0.0), (400.0, 0.0), (400.0, 300.0), (400.0, 300.0), (100.0, 300.0), (60.0, 340.0), (100.0, 0.0)]
    assert max(floor_overhang(raw, dpts, 90.0)) > 30.0, "the fixture's floor hangs past the collector"
    env = _comb_floor_and_winding([], threads, [(100.0, 0.0), (400.0, 0.0)], dpts, _Frame(90.0))  # type: ignore[arg-type]
    assert max(floor_overhang(env, dpts, 90.0)) <= 0.5


def test_a_fan_envelope_folded_by_the_floor_trim_still_has_its_ground() -> None:
    """Feature 287, the cohort seed 27 crash: the floor trim clamped an unclipped outer thread onto the collector line and
    left a fold of six points 1-3 px apart, which `dedup_ring` cannot merge. That ring crosses itself and `buffer(0)` of
    it is EMPTY, so the carve's acreage estimate and the seam pass were handed a field with no ground (NaN bounds). The
    envelope is now made a simple polygon where it is built (`ring_rules.simple_outline`), keeping the fan's ground; a
    ring already simple is returned as it stands. The fixture is the seed's own ring, at full precision - rounded to 0.1
    px it no longer collapses, which is why it is recorded rather than constructed."""
    import json
    import os

    from shapely.geometry import Polygon

    from l7r.diagram.waterfields.ring_rules import simple_outline

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "fixtures", "folded_envelope_seed27.json"), encoding="utf-8") as fh:
        folded = [tuple(p) for p in json.load(fh)["envelope"]]
    assert Polygon(folded).buffer(0).is_empty, "the fixture is the ring that emptied the field"
    fixed = simple_outline(folded)
    assert Polygon(fixed).is_valid and abs(Polygon(fixed).area - Polygon(folded).area) < 1.0
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert simple_outline(square) == square, "a simple ring is left alone"
    assert simple_outline([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (0.5, 0.5)]) == [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (0.5, 0.5)], "no ground to keep"
    bowtie = simple_outline([(0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0)])
    assert Polygon(bowtie).is_valid and Polygon(bowtie).area == 25.0, "a bow-tie keeps its larger lobe"


def test_a_sub_stride_canal_piece_is_dropped_and_the_canal_stays_joined() -> None:
    """water W56's other half: a canal cut leaves a remainder near a piece's own end. A remainder the canal runs on through
    hands its start to the next piece, so the canal still leaves the fork; one at the canal's far end is dropped."""
    from l7r.diagram.waterfields.trunks import STUB_MIN_RUN, drop_stub_pieces

    head = {"pts": [(0.0, 0.0), (3.0, 0.0)], "w": 6.0, "role": "main"}
    body = {"pts": [(3.0, 0.0), (200.0, 0.0)], "w": 5.0, "role": "main"}
    tail = {"pts": [(200.0, 0.0), (203.0, 0.0)], "w": 2.0, "role": "main"}
    lone = {"pts": [(500.0, 0.0), (504.0, 0.0)], "w": 2.0, "role": "main"}
    kept = drop_stub_pieces([head, body, tail, lone])
    assert kept == [body] and body["pts"][0] == (0.0, 0.0), "the head's start is handed on; the far-end remainder goes"
    assert all(sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(p["pts"], p["pts"][1:], strict=False)) >= STUB_MIN_RUN for p in kept)
    speck = {"pts": [(0.0, 0.0), (0.3, 0.0)], "w": 6.0, "role": "main"}
    nxt = {"pts": [(0.3, 0.0), (90.0, 0.0)], "w": 5.0, "role": "main"}
    assert drop_stub_pieces([speck, nxt]) == [nxt] and nxt["pts"][0] == (0.3, 0.0), "a speck at the successor's own start moves nothing"

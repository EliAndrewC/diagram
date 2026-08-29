"""Feature 139 T52 (GM 2026-08-28): the polder's ring canal CLOSES - every toe collector ends ON the trunk it meets."""

from __future__ import annotations

import math

from l7r.diagram.waterfields import build_polder
from l7r.diagram.waterfields.polder import _onto_poly


def _d(pt: tuple[float, float], poly: list[tuple[float, float]]) -> float:
    q = _onto_poly(pt, poly)
    return math.hypot(q[0] - pt[0], q[1] - pt[1])


def test_onto_poly_is_the_nearest_point_of_the_polyline() -> None:
    poly = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
    assert _onto_poly((50.0, 7.0), poly) == (50.0, 0.0)
    assert _onto_poly((130.0, 50.0), poly) == (100.0, 50.0)
    assert _onto_poly((-10.0, -10.0), poly) == (0.0, 0.0)  # clamped to the first vertex


def test_both_toe_collectors_end_on_the_feeder_and_the_drain() -> None:
    """The corner rounding sweeps each trunk's corner inside the lattice node the toes were laid to, so a
    toe's end stood 9 ft off the feeder's swept bend (the gap the GM pointed at, top-left of the ring).
    Each toe END now snaps onto the NEARER trunk - the east toe runs feeder -> drain, the west toe is the
    block's fourth side and runs drain -> feeder, so 'start onto the feeder' would throw it across the block."""
    for seed, wander in ((3, 0.0), (7, 0.3), (11, 0.15)):
        net = build_polder(2400, 2400, (300.0, 300.0), seed=seed, edge_wander=wander)
        trunks = {c["seg"]: c["pts"] for c in net["channels"] if c.get("seg") in ("feeder", "drain")}
        assert set(trunks) == {"feeder", "drain"}
        toes = [c for c in net["channels"] if c.get("seg") in ("e_toe", "w_toe")]
        assert len(toes) == 2
        for toe in toes:
            for end in (toe["pts"][0], toe["pts"][-1]):
                assert min(_d(end, trunks["feeder"]), _d(end, trunks["drain"])) < 0.6, (seed, toe["seg"], end)
            assert math.dist(toe["pts"][0], toe["pts"][-1]) > 500, "a toe still spans the block - it was not thrown across it"


# ---- feature 139 T55: a parcel stops at the ditch that bounds it ---------------------------------
def _parcel(x0: float, y0: float, x1: float, y1: float, n: int = 6) -> dict[str, object]:
    ring = (
        [(x0 + (x1 - x0) * i / n, y0) for i in range(n)]
        + [(x1, y0 + (y1 - y0) * i / n) for i in range(n)]
        + [(x1 - (x1 - x0) * i / n, y1) for i in range(n)]
        + [(x0, y1 - (y1 - y0) * i / n) for i in range(n)]
    )
    return {"poly": ring, "fill": "#000", "low": False}


def _inside(pts: list[tuple[float, float]], poly: list[tuple[float, float]]) -> int:
    hits = 0
    for q in pts:
        c = False
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            if (y1 > q[1]) != (y2 > q[1]) and q[0] < x1 + (q[1] - y1) * (x2 - x1) / (y2 - y1):
                c = not c
        hits += c
    return hits


def test_a_channel_running_through_a_parcel_is_cut_out_of_it() -> None:
    """GM 2026-08-29: "one of the vegetable grounds overlaps with the irrigated channels which run
    between the vegetable grounds and the ponds". The channels are laid on the ideal lattice line and
    the parcels wander off it, so a parcel can end up on the wrong side of its own ditch - and when
    that parcel is the block's leftover ground, its crop rows are drawn under the water."""
    from l7r.diagram.waterfields.polder import _plots_clear_of_channels

    plots = [_parcel(100.0, 100.0, 400.0, 700.0)]
    run = [(140.0, 60.0), (137.0, 380.0), (143.0, 740.0)]  # a lateral 40 ft inside the parcel's west edge, bending
    _plots_clear_of_channels(plots, [{"pts": run, "w": 4.0, "w_tail": 3.0}])
    ring = [(float(x), float(y)) for x, y in plots[0]["poly"]]  # type: ignore[union-attr]
    dense = [(a[0] + (b[0] - a[0]) * k / 20, a[1] + (b[1] - a[1]) * k / 20) for a, b in zip(run, run[1:], strict=False) for k in range(21)]
    assert _inside(dense, ring) == 0, "the ditch still runs through the parcel"
    assert min(q[0] for q in ring) >= 140.0, "the strip beyond the ditch was not cut away"
    assert max(q[0] for q in ring) > 390.0 and max(q[1] for q in ring) > 690.0, "the rest of the holding was cut away with it"


def test_a_parcel_clear_of_every_channel_keeps_its_own_outline() -> None:
    """The pass is a no-op where there is no water: a parcel nowhere near a channel comes back point for
    point, so the archetype's hand-piled wander survives (`polder_parcels_are_organic` reads it)."""
    from l7r.diagram.waterfields.polder import _plots_clear_of_channels

    plots = [_parcel(100.0, 100.0, 400.0, 700.0)]
    before = list(plots[0]["poly"])  # type: ignore[arg-type]
    _plots_clear_of_channels(plots, [{"pts": [(900.0, 60.0), (900.0, 740.0)], "w": 4.0, "w_tail": 3.0}])
    assert plots[0]["poly"] == before


def test_the_parcel_pass_stands_aside_where_there_is_nothing_to_do() -> None:
    """The guards, each reached: no channels at all, a channel with one point, a degenerate parcel, a
    boundary sample sitting exactly ON a centerline, and a parcel small enough that the band swallows
    it (there is no outline left to keep, so the parcel is left as it was rather than emptied)."""
    from l7r.diagram.waterfields.polder import _plots_clear_of_channels

    p = _parcel(100.0, 100.0, 400.0, 700.0)
    before = list(p["poly"])  # type: ignore[arg-type]
    _plots_clear_of_channels([p], [])  # no channels
    _plots_clear_of_channels([p], [{"pts": [(1.0, 1.0)], "w": 4.0}])  # a channel of one point
    assert p["poly"] == before

    thin = {"poly": [(10.0, 10.0), (20.0, 10.0)], "fill": "#000", "low": False}  # not a ring
    _plots_clear_of_channels([thin], [{"pts": [(0.0, 0.0), (100.0, 0.0)], "w": 4.0}])
    assert thin["poly"] == [(10.0, 10.0), (20.0, 10.0)]

    on_line = _parcel(100.0, 100.0, 400.0, 700.0)
    _plots_clear_of_channels([on_line], [{"pts": [(100.0, 60.0), (100.0, 740.0)], "w": 4.0}])  # dead along the parcel's own west edge
    assert min(q[0] for q in on_line["poly"]) >= 100.0  # type: ignore[union-attr]

    tiny = _parcel(200.0, 200.0, 203.0, 203.0)
    small_before = list(tiny["poly"])  # type: ignore[arg-type]
    _plots_clear_of_channels([tiny], [{"pts": [(201.5, 100.0), (201.5, 300.0)], "w": 40.0}])  # the band covers it whole
    assert tiny["poly"] == small_before


def test_clean_polder_parcels_cleans_a_block_and_re_measures_it() -> None:
    """`fit_polder` bisects with up to 45 candidate blocks and draws one, so the parcel/channel cleanup
    is skipped during the search (`clean_parcels=False`) and run once on the winner - which is what this
    entry point is for. It re-measures the acreage, because the cut is real ground."""
    from l7r.diagram.waterfields import clean_polder_parcels

    net = {
        "plots": [_parcel(100.0, 100.0, 400.0, 700.0)],
        "channels": [{"pts": [(140.0, 60.0), (143.0, 740.0)], "w": 4.0, "w_tail": 3.0}],
        "acres": 99.0,
    }
    out = clean_polder_parcels(net)
    assert out is net
    assert min(q[0] for q in net["plots"][0]["poly"]) >= 140.0  # type: ignore[index, union-attr]
    assert 0.0 < float(net["acres"]) < 99.0  # type: ignore[arg-type]

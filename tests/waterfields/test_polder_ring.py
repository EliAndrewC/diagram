"""Feature 150 T52 (GM 2026-08-28): the polder's ring canal CLOSES - every toe collector ends ON the trunk it meets."""

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


# ---- feature 150 T55: a parcel stops at the ditch that bounds it ---------------------------------
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


# ---- feature 287: the polder's placer guarantees (water W19, W44, W45) ----------------------------


def test_a_toe_runs_on_along_the_trunk_and_ends_on_its_centerline() -> None:
    """W45: past its junction a toe's end runs on 3 ft ALONG the trunk, never along its own heading - at a corner the two
    part, and the Kuwabata toes ended 2.5 ft off the drain's centerline. `along_trunk` and `end_on_centerline` are the
    placer's walk and the rule; the corner case is a trunk starting where the toe ends, the toe arriving square to it."""
    from l7r.diagram.waterfields.polder import along_trunk, end_on_centerline

    drain = [(100.0, 500.0), (400.0, 500.0), (700.0, 510.0)]
    toe_end, toe_prev = (100.0, 500.0), (100.0, 200.0)  # the toe comes down the west side and meets the drain's start
    heading = (toe_end[0] - toe_prev[0], toe_end[1] - toe_prev[1])
    off = (toe_end[0] + heading[0] / 300.0 * 3.0, toe_end[1] + heading[1] / 300.0 * 3.0)  # the old run-on: 3 ft down, off the drain
    assert not end_on_centerline(off, drain)
    on = along_trunk(drain, toe_end, heading, 3.0)
    assert end_on_centerline(on, drain) and on == (103.0, 500.0)
    assert along_trunk(drain, (400.0, 500.0), (-1.0, 0.0), 3.0) == (397.0, 500.0), "the run follows the heading's sense along the trunk"
    assert along_trunk(drain, (700.0, 510.0), (1.0, 0.0), 30.0) == (700.0, 510.0), "and stops at the trunk's end"
    for seed, wander in ((3, 0.0), (7, 0.3), (11, 0.15)):
        net = build_polder(2400, 2400, (300.0, 300.0), seed=seed, edge_wander=wander)
        trunks = [c["pts"] for c in net["channels"] if c.get("seg") in ("feeder", "drain")]
        for toe in (c for c in net["channels"] if c.get("seg") in ("e_toe", "w_toe")):
            for end in (toe["pts"][0], toe["pts"][-1]):
                assert any(end_on_centerline(end, t) for t in trunks), (seed, toe["seg"], end)


def test_every_lateral_lands_on_a_trunk_at_both_ends() -> None:
    """W44: every lateral of the ring and the lattice - the toes included, which carry the lateral role - lands within the
    gate's 13 ft of the feeder or the drain at both ends, on a small lattice and a wandered one."""
    for seed, wander, mosaic in ((5, 0.0, 0.0), (9, 0.4, 0.5)):
        net = build_polder(1600, 1600, (200.0, 200.0), seed=seed, rows=6, cols=4, edge_wander=wander, mosaic=mosaic)
        trunks = [c["pts"] for c in net["channels"] if c.get("role") in ("main", "drain")]
        laterals = [c for c in net["channels"] if c.get("role") == "lateral"]
        assert len(laterals) >= 5, "the lattice laid its laterals"
        for lat in laterals:
            for end in (lat["pts"][0], lat["pts"][-1]):
                assert min(_d(end, t) for t in trunks) <= 13.0, (seed, lat.get("seg"), end)


def test_no_polder_parcel_tapers_to_a_point() -> None:
    """W19: the apex pass re-hems a parcel whose CONVEX corner is a needle without that corner, drops one whose needle is a
    reflex notch (filling it would reach back over what it was cut round), and leaves a basin alone; every polder built
    keeps no needle."""
    from l7r.diagram.waterfields.polder import unpoint_parcels
    from l7r.diagram.waterfields.ring_rules import needle

    sliver = {"poly": [(0.0, 0.0), (100.0, 0.0), (100.0, 60.0), (40.0, 60.0), (300.0, 20.0)]}  # a 10-degree spike east
    notch = {"poly": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (52.0, 100.0), (50.0, 5.0), (48.0, 100.0), (0.0, 100.0)]}
    basin = {"poly": [(0.0, 0.0), (100.0, 0.0), (100.0, 60.0), (0.0, 60.0)]}
    assert needle(sliver["poly"]) and needle(notch["poly"]) and not needle(basin["poly"])
    plots = [sliver, notch, basin]
    unpoint_parcels(plots)
    assert plots == [sliver, basin], "the notched parcel is left as bank ground"
    assert not needle(sliver["poly"]) and len(sliver["poly"]) < 5
    assert basin["poly"] == [(0.0, 0.0), (100.0, 0.0), (100.0, 60.0), (0.0, 60.0)], "a basin is untouched"
    for seed, wander, mosaic in ((3, 0.5, 0.0), (8, 0.3, 0.6), (21, 0.4, 0.3)):
        net = build_polder(2400, 2400, (300.0, 300.0), seed=seed, edge_wander=wander, mosaic=mosaic)
        assert net["plots"] and not [p for p in net["plots"] if needle(p["poly"])], seed


def test_a_parcel_blunt_unrounded_but_a_needle_as_recorded_is_re_hemmed() -> None:
    """The violating case of the polder needle's record (feature 287 wave 5): a corner at 15.0 degrees unrounded that the
    record's 0.1 px rounding (`fields/comb.py`'s `plot_rings`) takes to a needle. The pass judges the ring as recorded, so
    the ring it leaves - rounded as the map records it - is no needle."""
    import math

    from l7r.diagram.waterfields.polder import unpoint_parcels
    from l7r.diagram.waterfields.ring_rules import needle

    a = math.radians(15.0)
    ring = [(0.0, 0.0), (200.0, 0.0), (200.0, 50.0), (100.0, 60.0), (12.0 * math.cos(a), 12.0 * math.sin(a))]
    assert not needle(ring) and needle([(round(x, 1), round(y, 1)) for x, y in ring]), "the case: blunt raw, a needle as recorded"
    plots = [{"poly": ring}]
    unpoint_parcels(plots)
    assert all(not needle([(round(x, 1), round(y, 1)) for x, y in p["poly"]]) for p in plots)
    assert plots and len(plots[0]["poly"]) == 4, "re-hemmed without the apex, not dropped"


def test_a_polder_channels_bank_is_its_own_in_feet() -> None:
    """Feature 328 wave 73 (0022, 0055): the bank a parcel keeps from a polder channel is the channel's own - a supply canal's
    5 ft beside the feeder, a delivery ditch's 1.5 ft bund beside a toe, half a bund beside the drain, and beside an interior
    lateral its 8 ft corridor less the ditch, split per side - in feet at the map's scale."""
    from l7r.diagram.waterfields.polder import channel_berm

    assert channel_berm({"seg": "feeder", "w": 4.5}, 1.0) == 5.0 and channel_berm({"seg": "feeder", "w": 4.5}, 2.0) == 2.5
    assert channel_berm({"seg": "e_toe", "w": 2.5}, 1.0) == 1.5 and channel_berm({"seg": "drain", "w": 5.5}, 1.0) == 0.75
    assert channel_berm({"seg": "lateral", "w": 2.5, "w_tail": 1.5}, 1.0) == 2.75
    assert channel_berm({"seg": "lateral", "w": 9.0}, 1.0) == 0.0, "a ditch wider than its corridor keeps no extra bank"


def test_arc_fraction_reads_where_a_point_lies_along_a_run() -> None:
    from l7r.diagram.waterfields.polder import arc_fraction

    run = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
    assert arc_fraction(run, (50.0, 5.0)) == 0.25 and arc_fraction(run, (100.0, 100.0)) == 1.0 and arc_fraction(run, (0.0, 0.0)) == 0.0


def test_the_band_narrows_with_the_ditch() -> None:
    """Feature 328 wave 73 (0055: half the ditch's drawn width at that point): a parcel beside a tapering ditch's narrow end is
    kept back by the narrow end's half-width, not the wide end's."""
    from l7r.diagram.waterfields.polder import _plots_clear_of_channels

    plot = {"poly": [(0.0, 0.0), (40.0, 0.0), (40.0, 100.0), (0.0, 100.0)]}
    ditch = {"pts": [(43.0, float(y)) for y in range(1000, -1, -20)], "w": 20.0, "w_tail": 2.0, "seg": "e_toe"}  # wide far off, 2 ft beside the plot
    _plots_clear_of_channels([plot], [ditch])
    # beside the plot the ditch is 2 to ~3 ft wide: its band (half of that plus the toe's 1.5 ft bund) reaches x ~40.0-40.5,
    # where the far end's 20 ft would have cut the parcel back to x 31.5
    assert max(x for x, _y in plot["poly"]) >= 39.0, plot["poly"]


def test_a_laterals_band_is_its_corridor_all_along() -> None:
    """Feature 328 wave 73 (0022: a ditch corridor of about 8 ft): beside an interior lateral the bank is the corridor less the
    ditch WHERE IT IS, so the band reaches 4 ft each side of the centerline at the head and the tail alike."""
    from l7r.diagram.waterfields.polder import channel_berm

    lat = {"seg": "lateral", "w": 2.5, "w_tail": 1.5}
    assert 2.5 / 2 + channel_berm(lat, 1.0, 2.5) == 4.0 and 1.5 / 2 + channel_berm(lat, 1.0, 1.5) == 4.0

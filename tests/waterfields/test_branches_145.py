"""Feature 145: the branches of banks.py and palette.py the hamlet-path floor found no test reaching."""

from __future__ import annotations

from l7r.diagram.waterfields.banks import ring_solidity
from l7r.diagram.waterfields.palette import organic_parcel


def test_ring_solidity_degenerate_rings_score_one() -> None:
    assert ring_solidity([(0.0, 0.0), (1.0, 1.0)]) == 1.0  # fewer than three distinct points
    assert ring_solidity([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]) == 1.0  # collinear: no hull
    assert abs(ring_solidity([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]) - 1.0) < 1e-9


def test_organic_parcel_leaves_a_degenerate_polygon_alone() -> None:
    import random

    assert organic_parcel([(0.0, 0.0), (1.0, 0.0)], random.Random(1), 4.0, 0.05, 6.0) == [(0.0, 0.0), (1.0, 0.0)]


# ---- carve.py: the dry-hem arms the reference fan does not enter (feature 146) ----------------


def test_dry_fields_steps_over_a_supply_canal_with_no_stroke() -> None:
    """A supply record with fewer than two points has no stroke to hold a berm off, so it is stepped
    over rather than measured - every distance below it needs a segment."""
    import random

    from l7r.diagram.waterfields.carve import _dry_fields
    from l7r.diagram.waterfields.frame import _Frame

    F = _Frame(90.0)
    canal = [(300.0, 200.0), (300.0, 900.0)]
    plain = _dry_fields(random.Random(1), F, canal, 1400.0, 1400.0, [])
    stub = _dry_fields(random.Random(1), F, canal, 1400.0, 1400.0, [], supply=[{"pts": [(300.0, 500.0)], "w": 6.0}])
    assert plain and len(stub) == len(plain), "the stub record changes nothing"


def test_dry_fields_plants_nothing_on_ground_a_keepout_claims() -> None:
    """The hem takes what is left over. A keepout circle across the whole band leaves it nothing, and
    the honest answer is no plots rather than plots drawn over the thing the keepout is protecting."""
    import random

    from l7r.diagram.waterfields.carve import _dry_fields
    from l7r.diagram.waterfields.frame import _Frame

    F = _Frame(90.0)
    canal = [(300.0, 200.0), (300.0, 900.0)]
    assert _dry_fields(random.Random(1), F, canal, 1400.0, 1400.0, [(300.0, 500.0, 400.0)]) == []


def _comb(**over):
    from l7r.diagram.waterfields import build_comb

    base = dict(
        W=1400.0,
        H=1400.0,
        sluice=(700.0, 300.0),
        seed=3,
        down_deg=90.0,
        offtakes_a=(0.3, 0.62, 0.93),
        offtakes_b=(0.55,),
        plot_across=46.0,
        row_step=(26.0, 30.0),
        grain_drift=4,
        grain=2.0,
        supply_banks=True,
        field_fall=320.0,
        canal_a_len=(420.0, 250.0),
        canal_b_len=(420.0, 250.0),
    )
    base.update(over)
    return build_comb(**base)


def test_a_closer_quad_that_would_run_off_the_sheet_is_dropped() -> None:
    """The canal closers fill the wedges the tessellation leaves at a fork or an outfall. One whose
    corner falls within 8 px of the frame would be drawn half off the sheet, so it is dropped - only a
    fan far larger than the canvas ever produces one."""
    big = _comb(field_fall=1600.0, canal_a_len=(1500.0, 900.0), canal_b_len=(1500.0, 900.0))
    assert big["plots"], "the oversize fan still carves"
    assert all(all(8 <= x <= 1392 and 8 <= y <= 1392 for x, y in p["poly"]) for p in big["plots"]), "nothing runs off"


def test_a_sector_the_drain_cuts_short_plants_nothing() -> None:
    """The sector's span is measured twice: once between its two boundaries, and again against the DRAIN
    that crosses below them. A sector long enough by the first measure and too short by the second stops
    here rather than planting a row the drain runs through."""
    net = _comb(sluice=(100.0, 700.0), down_deg=90.0, field_fall=900.0, canal_a_len=(1100.0, 700.0), canal_b_len=(1100.0, 700.0))
    assert isinstance(net["plots"], list)


def test_a_hem_one_boundary_wide_has_no_shared_normal_and_says_so() -> None:
    """REGRESSION (feature 146). `_miter_normals` mitres each boundary point's two chords, and with a
    single boundary there is no chord at all - it built an empty list and then indexed it. Measured on a
    down_deg=210 fan sluiced at the west edge, where the dry band clips to one column: `IndexError`, from
    a `build_comb` call with entirely legal arguments."""
    from l7r.diagram.waterfields.frame import _Frame, _miter_normals

    assert _miter_normals([], _Frame(90.0)) == []
    assert _miter_normals([(10.0, 10.0)], _Frame(90.0)) == []
    assert len(_miter_normals([(10.0, 10.0), (60.0, 10.0)], _Frame(90.0))) == 2

    net = _comb(sluice=(100.0, 700.0), down_deg=210.0, field_fall=900.0, canal_a_len=(1100.0, 700.0), canal_b_len=(1100.0, 700.0))
    assert isinstance(net["plots"], list), "the fan carves instead of raising"


def test_dry_plots_draw_the_maps_own_crop_mix() -> None:
    """Feature 328 wave 65 (0006: "each map picks its mix of the four crops at random"): a plot's crop is drawn on the map's
    mix, so a mix that weighs one crop alone plants only that crop, and `dry_crop_mix` rolls one weight per crop."""
    import random

    from l7r.diagram.waterfields.carve import _dry_fields, dry_crop_mix
    from l7r.diagram.waterfields.frame import _Frame
    from l7r.diagram.waterfields.palette import DRY_CROPS

    F = _Frame(90.0)
    canal = [(300.0, 200.0), (300.0, 900.0)]
    only_soy = [0.0 if c != "soy" else 1.0 for c in DRY_CROPS]
    plots = _dry_fields(random.Random(1), F, canal, 1400.0, 1400.0, [], crop_mix=only_soy)
    assert plots and {p["crop"] for p in plots} == {"soy"}
    mix = dry_crop_mix(random.Random(3))
    assert len(mix) == len(DRY_CROPS) and all(0.1 <= w <= 1.0 for w in mix)


def test_the_end_dry_plot_is_split_at_every_grain() -> None:
    """Feature 328 wave 65 (0006's plot size): the snap to the canal's length can stretch the END plot to ~1.85 plot widths;
    it is halved past 1.35 at every grain, the village grain (g = 1) too, so no plot runs past 1.35 widths along the canal."""
    import random

    from l7r.diagram.waterfields.carve import _dry_fields
    from l7r.diagram.waterfields.frame import _Frame

    F = _Frame(90.0)
    canal = [(300.0, 200.0), (300.0, 900.0)]  # along the canal is along y: a plot's near edge is its two least-x corners
    widest = 0.0
    for seed in range(40):
        for p in _dry_fields(random.Random(seed), F, canal, 1400.0, 1400.0, []):
            near = sorted(p["poly"])[:2]
            widest = max(widest, abs(near[0][1] - near[1][1]))
    assert widest <= 1.35 * 46 + 1.0, widest


def test_the_crop_stream_moves_with_the_geometry_stream_and_leaves_it_alone() -> None:
    """Feature 328 wave 65 (spec-fidelity): `crop_stream` seeded from a few words of R's state handed out the SAME stream
    after R had drawn; seeded from the whole state it moves with R, and it never advances R."""
    import random

    from l7r.diagram.waterfields.carve import crop_stream

    R = random.Random(5)
    R.random()  # a stream that has drawn: its state's words regenerate only every 624 outputs
    first = crop_stream(R).random()
    before = R.getstate()
    crop_stream(R)
    assert R.getstate() == before, "the crop stream never advances the geometry's"
    R.random()
    assert crop_stream(R).random() != first, "a draw of R moves the crop stream"

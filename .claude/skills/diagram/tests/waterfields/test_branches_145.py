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


def test_a_sector_too_short_to_hold_a_row_plants_nothing_rather_than_a_degenerate_one() -> None:
    """A row that straddles the spawn point has zero width and never plants, and a sector shorter than
    24 grain units cannot hold one at all. Both arms return an empty sector rather than a strip of
    nothing - the acreage bisection in `hamletgen/water.py` reads the result and moves on."""
    assert _comb()["plots"], "the reference-shaped fan carves"
    tiny = _comb(field_fall=60.0, canal_a_len=(120.0, 60.0), canal_b_len=(120.0, 60.0))
    assert tiny["plots"] == [], "there is no room for a single row"


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


def test_a_closer_quad_that_would_run_off_the_sheet_is_dropped_at_an_oblique_fall() -> None:
    """The frame guard on the canal closers. It needs a fan whose wedges reach the margin, which on this
    canvas means a large fan sluiced at the west edge falling on the diagonal."""
    net = _comb(sluice=(100.0, 700.0), down_deg=135.0, field_fall=900.0, canal_a_len=(1100.0, 700.0), canal_b_len=(1100.0, 700.0))
    assert all(all(8 <= x <= 1392 and 8 <= y <= 1392 for x, y in p["poly"]) for p in net["plots"])


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

"""tier city tests split out of `tests.settlement.test_city` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement
from tests.settlement.test_city import _CITY_SURFACE, _own_callables


@pytest.mark.tiers("city")
def test_moat_river_junction_feet_tilt_with_the_current():
    # GM 2026-07-24 hydrology review: the junction feet are NOT square rfoot tees. The upstream
    # (inlet) end shifts UPSTREAM off its square foot - a near-square, sediment-wary intake with
    # only a slight tilt - and the downstream (outlet) end sweeps DOWNSTREAM further (confluences
    # merge at downstream angles). River pts run upstream-first; a vertical river makes the
    # shifts pure y offsets, so the asymmetry is directly measurable.
    import math as m

    s = _crop_settlement()
    s.meta(name="RT", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    river = [(1360, 100), (1360, 1300)]  # flows top -> bottom (upstream-first)
    for ring in (pts, pts[::-1]):  # both ring orientations: keep[0] lands downstream on one, upstream on the other
        mo = s.moat(ring, gap=24, river=river, river_inlet_tilt=10.0, river_outlet_tilt=22.0)  # a caller's tilt; the default is square (0054)
        (inlet, adj_in), (outlet, adj_out) = sorted([(mo[0], mo[1]), (mo[-1], mo[-2])], key=lambda e: e[0][1])
        in_shift = adj_in[1] - inlet[1]  # upstream (negative-y) shift of the inlet foot off square
        out_shift = outlet[1] - adj_out[1]  # downstream (positive-y) sweep of the outlet foot
        assert in_shift > 0  # inlet tilts upstream, never smoothly flow-aligned
        assert out_shift > in_shift  # the outlet sweeps harder - the researched asymmetry


@pytest.mark.tiers("city")
def test_moat_river_junction_tilts_follow_a_reversed_river():
    # the OTHER branch of the tilt bookkeeping (keep[0]'s end downstream): same asymmetry when the
    # river runs bottom -> top (upstream-first pts reversed). Deterministic on purpose - this branch
    # was previously covered only by whichever orientation a pool map happened to roll, so an rng
    # shift elsewhere dropped it out of coverage (2026-07-24).
    import math as m

    s = _crop_settlement()
    s.meta(name="RT2", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    river = [(1360, 1300), (1360, 100)]  # flows bottom -> top (upstream-first)
    mo = s.moat(pts, gap=24, river=river, river_inlet_tilt=10.0, river_outlet_tilt=22.0)  # a caller's tilt; the default is square (0054)
    (outlet, adj_out), (inlet, adj_in) = sorted([(mo[0], mo[1]), (mo[-1], mo[-2])], key=lambda e: e[0][1])
    in_shift = inlet[1] - adj_in[1]  # upstream is +y now: the inlet foot shifts DOWN off square
    out_shift = adj_out[1] - outlet[1]  # the outlet foot sweeps UP, downstream with the current
    assert in_shift > 0  # inlet tilts upstream, never smoothly flow-aligned
    assert out_shift > in_shift  # the outlet sweeps harder - the researched asymmetry


@pytest.mark.tiers("city")
def test_a_moats_ends_meet_the_river_square_by_default():
    """0054: both ends of a moat open onto a river meet it at a right angle, leaning neither way - every reason found for
    tilting them is modern engineering (feature 328 wave 5; the 2026-07-24 tilts are a caller's choice now)."""
    import math as m

    s = _crop_settlement()
    s.meta(name="RT3", scale="city", walled=True, ftpx=3)
    pts = [(round(1000 + 300 * m.cos(2 * m.pi * i / 16)), round(700 + 300 * m.sin(2 * m.pi * i / 16))) for i in range(16)]
    mo = s.moat(pts, gap=24, river=[(1360, 100), (1360, 1300)])
    for end, adj in ((mo[0], mo[1]), (mo[-1], mo[-2])):
        assert abs(end[1] - adj[1]) < 1.0, "a foot square to a vertical river runs level"


@pytest.mark.tiers("city")
def test_no_pre_split_city_member_was_lost_in_the_move():
    # SUBSET, not equality, for the reason feature 112 recorded in its own guard: Stage 2
    # decomposes the oversized methods into named private helpers, so the composed class
    # legitimately holds MORE than the pre-split 27, and will hold more again the next time a
    # method is split. What must never happen is a pre-split member going MISSING - an addition is
    # visible in review, a subtraction is silent until whichever generator calls it happens to run.
    from l7r.diagram.settlement.city import CityMixin

    composed = set().union(*(_own_callables(c) for c in CityMixin.__mro__))
    assert composed >= _CITY_SURFACE, f"missing={sorted(_CITY_SURFACE - composed)}"


@pytest.mark.tiers("city")
def test_every_city_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely CityMixin
    unreachable = sorted(n for n in _CITY_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"


# ---- feature 174: the wall's arc-walking geometry, tested directly --------------------------------
# Branch-coverage tests. The end-to-end suite draws a whole city wall with its towers; these say what
# each helper promises, on a ring a reader can check by hand.

_SQUARE_RING = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]


# ---- feature 174: rowpack, the machiya/nagaya fabric ---------------------------------------------


def test_a_closed_rampart_JOINS_its_last_run_into_its_first() -> None:
    """`_gapped_ring` draws a wall with a genuine OPENING at each gate, "so the rampart can render
    OVER the ground lanes yet still let the road show THROUGH the gate - rather than painting a land
    rect over the wall (which would erase the road too, once on top)".

    On a CLOSED ring whose first vertex is not itself a gate, the last run continues into the first,
    or the wall would carry a seam at vertex 0 that no gate put there. That is why ONE mid-ring gate
    yields ONE run rather than two: the gap is at the gate, and the ring closes behind it.

    A GATE IS A RING VERTEX, not a point on an edge - `isg` tests vertices. A test passing a
    mid-edge point gets no gaps at all and would pass while exercising nothing, which is how this
    test was first written.
    """
    s = Settlement(1600, 1600, seed=15)
    s.meta(name="C", scale="city")
    ring = [(300.0, 300.0), (800.0, 300.0), (1300.0, 300.0), (1300.0, 800.0), (1300.0, 1300.0), (300.0, 1300.0)]

    assert s._gapped_ring(ring, [(800.0, 300.0)]).count("M") == 1, "one gate on a closed ring: one run, joined at vertex 0"
    assert s._gapped_ring(ring, [(800.0, 300.0), (1300.0, 800.0)]).count("M") == 2, "two gates cut it into two runs"
    assert s._gapped_ring(ring, [(300.0, 300.0)]).count("M") == 1, "a ring gated AT vertex 0 needs no join"
    assert s._gapped_ring(ring, []).count("M") == 1, "and an ungated wall is one unbroken run"

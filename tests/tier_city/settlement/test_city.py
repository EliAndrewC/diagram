"""tier city tests split out of `tests.settlement.test_city` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement.test_city import _CITY_SURFACE, _own_callables


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

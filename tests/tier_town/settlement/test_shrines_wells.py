"""tier town tests split out of `tests.settlement.test_shrines_wells` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _town


@pytest.mark.tiers("town")
def test_open_seat_answers_where_a_feature_can_actually_stand():
    # GM 2026-07-25: fitting one extra well into a packed quarter cost three regenerate-and-check
    # cycles of hand-picked coordinates because nothing outside the engine could ask _fits where
    # there was room. open_seat asks it directly, so its answer is what placement will actually take.
    s = Settlement(1200, 1200, seed=3)
    s.meta(name="T", scale="town")
    s.block_polys.append([(390, 390), (500, 390), (500, 510), (390, 510)])  # the left half of the rect is no-build
    seat = s.open_seat((400, 400, 600, 500), 20, 20)
    assert seat is not None and s._fits(seat[0], seat[1], 20, 20)  # a seat the real placement path accepts
    assert seat[0] >= 500 and not s._in_blocked(*seat)  # ... off the blocked ground, which a manifest-only scan could not have known

    far = s.open_seat((400, 400, 600, 500), 20, 20, clear_of=[(600, 500)])  # stand away from an existing feature
    assert far is not None and math.hypot(far[0] - 600, far[1] - 500) > math.hypot(seat[0] - 600, seat[1] - 500)

    s.M["commons"] = [{"poly": [(490, 380), (620, 380), (620, 520), (490, 520)]}]  # grazed waste over the clear half
    assert s.open_seat((400, 400, 600, 500), 20, 20, well=True) is None  # a wellhead may not stand in it...
    assert s.open_seat((400, 400, 600, 500), 20, 20) is not None  # ... though anything else may

    s.block_polys.append([(0, 0), (1200, 0), (1200, 1200), (0, 1200)])  # nowhere left at all
    assert s.open_seat((400, 400, 600, 500), 20, 20) is None


@pytest.mark.tiers("city", "town")
def test_draft_byres_uses_the_legacy_size_off_the_to_scale_tiers():
    # a legacy tier (town/city) sizes its byre from the urban glyph grain (bscale), not px(feet) - the
    # non-to-scale branch of the byre sizer.
    s = _town()  # scale="town" -> not to-scale
    hs = [{"x": 300 + i * 170, "y": 350, "w": 40, "h": 28, "kind": "plain", "rot": 0, "wealth": 1.0} for i in range(3)]
    s.M["houses"] = hs
    for h in hs:
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    placed = s.draft_byres(fraction=1.0, gap=40)
    assert placed and all(b["w"] > 0 for b in s.M["byres"])

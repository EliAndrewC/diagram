"""How many wells a hamlet keeps, and where they may be sunk (feature 166).

Carries `settlement_has_wells`, `wells_off_the_wet_toe` and `wells_clear_of_paddies`, which the retired
battery re-measured on every finished map.

THE COUNT IS A RESEARCHED BAND, NOT A CONSTANT. `wells_sized_to_population` wants 2-20 households per
well at hamlet scale - the setting's deliberate prosperity liberty runs generous - so a twelve-household
hamlet may honestly draw anywhere from 1 to 6. One per ~6 households sits mid-band and matches what the
hand-authored hamlets drew: a couple of shared wells among the courtyards, not one per farm and not one
for the whole place.

THE GROUND IS THE PLACER'S OWN JOB, and its docstring says so: `_well_ground_clear` is described there as
"the placement half of `wells_clear_of_paddies`" and of `wells_off_the_wet_toe`. You do not dig a well in
a watercourse, in the middle of a crop plot, or in a bog - the last found by settlement-review on
Akagahara, a wellhead standing among drawn reed glyphs about 50 ft from the drainage pond.
"""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen import well_target


@pytest.mark.parametrize(("households", "want"), [(1, 1), (4, 1), (8, 1), (15, 2), (30, 5), (60, 6)])
def test_the_well_count_follows_the_household_count_inside_its_band(households: int, want: int) -> None:
    """`settlement_has_wells`. A hamlet with no well is not a hamlet, and one well per farm is a
    different settlement from the one the sources describe."""
    assert well_target(households) == want


def test_a_hamlet_always_keeps_at_least_one_well() -> None:
    """The floor is the part that must not drift: a settlement drawn with no water source at all is
    wrong at any size, and the smallest hamlets are exactly where a naive `households / 6` rounds to
    nothing."""
    assert all(well_target(n) >= 1 for n in range(1, 200))


def test_the_well_count_is_capped_so_a_large_hamlet_is_not_all_wells() -> None:
    """The ceiling matters as much as the floor. Without it a 200-household map draws 33 wells, which is
    a well per courtyard and reads as a waterworks rather than a farming settlement."""
    assert all(well_target(n) <= 6 for n in range(1, 500))


def test_the_count_stays_inside_the_researched_band_of_2_to_20_households_per_well() -> None:
    """The band is the actual finding; the `/6` is one honest choice inside it. Asserting the BAND rather
    than the divisor means a future re-tuning is free to move within the research and is caught the
    moment it leaves it."""
    for n in range(2, 121):
        per_well = n / well_target(n)
        assert 2.0 <= per_well <= 20.0, f"{n} households over {well_target(n)} wells is {per_well:.1f} per well"

"""Row-village farms reached at their doors, on the seeds that found the failure (feature 374 batch 10, wave 146).

The round arbiter's route B for ranking row 771 (W141-3) takes the row-village door seating up as a placer guarantee with "a
seed-pinned test that is red first": these rolls refused at HEAD before wave 146 - a farm whose own fixtures stood across its
way in, so no door path left it - and roll with every farm reached after it. They roll real maps, so they live in the soak
tier (`tests/soak/CLAUDE.md`: the same generator over more seeds; every line they reach the gate already covers)."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg


@pytest.mark.parametrize(
    ("seed", "households", "archetype"),
    [
        (12, 16, "polder_grid"),  # its privy and manure heap across the break in its south band (wave 146 probe)
        (4, 16, "mulberry_dike_fishpond"),  # a row farm with no route from its door (m:w141-archetype-rolls)
    ],
)
def test_a_row_farm_is_reached_at_its_door(seed: int, households: int, archetype: str) -> None:
    hg.generate(hg.HamletSpec(name=f"Row-{archetype}-{seed}", seed=seed, households=households, field_archetype=archetype))


def test_the_ten_household_valley_seed_four_refuses_only_off_a_ford() -> None:
    """Still open (ranking row 774 waits on it): since wave 146 its farm is reached, and the roll refuses instead on a row street
    over the brook off a ford. Pinned to that refusal, so a return to a farm unreached turns this red - and so does its fix,
    which then rewrites this test as the farm-reached one above."""
    from l7r.diagram.hamletgen.ways.last_resort import WebRefused

    with pytest.raises(WebRefused, match="off_ford"):
        hg.generate(hg.HamletSpec(name="Row-valley-4", seed=4, households=10))


def test_the_polder_seed_four_refuses_on_its_streets_needle() -> None:
    """A KNOWN REGRESSION, WAIVED (the round arbiter, ask:b10-w146-polder4-regression, accept): green at HEAD, refused since
    wave 146 - street 0's straight join ends on the road beside the junction street 1 passes through, a sliver no end-trim
    reaches. Pinned to that refusal, so its fix (with the polder's capacity, the second guarantee) turns this red."""
    from l7r.diagram.hamletgen.ways.last_resort import WebRefused

    with pytest.raises(WebRefused, match="needle_loops"):
        hg.generate(hg.HamletSpec(name="Row-polder-4", seed=4, households=16, field_archetype="polder_grid"))

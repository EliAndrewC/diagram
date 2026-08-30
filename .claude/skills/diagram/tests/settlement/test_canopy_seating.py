"""No canopy tree stands under another's crown (feature 166).

Carries `tree_crowns_not_subsumed`, which the retired battery re-measured on every finished map.

THE RULE IS AN OVERLAP THRESHOLD, NOT A BAN ON OVERLAP, and the distinction is the whole of it.
Neighboring canopies interlace - that is what a wood looks like from above. What is refused is a tree drawn
WHOLLY INSIDE another's crown, which draws ink nobody can see and inflates the stand's apparent density:
a crown is refused when its centre lies inside an already-seated crown, or an already-seated centre lies
inside it (`d < max(r, r_other)`). Edge overlap, between that and `r + r_other`, stays.

The measurement behind the rule: on a 13 ft grid with +-42% jitter, two neighbours landed 2-3 ft apart and
a 6 ft crown vanished under a 12 ft one - 950 of the recorded crowns had their centre more than halfway
inside another. `research/vegetation.md`, "Forest density and crown size".
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

_crown_seat_clear = Settlement._crown_seat_clear


def test_a_crown_whose_centre_lies_inside_a_seated_crown_is_refused() -> None:
    seated = [(100.0, 100.0, 20.0)]
    assert not _crown_seat_clear(110.0, 100.0, 6.0, seated), "a small tree 10 ft inside a 20 ft crown vanishes under it"


def test_a_seated_crown_swallowed_by_a_NEW_larger_one_is_refused_too() -> None:
    """The rule is symmetric, and it has to be: the seating runs biggest-first, but a stand merged from
    two sources can offer a large crown after a small one is already down. Testing only one direction
    would let the same defect in through the other."""
    seated = [(100.0, 100.0, 5.0)]
    assert not _crown_seat_clear(104.0, 100.0, 30.0, seated), "a 30 ft crown swallowing a seated 5 ft one"


def test_interlacing_neighbours_are_allowed() -> None:
    """What a wood looks like from above. A rule that refused all overlap would draw an orchard."""
    seated = [(100.0, 100.0, 20.0)]
    assert _crown_seat_clear(135.0, 100.0, 20.0, seated), "crowns 35 apart with radius 20 each interlace, and may"


def test_a_crown_clear_of_everything_is_allowed() -> None:
    assert _crown_seat_clear(500.0, 500.0, 12.0, [(100.0, 100.0, 20.0)])


def test_the_threshold_is_max_radius_not_sum_and_not_either_one_alone() -> None:
    """Pinning the exact quantity, because `dev/gate.md` collects nine defects that were each a correct
    measurement of a DIFFERENT quantity. `d < max(r, r_other)` refuses; `d` between that and the SUM
    interlaces and is allowed."""
    seated = [(0.0, 0.0, 20.0)]
    assert not _crown_seat_clear(19.0, 0.0, 6.0, seated), "d=19 < max(20, 6) -> refused"
    assert _crown_seat_clear(21.0, 0.0, 6.0, seated), "d=21 > max(20, 6) -> interlacing, allowed"
    assert _crown_seat_clear(25.0, 0.0, 6.0, seated), "and well short of the sum (26), still allowed"


# ---- and the other half: no crown is drawn on a roof or a wellhead --------------------------------
# Carries `structures_clear_of_trees` and `wells_clear_of_trees`. The canopy is flushed LAST, after the
# buildings are down, so the guarantee has to live in the canopy placer rather than in the structure one -
# `_canopy_keepouts` collects what is already standing and `_crown_covers` refuses a tree over it.


def test_a_crown_is_refused_over_a_recorded_roof() -> None:
    """`structures_clear_of_trees`. A tree drawn over a farmhouse hides the building the map exists to
    show, and by flush time every roof is already recorded - so there is no excuse for missing one."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Woods", scale="hamlet", ftpx=1, down_deg=90)
    krect = [(400.0, 400.0, 60.0, 40.0)]
    assert s._crown_covers(410.0, 405.0, 14.0, krect, [], s.CANOPY_PAD), "a crown over a roof is refused"
    assert not s._crown_covers(900.0, 900.0, 14.0, krect, [], s.CANOPY_PAD), "and one well clear of it is not"


def test_a_crown_is_refused_over_a_wellhead() -> None:
    """`wells_clear_of_trees`. A wellhead under a canopy is a wellhead nobody can see, and the well is
    the one feature a reader looks for first on a farming map."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Woods", scale="hamlet", ftpx=1, down_deg=90)
    kcirc = [(300.0, 300.0, 12.0)]
    assert s._crown_covers(305.0, 300.0, 14.0, [], kcirc, s.CANOPY_PAD), "a crown over the wellhead is refused"
    assert not s._crown_covers(800.0, 300.0, 14.0, [], kcirc, s.CANOPY_PAD), "and one away from it is not"

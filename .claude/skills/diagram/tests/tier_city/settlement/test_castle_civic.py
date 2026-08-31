"""tier city tests split out of `tests.settlement.test_castle_civic` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _cap020


@pytest.mark.tiers("city")
def test_label_hits_counts_gate_furniture_arches_and_wellheads():
    # the ladder's scorer must see every drawn glyph a caption can bury. A torii is a bare [x, y, z]
    # triple and a wellhead has no w/h, so neither is in self.placed and both were invisible to it
    # (GM 2026-07-27) - which is how Tango's theater-stage caption walked onto Benten's gate and its
    # cremation-ground caption onto a well.
    s = Settlement(600, 600, seed=1)
    s.meta(name="T", scale="city", ftpx=3, down_deg=90)
    assert s._label_hits(300, 300, "caption", 11) == 0
    s.M.setdefault("gate_structs", []).append({"x": 300, "y": 300, "w": 20, "h": 12})
    s.M["torii"].append([300, 300, 1])
    s.M["wells"].append({"x": 300, "y": 300, "r": 8, "vr": 4})
    assert s._label_hits(300, 300, "caption", 11) == 3


@pytest.mark.tiers("city")
def test_dojos_roll_follows_the_samurai_cohort():
    # GM formula 2026-07-25: 1 private dojo per full 200 SAMURAI (the city's ~10% share of its
    # population) + a remainder-fraction chance of one extra, floored at 1; count= pins; too few
    # seats is loud. The samurai cohort is the driver, not the population - a dojo serves samurai
    # and nobody else - so the constants are read off the class rather than assumed here.
    def city_(seed, pop):
        s_ = Settlement(1200, 1200, seed=seed)
        s_.meta(name="C", scale="city", ftpx=3)
        s_.M["meta"]["population"] = pop
        return s_

    assert Settlement.DOJO_SAMURAI_FRAC == 0.10 and Settlement.DOJO_PER_SAMURAI == 200
    s = city_(2, 2000)  # 200 samurai = one full unit, zero remainder: exactly 1, no roll can add
    assert s.dojos([(300, 300), (600, 600)]) == 1
    assert s.M["meta"]["dojo_roll"] == 1 and len(s.M["dojos"]) == 1
    s2 = city_(2, 4000)  # 400 samurai = two full units, zero remainder: exactly 2
    assert s2.dojos([(300, 300), (600, 600)]) == 2
    assert len(s2.M["dojos"]) == 2
    # 3,000 -> 300 samurai -> 1 guaranteed + a 50% roll; the two seeds below straddle it
    rolls = {seed: city_(seed, 3000).dojos([(300, 300), (600, 600)]) for seed in (47, 162)}
    assert set(rolls.values()) <= {1, 2}
    assert city_(47, 3000).dojos([(300, 300), (600, 600)], count=2) == 2  # a pin overrides the roll
    s4 = city_(2, 4000)
    with pytest.raises(ValueError, match="vetted seats"):
        s4.dojos([(300, 300)])  # a guaranteed 2 needs 2 seats


@pytest.mark.tiers("capital", "city")
def test_ministry_label_inside_stacks_two_lines_on_the_glyph():
    """The capital's ministry captions sit ON the glyph (GM 2026-08-09) - the estate rule
    applied to the state offices, two stacked lines because the long names cannot fit the
    width in one; a provincial city keeps its beside-captions (smaller compounds)."""
    s = _cap020()
    s.ministry(700, 700, "Ministry of Retainers", label_inside=True)
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    recs = [L for L in s.M["labels"] if len(L) > 5 and L[5] in ("Ministry of", "Retainers")]
    assert len(recs) == 2
    for box2 in recs:
        assert box2[0] > 662 and box2[2] < 738 and box2[1] > 675 and box2[3] < 725  # on the glyph
    s2 = _cap020()
    s2.ministry(700, 700, "Records Hall", label_inside=True)  # a non-"Ministry of" office keeps one line
    s2.place_labels()  # feature 157: the LABEL PHASE
    assert any(len(L) > 5 and L[5] == "Records Hall" for L in s2.M["labels"])


# ---- feature 174: the private dojos, whose COUNT is a GM formula ----------------------------------


def test_the_dojo_count_follows_the_SAMURAI_cohort_not_the_population() -> None:
    """GM 2026-07-25, the bathhouse pattern applied to a samurai-driven institution: ONE dojo per
    full 200 samurai, plus a chance of one extra equal to the remainder fraction, floored at 1.

    WHY the samurai count and not the population: a dojo serves samurai and nobody else. The two
    happen to track at a 10% samurai share, but that is an arithmetic accident - if a city's share
    is ever declared away from 10%, this follows the samurai and the bathhouses do not.

    A 4,000-seat city (~400 samurai) keeps exactly 2, which is the case with no roll in it.
    """
    s = Settlement(2000, 2000, seed=5)
    s.meta(name="C", scale="city", population=4000)
    seats = [(300.0 + 200.0 * i, 300.0) for i in range(4)]
    n = s.dojos(seats)
    assert n == 2, "400 samurai is two full 200s and no remainder"
    assert len(s.M["dojos"]) == n and s.M["meta"]["dojo_roll"] == n, "and the roll is recorded, so a stale hand count cannot ship"


def test_the_dojo_count_is_FLOORED_at_one_because_the_private_tail_is_never_empty() -> None:
    """ "Floored at 1 - the private tail is never empty at this tier." A small provincial city still
    has a machi-dojo, so the formula may not round it away."""
    s = Settlement(2000, 2000, seed=5)
    s.meta(name="C", scale="city", population=600)
    assert s.dojos([(300.0, 300.0), (500.0, 300.0)]) >= 1


def test_too_few_vetted_seats_RAISES_rather_than_silently_placing_fewer() -> None:
    """The no-silent-caps rule: the gen author supplies vetted seats, and if the roll wants more
    than they supplied that is an authoring error to fix, not a shortfall to absorb - the samurai
    band can ask for up to 2."""
    s = Settlement(2000, 2000, seed=5)
    s.meta(name="C", scale="city", population=4000)
    with pytest.raises(ValueError, match="dojos rolled"):
        s.dojos([(300.0, 300.0)])


def test_a_private_dojo_records_itself_and_blocks() -> None:
    """The single-dojo drawing call underneath the roll."""
    s = Settlement(1000, 1000, seed=3)
    s.meta(name="C", scale="city")
    s.dojo(500.0, 500.0)
    assert s.M["dojos"], "recorded under its own key"
    assert not s._fits(500.0, 500.0, 8.0, 8.0), "and it holds its lot"

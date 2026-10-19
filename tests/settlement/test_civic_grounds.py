"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement

# ---- the justice works (feature 015) ----------------------------------------------------------


# ---- feature 021: districts + retainer terraces -----------------------------------------------


def test_district_records_a_named_region():
    """s.district is a declarative overlay like quarter(): records only, draws nothing (T003)."""
    s = _crop_settlement()
    s.district("east machi", "machi", [(100, 100), (400, 100), (400, 400), (100, 400)])
    s.district("castle foot", "terrace", [(500, 100), (700, 100), (700, 300), (500, 300)], rank_band="terrace")
    d = s.M["districts"]
    assert [r["name"] for r in d] == ["east machi", "castle foot"]
    assert "rank_band" not in d[0] and d[1]["rank_band"] == "terrace"


# ---------------------------------------------------------------------------
# Feature 115 composed-surface guard. See specs/115-civic-grounds-package/contracts/mixin-surface.md.
# ---------------------------------------------------------------------------

_CIVIC_GROUNDS_SURFACE = frozenset(
    {
        # funerary.py
        # justice.py
        # civic.py
        "district",
        # lodging.py
        # _way_seat_near is LIVE despite having no consumer outside civic_grounds.py: it is called by
        # _way_bearing_near, one line, inside the defining file. The pre-spec census excluded the
        # defining file (to avoid counting the def as a use) and so reported it deletable. A
        # dead-member census MUST count intra-file callers - research R6.
        # stable_yard.py
    }
)


def _civic_grounds_submixins():
    # Derived from the MRO rather than by importing the submodules, so this guard runs UNCHANGED
    # before and after the split: pre-split the list is empty (CivicGroundsMixin is the single class
    # and the collision assertion is vacuous), post-split it is the five sub-mixins. Feature 114's
    # tasks T007 records why the by-name-import shape cannot be red-proven in task order.
    from l7r.diagram.settlement.civic_grounds import CivicGroundsMixin

    return [c for c in CivicGroundsMixin.__mro__ if c is not CivicGroundsMixin and c is not object]


def _cg_own_members(cls):
    # Any non-dunder name the class body itself defines: methods AND data attributes. CivicGroundsMixin
    # has no class-level attributes today (all 22 members are functions, unlike 114's StructuresMixin),
    # so the data half is currently vacuous - kept because a constant is as easy to lose in a split as
    # a method and much easier to overlook if it is added later.
    return {k for k in vars(cls) if not k.startswith("__")}


def test_no_pre_split_civic_grounds_member_was_lost_in_the_move():
    # SUBSET, not equality: feature 115's stage 2 legitimately ADDS named private stages to
    # stable_yard.py, and equality would turn that into a contract edit - training a reader to update
    # the frozenset without thinking, which is the reflex that lets a real subtraction through. What
    # must never happen is a pre-split member going MISSING: an addition is visible in review, a
    # subtraction is silent until whichever generator calls it happens to run - and for
    # precinct_interior that is one frozen exhibit nobody runs by default.
    from l7r.diagram.settlement.civic_grounds import CivicGroundsMixin

    composed = set().union(*(_cg_own_members(c) for c in CivicGroundsMixin.__mro__))
    assert composed >= _CIVIC_GROUNDS_SURFACE, f"missing={sorted(_CIVIC_GROUNDS_SURFACE - composed)}"


def test_no_two_civic_grounds_submixins_define_the_same_name():
    # A member defined by two sub-mixins produces a working import, a clean `mypy --strict`, and one
    # silently dead implementation, because MRO just picks the first base. Nothing else in the gate
    # can see this.
    subs = _civic_grounds_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _cg_own_members(a) & _cg_own_members(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"


def test_every_civic_grounds_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely CivicGroundsMixin.
    # structures/compounds.py calls self._ward_fence_cap and trades.py calls self._way_bearing_near.
    unreachable = sorted(n for n in _CIVIC_GROUNDS_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"


# ---- feature 174: the two lodging works, which only a TOWN draws ----------------------------------
# `flophouse` and `inn` were wholly uncovered (94 statements at 46%) because no scripted generator
# produces a town yet. Both are ordinary drawing methods on a Settlement, so both take a direct call
# rather than waiting for the tier to convert - the same route that closed the _knobs town/city
# branches. What is asserted is the RULE each carries, not that the lines ran.


# ---- The caravan inn's FORM is a knob (feature 244) ---------------------------------------------------

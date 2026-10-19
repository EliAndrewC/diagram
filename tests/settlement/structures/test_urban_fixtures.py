"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/urban_fixtures.py`."""

from l7r.diagram.settlement import Settlement

from ._builders import _STRUCTURES_SURFACE, _own_members, _structures_submixins


def test_no_pre_split_structures_member_was_lost_in_the_move():
    # SUBSET, not equality, for the reason features 112 and 113 both recorded in their own guards:
    # a later decomposition legitimately adds named private helpers, and equality would turn every
    # such change into a contract edit - training a reader to update the frozenset without
    # thinking, which is exactly the reflex that lets a real subtraction through. What must never
    # happen is a pre-split member going MISSING: an addition is visible in review, a subtraction
    # is silent until whichever generator calls it happens to run.
    from l7r.diagram.settlement.structures import StructuresMixin

    composed = set().union(*(_own_members(c) for c in StructuresMixin.__mro__))
    assert composed >= _STRUCTURES_SURFACE, f"missing={sorted(_STRUCTURES_SURFACE - composed)}"


def test_no_two_structures_submixins_define_the_same_name():
    # The half that is easy to under-rate: a member defined by two sub-mixins produces a working
    # import, a clean `mypy --strict`, and one silently dead implementation, because MRO just picks
    # the first base.
    subs = _structures_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _own_members(a) & _own_members(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"


def test_every_structures_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely StructuresMixin
    unreachable = sorted(n for n in _STRUCTURES_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"

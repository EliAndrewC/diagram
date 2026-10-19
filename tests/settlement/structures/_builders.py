"""Split from test_structures.py by feature 174 - see this directory's CLAUDE.md."""


# ---- feature 114: the composed StructuresMixin surface ------------------------------------------
# The guard for the settlement/structures.py -> settlement/structures/ package split. See
# specs/114-structures-package/contracts/mixin-surface.md for the contract and its red proofs.

_STRUCTURES_SURFACE = frozenset(
    {
        # public entry points, called from pool gens, wip/, other engine modules and tests
        # "drum_tower" moved to structures/urban_fixtures.py (UrbanFixturesMixin) under feature 145 - still on Settlement
        "kosatsuba",
        "place_kosatsuba",
        # "theater_stage" moved to structures/urban_fixtures.py (UrbanFixturesMixin) under feature 145 - still on Settlement
        # private helpers, reached through self. Several have no consumer outside the class at
        # all - they stay in the surface precisely because a name nothing else calls is the kind a
        # careless partition drops without any other test noticing.
        # class-level ATTRIBUTES - the half a methods-only census cannot see. Feature 112 needed a
        # separate test (test_feature_012_archetype_constants_survived_the_split) because its guard
        # counted callables only; this one admits any non-dunder class-body name, so one assertion
        # covers all 33 members. A class attribute is as easy to lose in a split as a method and
        # much easier to overlook.
    }
)


def _structures_submixins():
    # Derived from the MRO rather than by importing the submodules, so this guard runs UNCHANGED
    # before and after the split: pre-split the list is empty (StructuresMixin is the single class
    # and the collision assertion is vacuous), post-split it is the seven sub-mixins. Importing
    # settlement.structures.urban et al. directly - the shape feature 112 used - cannot be written
    # before the package it imports from exists, which is what made 112's own red proof for the
    # collision assertion impossible to run in the order its task list implied (113 tasks T007).
    from l7r.diagram.settlement.structures import StructuresMixin

    return [c for c in StructuresMixin.__mro__ if c is not StructuresMixin and c is not object]


def _own_members(cls):
    # Any non-dunder name the class body itself defines: methods AND data attributes. Deliberately
    # NOT `callable(v)` - that is what makes URBAN
    # visible here rather than needing a second test of their own.
    return {k for k in vars(cls) if not k.startswith("__")}

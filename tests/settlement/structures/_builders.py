"""Split from test_structures.py by feature 174 - see this directory's CLAUDE.md."""


# ---- feature 114: the composed StructuresMixin surface ------------------------------------------
# The guard for the settlement/structures.py -> settlement/structures/ package split. See
# specs/114-structures-package/contracts/mixin-surface.md for the contract and its red proofs.

_STRUCTURES_SURFACE = frozenset(
    {
        # public entry points, called from pool gens, wip/, other engine modules and tests
        "building",
        "clear_label_seat",
        # "drum_tower" moved to structures/urban_fixtures.py (UrbanFixturesMixin) under feature 145 - still on Settlement
        "fire_tower",
        "kosatsuba",
        "label_blockers",
        "label_caption_hw",
        "label_seat_clear",
        "manor",
        "merchant_estate",
        "merchant_estates",
        "open_face_rot",
        "pack",
        "pasture",
        "place_kosatsuba",
        "place_punishment_spot",
        "road",
        "rowpack",
        "servant_ranges",
        # "theater_stage" moved to structures/urban_fixtures.py (UrbanFixturesMixin) under feature 145 - still on Settlement
        "try_building",
        # private helpers, reached through self. Several have no consumer outside the class at
        # all - they stay in the surface precisely because a name nothing else calls is the kind a
        # careless partition drops without any other test noticing.
        "_blocks_any_door",
        "_dims",
        "_door_is_clear",
        "_estate_wall_clear",
        "_face_street_rot",
        "_office_records",
        "_shortfall",
        "_solid_records",
        "_under_a_caption",
        # class-level ATTRIBUTES - the half a methods-only census cannot see. Feature 112 needed a
        # separate test (test_feature_012_archetype_constants_survived_the_split) because its guard
        # counted callables only; this one admits any non-dunder class-body name, so one assertion
        # covers all 33 members. A class attribute is as easy to lose in a split as a method and
        # much easier to overlook.
        "URBAN",
        "SERVANT_RANGE_DEPTH_FT",
        "_OFFICE_STANDOFF",
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
    # NOT `callable(v)` - that is what makes URBAN, SERVANT_RANGE_DEPTH_FT and _OFFICE_STANDOFF
    # visible here rather than needing a second test of their own.
    return {k for k in vars(cls) if not k.startswith("__")}

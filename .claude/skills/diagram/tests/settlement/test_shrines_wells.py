"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import math

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _byre_village, _crop_settlement, _nuc_village, _scatter_base_points, _town, _village, _walled_city


def test_a_wellhead_is_refused_in_the_paddy_water_and_allowed_on_the_rim():
    # the PLACEMENT half of wells_clear_of_paddies - both halves read paddy_wet_rings, so the siter
    # and the check cannot disagree about where the water is (the same-source doctrine)
    s = _town()
    basin = [[600, 600], [900, 600], [900, 900], [600, 900]]
    s.M["fields"] = [{"name": "f1", "kind": "paddy", "outline": [[400, 400], [900, 400], [900, 900], [400, 900]], "plot_polys": [basin]}]
    assert not s._well_ground_clear(750, 750)  # in the water
    assert not s._well_ground_clear(750, 594)  # the drawn head laps a basin's edge
    assert s._well_ground_clear(450, 450)  # the fan's unplanted rim slack, inside the envelope
    s.M["fields"][0]["plot_polys"] = [[[0, 0], [1, 1]]]  # a field drawing no real basins...
    assert not s._well_ground_clear(450, 450)  # ...falls back to its outline, as the rural tiers do
    s.M["fields"][0]["outline"] = [[0, 0]]  # and one drawing nothing at all contributes no water
    assert s._well_ground_clear(450, 450)
    s.M["fields"][0]["kind"] = "dry"  # a DRY field is not this rule's business
    assert s._well_ground_clear(750, 750)


def test_torii_path_places_one_torii_per_interior_vertex():
    s = _town()
    s.torii_path([(0, 0), (50, 50), (100, 0)])
    assert len(s.M["torii"]) == 1


def test_torii_even_runs():
    s = _town()
    s.torii_even([(0, 0), (100, 0), (100, 100)], 4)
    assert len(s.M["torii"]) == 4


def test_tree_stand_canopy_is_deferred_and_never_drawn_over_a_building_or_well():
    # the canopy is QUEUED at forest_patch() time and drawn at flush, so it is filtered against the
    # COMPLETE map: a building and a well placed AFTER the wood still end up with clear roofs.
    s = _town()
    s.forest_patch([(300, 300), (900, 300), (900, 900), (300, 900)])
    assert not s.M["tree_crowns"]  # nothing drawn yet - only the litter floor is down
    s.building(600, 600, 60, 40, "merchant", 0)
    s.well(500, 500)
    s.flush_tree_stands()
    crowns = s.M["tree_crowns"]
    assert crowns  # the stand itself did draw
    b = s.M["buildings"][-1]
    wl = s.M["wells"][-1]
    for i in range(0, len(crowns), 3):
        x, y, r = crowns[i], crowns[i + 1], crowns[i + 2]
        # CIRCLE vs RECT, the same rounded-corner measure `_crown_covers` and the gate's
        # structures_clear_of_trees use - NOT the naive AABB this line used to carry. The AABB
        # includes the four CORNER squares a circle cannot reach, so it called a crown sitting
        # diagonally off a corner an overlap: (562.5, 573.7) r=8.7 against a 60x40 building at
        # (600, 600) is 7.5 x 6.3 px clear of the nearest corner, i.e. 9.8 px away from a crown
        # that reaches 8.7. It only ever passed because no crown had landed in a corner diagonal
        # before the 2026-08-08 re-roll put one there (test geometry stricter than the rule it
        # guards is a false alarm waiting for a re-roll).
        dx, dy = max(abs(x - b["x"]) - b["w"] / 2, 0.0), max(abs(y - b["y"]) - b["h"] / 2, 0.0)
        assert dx * dx + dy * dy >= r * r
        assert math.hypot(x - wl["x"], y - wl["y"]) >= r + wl.get("vr", wl["r"])
    n = len(crowns)
    s.flush_tree_stands()  # idempotent - the queue is drained
    assert len(s.M["tree_crowns"]) == n


def test_fringe_trees_keep_off_the_crop():
    # the wood's advance-growth fringe seeds on waste ground, never in a worked field
    s = _town()
    s.field_polys.append([(100, 100), (400, 100), (400, 400), (100, 400)])
    assert s._fringe_blocked(250, 250, 8) is True  # inside the crop
    assert s._fringe_blocked(392, 250, 8) is True  # ... and within a crown's reach of its edge
    assert s._fringe_blocked(700, 700, 8) is False  # open waste ground


def test_commons_clears_the_wellhead_apron():
    s = _crop_settlement()
    s.well(300, 300)
    before = len(s.out)
    s.commons([(150, 150), (500, 150), (500, 450), (150, 450)], role="pasture")
    lim = s.M["wells"][0]["vr"] + 20 * s.bscale - 0.06  # 0.1-rounding slack, as in the halo test
    pts = _scatter_base_points(s.out[before:])
    assert pts and all((px - 300) ** 2 + (py - 300) ** 2 > lim * lim for px, py in pts)


def test_commons_keeps_scrub_off_a_shrine_and_torii():
    # a commons that OVERLAPS the shrine must not scatter scrub over the hall or its torii arch (both are
    # block_polys); the skip is per-tuft, so the plot is still recorded
    s = _nuc_village()
    s.shrine_hall(320, 400, "", w=60, h=48, kind="shrine", torii=[(320, 330)], graveyard=False)
    s.commons([(220, 150), (420, 150), (420, 650), (220, 650)])  # straddles the shrine + torii blocks
    assert len(s.M["commons"]) == 1


def test_marsh_keeps_reeds_off_a_building():
    s = _crop_settlement()
    s.shrine_hall(300, 300, "", w=60, h=48, kind="shrine", graveyard=False)  # a block_poly inside the marsh
    s.marsh([(150, 150), (500, 150), (500, 450), (150, 450)])  # reeds on the hall are skipped
    assert len(s.M["marshes"]) == 1


def test_torii_refuses_a_seat_standing_in_a_wall():
    # a torii is a freestanding gateway; an arch set INTO a barrier is impossible construction, so
    # the primitive refuses it outright (the hand-placed path - an avenue shortens itself instead)
    s = _walled_city()
    with pytest.raises(ValueError, match="would stand in the samurai ward fence"):
        s.torii_path([(600, 600), (600, 700), (600, 800)])


def test_draft_byres_scatters_shared_sheds_among_the_houses():
    s, hs = _byre_village()
    placed = s.draft_byres(fraction=0.6, gap=40)  # ~60% of 5 = 3 shared byres
    assert len(placed) == 3 and len(s.M["byres"]) == 3
    assert all(b["w"] > 0 and b["h"] > 0 for b in s.M["byres"])
    assert "<rect" in s.out[-1]  # a byre glyph was drawn


def test_draft_byres_skips_a_homestead_boxed_in_on_all_sides():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 300, "y": 300, "w": 40, "h": 28, "kind": "plain", "rot": 0, "wealth": 1.0}]
    s.placed.append((300, 300, 40, 28))
    for a in range(0, 360, 20):  # wall the homestead in with placed footprints
        rad = math.radians(a)
        s.placed.append((300 + 70 * math.cos(rad), 300 + 70 * math.sin(rad), 60, 60))
    assert s.draft_byres(fraction=1.0) == []  # nowhere to put a byre -> skipped


def test_draft_byres_keeps_off_the_paddy():
    s = _crop_settlement()
    s.M["houses"] = [{"x": 300, "y": 300, "w": 40, "h": 28, "kind": "plain", "rot": 0, "wealth": 1.0}]
    s.placed.append((300, 300, 40, 28))
    s.field_polys.append([(330, 200), (600, 200), (600, 500), (330, 500)])  # paddy on the E half of the ring
    placed = s.draft_byres(fraction=1.0)
    assert len(placed) == 1 and placed[0][0] < 330  # the byre lands on the dry (W) side, off the paddy


def test_shrine_well_places_a_well_beside_the_hall():
    s = _crop_settlement()
    s.M["religious"] = [{"x": 400, "y": 400, "w": 30, "h": 24, "kind": "shrine"}]
    spot = s.shrine_well(400, 400)
    assert spot is not None
    import math as _m

    assert _m.hypot(spot[0] - 400, spot[1] - 400) <= 115 and len(s.M["wells"]) == 1  # close beside the hall


def test_shrine_well_returns_none_when_boxed_in():
    s = _crop_settlement()
    for a in range(0, 360, 15):  # wall off every ring position around the hall
        rad = math.radians(a)
        for rr in (54, 66, 80, 96, 112):
            s.placed.append((400 + rr * math.cos(rad), 400 + rr * math.sin(rad), 40, 40))
    assert s.shrine_well(400, 400) is None and not s.M["wells"]


# ---- shrine: the primary Shinto hall glyph -------------------------------------------------
def test_shrine_draws_and_records_a_religious_hall():
    s = _village()
    s.shrine(300, 300)
    # TRUE SCALE (2026-07-21): the default is a 62x42 ft tutelary hall drawn through px(), no longer 104x68 raw px
    assert s.M["shrine"] == [300 - s.px(62) / 2, 300 - s.px(42) / 2, s.px(62), s.px(42)]
    assert any(r["kind"] == "shrine" and r["x"] == 300 for r in s.M["religious"])


def test_well_ground_clear_refuses_water_and_crop():
    """You do not sink a well in a watercourse, and you do not sink one in a crop plot. Placement
    predicted everything else about a well site - lanes, compounds, the bound, its neighbors - but
    never the water or the crop, which is how the overlap matrix found four wells standing in
    ditches, a channel and a hatake plot across three maps."""
    s = _town()
    assert s._well_ground_clear(500, 500)  # bare ground
    s.M["streams"] = [{"poly": [[500, 300], [500, 700]], "w": 9}]
    assert not s._well_ground_clear(500, 500)
    assert s._well_ground_clear(900, 500)  # well clear of it
    s.M["streams"] = []
    s.M["field_ditches"] = [{"poly": [[400, 500], [600, 500]], "w": 1.5}]
    assert not s._well_ground_clear(500, 500)
    s.M["field_ditches"] = []
    s.M["pond"] = [500, 500, 40, 24]
    assert not s._well_ground_clear(505, 500)
    assert s._well_ground_clear(900, 900)
    s.M["pond"] = None
    s.M["dry_plots"] = [{"poly": [[480, 480], [560, 480], [560, 560], [480, 560]], "crop": "barley", "theta": 0}]
    assert not s._well_ground_clear(520, 520)  # inside the plot
    assert not s._well_ground_clear(474, 520)  # its drawn head laps the plot's edge
    assert s._well_ground_clear(900, 900)


def test_place_wells_cistern_kind_is_recorded():
    """kind='cistern' marks a josui-ido on the buried main (research 021 item 4) - the record
    carries the kind so the service-band check and the samurai-quarter exemption can read it."""
    s = Settlement(600, 600, seed=5)
    seats = s.place_wells((100, 100, 300, 300), spacing=80, kind="cistern", coverage=False)
    assert seats, "the open ground must seat at least one well"
    ws = [w for w in s.M["wells"] if isinstance(w, dict) and w.get("kind") == "cistern"]
    assert len(ws) == len(seats)


# ---- feature 116: the composed ShrinesWellsMixin surface -----------------------------------------
# The guard for the settlement/shrines_wells.py -> settlement/shrines_wells/ package split. See
# specs/116-shrines-wells-package/contracts/mixin-surface.md for the contract and its red proofs.

_SHRINES_WELLS_SURFACE = frozenset(
    {
        # public entry points, called from pool gens, wip/, other engine modules and tests
        "draft_byres",
        "farm_wells",
        "flush_tree_stands",
        "forest",
        "frozen_terrain",
        "hill",
        "open_seat",
        "place_wells",
        "shrine",
        "shrine_hall",
        "shrine_well",
        "small_shrine",
        "torii_even",
        "torii_path",
        "well",
        "well_at",
        # private helpers, reached through self. - six of them from OUTSIDE this package
        # (_assert_walls_clear_of_torii from water_ways/civic_grounds/structures.compounds, _well_vr
        # and _well_ground_clear from civic_grounds, _tree_stand from castle_civic/core). The other
        # thirteen have no consumer outside the class at all - they stay in the surface precisely
        # because a name nothing else calls is the kind a careless partition drops without any other
        # test noticing.
        "_assert_walls_clear_of_torii",
        "_avenue_at_threshold",
        "_avenue_pitch",
        "_avenue_short_of_walls",
        "_build_well_index",
        "_crowns",
        "_draw_byre",
        "_draw_stand",
        "_farm_wells",
        "_footprint_clear",
        "_fringe_blocked",
        "_hall_caption_y",
        "_in_scrub_cover",
        "_place_wells",
        "_stand_fringe",
        "_terrain_fingerprint",
        "_torii",
        "_tree_stand",
        "_well_ground_clear",
        "_well_index",
        "_well_vr",
        "_wet_toe_keepout",
    }
)


def _shrines_wells_submixins():
    # Derived from the MRO rather than by importing the submodules, so this guard runs UNCHANGED
    # before and after the split: pre-split the list is empty (ShrinesWellsMixin is the single class
    # and the collision assertion is vacuous), post-split it is the seven sub-mixins. Importing
    # settlement.shrines_wells.wells et al. directly - the shape feature 112 used - cannot be written
    # before the package it imports from exists, which is what made 112's own red proof for the
    # collision assertion impossible to run in the order its task list implied (113 tasks T007).
    from l7r.diagram.settlement.shrines_wells import ShrinesWellsMixin

    return [c for c in ShrinesWellsMixin.__mro__ if c is not ShrinesWellsMixin and c is not object]


def _own_members(cls):
    # Any non-dunder name the class body itself defines: methods AND data attributes. Deliberately
    # NOT `callable(v)` - this class has no class-level constant today, but feature 112 needed a
    # whole extra test because its guard counted callables only, and this form covers the constant
    # somebody adds later for free.
    return {k for k in vars(cls) if not k.startswith("__")}


def test_no_pre_split_shrines_wells_member_was_lost_in_the_move():
    # SUBSET, not equality, for the reason features 112, 113 and 114 all recorded: a later
    # decomposition legitimately adds named private helpers, and equality would turn every such
    # change into a contract edit - training a reader to update the frozenset without thinking,
    # which is exactly the reflex that lets a real subtraction through. What must never happen is a
    # pre-split member going MISSING: an addition is visible in review, a subtraction is silent
    # until whichever generator calls it happens to run.
    from l7r.diagram.settlement.shrines_wells import ShrinesWellsMixin

    composed = set().union(*(_own_members(c) for c in ShrinesWellsMixin.__mro__))
    assert composed >= _SHRINES_WELLS_SURFACE, f"missing={sorted(_SHRINES_WELLS_SURFACE - composed)}"


def test_no_two_shrines_wells_submixins_define_the_same_name():
    # The half that is easy to under-rate: a member defined by two sub-mixins produces a working
    # import, a clean `mypy --strict`, and one silently dead implementation, because MRO just picks
    # the first base.
    subs = _shrines_wells_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _own_members(a) & _own_members(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"


def test_every_shrines_wells_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely ShrinesWellsMixin
    unreachable = sorted(n for n in _SHRINES_WELLS_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not reachable on Settlement: {unreachable}"


def test_frozen_terrain_is_still_a_context_manager():
    # The hazard unique to THIS split (specs/116 research R5): frozen_terrain is the first decorated
    # member in the lineage, and `ast` reports FunctionDef.lineno at the `def`, one line BELOW
    # @contextlib.contextmanager. A slice that drops the decorator keeps the NAME - so the surface
    # guard above passes, mypy --strict passes, the package imports - and turns a context manager
    # into a plain generator that fails at every `with self.frozen_terrain():` call site.
    s = Settlement(400, 400, seed=1)
    with s.frozen_terrain():
        assert s._frozen_wells is not None, "the freeze must actually build the index inside the scope"
    assert s._frozen_wells is None, "and release it on the way out"

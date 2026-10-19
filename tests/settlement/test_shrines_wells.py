"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import math

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _byre_village, _crop_settlement, _ground_points, _town, _village


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


def test_torii_even_takes_a_single_arch():
    # the commonest torii roll is one arch; `count - 1` divided by zero (found by the feature-316 audit)
    s = _town()
    s.torii_even([(0, 0), (100, 0), (100, 100)], 1)
    assert len(s.M["torii"]) == 1


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
    pts = _ground_points(s, before)
    assert pts and all((px - 300) ** 2 + (py - 300) ** 2 > lim * lim for px, py in pts)


def test_draft_byres_scatters_shared_sheds_among_the_houses():
    s, hs = _byre_village()
    s.pin_knob("byre_form", "detached_commons")  # the shared shed, the rare guess (269 B16) - the one form `fraction` sizes
    placed = s.draft_byres(fraction=0.6, gap=40)  # ~60% of 5 = 3 shared byres
    assert len(placed) == 3 and len(s.M["byres"]) == 3
    assert s.M["meta"]["byre_form"] == "detached_commons", "a map that draws byres declares their form (`byre_form_declared`)"
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
        "flush_tree_stands",
        # "forest" moved to shrines_wells/forest.py (ForestMixin) under feature 145 - still on Settlement, off the hamlet path module
        "frozen_terrain",
        "open_seat",
        "place_wells",
        "shrine",
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
        "_build_well_index",
        "_crowns",
        "_draw_byre",
        "_draw_stand",
        "_footprint_clear",
        "_fringe_blocked",
        "_in_scrub_cover",
        "_place_wells",
        "_stand_fringe",
        "_terrain_fingerprint",
        "_torii",
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


def test_byre_clear_of_all_but_refuses_the_paddy_and_a_neighbour_s_yard() -> None:
    """Feature 146: two of the byre arm's refusal reasons - it stands on dry ground off the basins, and it
    clears every recorded appurtenance except its OWN homestead's."""
    s = Settlement(1000, 1000, seed=1)
    house = {"x": 300.0, "y": 300.0, "w": 50.0, "h": 30.0}
    s.M["houses"].append(house)
    s.field_polys.append([(500, 500), (800, 500), (800, 800), (500, 800)])
    assert s._byre_clear_of_all_but(650, 650, 40, 24, house) is False, "in the basin"
    s.M["threshing_yards"].append({"x": 200.0, "y": 200.0, "w": 40.0, "h": 30.0})
    assert s._byre_clear_of_all_but(200, 200, 40, 24, house) is False, "on a neighbour's yard"
    assert s._byre_clear_of_all_but(120, 600, 40, 24, house) is True


def test_byre_clear_of_all_but_refuses_another_households_placed_bundle() -> None:
    """The third refusal: a bundle already PLACED that is not the owner's own.

    `placed` holds the homestead envelopes the roller has seated, and the owner's own is skipped by
    position - the arm belongs inside it. Any OTHER bundle overlapping the arm refuses the seat. The pool
    stopped reaching this line when the 227/230 merge re-packed the clusters, so it is a unit test rather
    than a map's incidental cover (feature 174: bring it up BY TESTS).
    """
    s = Settlement(1000, 1000, seed=1)
    house = {"x": 300.0, "y": 300.0, "w": 50.0, "h": 30.0}
    s.M["houses"].append(house)
    s.placed.append((300.0, 300.0, 60.0, 40.0))  # the owner's own bundle, at the house - skipped
    assert s._byre_clear_of_all_but(340, 300, 40, 24, house) is True, "the owner's own bundle does not refuse its arm"
    s.placed.append((420.0, 300.0, 60.0, 40.0))  # a NEIGHBOR's bundle, overlapping the arm below
    assert s._byre_clear_of_all_but(400, 300, 40, 24, house) is False, "a neighbor's placed bundle refuses it"


def test_fringe_blocked_refuses_the_crop_and_the_open_water() -> None:
    """Feature 146: the wood's fringe grows on WASTE ground. Two of its refusal reasons - a fringe tree
    inside (or within its own radius of) a crop polygon, and one standing on a watercourse."""
    s = Settlement(1000, 1000, seed=1)
    s.field_polys.append([(400, 400), (700, 400), (700, 700), (400, 700)])
    assert s._fringe_blocked(550, 550, 8.0) is True, "in the basin"
    assert s._fringe_blocked(396, 550, 8.0) is True, "off it, but inside the tree's own radius"
    s.M["streams"] = [{"pts": [[100, 900], [900, 900]], "w": 8, "poly": [[100, 896], [900, 896], [900, 904], [100, 904]]}]
    assert s._fringe_blocked(500, 900, 8.0) is True, "standing in the brook"
    assert s._fringe_blocked(150, 150, 8.0) is False


def test_stand_fringe_skips_a_seat_a_crown_already_covers() -> None:
    """Feature 146: the wood's fringe skips a seat whose ground is spoken for OR that an existing canopy
    already covers - the no-double-ink rule, the same one the grove clumps follow."""
    poly = [(200.0, 200.0), (900.0, 200.0), (900.0, 900.0), (200.0, 900.0)]

    def fringe(preload: bool) -> list:  # a FRESH settlement each time - the scatter draws from the RNG
        s = Settlement(1200, 1200, seed=3)
        s.meta(name="W", scale="town", ftpx=1)
        krect = [(150.0, 150.0, 950.0, 400.0)] if preload else []  # a canopy keep-out over the north band
        return s._stand_fringe(poly, 18.0, 6.0, krect, [])

    bare = fringe(False)
    assert bare, "the fixture must offer seats, or the skip proves nothing"
    assert len(fringe(True)) < len(bare), "seats an existing canopy already covers are skipped"


def test_a_byre_is_refused_a_seat_on_the_paddy():
    """A byre stands on dry ground: the draft team is stalled beside the steading, not in the rice."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.field_polys.append([(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (100.0, 400.0)])
    h = {"x": 600, "y": 600, "w": 40, "h": 26}
    # 18 px OUT from the field edge: past `_in_blocked`'s own 14 px setback (which would otherwise
    # answer first and leave this rule untested) and inside the byre's half-diagonal of 18.
    assert not s._byre_clear_of_all_but(418, 250, 30, 20, h), "its corner would be over the bund"
    assert s._byre_clear_of_all_but(700, 700, 30, 20, h)


def test_a_fringe_tree_is_refused_ground_already_spoken_for():
    """The wood's margin grows on WASTE ground - never over a blocking footprint, the crop, or a way."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.block_polys.append([(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (100.0, 400.0)])
    assert s._fringe_blocked(250, 250, 6)
    assert not s._fringe_blocked(700, 700, 6)


# ---- feature 174: the avenue-fitting engine, which owns a sando's stride -------------------------
# `_avenue_pitch` and `_avenue_short_of_walls` are the two corrections the engine makes to a gen's
# authored torii line. Both were untested: the gen authors the LINE, the engine owns the STRIDE, and
# neither half of that division of labor had an assertion on it.


def test_courtyard_annex_span_and_a_house_with_neither_side_wall_free():
    """The courtyard form's two measured edges the re-seated pool no longer reaches: the span a byre may stand from
    its owner (the house's longest half-extent, past the byre's half-depth, plus the search budget), and the seat
    search declining when a neighbor abuts each side wall - the caller then falls back to the shared spiral."""
    from l7r.diagram.settlement.shrines_wells.byres import COURTYARD_REACH, courtyard_annex_span

    assert courtyard_annex_span(46.0, 28.0, 10.9) == 46.0 / 2 + 10.9 * 0.55 + COURTYARD_REACH
    s = _crop_settlement()
    owner = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0}
    s.M["houses"] = [
        owner,
        {"x": 300.0 - 40.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0},
        {"x": 300.0 + 40.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0},
    ]
    assert s._courtyard_byre_seat(owner, 15.5, 10.5) is None


@pytest.mark.parametrize(("rot", "yard_y", "toward"), [(0.0, 500.0, 1.0), (0.0, 100.0, -1.0), (180.0, 500.0, -1.0)])
def test_courtyard_byre_reaches_along_its_side_wall_toward_its_owners_work_yard(rot: float, yard_y: float, toward: float) -> None:
    """The courtyard arm frames the working court: offset along the side wall toward the owner's NEAREST threshing yard,
    that side derived in the house's own frame (a house turned half round reaches the other way in local y) - so the arm
    keeps framing the court when the yard moves, which pinning a compass side would not."""
    s = _crop_settlement()
    owner = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": rot, "wealth": 1.0}
    s.M["houses"] = [owner]
    s.M["threshing_yards"] = [{"x": 300.0, "y": yard_y, "w": 30.0, "h": 30.0}, {"x": 1800.0, "y": 1400.0 - yard_y, "w": 30.0, "h": 30.0}]
    seat = s._courtyard_byre_seat(owner, 15.5, 10.5)
    assert seat is not None
    lyc = toward * (28.0 / 2.0 - 15.5 / 2.0)  # reach toward the court: the wall's half-length past the byre's half-width
    th = math.radians(rot)
    lx = -(40.0 / 2.0 + 10.5 / 2.0 + 3.0)  # the first wall tried, a drip line off it
    assert seat[:2] == pytest.approx((300.0 + lx * math.cos(th) - lyc * math.sin(th), 300.0 + lx * math.sin(th) + lyc * math.cos(th)))


def test_a_shared_byre_widens_its_spread_tier_until_it_holds_a_borrower() -> None:
    """Settlement-review, Kashikawa 2026-08-18: after the first shared shed, the spread tier (candidates near the farthest
    from every shed) WIDENS until it holds an owner a neighbor can borrow from, and stops there. Here the farthest
    homestead has no neighbor, so the near-best tier holds no borrower; the half tier takes in a pair of neighbors a little
    over half as far, and the second shed goes to one of them rather than out of everyone's reach."""
    from l7r.diagram.settlement.shrines_wells.byres import _BORROW_REACH

    def house(x: float, y: float, wealth: float) -> dict:
        return {"x": x, "y": y, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0, "wealth": wealth}

    s = _crop_settlement()
    hs = [
        house(400.0, 400.0, 1.5),  # the first shed's owner...
        house(400.0 + _BORROW_REACH - 20.0, 400.0, 1.0),  # ...with a neighbor, so it has a borrower
        house(1400.0, 400.0, 1.1),  # a pair of neighbors about 0.58 of the farthest distance out
        house(1400.0, 400.0 + _BORROW_REACH - 20.0, 1.1),
        house(1800.0, 1400.0, 1.4),  # the farthest, and alone
    ]
    s.M["houses"] = hs
    for h in hs:
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    s.pin_knob("byre_form", "detached_commons")
    placed = s.draft_byres(fraction=0.4, gap=40)
    assert len(placed) == 2, "the target: two shared sheds for five households"
    owner = [min(range(len(hs)), key=lambda i: math.hypot(hs[i]["x"] - x, hs[i]["y"] - y)) for x, y in placed]
    assert owner[0] in (0, 1), f"the first shed stands by the wealthiest owner with a borrower (spiralled toward its neighbor): {owner}"
    assert owner[1] in (2, 3), f"the second goes to the pair in the widened tier, not the isolated farthest house: {owner}"


def test_the_outer_stable_stands_on_its_own_in_its_owners_yard_on_about_half_the_households() -> None:
    """269 B16 (research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.html): on a household form the beast lives with its household - the byre names its owner
    (`of`), stands raked with that house a ken off one of its walls, and about half the households keep one (`byre_share`,
    rolled in `BYRE_KEEPER_SHARE`; the caller's `fraction` sizes only the shared form)."""
    from l7r.diagram.settlement.shrines_wells.byres import BYRE_KEEPER_SHARE

    s, hs = _byre_village()
    s.pin_knob("byre_form", "yard_shed")
    placed = s.draft_byres(fraction=0.9, gap=40)
    share = s.M["meta"]["byre_share"]
    assert BYRE_KEEPER_SHARE[0] <= share <= BYRE_KEEPER_SHARE[1] and s.M["meta"]["byre_target"] == max(1, round(5 * share))
    assert len(placed) == s.M["meta"]["byre_target"] == len(s.M["byres"]), "the target met, not the caller's 0.9"
    owners = {(h["x"], h["y"]): h for h in hs}
    for b in s.M["byres"]:
        h = owners[tuple(b["of"])]
        assert b["rot"] in (h["rot"], h["rot"] + 90.0), "raked with its house, long side along the wall it faces"
        gap = max(abs(b["x"] - h["x"]) - h["w"] / 2, abs(b["y"] - h["y"]) - h["h"] / 2)
        assert gap > 6.0, f"a shed of its own, not the inner stable's arm ({gap:.1f} px off the wall)"


def test_a_courtyard_byre_with_no_free_wall_takes_the_outer_stable_and_a_yard_with_no_room_the_spiral(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B16: the inner stable's arm needs a free side wall; without one the household's beast gets the outer stable's
    shed, and where the yard has no room either the spiral seats it - still naming its owner, whatever the fallback."""
    s = _crop_settlement()
    owner = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 2.0}
    s.M["houses"] = [
        owner,
        {"x": 300.0 - 40.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0},
        {"x": 300.0 + 40.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0},
    ]
    s.pin_knob("byre_form", "courtyard")
    s.draft_byres()
    first = s.M["byres"][0]
    assert first["of"] == [300.0, 300.0] and first["y"] < 300.0 - 14.0, "behind its owner's back wall, not against a flank"

    s2 = _crop_settlement()  # a small house: the household spiral's short leash clears only a small footprint
    s2.M["houses"] = [{"x": 300.0, "y": 300.0, "w": 20.0, "h": 14.0, "kind": "plain", "rot": 0.0, "wealth": 1.0}]
    s2.placed.append((300.0, 300.0, 20.0, 14.0))
    s2.pin_knob("byre_form", "yard_shed")
    monkeypatch.setattr(Settlement, "_yard_shed_seat", lambda self, h, bw, bh: None)
    s2.draft_byres()
    assert s2.M["byres"] and all("of" in b and b["rot"] == 0 for b in s2.M["byres"]), "the spiral's shed, still its household's"


def test_the_outer_stable_finds_no_seat_on_the_paddy() -> None:
    """269 B16: every yard seat the outer stable tries is refused where the ground round the house is basin."""
    s = _crop_settlement()
    owner = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0}
    s.M["houses"] = [owner]
    s.field_polys.append([(200.0, 200.0), (400.0, 200.0), (400.0, 400.0), (200.0, 400.0)])
    assert s._yard_shed_seat(owner, 15.5, 10.5) is None


def test_a_households_byre_is_never_stabled_across_the_brook_from_its_house(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H01: a brook passing 10 px off the owner's back wall puts every back-wall seat on the far bank;
    the arm, the outer stable and the spiral each refuse it and seat the beast on the house's bank - by the one
    same-bank predicate, `crosses_a_stream`."""
    from l7r.diagram.settlement._geom.water_index import crosses_a_stream

    for form in ("courtyard", "yard_shed"):
        s = _crop_settlement()
        owner = {"x": 300.0, "y": 300.0, "w": 40.0, "h": 28.0, "kind": "plain", "rot": 0.0, "wealth": 1.0}
        s.M["houses"] = [owner]
        s.M["streams"] = [{"poly": [[100.0, 276.0], [500.0, 276.0]], "w": 3.0}]  # 10 px behind the north wall
        s.pin_knob("byre_form", form)
        s.draft_byres()
        assert s.M["byres"], form
        assert all(not crosses_a_stream((300.0, 300.0), (b["x"], b["y"]), s.M["streams"]) for b in s.M["byres"]), form
    s = _crop_settlement()
    s.M["houses"] = [{"x": 300.0, "y": 300.0, "w": 20.0, "h": 14.0, "kind": "plain", "rot": 0.0, "wealth": 1.0}]
    s.placed.append((300.0, 300.0, 20.0, 14.0))
    s.M["streams"] = [{"poly": [[100.0, 290.0], [500.0, 290.0]], "w": 1.0}]
    s.pin_knob("byre_form", "yard_shed")
    monkeypatch.setattr(Settlement, "_yard_shed_seat", lambda self, h, bw, bh: None)
    s.draft_byres()
    assert all(b["y"] > 290.0 for b in s.M["byres"]), "the spiral's seats north of the brook are refused"


def test_the_coverage_pass_seats_a_well_beside_a_dwelling_the_grid_left_dry() -> None:
    """`place_wells`'s COVERAGE pass (research 0196: no dwelling left without a well): a dwelling no grid well can serve -
    here the grid seats none, its only dwelling far outside the box - gets one dropped beside it."""
    s = Settlement(800, 800, seed=5)
    s.M["houses"] = [{"x": 600.0, "y": 600.0, "w": 20.0, "h": 14.0}]
    seats = s.place_wells((100, 100, 300, 300), spacing=80, near=150)
    assert len(seats) == 1, seats
    assert math.dist(seats[0], (600.0, 600.0)) <= 150 * 0.6 + 1e-6, "seated beside the dwelling, within its reach"


def test_a_torii_refuses_a_seat_in_a_ward_fence() -> None:
    """Feature 392: the arch never stands in a barrier (`torii_seat_on_wall`); the ward fence is recorded directly, the
    ward drawer having gone with the town and city code."""
    s = Settlement(800, 800, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, toscale=True)
    s.M["wards"] = [{"name": "samurai", "boundary": [[100, 400], [700, 400]]}]
    with pytest.raises(ValueError, match="would stand in"):
        s._torii(400, 400, 0)


def test_well_at_refuses_ground_already_taken_by_a_well() -> None:
    s = Settlement(800, 800, seed=1)
    s.meta(name="W", scale="hamlet", ftpx=1, toscale=True)
    assert s.well_at(400, 400), "the case: open ground takes a well"
    assert not s.well_at(400, 400), "...and the same spot again does not"

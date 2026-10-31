"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import copy
import math
import os
import random
import re
import tempfile

import pytest

from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import Settlement, _centroid
from tests._scope import full_or
from tests.settlement._builders import _village


def _comb(*args, **kw):
    """the comb builder memoized on its arguments, handing every caller its OWN deep copy.

    WHY THE COPY IS NOT OPTIONAL: `draw_comb_field` MUTATES the net it is given - measured 2026-08-30,
    it rewrites `bund_beans` and `threads` - so a shared net would let one test's draw change what the
    next test builds on. A cached net handed out by reference is the classic shared-fixture bug, and it
    would surface as an unrelated test failing depending on execution order.

    WHY IT IS WORTH IT: a build is 0.501 s and a deepcopy of the result is 0.0018 s - 272x cheaper. This
    file called the comb builder ten times across about five distinct argument sets (2026-08-30 profile, the
    heaviest test file in the suite).

    AND WHY THE CACHE IS ON DISK RATHER THAN IN A DICT. A module-level dict is per-PROCESS, and with
    `--dist worksteal` the tests sharing an argument set usually land on different xdist workers - so a
    dict shares almost nothing and adds a deepcopy to every call. Measured: the dict version made this
    file slightly SLOWER (4.48 s -> 4.76 s CPU). `rollcache.obtain` is keyed on the engine and backed by
    disk, so one build serves every worker. The same mistake, and the same correction, as the comb tests
    in `tests/waterfields/`.
    """
    from tests.waterfields._builders import lay_comb  # local, as every caller in this file had it

    key = f"test_fields-comb:{args!r}:{sorted(kw.items())!r}"
    return copy.deepcopy(rollcache.obtain(key, lambda: lay_comb(*args, **kw))[0])


def test_taxfree_plots_with_no_interior_cells():
    # no interior plots -> _taxfree_plots is a no-op (a field whose cells all fell outside the outline)
    s = _village()
    s._taxfree_plots([], 2)
    assert s.M["taxfree"] == []


def test_water_field_accepts_a_polygon_shape():
    # water_field is normally handed a bbox 4-tuple; a POLYGON shape (list of vertices) takes the other
    # branch - the outline is grown from the poly and the bbox derived from it. The field is still recorded
    # with its irrigation ditches.
    s = _village()
    s.water_field([(150, 150), (360, 150), (360, 360), (150, 360)], "", "f", (150, 150), (360, 360), amp=10, plot=34)
    assert any(f["name"] == "f" and f["kind"] == "paddy" for f in s.M["fields"])
    assert any(d["field"] == "f" for d in s.M["field_ditches"])


def test_rest_plots_takes_whole_scattered_basins_toward_the_far_end_of_the_fall():
    # 269 B01: only basins at least the median's size, never two within REST_APART_SIDES sides, the far end favored.
    from l7r.diagram.settlement.fields.paddy import REST_APART_SIDES, rest_plots

    grid = [([(x, y), (x + 40, y), (x + 40, y + 40), (x, y + 40)], float(y)) for x in range(0, 800, 40) for y in range(0, 800, 40)]
    scraps = [([(1000 + x, 0), (1004 + x, 0), (1004 + x, 4)], 10000.0) for x in range(0, 40, 8)]  # tiny, and farthest down
    cands = grid + scraps
    picks = rest_plots(cands, random.Random(3), 4)
    assert len(picks) == 4 and all(i < len(grid) for i in picks), "a scrap of fabric is never a resting holding"
    cents = [(sum(p[0] for p in cands[i][0]) / 4, sum(p[1] for p in cands[i][0]) / 4) for i in picks]
    assert all(math.dist(a, b) >= REST_APART_SIDES * 40 - 1e-6 for k, a in enumerate(cents) for b in cents[k + 1 :])
    far = sum(sum(cands[i][1] for i in rest_plots(cands, random.Random(seed), 3)) for seed in range(40))
    assert far / 120 > 400, "resting plots favor the far end of the water's run"
    assert rest_plots([], random.Random(1), 3) == []
    one = [([(0, 0), (40, 0), (40, 40), (0, 40)], 5.0)]
    assert rest_plots(one, random.Random(1), 3) == [0], "a flat fall still picks"
    crowd = [([(x, 0), (x + 40, 0), (x + 40, 40), (x, 40)], 0.0) for x in (0, 40)]
    assert len(rest_plots(crowd, random.Random(1), 2)) == 1, "neighbors sharing a bund never both rest"


# ---- water_field: the BBOX-shape branch + taxfree + label ----------------------------------
def test_water_field_from_a_bbox_marks_taxfree_and_labels():
    # handed a 4-number bbox (not a polygon), water_field grows the outline from the bbox; label +
    # taxfree marks vermilion plots and renders the name.
    s = _village()
    s.water_field((150, 150, 470, 470), "Paddy", "f", (150, 150), (470, 470), amp=10, taxfree=2, plot=34)
    assert any(fd["name"] == "f" and fd["kind"] == "paddy" for fd in s.M["fields"])
    assert s.M["taxfree"]
    s.place_labels()  # feature 157: captions are queued and drawn in the LABEL PHASE, so run it before reading them
    assert any(lab[5] == "Paddy" for lab in s.M["labels"])


# ---- fallow_field: a whole field left fallow ----------------------------------------------
def test_fallow_field_records_a_fallow_field():
    s = _village()
    s.fallow_field((150, 150, 350, 350), "ff")
    assert any(fd["name"] == "ff" and fd["kind"] == "fallow" for fd in s.M["fields"])


# ---- pond: the optional feeder stream_curve branch ----------------------------------------
def test_pond_with_a_feeder_stream_curve_draws_the_feeder():
    s = _village()
    s.pond(300, 300, 90, 60, stream_curve="M 100 100 L 300 300")
    assert s.M["pond"] == [300, 300, 90, 60]
    assert (300, 300, 90, 60) in s.ellipses  # pond also blocks houses via its ellipse


# ---- water_field: a lateral column too SHORT to carry a ditch is skipped -------------------
def test_water_field_skips_a_lateral_column_too_short_for_a_ditch():
    # a shallow field at a COARSE plot grain: some interior columns span less than ~2.1 plots
    # between the high main and the low drain, so no lateral ditch fits there and it is skipped.
    s = Settlement(900, 900, seed=3)
    s.meta(name="V", scale="village")
    s.water_field((150, 150, 400, 320), "P", "f", (150, 150), (400, 320), amp=10, plot=100)
    assert any(fd["name"] == "f" for fd in s.M["fields"])
    assert any(d["role"] == "main" for d in s.M["field_ditches"])  # the main/drain still run


def test_land_use_overlay_draws_and_records_each_kind():

    net = _comb(1300, 1700, (520, 220), full_or(2, 5), down_deg=90, field_fall=760, offtakes_a=(0.32, 0.7), offtakes_b=())
    for overlay in ("mulberry_fishpond", "lotus", "tea_fringe"):
        s = Settlement(1400, 1800, seed=3)
        s.meta(name="LU", scale="village", ftpx=1, down_deg=90)
        n = s.apply_land_use(net, overlay, __import__("random").Random(1))
        assert n > 0 and s.M["meta"]["land_use_overlay"] == overlay and s.out
        rec = s.M["land_use"][-1]
        assert rec["overlay"] == overlay and rec["count"] == n
        if overlay != "tea_fringe":  # tea is a margin fringe, not plot-based, so it records no plot list
            # feature 010: the plot-based overlays record WHICH plots converted, and every one of them
            # must be a low/wet plot - the topographic eligibility filter.
            wet = {tuple(_centroid(p["poly"])) for p in net["plots"] if p.get("low")}
            assert rec["eligible"] == "wet" and len(rec["plots"]) == n
            assert all(tuple(p) in wet for p in rec["plots"])
    # "none" records zero and draws nothing extra
    s0 = Settlement(1400, 1800, seed=3)
    s0.meta(name="LU0", scale="village", ftpx=1, down_deg=90)
    assert s0.apply_land_use(net, "none", __import__("random").Random(1)) == 0
    with pytest.raises(ValueError):
        s0.apply_land_use(net, "quinoa", __import__("random").Random(1))


def test_land_use_overlay_topography_paths():
    """Feature 010: the three placement paths - no eligible ground at all, the clustered dike-pond
    growth, and the named wholesale-conversion opt-out that ignores the topographic filter."""

    net = _comb(1300, 1700, (520, 220), full_or(2, 5), down_deg=90, field_fall=760, offtakes_a=(0.32, 0.7), offtakes_b=())
    dry = {**net, "plots": [{**p, "low": False} for p in net["plots"]]}  # a field with NO low/wet ground
    s = Settlement(1400, 1800, seed=3)
    s.meta(name="LU1", scale="village", ftpx=1, down_deg=90)
    assert s.apply_land_use(dry, "lotus", __import__("random").Random(1)) == 0  # draws nothing, honestly
    assert s.M["land_use"][-1]["plots"] == []
    # eligible="all" is the ARCHETYPE opt-out: it converts ordinary rice ground too
    s2 = Settlement(1400, 1800, seed=3)
    s2.meta(name="LU2", scale="village", ftpx=1, down_deg=90)
    n2 = s2.apply_land_use(dry, "mulberry_fishpond", __import__("random").Random(1), fraction=0.9, eligible="all")
    assert n2 > 0 and s2.M["land_use"][-1]["eligible"] == "all"
    # fourth pass (GM 2026-07-23): the wholesale case repaints its rice leftovers as textured paddy and
    # records them - every plot is either converted or a recorded leftover, none floats as a bare outline
    assert len(s2.M["land_use"][-1]["leftover_plots"]) == len(dry["plots"]) - n2
    # the partial-overlay path records no leftovers (its unconverted plots are ordinary comb paddies)
    s3 = Settlement(1400, 1800, seed=3)
    s3.meta(name="LU3", scale="village", ftpx=1, down_deg=90)
    s3.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1))
    assert s3.M["land_use"][-1]["leftover_plots"] == []
    # take >= len(eligible) short-circuits to "convert everything eligible"
    two = [{"poly": [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], "low": True}] * 2
    assert len(Settlement._pick_overlay_plots(two, 5, clustered=True, rng=__import__("random").Random(1))) == 2


def test_pick_overlay_plots_grows_a_patch_from_its_seeds():
    """Feature 010: the clustered dike-pond path. Conversion was 挖塘培基 - one household digging one
    low plot in one dry season - so the patch GROWS outward from a seed by nearest-neighbor, rather
    than sprinkling evenly. Assert the growth actually happened: the chosen plots are mutually nearer
    than an evenly-spread subset of the same size would be."""
    import random as _r

    row = [{"poly": [(float(i * 100), 0.0), (float(i * 100 + 90), 0.0), (float(i * 100 + 90), 90.0)], "low": True} for i in range(20)]
    got = Settlement._pick_overlay_plots(row, 6, clustered=True, rng=_r.Random(4))
    assert len(got) == 6
    xs = sorted(_centroid(p["poly"])[0] for p in got)
    assert xs[-1] - xs[0] <= 5 * 100 + 1  # contiguous run, not scattered over the full 2000px row
    # unclustered takes the same eligible set but does NOT force contiguity
    assert len(Settlement._pick_overlay_plots(row, 6, clustered=False, rng=_r.Random(4))) == 6


def test_pond_fill_relocates_to_the_late_block_when_a_late_channel_joins():
    """The Tango in-wall tank (GM 2026-07-23): a comb head-race joins the pond from the LATE
    block, which draws after the whole shared water block - so an early fill can never cover the
    mouth's inside-the-rim overshoot and the cap rides ON TOP of the open water. The fill+sheen
    relocate to the late block (topmost late bed); the rim EDGE stays early so the mouth's bed
    still covers it. Manifest records the order for pond_fill_covers_channel_mouths."""
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "t")
        s = Settlement(1000, 1000, seed=1)
        s.meta(name="V", scale="village")
        s.pond(500, 250, 100, 70)
        s.field_channel([(500, 260), (500, 600)], "#6C9CBE", 5.0, 5.0, late=True)  # sluice inside the pond -> snapped to the rim
        s.finish(base, render=False)
        with open(base + ".svg") as _f:
            svg = _f.read()
    dc = s.M["drawn_channels"][0]
    assert dc["late"] and s.M["pond_layer"]["late"] is True  # the fill relocated to the late block
    assert s.M["pond_layer"]["bedz"] > dc["bedz"]  # fill recorded ABOVE the joining bed (same block)
    fill = svg.index('<ellipse cx="500" cy="250" rx="100" ry="70" fill="#9CB4C8"/>')
    assert fill > svg.index('stroke="#6C9CBE"')  # fill drawn AFTER the late bed (covers the cap)
    assert svg.index('stroke="#5C7488"') < svg.index('stroke="#6C9CBE"')  # rim edge stays early, below the bed


def test_comb_base_fill_noops_on_an_empty_net():
    """comb_base_fill draws and records nothing when the net has no plots (a degenerate field) -
    the guard that keeps a plotless comb from emitting a zero-area floor polygon."""
    s = Settlement(600, 600, seed=1)
    s.meta(name="Cb", scale="village", ftpx=2)
    s.comb_base_fill({"plots": [], "envelope": [(0, 0), (10, 0), (10, 10)]}, "empty")
    assert "empty" not in s.M.get("comb_floors", {})


def test_a_fry_village_takes_the_smallest_ponds_up_to_its_share_and_no_pond_is_sluiced():
    """Feature 280 M57/M60 (research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html, 200): a fry village's fry ponds are its smallest, their area within
    seven tenths of the block's ponds; an ordinary hamlet has none; and no pond is cut by a sluice of its own."""
    from l7r.diagram.settlement.fields.landuse import FRY_VILLAGE_SHARE, fry_pond_ids

    def sq(x: float, side: float) -> dict:
        return {"poly": [(x, 100.0), (x + side, 100.0), (x + side, 100.0 + side), (x, 100.0 + side)], "low": True}

    plots = [sq(100.0, 40.0), sq(300.0, 50.0), sq(500.0, 60.0), sq(700.0, 100.0)]
    area = lambda poly: float(abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))) / 2  # noqa: E731
    got = fry_pond_ids(plots, area, FRY_VILLAGE_SHARE)
    assert got == {id(plots[0]), id(plots[1]), id(plots[2])}, "the three small ponds are 7,700 of 17,700 sq ft; the big one would pass 0.7"
    assert fry_pond_ids(plots, area, 0.0) == set()
    for form, fry in (("none", 0), ("fry_village", 3)):
        s = Settlement(2000, 2000, seed=1)
        s.meta(field_archetype="mulberry_dike_fishpond")
        net = {"plots": [dict(p) for p in plots], "channels": [{"pts": [(1900, 100), (1950, 150)]}]}
        s.apply_land_use(net, "mulberry_fishpond", random.Random(1), fraction=1.0, eligible="all", fry_form=form)
        assert s.M["meta"]["fry_form"] == form and sum(d["kind"] == "fry" for d in s.M["dikeponds"]) == fry
        assert "dikepond_sluices" not in s.M


def test_apply_land_use_reanchor_leaves_a_placeholder_slot():
    # GM 2026-07-24 (the bald pond): the flush splice REPLACES the element at _late_water_idx
    # (self.out[idx:idx+1] = block), so every anchor assignment must be followed by an empty-string
    # placeholder. The overlay re-anchor lacked one, so the splice ate the next-appended element -
    # which, after the crown-deferral change, was a pond's entire crown group.
    s = Settlement(2000, 2000, seed=1)
    s.meta(field_archetype="mulberry_dike_fishpond")
    s._late_water_idx = len(s.out)
    s.out.append("")  # a live late-water anchor, as a comb-field channel draw would leave it
    plots = [{"poly": [(100.0 + 220 * i, 100.0), (280.0 + 220 * i, 100.0), (280.0 + 220 * i, 260.0), (100.0 + 220 * i, 260.0)], "low": True} for i in range(2)]
    s.apply_land_use({"plots": plots, "channels": []}, "mulberry_fishpond", random.Random(1), fraction=1.0, eligible="all")
    assert s._late_water_idx is not None and s.out[s._late_water_idx] == ""  # the slot the splice consumes is a placeholder, never real content


def test_flooded_leftover_paddy_gets_rounded_waterline():
    # GM 2026-07-23: a FLOODED leftover's waterline draws rounded + slightly irregular (bund corners silt
    # round, the toe wanders) via _rounded_pond - with NO edge stroke, so it never reads as a dug pond
    # (pond water paths carry the #6C9CBE stroke; the flooded paddy's body is strokeless).
    s = Settlement(2000, 2000, seed=2)
    s.meta(field_archetype="mulberry_dike_fishpond")
    plots = [{"poly": [(100.0 + 220 * i, 100.0), (280.0 + 220 * i, 100.0), (280.0 + 220 * i, 260.0), (100.0 + 220 * i, 260.0)], "low": True, "fill": "#93B7AC"} for i in range(4)]
    s.apply_land_use({"plots": plots, "channels": []}, "mulberry_fishpond", random.Random(3), fraction=0.5, eligible="all")
    body = "".join(s.out)
    assert re.search(r'<path d="[^"]*Q[^"]*" fill="#93B7AC"/>', body)  # a strokeless, corner-filleted water body


def test_dikepond_digs_back_from_a_penetrating_lateral():
    # GM 2026-07-23: the canal at the toe BOUNDS the bank - a lateral riding inside the parcel line makes
    # the whole pond unit shrink about its centroid until the bank clears the canal, and the SHRUNK outline
    # is what dikeponds records (the drawn truth, which mulberry_banks_clear_of_channels then reads).
    s = Settlement(2000, 2000, seed=1)
    s.meta(field_archetype="mulberry_dike_fishpond")
    plot = {"poly": [(100.0, 100.0), (300.0, 100.0), (300.0, 300.0), (100.0, 300.0)], "low": True}
    net = {"plots": [plot], "channels": [{"pts": [(103.0, 50.0), (103.0, 350.0)]}]}  # rides 3 px inside the west edge
    s.apply_land_use(net, "mulberry_fishpond", random.Random(1), fraction=1.0, eligible="all")
    rec = s.M["dikeponds"][0]["parcel"]
    assert min(x for x, _ in rec) >= 103.0 + 1.0  # dug back clear of the lateral (>= 1 px past its line)


def test_mulberry_rows_crowns_avoid_channels():
    # GM 2026-07-23: the crowns are coppiced BUSHES - any crown whose circle would reach a channel
    # centerline (r + 3 px clearance) is dropped, so bushes never stand in the canal at the dike toe.
    poly = [(0.0, 0.0), (160.0, 0.0), (160.0, 320.0), (0.0, 320.0)]

    def crowns(channels):
        s = Settlement(600, 600, seed=1)
        s._mulberry_rows(poly, "M -10 -10 L 170 -10 L 170 330 L -10 330 Z", 80.0, 160.0, random.Random(7), channels)
        return s.out[-1].count("<circle")

    unblocked = crowns(None)
    blocked = crowns([((80.0, -20.0), (80.0, 340.0))])  # a canal crossing the top + bottom bank rows
    assert 0 < blocked < unblocked


def test_mulberry_rows_skips_a_parcel_too_small_to_plant():
    # fourth pass: a parcel whose apothem cannot hold the water inset (`DIKEPOND_WATER_INSET`) has no bank to plant - the
    # helper draws nothing rather than wrapping crown rows around a degenerate loop.
    s = Settlement(400, 400, seed=1)
    before = len(s.out)
    s._mulberry_rows([(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)], "M 0 0 Z", 10.0, 10.0, random.Random(1))
    assert len(s.out) == before


# --- feature 112: the composed FieldsMixin surface -----------------------------------------------
# settlement/fields.py became a package of four sub-mixins composed in fields/__init__.py. The
# guard below is the whole safety property of that split: core.py imports ONE name and the class
# must keep contributing exactly what it contributed before. Two failure modes it exists for -
# a member dropped in the move (the composed class silently loses a method, and only a generator
# that happens to call it notices), and a member defined by TWO sub-mixins (MRO picks one and
# orphans the other, with no import error, no type error, and no test failure anywhere else).
# Proven to fire against both before it was trusted - see specs/112-fields-package/tasks.md T005.

_FIELDS_SURFACE = frozenset(
    {
        # public entry points, called from pool gens, hamletgen, other engine modules and checks
        "apply_land_use",
        "comb_base_fill",
        "fallow_field",
        "pond",
        "water_field",
        # private helpers, reached through self. (several also called on an instance from tests
        # and from settlement/land/nearring.py, which is why they are part of the surface)
        "_draw_furrows",
        # `_fallow_patch` (the blighted sub-region with red crosses) was RETIRED by 269 B01: a resting paddy plot is a whole
        # basin (`rest_basin`), never a patch within one - a deliberate removal, not a member lost in a move.
        "_mulberry_rows",
        "_paddy_surface",
        "_pick_overlay_plots",
        "_rows",
        "_taxfree_plots",
    }
)


def _fields_submixins():
    from l7r.diagram.settlement.fields.drawing import FieldDrawingMixin
    from l7r.diagram.settlement.fields.landuse import LandUseMixin
    from l7r.diagram.settlement.fields.paddy import PaddyMixin

    return [PaddyMixin, FieldDrawingMixin, LandUseMixin]


def _own_callables(cls):
    return {k for k, v in vars(cls).items() if callable(v) or isinstance(v, staticmethod)}


def test_no_pre_split_fields_member_was_lost_in_the_move():
    # SUBSET, not equality, and the reason is worth stating. Stage 2 of feature 112 decomposed the
    # three oversized methods into named private helpers, so the composed class legitimately holds
    # `bund_junctions`, `draw_comb_field` and the in-field features' placers (`_paddy_features`, `_plot_pond`, `_plot_rock`,
    # `_plot_grave_island`, `_plot_center_span`, `_rounded_pond`) left the set with the field's old placement (feature 444 T16: the field's placement
    # is Rust's, its five drawing functions moved to `drawing.py`) - not lost in a move, deleted with the code they were.
    # MORE than the pre-split 24, and will hold more again the next time a method is split. What
    # must never happen is a pre-split member going MISSING: an addition is visible in review,
    # while a subtraction is silent until whichever generator calls it happens to run. The
    # assertion therefore guards the direction that hides. The red proof still holds - deleting a
    # member names it in `missing` (specs/112-fields-package/tasks.md T005).
    composed = set().union(*(_own_callables(c) for c in _fields_submixins()))
    assert composed >= _FIELDS_SURFACE, f"missing={sorted(_FIELDS_SURFACE - composed)}"


def test_no_two_fields_submixins_define_the_same_name():
    subs = _fields_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _own_callables(a) & _own_callables(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"


def test_every_fields_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely FieldsMixin
    unreachable = sorted(n for n in _FIELDS_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"


def test_feature_012_archetype_constants_survived_the_split():
    # the three class-level tuples gating the in-field pond / rock / grave island. They are class
    # ATTRIBUTES, not methods, so the surface test above cannot see them - and a transformer that
    # slices a class body by its function definitions is exactly what would drop them.
    for name in ("_PADDY_POND_KINDS", "_PADDY_GRAVE_KINDS"):
        assert isinstance(getattr(Settlement, name), tuple), name
    assert "valley_paddy" in Settlement._PADDY_POND_KINDS


def test_hem_on_water_sees_a_stream_and_a_pond_separately():
    """the comb builder lays the fan from pure geometry and `draw_comb_field` used to render it blind - it
    was the ONLY placer that consulted nothing, so a dry-hem plot could be drawn straight across a
    stream authored earlier (Ubame's). The two arms are different geometry: a stroked watercourse with
    a half-width, and the pond's ellipse."""
    from l7r.diagram.hamletgen.water.brook_rules import hem_on_water

    plot = [(100.0, 100.0), (140.0, 100.0), (140.0, 140.0), (100.0, 140.0)]
    assert hem_on_water(plot, [([(0.0, 120.0), (500.0, 120.0)], 4.5)], None), "the stream runs under it"
    assert hem_on_water(plot, [], (120.0, 120.0, 60.0, 40.0)), "and the pond stands under it"
    assert not hem_on_water(plot, [([(0.0, 900.0), (500.0, 900.0)], 4.5)], (800.0, 800.0, 20.0, 20.0))


def test_comb_base_fill_can_floor_the_whole_envelope():
    """Cities crop tight and carry no surrounding scrub, so their field floor must cover the edge
    junctions too; a village clips the fill to the plots' union bbox instead, which hides the nucleated
    map's harmless phantom tail. Gated by `paddy_fan_has_floor`."""
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    net = {
        "plots": [{"poly": [(100.0, 100.0), (300.0, 100.0), (300.0, 300.0), (100.0, 300.0)]}],
        "envelope": [(90.0, 90.0), (310.0, 90.0), (310.0, 310.0), (90.0, 310.0)],
    }
    s.comb_base_fill(net, "p", full_envelope=True)
    assert any("310.0,90.0" in frag for frag in s.out), "the envelope itself is the floor"


# ---- feature 174: the overlay plot picker, tested DIRECTLY -----------------------------------------
# GM 2026-08-31: "the make done tests are doing the straightforward branch coverage thing while our
# full tests are doing the more traditional end to end testing thing... if that would require
# 'duplication' to reach one hundred percent code coverage, then I think that is okay."
#
# The test above builds a real comb and applies each overlay end to end - the second kind. These are
# the first kind: `_pick_overlay_plots` takes a plain list and a seeded Random, so its two spreading
# doctrines can be asserted as the RESEARCH says they behave, without a map.


def _plots(n: int, spacing: float = 100.0):
    """n plots in a row, far enough apart that "nearest neighbor" is unambiguous."""
    return [{"poly": [(i * spacing, 0.0), (i * spacing + 10.0, 0.0), (i * spacing + 10.0, 10.0), (i * spacing, 10.0)], "i": i} for i in range(n)]


def test_a_dike_pond_conversion_spreads_as_PATCHES_from_where_someone_started() -> None:
    """Research D2, and the reason this is clustered at all: the 桑基魚塘 conversion was 挖塘培基 -
    dig one low plot into a pond, pile the spoil into a dike around it - a single-plot job one
    household did in one dry season. It spread as a patchwork radiating from where someone started,
    not as an even sprinkle. (Shunde grew 40,084 -> 58,094 mu over 61 years, plot by plot.)

    Asserted as CONTIGUITY, which is the observable consequence: the picked plots form far fewer
    runs than an even scatter of the same count would.
    """
    import random as _random

    eligible = _plots(30)
    picked = Settlement._pick_overlay_plots(eligible, 9, clustered=True, rng=_random.Random(4))
    idx = sorted(p["i"] for p in picked)
    runs = 1 + sum(1 for a, b in zip(idx, idx[1:], strict=False) if b != a + 1)
    assert len(picked) == 9
    assert runs <= 3, f"patches, not a sprinkle: {runs} runs across {idx}"


def test_the_lotus_overlay_draws_EVENLY_because_the_wet_bottom_is_already_contiguous() -> None:
    """ "the wet bottom is already contiguous by nature, so an even draw from the eligible set lands
    contiguously without extra help" - so the unclustered branch is a plain sample, and asserting it
    is what stops the clustered rule being applied to everything."""
    import random as _random

    eligible = _plots(30)
    picked = Settlement._pick_overlay_plots(eligible, 9, clustered=False, rng=_random.Random(4))
    assert len(picked) == 9
    assert len({p["i"] for p in picked}) == 9, "nine distinct plots, no repeats"


def test_asking_for_every_eligible_plot_returns_them_ALL_without_sampling() -> None:
    """The short-circuit: `take >= len(eligible)`. A sample of everything is still everything, but
    going through the patch-growing loop for it would be a needless walk - and the loop's own
    termination depends on there being an unpicked plot left."""
    import random as _random

    eligible = _plots(5)
    assert Settlement._pick_overlay_plots(eligible, 5, clustered=True, rng=_random.Random(1)) == eligible
    assert Settlement._pick_overlay_plots(eligible, 99, clustered=False, rng=_random.Random(1)) == eligible


def test_the_patch_seeds_are_A_HANDFUL_not_everyone_at_once() -> None:
    """`n_seeds = max(1, round(take / 9))` - "a handful of households started digging, not everyone
    at once". A small take must still get at least one seed, which is the `max(1, ...)`."""
    import random as _random

    picked = Settlement._pick_overlay_plots(_plots(20), 2, clustered=True, rng=_random.Random(2))
    assert len(picked) == 2, "even a two-plot conversion has a seed to grow from"


def test_a_TEA_dike_is_drawn_as_clipped_hedgerows_not_as_crowns(monkeypatch: pytest.MonkeyPatch) -> None:
    """269 B34: tea is the third premodern dike planting (research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html). A clipped tea bush reads
    as a hedge, so its rows are runs of dark stroke, broken between bushes - a different SHAPE from the
    mulberry's scatter of round crowns, which is what lets a reader tell the two at fit zoom.
    """
    # the toy comb's plots are small; the crop's glyph is the subject, not feature 280's deeper water inset (M58)
    monkeypatch.setattr(__import__("l7r.diagram.settlement.fields.landuse", fromlist=["x"]), "DIKEPOND_WATER_INSET", 11.0)
    net = _comb(1300, 1700, (520, 220), full_or(2, 5), down_deg=90, field_fall=760, offtakes_a=(0.32, 0.7), offtakes_b=())
    s = Settlement(1400, 1800, seed=3)
    s.meta(name="LUT", scale="village", ftpx=1, down_deg=90)
    n = s.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), dike_crop="tea")
    ink = "".join(s.out)
    assert n > 0, "the conversion still happens"
    assert s.M["meta"]["dike_crop"] == "tea"
    assert "#3F5A2A" in ink or "#4A6630" in ink, "the hedgerow runs are drawn"
    assert "tea dike" in "".join(str(c) for c in s.out_cls), "the bank and its bushes light as the tea dike"


def test_every_attested_DIKE_CROP_draws_a_form_that_tells_it_from_the_others(monkeypatch: pytest.MonkeyPatch) -> None:
    """`DIKE_CROPS` holds three distinct premodern plantings (269 B34; research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html) and each is a
    different SHAPE at fit zoom, which is the whole reason they are separate forms rather than colors:

      - mulberry: a scatter of coppiced crowns in two rows
      - tea: two clipped hedgerows, dark runs broken between bushes
      - fruit: an orchard's single crowns at a regular pitch

    So the test is that no two draw the same ink - which is the property a reader depends on, and the one a
    fourth crop added as a color would break. The modern cane, banana and vegetable dikes are refused.
    """
    # the toy comb's plots are small; the crop's glyph is the subject, not feature 280's deeper water inset (M58)
    monkeypatch.setattr(__import__("l7r.diagram.settlement.fields.landuse", fromlist=["x"]), "DIKEPOND_WATER_INSET", 11.0)
    net = _comb(1300, 1700, (520, 220), full_or(2, 5), down_deg=90, field_fall=760, offtakes_a=(0.32, 0.7), offtakes_b=())
    ink = {}
    for crop in ("mulberry", "tea", "fruit"):
        s = Settlement(1400, 1800, seed=3)
        s.meta(name=f"LU{crop}", scale="village", ftpx=1, down_deg=90)
        s.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), dike_crop=crop)
        ink[crop] = "".join(s.out)
    assert len(set(ink.values())) == 3, f"three crops, three distinguishable plantings: {[k for k in ink]}"
    for modern in ("sugarcane", "banana", "vegetable"):
        with pytest.raises(ValueError, match="dike_crop"):
            Settlement(1400, 1800, seed=3).apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), dike_crop=modern)


def test_an_unknown_dike_crop_or_leftover_form_is_REFUSED_at_the_call() -> None:
    """The two validators beside the knobs. A misspelling must fail loudly at the call rather than
    silently draw the default - the same no-silent-default rule the spec validators carry, applied
    where the value arrives as an argument instead of on a spec.
    """
    net = _comb(1300, 1700, (520, 220), full_or(2, 5), down_deg=90, field_fall=760, offtakes_a=(0.32, 0.7), offtakes_b=())
    s = Settlement(1400, 1800, seed=3)
    s.meta(name="LUX", scale="village", ftpx=1, down_deg=90)
    with pytest.raises(ValueError, match="dike_crop"):
        s.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), dike_crop="kiwi")
    with pytest.raises(ValueError, match="leftover"):
        s.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), leftover="fallow")
    with pytest.raises(ValueError, match="leftover"):  # retired with the modern vegetable dike (269 E9)
        s.apply_land_use(net, "mulberry_fishpond", __import__("random").Random(1), leftover="vegetables")


def test_a_dike_pond_bank_is_a_ring_around_its_water():
    """Feature 228 (GM 2026-09-12): hovering the mulberry dike lit the fish pond inside it, because the bank
    was a filled disk under the pond and raster mode washes the lit class over the image. The bank is now
    the ring between its outer edge and the water's - the perimeter dike's own band form - so the pond
    shows through the hole: one path, the bank outline then the water outline, under the even-odd rule.
    The pond's own path is unchanged."""
    s = Settlement(2000, 2000, seed=1)
    s.meta(field_archetype="mulberry_dike_fishpond")
    plots = [{"poly": [(100.0, 100.0), (280.0, 100.0), (280.0, 260.0), (100.0, 260.0)], "low": True}]
    s.apply_land_use({"plots": plots, "channels": []}, "mulberry_fishpond", random.Random(1), fraction=1.0, eligible="all")
    banks = [t for t, c in zip(s.out, s.out_cls, strict=True) if c == "mulberry dike" and 'fill="#C2A772"' in t]
    ponds = [t for t, c in zip(s.out, s.out_cls, strict=True) if c == "fish pond"]
    assert len(banks) == 1 and len(ponds) == 1, (banks, ponds)
    bank_d = re.search(r' d="([^"]*)"', banks[0]).group(1)
    pond_d = re.search(r' d="([^"]*)"', ponds[0]).group(1)
    assert 'fill-rule="evenodd"' in banks[0] and 'fill-rule' not in ponds[0]
    assert pond_d.count("Z") == 1 and pond_d.startswith("M ") and pond_d.endswith("Z")
    assert bank_d.count("Z") == 2 and bank_d.endswith(" " + pond_d), bank_d  # the hole IS the pond's outline
    outer = bank_d[: -len(pond_d) - 1]
    assert outer.startswith("M ") and outer.endswith("Z") and outer != pond_d
    bank, water = s.M["dikeponds"][0]["bank"], s.M["dikeponds"][0]["water"]  # the records are untouched (FR-003)
    assert min(x for x, _y in bank) < min(x for x, _y in water) and max(x for x, _y in bank) > max(x for x, _y in water)


def test_the_mulberry_rows_grow_with_the_bank_so_the_spacing_holds() -> None:
    """Feature 280 (settlement-review of Kuwabata): a 23 ft bank kept two rows and the bushes thinned by half."""
    from l7r.diagram.settlement.fields.landuse import mulberry_row_ts

    assert len(mulberry_row_ts(11.0)) == 2 and len(mulberry_row_ts(23.0)) == 4 and len(mulberry_row_ts(3.0)) == 2
    assert all(0.0 < t < 1.0 for t in mulberry_row_ts(23.0))


def test_the_dikepond_inset_leaves_the_rolled_split_water() -> None:
    """Feature 385 T10 (D74): the inset is derived from the rolled split on the map's median parcel, so that parcel is the split's
    share water - six, four or seven parts in ten (0018); with no parcel, the water-heavy split's 23 ft stands."""
    from l7r.diagram.settlement._knobs import KNOBS
    from l7r.diagram.settlement.fields.landuse import DIKEPOND_WATER_INSET, dikepond_inset

    assert KNOBS["dikepond_split"].value_space == [0.6, 0.4, 0.7, 0.5, 0.3]
    rect = [(0.0, 0.0), (120.0, 0.0), (120.0, 80.0), (0.0, 80.0)]
    small, big = [(0.0, 0.0), (60.0, 0.0), (60.0, 40.0), (0.0, 40.0)], [(0.0, 0.0), (200.0, 0.0), (200.0, 150.0), (0.0, 150.0)]
    for share in (0.6, 0.4, 0.7, 0.5, 0.3):
        d = dikepond_inset([small, rect, big], share)
        apo = (60 + 40 + 60 + 40) / 4  # the rectangle's mean centroid-to-edge-midpoint distance
        assert (1 - d / apo) ** 2 == pytest.approx(share), "the median parcel, scaled as `_rounded_pond` scales it, is the share water"
    assert dikepond_inset([rect], 0.4) > dikepond_inset([rect], 0.6) > dikepond_inset([rect], 0.7), "drier splits, wider banks"
    assert dikepond_inset([], 0.4) == DIKEPOND_WATER_INSET

"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import copy
import os
import tempfile
from pathlib import Path

import pytest

from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import Settlement
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


def test_comb_base_fill_finds_the_plots_box_itself_when_the_net_carries_none():
    """A net without the Rust field's `plots_box` (444 T16) is boxed from its plots' corners, and its floor recorded."""
    s = Settlement(600, 600, seed=1)
    s.meta(name="Cb", scale="village", ftpx=2)
    net = {"plots": [{"poly": [(10, 10), (50, 10), (50, 40), (10, 40)]}], "envelope": [(0, 0), (100, 0), (100, 100), (0, 100)]}
    s.comb_base_fill(net, "boxed")
    assert s.M["comb_floors"]["boxed"] == [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]


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
        "comb_base_fill",
        "fallow_field",
        "pond",
        "water_field",
        # private helpers, reached through self. (several also called on an instance from tests
        # and from settlement/land/nearring.py, which is why they are part of the surface)
        "_draw_furrows",
        # `_fallow_patch` (the blighted sub-region with red crosses) was RETIRED by 269 B01: a resting paddy plot is a whole
        # basin (`rest_basin`), never a patch within one - a deliberate removal, not a member lost in a move.
        "_paddy_surface",
        "_rows",
        "_taxfree_plots",
    }
)


def _fields_submixins():
    from l7r.diagram.settlement.fields.drawing import FieldDrawingMixin
    from l7r.diagram.settlement.fields.paddy import PaddyMixin

    return [PaddyMixin, FieldDrawingMixin]


def _own_callables(cls):
    return {k for k, v in vars(cls).items() if callable(v) or isinstance(v, staticmethod)}


def test_no_pre_split_fields_member_was_lost_in_the_move():
    # SUBSET, not equality, and the reason is worth stating. Stage 2 of feature 112 decomposed the
    # three oversized methods into named private helpers, so the composed class legitimately holds
    # `bund_junctions`, `draw_comb_field` and the in-field features' placers (`_paddy_features`, `_plot_pond`, `_plot_rock`,
    # `_plot_grave_island`, `_plot_center_span`, `_rounded_pond`) and the overlay's and the rest's (`apply_land_use` and its steps,
    # `resting_plots`) left the set with the field's old placement (feature 444 T16: the field's placement
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


def test_the_dikepond_ink_draws_its_leftover_rice_mottled_and_its_tea_hedges(tmp_path) -> None:  # noqa: ANN001
    """`ink.dikeponds` (feature 444 T16): a rice parcel the conversion left keeps the GM's 2026-07-23 repaint - its shoots on a
    jittered grid - and a tea crop's hedges are drawn as clipped strips."""
    from l7r.diagram.settlement.fields import ink

    s = Settlement(400, 400, seed=1)
    s.meta(name="Dk", scale="hamlet", ftpx=2)
    rice = [(10.0, 10.0), (60.0, 10.0), (60.0, 50.0), (10.0, 50.0)]
    ink.dikeponds(s, [("rice", rice, None, None)], ("tea", [], [[(100.0, 100.0), (180.0, 100.0)]]), 1.2)
    base = str(tmp_path / "dk")
    s.finish(base, render=False)
    svg = Path(base + ".svg").read_text(encoding="utf-8")
    assert svg.count('r="1.0" fill="#6F9061"') > 20, "the leftover's shoots, on the jittered grid"
    assert "stroke-linecap=\"butt\"" in svg and "polyline" in svg, "the tea hedge"
    again = Settlement(400, 400, seed=1)
    again.meta(name="Dk", scale="hamlet", ftpx=2)
    ink.dikeponds(again, [("rice", rice, None, None)], ("tea", [], []), 1.2)
    again.finish(str(tmp_path / "dk2"), render=False)
    shoots = [ln for ln in svg.split("<") if 'fill="#6F9061"' in ln]
    assert shoots == [ln for ln in Path(str(tmp_path / "dk2") + ".svg").read_text(encoding="utf-8").split("<") if 'fill="#6F9061"' in ln], "seeded from the parcel"

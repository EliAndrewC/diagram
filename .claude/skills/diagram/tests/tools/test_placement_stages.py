"""The stage-by-stage walk-through page (`tools/placement_stages.py`).

Feature 174, under the GM's 2026-09-02 ruling; the module had never been measured and its docstring
claimed exemption. The page is COMMITTED and is how the GM reads the build order, so the properties
worth pinning are the ones that were learned by getting them wrong:

- a stage that lays no ink gets a CARD of what it decided, not a blank cream plate (GM 2026-08-23:
  *"the water skeleton, which is the first picture, appears to be blank"*);
- the baseline for "what did this stage decide" is taken BEFORE stage 1, because the constructor has
  already written the canvas size and stage 1 was claiming credit for it;
- every plate this run did not write is PRUNED - a reorder once left seven orphans in the committed
  directory, one of them a picture of the very build order the feature had removed.

The stage list is stubbed: the point is the page's logic, and rolling eighteen real stages to test
an HTML writer would cost minutes per run.

ALSO, from feature 176 (landed on main while this feature was in flight, and merged here rather than
either side being dropped): the page was written from a notes roster, and a stage added to `STAGES` without a
note rendered "(no note yet)" with nothing red - feature 227 made the docstrings the source and the gate the check. The GM, 2026-09-02: *"I think the hamlet placement
order HTML file is outdated. For example, it does not mention anything about adding labels being its
own final step."* It did not, because `stage_labels` had no entry - so the roster of notes is held to
the roster of stages in BOTH directions, below.

`tooling`: it renders and writes files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.hamletgen.driver import STAGES
from l7r.diagram.tools import placement_stages as ps

pytestmark = [pytest.mark.tooling, pytest.mark.renders]  # the plates ARE renders: the tool writes a PNG per stage on purpose (feature 213 FR-006)

_SPEC = HamletSpec(name="Probe", seed=4, households=10, down_deg=90, water_sink="pond")


def test_ink_counts_records_across_all_four_layers_not_pixels() -> None:
    """ "did that stage DRAW anything" - deliberately a record count, because a stage may legitimately
    emit ink invisible at plate scale and that is not the case being detected."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    base = ps._ink(s)
    s.out.append("<rect/>")
    s.toplabels.append("<text/>")
    assert ps._ink(s) == base + 2, "every layer counts, not just the main one"
    s.lane([(10.0, 10.0), (90.0, 10.0)], width=5)
    assert ps._ink(s) > base + 2, "...and a deferred way counts as ink the moment it is laid (the web stage draws nothing else)"


def test_decisions_reads_the_maps_metadata_as_it_stands() -> None:
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    d = ps._decisions(s)
    assert d and d is not s.M["meta"], "a copy - the caller compares it against a later snapshot"


def _stub_stages(monkeypatch: pytest.MonkeyPatch, *stages: Any) -> None:
    monkeypatch.setattr(ps, "STAGES", list(stages))


def test_a_stage_that_lays_NO_INK_gets_a_card_of_what_it_decided_rather_than_a_blank_plate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The GM read a cream square as a broken render, and they were right to. A metadata-only stage
    now shows its decisions - generically, so any future one gets the same treatment and a stage that
    STOPS drawing announces itself here instead of turning quietly blank."""

    def stage_decides_only(s: Any, _plan: Any) -> None:
        s.M["meta"]["water_flow"] = "north-east"

    _stub_stages(monkeypatch, stage_decides_only)
    page = ps.build_page(str(tmp_path), 300, _SPEC)
    html = Path(page).read_text()
    assert list(tmp_path.glob("*.png")) == [], "no plate was written"
    assert "water_flow" in html and "north-east" in html, "the card shows what it decided"
    assert "no ink" in capsys.readouterr().out


def test_the_decision_baseline_is_taken_BEFORE_stage_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`Settlement.__init__` already writes the canvas W/H into `meta`. Starting from an empty dict
    made stage 1 claim credit for two values the constructor set - so the card would report the
    canvas size as something the drainage stage decided."""

    def stage_decides_only(s: Any, _plan: Any) -> None:
        s.M["meta"]["water_flow"] = "north-east"

    _stub_stages(monkeypatch, stage_decides_only)
    html = Path(ps.build_page(str(tmp_path), 300, _SPEC)).read_text()
    assert "water_flow" in html
    assert ">W<" not in html and ">H<" not in html, "the constructor's own values are not credited to a stage"


def test_a_stage_that_DRAWS_gets_a_plate_and_the_live_settlement_is_not_finished(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ "A COPY is finished, not the live settlement": `finish` flushes canopies, seats captions and
    crops, all of which mutate. Snapshotting the real one would change the map the next stage sees,
    and the page would document a build nobody runs. The second stage seeing an unfinished settlement
    is the assertion."""
    seen: list[int] = []

    def stage_draws(s: Any, _plan: Any) -> None:
        s.add('<rect x="10" y="10" width="50" height="50" fill="#333"/>')

    def stage_after(s: Any, _plan: Any) -> None:
        seen.append(ps._ink(s))
        s.add('<rect x="80" y="80" width="20" height="20" fill="#777"/>')

    _stub_stages(monkeypatch, stage_draws, stage_after)
    page = ps.build_page(str(tmp_path), 200, _SPEC)
    plates = sorted(p.name for p in tmp_path.glob("*.png"))
    assert plates == ["01-stage_draws.png", "02-stage_after.png"], plates
    assert seen and seen[0] < 50, f"the second stage saw a part-built map, not a finished one: {seen}"
    assert not list(tmp_path.glob("*.svg")) and not list(tmp_path.glob("*.json")), "the svg/json were means to the plate"
    assert 'src="01-stage_draws.png"' in Path(page).read_text()


def test_a_plate_this_run_did_not_write_is_PRUNED(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The orphan case, and it is not hypothetical: feature 128 renumbered the stages and left seven
    plates behind in a COMMITTED directory, including one showing lanes before houses - a picture of
    the exact build order that feature had removed. The per-stage removal cannot see a renumber, so
    the sweep at the end prunes anything this run did not write."""

    def stage_draws(s: Any, _plan: Any) -> None:
        s.add('<rect x="10" y="10" width="50" height="50" fill="#333"/>')

    (tmp_path / "04-stage_ways.png").write_bytes(b"stale")
    _stub_stages(monkeypatch, stage_draws)
    ps.build_page(str(tmp_path), 200, _SPEC)
    assert not (tmp_path / "04-stage_ways.png").exists(), "the orphan is gone"
    assert "pruned stale plate 04-stage_ways.png" in capsys.readouterr().out, "and it said so"


def test_a_stage_that_USED_to_draw_and_no_longer_does_leaves_no_orphan_at_its_own_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The other half: same index, stopped drawing. Removed as the stage is processed rather than by
    the sweep, because the sweep would keep it if some other stage happened to claim the name."""

    def stage_draws(_s: Any, _plan: Any) -> None:
        return None

    (tmp_path / "01-stage_draws.png").write_bytes(b"stale")
    _stub_stages(monkeypatch, stage_draws)
    ps.build_page(str(tmp_path), 200, _SPEC)
    assert not (tmp_path / "01-stage_draws.png").exists()


def test_a_stage_with_no_docstring_says_so_on_the_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The page is documentation; a stage nobody has written up must ASK for the docstring rather than
    render an empty cell that reads as "nothing to say about this one" (feature 227: the docstring is the source)."""

    def stage_unknown(_s: Any, _plan: Any) -> None:
        return None

    _stub_stages(monkeypatch, stage_unknown)
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    assert "no docstring" in html and "Steps:" in html


def test_main_writes_the_page_where_it_is_told_and_reports_the_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(ps, "build_page", lambda out, width, spec, steps_too=True: f"{out}/hamlet-placement.html")
    assert ps.main(["--out", str(tmp_path), "--width", "700"]) == 0
    assert "wrote" in capsys.readouterr().out


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    """This module is run as a script by `make placement-stages`, where the skill root is NOT on the
    path; under pytest it always is, so the import-time branch that fixes that would never otherwise
    execute. Re-imported with the entry removed, it puts it back."""
    import importlib
    import sys

    monkeypatch.setattr(sys, "path", [p for p in sys.path if Path(p).resolve() != Path(ps.SKILL).resolve()])
    reloaded = importlib.reload(ps)
    assert Path(reloaded.SKILL).resolve() in [Path(p).resolve() for p in sys.path]


# ---- feature 176, then 227: every stage explains itself in its docstring and declares its steps ------


def test_every_stage_explains_itself_and_declares_its_steps() -> None:
    """Feature 227 FR-004 (GM 2026-09-12: the page "generated based on the documentation, the docstrings, the stages"):
    EVERY stage in `STAGES` has a docstring with a purpose paragraph and a `Steps:` section naming the functions that
    are its algorithm; every name resolves to a function or method with a docstring of its own. A stage that explains
    nothing, or a step that does, fails the gate - the page cannot go quietly stale."""
    for stage in STAGES:
        title, paras, steps = ps.stage_doc(stage)
        assert "no docstring" not in title, f"{stage.__name__} has no docstring"
        assert steps, f"{stage.__name__} declares no Steps:"
        for path in steps:
            name, sparas = ps.step_doc(path)
            assert name == path.rsplit(".", 1)[-1] and sparas and "no docstring" not in sparas[0], f"{stage.__name__} step {path} has no docstring"


def test_stage_doc_reads_the_title_the_paragraphs_and_the_steps() -> None:
    def stage_toy(_s: Any, _plan: Any) -> None:
        """The toy stage.

        A paragraph about it,
        wrapped over two lines.

        Steps:
            l7r.diagram.hamletgen.plan.plan_site
            l7r.diagram.settlement.Settlement.try_place
        """

    title, paras, steps = ps.stage_doc(stage_toy)
    assert title == "The toy stage" and paras == ["A paragraph about it, wrapped over two lines."]
    assert steps == ["l7r.diagram.hamletgen.plan.plan_site", "l7r.diagram.settlement.Settlement.try_place"]
    assert ps.resolve_step(steps[1]).__name__ == "try_place", "a method resolves through its class"
    with pytest.raises(ImportError):
        ps.resolve_step("no.such.module.here")
    assert ps.step_doc("l7r.diagram.tools.placement_stages._ink")[0] == "_ink"


def test_the_homesteads_plate_draws_the_site_boundary_it_appeared_with(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 227 D4: the one new picture - the stage whose run RECORDS `site_boundary` gets that boundary drawn
    over its plate (chords, rings, corridors), mapped through the finished copy's view; other plates do not."""
    seen: list[Any] = []

    def fake_plate(snap: Any, out_dir: str, stem: str, width: int, overlay: Any = None, render_w: int = 2600) -> tuple[str, int, int]:
        seen.append((stem, overlay))
        return (stem + ".png", 10, 10)

    def stage_draws(s: Any, _plan: Any) -> None:
        s.out.append("<rect/>")

    def stage_bounds(s: Any, _plan: Any) -> None:
        s.M["site_boundary"] = {"chords": [[[0, 0], [1, 0], [0, -1]]], "rings": [], "holes": [], "water": [], "corridors": []}
        s.out.append("<rect/>")

    monkeypatch.setattr(ps, "_plate", fake_plate)
    _stub_stages(monkeypatch, stage_draws, stage_bounds, stage_draws)
    ps.build_page(str(tmp_path), 200, _SPEC)
    got = {stem: o is not None for stem, o in seen}  # the plates render in a thread pool: judge by stem, not by completion order
    assert got == {"01-stage_draws": False, "02-stage_bounds": True, "03-stage_draws": False}


def test_a_plate_draws_its_overlay_in_the_boundary_colors(tmp_path: Path) -> None:
    """Feature 227 D4: the site boundary drawn over the homesteads plate - the rings red, the chords blue, the
    corridors teal - mapped through the copy's view (the whole canvas on an uncropped mid-roll copy)."""
    from PIL import Image

    from l7r.diagram.settlement import Settlement

    s = Settlement(W=300, H=300, seed=1)
    s.add("<rect/>", cls="-")  # tagged ink, as the engine adds it: the finish checks the side list against the stream
    overlay = {
        "chords": [[[20.0, 150.0], [280.0, 150.0], [0.0, -1.0]]],
        "rings": [[[40.0, 40.0], [120.0, 40.0], [120.0, 120.0], [40.0, 120.0]]],
        "holes": [],
        "water": [[[20.0, 250.0], [280.0, 250.0], 5.0]],
        "corridors": [],
    }
    img, iw, ih = ps._plate(s, str(tmp_path), "06-stage_homesteads", 300, overlay)
    with Image.open(tmp_path / img) as im:
        px = list(im.convert("RGB").getdata())
    assert any(r > 150 and g < 90 and b < 90 for r, g, b in px), "a red ring"
    assert any(b > 150 and r < 90 for r, g, b in px), "a blue chord"
    assert any(g > 110 and b > 110 and r < 80 for r, g, b in px), "a teal corridor"


def test_the_page_renders_each_stages_steps_and_the_homesteads_legend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 227 FR-004: under every stage, the functions its `Steps:` names, each in its own words; the homesteads
    plate carries the legend for the boundary drawn over it."""

    def stage_homesteads(s: Any, _plan: Any) -> None:
        """A toy homesteads stage.

        It draws one rectangle.

        Steps:
            l7r.diagram.tools.placement_stages._ink
            l7r.diagram.tools.placement_stages.stage_doc
        """
        s.out.append("<rect/>")

    monkeypatch.setattr(ps, "_plate", lambda snap, out_dir, stem, width, overlay=None, render_w=2600: (stem + ".png", 10, 10))
    _stub_stages(monkeypatch, stage_homesteads)
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    assert html.count('<div class="step">') == 2 and "step by step (2)" in html
    assert "_ink" in html and "How many SVG records" in html, "the step is shown in its own docstring's words"
    assert "Drawn over this plate" in html, "the homesteads legend"


# ---- the plate after every step (feature 227 FR-007) ----------------------------------------------


def _drawing_stage() -> Any:
    """A stub stage whose docstring declares two ENGINE steps - one that draws, one that only measures.

    The steps are engine names rather than this module's own functions on purpose: under the full run the test
    package can be imported twice under two names, so patching the copy `resolve_step` finds watches a function
    the stage does not call - which is exactly how this test passed alone and failed at the gate."""

    def stage_two_steps(s: Any, _plan: Any) -> None:
        """Draws with one step and measures with the other.

        Steps:
            l7r.diagram.settlement.Settlement.add
            l7r.diagram.hamletgen.ways.geom.polyline_len
        """
        from l7r.diagram.hamletgen.ways.geom import polyline_len

        s.add('<rect x="10" y="10" width="50" height="50" fill="#333"/>')
        polyline_len([(0.0, 0.0), (10.0, 0.0)])

    return stage_two_steps


def test_a_step_that_DREW_gets_its_own_plate_and_one_that_only_measured_does_not(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The GM's refinement, 2026-09-12: a plate *"for literally every stage at which it would be possible to render
    an image that has actual content"*, and nothing where there is none - they named the no-content case themselves
    (*"the entire 'The bearing and the fall' phase There are literally no map visible features"*)."""
    _stub_stages(monkeypatch, _drawing_stage())
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    plates = sorted(p.name for p in tmp_path.glob("*.png"))
    assert plates == ["01-01-add.png", "01-stage_two_steps.png"], plates
    assert 'src="01-01-add.png"' in html and "the map after this step" in html
    assert "polyline_len" in html, "the step that drew nothing is still explained in words"


def test_the_step_plates_can_be_turned_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_stages(monkeypatch, _drawing_stage())
    ps.build_page(str(tmp_path), 200, _SPEC, steps_too=False)
    assert sorted(p.name for p in tmp_path.glob("*.png")) == ["01-stage_two_steps.png"]


def test_a_step_plate_this_run_did_not_write_is_pruned_too(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The sweep keeps what the page REFERENCES. Built from the stage rows alone it deleted every step plate the
    moment after it was rendered - measured on the first real run of this feature."""
    (tmp_path / "01-09-gone_step.png").write_bytes(b"stale")
    _stub_stages(monkeypatch, _drawing_stage())
    ps.build_page(str(tmp_path), 200, _SPEC)
    assert not (tmp_path / "01-09-gone_step.png").exists()
    assert (tmp_path / "01-01-add.png").exists(), "...and the one this run wrote survives the sweep"


def test_a_watermark_rewinds_a_copy_to_where_a_step_left_it() -> None:
    """Drawing here is append-only, which is what makes the rewind exact - and the DEFERRED stores are wound back
    with the ink, because each of their entries holds the index of the slot it reserved in `out` and `finish` writes
    through it (the first real run crashed in `flush_blade_groups` with an IndexError on exactly that)."""
    import copy

    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    s.add("<rect/>")
    mark = ps._watermark(s)
    assert ps._ink_total(mark) == ps._ink(s), "the watermark stands where the ink count does"
    s.add("<circle/>")
    s._blade_groups.append((len(s.out) - 1, "#333", []))
    snap = copy.deepcopy(s)
    ps._rewind(snap, mark)
    assert len(snap.out) == len(s.out) - 1 and len(snap.out_cls) == len(snap.out), "the layer and its class side-list move together"
    assert snap._blade_groups == [], "the deferred group whose slot no longer exists is gone"


def test_a_step_is_watched_wherever_its_name_is_bound_and_the_wrap_is_undone() -> None:
    """A step imported by name into another engine module binds a second reference, and patching only the defining
    module would watch a function nobody calls. The wrap is undone on the way out, so no map is ever rolled through
    a patched engine."""
    from l7r.diagram.hamletgen import ways
    from l7r.diagram.hamletgen.ways import geom

    points, target = ps._bind_points("l7r.diagram.hamletgen.ways.geom.polyline_len")
    assert (geom, "polyline_len") in points and (ways, "polyline_len") in points, points
    assert target is geom.polyline_len

    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    with ps._watch_steps(s, ["l7r.diagram.hamletgen.ways.geom.polyline_len"]) as marks:
        assert geom.polyline_len([(0.0, 0.0), (3.0, 4.0)]) == 5.0, "the wrapper returns what the step returns"
        assert "l7r.diagram.hamletgen.ways.geom.polyline_len" in marks
    assert geom.polyline_len is target and ways.polyline_len is target, "and the engine is put back"


def test_a_step_plate_that_will_not_render_is_reported_and_the_page_says_why(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The rewind reconstructs a moment INSIDE a stage rather than one the engine ever finished at, so a step that
    draws into what the step before it left can leave a document the renderer refuses - one of the field's five
    parts does. The page then loses one picture and says so, and "no plate" keeps meaning "drew nothing". A STAGE
    plate that will not render still fails the run: that IS a moment the engine passes through."""
    import subprocess

    real = ps._plate

    def sometimes(snap: Any, out_dir: str, stem: str, width: int, overlay: Any = None, render_w: int = 2600) -> tuple[str, int, int]:
        if "-01-" in stem:
            raise subprocess.CalledProcessError(1, ["resvg"])
        return real(snap, out_dir, stem, width, overlay, render_w)

    monkeypatch.setattr(ps, "_plate", sometimes)
    _stub_stages(monkeypatch, _drawing_stage())
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    # ASSERTED ON THE PAGE, NOT ON THE PRINT. The report line is written from the plate WORKER, and a print from a
    # worker thread races pytest's capture teardown under xdist - the capsys form passed alone and failed in the full
    # run, twice. What matters is what the reader gets, which is a step with no plate and a line saying why.
    assert "not a document the renderer will read" in html
    assert 'src="01-01-add.png"' not in html


def test_a_STAGE_plate_that_will_not_render_stops_the_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    def never(snap: Any, out_dir: str, stem: str, width: int, overlay: Any = None, render_w: int = 2600) -> tuple[str, int, int]:
        raise subprocess.CalledProcessError(1, ["resvg"])

    monkeypatch.setattr(ps, "_plate", never)
    _stub_stages(monkeypatch, _drawing_stage())
    with pytest.raises(subprocess.CalledProcessError):
        ps.build_page(str(tmp_path), 200, _SPEC, steps_too=False)


def test_balancing_closes_a_group_the_rewind_cut_open_and_skips_a_layer_that_is_not_a_list() -> None:
    """A stage opens a `<g>` in one record and closes it in another, so a watermark between the two leaves a prefix
    resvg refuses outright - measured on the beads step of the field stage. The class side-list gets the same number
    of entries, because the page writer reads the two in step."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    s.add('<g stroke="#333">')
    s.add('<rect x="1" y="1" width="2" height="2"/>')
    ps._balance_groups(s)
    assert s.out[-1] == "</g>" and len(s.out_cls) == len(s.out), "the group is closed and the side-list keeps step"
    ps._balance_groups(s)
    assert s.out.count("</g>") == 1, "idempotent: a balanced prefix is left alone"

    class _NotLists:
        out = None
        top = None
        walls = None
        toplabels = None

    ps._balance_groups(_NotLists())  # type: ignore[arg-type]  # a layer that is not a list contributes nothing


def test_every_clickable_class_is_named_somewhere_on_the_committed_page() -> None:
    """THE RULE THE GM GAVE, MECHANICALLY (2026-09-12): *"anything that I can click on after having it
    highlighted when I move my mouse over it on the HTML version of the map should be mentioned on the page
    ... Otherwise, how can I hit control f and then find out where the privies are being laid out?"*

    Measured when they asked: 22 of the 51 hoverable classes appeared nowhere on the page, because every word
    of it came from stage and step docstrings and a docstring does not enumerate what its code draws. The
    stage lists are derived from the ink now, and what one map cannot draw is named beside a map that does.

    This reads the COMMITTED page rather than building one, so it costs no roll; the page is regenerated by
    every landing, so a stale page is a failure worth seeing."""
    import html as _html
    import re as _re

    from l7r.diagram.interactive.classes import CLASSES

    page = Path(ps.SKILL) / "dev" / "placement-stages" / "hamlet-placement.html"
    if not page.exists():
        pytest.skip("the page has not been plated in this tree")
    text = _html.unescape(_re.sub(r"<[^>]+>", " ", page.read_text())).lower()
    missing = [k for k in sorted(CLASSES) if not any(f in text for f in (k, k + "s", k.rstrip("s"), k.replace(" ", "_")))]
    assert not missing, f"a reader can click these and the page never names them: {missing}"


def test_features_between_reads_the_classes_whose_ink_appeared() -> None:
    """The derivation the page's feature lists rest on: the class side-lists run parallel to the ink layers,
    so the difference between two watermarks is what one stage or step drew. Ruled-but-not-highlighted ink
    (`"-"`) is excluded, because a reader cannot click it - and a layer that is not a list contributes
    nothing rather than raising."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    lo = ps._watermark(s)
    s.add('<rect x="1" y="1" width="9" height="9" fill="#333"/>', cls="farmhouse")
    s.add('<rect x="20" y="1" width="9" height="9" fill="#444"/>', cls="byre")
    s.add('<rect x="40" y="1" width="9" height="9" fill="#555"/>', cls="-")
    assert ps.features_between(s, lo, ps._watermark(s)) == ["byre", "farmhouse"], "sorted, and the '-' is left out"
    assert ps.features_between(s, ps._watermark(s), ps._watermark(s)) == [], "no ink between two equal marks"

    class _NoLayers:
        M = {"meta": {}}
        out = None
        out_cls = None
        top = None
        top_cls = None
        walls = None
        walls_cls = None
        toplabels = None
        toplabels_cls = None

    assert ps.features_between(_NoLayers(), {}, {}) == []  # type: ignore[arg-type]


def _classed_stage() -> Any:
    """A stub stage that draws CLASSED ink through a declared step, so the page prints both feature lines."""

    def stage_classed(s: Any, _plan: Any) -> None:
        """Draws one thing a reader can click.

        Steps:
            l7r.diagram.settlement.Settlement.add
        """
        s.add('<rect x="10" y="10" width="50" height="50" fill="#333"/>', cls="farmhouse")

    return stage_classed


def test_the_page_names_the_features_a_stage_and_its_step_put_on_the_map(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The GM's rule (2026-09-12): anything a reader can click must be findable on the page. The stage line and
    the step line are both derived from the ink, so a feature cannot be renamed or moved between stages
    without the page following it."""
    monkeypatch.setattr(ps, "_plate", lambda snap, out_dir, stem, width, overlay=None, render_w=2600: (stem + ".png", 10, 10))
    _stub_stages(monkeypatch, _classed_stage())
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    assert "Features this stage puts on the map" in html and "farmhouse" in html
    assert "<span class=\"fl\">Draws</span> farmhouse" in html, "the step names what it drew too"


def test_the_closing_section_names_what_this_map_cannot_draw(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One map's ink can only name what that map has, and the pool draws five kinds of place - so every other
    clickable class is named beside a shipped map that has it, read from that map's own interactive page."""
    from l7r.diagram.interactive.classes import CLASSES

    rest = ps.elsewhere_in_the_pool({"farmhouse"}, ps.SKILL)
    assert rest and len(rest) == len(CLASSES) - 1, "everything but the one named class is accounted for"
    assert all(isinstance(m, str) for _k, m in rest), "each carries a map name, or '' when no map draws it"
    assert ps.elsewhere_in_the_pool(set(CLASSES), ps.SKILL) == [], "nothing is left when every class is named"

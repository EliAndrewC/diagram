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

`tooling`: it renders and writes files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.tools import placement_stages as ps

pytestmark = pytest.mark.tooling

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


def test_a_stage_with_no_NOTES_entry_says_so_on_the_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The page is documentation; a stage nobody has written up must ASK for the note rather than
    render an empty cell that reads as "nothing to say about this one"."""

    def stage_unknown_to_notes(_s: Any, _plan: Any) -> None:
        return None

    _stub_stages(monkeypatch, stage_unknown_to_notes)
    html = Path(ps.build_page(str(tmp_path), 200, _SPEC)).read_text()
    assert "no note yet" in html and "add one" in html.lower()


def test_main_writes_the_page_where_it_is_told_and_reports_the_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(ps, "build_page", lambda out, width, spec: f"{out}/hamlet-placement.html")
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

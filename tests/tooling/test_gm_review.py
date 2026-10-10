"""The GM's review after landing (feature 375, FR-012, plan D12): `make gm-review`, `make accept`, `make gm-reviewed`.

The GM wants features to land without waiting on him, with "that and only that category of box unticked". Each case is a
step of that box's life: a row appears (an arbiter ruling or an accepted finding), the box appears with it, the feature lands
and reads `Done - GM review pending`, the GM reviews it (or overturns a row into another feature), and the box closes the
feature through its closing check.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_modal_checks import _load

gm = _load("gm_review")
todo = _load("speckit-todo")
ha = _load("hm_arbiter")
cc = _load("close_check")


@pytest.fixture
def root(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    monkeypatch.setattr(cc, "GRANDFATHERED", tmp_path / "none.txt")
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))
    for name in ("375-x", "376-y"):
        d = tmp_path / "specs" / name
        d.mkdir(parents=True)
        (d / "spec.md").write_text("# Feature\n\n**Status**: In progress\n")
        (d / "tasks.md").write_text("- [x] T01 built\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    return tmp_path


def test_a_row_for_the_gm_brings_its_box_and_the_feature_reads_pending(root: pathlib.Path) -> None:
    d = root / "specs" / "375-x"
    assert todo.feature(d).state == "closed" and gm.listing(root) == "gm-review: nothing waits on the GM\n"
    with pytest.raises(ValueError, match="two words"):
        gm.accept(d, "the steam arcs", "fine")
    gm.accept(d, "the steam arcs off center", "a drawing nicety no norm sets")
    assert gm.box(d) in (d / "tasks.md").read_text()
    assert todo.feature(d).state == "done - GM review pending" and todo.holding(d) == []
    assert "TO REVIEW - 375-x" in gm.listing(root) and "[0] accepted: the steam arcs off center" in gm.listing(root)
    assert not gm.ensure_box(d), "one box"


def test_an_arbiter_ruling_is_a_row_and_the_gm_closes_it(root: pathlib.Path) -> None:
    d = root / "specs" / "375-x"
    ha.trip(root, "reversal:/a.md", "reversal", "/a.md", "A -> B -> A", 1)
    ha.record_ruling(root, "reversal:/a.md", {"ruling": "accept", "why": "the second wording is the right one"}, "round-arbiter")
    assert gm.box(d) in (d / "tasks.md").read_text(), "the ruling's row brought the box"
    with pytest.raises(ValueError, match="no report.md"):
        gm.reviewed(root, d)
    (d / "report.md").write_text("# report\n")
    assert gm.reviewed(root, d) == ["1 row(s) of 375-x reviewed"]
    assert todo.feature(d).state == "closed" and all("reviewed" in r for r in gm.rows(d))
    assert "nothing waits" in gm.listing(root)


def test_an_overturned_row_becomes_an_open_row_of_another_feature(root: pathlib.Path) -> None:
    d, other = root / "specs" / "375-x", root / "specs" / "376-y"
    (d / "report.md").write_text("# report\n")
    gm.accept(d, "the bath at 18 by 12 ft", "the resident's particular allows it")
    with pytest.raises(ValueError, match="OVERTURN"):
        gm.reviewed(root, d, 5, other)
    assert gm.reviewed(root, d, 0, other)[0] == "row 0 overturned - an open row of 376-y"
    found = json.loads((other / "found.jsonl").read_text())
    assert found["status"] == "open" and "overturned by the GM" in found["finding"]


def test_the_held_rows_and_the_command_line(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    held = root / gm.HELD
    held.parent.mkdir(parents=True)
    held.write_text(json.dumps({"a#door band": {"flag": "Held: question for the GM"}, "b#x": {"flag": "deviation-tempting"}}))
    assert gm.held(root) == ["a#door band: Held: question for the GM"] and "HELD - work cannot go on" in gm.listing(root)
    monkeypatch.chdir(root)
    assert gm.main(["list"]) == 0 and "door band" in capsys.readouterr().out
    assert gm.main(["accept", "375", "a finding", "a reason here"]) == 0
    assert gm.main(["accept", "375", "a finding", "x"]) == 1
    assert gm.main(["reviewed", "375"]) == 1, "no report: the box would close it"
    (root / "specs" / "375-x" / "report.md").write_text("# report\n")
    assert gm.main(["reviewed", "375"]) == 0
    assert gm.main(["bogus"]) == 2
    with pytest.raises(SystemExit):
        gm.main(["reviewed", "999"])
    assert gm.rows(root / "specs" / "376-y") == []
    (root / "specs" / "376-y" / "gm-review.jsonl").write_text("not json\n")
    assert gm.rows(root / "specs" / "376-y") == []

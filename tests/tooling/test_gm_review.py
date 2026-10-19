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
    assert "375  x" in gm.listing(root) and "1 accepted" in gm.listing(root)
    assert "[0] the steam arcs off center" in gm.listing(root, "375") and "a drawing nicety" in gm.listing(root, "375")
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


def test_a_discussed_row_is_reviewed_with_the_gms_words(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    d = root / "specs" / "375-x"
    (d / "report.md").write_text("# report\n")
    gm.accept(d, "the steam arcs off center", "a drawing nicety no norm sets")
    assert 'make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS="<his words>")' in gm.listing(root), "says how a discussion closes it"
    with pytest.raises(ValueError, match="two words"):
        gm.reviewed(root, d, words="fine")
    monkeypatch.chdir(root)
    monkeypatch.setenv("GM_WORDS", "I don't know that we need any tooling around it")
    assert gm.main(["reviewed", "375"]) == 0
    assert gm.rows(d)[0]["gm_words"] == "I don't know that we need any tooling around it"
    assert "nothing waits" in gm.listing(root)


def test_an_overturned_row_becomes_an_open_row_of_another_feature(root: pathlib.Path) -> None:
    d, other = root / "specs" / "375-x", root / "specs" / "376-y"
    (d / "report.md").write_text("# report\n")
    gm.accept(d, "the bath at 18 by 12 ft", "the resident's particular allows it")
    with pytest.raises(ValueError, match="OVERTURN"):
        gm.reviewed(root, d, 5, other)
    gm.accept(d, "the bath door on the yard", "the yard is the service side")
    assert gm.reviewed(root, d, 0, other) == ["row 0 overturned - an open row of 376-y"]
    assert "reviewed" in gm.rows(d)[0] and "reviewed" not in gm.rows(d)[1], "an overturn reviews its own row, not the feature's"
    assert gm.rows(d)[0]["overturned_to"] == "376-y" and "the bath door" in gm.listing(root, "375")
    found = json.loads((other / "found.jsonl").read_text())
    assert found["status"] == "open" and "overturned by the GM" in found["finding"]
    (d / gm.ROWS).open("a").write(json.dumps({"kind": "arbiter-fix-declined", "trigger": "t", "tooling_fix": "re-owe less", "note": "FR-015 says"}) + "\n")
    gm.reviewed(root, d, 2, other)
    last = json.loads((other / "found.jsonl").read_text().splitlines()[-1])
    assert last["finding"] == "overturned by the GM: re-owe less - FR-015 says", "a declined fix carries the fix and why it was declined"


def test_one_row_is_reviewed_alone(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    d = root / "specs" / "375-x"
    gm.accept(d, "the bath at 18 by 12 ft", "the resident's particular allows it")
    gm.accept(d, "the bath door on the yard", "the yard is the service side")
    assert gm.reviewed_row(d, 1, "already built elsewhere") == "row 1 of 375-x reviewed; 1 still wait on the GM"
    assert "reviewed" not in gm.rows(d)[0] and gm.rows(d)[1]["gm_words"] == "already built elsewhere"
    assert "- [ ] GM review" in (d / "tasks.md").read_text(), "one row reviewed leaves the feature's box open"
    with pytest.raises(ValueError, match="ROW=2"):
        gm.reviewed_row(d, 2)
    monkeypatch.chdir(root)
    assert gm.main(["reviewed-row", "375", "0"]) == 0 and "0 still wait" in capsys.readouterr().out


def test_the_held_rows_and_the_command_line(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    held = root / gm.HELD
    held.parent.mkdir(parents=True)
    held.write_text(json.dumps({"a#door band": {"flag": "Held: question for the GM"}, "b#x": {"flag": "deviation-tempting"}}))
    assert gm.held(root) == ["a#door band: Held: question for the GM"] and "HELD - work cannot go on" in gm.listing(root)
    assert "      question for the GM" in gm.listing(root), "the flag under its key, without the word the heading already says"
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


def test_the_summary_counts_and_one_feature_groups_its_rows(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    d = root / "specs" / "375-x"
    for trigger in ("round:modal-form|modal:sheet/kitchen@3", "round:quote-check|q:0047@3"):
        ha.trip(root, trigger, "round", trigger, "three rounds", 1)
        ha.record_ruling(root, trigger, {"ruling": "accept", "why": "the rounds converged"}, "round-arbiter")
    ha.trip(root, "red-gate@2026-10-10T22:25:54Z", "red-gate", "gate", "two reds", 1)
    ha.record_ruling(root, "red-gate@2026-10-10T22:25:54Z", {"ruling": "continue", "why": "not a loop"}, "round-arbiter")
    summary = gm.listing(root, width=200)
    assert "3 rulings (1 continue)" in summary and "converged" not in summary, "the bare listing counts, never lists rows"
    one = gm.listing(root, "375", width=200)
    assert "[0-1] accept: modal-form sheet/kitchen; quote-check 0047\n        the rounds converged" in one, "one reason, one line"
    assert "[2] continue: red-gate 2026-10-10T22:25:54Z" in one
    assert gm.listing(root, "375", width=80).count("\n") == one.count("\n") and max(map(len, gm.listing(root, "375", width=80).splitlines())) <= 80
    assert gm._ids([0, 1, 2, 5, 7, 8]) == "0-2,5,7-8" and gm._subject({"trigger": "reversal:/a/b/c.html"}) == ("reversal", "c.html")
    assert gm._subject({"trigger": "odd"}) == ("", "odd")
    gm.reviewed(root, d) if (d / "report.md").write_text("# r\n") else None
    assert gm.listing(root, "375") == "gm-review: nothing of 375-x waits on the GM\n"
    monkeypatch.chdir(root)
    assert gm.main(["list", "375"]) == 0 and "nothing of 375-x" in capsys.readouterr().out


def _rows(d: pathlib.Path, *rs: dict) -> None:
    with (d / gm.ROWS).open("a", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in rs)


def test_explain_says_what_fired_what_was_ruled_and_what_the_gm_is_asked(root: pathlib.Path) -> None:
    """The GM, 2026-10-12: the rows did not tell him what he was being asked to rule on."""
    d = root / "specs" / "375-x"
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "agents" / "modal-form.md").write_text("---\ndescription: Judges a modal's FORM - run on the modals\n---\n")
    (root / "research" / "questions").mkdir(parents=True)
    for name in ("0047-farm-privies.html", "0047-farm-privies.drawing.html"):
        (root / "research" / "questions" / name).write_text("")
    ha.trip(root, "round:modal-form|modal:sheet/kitchen@3", "round", "modal-form|modal:sheet/kitchen", "three rounds on the kitchen", 1)
    ha.record_ruling(
        root, "round:modal-form|modal:sheet/kitchen@3", {"ruling": "accept", "why": "the rounds converged", "what": "nothing is left", "tooling_fix": "count only own rounds"}, "round-arbiter"
    )
    assert gm.rows(d)[0]["asked"] == "three rounds on the kitchen" and gm.rows(d)[0]["what"] == "nothing is left", "the question kept"
    ha.trip(root, "round:quote-check|q:0047@3", "round", "quote-check|q:0047", "", 1)
    ha.record_ruling(root, "round:quote-check|q:0047@3", {"ruling": "continue", "why": "one new note", "tooling_fix": "keep replies"}, "round-arbiter")
    ha.settle_fix(root, "round:quote-check|q:0047@3", "declined", "it contradicts FR-015")
    _rows(
        d,
        {
            "kind": "arbiter-fix-done",
            "trigger": "round:modal-form|modal:sheet/kitchen@3",
            "tooling_fix": "count only own rounds",
            "note": "counted per feature",
            "test": "tests/tooling/test_hm_arbiter.py",
        },
        {"kind": "arbiter-fix-done", "trigger": "reversal:/x/.clones/c/docs/a.md", "tooling_fix": "bundle the reversal", "note": "bundled now"},
        {"kind": "arbiter", "trigger": "reversal:/x/.clones/c/docs/a.md", "ruling": "process-fault", "why": "two checks pulled"},
    )
    gm.accept(d, "the steam arcs off center", "a drawing nicety no norm sets")
    for t in ("red-gate@2026-10-10T22:25:54Z", "cascade:375", "ask:f375-x", "odd"):
        _rows(d, {"kind": "arbiter", "trigger": t, "ruling": "continue", "why": "fine as it is"})
    e = " ".join(gm.explain(root, "375", width=200).split())  # wrapped at 110 columns: compare the words
    assert "[0] modal-form sheet/kitchen" in e and "check (judges a modal's FORM) was owed a round 3 on sheet/kitchen" in e
    assert "As it fired: three rounds on the kitchen" in e and "Where: l7r/diagram/interactive/assets/modals/sheet/kitchen.md" in e
    assert "The arbiter ruled: ACCEPT - stop checking" in e and "It set the next step: nothing is left" in e
    assert "[3] the tooling fix: DONE" in e and "Test: tests/tooling/test_hm_arbiter.py" in e, "the fix shown under its ruling"
    assert "Where: research/questions/0047-farm-privies.html" in e and "[2] the tooling fix: DECLINED" in e
    assert "YOUR DECISION: should this fix be made after all?" in e and "OVERTURN=2 TO=" in e
    assert "Where: docs/a.md" in e and "PROCESS FAULT" in e and "A -> B -> A" in e
    assert "A session accepted this finding without fixing it: the steam arcs off center" in e
    assert "CONTINUE - nothing is stuck" in e and "CONTINUE - allow one more round" in e, "a continue says what it lets go on"
    assert "went red twice" in e and "faster than one per changed line" in e and "process question" in e and "Trigger odd." in e
    one = gm.explain(root, "375", "3", width=200)
    assert "[0] modal-form" in one and "quote-check" not in one, "ROW= a fix row shows the ruling it settles"
    _rows(d, {"kind": "arbiter-fix-done", "trigger": "round:gone|q:0001@3", "tooling_fix": "an orphan fix", "note": "made it so"})
    orphan = gm.explain(root, "375", "11", width=200)
    assert "The fix asked for: an orphan fix" in orphan and "[0]" not in orphan
    assert gm.explain(root, "375", "99") == "gm-review: no open row 99 in 375-x\n"
    assert gm.explain(root, "376") == "gm-review: nothing of 376-y waits on the GM\n"
    assert max(map(len, gm.explain(root, "375", width=60).splitlines())) <= 60


def test_explain_with_no_feature_names_only_what_needs_the_gm(root: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # noqa: ANN001
    held = root / gm.HELD
    held.parent.mkdir(parents=True)
    held.write_text(json.dumps({"a#door band": {"flag": "Held: which door size stands?", "fix": "narrow the doors"}, "b#tubs": {"flag": "Held behind #retainers (row 21): after that lands"}}))
    d = root / "specs" / "375-x"
    _rows(
        d,
        {"kind": "arbiter-fix-declined", "trigger": "round:modal-depiction|modal:sheet/garden@3", "tooling_fix": "re-owe less", "note": "contradicts FR-015"},
        {"kind": "arbiter", "trigger": "red-gate@t", "ruling": "continue", "why": "not a loop"},
    )
    e = gm.explain(root, width=200)
    assert "1. HELD QUESTION: a#door band\n    which door size stands?. The fix it would make: narrow the doors." in e
    assert "WAITING ON OTHER WORK - held in the ranking until another row is done; nothing for you to decide\n\n  * b#tubs\n    Waits on #retainers" in e, (
        "a row held behind other work is not a decision of the GM's"
    )
    assert "2. A TOOLING FIX DECLINED TO YOU: feature 375 row [0], modal-depiction sheet/garden" in e
    assert "The other 1 row(s) are decisions already made" in e
    assert "needs a decision: 1 held question(s), 1 fix(es) declined" in gm.listing(root, width=200)
    assert "WAITING ON OTHER WORK - held in the ranking behind another row, not on the GM\n  * b#tubs\n      waits on #retainers" in gm.listing(root, width=200)
    assert gm.listing(root, width=200).startswith("GM REVIEW - 1 held question(s), 1 waiting on other work,")
    monkeypatch.chdir(root)
    assert gm.main(["explain", "375", "1"]) == 0 and "went red twice" in capsys.readouterr().out
    held.write_text(json.dumps({"b#tubs": {"flag": "Held behind #retainers (row 21): after that lands"}}))
    (d / gm.ROWS).write_text("")
    (held.parent / "waves.json").write_text(json.dumps({"a#door band": "115"}))
    assert gm.explain(root, width=200).startswith("WHAT NEEDS YOUR DECISION: nothing - no held question and no fix declined to you")
    (held.parent / "waves.json").write_text(json.dumps({"b#tubs": "115"}))
    assert gm.held(root) == [] and "WAITING ON OTHER WORK" not in gm.explain(root), "a row its wave closed is held no more"

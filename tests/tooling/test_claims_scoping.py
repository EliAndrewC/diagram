"""`scripts/record/claims.py` - a re-check scoped to the blocks a claim rests on (feature 318, FR-016, SC-011).

The GM, 2026-10-04, on 370 claims re-owed by a few edits to one page: *"fix that ... to ensure the rechecks are appropriately
scoped"*. An edit to one block re-owes in full only the claims resting on it; the claims whose blocks stand owe a triage, and
a triage reply clears every claim it does not name; a row checked before the rule is owed in full; the backfill gives rows
checked at today's research their pages.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_claims_index import MOD, _commit, _repo, _tree, cx

PAGE = '<h2 id="row-villages-resson">Row villages</h2>\n<p class="intro">Why asked.</p>\n<p>Farms face the street.</p>\n<p>Each lane is 5 ft.</p>\n'
SHARE = "l7r/diagram/hamletgen/rows.py::SHARE#dry share"
FAR = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
QDIR = "research/questions"


def _checked(tmp: pathlib.Path) -> tuple[pathlib.Path, dict, dict]:
    """A tree whose SHARE claim rests on the first block and far_row's on the second, recorded from a bundle."""
    skill = _tree(tmp, MOD, PAGE)
    cur = cx.current(skill)
    manifest = cx.bundle(tmp, cur, sorted(cur), tmp / "b").read_text()
    assert "END EVERY VERDICT NOTE with the blocks" in manifest
    q = (tmp / "b" / "questions" / "0033-row-villages-resson.html.txt").read_text()
    assert "[intro] Why asked." in q and "[§1] Farms face the street." in q and "[§2] Each lane is 5 ft." in q
    blocks = json.loads((tmp / "b" / "blocks.json").read_text())
    units = json.loads((tmp / "b" / "units.json").read_text())
    reply = "".join(f"VERDICT {k} IN-STEP - ok {'[§1]' if k == SHARE else '[§2]' if k == FAR else '[§]'}\n" for k in units)
    index, msgs = cx.record({}, units, reply, "d", blocks["numbered"])
    assert not [m for m in msgs if "refused" in m or "no verdict" in m]
    return skill, index, blocks["snapshots"]


def test_a_verdict_keeps_the_blocks_it_rests_on_and_the_pages_it_was_checked_at(tmp_path: pathlib.Path) -> None:
    _skill, index, store = _checked(tmp_path)
    name = "0033-row-villages-resson.html"
    assert index[SHARE]["note"] == "ok" and len(index[SHARE]["rests"]) == 1 and index[SHARE]["rests"][0].startswith(f"{name}:")
    assert index[SHARE]["rests"] != index[FAR]["rests"] and set(index[SHARE]["pages"]) == {name}
    assert index[SHARE]["pages"][name] in store and len(store[index[SHARE]["pages"][name]]) == 2, "the intro is no block"
    assert all("rests" not in v or v["rests"] == [] for k, v in index.items() if k not in (SHARE, FAR) and "#" in k and v.get("research") == "")


def test_rests_of_reads_the_closing_tag_only() -> None:
    numbered = {"§1": "p:a", "§2": "p:b"}
    assert cx.rests_of("ok [§2, §1]", numbered) == ("ok", ["p:a", "p:b"])
    assert cx.rests_of("silent [§]", numbered) == ("silent", [])
    assert cx.rests_of("ok [§9]", numbered) == ("ok", []), "a number the bundle does not hold is dropped"
    assert cx.rests_of("cites [§1] mid-note only", numbered) == ("cites [§1] mid-note only", None)


def test_an_edit_to_one_block_owes_in_full_only_the_claims_resting_on_it(tmp_path: pathlib.Path) -> None:
    skill, index, store = _checked(tmp_path)
    qdir = skill / QDIR
    assert cx.owed(cx.current(skill), index, qdir, store) == []
    _tree(tmp_path, MOD, PAGE.replace("5 ft", "6 ft"))
    due = dict(cx.owed(cx.current(skill), index, qdir, store))
    assert due == {FAR: "rests changed", SHARE: "triage"}
    assert cx.judged(list(due.items())) == [FAR]
    assert dict(cx.owed(cx.current(skill), index, qdir, None)) == {FAR: "research changed", SHARE: "research changed"}, "no snapshots: in full"
    assert dict(cx.owed(cx.current(skill), index))[SHARE] == "research changed", "no question directory: as before"


def test_a_row_checked_before_the_rule_is_owed_in_full_and_one_with_no_rests_is_triaged(tmp_path: pathlib.Path) -> None:
    skill, index, store = _checked(tmp_path)
    _tree(tmp_path, MOD, PAGE.replace("5 ft", "6 ft"))
    old = {k: {kk: vv for kk, vv in v.items() if kk not in ("pages", "rests")} for k, v in index.items()}
    assert dict(cx.owed(cx.current(skill), old, skill / QDIR, store))[FAR] == "research changed"
    silent = {k: {kk: vv for kk, vv in v.items() if kk != "rests"} for k, v in index.items()}
    assert dict(cx.owed(cx.current(skill), silent, skill / QDIR, store)) == {FAR: "triage", SHARE: "triage"}


def test_the_triage_shows_only_the_changed_blocks_and_clears_the_claims_it_does_not_name(tmp_path: pathlib.Path) -> None:
    skill, index, store = _checked(tmp_path)
    _tree(tmp_path, MOD, PAGE.replace("5 ft", "6 ft").replace("</p>\n<p>Each", "</p>\n<p>A new rule.</p>\n<p>Each"))
    cur = cx.current(skill)
    manifest = cx.triage_bundle(cur, index, store, [SHARE], skill / QDIR, tmp_path / "t").read_text()
    assert "> Each lane is 6 ft." in manifest and "> A new rule." in manifest and "Farms face" not in manifest
    assert f"- KEY `{SHARE}`" in manifest and "last verdict IN-STEP: ok" in manifest
    data = json.loads((tmp_path / "t" / "triage.json").read_text())
    store2 = {**store, **data["snapshots"]}
    cleared, msgs = cx.record_triage(index, data["units"], "triage: none bear on it\n", "d2")
    assert msgs == [] and cleared[SHARE]["triaged"] == "d2" and cleared[SHARE]["verdict"] == "IN-STEP"
    assert SHARE not in dict(cx.owed(cur, cleared, skill / QDIR, store2)), "cleared at today's page"
    touched, msgs = cx.record_triage(index, data["units"], f"TOUCHES {SHARE} - the new rule\nTOUCHES p::x#y - stray\n", "d2")
    assert msgs == ["refused: `p::x#y` is not a claim of this triage", f"touched: {SHARE} - the new rule"]
    assert dict(cx.owed(cur, touched, skill / QDIR, store2))[SHARE] == "triage touched"
    again, _ = cx.record_triage(touched, data["units"], "", "d3")
    assert "triage" not in again[SHARE], "a later clearing drops the mark"


def test_a_removal_reaches_the_triage_shown_from_the_pages_history(tmp_path: pathlib.Path) -> None:
    """The plan review's case: a row with no `rests` may rest on the very block an edit deletes - the triage must SHOW it."""
    root = _repo(tmp_path)
    skill, index, store = _checked(root)
    _commit(root, "the page with both blocks")
    silent = {k: {kk: vv for kk, vv in v.items() if kk != "rests"} for k, v in index.items()}
    _tree(root, MOD, PAGE.replace("<p>Each lane is 5 ft.</p>\n", ""))
    cur = cx.current(skill)
    assert dict(cx.owed(cur, silent, skill / QDIR, store)) == {FAR: "triage", SHARE: "triage"}
    manifest = cx.triage_bundle(cur, silent, store, [SHARE, FAR], skill / QDIR, tmp_path / "t").read_text()
    assert "Removed blocks (no longer on the page):\n\n> Each lane is 5 ft." in manifest and "New or changed blocks:\n\n(none)" in manifest
    assert f"- KEY `{FAR}`" in manifest and json.loads((tmp_path / "t" / "triage.json").read_text())["forced"] == []


def test_a_removal_the_history_cannot_show_owes_its_claims_in_full(tmp_path: pathlib.Path) -> None:
    skill, index, store = _checked(tmp_path)  # no repository: no history to read the removed block back from
    _tree(tmp_path, MOD, PAGE.replace("<p>Each lane is 5 ft.</p>\n", ""))
    cur = cx.current(skill)
    cx.triage_bundle(cur, index, store, [SHARE], skill / QDIR, tmp_path / "t")
    data = json.loads((tmp_path / "t" / "triage.json").read_text())
    assert data["forced"] == [SHARE]
    out, msgs = cx.record_triage(index, data["units"], "", "d", data["forced"])
    assert out[SHARE]["triage"] == "touched" and msgs == [f"touched: {SHARE} - a removed block the history no longer shows"], "an empty reply clears nothing forced"


def test_the_backfill_gives_only_rows_checked_at_todays_research_their_pages(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path, MOD, PAGE)
    cur = cx.current(skill)
    index = {k: {"verdict": "IN-STEP", "code": r.code, "core": r.unit.core, "research": r.research} for k, r in cur.items()}
    index[FAR]["research"] = "stale"
    store: dict[str, list[str]] = {}
    assert cx.backfill(cur, index, skill / QDIR, store) == 1
    assert "pages" in index[SHARE] and "pages" not in index[FAR] and len(store) == 1
    assert cx.backfill(cur, index, skill / QDIR, store) == 0, "once"


def test_the_command_line_triage_triaged_and_backfill(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    skill = root
    _tree(root, MOD, PAGE)
    assert cx.main(["--root", str(root), "triage"]) == 0 and "no claim is owed a triage" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "bundle", "--owed", "--out", str(tmp_path / "b")]) == 0
    units = json.loads((tmp_path / "b" / "units.json").read_text())
    (tmp_path / "r.txt").write_text("".join(f"VERDICT {k} IN-STEP - ok {'[§1]' if k == SHARE else '[§2]' if k == FAR else '[§]'}\n" for k in units))
    assert cx.main(["--root", str(root), "record", "--bundle", str(tmp_path / "b"), "--reply", str(tmp_path / "r.txt")]) == 0
    assert (root / cx.STORE).is_file()
    _commit(root, "checked")
    _tree(root, MOD, PAGE.replace("5 ft", "6 ft"))
    capsys.readouterr()
    assert cx.main(["--root", str(root), "owed"]) == 0
    out = capsys.readouterr().out
    assert "1 claim(s) in 1 file(s) owe impl-drift" in out and "1 claim(s) owe only a TRIAGE" in out
    assert cx.main(["--root", str(root), "bundle", "--owed", "--out", str(tmp_path / "c")]) == 0
    assert list(json.loads((tmp_path / "c" / "units.json").read_text())) == [FAR], "the triage claim is not judged"
    assert cx.main(["--root", str(root), "triage", "--out", str(tmp_path / "t")]) == 0
    (tmp_path / "t.txt").write_text("")
    assert cx.main(["--root", str(root), "triaged", "--bundle", str(tmp_path / "t"), "--reply", str(tmp_path / "t.txt")]) == 0
    assert "0 of 1 sent on to impl-drift" in capsys.readouterr().out
    assert [k for k, _w in cx.owed(cx.current(skill), cx.load_index(root / cx.INDEX), skill / cx.QUESTIONS.split("/", 3)[-1], cx.load_store(root / cx.STORE))] == [FAR]
    assert cx.main(["--root", str(root), "backfill"]) == 0 and "row(s) given the pages" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "report"]) == 0


def test_a_rest_on_a_page_the_claim_does_not_cite_is_dropped_and_named() -> None:
    """Feature 328 wave 95: an agent re-sent a fresh bundle cited the section numbers of the bundle it first read, and the
    claims came to rest on blocks of pages they do not cite, so an edit to their own pages no longer re-owed
    them. A rest outside the claim's own pages is dropped - the claim then owes a triage of any change on its pages - and named."""
    units = {SHARE: {"uid": SHARE.split("#")[0], "code": "c", "core": "c", "research": "r", "pages": {"0033-row-villages-resson.html": "d"}}}
    numbered = {"§1": "0033-row-villages-resson.html:a", "§2": "0081-village-lanes.drawing.html:b"}
    index, msgs = cx.record({}, units, f"VERDICT {SHARE} IN-STEP - ok [§1, §2]\n", "d", numbered)
    assert index[SHARE]["rests"] == ["0033-row-villages-resson.html:a"]
    assert any("0081-village-lanes.drawing.html" in m for m in msgs)
    index, msgs = cx.record({}, units, f"VERDICT {SHARE} IN-STEP - ok [§2]\n", "d", numbered)
    assert "rests" not in index[SHARE], "nothing of its own pages left: any change on them is triaged"

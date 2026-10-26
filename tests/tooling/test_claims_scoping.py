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

from tests.tooling.test_claims_index import MOD, Q, _commit, _repo, _tree, cx

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


def test_a_claim_that_newly_cites_a_page_is_owed_in_full(tmp_path: pathlib.Path) -> None:
    """Feature 385 T105 (D123): T100's two UNRESEARCHED claims relabeled to cite 0035 and 0246 rested on nothing, so they were
    listed `triage`, their triage bundle named no claim and `make claims-bundle OWED=1` refused them."""
    skill, index, store = _checked(tmp_path)
    cur = cx.current(skill)
    was_unresearched = {**index, SHARE: {**index[SHARE], "pages": {}, "rests": [], "research": "before the relabel"}}
    assert dict(cx.owed(cur, was_unresearched, skill / QDIR, store))[SHARE] == "research changed"
    reworded = {**index, SHARE: {**index[SHARE], "research": "its words moved, its pages did not"}}
    assert dict(cx.owed(cur, reworded, skill / QDIR, store))[SHARE] == "triage", "the pages it was checked at: the triage rule stands"


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
    # what every triage bundle repeats - before its first page - is a line naming the agent; the rules are its contract,
    # its system prompt (feature 383 amendment 6, plan D38)
    assert len(manifest.split("\n## ", 1)[0]) < 400
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


def test_the_command_line_triage_triaged_and_backfill(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cx, "TRIAGE_SKIP_MAX", 0)  # the triage path itself; a triage of a few claims skips it (feature 430 T06), below
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
    (tmp_path / "t.txt").write_text("No claim is touched.\n")  # T92: an empty reply is unread, and refused
    assert cx.main(["--root", str(root), "triaged", "--bundle", str(tmp_path / "t"), "--reply", str(tmp_path / "t.txt")]) == 0
    assert "0 of 1 sent on to impl-drift" in capsys.readouterr().out
    assert [k for k, _w in cx.owed(cx.current(skill), cx.load_index(root / cx.INDEX), skill / cx.QUESTIONS.split("/", 3)[-1], cx.load_store(root / cx.STORE))] == [FAR]
    assert cx.main(["--root", str(root), "backfill"]) == 0 and "row(s) given the pages" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "report"]) == 0
    _tree(root, MOD, PAGE.replace("5 ft", "7 ft"))
    monkeypatch.setattr(cx, "TRIAGE_SKIP_MAX", 3)
    capsys.readouterr()
    assert cx.main(["--root", str(root), "triage", "--out", str(tmp_path / "small")]) == 0
    said = capsys.readouterr().out
    assert "goes straight to impl-drift" in said and (tmp_path / "small" / "units.json").is_file(), "feature 430 T06: one claim is no triage"


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


def test_a_withdrawn_block_that_never_reached_a_commit_is_shown_not_forced(tmp_path: pathlib.Path) -> None:
    """Feature 375 T04, the defect 372's wave 108 met: a bullet drafted and withdrawn before any commit. The claims were checked
    with it on the page; the page went back to its committed words; the triage reply named no claim, and every claim citing the
    page was still owed in full, because no version in the page's history held the withdrawn block's words. The snapshot's own
    text is now kept (`keep_texts`) and read first."""
    root = _repo(tmp_path)
    _tree(root, MOD, PAGE)
    _commit(root, "the page as committed")
    drafted = PAGE.replace("<p>Each lane", "<p>A drafted rule.</p>\n<p>Each lane")
    skill, index, store = _checked_at(root, drafted)
    _tree(root, MOD, PAGE)  # withdrawn: the page is back to its committed words
    cur = cx.current(skill)
    manifest = cx.triage_bundle(cur, index, store, [SHARE, FAR], skill / QDIR, tmp_path / "t").read_text()
    data = json.loads((tmp_path / "t" / "triage.json").read_text())
    assert data["forced"] == [], "the withdrawn block is shown from its kept text, so nothing is owed in full"
    assert "Removed blocks (no longer on the page):\n\n> A drafted rule." in manifest
    out, msgs = cx.record_triage(index, data["units"], "No claims are touched, so I have no `TOUCHES` lines.\n", "d", data["forced"])
    assert msgs == [] and "triage" not in out[SHARE] and "triage" not in out[FAR]


def _checked_at(root: pathlib.Path, page: str) -> tuple[pathlib.Path, dict, dict]:
    """`_checked` at `page`, with the snapshot texts kept as `claims-checked` keeps them."""
    skill = _tree(root, MOD, page)
    cur = cx.current(skill)
    cx.bundle(root, cur, sorted(cur), root / "b")
    blocks = json.loads((root / "b" / "blocks.json").read_text())
    units = json.loads((root / "b" / "units.json").read_text())
    reply = "".join(f"VERDICT {k} IN-STEP - ok {'[§1]' if k == SHARE else '[§3]' if k == FAR else '[§]'}\n" for k in units)
    index, _msgs = cx.record({}, units, reply, "d", blocks["numbered"])
    assert cx.keep_texts(skill / QDIR, units) == 1
    assert cx.keep_texts(skill / QDIR, units) == 0, "kept once"
    return skill, index, blocks["snapshots"]


def test_the_triage_reads_only_lines_that_open_with_touches(tmp_path: pathlib.Path) -> None:
    """FR-005(a): a prose mention or a mid-line TOUCHES names nothing; a line that opens with it (bare, or in backticks) does."""
    skill, index, _store = _checked(tmp_path)
    units = {SHARE: {"research": "r", "pages": {}}, FAR: {"research": "r", "pages": {}}}
    reply = f"The other claims are cleared; nothing TOUCHES {FAR} - here.\n- TOUCHES {FAR} - a bulleted line\n`TOUCHES {SHARE} - in backticks`\n"
    out, msgs = cx.record_triage(index, units, reply, "d")
    assert msgs == [f"touched: {SHARE} - in backticks"] and "triage" not in out[FAR]
    assert cx.kept_text(skill / QDIR, "no-such-snapshot") == ""


WALLS = "docs/buildings.md::Walls#walls"
DOC = "## Walls\n<!-- Research: walls - CONVENTION -->\n\nA wall stands round the yard.\n\n| part | band |\n|---|---|\n| wall | 3 ft |\n| gate | 8 ft |\n"


def _checked_doc(root: pathlib.Path) -> tuple[pathlib.Path, dict, dict]:
    """A tree whose procedure section `Walls` carries one claim and a table, its claims recorded from a bundle."""
    skill = _tree(root, MOD, PAGE)
    (skill / "docs" / "buildings.md").write_text(DOC)
    cur = cx.current(skill)
    cx.bundle(root, cur, sorted(cur), root / "b")
    blocks = json.loads((root / "b" / "blocks.json").read_text())
    units = json.loads((root / "b" / "units.json").read_text())
    assert units[WALLS]["section"] == cur[WALLS].unit.core and cur[WALLS].unit.core in blocks["snapshots"]
    reply = "".join(f"VERDICT {k} IN-STEP - ok [§]\n" for k in units)
    index, _msgs = cx.record({}, units, reply, "d", blocks["numbered"])
    assert index[WALLS]["section"] == cur[WALLS].unit.core
    return skill, index, {**blocks["snapshots"]}


def test_a_section_edit_off_a_claims_line_owes_a_triage_of_the_changed_rows(tmp_path: pathlib.Path) -> None:
    """Feature 375 FR-002 (372's wave 106: impl-drift over 73, 105 and 105 claims for edits off their lines): a regenerated
    table row re-owes no claim in full; the triage shows only the row that changed, and clearing records the section."""
    root = _repo(tmp_path)
    skill, index, store = _checked_doc(root)
    _commit(root, "the section as checked")
    assert dict(cx.owed(cx.current(skill), index, skill / QDIR, store)).get(WALLS) is None
    (skill / "docs" / "buildings.md").write_text(DOC.replace("| gate | 8 ft |", "| gate | 10 ft |"))
    cur = cx.current(skill)
    assert dict(cx.owed(cur, index, skill / QDIR, store))[WALLS] == cx.SECTION_TRIAGE
    assert WALLS not in cx.judged(cx.owed(cur, index, skill / QDIR, store))
    manifest = cx.triage_bundle(cur, index, store, [WALLS], skill / QDIR, tmp_path / "t").read_text()
    assert "## docs/buildings.md::Walls (a procedure section" in manifest and "> | gate | 10 ft |" in manifest
    assert "Removed blocks (no longer in the section):\n\n> | gate | 8 ft |" in manifest and "| wall | 3 ft |" not in manifest
    data = json.loads((tmp_path / "t" / "triage.json").read_text())
    assert data["forced"] == [] and data["units"][WALLS]["section"] == cur[WALLS].unit.core
    cleared, _ = cx.record_triage(index, data["units"], "", "d2")
    assert cleared[WALLS]["section"] == cur[WALLS].unit.core
    assert WALLS not in dict(cx.owed(cur, cleared, skill / QDIR, {**store, **data["snapshots"]}))
    (skill / "docs" / "buildings.md").write_text(DOC.replace("walls - CONVENTION", "walls - GUESS"))
    assert dict(cx.owed(cx.current(skill), index, skill / QDIR, store))[WALLS] == "code changed", "its own line moved: owed in full"


def test_a_removed_row_no_history_shows_forces_the_section_claim(tmp_path: pathlib.Path) -> None:
    skill, index, store = _checked_doc(tmp_path)  # no repository: no history to read the removed row back from
    (skill / "docs" / "buildings.md").write_text(DOC.replace("| gate | 8 ft |\n", ""))
    cur = cx.current(skill)
    cx.triage_bundle(cur, index, store, [WALLS], skill / QDIR, tmp_path / "t")
    assert json.loads((tmp_path / "t" / "triage.json").read_text())["forced"] == [WALLS]


def test_the_section_backfill_rekeys_current_rows_and_leaves_owed_ones_owed(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path, MOD, PAGE)
    (skill / "docs" / "buildings.md").write_text(DOC)
    cur = cx.current(skill)
    cl = cx.engine(pathlib.Path(cx.__file__).resolve().parents[2])
    old = cl._sha(cur[WALLS].unit.core + "\x1f" + cur[WALLS].claim.normalized())
    index = {WALLS: {"verdict": "IN-STEP", "code": old, "research": ""}, PRECINCT: {"verdict": "IN-STEP", "code": "stale", "research": ""}}
    assert dict(cx.owed(cur, index))[WALLS] == "code changed", "the new fingerprint alone would owe it"
    store: dict[str, list[str]] = {}
    assert cx.backfill_sections(cur, index, store) == 1
    assert WALLS not in dict(cx.owed(cur, index)) and dict(cx.owed(cur, index))[PRECINCT] == "code changed"
    assert store[cur[WALLS].unit.core] and cx.backfill_sections(cur, index, store) == 0, "once"


PRECINCT = "docs/building-programs.md::Country shrine (a village district's shrine)#precinct"


def test_a_triage_of_a_section_and_a_page_together_shows_both(tmp_path: pathlib.Path) -> None:
    """Feature 374: the sections' loop bound its removed blocks to `gone`, the pages' map, so a triage owing a section and a
    page at once failed with `'list' object has no attribute 'get'`."""
    root = _repo(tmp_path)
    skill, index, store = _checked_doc(root)
    _commit(root, "the section and the page as checked")
    (skill / "docs" / "buildings.md").write_text(DOC.replace("| gate | 8 ft |", "| gate | 10 ft |"))
    _tree(root, MOD, PAGE.replace("5 ft", "6 ft"))
    cur = cx.current(skill)
    owed = dict(cx.owed(cur, index, skill / QDIR, store))
    assert owed[WALLS] == cx.SECTION_TRIAGE and SHARE in owed
    manifest = cx.triage_bundle(cur, index, store, [WALLS, SHARE], skill / QDIR, tmp_path / "t").read_text()
    assert "## docs/buildings.md::Walls (a procedure section" in manifest and "> Each lane is 6 ft." in manifest


def test_a_relabel_a_mislabeled_verdict_prescribed_owes_no_new_round(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fix on ask:t01-claim-labels (feature 385): a claim whose unit changed only in its
    `Research:` lines owes nothing when its own text is unchanged, or when its last verdict was MISLABELED - the relabel that
    verdict prescribed. A label rewritten after an IN-STEP verdict, or any change to the unit's body, still owes a round."""
    skill, index, store = _checked(tmp_path)
    qdir = skill / QDIR
    assert index[FAR].get("body") and index[FAR].get("claim"), "a recorded row keeps the body and the claim"
    mod = next(skill.rglob("rows.py"))
    relabeled = mod.read_text().replace("0033-row-villages-resson.html\n    \"\"\"", "0033-row-villages-resson.html: the far row\n    \"\"\"")
    mod.write_text(relabeled)
    assert dict(cx.owed(cx.current(skill), index, qdir, store)).get(FAR) == "code changed", "an IN-STEP label rewritten still owes"
    index[FAR]["verdict"] = "MISLABELED"
    assert FAR not in dict(cx.owed(cx.current(skill), index, qdir, store)), "the relabel its MISLABELED verdict prescribed owes nothing"
    mod.write_text(relabeled.replace("return x * SHARE", "return x * SHARE * 2"))
    assert dict(cx.owed(cx.current(skill), index, qdir, store)).get(FAR) == "code changed", "a change to the body owes a round"


def test_the_gate_takes_a_relabel_as_the_answer_to_its_mislabeled(tmp_path: pathlib.Path) -> None:
    """Feature 385 T23 (plan D45; found by T05): `owed` asks nothing of a relabel its MISLABELED verdict prescribed, so the gate
    must not refuse that verdict - it did, as an introduced finding no command could clear. Its text unchanged, it still refuses."""
    skill, index, store = _checked(tmp_path)
    index[FAR]["verdict"] = "MISLABELED"
    cur = cx.current(skill)
    assert not cx.relabel_answered(index[FAR], cur[FAR], skill), "the text unchanged: not answered"
    assert cx.classify(cur, index, {}, {}, skill / QDIR)[0], "an unanswered MISLABELED on code the base lacks is introduced"
    mod = next(skill.rglob("rows.py"))
    relabeled = mod.read_text().replace("0033-row-villages-resson.html\n    \"\"\"", "0033-row-villages-resson.html: the far row\n    \"\"\"")
    mod.write_text(relabeled)
    cur = cx.current(skill)
    assert cx.relabel_answered(index[FAR], cur[FAR], skill), "the prescribed relabel answers it"
    assert FAR not in " ".join(cx.classify(cur, index, {}, {}, skill / QDIR, frozenset(), frozenset({FAR}))[0])
    mod.write_text(relabeled.replace("return x * SHARE", "return x * SHARE * 2"))
    assert not cx.relabel_answered(index[FAR], cx.current(skill)[FAR], skill), "the body moved: judged again, not answered"


def test_claims_checked_at_different_versions_each_see_their_own_changes(tmp_path: pathlib.Path) -> None:
    """Feature 385 T02 (plan D11): the triage listed one page's changed blocks once for every claim citing it, so a claim
    checked at a later version was shown changes it had already been checked against. Each version is now its own section."""
    skill, index, store = _checked(tmp_path)
    qdir = skill / QDIR
    page = qdir / "0033-row-villages-resson.html"
    page.write_text(page.read_text().replace("Each lane is 5 ft.", "Each lane is 6 ft."))
    mid, blocks = cx.page_blocks(page.name, qdir, {})
    store = {**store, mid: [d for d, _w in blocks]}
    index[FAR]["pages"] = {page.name: mid}  # far_row re-checked at the 6 ft version
    page.write_text(page.read_text().replace("Farms face the street.", "Farms face the lane."))
    manifest = cx.triage_bundle(cx.current(skill), index, store, [SHARE, FAR], qdir, tmp_path / "t").read_text()
    sections = [s for s in manifest.split("## ")[1:] if s.startswith("research/questions/0033")]
    assert len(sections) == 2, "one section per version checked at"
    far = next(s for s in sections if FAR in s)
    share = next(s for s in sections if SHARE in s)
    assert "> Farms face the lane." in far and "6 ft" not in far.split("Claims citing it")[0], "far_row was checked at 6 ft"
    assert "> Farms face the lane." in share and "> Each lane is 6 ft." in share, "SHARE was checked before both changes"


def test_a_claim_the_triage_has_nothing_to_show_is_owed_in_full(tmp_path: pathlib.Path) -> None:
    """Feature 385 T03: two claims relabeled to cite pages their last check never read were owed a triage, but no page of theirs
    had moved, so the bundle showed nothing and the agent could clear nothing - they go on to impl-drift in full."""
    skill, index, store = _checked(tmp_path)
    cur = cx.current(skill)
    cx.triage_bundle(cur, index, store, [SHARE], skill / QDIR, tmp_path / "t")
    assert json.loads((tmp_path / "t" / "triage.json").read_text())["forced"] == [SHARE]


def test_a_triage_reply_is_read_from_a_transcript_and_an_unread_one_clears_nothing(tmp_path: pathlib.Path) -> None:
    """Feature 385 T92: T31's `make claims-triaged` on an agent's `.output` cleared all 281 claims, 18 of them TOUCHES."""
    line = "TOUCHES l7r/x.py::f#a - its block moved"
    rec = {"type": "assistant", "message": {"content": [{"type": "text", "text": line}]}}
    out = tmp_path / "agent.output"
    out.write_text(json.dumps({"type": "user", "message": {"content": "go"}}) + "\n" + json.dumps(rec) + "\n")
    assert cx.claims_triage.triage_reply(out) == line
    plain = tmp_path / "reply.md"
    plain.write_text(line + "\n")
    assert cx.claims_triage.triage_reply(plain).strip() == line
    (tmp_path / "empty.output").write_text("")
    assert cx.claims_triage.triage_reply(tmp_path / "empty.output") == ""


def test_a_code_change_owes_a_triage_of_its_hunks_and_clears_the_claims_it_does_not_touch(tmp_path: pathlib.Path) -> None:
    """Feature 385 T116 (D133): one edit to `web.stage_web` re-owed its 20 claims in full, 17 of them unaffected. A code change
    owes its claims a triage of the unit's diff against origin/main; a claim the triage does not name is cleared at its new
    code; a claim whose own line was rewritten, or a unit with no hunk to show, is owed in full."""
    root = _repo(tmp_path)
    skill, index, store = _checked(root)
    _commit(root, "as checked")
    cx.claims_triage._git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    (skill / "l7r/diagram/hamletgen/rows.py").write_text(MOD.replace("x * SHARE", "x * SHARE * 2"))
    cur = cx.current(skill)
    assert dict(cx.owed(cur, index, skill / QDIR, store)) == {FAR: cx.CODE_TRIAGE}
    assert cx.judged(cx.owed(cur, index, skill / QDIR, store)) == []
    manifest = cx.triage_bundle(cur, index, store, [FAR], skill / QDIR, tmp_path / "t").read_text()
    assert "## l7r/diagram/hamletgen/rows.py::far_row (a unit of code" in manifest and "+    return x * SHARE * 2" in manifest
    data = json.loads((tmp_path / "t" / "triage.json").read_text())
    assert data["forced"] == [] and data["units"][FAR]["code"] == cur[FAR].code
    cleared, _ = cx.record_triage(index, data["units"], "", "d2")
    assert FAR not in dict(cx.owed(cur, cleared, skill / QDIR, store)), "cleared at its new code"
    touched, _ = cx.record_triage(index, data["units"], f"TOUCHES {FAR} - the share doubled", "d2")
    assert dict(cx.owed(cur, touched, skill / QDIR, store))[FAR] == "code changed", "a named claim goes on to impl-drift"
    # the claim's own line rewritten with the code: known from the row's claim text, or else seen among the hunk's added lines
    (skill / "l7r/diagram/hamletgen/rows.py").write_text(MOD.replace("x * SHARE", "x * SHARE * 2").replace(f"    Research: dry share - {Q}", "    Research: dry share - GUESS"))
    cur = cx.current(skill)
    assert dict(cx.owed(cur, index, skill / QDIR, store))[FAR] == "code changed", "its text is known rewritten"
    bare = {k: {f: v for f, v in r.items() if f != "claim"} for k, r in index.items()}
    assert dict(cx.owed(cur, bare, skill / QDIR, store))[FAR] == cx.CODE_TRIAGE
    cx.triage_bundle(cur, bare, store, [FAR], skill / QDIR, tmp_path / "t")
    assert json.loads((tmp_path / "t" / "triage.json").read_text())["forced"] == [FAR], "its line is among the added lines"
    # landed before its check: no hunk to read, owed in full
    (skill / "l7r/diagram/hamletgen/rows.py").write_text(MOD.replace("x * SHARE", "x * SHARE * 2"))
    _commit(root, "landed")
    cx.claims_triage._git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    cx.triage_bundle(cx.current(skill), index, store, [FAR], skill / QDIR, tmp_path / "t")
    assert json.loads((tmp_path / "t" / "triage.json").read_text())["forced"] == [FAR]

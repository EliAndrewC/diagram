"""`scripts/record/claims.py` - the claims index: owed, bundle, record, report and the push's verdict (feature 316).

The GM, 2026-10-02: *"our tooling should be able to evaluate whether or not an annotated thing has been edited since the last
time a subagent check ran on it"*, and the push rule the GM accepted: an owed row blocks, a finding the change introduces blocks,
a pre-existing finding warns. One case per acceptance scenario of spec US2-US4, on a small engine tree in tmp.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


cx = _load("_claims")
Q = "research/questions/0033-row-villages-resson.html"
PAGE = '<h2 id="row-villages-resson">Row villages</h2>\n<p class="intro">Why asked.</p>\n<p>Farms face the street.</p>\n'
MOD = f'''"""Rows.

Research: plumbing - NONE
"""

SHARE = 0.5
"""Research: dry share - {Q}"""


def far_row(x):
    """Lay the far row.

    Research: dry share - {Q}
    """
    return x * SHARE


def helper(y):
    return y + 1
'''


def _tree(root: pathlib.Path, mod: str = MOD, page: str = PAGE) -> pathlib.Path:
    skill = root
    (skill / "l7r" / "diagram" / "hamletgen").mkdir(parents=True, exist_ok=True)
    (skill / "l7r" / "diagram" / "hamletgen" / "__init__.py").write_text("from . import rows\n")
    (skill / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(mod)
    (skill / "research" / "questions").mkdir(parents=True, exist_ok=True)
    (skill / "research" / "questions" / "0033-row-villages-resson.html").write_text(page)
    (skill / "docs").mkdir(parents=True, exist_ok=True)
    (skill / "docs" / "buildings.md").write_text("## Walls\n<!-- Research: walls - CONVENTION -->\n")
    (skill / "docs" / "building-programs.md").write_text("### Country shrine (a village district's shrine)\n<!-- Research: precinct - UNRESEARCHED -->\n")
    return skill


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _repo(tmp: pathlib.Path) -> pathlib.Path:
    _tree(tmp)
    _git(tmp, "init", "-q", "-b", "main")
    _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "root")
    return tmp


def _commit(root: pathlib.Path, msg: str = "c") -> None:
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)


def _all_in_step(root: pathlib.Path) -> dict[str, dict[str, str]]:
    cur = cx.current(root)
    return {k: {"verdict": "IN-STEP", "code": r.code, "core": r.unit.core, "research": r.research, "date": "d", "note": ""} for k, r in cur.items()}


def test_every_claim_is_a_row_including_inherited_and_procedure_claims(tmp_path: pathlib.Path) -> None:
    cur = cx.current(_tree(tmp_path))
    keys = sorted(cur)
    assert keys == sorted(
        [
            "l7r/diagram/hamletgen/rows.py::SHARE#dry share",
            "l7r/diagram/hamletgen/rows.py::far_row#dry share",
            "l7r/diagram/hamletgen/rows.py::helper#plumbing",
            "docs/buildings.md::Walls#walls",
            "docs/building-programs.md::Country shrine (a village district's shrine)#precinct",
        ]
    )
    assert cur["docs/buildings.md::Walls#walls"].research == "" and cur["l7r/diagram/hamletgen/rows.py::far_row#dry share"].research


def test_owed_says_new_code_changed_and_research_changed_and_nothing_for_prose_or_the_intro(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path)
    index = _all_in_step(tmp_path)
    assert all(why == "new" for _k, why in cx.owed(cx.current(skill), {}))
    assert cx.owed(cx.current(skill), index) == []
    _tree(tmp_path, MOD.replace("Lay the far row.", "Lay the far row, said otherwise.").replace("    return x * SHARE", "    # a comment\n    return x*SHARE"))
    assert cx.owed(cx.current(skill), index) == [], "prose, a comment and formatting owe nothing"
    _tree(tmp_path, page=PAGE.replace("Why asked.", "Why it is asked."))
    assert cx.owed(cx.current(skill), index) == [], "the intro is not a finding"
    _tree(tmp_path, MOD.replace("x * SHARE", "x * SHARE * 2"))
    assert cx.owed(cx.current(skill), index) == [("l7r/diagram/hamletgen/rows.py::far_row#dry share", cx.CODE_TRIAGE)]
    _tree(tmp_path, MOD.replace("SHARE = 0.5", "SHARE = 0.4"))
    assert sorted(k.rsplit("::", 1)[1] for k, _w in cx.owed(cx.current(skill), index)) == ["SHARE#dry share", "far_row#dry share"]
    _tree(tmp_path, page=PAGE.replace("face the street", "face south"))
    assert [(k.rsplit("::", 1)[1], w) for k, w in cx.owed(cx.current(skill), index)] == [("SHARE#dry share", "research changed"), ("far_row#dry share", "research changed")]


def test_a_new_unit_with_only_the_inherited_none_is_named_before_the_check(tmp_path: pathlib.Path) -> None:
    """Feature 405 T37 (D11): T14's new `_walk_in` inherited its module's NONE and its first impl-drift round spent itself saying
    so. `claims-owed` names such a unit while it is new; an own claim, or a unit already checked, is not named."""
    skill = _tree(tmp_path)
    cur = cx.current(skill)
    notes = cx.inherited_none(cur, cx.owed(cur, {}))
    assert notes == [
        "claims-owed: l7r/diagram/hamletgen/rows.py::helper is new and carries only its module's NONE - if it decides anything about the place, give it its own `Research:` line before the check"
    ]
    assert cx.inherited_none(cur, cx.owed(cur, _all_in_step(tmp_path))) == [], "checked: no longer new"


def test_a_missing_question_fingerprints_as_missing(tmp_path: pathlib.Path) -> None:
    assert cx.research_fp([Q], tmp_path) == cx.research_fp([Q], tmp_path, {}) != ""
    assert cx.research_fp([], tmp_path) == ""


def test_the_bundle_holds_each_unit_its_claims_and_the_cited_pages(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path)
    (skill / "research" / "questions" / "0033-row-villages-resson.drawing.html").write_text("<h2>How our maps draw</h2>\n<!-- x -->\n")
    cur = cx.current(skill)
    keys = sorted(cur)
    manifest = cx.bundle(tmp_path, cur, keys, tmp_path / "b").read_text()
    assert "## UNIT l7r/diagram/hamletgen/rows.py::far_row (function" in manifest
    assert "return x * SHARE" in manifest and "constants it reads: `SHARE=Constant(value=0.5)`" in manifest
    assert '"""Research: dry share' in manifest, "a constant brings its claim literal"
    assert "(inherited from the module docstring)" in manifest
    assert "`questions/0033-row-villages-resson.html.txt` - Row villages" in manifest and "Farms face the street." not in manifest
    q = (tmp_path / "b" / "questions" / "0033-row-villages-resson.html.txt").read_text()
    assert q.startswith("# Row villages") and "[intro] Why asked." in q and "Farms face the street." in q
    assert not (tmp_path / "b" / "questions" / "0033-row-villages-resson.drawing.html.txt").exists(), "only what a claim cites"
    units = json.loads((tmp_path / "b" / "units.json").read_text())
    assert set(units) == set(keys) and units[keys[0]]["code"] == cur[keys[0]].code
    cx.bundle(tmp_path, cur, keys[:1], tmp_path / "b")  # a second build replaces the first
    assert len(json.loads((tmp_path / "b" / "units.json").read_text())) == 1


def test_a_bundle_carries_the_context_and_the_pages_a_re_check_asks_for(tmp_path: pathlib.Path) -> None:
    """Feature 374: a CANNOT-TELL verdict asked for a helper's body or a page no claim cites; WITH= and PAGES= add them."""
    skill = _tree(tmp_path)
    (skill / "research" / "questions" / "0033-row-villages-resson.drawing.html").write_text("<h2>How our maps draw</h2>\n<p>Drawn so.</p>\n")
    cur = cx.current(skill)
    keys = sorted(cur)
    ctx = ["l7r/diagram/hamletgen/rows.py::far_row", "l7r/diagram/hamletgen/rows.py::SHARE"]
    added = "research/questions/0033-row-villages-resson.drawing.html"  # the pointer form, as a claim names it, or a bare name
    manifest = cx.bundle(skill, cur, keys, tmp_path / "b", ctx, [added]).read_text()
    assert "## CONTEXT l7r/diagram/hamletgen/rows.py::far_row" in manifest and "SHARE = 0.5" in manifest
    assert (tmp_path / "b" / "questions" / "0033-row-villages-resson.drawing.html.txt").exists(), "an added page"
    with pytest.raises(ValueError, match="no question file 9999-none.html"):  # a page named and not found is never skipped
        cx.bundle(skill, cur, keys, tmp_path / "b2", ctx, ["9999-none.html"])
    with pytest.raises(ValueError):
        cx.context_source(skill, "l7r/diagram/hamletgen/rows.py::nothing")


def test_record_writes_verdicts_refuses_strangers_and_keeps_unclaimed_rows_until_rechecked() -> None:
    units = {"p::f#a": {"code": "c1", "core": "k1", "research": "r1", "uid": "p::f"}, "p::f#b": {"code": "c2", "core": "k1", "research": "", "uid": "p::f"}}
    reply = "claims: 2\nVERDICT p::f#a DRIFTED - the share is fixed\n`VERDICT p::f#zz IN-STEP - x`\nUNCLAIMED p::f - the row count\nUNCLAIMED p::g - stray\n"
    out, msgs = cx.record({"old": {"verdict": "IN-STEP"}}, units, reply, "2026-10-02")
    assert out["p::f#a"] == {"verdict": "DRIFTED", "code": "c1", "core": "k1", "research": "r1", "date": "2026-10-02", "note": "the share is fixed"}
    assert "p::f#b" not in out and out["p::f#the row count"]["verdict"] == "UNCLAIMED" and "old" in out
    assert msgs == [
        "refused: `p::f#zz` is not a unit of this bundle",
        "no verdict for `p::f#b` - it stays owed",
        "UNCLAIMED p::f - the row count: write a claim for it, then check it",
        "refused: UNCLAIMED `p::g` is not a unit of this bundle",
    ]
    again, _ = cx.record(out, units, "VERDICT p::f#a IN-STEP - fixed\nVERDICT p::f#b IN-STEP - ok\n", "d")
    assert "p::f#the row count" not in again and again["p::f#a"]["verdict"] == "IN-STEP"


def test_the_report_counts_lists_findings_and_the_open_research(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path)
    index = _all_in_step(tmp_path)
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    index[k] |= {"verdict": "DRIFTED", "note": "296"}
    index["l7r/diagram/hamletgen/rows.py::helper#an unclaimed thing"] = {"verdict": "UNCLAIMED", "note": "n"}
    index["gone::x#y"] = {"verdict": "DRIFTED"}
    text = cx.report(cx.current(skill), index)
    assert text.startswith("claims: 5 in scope; IN-STEP 4, DRIFTED 1, UNCLAIMED 1; owed 0")
    assert f"DRIFTED        {k} - 296" in text and "gone::x" not in text
    assert "UNRESEARCHED claims (the open research): 1" in text


def test_a_finding_in_a_deferred_unit_is_reported_deferred(tmp_path: pathlib.Path) -> None:
    """Feature 328 amendment 8 (the GM 2026-10-07): a finding in code only the legacy hand-authored settlements run is DEFERRED,
    not DRIFTED - shown and counted so, and never a finding the push's gate classifies."""
    skill = _tree(tmp_path)
    index = _all_in_step(tmp_path)
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    index[k] |= {"verdict": "DRIFTED", "note": "296"}
    deferred = frozenset({k.rsplit("#", 1)[0]})
    text = cx.report(cx.current(skill), index, deferred=deferred)
    assert "IN-STEP 4, DEFERRED 1" in text and f"DEFERRED       {k} - 296" in text and "DRIFTED" not in text
    assert cx.classify(cx.current(skill), index, {}, {}, tmp_path, deferred) == ([], [], [])
    f = tmp_path / "deferred.json"
    f.write_text('{"why": "legacy", "units": ["a::b"], "keys": ["c::d#e"]}')
    assert cx.load_deferred(f) == frozenset({"a::b", "c::d#e"}) and cx.load_deferred(tmp_path / "none.json") == frozenset()
    assert cx.shown("c::d#e", "DRIFTED", frozenset({"c::d#e"})) == "DEFERRED" and cx.shown("c::d#f", "DRIFTED", frozenset({"c::d#e"})) == "DRIFTED"


def _row(cur: dict, key: str, verdict: str, **kw: str) -> dict[str, str]:
    r = cur[key]
    return {"verdict": verdict, "code": r.code, "core": r.unit.core, "research": r.research, "note": "n", **kw}


def test_classify_introduced_and_pre_existing(tmp_path: pathlib.Path) -> None:
    base_skill = _tree(tmp_path / "base")
    base = cx.current(base_skill)
    cores, bq = cx.base_cores(base_skill), base_skill / "research" / "questions"
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    # IN-STEP at the base, a finding now on the same code, claim and research - a re-judgment: carried (385 FR-013, round 2)
    assert cx.classify(base, {k: _row(base, k, "DRIFTED")}, {k: _row(base, k, "IN-STEP")}, cores, bq) == ([], [], [(k, f"DRIFTED        {k} - n")])
    # a finding at both ends, whatever changed: pre-existing
    head = cx.current(_tree(tmp_path / "head", MOD.replace("x * SHARE", "x * SHARE + 1")))
    assert cx.classify(head, {k: _row(head, k, "DRIFTED")}, {k: _row(base, k, "DRIFTED")}, cores, bq) == ([], [f"DRIFTED        {k} - n"], [])
    # no base row: untouched code and research is pre-existing; changed code is introduced
    assert cx.classify(base, {k: _row(base, k, "DRIFTED")}, {}, cores, bq)[0] == []
    assert cx.classify(head, {k: _row(head, k, "DRIFTED")}, {}, cores, bq)[0]
    # a rename with the code intact is pre-existing; a copy beside a live original is introduced
    renamed = cx.current(_tree(tmp_path / "ren", MOD.replace("def far_row", "def far_rows")))
    kr = k.replace("far_row#", "far_rows#")
    assert cx.classify(renamed, {kr: _row(renamed, kr, "MISLABELED")}, {}, cores, bq)[0] == []
    copied = cx.current(_tree(tmp_path / "copy", MOD + MOD[MOD.index("def far_row") :].split("def helper")[0].replace("def far_row", "def far_row2")))
    kc = k.replace("far_row#", "far_row2#")
    assert cx.classify(copied, {kc: _row(copied, kc, "MISLABELED")}, {}, cores, bq)[0]
    # the cited question's findings changed under a first finding on unchanged code: carried, not introduced (385 FR-013)
    moved = cx.current(_tree(tmp_path / "moved", page=PAGE.replace("face the street", "face south")))
    assert cx.classify(moved, {k: _row(moved, k, "DRIFTED")}, {}, cores, bq) == ([], [], [(k, f"DRIFTED        {k} - n")])
    # an IN-STEP row is no finding
    assert cx.classify(base, {k: _row(base, k, "IN-STEP")}, {}, cores, bq) == ([], [], [])


def test_a_finding_the_check_tags_outside_the_change_is_carried_not_refused(tmp_path: pathlib.Path) -> None:
    """Feature 405 T36 (D10): T14's claims round refused three findings on code T14 never changed, because the unit's code
    changed. The check tags such a finding `[outside the change]`; the gate carries it as a task when it is an UNCLAIMED decision
    or its claim is as the base had it - never one under a claim the change added or reworded, nor an untagged one."""
    base_skill = _tree(tmp_path / "base")
    base = cx.current(base_skill)
    cores, bq = cx.base_cores(base_skill), base_skill / "research" / "questions"
    head = cx.current(_tree(tmp_path / "head", MOD.replace("x * SHARE", "x * SHARE + 1")))
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    claim = head[k].claim.normalized()
    line = f"DRIFTED        {k} - n"
    was = {k: _row(base, k, "IN-STEP", claim=claim)}
    assert cx.classify(head, {k: _row(head, k, "DRIFTED", claim=claim)}, was, cores, bq)[0] == [line], "untagged: introduced"
    assert cx.classify(head, {k: {**_row(head, k, "DRIFTED", claim=claim), "outside": True}}, was, cores, bq) == ([], [], [(k, line)])
    assert cx.classify(head, {k: {**_row(head, k, "DRIFTED", claim="reworded"), "outside": True}}, was, cores, bq)[0] == [line]
    assert cx.classify(head, {k: {**_row(head, k, "DRIFTED", claim=claim), "outside": True}}, {}, cores, bq)[0] == [line], "a new claim"
    ku = "l7r/diagram/hamletgen/rows.py::far_row#the row laid twice"
    row = {"verdict": "UNCLAIMED", "code": head[k].code, "core": head[k].unit.core, "research": "", "note": "the row laid twice"}
    assert cx.classify(head, {ku: {**row, "outside": True}}, {}, cores, bq)[2] == [(ku, f"UNCLAIMED      {ku} - the row laid twice")]
    assert cx.classify(head, {ku: row}, {}, cores, bq)[0], "an untagged decision in changed code: introduced"


def test_the_bundle_marks_the_change_and_the_record_keeps_the_tag(tmp_path: pathlib.Path) -> None:
    """Feature 405 T36 (D10): the check sees which lines the change made, and what it tags outside them is kept on the row."""
    assert cx.mark_changed("a\nb\nc", 10, {11}) == "  a\n+ b\n  c"
    assert cx.mark_changed("a\nb", 10, {40}) == "a\nb", "a unit the change did not touch is shown as it is"
    assert cx.outside_tag("[outside the change] the grove band [§3]") == (True, "the grove band [§3]")
    assert cx.outside_tag("the grove band") == (False, "the grove band")
    k = "p.py::f#c"
    units = {k: {"code": "c1", "core": "k1", "research": "", "uid": "p.py::f"}}
    reply = f"VERDICT {k} DRIFTED - [outside the change] the fallback keeps the end [§]\nUNCLAIMED p.py::f - [outside the change] the band\n"
    out, _msgs = cx.record({}, units, reply, "2026-10-21")
    assert out[k]["outside"] is True and out[k]["note"] == "the fallback keeps the end"
    assert out["p.py::f#the band"]["outside"] is True
    out, _msgs = cx.record({}, units, f"VERDICT {k} IN-STEP - [outside the change] fine [§]\n", "2026-10-21")
    assert "outside" not in out[k], "only a finding carries the tag"
    # the lines the delta changed, against the merge base with origin/main, the working tree included
    repo = tmp_path / "repo"
    repo.mkdir()
    g = ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"]
    (repo / "m.py").write_text("a = 1\nb = 2\nc = 3\n")
    subprocess.run([*g, "init", "-q"], check=True)
    subprocess.run([*g, "add", "-A"], check=True)
    subprocess.run([*g, "commit", "-qm", "base"], check=True)
    subprocess.run([*g, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
    (repo / "m.py").write_text("a = 1\nb = 20\nc = 3\nd = 4\n")
    assert cx.changed_lines(repo) == {"m.py": {2, 4}}


def test_a_base_with_no_claims_at_all_makes_every_first_finding_on_untouched_code_pre_existing(tmp_path: pathlib.Path) -> None:
    # this feature's own landing: main holds the code but no claims - its units still have cores (the push once read
    # "no claim at the base" as "no unit at the base" and called every audit finding introduced)
    bare = MOD.replace("Research: plumbing - NONE\n", "").replace(f'"""Research: dry share - {Q}"""\n', "").replace(f"\n    Research: dry share - {Q}\n    ", "")
    base_skill = _tree(tmp_path / "base", bare)
    assert cx.current(base_skill) == {} or all("rows.py" not in k for k in cx.current(base_skill))
    head = cx.current(_tree(tmp_path / "head"))
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    intro, pre, _carried = cx.classify(head, {k: _row(head, k, "DRIFTED")}, {}, cx.base_cores(base_skill), base_skill / "research" / "questions")
    assert intro == [] and pre


def test_the_gate_refuses_owed_and_introduced_and_warns_pre_existing(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    assert any(r.startswith("owed (new)") for r in cx.gate(root)[0])
    cx.save_index(root / cx.INDEX, _all_in_step(root))
    _commit(root, "base")
    assert cx.gate(root) == ([], [])
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    idx = cx.load_index(root / cx.INDEX)
    idx[k]["verdict"] = "DRIFTED"
    cx.save_index(root / cx.INDEX, idx)
    refuse, warn = cx.gate(root)  # HEAD is the merge base (no origin/main): IN-STEP there, DRIFTED now on the same code
    assert (
        refuse
        == [f"carry: DRIFTED        {k} -  - a finding on code the change left unchanged: file it with `make task-start F=<n> T=<Txx>`, then `make claims-carry F=<n>` (make land files it itself)"]
        and warn == []
    )
    (root / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(MOD.replace("x * SHARE", "x * SHARE + 1"))
    cur = cx.current(root)
    idx[k] |= {"code": cur[k].code, "core": cur[k].unit.core}
    cx.save_index(root / cx.INDEX, idx)
    assert cx.gate(root)[0] == [f"introduced: DRIFTED        {k} - "]  # the code changed under it: introduced, as before
    _commit(root, "drift")
    assert cx.gate(root) == ([], [f"pre-existing: DRIFTED        {k} - "])


def test_a_page_edit_finding_on_unchanged_code_is_carried_not_introduced(tmp_path: pathlib.Path) -> None:
    """Feature 385 amendment 3 (the GM 2026-10-17, "Yes, please lock in option three."): a finding whose code and claim stand
    as at the base, surfaced only because its cited page changed, is CARRIED; changed code under the same page edit is still
    introduced, and a moved unit is never carried."""
    base_skill = _tree(tmp_path / "base")
    base = cx.current(base_skill)
    cores, bq = cx.base_cores(base_skill), base_skill / "research" / "questions"
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    edited = PAGE.replace("face the street", "face south")
    page = cx.current(_tree(tmp_path / "page", page=edited))
    # IN-STEP at the base, the page edited, the code and claim as they were: carried
    assert cx.classify(page, {k: _row(page, k, "DRIFTED")}, {k: _row(base, k, "IN-STEP")}, cores, bq)[2] == [(k, f"DRIFTED        {k} - n")]
    # the same page edit with the code changed too: introduced
    both = cx.current(_tree(tmp_path / "both", MOD.replace("x * SHARE", "x * SHARE + 1"), page=edited))
    assert cx.classify(both, {k: _row(both, k, "DRIFTED")}, {k: _row(base, k, "IN-STEP")}, cores, bq)[:3:2] == ([f"DRIFTED        {k} - n"], [])
    assert cx.classify(both, {k: _row(both, k, "DRIFTED")}, {}, cores, bq)[:3:2] == ([f"DRIFTED        {k} - n"], [])
    # a renamed unit under a page edit: never carried
    ren = cx.current(_tree(tmp_path / "ren", MOD.replace("def far_row", "def far_rows"), page=edited))
    kr = k.replace("far_row#", "far_rows#")
    assert cx.classify(ren, {kr: _row(ren, kr, "DRIFTED")}, {}, cores, bq)[2] == []


def _active(root: pathlib.Path, feature: str = "900-x", tasks: str = "- [ ] T01 the work [lands-open]\n      research: rendering\n") -> pathlib.Path:
    d = root / "specs" / feature
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks.md").write_text("# Tasks\n\n" + tasks + "- [ ] GM review (make gm-reviewed F=900) [lands-open]\n")
    (root / ".specify").mkdir(exist_ok=True)
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": f"specs/{feature}"}))
    return d


def test_the_gate_refuses_an_unfiled_carry_naming_the_command_and_lets_a_filed_one_through(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    cx.save_index(root / cx.INDEX, _all_in_step(root))
    d = _active(root)
    _commit(root, "base")
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    q = root / "research" / "questions" / "0033-row-villages-resson.html"
    q.write_text(PAGE.replace("face the street", "face south"))
    idx = cx.load_index(root / cx.INDEX)
    for key, row in cx.current(root).items():  # every claim on the page re-checked against its edit; one comes back DRIFTED
        idx[key]["research"] = row.research
    idx[k]["verdict"] = "DRIFTED"
    cx.save_index(root / cx.INDEX, idx)
    refuse, _warn = cx.gate(root)
    assert refuse == [f"carry: DRIFTED        {k} -  - a finding on code the change left unchanged: file it with `make claims-carry F=900` (make land files it itself)"]
    # filing into another feature is refused; into the active one, a new box before the GM-review box
    other = root / "specs" / "901-y"
    other.mkdir()
    (other / "tasks.md").write_text("- [ ] T01 x [lands-open]\n")
    assert cx.main(["--root", str(root), "carry", "--feature", "901"]) == 2
    assert cx.main(["--root", str(root), "carry", "--feature", "900"]) == 0
    text = (d / "tasks.md").read_text()
    assert (
        f"- [ ] T02 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: {k} [lands-open]\n      research: rendering\n- [ ] GM review"
        in text
    )
    refuse, warn = cx.gate(root)
    assert refuse == [] and warn == [f"carried (900-x T02): DRIFTED        {k} - "]
    assert cx.main(["--root", str(root), "carry", "--feature", "900"]) == 0  # nothing left unfiled: writes nothing
    assert (d / "tasks.md").read_text() == text
    # ticking the task un-files the key: it refuses again
    (d / "tasks.md").write_text(text.replace("- [ ] T02", "- [x] T02"))
    assert cx.gate(root)[0][0].startswith("carry: ")
    # with T=, into an existing open box's words
    (d / "tasks.md").write_text(text.replace("- [ ] T02", "- [x] T02"))
    assert cx.main(["--root", str(root), "carry", "--feature", "900", "--task", "T01"]) == 0
    assert f"- [ ] T01 the work; carried by the claims gate (385 FR-013): {k} [lands-open]" in (d / "tasks.md").read_text()
    assert cx.gate(root)[0] == []
    assert cx.main(["--root", str(root), "carry", "--feature", "900", "--task", "T02"]) == 0  # nothing unfiled


def test_a_landing_with_no_engine_code_files_its_carries_into_the_claims_feature(tmp_path: pathlib.Path) -> None:
    """The GM, 2026-10-26: "a finding carried by a landing that changes no engine code should go to 405 instead" - feature 422,
    a research landing, was held open on five engine findings while 405 was on hold. An engine delta still files into its own."""
    root = _repo(tmp_path)
    cx.save_index(root / cx.INDEX, _all_in_step(root))
    d = _active(root)
    claims = _active(root, "405-claims")
    _active(root, "900-x")  # ...the landing's feature stays the active one
    _commit(root, "base")
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    q = root / "research" / "questions" / "0033-row-villages-resson.html"
    q.write_text(PAGE.replace("face the street", "face south"))
    idx = cx.load_index(root / cx.INDEX)
    for key, row in cx.current(root).items():
        idx[key]["research"] = row.research
    idx[k]["verdict"] = "DRIFTED"
    cx.save_index(root / cx.INDEX, idx)
    assert cx.gate(root)[0] == [f"carry: DRIFTED        {k} -  - a finding on code the change left unchanged: file it with `make claims-carry F=405` (make land files it itself)"]
    assert cx.main(["--root", str(root), "carry", "--feature", "900"]) == 0  # the landing names itself, as make land does
    assert "Carried by the claims gate" not in (d / "tasks.md").read_text()
    assert (
        f"- [ ] T02 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: {k} [lands-open]"
        in (claims / "tasks.md").read_text()
    )
    assert cx.gate(root) == ([], [f"carried (405-claims T02): DRIFTED        {k} - "])
    # an engine path in the delta: the feature being landed again
    (root / "l7r" / "diagram" / "hamletgen" / "other.py").write_text("x = 1\n")
    assert cx.gate(root)[0][0].endswith("file it with `make claims-carry F=900` (make land files it itself)")
    assert cx.main(["--root", str(root), "carry", "--feature", "405"]) == 2


def test_a_verdict_line_that_cannot_be_recorded_is_refused_aloud(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The round arbiter's fix on hour:385-approach-checklist@29: a path missing `diagram/`, `UNRESEARCHED IN-STEP` and a note's
    pointer to `0246-...lanes.html` (no `.drawing`) were each dropped with a quiet message, or found only by `make done`."""
    (tmp_path / "research/questions").mkdir(parents=True)
    (tmp_path / "research/questions/0246-x.drawing.html").write_text("")
    units = {"l7r/a.py::f#a": {}, "l7r/a.py::f#b": {}, "l7r/a.py::f#c": {}}
    reply = "\n".join(
        [
            "VERDICT l7r/a.py::f#a IN-STEP - ok, research/questions/0246-x.drawing.html",
            "VERDICT a.py::f#a IN-STEP - its path missing",
            "VERDICT l7r/a.py::f#b UNRESEARCHED IN-STEP - two tokens",
            "VERDICT l7r/a.py::f#c DRIFTED - see research/questions/0246-x.html",
            "UNCLAIMED l7r/a.py::f - kept",
        ]
    )
    kept, bad = cx.claims_triage.vet(reply, units, tmp_path, cx._VERDICT)
    assert kept.splitlines() == [reply.splitlines()[0], reply.splitlines()[-1]]
    assert [b.split(":")[0] for b in bad] == ["not a claim of this bundle", "not a claim of this bundle", "no such question file"]
    assert "REFUSED line" in capsys.readouterr().err


def test_a_refused_bundle_build_leaves_no_bundle_behind(tmp_path: pathlib.Path) -> None:
    """The round arbiter's fix on hour:385-approach-checklist@31: twice an impl-drift sent beside a refused `make claims-bundle`
    read the bundle the step before had left in the same directory, and judged claims nobody had asked about."""
    root = _repo(tmp_path)
    out = tmp_path / "b"
    assert cx.main(["--root", str(root), "bundle", "--owed", "--out", str(out)]) == 0 and (out / "MANIFEST.md").is_file()
    assert cx.main(["--root", str(root), "bundle", "--units", "nope", "--out", str(out)]) == 2
    assert not (out / "MANIFEST.md").exists(), "the refused build cleared the directory a check would read"


def test_the_command_line(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    assert cx.main(["--root", str(root), "owed"]) == 0 and "claims-owed: 5 claim(s) in 3 file(s)" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "bundle", "--units", "nope"]) == 2
    assert cx.main(["--root", str(root), "bundle", "--owed", "--out", str(tmp_path / "b")]) == 0
    units = json.loads((tmp_path / "b" / "units.json").read_text())
    # feature 385 T94: a transcript's last reply is what is recorded; an empty one is refused and writes nothing
    reply = tmp_path / "agent.output"
    reply.write_text("")
    assert cx.main(["--root", str(root), "record", "--bundle", str(tmp_path / "b"), "--reply", str(reply)]) == 2
    assert "claims-checked: refused - no reply text" in capsys.readouterr().err
    text = "".join(f"VERDICT {k} IN-STEP - ok\n" for k in units)
    reply.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}) + "\n")
    assert cx.main(["--root", str(root), "record", "--bundle", str(tmp_path / "b"), "--reply", str(reply)]) == 0
    assert "5 of 5 recorded" in capsys.readouterr().out
    stranger = tmp_path / "stranger.txt"
    stranger.write_text("VERDICT l7r/nope.py::f#x IN-STEP - a stranger\n")
    assert cx.main(["--root", str(root), "record", "--bundle", str(tmp_path / "b"), "--reply", str(stranger)]) == 3, "a refused line"
    assert "REFUSED line" in capsys.readouterr().err
    assert cx.main(["--root", str(root), "owed"]) == 0 and "no claim is owed" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "bundle", "--module", "hamletgen/rows.py"]) == 3, "not owed, no reason"
    assert cx.main(["--root", str(root), "bundle", "--module", "hamletgen/rows.py", "--reason", "a deliberate recheck", "--out", str(tmp_path / "c")]) == 0
    assert "re-check of 3 claim(s) not owed, because: a deliberate recheck" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "report"]) == 0 and "IN-STEP 5" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "gate"]) == 0
    idx = cx.load_index(root / cx.INDEX)
    del idx[next(iter(idx))]
    cx.save_index(root / cx.INDEX, idx)
    assert cx.main(["--root", str(root), "gate"]) == 1 and "REFUSED owed (new)" in capsys.readouterr().out


def test_a_key_whose_label_holds_a_comma_is_named_whole() -> None:
    known = {"p::f#the track out, the field spur and a row street stay whole": 1, "p::f#a": 2, "p::f#a, b": 3, "p::g#c": 4}
    whole = "p::f#the track out, the field spur and a row street stay whole"
    assert cx.split_keys(f"{whole},p::g#c", known) == [whole, "p::g#c"]
    assert cx.split_keys("p::f#a, b,p::g#c", known) == ["p::f#a, b", "p::g#c"], "the longest known run"
    assert cx.split_keys("p::f#a,p::g#c", known) == ["p::f#a", "p::g#c"]
    assert cx.split_keys("nope, p::g#c,", known) == ["nope", "p::g#c"], "an unknown piece alone, an empty one dropped"


def test_a_class_is_shown_as_its_own_statements_and_each_method_under_its_own_heading(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path, MOD + '\n\nclass Farm:\n    """Research: farm - NONE"""\n\n    SIZE = 3\n\n    def lay(self):\n        return self.SIZE * 2\n')
    cur = cx.current(skill)
    keys = [k for k in cur if "Farm" in k]
    manifest = cx.bundle(tmp_path, cur, keys, tmp_path / "b").read_text()
    head, _sep, method = manifest.partition("## UNIT l7r/diagram/hamletgen/rows.py::Farm.lay")
    assert "SIZE = 3" in head and "return self.SIZE" not in head and "return self.SIZE * 2" in method


def test_a_shortened_pointer_in_a_verdict_note_gets_its_full_name() -> None:
    """Feature 319: impl-drift wrote `0236-...-home-plot.drawing.html` into four notes, and the index then failed the pointer
    check. A unique stem is expanded; a number with no question, or two, is left for a person."""
    stems = ["0236-a-hamlets-home-plot", "0031-clustered", "0019-polders", "0019-polder-two"]
    reply = "VERDICT k DRIFTED - see 0236-...-home-plot.drawing.html and 0031-...html; 0019-...-x.html; 9999-...html [§]"
    got = cx.unelide(reply, stems)
    assert "0236-a-hamlets-home-plot.drawing.html" in got and "0031-clustered.html" in got
    assert "0019-...-x.html" in got and "9999-...html" in got, "ambiguous or unknown numbers stay as written"


def test_the_base_tree_is_read_when_a_listed_path_is_gone(tmp_path: pathlib.Path) -> None:
    # feature 378: `docs/buildings/` left the repository, `git archive` failed WHOLE on that one pathspec, and the gate's
    # base tree came back empty - every first finding then read as introduced. The paths the base holds are read.
    root = _repo(tmp_path)
    _commit(root, "base")
    base = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    assert "docs/buildings" in cx.BASE_PATHS and not (root / "docs" / "buildings").exists(), "the fixture lacks a listed path"
    out = tmp_path / "base"
    out.mkdir()
    tree = cx.base_tree(root, base, out)
    assert (tree / "l7r" / "diagram" / "hamletgen" / "rows.py").is_file()
    assert (tree / "research" / "questions" / "0033-row-villages-resson.html").is_file()
    assert "l7r/diagram/hamletgen/rows.py::SHARE" in cx.base_cores(tree), "the base's units are read, so a finding is judged against them"


def test_the_base_tree_s_units_are_kept_by_module(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """383 amendment 2 (FR-019): every push parsed the whole base tree (8.5 s of a landing's push); each module's units are kept
    by what it reads, so the next base reads the memo - and the same cores either way."""
    root = _repo(tmp_path)
    _commit(root, "base")
    base = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    out = tmp_path / "base"
    out.mkdir()
    tree = cx.base_tree(root, base, out)
    monkeypatch.delenv("L7R_CACHE_OFF", raising=False)
    first = cx.base_cores(tree, keep=root)
    assert first == cx.base_cores(tree), "the memo changes no core"
    cl = cx.engine(pathlib.Path(cx.__file__).resolve().parents[2])

    def parsed_again(*_a, **_k):  # noqa: ANN002, ANN003, ANN202
        raise AssertionError("a module the memo holds was parsed again")

    monkeypatch.setattr(cl, "module_units", parsed_again)
    assert cx.base_cores(tree, keep=root) == first, "the second read comes from the memo"


def test_a_bundle_carries_the_module_functions_a_unit_calls() -> None:
    """The round arbiter's tooling fix on ask:t03-claims-at-landing: `_clear_link` was judged CANNOT-TELL because its bundle
    lacked `link_survives`, the function its answer turns on."""
    import types

    root = pathlib.Path(__file__).resolve().parents[2]
    unit = types.SimpleNamespace(path="l7r/diagram/hamletgen/ways/clearance.py", qualname="_clear_link")
    src = cx.context_source(root, "l7r/diagram/hamletgen/ways/clearance.py::_clear_link")
    got = cx.callees(root, unit, src)
    assert "l7r/diagram/hamletgen/ways/clearance.py::link_survives" in got and len(got) <= cx.CALLEES_MAX
    assert all(not r.endswith("::_clear_link") for r in got), "never itself"
    assert cx.callees(root, types.SimpleNamespace(path="no/such.py", qualname="f"), "def f():\n    g()\n") == []


def test_a_bundle_carries_the_constants_a_unit_reads_and_what_a_cannot_tell_names() -> None:
    """Feature 385 T25 (plan D47; the round arbiter's fix on ask:t05-old-drifts-at-landing): the standoff claim on
    `_seat_households` was CANNOT-TELL three rounds running, each for the next layer its note named - imported callees, theirs,
    then module constants. A first bundle carries the constants the unit reads; a re-bundle chases what the note names."""
    import sys
    import types

    root = pathlib.Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "scripts" / "record"))
    import claims_context as cc

    path = "l7r/diagram/hamletgen/homesteads/stages.py"
    unit = types.SimpleNamespace(path=path, qualname="_seat_households_as")
    got = cx.callees(root, unit, cx.context_source(root, f"{path}::_seat_households_as"))
    assert any(r.endswith("::BUNDLE_PITCH") for r in got), f"an imported constant the unit reads: {got}"
    assert sum(not r.rsplit("::", 1)[1].isupper() for r in got) <= cx.CALLEES_MAX and all(r.startswith("l7r/") for r in got)
    deep = cc.chase(root, path, ["front_row", "turn_the_seat", "no_such_name"], cx.context_source)
    names = {r.rsplit("::", 1)[1] for r in deep}
    assert {"front_row", "turn_the_seat", "_front_row_from_chains", "STANDOFF_SLACK_PX", "HOUSE_PADDY_GAP_FT"} <= names, deep
    assert cc.chase(root, path, ["front_row"], cx.context_source, budget=10) == [], "the budget holds"
    assert cc.chase(root, path, ["HOUSE_PADDY_GAP_FT"], cx.context_source) == ["l7r/diagram/settlement/houses.py::HOUSE_PADDY_GAP_FT"], "a name the module never imports"
    # a label naming a distance, gap or standoff carries every direct callee and the constants they read, uncapped (the words)
    assert cc.DISTANCE.search("front-row standoff from the field") and not cc.DISTANCE.search("the declared cluster shape")
    far = cc.direct(root, unit, cx.context_source(root, f"{path}::_seat_households_as"), cx.context_source)
    assert any(r.endswith("::front_row") for r in far) and any(r.endswith("::BUNDLE_PITCH") for r in far), far
    assert len(far) > cx.CALLEES_MAX, "uncapped"
    reach = {r.rsplit("::", 1)[1] for r in far}
    assert {"_front_row_from_chains", "HOUSE_PADDY_GAP_FT", "STANDOFF_SLACK_PX"} <= reach, "two calls down, and what they read"
    assert len(far) == len(set(far)), "each once"


def test_findings_a_round_arbiter_ruling_carried_are_filed_with_the_ruling(tmp_path: pathlib.Path) -> None:
    """Feature 385 T45 (D59): KEYS= with RULING= files findings the gate counts as introduced, which an arbiter ruling carried -
    the box and its record row together, the row naming the ruling; a ruling the feature's record does not hold is refused, and
    KEYS= without RULING= too."""
    root = _repo(tmp_path)
    d = _active(root)
    k = "l7r/diagram/hamletgen/rows.py::far_row#dry share"
    args = ["--root", str(root), "carry", "--feature", "900", "--keys", f"{k}; ", "--ruling", "ask:t07-x"]
    assert cx.main(args) == 2, "no arbiter.jsonl: the ruling is not recorded"
    (d / "arbiter.jsonl").write_text('{"trigger": "ask:t07-y", "ruling": "continue"}\nnot json\n{"trigger": "ask:t07-x", "ruling": "continue"}\n')
    assert cx.main(["--root", str(root), "carry", "--feature", "900", "--keys", k]) == 2, "KEYS= alone is refused"
    assert cx.main(args) == 0
    assert f"- [ ] T02 Carried by the round arbiter's ruling ask:t07-x: findings it carried - fix the code or the claim and re-check each: {k} [lands-open]" in (d / "tasks.md").read_text()
    row = json.loads((d / "claims-carried.jsonl").read_text().splitlines()[-1])
    assert row["task"] == "T02" and row["keys"] == [k] and row["ruling"] == "ask:t07-x"
    assert cx.main(args[:5] + ["--task", "T01"] + args[5:]) == 0
    assert f"- [ ] T01 the work; carried by the round arbiter's ruling ask:t07-x: {k} [lands-open]" in (d / "tasks.md").read_text()


def test_a_changed_constant_names_the_drawing_pages_still_stating_its_old_figure(tmp_path: pathlib.Path) -> None:
    """Feature 385 T62, the round arbiter on ask:t10-findings-at-landing: three stale 23 ft pages were found at landing, not at the edit."""
    st = cx.claims_stale
    root = tmp_path
    mod = root / "l7r" / "rows.py"
    mod.parent.mkdir(parents=True)
    mod.write_text('INSET = 23.0\n"""Research: inset - research/questions/0018-ponds.drawing.html: 23 ft"""\nOTHER = 23\n')
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    (q / "0018-ponds.drawing.html").write_text("<p>set in 23 ft</p>")  # the cited page itself
    (q / "0022-bunds.drawing.html").write_text('<p>23 feet, as <a href="0018-ponds.html">the ponds</a></p>')  # links it
    (q / "0030-other.drawing.html").write_text("<p>23 ft</p>")  # states it, links nothing cited
    (q / "0031-near.drawing.html").write_text('<p>123 ft or 23.5 ft, <a href="0018-ponds.html">x</a></p>')  # a longer number only
    _git(root, "init", "-q", "-b", "main")
    _commit(root)
    base = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    assert st.stale(root, base) == []  # nothing changed
    mod.write_text('INSET = 23.0\n"""Research: inset - research/questions/0018-ponds.drawing.html: derived per map"""\nOTHER = 23\n')
    found = st.stale(root, base)
    assert [ln.split()[2] for ln in found] == ["research/questions/0018-ponds.drawing.html", "research/questions/0022-bunds.drawing.html"]
    assert "INSET was 23.0 in l7r/rows.py" in found[0]
    assert st.figures(ast.parse("x = (0, 1, 2.5, 30.0)").body[0].value) == ["2.5", "30"]  # type: ignore[attr-defined]


def test_a_reply_s_notes_are_written_in_the_house_style_and_its_keys_as_given() -> None:
    """Feature 385 T78 (plan D97): T10's gate went red on an index note's British spelling, copied from an impl-drift reply."""
    brit = "gr" + "ey"
    reply = f"VERDICT l7r/x.py::{brit}_band#a {brit} edge DRIFTED - the {brit} band is wider\nUNCLAIMED l7r/x.py::f - a {brit} stone"
    verdicts, unclaimed = cx.parse_reply(reply)
    key = f"l7r/x.py::{brit}_band#a {brit} edge"
    assert key in verdicts, "the key is matched as written"
    assert verdicts[key] == ("DRIFTED", "the gray band is wider") and unclaimed == [("l7r/x.py::f", "a gray stone")]


def test_an_entry_added_to_a_claimed_dict_owes_its_claims_a_triage_and_an_edited_claim_its_check(tmp_path: pathlib.Path) -> None:
    """Feature 385 T83 (plan D104): after the backfill, a dict's new entry owes `section triage`, never `code changed` for all."""
    mod = f'BANDS = {{\n    "a": 1,\n    "b": 2,\n}}\n"""Research:\n    band a - {Q}\n    band b - {Q}\n"""\n'
    root = _tree(tmp_path, mod=mod)
    cur = cx.current(root)
    index, store = _all_in_step(root), {}
    for k, r in cur.items():  # the dict's rows as the old fingerprint (the whole value) wrote them
        if "::BANDS#" in k:
            index[k]["code"] = cx.engine(REPO)._sha(r.unit.core + "\x1f" + r.claim.normalized())
    assert cx.backfill_sections(cur, index, store) == 2 and cx.owed(cur, index) == []
    (root / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(mod.replace('    "b": 2,\n', '    "b": 2,\n    "c": 3,\n'))
    assert sorted(w for _k, w in cx.owed(cx.current(root), index)) == [cx.SECTION_TRIAGE, cx.SECTION_TRIAGE]
    (root / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(mod.replace("band b - ", "band b, wider - "))
    assert [w for _k, w in cx.owed(cx.current(root), index)] == ["new"], "an edited claim line is a new claim, checked in full"


def test_an_aside_outside_the_change_is_filed_when_the_reply_is_recorded(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The round arbiter's fix on hour:385-approach-checklist@32: two checker asides lived only in replies - one in an .output
    transcript `make record-checked` read raw, one in prose - and neither reached a filed row."""
    import record_owed

    filed: list[tuple[str, str]] = []
    monkeypatch.setattr(record_owed, "file_outside", lambda root, check, reply: filed.append((check, reply)) or [{"file": "f", "block": "b", "finding": "x"}])
    reply = "VERDICT l7r/a.py::f#a IN-STEP - ok\n\nOUTSIDE THE CHANGE\n- research/questions/0246-x.drawing.html | a block | a gloss owed\n"
    cx.claims_triage.vet(reply, {"l7r/a.py::f#a": {}}, tmp_path, cx._VERDICT)
    assert filed and filed[0][0] == "impl-drift" and "OUTSIDE THE CHANGE" in filed[0][1]
    assert record_owed.outside.__call__ and len(record_owed.outside(reply)) == 1, "the row shape the agent file now asks for parses"


def test_the_gate_refuses_a_claim_the_grammar_cannot_read_in_a_changed_file(tmp_path: pathlib.Path) -> None:
    """Feature 385 T137 (D149): T136 landed "CONVENTION <page>" by the direct route, which runs no gate; the push's claims gate
    now refuses such a claim in any file the delta changed."""
    root = _repo(tmp_path)
    cx.save_index(root / cx.INDEX, _all_in_step(root))
    _commit(root, "base")
    cx._git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    assert cx.delta_form_problems(root) == []
    bad = MOD.replace("Research: plumbing - NONE", f"Research: plumbing - CONVENTION {Q}")
    (root / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(bad)
    _commit(root, "a malformed claim")
    probs = cx.delta_form_problems(root)
    assert len(probs) == 1 and probs[0].startswith("l7r/diagram/hamletgen/rows.py") and "the claims grammar:" in probs[0]
    assert any(r == probs[0] for r in cx.gate(root)[0]), "refused at the push"


def test_a_unit_moved_to_another_file_keeps_its_rows(tmp_path: pathlib.Path) -> None:
    """Feature 405 T58: a file split into a package at the 1,000-line bar (T53) moves its units with their code intact; keyed by
    file, the index owed every moved claim a full check. The moved rows carry over, and a moved unit whose code changed is owed."""
    skill = _tree(tmp_path)
    cur = cx.current(skill)
    index = {k.replace("hamletgen/rows.py", "hamletgen/old_rows.py"): v for k, v in _all_in_step(tmp_path).items()}
    rows = {k for k in cur if "hamletgen/rows.py" in k}
    assert rows and set(cx.moved(cur, index)) == rows, "every claim of the moved unit matched"
    assert cx.owed(cur, index) == [], "a pure move owes nothing"
    assert cx.rekey(cur, index) == len(rows) and set(index) >= set(cur) and not any("old_rows" in k for k in index)
    moved_then_changed = {k.replace("hamletgen/rows.py", "hamletgen/old_rows.py"): v for k, v in _all_in_step(tmp_path).items()}
    _tree(tmp_path, MOD.replace("x * SHARE", "x * SHARE * 2"))
    cur = cx.current(skill)
    assert "l7r/diagram/hamletgen/rows.py::far_row#dry share" not in cx.moved(cur, moved_then_changed), "its code changed: not a pure move"


def test_a_claims_label_its_own_account_contradicts_is_flagged_with_its_fix(tmp_path: pathlib.Path) -> None:
    """Feature 405 T120 (plan D91): T115-T108's claims rounds went to MISLABELED labels whose own words said so."""
    from l7r.diagram.tools.claims import parse_claim  # noqa: PLC0415

    lb = cx.claims_labels
    q = tmp_path / "q"
    q.mkdir()
    (q / "0246-lanes.drawing.html").write_text("<p>a 7 ft gap off a garden fence; 3 ft is a GUESS</p>")
    page = "research/questions/0246-lanes.drawing.html"

    def said(line: str) -> list[str]:
        return lb.flag("k", parse_claim(line), q, {})

    departs = said("off its own garden - GUESS: kept 3 ft, stricter than the page's gap")
    assert len(departs) == 1 and "`DEVIATION <page>`" in departs[0]
    bare = said("off the fence - GUESS: 7 ft, as 0246 keeps it")
    assert len(bare) == 1 and "names 0246" in bare[0]
    unstated = said(f"off the well - GUESS {page}: 9 ft round the curb")
    assert len(unstated) == 1 and "states 9 ft" in unstated[0]
    for right in (
        f"off the fence - {page}: 7 ft",  # cited
        "off the shed - GUESS: 5 ft, which no page sizes",  # bare, names nothing
        "off a corner - GUESS: 13 ft; 0246 does not say how far, so the 13 ft is ours",  # bare, names a silent page
        f"off the bed - GUESS {page}: 3 ft",  # the page states the guess's figure
        f"off its own garden - DEVIATION {page}: 3 ft, short of the page's 7 ft",  # a departure labeled one
    ):
        assert said(right) == [], right
    rows = {"k": type("R", (), {"claim": parse_claim("x - GUESS: as 0081 says")})(), "none": type("R", (), {"claim": None})()}
    assert len(lb.flags(rows, ["k", "k", "none", "gone"], q)) == 1  # once a key; an unclaimed or missing row is skipped


def test_a_verdict_set_off_by_a_dash_or_closed_by_a_colon_is_read_against_its_key() -> None:
    """Feature 417 T50: an impl-drift reply wrote `KEY - IN-STEP - note` and `KEY - IN-STEP: note`; the dash went into the key and
    nothing was recorded."""
    reply = "VERDICT l7r/x.py::f#a T - IN-STEP - a note\nVERDICT l7r/x.py::g#b - DRIFTED: known (417 T32): it\nVERDICT l7r/x.py::h#c IN-STEP - plain"
    verdicts, _ = cx.parse_reply(reply)
    assert verdicts == {"l7r/x.py::f#a T": ("IN-STEP", "a note"), "l7r/x.py::g#b": ("DRIFTED", "known (417 T32): it"), "l7r/x.py::h#c": ("IN-STEP", "plain")}

"""`scripts/_claims.py` - the claims index: owed, bundle, record, report and the push's verdict (feature 316).

The GM, 2026-10-02: *"our tooling should be able to evaluate whether or not an annotated thing has been edited since the last
time a subagent check ran on it"*, and the push rule the GM accepted: an owed row blocks, a finding the change introduces blocks,
a pre-existing finding warns. One case per acceptance scenario of spec US2-US4, on a small engine tree in tmp.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
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
    skill = root / cx.SKILL
    (skill / "l7r" / "diagram" / "hamletgen").mkdir(parents=True, exist_ok=True)
    (skill / "l7r" / "diagram" / "hamletgen" / "__init__.py").write_text("from . import rows\n")
    (skill / "l7r" / "diagram" / "hamletgen" / "rows.py").write_text(mod)
    (skill / "research" / "questions").mkdir(parents=True, exist_ok=True)
    (skill / "research" / "questions" / "0033-row-villages-resson.html").write_text(page)
    (skill / "buildings").mkdir(exist_ok=True)
    (skill / "buildings.md").write_text("## Walls\n<!-- Research: walls - CONVENTION -->\n")
    (skill / "buildings" / "programs.md").write_text("### Country shrine (a village district's shrine)\n<!-- Research: precinct - UNRESEARCHED -->\n")
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
    cur = cx.current(root / cx.SKILL)
    return {k: {"verdict": "IN-STEP", "code": r.code, "core": r.unit.core, "research": r.research, "date": "d", "note": ""} for k, r in cur.items()}


def test_every_claim_is_a_row_including_inherited_and_procedure_claims(tmp_path: pathlib.Path) -> None:
    cur = cx.current(_tree(tmp_path))
    keys = sorted(cur)
    assert keys == sorted(
        [
            ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::SHARE#dry share",
            ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share",
            ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::helper#plumbing",
            ".claude/skills/diagram/buildings.md::Walls#walls",
            ".claude/skills/diagram/buildings/programs.md::Country shrine (a village district's shrine)#precinct",
        ]
    )
    assert cur[".claude/skills/diagram/buildings.md::Walls#walls"].research == "" and cur[".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share"].research


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
    assert cx.owed(cx.current(skill), index) == [(".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share", "code changed")]
    _tree(tmp_path, MOD.replace("SHARE = 0.5", "SHARE = 0.4"))
    assert sorted(k.rsplit("::", 1)[1] for k, _w in cx.owed(cx.current(skill), index)) == ["SHARE#dry share", "far_row#dry share"]
    _tree(tmp_path, page=PAGE.replace("face the street", "face south"))
    assert [(k.rsplit("::", 1)[1], w) for k, w in cx.owed(cx.current(skill), index)] == [("SHARE#dry share", "research changed"), ("far_row#dry share", "research changed")]


def test_a_missing_question_fingerprints_as_missing(tmp_path: pathlib.Path) -> None:
    assert cx.research_fp([Q], tmp_path) == cx.research_fp([Q], tmp_path, {}) != ""
    assert cx.research_fp([], tmp_path) == ""


def test_the_bundle_holds_each_unit_its_claims_and_the_cited_pages(tmp_path: pathlib.Path) -> None:
    skill = _tree(tmp_path)
    (skill / "research" / "questions" / "0033-row-villages-resson.drawing.html").write_text("<h2>How our maps draw</h2>\n<!-- x -->\n")
    cur = cx.current(skill)
    keys = sorted(cur)
    manifest = cx.bundle(tmp_path, cur, keys, tmp_path / "b").read_text()
    assert "## UNIT .claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row (function" in manifest
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
    k = ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share"
    index[k] |= {"verdict": "DRIFTED", "note": "296"}
    index[".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::helper#an unclaimed thing"] = {"verdict": "UNCLAIMED", "note": "n"}
    index["gone::x#y"] = {"verdict": "DRIFTED"}
    text = cx.report(cx.current(skill), index)
    assert text.startswith("claims: 5 in scope; IN-STEP 4, DRIFTED 1, UNCLAIMED 1; owed 0")
    assert f"DRIFTED        {k} - 296" in text and "gone::x" not in text
    assert "UNRESEARCHED claims (the open research): 1" in text


def _row(cur: dict, key: str, verdict: str, **kw: str) -> dict[str, str]:
    r = cur[key]
    return {"verdict": verdict, "code": r.code, "core": r.unit.core, "research": r.research, "note": "n", **kw}


def test_classify_introduced_and_pre_existing(tmp_path: pathlib.Path) -> None:
    base_skill = _tree(tmp_path / "base")
    base = cx.current(base_skill)
    cores, bq = cx.base_cores(base_skill), base_skill / "research" / "questions"
    k = ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share"
    # IN-STEP at the base, a finding now: introduced
    assert cx.classify(base, {k: _row(base, k, "DRIFTED")}, {k: _row(base, k, "IN-STEP")}, cores, bq)[0]
    # a finding at both ends, whatever changed: pre-existing
    head = cx.current(_tree(tmp_path / "head", MOD.replace("x * SHARE", "x * SHARE + 1")))
    assert cx.classify(head, {k: _row(head, k, "DRIFTED")}, {k: _row(base, k, "DRIFTED")}, cores, bq) == ([], [f"DRIFTED        {k} - n"])
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
    # the cited question's findings changed under a first finding: introduced
    moved = cx.current(_tree(tmp_path / "moved", page=PAGE.replace("face the street", "face south")))
    assert cx.classify(moved, {k: _row(moved, k, "DRIFTED")}, {}, cores, bq)[0]
    # an IN-STEP row is no finding
    assert cx.classify(base, {k: _row(base, k, "IN-STEP")}, {}, cores, bq) == ([], [])


def test_a_base_with_no_claims_at_all_makes_every_first_finding_on_untouched_code_pre_existing(tmp_path: pathlib.Path) -> None:
    # this feature's own landing: main holds the code but no claims - its units still have cores (the push once read
    # "no claim at the base" as "no unit at the base" and called every audit finding introduced)
    bare = MOD.replace("Research: plumbing - NONE\n", "").replace(f'"""Research: dry share - {Q}"""\n', "").replace(f"\n    Research: dry share - {Q}\n    ", "")
    base_skill = _tree(tmp_path / "base", bare)
    assert cx.current(base_skill) == {} or all("rows.py" not in k for k in cx.current(base_skill))
    head = cx.current(_tree(tmp_path / "head"))
    k = ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share"
    intro, pre = cx.classify(head, {k: _row(head, k, "DRIFTED")}, {}, cx.base_cores(base_skill), base_skill / "research" / "questions")
    assert intro == [] and pre


def test_the_gate_refuses_owed_and_introduced_and_warns_pre_existing(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    assert any(r.startswith("owed (new)") for r in cx.gate(root)[0])
    cx.save_index(root / cx.INDEX, _all_in_step(root))
    _commit(root, "base")
    assert cx.gate(root) == ([], [])
    k = ".claude/skills/diagram/l7r/diagram/hamletgen/rows.py::far_row#dry share"
    idx = cx.load_index(root / cx.INDEX)
    idx[k]["verdict"] = "DRIFTED"
    cx.save_index(root / cx.INDEX, idx)
    refuse, warn = cx.gate(root)  # HEAD is the merge base (no origin/main): IN-STEP there, DRIFTED now
    assert refuse == [f"introduced: DRIFTED        {k} - "] and warn == []
    _commit(root, "drift")
    assert cx.gate(root) == ([], [f"pre-existing: DRIFTED        {k} - "])


def test_the_command_line(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _repo(tmp_path)
    assert cx.main(["--root", str(root), "owed"]) == 0 and "claims-owed: 5 claim(s) in 3 file(s)" in capsys.readouterr().out
    assert cx.main(["--root", str(root), "bundle", "--units", "nope"]) == 2
    assert cx.main(["--root", str(root), "bundle", "--owed", "--out", str(tmp_path / "b")]) == 0
    reply = tmp_path / "reply.txt"
    units = json.loads((tmp_path / "b" / "units.json").read_text())
    reply.write_text("".join(f"VERDICT {k} IN-STEP - ok\n" for k in units))
    assert cx.main(["--root", str(root), "record", "--bundle", str(tmp_path / "b"), "--reply", str(reply)]) == 0
    assert "5 of 5 recorded" in capsys.readouterr().out
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
    head, _sep, method = manifest.partition("## UNIT .claude/skills/diagram/l7r/diagram/hamletgen/rows.py::Farm.lay")
    assert "SIZE = 3" in head and "return self.SIZE" not in head and "return self.SIZE * 2" in method


def test_a_shortened_pointer_in_a_verdict_note_gets_its_full_name() -> None:
    """Feature 319: impl-drift wrote `0236-...-home-plot.drawing.html` into four notes, and the index then failed the pointer
    check. A unique stem is expanded; a number with no question, or two, is left for a person."""
    stems = ["0236-a-hamlets-home-plot", "0031-clustered", "0019-polders", "0019-polder-two"]
    reply = "VERDICT k DRIFTED - see 0236-...-home-plot.drawing.html and 0031-...html; 0019-...-x.html; 9999-...html [§]"
    got = cx.unelide(reply, stems)
    assert "0236-a-hamlets-home-plot.drawing.html" in got and "0031-clustered.html" in got
    assert "0019-...-x.html" in got and "9999-...html" in got, "ambiguous or unknown numbers stay as written"

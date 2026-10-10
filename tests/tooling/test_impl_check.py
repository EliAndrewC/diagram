"""`scripts/record/impl_check.py` and the closing check (feature 378): a `research record` feature closes only once each
question whose findings it changed is cited by a checked `Research:` claim, or recorded as implemented nowhere.

WHAT THESE PROVE (SC-001, SC-002, FR-008): over a real git tree whose commits are written as this repository writes them,
a changed question with no claim and no line is missing; one whose claims are owed their check is missing; one cited by a
checked claim - DRIFTED as well as IN-STEP - is not, nor one recorded "no code implements it"; a change to a drawing page
alone owes nothing; an untagged feature owes nothing; and the closing check refuses on what is missing.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ic = _load("impl_check", "scripts/record/impl_check.py")
cc = _load("close_check", "scripts/gates/close_check.py")


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _tree(tmp: pathlib.Path, affects: str = "magistracy, research record", page: str = "0047-the-privy.html") -> tuple[pathlib.Path, pathlib.Path]:
    root = tmp / "repo"
    (root / "research" / "questions").mkdir(parents=True)
    d = root / "specs" / "390-privy-loose-ends"
    d.mkdir(parents=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    (d / "spec.md").write_text(f"# 390\n\n**Status**: In progress\n\n**Affects**: {affects}\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "390: claimed")
    (root / "research" / "questions" / page).write_text("<h2>q</h2><p>a finding</p>\n")
    (root / "research" / "questions" / "0099-other.html").write_text("<p>someone else's</p>\n")
    _git(root, "add", "research/questions/" + page)
    _git(root, "commit", "-qm", "Feature 390: the privy's finding")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "Feature 391: another feature's page")
    return root, d


def test_a_changed_question_with_no_claim_and_no_line_is_missing(tmp_path: pathlib.Path) -> None:
    root, d = _tree(tmp_path)
    assert ic.changed_questions(root, 390) == ["0047"], "only this feature's commits, only the findings page"
    lines, missing = ic.report(root, d, cites=({}, set(), {}))
    assert len(missing) == 1 and "0047" in missing[0] and "no code implements it" in missing[0]


def test_claims_owed_their_check_are_missing_until_checked_and_a_drift_closes(tmp_path: pathlib.Path) -> None:
    root, d = _tree(tmp_path)
    key = "l7r/diagram/x.py::privy#placement"
    _lines, missing = ic.report(root, d, cites=({"0047": [key]}, {key}, {}))
    assert missing and "owed their impl-drift check" in missing[0]
    lines, missing = ic.report(root, d, cites=({"0047": [key]}, set(), {key: "DRIFTED"}))
    assert missing == [] and any("DRIFTED" in ln and key in ln for ln in lines), "a drift is shown and closes - the code is not fixed here"


def test_a_question_recorded_as_implemented_nowhere_is_not_missing(tmp_path: pathlib.Path) -> None:
    root, d = _tree(tmp_path)
    (d / "implementation-check.md").write_text("- 0047: no code implements it - the magistracy's privy is not drawn yet\n")
    assert "must say what was searched" in ic.report(root, d, cites=({}, set(), {}))[1][0], "a reason with no search is not (b)"
    (d / "implementation-check.md").write_text("- 0047: no code implements it - the magistracy's privy is not drawn yet; searched: grep -rn privy l7r/diagram/compound*.py\n")
    lines, missing = ic.report(root, d, cites=({}, set(), {}))
    assert missing == [] and any("the magistracy's privy is not drawn yet" in ln for ln in lines)


def test_a_drawing_page_alone_and_an_untagged_feature_owe_nothing(tmp_path: pathlib.Path) -> None:
    root, d = _tree(tmp_path, page="0047-the-privy.drawing.html")
    assert ic.report(root, d, cites=({}, set(), {}))[1] == []
    root2, d2 = _tree(tmp_path / "b", affects="tooling")
    assert ic.report(root2, d2, cites=({}, set(), {}))[1] == []


def test_the_closing_check_refuses_on_what_is_missing(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    root, d = _tree(tmp_path)
    (d / "report.md").write_text("report\n")

    class _Stub:  # impl_check with no claim in the tree: the closing check is what is under test
        @staticmethod
        def missing(d_, root_):  # noqa: ANN001, ANN205
            assert root_ == root.resolve() and d_ == d, "asked of the feature, in the repository holding it"
            return [f"{d_.name} owes its implementation check (feature 378): {m}" for m in ic.report(root_, d_, cites=({}, set(), {}))[1]]

    monkeypatch.setattr(cc, "_impl_check", lambda: _Stub)
    why = cc.reasons(d, root / "specs")
    assert any("owes its implementation check (feature 378): 0047" in w for w in why)
    (d / "implementation-check.md").write_text("- 0047: no code implements it - not drawn; searched: grep -rn privy l7r\n")
    assert cc.reasons(d, root / "specs") == []

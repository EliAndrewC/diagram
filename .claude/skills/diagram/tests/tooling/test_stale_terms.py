"""`scripts/_stale_terms.py` (feature 253): after a value changed, where does the OLD value still stand?

WHAT THESE PROVE. The rule on plain inputs - a replaced line's shared backticked SUBJECT plus a value the new
line dropped, found on another operative line - and what it must not report: a changed line with no subject,
the Review history, `request.md`, `tasks.md`, `research.md`. Then the REAL case it was built for: feature
251's directory at the dispatch of its first amendment review against what the previous round saw, where
two of that round's findings were exactly this shape.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_stale_terms", REPO / "scripts" / "_stale_terms.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


st = _load()

OLD = {"spec.md": "# F\n\n| `reader` | sonnet | high |\n\n**FR-7** `reader` moves to Sonnet at high effort.\n\nThe `checker` stays.\n\n## Review history\n\n- round 1: `reader` on sonnet.\n", "request.md": "> put `reader` on sonnet\n", "tasks.md": "- [x] T1 the table only\n      verify: DONE. `reader` sonnet\n", "research.md": "| `reader` | sonnet tested |\n"}
NEW = {**OLD, "spec.md": OLD["spec.md"].replace("| `reader` | sonnet | high |", "| `reader` | opus | high |")}


def test_the_old_value_beside_its_subject_is_a_candidate_and_nothing_else_is():
    found = st.stale_candidates(OLD, NEW)
    assert [(c["file"], c["line"], c["subject"], c["old_values"]) for c in found] == [("spec.md", 5, "reader", ["sonnet"])]
    assert "moves to Sonnet" in found[0]["text"] and found[0]["changed_in"] == "spec.md"
    live = {**NEW, "tasks.md": "- [ ] T2 put `reader` on sonnet\n      verify: DONE. `reader` sonnet\n"}
    assert [(c["file"], c["line"]) for c in st.stale_candidates(OLD, live)] == [("spec.md", 5), ("tasks.md", 1)], "a TASK line is live text; its dated verify note is not"
    wide = {**NEW, "data-model.md": "`reader`: model sonnet\n", "contracts/api.md": "the `reader` contract assumes sonnet\n", "gm-request.md": "> `reader` on sonnet\n", "measure/h.py": "# `reader` sonnet\n", "plan-review.json": "{\"x\": \"`reader` sonnet\"}"}
    assert sorted(c["file"] for c in st.stale_candidates(OLD, wide)) == ["contracts/api.md", "data-model.md", "spec.md"], "a file kind nobody named is SEARCHED; the named ones are not"


def test_no_change_no_subject_or_no_dropped_value_yields_nothing():
    assert st.stale_candidates(OLD, OLD) == []
    plain_old, plain_new = {"spec.md": "the reader is on sonnet\nlater: reader sonnet\n"}, {"spec.md": "the reader is on opus\nlater: reader sonnet\n"}
    assert st.stale_candidates(plain_old, plain_new) == [], "no backticked subject, no anchor, no candidate"
    grown_old, grown_new = {"spec.md": "`reader` runs\nelsewhere `reader` runs\n"}, {"spec.md": "`reader` runs daily\nelsewhere `reader` runs\n"}
    assert st.stale_candidates(grown_old, grown_new) == [], "a line that only GAINED words dropped no value"
    assert st.stale_candidates({}, {"spec.md": "`new` file\n"}) == [], "a file the previous round never saw has no old side"


def test_changed_pairs_pairs_replacements_only():
    assert st.changed_pairs("a\nb\nc\n", "a\nB\nc\nd\n") == [("b", "B")]


def test_render_lists_candidates_and_says_so_when_there_are_none():
    assert "no candidate" in st.render([])
    many = [{"file": "spec.md", "line": n, "subject": "reader", "old_values": ["sonnet"], "text": "x", "changed_in": "spec.md", "changed_to": "y"} for n in range(30)]
    text = st.render(many)
    assert "30 candidate(s)" in text and "and 5 more" in text and "spec.md:0  `reader` still with sonnet" in text


def _git(*args: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=False).returncode == 0


@pytest.mark.skipif(not (_git("cat-file", "-e", "36d34718^{commit}") and _git("cat-file", "-e", "a5d5051e^{commit}")), reason="a shallow checkout without feature 251's history")
def test_the_real_case_feature_251s_first_amendment_round():
    """Two of that round's six findings were a value left beside its subject: FR-007's Sonnet and FR-008's medium."""
    feature = "251-tiered-subagent-checks"
    found = st.stale_candidates(st.read_ref(REPO, "a5d5051e", feature), st.read_ref(REPO, "36d34718", feature))
    texts = [c["text"] for c in found]
    assert any("`source-reader` moves to Sonnet at high effort" in t for t in texts), "FR-007 - round 1, item 1"
    assert any("(Opus, medium, the same tools)" in t for t in texts), "FR-008 - round 1, item 2"
    assert {c["file"] for c in found} == {"spec.md"} and len(found) <= 4, "the operative document only, and few enough to read"


def test_main_against_a_ref_and_its_refusals(tmp_path, capsys):
    assert st.main(["999-no-such-feature", "--clone", str(REPO)]) == 2
    clone = tmp_path / "c"
    (clone / "specs" / "301-x").mkdir(parents=True)
    (clone / "specs" / "301-x" / "spec.md").write_text(NEW["spec.md"], encoding="utf-8")
    assert st.main(["301-x", "--clone", str(clone)]) == 2, "no snapshot and no ref: say so"
    snap = clone / ".git" / "review-round" / "301-x" / "snapshot"
    snap.mkdir(parents=True)
    (snap / "spec.md").write_text(OLD["spec.md"], encoding="utf-8")
    capsys.readouterr()
    assert st.main(["301", "--clone", str(clone)]) == 1, "a prefix names the feature; candidates exit 1"
    assert "spec.md:5" in capsys.readouterr().out
    (snap / "spec.md").write_text(NEW["spec.md"], encoding="utf-8")
    assert st.main(["301-x", "--clone", str(clone)]) == 0
    subprocess.run(["git", "init", "-q", str(clone)], check=True)
    subprocess.run(["git", "-C", str(clone), "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(clone), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"], check=True)
    assert st.main(["301-x", "--clone", str(clone), "--against", "HEAD"]) == 0, "the committed state equals the present one"

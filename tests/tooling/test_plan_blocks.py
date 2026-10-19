"""Feature 375 amendment 11 (SC-036 to SC-039): a plan reviewed by its changed blocks, finished sections archived, no plan copy
in the verdict, a lean bundle for a section's review.

WHAT THESE PROVE, on a feature in a real git repository: an edit to one block owes that block alone, and recording it clears the
tick; an unchanged block keeps its verdict; a record from before the amendment covers the blocks of the text it reviewed; the
archive moves only finished, CLEAR sections, byte for byte, and owes no review; a converted record keeps every verdict and holds
no plan text; a typo is still a typo, read from git; the bundle carries the request, the cited requirements whole, the index,
the blocks and their earlier text - and less than the spec and plan it stands in for.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("_plan_gate_blocks", script("plan_gate"))
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
sys.modules["_plan_gate_blocks"] = gate
_spec.loader.exec_module(gate)

PLAN = """# Plan

**D1 - shared.** Every gate is checked once.

## Batch 1

### Wave 1 (T01)

**D2 - the sty.** The sty stands by the house (FR-001).

## Batch 2

### Wave 2 (T02)

**D3 - the well.** The well stands by the lane (FR-002).

## Notes

A note on the waves, 3 items.
"""
SPEC = """# Spec

## Requirements

- **FR-001 The sty.** A sty stands against the house, as the record says.
- **FR-002 The well.** A well stands by its lane.
- **FR-003 Unrelated.** Something else entirely.

## Success criteria

- **SC-001** (FR-001) The sty is drawn.
"""
WITHIN = {"id": "D", "summary": "s", "class": "within", "why": "w"}


@pytest.fixture(autouse=True)
def _census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True, text=True).stdout


def feature(tmp: pathlib.Path, tasks: str = "- [x] T01 the sty\n- [ ] T02 the well\n") -> pathlib.Path:
    root = tmp / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    d = root / "specs" / "999-x"
    d.mkdir(parents=True)
    (d / "plan.md").write_text(PLAN)
    (d / "spec.md").write_text(SPEC)
    (d / "request.md").write_text("> the GM's words\n")
    (d / "tasks.md").write_text(tasks)
    gate.record(d, {"plan_sha256": hashlib.sha256(PLAN.encode()).hexdigest(), "decisions": [WITHIN]}, "spec-fidelity")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "the plan, reviewed")
    return d


def test_an_edit_to_one_block_owes_that_block_alone(tmp_path: pathlib.Path) -> None:
    d = feature(tmp_path)
    assert gate.owed(d) is None
    (d / "plan.md").write_text(PLAN.replace("A note on the waves, 3 items.", "A note on the waves, 4 items, and a new rule."))
    rule, reason = gate.owed(d)
    assert rule == "plan-review-stale" and "## Notes" in reason and "Batch 1" not in reason, "only the edited block is named"
    keys, _ = gate.block_status(json.loads((d / "plan-review.json").read_text()), (d / "plan.md").read_text(), set())
    assert keys == ["## Notes"], "every other block keeps its verdict"
    body = dict((k, b) for k, b, _a in gate.blocks((d / "plan.md").read_text()))["## Notes"]
    with pytest.raises(PermissionError):
        gate.record_blocks(d, {"blocks": {"## Notes": gate.block_digest(body)}, "decisions": []}, "main")
    with pytest.raises(ValueError, match="changed while"):
        gate.record_blocks(d, {"blocks": {"## Notes": "0" * 64}, "decisions": []}, "spec-fidelity")
    gate.record_blocks(d, {"blocks": {"## Notes": gate.block_digest(body)}, "decisions": [WITHIN]}, "spec-fidelity")
    assert gate.owed(d) is None, "the changed block's review clears the tick"


def test_a_record_from_before_the_amendment_covers_the_blocks_it_reviewed(tmp_path: pathlib.Path) -> None:
    d = feature(tmp_path)
    old = {"plan_sha256": hashlib.sha256(PLAN.encode()).hexdigest(), "plan_text": PLAN, "verdict": "CLEAR", "decisions": [WITHIN]}
    (d / "plan-review.json").write_text(json.dumps(old))
    (d / "plan.md").write_text(PLAN.replace("by the lane", "by the pond"))
    assert gate.owed(d)[1].count("block(s)") == 1 and "Wave 2 (T02)" in gate.owed(d)[1]
    slim = gate.slim_record(old)
    assert "plan_text" not in slim and all(e["verdict"] == "CLEAR" for e in slim["blocks"].values())
    (d / "plan-review.json").write_text(json.dumps(slim))
    assert "Wave 2 (T02)" in gate.owed(d)[1], "converted, it owes the same"
    (d / "plan.md").write_text(PLAN.replace("checked once", "cheked once"))
    assert gate.owed(d) is None, "a typo is still a typo: its earlier text read from git (FR-045)"


def test_the_archive_moves_only_finished_clear_sections_and_owes_nothing(tmp_path: pathlib.Path) -> None:
    d = feature(tmp_path)
    sec = gate.task_sections(PLAN)["T01"]
    assert [s for s in gate.archivable(d)] == [sec], "T02 is open: its section stays"
    assert gate.archive(d, today="2026-10-13") == ["T01"]
    plan = (d / "plan.md").read_text()
    assert sec not in plan and "<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-13" in plan
    assert sec in (d / "plan-done.md").read_text(), "byte for byte"
    assert gate.owed(d) is None, "the move owes no review"
    (d / "tasks.md").write_text("- [x] T01 the sty\n- [x] T02 the well\n")
    assert gate.archive(d) == ["T02"] and "Wave 2" not in (d / "plan.md").read_text() and gate.owed(d) is None


def test_the_bundle_is_lean_and_whole_where_it_must_be(tmp_path: pathlib.Path) -> None:
    import os

    d = feature(tmp_path)
    (d / "plan.md").write_text(PLAN.replace("by the lane (FR-002)", "by the lane, two to a lane (FR-002)"))
    here = os.getcwd()
    try:
        os.chdir(d.parent.parent)
        out = subprocess.run([sys.executable, str(script("plan_gate")), "delta", str(d)], capture_output=True, text=True, check=True).stdout
    finally:
        os.chdir(here)
    manifest = pathlib.Path(out.split("read ", 1)[1].split(" and the files", 1)[0])
    b = manifest.parent
    assert (b / "request.md").read_text() == "> the GM's words\n", "the GM's words, whole"
    assert "FR-002 The well.** A well stands by its lane." in (b / "spec-cited.md").read_text()
    assert "FR-003" not in (b / "spec-cited.md").read_text() and "FR-003 Unrelated" in (b / "spec-index.md").read_text()
    assert "two to a lane" in (b / "blocks.md").read_text() and "Batch 1" not in (b / "blocks.md").read_text()
    assert "by the lane (FR-002)" in (b / "earlier.md").read_text(), "the block as last judged CLEAR, from git"
    assert "verdict CLEAR -->" in (b / "earlier.md").read_text(), "feature 385 T114: the verdict it got, named"
    assert "BLOCKS=1" in manifest.read_text()
    size = sum(f.stat().st_size for f in b.iterdir())
    assert size < len(SPEC) + len(PLAN) + 2000, "a bundle no larger than the spec and plan it stands in for"
    # feature 385 T29: each block set its own directory, so a second review's bundle never overwrites one being read
    assert b.name.startswith(f"plan-{d.name}-blocks-") and b.name != f"plan-{d.name}-blocks", b.name
    (d / "plan.md").write_text(PLAN.replace("by the lane (FR-002)", "by the lane, three to a lane (FR-002)"))
    try:
        os.chdir(d.parent.parent)
        out2 = subprocess.run([sys.executable, str(script("plan_gate")), "delta", str(d)], capture_output=True, text=True, check=True).stdout
    finally:
        os.chdir(here)
    b2 = pathlib.Path(out2.split("read ", 1)[1].split(" and the files", 1)[0]).parent
    assert b2 != b and (b / "blocks.md").is_file() and "two to a lane" in (b / "blocks.md").read_text(), "the first review's bundle stands"


def test_a_block_deleted_by_hand_is_owed_and_its_removal_reviewed(tmp_path: pathlib.Path) -> None:
    """The plan review of amendment 11: a decision deleted outside `make plan-archive` is a change like any other."""
    d = feature(tmp_path)
    (d / "plan.md").write_text(PLAN.replace(gate.task_sections(PLAN)["T02"], ""))
    rule, reason = gate.owed(d)
    assert rule == "plan-review-stale" and "(removed) ### Wave 2 (T02)" in reason
    gate.record_blocks(d, {"blocks": {"(removed) ### Wave 2 (T02)": "removed"}, "decisions": [WITHIN]}, "spec-fidelity")
    assert gate.owed(d) is None, "its removal judged, it leaves the record"


def test_a_typo_s_earlier_text_is_found_however_far_back(tmp_path: pathlib.Path) -> None:
    """The plan review: no cap on the history walk - the reviewed text sits more than a chunk of versions back."""
    d = feature(tmp_path)
    root = d.parent.parent
    for i in range(gate.HISTORY_CHUNK + 5):  # later commits that touch only another block, kept CLEAR by their reviews
        (d / "plan.md").write_text((d / "plan.md").read_text().replace(f"items{'.' if i == 0 else f' v{i - 1}.'}", f"items v{i}."))
        _git(root, "commit", "-qam", f"v{i}")
    review = json.loads((d / "plan-review.json").read_text())
    notes = dict((k, b) for k, b, _a in gate.blocks((d / "plan.md").read_text()))["## Notes"]
    review["blocks"]["## Notes"]["sha256"] = gate.block_digest(notes)
    (d / "plan-review.json").write_text(json.dumps(review))
    (d / "plan.md").write_text((d / "plan.md").read_text().replace("checked once", "cheked once"))
    assert gate.owed(d) is None, "the typo is measured against text 30 versions back"


def test_the_blocks_a_whole_plan_blocked_left_are_owed_once_the_blocking_block_is_cleared(tmp_path: pathlib.Path) -> None:
    """Feature 385: a whole-plan BLOCKED review is recorded on every block. The blocking decision fixed in its own block and that
    block re-reviewed CLEAR, the blocks beside it - unchanged - still read BLOCKED; `plan-delta` called nothing owed and `make
    decide` refused the task for ever. Now a BLOCKED block is owed a review like a changed one."""
    import os

    d = feature(tmp_path)
    bad = {"id": "D2", "summary": "s", "class": "narrowing", "ruling": "NOT LEGITIMATE", "why": "w"}
    gate.record(d, {"plan_sha256": hashlib.sha256(PLAN.encode()).hexdigest(), "decisions": [bad]}, "spec-fidelity")
    fixed = PLAN.replace("The sty stands by the house (FR-001).", "The sty stands against the house (FR-001).")
    (d / "plan.md").write_text(fixed)
    body = dict((k, b) for k, b, _a in gate.blocks(fixed))["### Wave 1 (T01)"]
    gate.record_blocks(d, {"blocks": {"### Wave 1 (T01)": gate.block_digest(body)}, "decisions": [WITHIN]}, "spec-fidelity")
    keys, blocked = gate.block_status(json.loads((d / "plan-review.json").read_text()), fixed, set())
    assert not keys and blocked, "the fixed block CLEAR, its neighbors still BLOCKED and unchanged"
    here = os.getcwd()
    try:
        os.chdir(d.parent.parent)
        out = subprocess.run([sys.executable, str(script("plan_gate")), "delta", str(d)], capture_output=True, text=True, check=True).stdout
    finally:
        os.chdir(here)
    assert "no block of" not in out and "MODE 4" in out, "the BLOCKED blocks are owed their review"


def test_a_requirement_cited_as_another_feature_s_is_bundled_from_that_feature(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T66 (plan D85): T65's review was handed 385's own FR-005 for a block citing 375's."""
    sys.path.insert(0, str(script("plan_bundle").parent))
    import plan_bundle  # noqa: PLC0415

    monkeypatch.setattr(plan_bundle, "OUT", tmp_path / "out")
    d = feature(tmp_path)
    other = d.parent / "375-enforced"
    other.mkdir()
    (other / "spec.md").write_text("## Requirements\n\n- **FR-002 The archive.** Archiving voids nothing.\n- **FR-044 The plan.** Finished sections move.\n")
    body = "## T05 - x\n\nAs feature 375's FR-002 has it, and 375 FR-044, and feature 375, FR-099 (no such id); FR-001 is ours.\n"
    manifest = plan_bundle.build(d, "t", [("## T05 - x", body)], {}, "how")
    cited = (manifest.parent / "spec-cited.md").read_text()
    assert "<!-- feature 375 -->\n- **FR-002 The archive.**" in cited and "FR-044 The plan." in cited
    assert "FR-001 The sty." in cited, "an unqualified id is the reviewed feature's"
    assert "FR-002 The well." not in cited, "385's same-numbered requirement is not handed for 375's"
    (other / "plan.md").write_text("# Plan\n\n**D18 - lands open.** An open box holds the landing unless the line names it.\n")
    (d / "plan.md").write_text(PLAN + "\n**D18 - the sty.** One predicate.\n")
    manifest = plan_bundle.build(d, "t2", [("## T05 - x", "## T05 - x\n\nFeature 375 plan D18 says so.\n")], {}, "how")
    cited = (manifest.parent / "spec-cited.md").read_text()
    assert "D18 - lands open." in cited and "D18 - the sty." not in cited, "T71: a decision from its own feature's plan"


def test_decide_refuses_a_section_quoting_the_gm_with_words_not_in_the_request(tmp_path: pathlib.Path) -> None:
    """Feature 385 T84 (plan D105): three of the evening's review rounds were lost to the GM's words missing from request.md."""
    sys.path.insert(0, str(script("plan_lint.py").parent))
    import plan_lint  # noqa: PLC0415

    d = tmp_path / "specs" / "385-x"
    d.mkdir(parents=True)
    (d / "request.md").write_text("> Please make sure to implement any obvious performance / tooling / process improvements along the way.\n")
    ok = 'The GM, 2026-10-18: "implement any obvious ... tooling ... improvements"; done.\n'
    bad = 'As the GM\'s words have it: "we either have or don\'t need tooling". And "this" is no attribution.\n'
    mention = 'a `"the GM"` mention, and WHY="awaiting the GM on it" - no quote of his.\n'
    assert plan_lint.refusal(d, ok + mention) == ""
    why = plan_lint.refusal(d, bad)
    assert "we either have or don't need tooling" in why and '"this"' not in why


def test_decide_refuses_an_item_4_figure_whose_sentence_carries_no_measurement() -> None:
    """Feature 385 T86 (plan D107): T81's "4.4 s (measured)" came back unreviewable, a round lost."""
    sys.path.insert(0, str(script("plan_lint.py").parent))
    import plan_lint  # noqa: PLC0415

    head = "### T05 Approach (checklist part A)\n\n"
    ok = head + "4. **World.** Yes - measured 2026-10-19 (two warm runs): it took `4.4 s`, round 2 of seed 45, at 01:30Z for T10.\n5. **x.** y\n"
    assert plan_lint.unlabeled_figure(ok) == ""
    assert plan_lint.unlabeled_figure(head + "4. **World.** See `make claims-owed F=385` and `dev/run-log/2026-10/x.json`.\n") == ""
    bad = ok.replace("5. **x.**", "Then it took 2.5 h.\n5. **x.**")
    assert plan_lint.unlabeled_figure(bad) == "Then it took 2.5 h.", "each sentence carries its own label"
    assert plan_lint.unlabeled_figure(head + "4. **World.** It takes `4.4 s` (measured).\n") != "", "a value in a code span is read"
    assert plan_lint.unlabeled_figure(head + "4. **World.** It takes 19 degrees, m:turn-angle.\n") == ""


def test_earlier_text_ruled_blocked_is_shown_as_blocked(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T114 (D142): T102's round-2 bundle showed its round-1 text, ruled BLOCKED, under "its last CLEAR verdict"."""
    sys.path.insert(0, str(script("plan_gate").parent))
    import plan_bundle  # noqa: PLC0415

    d = feature(tmp_path)
    monkeypatch.setattr(plan_bundle, "OUT", tmp_path / "out")
    m = plan_bundle.build(d, "T05", [("the section of T05", "now")], {"T05": ("then", "BLOCKED"), "T06": ("before", "")}, "how")
    text = (m.parent / "earlier.md").read_text()
    assert text.startswith("# Each changed block's text when last judged, with that verdict")
    assert '<!-- block "T05" verdict BLOCKED -->\nthen' in text and '"T06" verdict no verdict recorded' in text
    assert "CLEAR" not in text and "and the verdict it got" in m.read_text()

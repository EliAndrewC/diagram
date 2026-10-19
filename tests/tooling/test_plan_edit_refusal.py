"""`hm_planhold` (feature 385 T85, plan D106): a running plan review holds the section or blocks it reads; a write that would
change held text is refused, naming the review; a dead dispatch's hold alone yields to PLAN_EDIT_OK."""

from __future__ import annotations

import pathlib
import sys

import pytest

from tests._scripts import script

pytestmark = pytest.mark.tooling
sys.path.insert(0, str(script("hm_planhold.py").parent))
import hm_planhold as ph  # noqa: E402

PLAN = "# Plan\n\n## T05 - five\n\n### T05 Decisions\n\n**D10 - a rule.** the held decision text\n\n## T06 - six\n\nthe free section text\n"


def _root(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    plan = tmp / "specs" / "385-x" / "plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text(PLAN)
    return tmp, plan


def test_a_task_preflight_holds_its_section(tmp_path: pathlib.Path) -> None:
    root, plan = _root(tmp_path)
    state: dict = {}
    ph.hold(state, "t1", "read /tmp/l7r-check/plan-385-x-T05/MANIFEST.md and the files beside it", 100.0)
    ph.launched(state, "t1", "agent9")
    edit = {"file_path": str(plan), "old_string": "the held decision text", "new_string": "x"}
    msg = ph.refusal(state, root, "Edit", edit, 110.0, False)
    assert "T05's section" in msg and "agent agent9" in msg
    assert ph.refusal(state, root, "Edit", {**edit, "old_string": "the free section text"}, 110.0, False) == "", "T06 is free"
    assert ph.refusal(state, root, "Write", {"file_path": str(plan), "content": PLAN.replace("held", "new")}, 110.0, False)
    assert ph.refusal(state, root, "Write", {"file_path": str(plan), "content": PLAN + "\nmore\n"}, 110.0, False) == ""
    py = 'python3 - <<EOF\np="specs/385-x/plan.md"; t=open(p).read().replace("the held decision text", "y"); open(p,"w").write(t)\nEOF'
    assert ph.refusal(state, root, "Bash", {"command": py}, 110.0, False), "a held line in a Bash write"
    assert ph.refusal(state, root, "Bash", {"command": "sed -i 's/## T05 - five/## T05 - 5/' specs/385-x/plan.md"}, 110.0, False)
    assert ph.refusal(state, root, "Bash", {"command": "grep -n 'the held decision text' specs/385-x/plan.md"}, 110.0, False) == "", "a read"
    assert ph.refusal(state, root, "Edit", edit, 110.0, True), "a live review has no escape"
    ph.returned(state, "agent9")
    assert ph.refusal(state, root, "Edit", edit, 120.0, False) == "", "returned: the hold is gone"


def test_a_block_review_holds_its_blocks_and_a_dead_dispatch_yields_to_the_escape(tmp_path: pathlib.Path) -> None:
    root, plan = _root(tmp_path)
    bundle = tmp_path / "b" / "plan-385-x-blocks-T06-abc"
    bundle.mkdir(parents=True)
    (bundle / "blocks.md").write_text('<!-- block "## T06 - six" sha256 0 -->\n## T06 - six\n\nthe free section text\n')
    state: dict = {}
    ph.hold(state, "t2", f"read {bundle}/MANIFEST.md and the files beside it", 100.0)
    edit = {"file_path": str(plan), "old_string": "the free section text", "new_string": "x"}
    assert "1 block(s)" in ph.refusal(state, root, "Edit", edit, 101.0, False)
    late = 100.0 + ph.PENDING_S + 1  # never launched: dead
    assert ph.refusal(state, root, "Edit", edit, late, False) and ph.refusal(state, root, "Edit", edit, late, True) == ""

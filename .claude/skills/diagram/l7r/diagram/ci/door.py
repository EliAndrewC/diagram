"""The build-side door for the FULL sweep (FR-025, research R11).

The build cannot ask a question, so the prompt's answer travels in the TREE it tests: the
`permitted` entry `bypass-audit` writes to `dev/bypass-log/` when an operator answers the local
prompt, committed and shipped with the work. The door opens only to an entry that

    - has outcome `permitted` and a target naming the full sweep,
    - whose recorded commit is an ancestor of HEAD          (it authorized THIS work), and
    - is NOT an ancestor of origin/main                       (an entry inherited from main
                                                              authorizes nothing).

It never reads `REF_WHY` from the environment - that is the tier-2 override with extra steps, and
the 127 audit found it walked through three times. Forging an entry is an edit to a tracked file,
visible in the diff: the bar feature 127 set for every remaining bypass.
"""

from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path


def _is_ancestor(root: Path, commit: str, ref: str) -> bool:
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, ref], capture_output=True).returncode == 0


def check(root: Path, skill: Path, base_ref: str = "origin/main") -> tuple[bool, str]:
    """(may the full scope run, why)."""
    seen = 0
    for f in sorted(glob.glob(str(skill / "dev" / "bypass-log" / "*.json")), reverse=True):
        try:
            e = json.loads(Path(f).read_text(encoding="utf-8"))
        except ValueError:
            continue
        if "FULL" not in str(e.get("target", "")):
            continue
        seen += 1
        if e.get("outcome") != "permitted":
            continue
        commit = str(e.get("commit", ""))
        if not commit or not _is_ancestor(root, commit, "HEAD"):
            continue
        if _is_ancestor(root, commit, base_ref):
            continue
        return True, f"permitted entry {Path(f).name} (commit {commit}) authorizes FULL: {str(e.get('why', ''))[:80]}"
    if seen:
        return False, "no committed `permitted` FULL entry authored by THIS work (entries seen were cancelled, refused, or inherited from main) - answer the local prompt: make done FULL=1"
    return False, "no FULL entry in dev/bypass-log/ at all - the prompt was never answered for this work (run the merge action with FULL=1 in a terminal)"

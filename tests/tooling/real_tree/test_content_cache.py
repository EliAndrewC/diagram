"""THE REAL TREE's half of `tests/tooling/test_content_cache.py`: SC-002 over this repository itself.

Moved here by feature 444 T36 (the GM 2026-11-07: "any single test which takes even 100 milliseconds is fairly suspect"; then "please
proceed with all 3 of those things"): it checks a TOOL's behavior over the whole repository, and a scan of the whole repository reads
every file, so the gate's recorded reads selected it for every edit, a Rust one included. It is the tool's property, not the edited
file's: `tests/tooling/real_tree/` runs when the gate plans full (any `scripts/`, gate-configuration or tooling change - the tool's
own) and on `FULL=1`, never for an engine or a Rust increment (`pool_readers.rust_readers`, `tests/CLAUDE.md`).
"""

from __future__ import annotations

import subprocess

from tests.tooling.test_content_cache import ROOT, _same_on_and_off

ARGV = ["scripts/hooks/lib/hm_conflict.py", "--tracked", "."]


def test_the_whole_repository_s_conflicts_are_the_same_with_the_cache() -> None:
    """SC-002 over this repository itself, for the check that reads every tracked file (the pointer check is compiled since
    feature 449 T065 and keeps no cache).

    ...ON A TREE THAT HELD STILL (405 batch 8): the claims round and the landing cohort's record commit beside the gate (405 T48,
    T50), and a file tracked between the three runs read as the cache changing the answer (23,143 files, then 23,144). A run
    the tree moved under is asked again, at most twice; a real difference repeats on a still tree."""
    for _ in range(3):
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout
        try:
            _same_on_and_off(ARGV, ROOT)
            return
        except AssertionError:
            if subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout == head:
                raise
    _same_on_and_off(ARGV, ROOT)

"""The text of every plan block a review or a ruling found CLEAR, kept by its digest (feature 405 T102).

WHY. A plan record keeps each block's verdict and digest, not its text (amendment 11, D63: the record would otherwise copy the
plan). A block edited by a typo since its verdict is forgiven by finding its reviewed text in plan.md's GIT HISTORY
(`plan_gate.History`) - so a block reviewed, or accepted by the round arbiter, before it was committed could not be found, and
the decide guard refused a check on T100 that it let through minutes later, once a commit had put the text in history (batch
10, 2026-10-21, escaped with DECIDE_OK). The text is kept here when the verdict is written, so one reading holds whether or not
the reviewed version was ever committed.

Kept in the clone's git directory (`plan-seen/<digest>.txt`), never in the tree: it is a cache of what was reviewed, and a
clone that has none falls back to the history, as before.
"""

from __future__ import annotations

import pathlib
import subprocess
from collections.abc import Iterable

DIR = "plan-seen"


def _store(plan: pathlib.Path) -> pathlib.Path | None:
    got = subprocess.run(["git", "-C", str(plan.parent), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, check=False)
    return pathlib.Path(got.stdout.strip()) / DIR if got.returncode == 0 and got.stdout.strip() else None


def keep(plan: pathlib.Path, pairs: Iterable[tuple[str, str]]) -> None:
    """Keep each (digest, text) a verdict was written at."""
    store = _store(plan)
    if store is None:
        return
    store.mkdir(parents=True, exist_ok=True)
    for sha, text in pairs:
        (store / f"{sha}.txt").write_text(text, encoding="utf-8")


def recall(plan: pathlib.Path, sha: str) -> str | None:
    """The text a block had when a verdict was written at `sha`, or None when none was kept."""
    store = _store(plan)
    f = store / f"{sha}.txt" if store is not None and sha.isalnum() else None
    return f.read_text(encoding="utf-8") if f is not None and f.is_file() else None

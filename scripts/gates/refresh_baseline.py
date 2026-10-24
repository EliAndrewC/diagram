#!/usr/bin/env python3
"""refresh_baseline.py - the incremental gate's baseline refreshed off the landing's path (feature 415 T05, D8; FR-006).

    refresh_baseline.py <clone root> <commit> "<reason>"     what `make land` starts, detached, after a push

WHY (the GM 2026-10-24, item 6: "run what is reached, however much, and refresh the baseline in the background"). The gate's
baseline is the LAST FULL RUN (`l7r/diagram/ci/incremental.py`), so every incremental landing selects every change since it,
and the selection grows - 1,492, then 1,965, then 2,657 tests over three runs (feature 415 `research.md` R2). A full run resets
it, but a full run on a landing's path costs ~200 s. So after a push whose gate selected at least `REFRESH_FRACTION` of its
baseline (`land.py`), this runs one full gate where nothing waits on it:

1. under a lock in the git common dir (one at a time; a later refresh waits for the running one);
2. in a detached worktree at the pushed commit - never in the clone, whose next edit would move the tree under the run;
3. `make done INCR_FORCE="refresh: ..."` there: a fresh worktree has no verification to short-circuit on, and the reason is the
   run record's `plan_reason` (D2);
4. when it is green, its `gate-baseline/` replaces the clone's - each coverage file path rewritten from the worktree's root to
   the clone's (the coverage data holds absolute paths; the manifest, the closures and the tooling reads are repository-
   relative) - unless the clone's baseline was saved after the refresh started (a newer full run stands);
5. its run record is copied into the clone's `dev/run-log/` and committed path by path; the worktree is removed.

Everything it does goes to `<clone git dir>/land-refresh.log`.
"""

from __future__ import annotations

import fcntl
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASELINE = "gate-baseline"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout.strip()


def rewrite_paths(db: Path, old_root: str, new_root: str) -> int:
    """Every coverage file path under `old_root` moved under `new_root`; returns how many."""
    con = sqlite3.connect(str(db))
    try:
        old, new = old_root.rstrip("/") + "/", new_root.rstrip("/") + "/"
        cur = con.execute("UPDATE file SET path = ? || substr(path, ?) WHERE substr(path, 1, ?) = ?", (new, len(old) + 1, len(old), old))
        con.commit()
        return cur.rowcount
    finally:
        con.close()


def install(src: Path, dst: Path, wt_root: Path, clone_root: Path, started: float) -> str:
    """The worktree's baseline into the clone's place, paths rewritten - or why not."""
    if (dst / "manifest.json").is_file() and (dst / "manifest.json").stat().st_mtime > started:
        return "the clone's baseline was saved after the refresh started - it stands"
    if not (src / "coverage.db").is_file() or not (src / "manifest.json").is_file():
        return "the refresh saved no baseline"
    staged = Path(tempfile.mkdtemp(prefix=".refresh-", dir=dst.parent))
    shutil.rmtree(staged)
    shutil.copytree(src, staged)
    n = rewrite_paths(staged / "coverage.db", str(wt_root), str(clone_root))
    old = dst.with_name(dst.name + ".replaced")
    shutil.rmtree(old, ignore_errors=True)
    if dst.exists():
        os.replace(dst, old)
    os.replace(staged, dst)
    shutil.rmtree(old, ignore_errors=True)
    return f"installed, {n} coverage path(s) rewritten"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    clone, commit, reason = Path(argv[0]).resolve(), argv[1], argv[2]
    gd = Path(git(clone, "rev-parse", "--absolute-git-dir"))
    common = Path(git(clone, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    with (common / "l7r-refresh.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # one at a time; a later refresh waits
        started = time.time()
        wt = Path(tempfile.mkdtemp(prefix="l7r-refresh-"))
        shutil.rmtree(wt)
        try:
            if subprocess.run(["git", "-C", str(clone), "worktree", "add", "-q", "--detach", str(wt), commit]).returncode:
                print(f"refresh: no worktree at {commit}")
                return 1
            rc = subprocess.run(["make", "--no-print-directory", "done", f"INCR_FORCE={reason}"], cwd=wt).returncode
            if rc:
                print(f"refresh: the full gate at {commit} was red (exit {rc}) - the clone's baseline stands")
                return rc
            wt_gd = Path(git(wt, "rev-parse", "--absolute-git-dir"))
            print(f"refresh: {install(wt_gd / BASELINE, gd / BASELINE, wt, clone, started)}")
            rec = wt_gd / "last-run-record"
            if rec.is_file() and Path(rec.read_text().strip()).is_file():
                src = Path(rec.read_text().strip())
                dst = clone / src.relative_to(wt)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                subprocess.run(["git", "-C", str(clone), "add", "--", str(dst.relative_to(clone))])
                subprocess.run(["git", "-C", str(clone), "commit", "-q", "-m", f"the baseline refresh's run record ({reason})", "--", str(dst.relative_to(clone))])
            return 0
        finally:
            subprocess.run(["git", "-C", str(clone), "worktree", "remove", "--force", str(wt)], capture_output=True)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406: every tool records its run

    sys.exit(usage_log.exited("refresh_baseline", main(sys.argv[1:])))

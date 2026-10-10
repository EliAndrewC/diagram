#!/usr/bin/env python3
"""Replay recorded deltas through the OLD owing and the NEW (feature 375, SC-001).

SC-001: replaying feature 372's recorded deltas for waves 106, 108 and 111, the `modal-depiction` units owed in full fall by at
least two thirds and the `impl-drift` claims owed by at least four fifths. A delta is one commit against its parent, as the
history recorded it. For each:

- OLD - the commit's own scripts and engine, in a detached worktree of the commit, with the parent's claims index: what that
  delta owed when it was made - owed at the commit less what was already owed at the parent (a claim owed earlier and
  answered in this commit belongs to the earlier delta).
- NEW - this tree's scripts and engine run over the same worktree: the claims index of the parent migrated as
  `claims-backfill-sections` migrates it (FR-002), and the modal units split into those owed in full (their own words moved)
  and those owed only a triage (a page they name moved, FR-001). A triage-only unit is owed its check only if a triage names it,
  which is a judgment: the replay writes each delta's triage bundle beside its figures so the triage can be run on it.

    replay_owing.py <rev> [<rev> ...] [--out DIR]     one JSON line per commit, then the totals
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPARSE = ("l7r", "scripts", "docs", "research/questions", "research/assets", "dev/claims-index.json", "dev/claims-pages.json",
          "dev/claims-deferred.json", "dev/modals.md", "dev/modals-particular.md", "pyproject.toml")


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout


def worktree(rev: str, base: Path) -> Path:
    """A sparse detached worktree of `rev` under `base`, made once."""
    wt = base / rev[:10]
    if not wt.is_dir():
        git("worktree", "add", "-q", "--no-checkout", "--detach", str(wt), rev)
        git("sparse-checkout", "set", "--no-cone", *SPARSE, cwd=wt)
        git("checkout", "-q", "--detach", rev, cwd=wt)
    return wt


def py(code: str, *args: str, cwd: Path) -> str:
    """Run a snippet in a fresh interpreter (the old and the new engine cannot share one process)."""
    return subprocess.run([sys.executable, "-c", code, *args], capture_output=True, text=True, check=True, cwd=cwd).stdout


_OLD_MODALS = """
import sys, json; sys.path.insert(0, 'scripts/record'); import modal_owed as mo
print(json.dumps([[s, w] for s, w, _f in mo.owed(__import__('pathlib').Path('.').resolve(), sys.argv[1])]))
"""
_NEW_MODALS = """
import sys, json, pathlib; sys.path.insert(0, sys.argv[2] + '/scripts/record'); import modal_owed as mo, modal_triage as mt
rows = mo.owed(pathlib.Path('.').resolve(), sys.argv[1])
print(json.dumps([[s, w, mt.triage_only(w)] for s, w, _f in rows]))
"""
_TRIAGE = """
import os, sys, pathlib; sys.path.insert(0, sys.argv[2] + '/scripts/record'); import modal_triage as mt
manifest, n = mt.bundle(pathlib.Path('.').resolve(), pathlib.Path(sys.argv[3]), sys.argv[1])
print(n)
"""
_CLAIMS = """
import sys, json, pathlib
scripts = sys.argv[1]; sys.path.insert(0, scripts + '/scripts/record'); import claims as cx
root = pathlib.Path('.').resolve(); qdir = root / cx.QUESTIONS
index = json.loads(pathlib.Path(sys.argv[2]).read_text()); store = json.loads(pathlib.Path(sys.argv[3]).read_text())
cur = cx.current(root)
if sys.argv[4] == 'migrate':
    cx.backfill_sections(cur, index, store)
    pathlib.Path(sys.argv[2]).write_text(json.dumps(index)); pathlib.Path(sys.argv[3]).write_text(json.dumps(store))
    print('[]')
else:
    print(json.dumps(cx.owed(cur, index, qdir, store)))
"""


def replay(rev: str, base: Path, triage: bool = False) -> dict:
    parent = git("rev-parse", f"{rev}^").strip()
    wt, wp = worktree(rev, base), worktree(parent, base)
    old_modals = json.loads(py(_OLD_MODALS, parent, cwd=wt))
    new_modals = json.loads(py(_NEW_MODALS, parent, str(ROOT), cwd=wt))
    idx, store = base / f"{rev[:10]}.index.json", base / f"{rev[:10]}.store.json"
    for src, dst in ((wp / "dev/claims-index.json", idx), (wp / "dev/claims-pages.json", store)):
        shutil.copyfile(src, dst) if src.is_file() else dst.write_text("{}")
    # what the DELTA owes: owed at the commit, less what was already owed at its parent (both against the parent's index) -
    # a claim owed earlier and answered in this very commit is the earlier delta's, not this one's
    old_was = {k for k, _w in json.loads(py(_CLAIMS, str(wp), str(idx), str(store), "owed", cwd=wp))}
    old_claims = [r for r in json.loads(py(_CLAIMS, str(wt), str(idx), str(store), "owed", cwd=wt)) if r[0] not in old_was]
    py(_CLAIMS, str(ROOT), str(idx), str(store), "migrate", cwd=wp)
    new_was = {k for k, _w in json.loads(py(_CLAIMS, str(ROOT), str(idx), str(store), "owed", cwd=wp))}
    new_claims = [r for r in json.loads(py(_CLAIMS, str(ROOT), str(idx), str(store), "owed", cwd=wt)) if r[0] not in new_was]
    full = lambda rows: [k for k, why in rows if why not in ("triage", "section triage")]  # noqa: E731
    dep = "modal-depiction:"
    if triage and any(t for s, _w, t in new_modals if s.startswith("modal-depiction:")):
        env = {**__import__("os").environ, "RECORD_CHECKS_DIR": str(base / f"store-{rev[:10]}")}
        subprocess.run([sys.executable, "-c", _TRIAGE, parent, str(ROOT), str(base / f"triage-{rev[:10]}")], cwd=wt, env=env,
                       check=True, capture_output=True)
    return {
        "rev": rev[:10],
        "subject": git("log", "-1", "--format=%s", rev).strip()[:90],
        "modal_depiction_old": sum(1 for s, _w in old_modals if s.startswith(dep)),
        "modal_depiction_new_full": sum(1 for s, _w, t in new_modals if s.startswith(dep) and not t),
        "modal_depiction_new_triage": sum(1 for s, _w, t in new_modals if s.startswith(dep) and t),
        "impl_drift_old": len(full(old_claims)),
        "impl_drift_new_full": len(full(new_claims)),
        "impl_drift_new_triage": len(new_claims) - len(full(new_claims)),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("revs", nargs="+")
    ap.add_argument("--out", default="/tmp/l7r-replay")
    ap.add_argument("--triage", action="store_true", help="write each commit's pop-up triage bundle under OUT/triage-<rev>")
    a = ap.parse_args(argv)
    base = Path(a.out)
    base.mkdir(parents=True, exist_ok=True)
    totals: dict[str, int] = {}
    try:
        for rev in a.revs:
            row = replay(git("rev-parse", rev).strip(), base, a.triage)
            print(json.dumps(row), flush=True)
            for k, v in row.items():
                if isinstance(v, int):
                    totals[k] = totals.get(k, 0) + v
    finally:
        for wt in base.iterdir():
            if wt.is_dir() and (wt / ".git").is_file():
                subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)
    print(json.dumps({"totals": totals}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

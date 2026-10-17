#!/usr/bin/env python3
"""What `make land-tooling`'s tooling tests cost with the clone's passes reused, against without (feature 383 amendment 1,
SC-010) - the measurement as a command, so it can be taken again.

    tooling_reuse_time.py [--root <clone>] [--json <out>]

It records the clone's passes on its HEAD (`make test-file FILE=tests/tooling`), builds a detached worktree at that HEAD -
the checkout `make land-tooling` builds - and times `make test-file FILE=tests/tooling` there with `L7R_TEST_DEPS=reuse`, then
with the reuse off, back to back; it prints both, the tests each ran, and the load. The worktree is removed on every exit. It
also prints, from the clone's kept passes, how many tooling test files always run and which program makes each run.
The clone's tree must be clean (what it records must be what the worktree holds).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[float, str, int]:
    t = time.monotonic()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, env={**os.environ, **(env or {})})
    return time.monotonic() - t, p.stdout + p.stderr, p.returncode


def _passed(out: str) -> int:
    m = re.findall(r"(\d+) passed", out)
    return int(m[-1]) if m else 0


def always_run(store: Path) -> dict[str, object]:
    """From the kept passes (per test since 383 amendment 5): how many tests and test files are kept, and how many tests always run
    (a program started against the repository whose reads are not known - by the test, its file or the session), by program."""
    try:
        kept = json.loads(store.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {"files": 0, "tests": 0, "always_run": 0, "by_cause": {}}
    files, tests, session = kept.get("files", {}), kept.get("tests", {}), kept.get("session", {})
    causes: dict[str, int] = {}
    always = 0
    for n, e in tests.items():
        why = set(e.get("opaque") or []) | set(files.get(n.split("::", 1)[0], {}).get("entry", {}).get("opaque") or []) | set(session.get("opaque") or [])
        if why:
            always += 1
            for c in why:
                causes[c] = causes.get(c, 0) + 1
    return {"files": len(files), "tests": len(tests), "always_run": always, "by_cause": dict(sorted(causes.items()))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    root = Path(subprocess.run(["git", "-C", args.root, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
    if subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip():
        print("tooling-reuse-time: the clone has uncommitted changes - commit first, so the worktree holds what is recorded", file=sys.stderr)
        return 2
    test = ["make", "--no-print-directory", "test-file", "FILE=tests/tooling"]
    _t, out, rc = _run(test, root, {"L7R_TEST_DEPS": "record"})
    if rc != 0:
        print(out[-2000:], file=sys.stderr)
        return 1
    common = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    kept = always_run(Path(common) / "l7r-cache" / "tooling-test-passes.json")
    wt = root.parent / f"{root.name}-reuse-measure"
    subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(wt)], capture_output=True)
    subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", "--detach", str(wt), "HEAD"], check=True)
    try:
        reuse_s, reuse_out, rc1 = _run(test, wt, {"L7R_TEST_DEPS": "reuse"})
        full_s, full_out, rc2 = _run(test, wt, {"L7R_TEST_DEPS": "off"})
    finally:
        subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(wt)], capture_output=True)
    row = {
        "reuse_s": round(reuse_s, 2),
        "reuse_ran": _passed(reuse_out),
        "full_s": round(full_s, 2),
        "full_ran": _passed(full_out),
        "load": round(os.getloadavg()[0], 1),
        "ok": rc1 == 0 and rc2 == 0,
        **kept,
    }
    print(f"with reuse {row['reuse_s']} s ({row['reuse_ran']} tests ran), without {row['full_s']} s ({row['full_ran']}), load {row['load']}")
    print(f"tooling tests kept {kept['tests']} in {kept['files']} files, always run {kept['always_run']} (by program: {kept['by_cause']})")
    if args.json:
        Path(args.json).write_text(json.dumps(row, indent=1) + "\n", encoding="utf-8")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

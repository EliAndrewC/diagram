#!/usr/bin/env python3
"""cover_changed.py - the coverage floor asked of the engine modules a change touched, in seconds (the GM 2026-10-24).

    cover_changed.py [--base origin/main]      exit 1, naming each module and its uncovered added lines; 0 when none

WHY. T135's landing ran `make done` for five minutes and failed on four lines of `knots.py` its own tests did not reach; the
gate's coverage floor is the only place coverage was asked. The GM: "we can check coverage in the specific files that changed,
and then that saves a lot of time." So the lines the change ADDED to each engine module (`git diff -U0` against the merge base
with `--base`, the working tree included) are asked of that module's mirrored test directory (`tests/` mirrors the source:
`l7r/diagram/hamletgen/ways/knots.py` -> `tests/hamletgen/ways/`, the whole directory, as `make test-file` runs it), with
coverage on, the map-rolling tests left out (`-m "not rolls_map"`: seconds, not minutes).

WHAT IT CANNOT SEE. A line only a roll or a test in another directory reaches reads as uncovered here though the gate's floor
counts it: `make land` refuses on it, and the escape is `COVER_OK="<reason>"`, logged by the make target. Lines the change did
not add are never asked - the gate's floor still holds the whole engine.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

#: the engine modules this asks of: `l7r/**/*.py` (the gate's floor, `[tool.coverage.run]`)
ENGINE_PY = re.compile(r"^l7r/.*\.py$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def added_lines(diff: str) -> dict[str, set[int]]:
    """Each file's added line numbers, read from a `git diff -U0` (its `+++ b/<path>` headers and `@@` hunks)."""
    out: dict[str, set[int]] = {}
    path = None
    for ln in diff.splitlines():
        if ln.startswith("+++ "):
            path = ln[6:] if ln.startswith("+++ b/") else None
        elif path and (m := HUNK.match(ln)):
            start, count = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            out.setdefault(path, set()).update(range(start, start + count))
    return {p: s for p, s in out.items() if s}


def mirrored(root: Path, path: str) -> str:
    """The test directory that mirrors an engine module: `l7r/diagram/<pkg>/<mod>.py` -> `tests/<pkg>/`, climbing to the nearest
    one that exists; `tests` at worst."""
    rel = Path(path).relative_to("l7r/diagram") if path.startswith("l7r/diagram/") else Path(path).relative_to("l7r")
    d = Path("tests") / rel.parent
    while d != Path("tests") and not (root / d).is_dir():
        d = d.parent
    return str(d)


def uncovered(root: Path, added: dict[str, set[int]]) -> dict[str, list[int]]:
    """Each changed module's added lines its mirrored tests leave unrun (coverage's own exclusions honored)."""
    dirs = sorted({mirrored(root, p) for p in added})
    sources = sorted({str(Path(p).parent) for p in added})
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "cover.json"
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-n",
            "4",
            "--dist",
            "worksteal",
            "-p",
            "no:cacheprovider",
            "-m",
            "not rolls_map",
            "--cov-fail-under=0",
            *(f"--cov={s}" for s in sources),
            f"--cov-report=json:{report}",
            *dirs,
        ]
        done = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if not report.is_file():  # pytest wrote no report: say why, never pass silently
            raise RuntimeError("cover-changed: the tests wrote no coverage report - " + (done.stdout + done.stderr).strip()[-800:])
        files = json.loads(report.read_text(encoding="utf-8")).get("files", {})
    out = {}
    for path, lines in added.items():
        missing = set((files.get(path) or {}).get("missing_lines") or []) & lines
        if missing:
            out[path] = sorted(missing)
    return out


def main(argv: list[str]) -> int:
    base = argv[argv.index("--base") + 1] if "--base" in argv else "origin/main"
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip() or ".")
    merge = git(root, "merge-base", base, "HEAD").strip() or base
    added = {p: s for p, s in added_lines(git(root, "diff", "-U0", merge, "--", "l7r/")).items() if ENGINE_PY.match(p) and (root / p).is_file()}
    if not added:
        return 0
    missing = uncovered(root, added)
    for path, lines in missing.items():
        print(f"cover-changed: {path} - added lines its tests ({mirrored(root, path)}) do not reach: {', '.join(map(str, lines))}")
    if missing:
        print(
            "cover-changed: a test for each, in the mirrored file, before the gate's five minutes find it (`make cover-changed` "
            "asks again in seconds); a line only a roll or another directory reaches: COVER_OK=\"<reason>\""
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("cover_changed", main(sys.argv[1:])))

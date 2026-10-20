#!/usr/bin/env python3
"""The gate's first phase - the cheap checks that turned feature 372's gates red, in seconds, before the expensive ones
(feature 375, FR-004, plan D14).

WHY. Measured from 372's wave 106 (2026-10-10): its gate went red about six times, every cause one a cheap check finds - a file
edited mid-gate, `building-programs.md` stale twice, stub pointers in found rows, two untested lines. Each red cost a gate run.
So `make done` begins here and stops here on a failure:

1. THE DERIVED FILES regenerated - `make docs`, `make building-programs`, `make glossary` - and any that moved named, to commit;
2. THE RECORD builds (`make record CHECK=1`) and its pointers resolve (`check-research-pointers.py`);
3. THE QUICK TIER (`make quick FROM_PREFLIGHT=1`: lint, types, spec-lint on the delta, the file-size bar, house style, the unit
   tests - its TIME not judged here: a green but slow quick after a merge of main stopped a gate whose tests all passed);
4. THE CHANGED ENGINE LINES covered - the quick tree run once more with coverage over just the engine files the delta changed,
   and every changed line it leaves unrun named. A line in a module OFF the hamlet path (no rolled map reaches it; the path
   is `tools/claims.scope`, the import graph of hamlet generation) stops the preflight: only a unit test can cover it, and
   the gate's 100% floor would refuse it minutes later. A line ON the path may be reached only by a rolled map, which the
   preflight does not roll, so it is reported and left to the gate (the floor judges it there).

And THE TREE HELD STILL: the gate hashes every tracked file that differs from HEAD (and HEAD itself) when it starts and again
before it reports green, and a difference fails it, naming the file - 372's wave 106 went red once on a file edited mid-gate,
and a green run over a tree that moved under it vouches for nothing.

    preflight.py [--root DIR] [--skip-quick]
    preflight.py --tree-snap FILE | --tree-check FILE
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
DERIVED = ("docs", "building-programs", "glossary")
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)


def run(cmd: list[str], root: Path, quiet: bool = True) -> int:
    r = subprocess.run(cmd, cwd=root, capture_output=quiet, text=True, check=False)
    if r.returncode and quiet:
        sys.stdout.write((r.stdout or "")[-3000:] + (r.stderr or "")[-3000:])
    return r.returncode


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else ""


def base(root: Path) -> str:
    return git(root, "merge-base", "HEAD", "origin/main").strip() or git(root, "rev-parse", "HEAD").strip()


def changed_lines(root: Path) -> dict[str, set[int]]:
    """Engine `.py` files the delta changed (against the merge base, working tree included), with the lines it added or changed."""
    out: dict[str, set[int]] = {}
    diff = git(root, "diff", "-U0", base(root), "--", "l7r")
    for chunk in re.split(r"^diff --git ", diff, flags=re.M)[1:]:
        m = re.search(r"^\+\+\+ b/(\S+\.py)$", chunk, re.M)
        if not m:
            continue
        lines = out.setdefault(m.group(1), set())
        for h in _HUNK.finditer(chunk):
            start, n = int(h.group(1)), int(h.group(2) or 1)
            lines.update(range(start, start + n))
    # `ci/` is not engine code (feature 132 FR-025: a ci-only change is DIRECT) and its tests are tooling tests, which the quick
    # tier never runs - so its lines are the gate's to judge, not the preflight's
    return {f: ls for f, ls in out.items() if ls and not f.startswith("l7r/diagram/ci/")}


def uncovered(cov: dict, changed: dict[str, set[int]]) -> dict[str, list[int]]:
    """Each changed file's changed lines that coverage counted as statements and no quick test ran."""
    out = {}
    files = cov.get("files", {})
    for f, lines in changed.items():
        data = files.get(f) or next((v for k, v in files.items() if k.endswith(f)), None)
        missing = sorted(set((data or {}).get("missing_lines", [])) & lines) if data else []
        if missing:
            out[f] = missing
    return out


def hamlet_path(root: Path) -> set[str]:
    """The engine files hamlet generation imports, directly or through others (`tools/claims.scope`)."""
    sys.path.insert(0, str(root))
    from l7r.diagram.tools import claims  # noqa: PLC0415

    return {str(p.relative_to(root)) for p in claims.scope(root).values()}


def outside_quick(root: Path) -> set[str]:
    """Engine files a test OUTSIDE the quick tier reaches - a `tooling`-marked module under `tests/tools/`, or a town or city
    tier test, whether or not a quick test reaches the file too - found by the mirrored layout (`tests/<tree>/a/test_b.py` tests `l7r/diagram/a/b.py`). A line only
    those reach is the gate's to judge (the plan review of amendment 2: `citybudget.py`'s lines 358 and 432, the audits)."""
    out: set[str] = set()
    tests = list((root / "tests" / "tier_town").rglob("test_*.py")) + list((root / "tests" / "tier_city").rglob("test_*.py"))
    tests += [t for t in (root / "tests" / "tools").glob("test_*.py") if "pytestmark = pytest.mark.tooling" in t.read_text(encoding="utf-8")]
    for t in tests:
        rel = t.relative_to(root / "tests").parts[1:] if t.parts[-2] != "tools" or "tier_" in str(t) else ("tools", t.name)
        stem = Path(*rel[:-1], rel[-1][len("test_"):-len(".py")])
        for cand in (Path("l7r/diagram") / f"{stem}.py", Path("l7r/diagram") / stem / "__init__.py"):
            if (root / cand).is_file():
                out.add(str(cand))
        if (root / "l7r/diagram" / stem).is_dir():
            out.update(str(f.relative_to(root)) for f in (root / "l7r/diagram" / stem).rglob("*.py"))
    return out


def coverage_step(root: Path, changed: dict[str, set[int]], workers: str) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """(off-path uncovered lines, on-path uncovered lines) from one quick-tree run with coverage over the changed files."""
    if not changed:
        return {}, {}
    mods = sorted({f[:-3].replace("/", ".").removesuffix(".__init__") for f in changed})
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "cov.json"
        cmd = [sys.executable, "-m", "pytest", "-q", "-n", workers, "--dist", "worksteal", "-p", "no:cacheprovider",
               "-m", "not rolls_map and not tooling", "--no-cov-on-fail", f"--cov-report=json:{report}",
               *[f"--cov={m}" for m in mods], "tests", "--ignore=tests/tier_town", "--ignore=tests/tier_city",
               "--ignore=tests/gate", "--ignore=tests/full", "--ignore=tests/tooling"]
        env = {**os.environ, "COVERAGE_FILE": str(Path(tmp) / ".coverage")}
        subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False, env=env)
        cov = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
    gaps = uncovered(cov, changed)
    path = (hamlet_path(root) | outside_quick(root)) if gaps else set()  # where a test the quick tier skips may reach a line
    return {f: v for f, v in gaps.items() if f not in path}, {f: v for f, v in gaps.items() if f in path}


#: tracked files the gate itself writes, measured on a gate run (feature 375 T23) - never a moved file of the session's
GATE_WRITES: frozenset[str] = frozenset()


def tree(root: Path) -> dict[str, str]:
    """HEAD and every tracked file that differs from it, by content hash."""
    out = {"HEAD": git(root, "rev-parse", "HEAD").strip()}
    paths = [p for p in git(root, "diff", "--name-only", "HEAD").splitlines() if p and p not in GATE_WRITES]
    if paths:
        r = subprocess.run(["git", "-C", str(root), "hash-object", "--stdin-paths"], input="\n".join(paths), capture_output=True,
                           text=True, check=False)
        out.update(zip(paths, (r.stdout.split() if r.returncode == 0 else ["?"] * len(paths)), strict=False))
    return out


def tree_moved(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


#: what a pool map's roll writes beside its generator (feature 385 T87, plan D108)
_MAP_OUTPUTS = (".json", ".png", ".svg", ".html", ".webp")


def rolled_outputs(root: Path, census: Path) -> set[str]:
    """The map outputs (beside each `.gen.py`) of every pool map the gate's own run rolled, by its roll census (feature 385 T87,
    plan D108; T10's gate rolled Kuwabata and then failed on its own `kuwabata.json` as a tree move)."""
    out: set[str] = set()
    try:
        lines = census.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        gen = Path(str(r.get("gen") or "")) if r.get("kind") == "roll" and r.get("gen") else None
        if gen is None or not gen.name.endswith(".gen.py"):
            continue
        stem = gen.name[: -len(".gen.py")]
        try:
            rel = gen.resolve().parent.relative_to(root.resolve())
        except ValueError:
            continue
        out |= {f"{rel.as_posix()}/{stem}{ext}" for ext in _MAP_OUTPUTS}
    return out


def stray_probes(root: Path) -> list[str]:
    """Probe test files a diagnosis left in the tree (`tests/**/test_zz_probe*.py`): each runs in the full suite and can turn it
    red on its own, and the round arbiter found four in pytest's failure list on red-gate@2026-10-17T17:21:08Z (feature 385,
    its tooling fix) - so the gate refuses to start while any stands."""
    return sorted(str(p.relative_to(root)) for p in (root / "tests").rglob("test_zz_probe*.py"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--skip-quick", action="store_true", help="the quick tier already ran (a test of the other steps)")
    ap.add_argument("--workers", default=os.environ.get("XDIST_WORKERS", "4"))
    ap.add_argument("--tree-snap", default="")
    ap.add_argument("--tree-check", default="")
    ap.add_argument("--census", default="", help="the roll census the gate wrote (default <root>/.git/roll-census.jsonl)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if a.tree_snap:
        Path(a.tree_snap).write_text(json.dumps(tree(root)), encoding="utf-8")
        return 0
    if a.tree_check:
        try:
            before = json.loads(Path(a.tree_check).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return 0
        moved = tree_moved(before, tree(root))
        rerolled = sorted(set(moved) & rolled_outputs(root, Path(a.census) if a.census else root / ".git" / "roll-census.jsonl"))
        moved = [m for m in moved if m not in rerolled]
        if rerolled:
            print("preflight: re-rolled by the gate - commit them (feature 385 T87):\n  " + "\n  ".join(rerolled))
        if moved:
            print("GATE NOT GREEN: the tree moved while the gate ran - it vouches for none of it (feature 375 FR-004):\n  "
                  + "\n  ".join("HEAD (a commit or a checkout)" if m == "HEAD" else m for m in moved))
            return 1
        return 0
    if probes := stray_probes(root):
        print("preflight: probe test files are left in the tree - delete them; the gate stops here (feature 385):\n  " + "\n  ".join(probes))
        return 1
    t0 = time.monotonic()
    marks: list[tuple[str, float]] = []

    def mark(step: str) -> None:
        marks.append((step, time.monotonic()))

    before = git(root, "status", "--porcelain")
    for target in DERIVED:
        if run(["make", "--no-print-directory", target], root):
            print(f"preflight: `make {target}` failed - the gate stops here (feature 375 FR-004)")
            return 1
    mark("derived")
    moved = sorted(set(git(root, "status", "--porcelain").splitlines()) - set(before.splitlines()))
    moved = [m for m in moved if m[3:].strip()]
    if moved:
        print("preflight: regenerated, commit them with the change:\n  " + "\n  ".join(m[3:] for m in moved))
    for cmd, what in ((["make", "--no-print-directory", "record", "CHECK=1"], "the record does not build"),
                      ([sys.executable, "scripts/gates/check-research-pointers.py", str(root)], "a research pointer does not resolve")):
        if run(cmd, root):
            print(f"preflight: {what} - the gate stops here (feature 375 FR-004)")
            return 1
    mark("record and pointers")
    if not a.skip_quick and run(["make", "--no-print-directory", "quick", "FROM_PREFLIGHT=1"], root, quiet=False):
        print("preflight: `make quick` failed - the gate stops here (feature 375 FR-004)")
        return 1
    mark("quick")
    off, on = coverage_step(root, changed_lines(root), a.workers)
    mark("coverage of the changed lines")
    prev = t0
    steps = []
    for step, t in marks:
        steps.append(f"{step} {t - prev:.0f} s")
        prev = t
    print("preflight: " + ", ".join(steps))
    for f, ls in sorted(on.items()):
        print(f"preflight: {f} lines {ls[:12]} - no quick test runs them; a rolled map or a test the quick tier skips may (the gate's floor judges)")
    if off:
        for f, ls in sorted(off.items()):
            print(f"preflight: {f} lines {ls[:12]} - changed, run by no quick test, and off the hamlet path: only a unit test covers them")
        print("preflight: the gate stops here - the 100% floor would refuse these minutes from now (feature 375 FR-004)")
        return 1
    print(f"preflight: clean in {time.monotonic() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    raise SystemExit(usage_log.exited("preflight", main()))

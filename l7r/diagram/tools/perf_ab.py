"""Two engines timed against each other - the time evidence a performance change reports, never a gate (feature 435).

`make perf-ab A=<commit> B=<commit>` checks each commit out in a detached worktree and takes the reference snapshot with its
scaling legs (`make perf SCALING=1`) in each, ALTERNATING A, B, A, B ... `N` times, so a change in the host's load falls on
both arms alike. Per size and seed it prints each arm's best time and the spread of its runs (best to worst), and the calls
of each (counted once, in each arm's first run; later runs skip the counting pass, `L7R_PERF_NO_COUNTS`).

It refuses nothing and decides nothing: a timing depends on load and on which core runs it, so the spread is printed beside
every best, and the reader judges (docs/performance-checklist.md, the GM 2026-10-27: "timings are not a gate, but improving
timings is the goal of any performance improvement ticket").
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.tools import perf_profile

Run = Callable[[str, str, bool], dict[str, Any]]


def snapshot(tree: str, label: str, counted: bool) -> dict[str, Any]:
    """One snapshot in `tree` with its scaling legs, read back from the record it writes."""
    env = {**os.environ, **({} if counted else {"L7R_PERF_NO_COUNTS": "1"})}
    subprocess.run(["make", "-C", tree, "--no-print-directory", "perf", f"LABEL={label}", "SCALING=1"], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    path = sorted(glob.glob(os.path.join(tree, "dev", "perf-log", f"*-{label}-*.json")))[-1]
    with open(path, encoding="utf-8") as fh:
        return dict(json.load(fh))


def legs(snap: Mapping[str, Any]) -> dict[tuple[int, int], tuple[float | None, int]]:
    """(households, seed) -> (seconds, calls) of every timed leg of a snapshot."""
    out: dict[tuple[int, int], tuple[float | None, int]] = {}
    for leg in [*snap.get("rows", []), *snap.get("scaling", [])]:
        out[(int(leg["asked"]), int(leg["seed"]))] = (leg.get("seconds"), sum((leg.get("calls") or {}).values()))
    return out


def compare(runs: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[str]:
    """The table: per size and seed, each arm's best and spread (in seconds) and its calls; a refused leg named."""
    a, b = runs["A"], runs["B"]
    keys = sorted({k for s in [*a, *b] for k in legs(s)})
    lines = [f"{'households, seed':>17}  {'A best':>7} {'spread':>6}  {'B best':>7} {'spread':>6}  {'time':>6}  {'A calls':>11} {'B calls':>11}  {'calls':>6}"]
    for k in keys:
        cells = []
        for arm in (a, b):
            ts = [t for s in arm if (t := legs(s).get(k, (None, 0))[0]) is not None]
            calls = next((c for s in arm if (c := legs(s).get(k, (None, 0))[1])), 0)
            cells.append((min(ts) if ts else None, (max(ts) - min(ts)) if ts else None, calls))
        (ab, asp, ac), (bb, bsp, bc) = cells
        if ab is None or bb is None:
            lines.append(f"{str(k):>17}  {'refused' if ab is None else f'{ab:7.2f}':>7} {'':>6}  {'refused' if bb is None else f'{bb:7.2f}':>7}")
            continue
        dt = f"{100 * (bb - ab) / ab:+5.0f}%" if ab else ""
        dc = f"{100 * (bc - ac) / ac:+5.0f}%" if ac else ""
        lines.append(f"{str(k):>17}  {ab:7.2f} {asp:6.2f}  {bb:7.2f} {bsp:6.2f}  {dt:>6}  {ac:11,} {bc:11,}  {dc:>6}")
    lines.append("time: best of each arm's runs; spread: its worst less its best - read the change against the spread, never as a pass")
    return lines


def ab(trees: Mapping[str, str], n: int, run: Run = snapshot) -> dict[str, list[dict[str, Any]]]:
    """Alternate the arms `n` times; each arm's snapshots."""
    out: dict[str, list[dict[str, Any]]] = {"A": [], "B": []}
    for i in range(n):
        for arm in ("A", "B"):
            out[arm].append(run(trees[arm], f"ab-{arm}{i + 1}", i == 0))
    return out


def worktree(commit: str, where: str) -> str:
    """A detached worktree of `commit` under `where`."""
    path = os.path.join(where, commit.replace("/", "_"))
    subprocess.run(["git", "-C", perf_profile.SKILL, "worktree", "add", "--detach", path, commit], check=True, capture_output=True)
    return path


def main(argv: list[str] | None = None, run: Run = snapshot) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("a", help="the before commit")
    ap.add_argument("b", nargs="?", default="HEAD", help="the after commit (default HEAD)")
    ap.add_argument("--n", type=int, default=3, help="runs of each arm, alternated (default 3)")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory(prefix="perf-ab-") as where:
        trees = {"A": worktree(a.a, where), "B": worktree(a.b, where)}
        try:
            print("\n".join(compare(ab(trees, a.n, run))))
        finally:
            for path in trees.values():
                subprocess.run(["git", "-C", perf_profile.SKILL, "worktree", "remove", "--force", path], check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_ab")
    raise SystemExit(main())

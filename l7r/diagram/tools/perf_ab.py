"""Two engines timed against each other - the time evidence a performance change reports, never a gate (features 435, 436).

THREE FORMS, DECIDED BY WHAT IS COMPARED (feature 436, the GM 2026-10-27: "test a refactor first by doing the quick version
... then we could move on to running a larger subset of the tests and seeds"):

- QUICK, the default: one seed at one size (`make perf-ab A=<commit>`: seed 25 at 40 households), 6 runs a version.
- SUBSET: more than one seed or more than one size (`SEEDS=25,39 HOUSEHOLDS=20,40`), 3 runs a version.
- FULL (`FULL=1`): the whole snapshot with its scaling legs (`make perf SCALING=1`), 3 runs a version.

QUICK FIRST, ENFORCED: a subset or full run is refused before it rolls unless a quick comparison of the same two engines -
judged by their code, docstrings and comments aside (`render_cache.engine_fingerprint`) - is on record in this clone, or
`PERF_AB_QUICK_OK="<reason>"` says why not (the reason logged). It refuses a skipped step, never a timing.

Each version is checked out in a detached worktree. The quick and subset forms roll in one worker process per version,
warmed by one untimed roll as `make perf` warms its first, each roll timed by that version's own `perf_snapshot.measure`;
the full form runs `make perf SCALING=1` in each worktree. The versions ALTERNATE, A then B, then B then A, so neither always
runs first. Per size and seed it prints each version's best wall time and CPU time with the spread of its runs (worst less
best), the change between versions, and the calls of each (counted once, in a separate pass). A quick comparison prints the
NOISE FLOOR of its form beside it - one engine timed against itself (`make perf-ab AA=1`) - to read a change against.

It decides nothing about the engines: a timing depends on load and on which core runs it (docs/performance-checklist.md,
the GM 2026-10-27: "timings are not a gate, but improving timings is the goal of any performance improvement ticket").
"""

from __future__ import annotations

import argparse
import datetime
import glob
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.tools import perf_profile

Key = tuple[int, int]  # (households, seed)
Leg = tuple[float | None, float | None]  # (wall seconds, CPU seconds); None where the roll was refused
Run = dict[Key, Leg]
Snapshot = Callable[[str, str, bool], dict[str, Any]]

QUICK_N = 6
"""Research: plumbing - NONE: runs a version in the quick form, the GM's "a single Hamlet seed 6 times" (feature 436)"""
WIDE_N = 3
"""Research: plumbing - NONE: runs a version in the subset and full forms, feature 435's best of 3"""
GUARD = "perf-ab-quick-first"
ESCAPE = "PERF_AB_QUICK_OK"

#: THE WORKER, run in a version's worktree with that worktree first on its path, so the code that rolls and times is the
#: version's own. One JSON request a line; each answer is marked, because `measure` prints its progress to the same stdout.
WORKER = r"""
import json, sys
sys.path.insert(0, ".")
from l7r.diagram.tools import perf_snapshot as ps
warm = True
for line in sys.stdin:
    q = json.loads(line)
    if q["op"] == "count":
        got = ps.count_calls((q["seed"],), households=q["households"])
        out = {"calls": sum(sum(v.values()) for v in got.values())}
    else:
        row = ps.measure((q["seed"],), households=q["households"], warm=warm)[0]
        warm = False
        refused = bool(row.get("refused"))
        out = {"wall": None if refused else round(sum(row["stages"].values()), 2),
               "cpu": None if refused else round(sum((row.get("cpu_stages") or {}).values()), 2)}
    print("@@" + json.dumps(out), flush=True)
"""


class Worker:
    """One version's roller: a process in its worktree, asked for a timed roll or a call count, one at a time."""

    def __init__(self, tree: str, script: str = WORKER) -> None:
        env = {**os.environ, "PYTHONPATH": tree}
        self.proc = subprocess.Popen([sys.executable, "-c", script], cwd=tree, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    def ask(self, q: Mapping[str, Any]) -> dict[str, Any]:
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(dict(q)) + "\n")
        self.proc.stdin.flush()
        for line in self.proc.stdout:
            if line.startswith("@@"):
                return dict(json.loads(line[2:]))
        raise RuntimeError("the worker ended before it answered - roll that seed with `make perf` in the worktree to see why")

    def roll(self, key: Key) -> Leg:
        got = self.ask({"op": "roll", "households": key[0], "seed": key[1]})
        return got["wall"], got["cpu"]

    def count(self, key: Key) -> int:
        return int(self.ask({"op": "count", "households": key[0], "seed": key[1]})["calls"])

    def close(self) -> None:
        if self.proc.stdin is not None:
            self.proc.stdin.close()
        self.proc.wait(timeout=60)


def order(i: int) -> tuple[str, str]:
    """The versions' order in run `i`: A then B, then B then A, so neither always runs first (feature 436)."""
    return ("A", "B") if i % 2 == 0 else ("B", "A")


def rolled(trees: Mapping[str, str], keys: Sequence[Key], n: int, make: Callable[[str], Any] = Worker) -> tuple[dict[str, list[Run]], dict[str, dict[Key, int]]]:
    """The quick and subset forms: `n` runs of every key on each version's worker, alternated; then each version's calls."""
    workers = {arm: make(trees[arm]) for arm in ("A", "B")}
    try:
        runs: dict[str, list[Run]] = {"A": [], "B": []}
        for i in range(n):
            for arm in order(i):
                runs[arm].append({k: workers[arm].roll(k) for k in keys})
        calls = {arm: {k: workers[arm].count(k) for k in keys} for arm in ("A", "B")}
    finally:
        for w in workers.values():
            w.close()
    return runs, calls


def snapshot(tree: str, label: str, counted: bool) -> dict[str, Any]:
    """The full form: one `make perf SCALING=1` in `tree`, read back from the record it writes."""
    env = {**os.environ, **({} if counted else {"L7R_PERF_NO_COUNTS": "1"})}
    subprocess.run(["make", "-C", tree, "--no-print-directory", "perf", f"LABEL={label}", "SCALING=1"], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    path = sorted(glob.glob(os.path.join(tree, "dev", "perf-log", f"*-{label}-*.json")))[-1]
    with open(path, encoding="utf-8") as fh:
        return dict(json.load(fh))


def legs(snap: Mapping[str, Any]) -> tuple[Run, dict[Key, int]]:
    """A full snapshot's legs, (households, seed) -> (wall, CPU), each summed from its stages to the hundredth (the leg's own
    `seconds` is rounded to the tenth), or the leg's totals where it records no stages; and each leg's calls."""
    run: Run = {}
    calls: dict[Key, int] = {}
    for leg in [*snap.get("rows", []), *snap.get("scaling", [])]:
        k = (int(leg["asked"]), int(leg["seed"]))
        stages, cpu = leg.get("stages") or {}, leg.get("cpu_stages") or {}
        if leg.get("seconds") is None:
            run[k] = (None, None)
        else:
            run[k] = (round(sum(stages.values()), 2) if stages else leg["seconds"], round(sum(cpu.values()), 2) if cpu else leg.get("cpu_seconds"))
        calls[k] = sum((leg.get("calls") or {}).values())
    return run, calls


def swept(trees: Mapping[str, str], n: int, take: Snapshot = snapshot) -> tuple[dict[str, list[Run]], dict[str, dict[Key, int]]]:
    """The full form: `n` snapshots a version, alternated; the calls from each version's first (the only one that counts)."""
    runs: dict[str, list[Run]] = {"A": [], "B": []}
    calls: dict[str, dict[Key, int]] = {}
    for i in range(n):
        for arm in order(i):
            run, counted = legs(take(trees[arm], f"ab-{arm}{i + 1}", i == 0))
            runs[arm].append(run)
            calls.setdefault(arm, counted)
    return runs, calls


def best(runs: Sequence[Run], k: Key, what: int) -> tuple[float, float] | None:
    """The best of a version's runs at `k` and its spread (worst less best), of wall time (`what` 0) or CPU time (1)."""
    ts = [t for r in runs if (t := r.get(k, (None, None))[what]) is not None]
    return (min(ts), max(ts) - min(ts)) if ts else None


def change(a: float, b: float) -> str:
    return f"{100 * (b - a) / a:+.0f}%" if a else ""


def compare(runs: Mapping[str, Sequence[Run]], calls: Mapping[str, Mapping[Key, int]]) -> list[str]:
    """The table: per size and seed, each version's best and spread of wall and of CPU time, the change, and the calls."""
    head = (
        f"{'households, seed':>17}  {'A wall':>7} {'+-':>5} {'B wall':>7} {'+-':>5} {'wall':>5}  {'A cpu':>7} {'+-':>5} {'B cpu':>7} {'+-':>5} {'cpu':>5}  {'A calls':>11} {'B calls':>11} {'calls':>6}"
    )
    lines = [head]
    for k in sorted({k for arm in runs.values() for r in arm for k in r}):
        wall = [best(runs[arm], k, 0) for arm in ("A", "B")]
        cpu = [best(runs[arm], k, 1) for arm in ("A", "B")]
        ac, bc = calls.get("A", {}).get(k, 0), calls.get("B", {}).get(k, 0)
        if wall[0] is None or wall[1] is None:
            lines.append(f"{str(k):>17}  {'refused' if wall[0] is None else f'{wall[0][0]:7.2f}':>7} {'':>5} {'refused' if wall[1] is None else f'{wall[1][0]:7.2f}':>7}")
            continue
        (aw, asp), (bw, bsp) = wall
        cells = []
        for got in cpu:
            cells.append(f"{got[0]:7.2f} {got[1]:5.2f}" if got else f"{'':>7} {'':>5}")
        dc = change(cpu[0][0], cpu[1][0]) if cpu[0] and cpu[1] else ""
        lines.append(f"{str(k):>17}  {aw:7.2f} {asp:5.2f} {bw:7.2f} {bsp:5.2f} {change(aw, bw):>5}  {cells[0]} {cells[1]} {dc:>5}  {ac:11,} {bc:11,} {change(ac, bc) if ac else '':>6}")
    lines.append("best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass")
    return lines


def keys_of(seeds: Sequence[int], sizes: Sequence[int]) -> list[Key]:
    return [(h, s) for h in sizes for s in seeds]


def form(seeds: Sequence[int], sizes: Sequence[int], full: bool) -> str:
    """The form is the count compared, never which variable spelled it (feature 436 FR-001)."""
    return "full" if full else "quick" if len(seeds) == 1 and len(sizes) == 1 else "subset"


def state_dir() -> str:
    """Where this clone keeps its quick comparisons and floors: under git's own directory, never committed."""
    common = subprocess.run(["git", "-C", perf_profile.SKILL, "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=True).stdout.strip()
    return os.path.join(perf_profile.SKILL, common, "perf-ab") if not os.path.isabs(common) else os.path.join(common, "perf-ab")


def engine_key(tree: str) -> str:
    """A version's engine by its code, docstrings and comments aside - the key the render cache stamps maps with."""
    from l7r.diagram.pipeline.render_cache import engine_fingerprint

    return engine_fingerprint(tree)[:16]


def pair(ka: str, kb: str) -> str:
    return "-".join(sorted((ka, kb)))


def write(path: str, data: Mapping[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dict(data), fh, indent=2)


def read(path: str) -> dict[str, Any] | None:
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return dict(json.load(fh))


def escape_log() -> Any:
    """`scripts/pages/escape_log.py`, the escape every refusal in Python records itself through."""
    path = os.path.join(perf_profile.SKILL, "scripts", "pages", "escape_log.py")
    spec = importlib.util.spec_from_file_location("escape_log", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def refusal(a: str, b: str, what: str, seed: int, size: int) -> str:
    return (
        f"perf-ab: refused - a {what} comparison before a quick one: no quick comparison of these two engines is on record in this clone.\n"
        f"  Run the quick form first, iterate on it, then come back:  make perf-ab A={a} B={b} SEEDS={seed} HOUSEHOLDS={size}\n"
        f'  A case that genuinely needs the wider run first: {ESCAPE}="<reason>" (recorded). This refuses a skipped step, never a timing.'
    )


def floor_line(floor: Mapping[str, Any] | None, seed: int, size: int, n: int) -> str:
    if floor is None:
        return f"floor: none on record for seed {seed} at {size} households, {n} runs - take it once: make perf-ab AA=1 SEEDS={seed} HOUSEHOLDS={size} N={n}"
    return f"floor (one engine against itself, taken {floor['utc']}): wall {floor['wall']}, CPU {floor['cpu']} - a change inside it is not a change"


def worktree(commit: str, where: str, name: str) -> str:
    """A detached worktree of `commit` under `where`."""
    path = os.path.join(where, name)
    subprocess.run(["git", "-C", perf_profile.SKILL, "worktree", "add", "--detach", path, commit], check=True, capture_output=True)
    return path


def floor_of(runs: Mapping[str, Sequence[Run]], k: Key) -> dict[str, str]:
    """An A/A run's floor at `k`: the change between its two workers' bests, wall and CPU."""
    out = {}
    for what, name in ((0, "wall"), (1, "cpu")):
        a, b = best(runs["A"], k, what), best(runs["B"], k, what)
        out[name] = change(a[0], b[0]) if a and b else "n/a"
    return out


def main(argv: list[str] | None = None, make: Callable[[str], Any] = Worker, take: Snapshot = snapshot, env: Mapping[str, str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("a", help="the before commit (with --aa, the one engine)")
    ap.add_argument("b", nargs="?", default="HEAD", help="the after commit (default HEAD)")
    ap.add_argument("--seeds", default="25", help="comma-separated seeds (default 25)")
    ap.add_argument("--households", default="40", help="comma-separated sizes (default 40)")
    ap.add_argument("--full", action="store_true", help="the whole snapshot with its scaling legs")
    ap.add_argument("--aa", action="store_true", help="the noise floor: A against itself, in the quick form")
    ap.add_argument("--n", type=int, default=None, help="runs a version (default 6 quick, 3 otherwise)")
    a = ap.parse_args(argv)
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    sizes = [int(x) for x in a.households.split(",") if x.strip()]
    kind = form(seeds, sizes, a.full)
    n = a.n or (QUICK_N if kind == "quick" else WIDE_N)
    if a.aa and kind != "quick":
        print("perf-ab: AA=1 takes the floor of a quick form - one seed at one size", file=sys.stderr)
        return 2
    state = state_dir()
    with tempfile.TemporaryDirectory(prefix="perf-ab-") as where:
        trees = {"A": worktree(a.a, where, "A")}
        trees["B"] = trees["A"] if a.aa else worktree(a.b, where, "B")
        try:
            keys = {arm: engine_key(tree) for arm, tree in trees.items()}
            record = os.path.join(state, "quick", pair(keys["A"], keys["B"]) + ".json")
            if kind != "quick" and read(record) is None:
                try:
                    allowed = escape_log().escape(ESCAPE, GUARD, "no-quick-first", {"form": kind, "a": a.a, "b": a.b}, env)
                except Exception as err:  # `NoReason`: set, with no reason worth recording
                    print(f"perf-ab: refused - {err}", file=sys.stderr)
                    return 2
                if not allowed:
                    print(refusal(a.a, a.b, kind, seeds[0], sizes[0]), file=sys.stderr)
                    return 2
            runs, calls = swept(trees, n, take) if kind == "full" else rolled(trees, keys_of(seeds, sizes), n, make)
            print("\n".join(compare(runs, calls)))
            utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            floor_path = os.path.join(state, "floor", f"{seeds[0]}-{sizes[0]}-{n}.json")
            if a.aa:
                write(floor_path, {"utc": utc, "commit": a.a, "seed": seeds[0], "households": sizes[0], "n": n, **floor_of(runs, (sizes[0], seeds[0]))})
                print(f"floor recorded for seed {seeds[0]} at {sizes[0]} households, {n} runs")
            elif kind == "quick":
                write(record, {"utc": utc, "a": a.a, "b": a.b, "keys": keys, "seed": seeds[0], "households": sizes[0], "n": n, "table": compare(runs, calls)})
                print(floor_line(read(floor_path), seeds[0], sizes[0], n))
        finally:
            for path in {*trees.values()}:
                subprocess.run(["git", "-C", perf_profile.SKILL, "worktree", "remove", "--force", path], check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_ab")
    raise SystemExit(main())

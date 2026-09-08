"""The roll census's attribution and VERDICT (feature 213, GM 2026-09-07).

Two halves. The attribution half is called by the `-p` shim (`rollcensus.py`) inside each test worker:
`begin(nodeid)` puts the test's id and a fresh request id into the environment, `end()` takes them out, and
`rolls_first(items)` moves the map-rolling tests to the front of collection. The verdict half runs once,
after pytest, from the Makefile (`python3 -m l7r.diagram.ci rollcensus verdict`): it reads the census file
the engine wrote at its chokepoints (`_census.py`) and judges it against the roster (`tests/rolls.py`).

WHAT FAILS THE GATE, each named in the spec (FR-003):
  - a spec ROLLED more than once in the run - two distinct request ids, less the roster's stated
    Duplicates; a `generate` that re-rolls inside one request is ONE roll with N attempts, reported;
  - a rolled spec the roster does not list - the message says to add the row with its reason;
  - on a FULL run, a roster row nothing rolled - a stale roster is as wrong as a short one;
  - a render (a PNG or the page's raster) from a test that does not carry the `renders` marker;
  - a roll IN THE WORKER (the record's pid is the worker's) from a test module the roster does not except;
  - a roll from a STUB-excepted module that took longer than a stand-in stage can (STUB_MAX_S).
A `PoolGen` (the pool sweep's gate_obtain child) may roll its generator once, when its cache key moved.
Many tests SERVED by one roll is the passing state - that is the whole point of the share.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from l7r.diagram import _census

MARKER = "renders"  # the marker a test OF rendering carries (registered in pyproject.toml)
STUB_MAX_S = 5.0  # a stand-in stage roll (a stub `InProcess` module) costs milliseconds; the shortest real hamlet roll in the 2026-09-08 census was 11 s


# ---------------------------------------------------------------------------------------------------
# attribution (in the worker)
# ---------------------------------------------------------------------------------------------------


def configure() -> None:
    os.environ[_census.WORKER_ENV] = str(os.getpid())


def begin(nodeid: str) -> None:
    os.environ[_census.TEST_ENV] = nodeid
    os.environ[_census.REQUEST_ENV] = uuid.uuid4().hex[:12]


def end() -> None:
    os.environ.pop(_census.TEST_ENV, None)
    os.environ.pop(_census.REQUEST_ENV, None)


def rolls_first(items: list[Any]) -> None:
    """The map-rolling tests (the `rolls_map` marker, which `tests/test_markers.py` proves every roller carries)
    to the front, in their collected order; everything else after, in its. Under worksteal the long rolls then
    start at t=0 rather than when a worker happens to reach their module (spec FR-010). And the tests OF
    rendering - the `renders` marker - are written beside the census, because the verdict runs after pytest
    and cannot ask a collected item for its markers then."""
    rolling = [it for it in items if it.get_closest_marker("rolls_map") is not None]
    rest = [it for it in items if it.get_closest_marker("rolls_map") is None]
    items[:] = rolling + rest
    path = os.environ.get(_census.ENV)
    if path:
        renders = sorted(it.nodeid for it in items if it.get_closest_marker(MARKER) is not None)
        with contextlib.suppress(OSError):
            Path(renders_file(path)).write_text("\n".join(renders) + "\n", encoding="utf-8")


def renders_file(census_path: str) -> str:
    return census_path + ".renders"


# ---------------------------------------------------------------------------------------------------
# the verdict (after pytest)
# ---------------------------------------------------------------------------------------------------


def read(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # a half-written line from a killed child is not a verdict
    return rows


def _key(spec: dict[str, Any] | None) -> tuple[str, int] | None:
    if not spec or spec.get("name") is None or spec.get("seed") is None:
        return None
    return (str(spec["name"]), int(spec["seed"]))


def _module(nodeid: str | None) -> str:
    return (nodeid or "").split("::")[0]


def _exception(nodeid: str | None, in_process: Any) -> Any:
    """The roster's `InProcess` entry covering `nodeid`'s module, or None."""
    mod = _module(nodeid)
    for e in in_process:
        if mod == e.module or mod.startswith(e.module):
            return e
    return None


def _excepted(nodeid: str | None, in_process: Any) -> bool:
    return bool(_exception(nodeid, in_process) is not None)


def judge(rows: list[dict[str, Any]], roster: Any, *, full: bool, renders_ok: set[str]) -> tuple[list[str], list[str]]:
    """`(failures, report_lines)` for one run's census against `roster` (the `tests.rolls` module).

    `renders_ok` is the set of test ids that carry the `renders` marker (the plugin cannot see markers
    at record time; the Makefile passes the file the collection wrote). A roll is a group of `roll`
    records sharing (spec key, request id, PROCESS): a `generate` that re-rolls does so inside one process,
    so its attempts share all three, while two children of one test - the fan-out's serial and pool halves,
    the immune test's plain and perturbed runs - differ by pid and are two rolls (the first census grouped by
    request alone and reported the fan-out as one roll with two attempts, which hid the duplicate it exists
    to state). Three roster kinds soften the rule where the census found it had to: a `Duplicate` (a second
    roll a test makes by its nature), a `PoolGen` (the pool sweep's `gate_obtain` child, which rolls a shipped
    generator only when its cache key moved - allowed once, never stale), and a stub `InProcess` module
    (stand-in stages: its records are reported and bounded by `STUB_MAX_S`, never counted as hamlets)."""
    rolls: dict[tuple[tuple[str, int], str, str], list[dict[str, Any]]] = defaultdict(list)
    unnamed: list[dict[str, Any]] = []
    stubs: list[dict[str, Any]] = []
    floor: list[dict[str, Any]] = []  # rolls no test requested: the hamlet-floor phase's own (it runs after pytest, under the same census)
    for r in rows:
        if r.get("kind") != "roll":
            continue
        key = _key(r.get("spec"))
        if key is None:
            unnamed.append(r)
            continue
        if not r.get("test"):
            floor.append(r)
            continue
        exc = _exception(r.get("test"), roster.IN_PROCESS)
        if exc is not None and getattr(exc, "stub", False):
            stubs.append(r)
            continue
        rolls[(key, str(r.get("request")), str(r.get("pid")))].append(r)
    by_spec: dict[tuple[str, int], list[list[dict[str, Any]]]] = defaultdict(list)
    for (key, _req, _pid), attempts in rolls.items():
        by_spec[key].append(attempts)
    rostered = roster.by_key()
    pool_gens = {p.key: p for p in getattr(roster, "POOL_GENS", ())}
    pool_rolled: set[tuple[str, int]] = set()
    failures: list[str] = []
    lines: list[str] = []
    served = sum(1 for r in rows if r.get("kind") == "served")
    total = sum(len(v) for v in by_spec.values())
    lines.append(f"roll census: {total} roll(s) of {len(by_spec)} spec(s); {served} request(s) served from a shared roll; roster {len(rostered)} row(s)")
    for key in sorted(by_spec, key=lambda k: (k[0], k[1])):
        groups = by_spec[key]
        tests = sorted({str(g[0].get("test")) for g in groups})
        attempts = ", ".join(str(len(g)) for g in groups)
        secs = sum(float(r.get("dt") or 0) for g in groups for r in g)
        row = rostered.get(key)
        pool = pool_gens.get(key)
        is_pool = [pool is not None and str(g[0].get("test", "")).startswith(pool.test) for g in groups]
        others = [g for g, p in zip(groups, is_pool, strict=True) if not p]
        n_pool = sum(is_pool)
        if n_pool:
            pool_rolled.add(key)
        status = "rostered" if row else ("pool gen" if pool else "NOT IN THE ROSTER")
        tail = " (+ the pool gen: its key moved)" if n_pool and row else ""
        lines.append(f"  {key[0]} seed={key[1]}: {len(groups)} roll(s), attempts {attempts}, {secs:.0f}s - {status}{tail}; requested by {', '.join(t.split('::')[-1][:60] for t in tests)}")
        if n_pool > 1:
            failures.append(f"{key[0]} seed={key[1]}: the pool sweep rolled its generator {n_pool} times in one run - gate_obtain rolls a gen once per key")
        if others and row is None:
            failures.append(
                f"{key[0]} seed={key[1]} was rolled by {tests[0]} but is not in the roster: add a `Roll` to tests/rolls.py naming what this roll uniquely carries - or reuse a rostered roll"
            )
        allowed_dups = [d for d in roster.DUPLICATES if d.key == key]
        matched = len([d for d in allowed_dups if any(str(g[0].get("test", "")).startswith(d.test) for g in others)])
        extra = len(others) - 1 - matched
        if extra > 0:
            failures.append(
                f"{key[0]} seed={key[1]} was rolled {len(others)} times in one run (by {', '.join(tests)}) - a spec is rolled ONCE per gate and shared; a site that must roll it again by its nature is a stated `Duplicate` in tests/rolls.py"
            )
        for g in others:
            first = g[0]
            if str(first.get("pid")) == str(first.get("worker")) and not _excepted(first.get("test"), roster.IN_PROCESS):
                failures.append(
                    f"{key[0]} seed={key[1]} was rolled IN THE TEST WORKER by {first.get('test')} - every gate roll runs in a child (spec FR-007); a site that must roll in the worker is a stated `InProcess` exception in tests/rolls.py"
                )
    if full:
        for key, row in sorted(rostered.items()):
            if key not in by_spec:
                failures.append(f"roster row {key[0]} seed={key[1]} ({row.rolled_by}) was not rolled by this full run - a stale row is as wrong as a missing one; remove it or roll it")
    for r in unnamed:
        if str(r.get("pid")) == str(r.get("worker")) and not _excepted(r.get("test"), roster.IN_PROCESS):
            failures.append(f"a roll with no spec ran in the test worker under {r.get('test')} - pass the spec to roll_scope, or except the module in tests/rolls.py")
    for r in floor:
        spec = r.get("spec") or {}
        failures.append(
            f"the hamlet-floor phase ROLLED {spec.get('name')} seed={spec.get('seed')} itself ({float(r.get('dt') or 0):.0f}s) - the tests' roll is the floor's record (spec FR-001, 207's D14): "
            "on a full run every rostered spec was just rolled and stored; on an incremental run this means the selection did not run the test that rolls it - a roll child's coverage carries "
            "its requester's context since feature 213 (_census.CONTEXT_ENV), so check the baseline was taken after that landed, or that the roller is a rostered test at all"
        )
    if floor:
        lines.append(f"  hamlet-floor rolls (no test requested them): {len(floor)}")
    for r in stubs:
        dt = float(r.get("dt") or 0)
        if dt > STUB_MAX_S:
            spec = r.get("spec") or {}
            failures.append(
                f"{r.get('test')} is excepted as a stub-stage module, but its roll of {spec.get('name')} seed={spec.get('seed')} took {dt:.0f}s - a stand-in stage costs milliseconds; a real roll there is a real roll: a roster row and a child"
            )
    if stubs:
        lines.append(f"  stand-in stage rolls (stub-excepted modules, no map): {len(stubs)}, {sum(float(r.get('dt') or 0) for r in stubs):.1f}s in all")
    for r in rows:
        if r.get("kind") == "render" and str(r.get("test") or "") not in renders_ok:
            failures.append(f"{r.get('test')} rendered a {r.get('what')} - tests do not render (DIAGRAM_SKIP_RENDER is the suite's default); a test OF rendering carries the `renders` marker")
    for d in roster.DUPLICATES:
        lines.append(f"  stated duplicate: {d.key[0]} seed={d.key[1]} by {d.test.split('::')[-1][:60]} ({d.mechanism}) - {d.reason}")
    for key, p in sorted(pool_gens.items()):
        lines.append(f"  pool gen: {key[0]} seed={key[1]} ({p.gen}) - {'ROLLED this run: its cache key moved' if key in pool_rolled else 'served from the gen cache, not rolled'}")
    return failures, lines


def main(argv: list[str]) -> int:
    """`verdict [--full]` - the Makefile's call after the test phase; `--full` when the run was a full one,
    so a stale roster row counts."""
    if not argv or argv[0] != "verdict":
        print("usage: rollcensus verdict [--full]", file=sys.stderr)
        return 2
    path = os.environ.get(_census.ENV)
    if not path:
        print("rollcensus: L7R_ROLL_CENSUS is not set - no census to judge", file=sys.stderr)
        return 2
    rfile = Path(renders_file(path))
    renders_ok = {ln.strip() for ln in rfile.read_text(encoding="utf-8").splitlines() if ln.strip()} if rfile.is_file() else set()
    from tests import rolls  # the roster lives beside the tests it governs (spec D1)

    failures, lines = judge(read(Path(path)), rolls, full="--full" in argv, renders_ok=renders_ok)
    print("\n".join(lines))
    if failures:
        print("\nROLL CENSUS FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("roll census: green")
    return 0

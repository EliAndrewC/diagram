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


def run_db(root: Path) -> Path:
    """The run's COMBINED coverage database, as the Makefile leaves it before the verdict (`coverage combine`, then
    the incremental merge over the kept baseline contexts) - the same file the floors are judged on."""
    return root / ".claude" / "skills" / "diagram" / ".coverage"


def unique_by_context(db: Path) -> dict[str, list[tuple[str, int]]] | None:
    """Per coverage context, the engine lines NO other context of the run reaches - `make roll-audit`'s arithmetic
    with no floor, so every context is both a candidate and an "other". None when there is no database (a run
    without contexts, `make quick`): the rule cannot be judged and is not."""
    if not db.is_file():
        return None
    from l7r.diagram.tools import roll_audit

    return {ctx: uniq for ctx, _n, uniq in roll_audit.unique_lines(roll_audit.read_contexts(db), 0)}


def _fmt_lines(uniq: list[tuple[str, int]]) -> str:
    """`file:12-14,20; other.py:7` - the lines a roll alone reaches, compact enough to read in a gate log."""
    by_file: dict[str, list[int]] = defaultdict(list)
    for f, ln in uniq:
        by_file[f].append(ln)
    parts = []
    for f in sorted(by_file):
        nums = sorted(set(by_file[f]))
        runs: list[str] = []
        start = prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
                continue
            runs.append(str(start) if start == prev else f"{start}-{prev}")
            start = prev = n
        runs.append(str(start) if start == prev else f"{start}-{prev}")
        parts.append(f"{f}:{','.join(runs)}")
    return "; ".join(parts)


def judge(
    rows: list[dict[str, Any]], roster: Any, *, full: bool, renders_ok: set[str], engine_changed: bool = True, unique: dict[str, list[tuple[str, int]]] | None = None
) -> tuple[list[str], list[str]]:
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
        # A STUB IS AN IN-PROCESS RECORD (feature 216): the exception is about rolls made IN THE WORKER, so only a
        # record whose pid is the worker's is a stand-in stage. A child roll a stub-excepted module REQUESTS is a
        # real shared roll and is judged by the roster like any other - the first census after 216 bucketed the
        # fan-out's request for Polder 12 as a 62 s "stub" and then reported the Polder row as never rolled.
        if exc is not None and getattr(exc, "stub", False) and str(r.get("pid")) == str(r.get("worker")):
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
        # A STATED DUPLICATE claims one group (matched by its test); what remains must fit the roster: one roll for a
        # `Roll` row, one for a `PoolGen` (the cold gen roll, requested by WHICHEVER reader came first - the sweep or
        # a gate module reading the pool's map, feature 215), both when a key is both.
        dups = [d for d in roster.DUPLICATES if d.key == key]
        claimed: list[int] = []
        for d in dups:
            for gi, g in enumerate(groups):
                if gi not in claimed and str(g[0].get("test", "")).startswith(d.test):
                    claimed.append(gi)
                    break
        rest = [g for gi, g in enumerate(groups) if gi not in claimed]
        allowed = (1 if row else 0) + (1 if pool else 0)
        if pool and len(rest) >= (1 if row else 0) + 1:
            pool_rolled.add(key)
        status = "rostered" if row else ("pool gen" if pool else "NOT IN THE ROSTER")
        tail = " (+ the pool gen: its key moved)" if pool and row and len(rest) >= 2 else ""
        lines.append(f"  {key[0]} seed={key[1]}: {len(groups)} roll(s), attempts {attempts}, {secs:.0f}s - {status}{tail}; requested by {', '.join(t.split('::')[-1][:60] for t in tests)}")
        # THE LINES A ROLL EARNS (feature 217, GM 2026-09-08: *"if it is literally ever possible for us to achieve one
        # hundred percent code coverage in our make done tests, Without adding a new map roll to the unit tests. then we
        # should always do that"*). A roll is justified by the engine lines its coverage context reaches that NO other
        # context of the run reaches; a roll with none can be removed with 100% kept, so under constitution VI it must be.
        # The count and the lines are PRINTED for every roll, green or red, so the number is seen every gate; the pool
        # sweep's roll of a shipped generator is printed and never judged (the pool's membership is the GM's exhibit
        # decision, spec FR-001a). A record with no context, or a context the database never saw, is not judged.
        for g in groups:
            first = g[0]
            ctx = str(first.get("context") or f"{first.get('test')}|run")
            if unique is None or ctx not in unique:
                continue
            uniq = unique[ctx]
            is_pool = bool(pool) and str(first.get("test") or "").startswith(str(getattr(pool, "test", "") or "\0"))
            lines.append(
                f"      lines only this roll reaches: {len(uniq)}" + (" (the shipped generator's roll: printed, never judged)" if is_pool else "") + (f" - {_fmt_lines(uniq)}" if uniq else "")
            )
            if not uniq and not is_pool:
                failures.append(
                    f"{key[0]} seed={key[1]} (rolled by {first.get('test')}, context {ctx}) reaches NO engine line that no other context reaches - "
                    "constitution VI, THE GATE ROLLS ONLY WHAT THE FLOOR NEEDS: a roll with no line of its own is removed with 100% kept. "
                    "Pack its assertions onto a roll already made, make them unit tests of the placer, or move the test to tests/soak/ "
                    "(the tier above the gate; `make soak` names it) - then remove the row from tests/rolls.py. `make roll-audit` shows every roll's lines."
                )
        if allowed == 0 and rest:
            failures.append(
                f"{key[0]} seed={key[1]} was rolled by {tests[0]} but is not in the roster: add a `Roll` to tests/rolls.py naming what this roll uniquely carries - or reuse a rostered roll"
            )
        elif len(rest) > allowed:
            failures.append(
                f"{key[0]} seed={key[1]} was rolled {len(groups)} times in one run (by {', '.join(tests)}) - a spec is rolled ONCE per gate and shared; a site that must roll it again by its nature is a stated `Duplicate` in tests/rolls.py"
            )
        for g in rest:
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
        if full or engine_changed:
            failures.append(
                f"the hamlet-floor phase ROLLED {spec.get('name')} seed={spec.get('seed')} itself ({float(r.get('dt') or 0):.0f}s) - the tests' roll is the floor's record (spec FR-001, 207's D14): "
                "on a full run every rostered spec was just rolled and stored; on an incremental run with an engine change this means the selection did not run the test that rolls it - a roll "
                "child's coverage carries its requester's context since feature 213 (_census.CONTEXT_ENV), so check the baseline was taken after that landed, or that the roller is a rostered test at all"
            )
    if floor:
        # NO ENGINE CHANGE and the floor still rolled: the roll cache's record was stale for a reason the selection cannot see -
        # an edit made and then reverted leaves the cache holding the edited roll while the baseline says nothing changed.
        # The floor's roll is then the only way the record gets refreshed: reported, not failed.
        lines.append(
            f"  hamlet-floor rolls (no test requested them): {len(floor)}"
            + (
                ""
                if full or engine_changed
                else " - allowed: no engine file changed against the baseline, so the cache's record was stale on its own (an edit reverted?) and no test could have been selected to refresh it"
            )
        )
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


def engine_changed(root: Path | None) -> bool:
    """Did this run's plan see an engine change against the baseline? Read from the incremental plan the test
    phase wrote; no root or no plan reads as changed - the strict side, where a floor roll fails."""
    if root is None:
        return True
    from l7r.diagram.ci import incremental

    plan = incremental.baseline_dir(root) / incremental.PLAN
    try:
        return bool(json.loads(plan.read_text(encoding="utf-8")).get("changed_engine"))
    except OSError, ValueError:
        return True


def main(argv: list[str], root: Path | None = None) -> int:
    """`verdict [full]` - the Makefile's call after the test phase; the word `full` when the run was a full one,
    so a stale roster row counts. `root` (the repository) locates the incremental plan, which says whether an
    engine file changed - the difference between a floor roll that signals a missed roller and one that refreshes
    a record the selection could not have known was stale."""
    if not argv or argv[0] != "verdict":
        print("usage: rollcensus verdict [full]", file=sys.stderr)
        return 2
    path = os.environ.get(_census.ENV)
    if not path:
        print("rollcensus: L7R_ROLL_CENSUS is not set - no census to judge", file=sys.stderr)
        return 2
    rfile = Path(renders_file(path))
    renders_ok = {ln.strip() for ln in rfile.read_text(encoding="utf-8").splitlines() if ln.strip()} if rfile.is_file() else set()
    from tests import rolls  # the roster lives beside the tests it governs (spec D1)

    # A POSITIONAL WORD, NOT A FLAG (feature 215): the ci parser owns `--full` (feature 130) and ate it, so the verdict
    # ran every gate with `full=False` and the stale-row rule never fired - found when two rows left behind on purpose
    # came up green. Feature 207's `incremental plan full` met the same trap the same way.
    full = "full" in argv[1:]
    unique = unique_by_context(run_db(root)) if root is not None else None
    failures, lines = judge(read(Path(path)), rolls, full=full, renders_ok=renders_ok, engine_changed=full or engine_changed(root), unique=unique)
    print("\n".join(lines))
    if failures:
        print("\nROLL CENSUS FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("roll census: green")
    return 0

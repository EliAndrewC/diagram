"""The Python calls a 40-household hamlet makes, by stage and by step - the counts the placement-stages page shows (feature 434).

`make phase-calls` rolls one hamlet - the reference spec at 40 households by default, seed 39 - stage by stage, each stage
under its own cProfile profiler as `make perf-fanout` measures it (`perf_profile.profile_stage`). Each step the page lists
under a stage (its docstring's `Steps:`, `placement_stages.stage_doc`) is wrapped wherever its name is bound
(`placement_stages._bind_points`, the page's own binding) so that, while it runs, the profiler that was running is switched
off and the step's own switched on, and back on its return: a call is counted once, by the innermost listed step running or
by the stage (its own work). The wrappers' frames and the profilers' switches are taken out of the counts, so a stage's
total is cProfile's count of the stage alone - the fanout's for the same seed and engine.

Each stage is measured as the fanout measures it, in a fresh process that runs the stages before it plainly (`stage_job`):
one sequential roll measuring every stage was measured short of the fanout (`measure`'s docstring).

The record, `dev/phase-calls.json`, keeps the newest measurement per map type (the settlement form, field archetype and water
sink the spec sets), with its date, seed, households and engine commit; `make placement-stages` reads it
(`tools/placement_calls.py`).
"""

from __future__ import annotations

import argparse
import cProfile
import datetime
import functools
import io
import json
import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack, redirect_stdout
from typing import Any

from l7r.diagram.tools import perf_profile

RECORD = os.path.join(perf_profile.SKILL, "dev", "phase-calls.json")
HOUSEHOLDS = 40
SEED = 39
JOBS = 3  # the fanout's default: each worker holds a roll
_SWITCHES = ("<method 'enable' of '_lsprof.Profiler' objects>", "<method 'disable' of '_lsprof.Profiler' objects>")


def counted(prof: cProfile.Profile) -> int:
    """A profiler's calls, less the tally's own: the wrappers' frames (this module's) and the profilers' switches."""
    prof.create_stats()  # ...read directly: `pstats.Stats` refuses a profiler that recorded nothing (a step that never ran)
    stats: dict[tuple[str, int, str], tuple[Any, ...]] = prof.stats  # type: ignore[attr-defined]
    return sum(v[1] for (f, _ln, fn), v in stats.items() if os.path.abspath(f) != os.path.abspath(__file__) and fn not in _SWITCHES)


class Tally:
    """The profilers of one stage and the stack of the one switched on: the stage's own first, a step's on top while it runs."""

    def __init__(self) -> None:
        self.stack: list[cProfile.Profile] = []

    def held(self, target: Callable[..., Any], prof: cProfile.Profile) -> Callable[..., Any]:
        """`target`, its calls counted by `prof` while it runs, the profiler beneath it switched back on after."""
        stack = self.stack

        def step(*a: Any, **k: Any) -> Any:
            stack[-1].disable()
            stack.append(prof)
            prof.enable()
            try:
                return target(*a, **k)
            finally:
                prof.disable()
                stack.pop()
                stack[-1].enable()

        return functools.update_wrapper(step, target)

    def stage(self, run: Callable[[], Any], steps: Sequence[str], bind: Callable[[str], tuple[list[tuple[Any, str]], Any]]) -> dict[str, Any]:
        """Run one stage (`run`) with its `steps` held; its calls: `calls`, `own` (outside every step) and `steps`."""
        own = cProfile.Profile()
        profs = {p: cProfile.Profile() for p in steps}
        restore: list[tuple[Any, str, Any]] = []
        for path in steps:
            try:
                points, target = bind(path)
            except AttributeError, ImportError:  # a name the roster test fails the gate on; the page shows it at 0
                continue
            wrapped = self.held(target, profs[path])
            for obj, leaf in points:
                restore.append((obj, leaf, getattr(obj, leaf)))
                setattr(obj, leaf, wrapped)
        self.stack[:] = [own]
        try:
            own.enable()
            try:
                run()
            finally:
                own.disable()
        finally:
            for obj, leaf, original in reversed(restore):
                setattr(obj, leaf, original)
        by_step = {p: counted(pr) for p, pr in profs.items()}
        mine = counted(own) + 1  # ...the stage's own closing `disable`, which the fanout's profile counts too
        return {"calls": mine + sum(by_step.values()), "own": mine, "steps": by_step}


def type_key(spec: Mapping[str, Any]) -> str:
    """The map type a measurement stands for: the knobs that decide which stages do work."""
    return "/".join(str(spec.get(k) or "rolled") for k in ("settlement_form", "field_archetype", "water_sink"))


def stage_job(job: tuple[int, int, Mapping[str, Any], int]) -> tuple[str, dict[str, Any]]:
    """One stage measured as `make perf-fanout` measures it: a fresh roll of `(seed, households, overrides)` whose stages before
    the `k`th run plainly, then the `k`th under the tally - its name and its counts."""
    from l7r.diagram.hamletgen import HamletSpec, plan_site
    from l7r.diagram.hamletgen.driver import STAGES, roll_scope
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.tools.placement_stages import _bind_points, stage_doc

    seed, households, overrides, k = job
    with ExitStack() as band:
        band.enter_context(beyond_the_band())
        plan = plan_site(HamletSpec(seed=seed, **_spec(households, overrides)))
        s = Settlement(W=plan.W, H=plan.H, seed=seed)
        with redirect_stdout(io.StringIO()), roll_scope(plan.spec):
            for st in STAGES[:k]:
                st(s, plan)
            st = STAGES[k]
            return st.__name__.replace("stage_", ""), Tally().stage(functools.partial(st, s, plan), stage_doc(st)[2], _bind_points)


def _spec(households: int, overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    return {**REFERENCE, "households": households, **(overrides or {})}


def measure(seed: int = SEED, households: int = HOUSEHOLDS, overrides: Mapping[str, Any] | None = None, jobs: int = JOBS, pool_cls: Any = ProcessPoolExecutor) -> dict[str, Any]:  # noqa: ANN401
    """One hamlet measured stage by stage, each stage in its own fresh roll (`stage_job`): its type, total and per-stage counts.

    EACH STAGE IN A FRESH PROCESS, AS THE FANOUT DOES IT: one sequential roll measuring every stage was 3,317 calls short of the
    fanout's 5,205,034 on seed 39's 40-household homesteads (measured 2026-10-27, make phase-calls against make perf-fanout) -
    the process a stage meets is not the one a plain roll of the stages before it leaves."""
    from l7r.diagram.hamletgen.driver import STAGES

    fresh = {"max_tasks_per_child": 1} if pool_cls is ProcessPoolExecutor else {}
    with pool_cls(max_workers=max(1, jobs), **fresh) as pool:
        stages = dict(pool.map(stage_job, [(seed, households, dict(overrides or {}), k) for k in range(len(STAGES))]))
    spec = _spec(households, overrides)
    return {"type": type_key(spec), "seed": seed, "households": households, "total": sum(v["calls"] for v in stages.values()), "stages": stages}


def record(m: Mapping[str, Any], path: str = RECORD, commit: str | None = None, today: str | None = None) -> dict[str, Any]:
    """Keep `m` as its type's newest measurement in the record at `path`; the record."""
    try:
        with open(path, encoding="utf-8") as fh:
            rec: dict[str, Any] = json.load(fh)
    except OSError:
        rec = {}
    rec[m["type"]] = {**m, "date": today or datetime.date.today().isoformat(), "commit": commit or _commit()}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return rec


def _commit() -> str:
    out = subprocess.run(["git", "-C", perf_profile.SKILL, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def report(m: Mapping[str, Any]) -> str:
    """The stage table a measurement prints: each stage's calls and share."""
    total = m["total"] or 1
    lines = [f"phase-calls {m['type']} seed {m['seed']}, {m['households']} households: {m['total']:,} calls"]
    lines += [f"  {name:15s} {v['calls']:>11,}  {100 * v['calls'] / total:5.1f}%" for name, v in m["stages"].items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--households", type=int, default=HOUSEHOLDS)
    ap.add_argument("--form", default=None, help="settlement form (nucleated, linear, dispersed)")
    ap.add_argument("--archetype", default=None, help="field archetype")
    ap.add_argument("--sink", default=None, help="water sink (pond, offmap)")
    ap.add_argument("--jobs", type=int, default=JOBS)
    a = ap.parse_args(argv)
    over = {k: v for k, v in (("settlement_form", a.form), ("field_archetype", a.archetype), ("water_sink", a.sink)) if v}
    m = measure(a.seed, a.households, over, a.jobs)
    record(m)
    print(report(m))
    print(f"recorded in {os.path.relpath(RECORD, perf_profile.SKILL)}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.phase_calls")
    raise SystemExit(main())

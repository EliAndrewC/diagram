"""The Rust stage gate (feature 444 amendment 5, FR-019 and FR-020): every seed rolled through the Rust stages alone and judged
where they complete, the failing list kept, and each failing stage's input replayed until it passes.

    make rust-gate        the fresh block, the pinned row variants and the failing list; exit 1 when any seed fails

WHY: the GM, 2026-10-31: "no Rust stage ever ends with any failing checks at the point where that stage has completed", and
"if a seed fails, we automatically add it to a list of seeds which are always checked until the first time they pass". A seed
fails when a Rust stage raises, or when a check of the finished map fails whose every read of the map is of something the Rust
stages wrote (`hamletgen/rust_prefix.py` `Reads`); a check that reads what only a later stage writes is that stage's and is not
asked, so the check-to-stage assignment is derived from what each check reads and no table is kept. The seeds: no fixed
block - a fresh block of 48 from a start the Makefile derives from the engine (`cohort_gate.py fresh-seed`), the six pinned row
variants each on a fresh seed, and the failing list (`dev/rust-gate/failing.json`). A failing seed stays on the list until it
first passes; beside it, the state its stage started from (`dev/rust-gate/frozen/`) is replayed into that stage until it passes,
so a failure does not leave the list only because a change upstream made the seed another map. Each run is recorded
(`dev/rust-gate/<utc>.json`) with the engine it rolled, which `scripts/gates/cohort_gate.py` asks of every engine landing.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import pickle
import sys
import time
from collections.abc import Sequence
from typing import Any

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.driver import STAGES, fresh_settlement
from l7r.diagram.hamletgen.rust_prefix import Reads, held, off_the_front, owned_reads, roll_through, rust_stages, stage_name
from l7r.diagram.tools.cohort_audit import PINNED_ROWS, POST_CHECKS, fail_line

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LOG = os.path.join(HERE, "dev", "rust-gate")
FAILING = os.path.join(LOG, "failing.json")
FROZEN = os.path.join(LOG, "frozen")
#: the fresh block's size, the landing cohort's 48 (feature 386)
SEEDS = 48


def households(seed: int) -> int:
    """A seed's household count, as the cohort's fresh block sizes it (`cohort_audit.fresh_specs`)."""
    return 10 + (seed * 7) % 11


def gate_specs(start: int) -> list[tuple[int, int, dict[str, str]]]:
    """The fresh block from `start`, then each pinned row variant on the next fresh seed - no fixed seed (FR-020)."""
    fresh = [(start + i, households(start + i), {}) for i in range(SEEDS)]
    return fresh + [(start + SEEDS + i, households(start + SEEDS + i), dict(pins)) for i, pins in enumerate(PINNED_ROWS)]


def judge(before: dict[str, Any], manifest: dict[str, Any], owned: set[str]) -> list[tuple[str, set[str]]]:
    """(FAIL line, what the check read) for each check the Rust stages own that fails on `manifest`: a check that read
    something, everything it read either a part the Rust stages own - written by them on any seed of the run, so a stage that
    wrote nothing on this one is still judged on its empty output - or a part the fresh settlement already held (`before`)."""
    allowed = owned | held(before)
    out = []
    for name, check in POST_CHECKS:
        seen: set[str] = set()
        found = check(Reads(manifest, seen))
        reads = owned_reads(seen)
        if found and reads and reads <= allowed:
            out.append((fail_line(name, found), reads))
    return out


def _spec(seed: int, n: int, pins: dict[str, str]) -> Any:
    return hg.HamletSpec(name=f"Rust-{seed}", seed=seed, households=n, **({"settlement_form": "linear", **pins} if pins else {}))  # type: ignore[arg-type]  # as the cohort pins a row


Rolled = dict[str, Any]


def roll(seed: int, n: int, pins: dict[str, str], stages: Sequence[Any]) -> Rolled:
    """One seed through the Rust stages, not yet judged: its FAIL lines if it raised, the stage and the frozen input that
    raised, and the map, its fresh start and the trace for `verdict`. The plan's rolls are the first Rust stage's (water_frame's
    port rolls them, T19), so a plan that cannot be rolled is its, with no input to freeze."""
    try:
        plan = copy.deepcopy(hg.plan_site(_spec(seed, n, pins)))
    except Exception as e:  # noqa: BLE001 - a plan that cannot be rolled fails the first Rust stage, by its name
        return {"lines": [f"FAIL refused:{type(e).__name__} -> {str(e)[:300]}"], "stage": stage_name(stages[0]), "frozen": None, "trace": []}
    return _rolled(plan, stages, None)


def _rolled(plan: Any, stages: Sequence[Any], start: tuple[Any, Any] | None) -> Rolled:
    before = copy.deepcopy(fresh_settlement(plan).M)  # what a fresh settlement holds: the inputs a check may read beside the output
    s, failed, err, trace = roll_through(plan, stages, start=start)
    if failed is not None:
        return {"lines": [f"FAIL refused:{type(err).__name__} -> {str(err)[:300]}"], "stage": failed, "frozen": trace[-1][1], "trace": trace}
    return {"lines": [], "stage": None, "frozen": None, "trace": trace, "before": before, "manifest": s.M}


def verdict(r: Rolled, owned: Sequence[set[str]]) -> tuple[list[str], str | None, bytes | None]:
    """A rolled seed judged where EACH Rust stage completes (the GM: "no Rust stage ever ends with any failing checks at the point
    where that stage has completed"): (its FAIL lines, the stage charged, that stage's frozen input). After stage i the map is
    the next stage's frozen input (or the final map), judged by the checks the stages up to i own (`owned[i]`); the first stage
    whose completion fails is charged, with its own input - so a later stage that rewrites a part cannot hide an earlier failure."""
    if r["lines"]:
        return r["lines"], r["stage"], r["frozen"]
    trace = r["trace"]
    for i, (name, frozen, _wrote) in enumerate(trace):
        after = pickle.loads(trace[i + 1][1])[0].M if i + 1 < len(trace) else r["manifest"]  # noqa: S301 - the gate's own state
        failed = judge(r["before"], after, owned[i] if i < len(owned) else set())
        if failed:
            return [line for line, _reads in failed], name, frozen
    return [], None, None


def replay(path: str, stage: str, stages: Sequence[Any], owned: Sequence[set[str]]) -> list[str]:
    """A frozen input replayed into `stage` and the Rust stages after it: its FAIL lines (none: it passes). A fixture that no
    longer loads - the engine's classes changed under it - is reported as a failure, never dropped silently."""
    try:
        with open(path, "rb") as fh:
            s, plan = pickle.load(fh)  # noqa: S301 - the gate's own fixture, written by this module
    except Exception as e:  # noqa: BLE001
        return [f"FAIL frozen_input_unloadable -> {path}: {type(e).__name__} {str(e)[:200]} - read it, then remove its entry by hand"]
    names = [stage_name(st) for st in stages]
    rest = stages[names.index(stage) :] if stage in names else stages
    return verdict(_rolled(plan, rest, (s, plan)), owned[len(stages) - len(rest) :])[0]


def load_failing(path: str = FAILING) -> list[dict[str, Any]]:
    try:
        with open(path, encoding="utf-8") as fh:
            return list(json.load(fh))
    except OSError, ValueError:
        return []


def run(start: int, stages: Sequence[Any] | None = None, failing_path: str = FAILING, frozen_dir: str = FROZEN) -> dict[str, Any]:
    """The gate: every seed and every frozen input judged, the failing list brought up to date. Returns the record."""
    stages = list(rust_stages() if stages is None else stages)
    listed = load_failing(failing_path)
    seen_seeds = {(e["seed"], e["households"], json.dumps(e.get("pins") or {}, sort_keys=True)) for e in listed}
    specs = gate_specs(start) + [(e["seed"], e["households"], dict(e.get("pins") or {})) for e in listed]
    rows, kept, by_seed = [], [], {}
    rolled = {key: roll(key[0], key[1], json.loads(key[2]), stages) for key in dict.fromkeys((sd, hh, json.dumps(p, sort_keys=True)) for sd, hh, p in specs)}
    # what the Rust stages up to each one OWN - the parts any of them wrote, on any seed: owned[i] judges the map after stage i
    owned = [set().union(*(e[2] for r in rolled.values() for e in r["trace"][: i + 1])) for i in range(len(stages))]
    for (seed, n, pins), r in rolled.items():
        lines, stage, frozen = verdict(r, owned)
        rows.append({"seed": seed, "households": n, "pins": json.loads(pins), "verdict": "fail" if lines else "pass", "stage": stage, "failures": lines})
        by_seed[(seed, n, pins)] = (lines, stage, frozen)
    replays = []
    for e in listed:  # the list's entries: the seed rolled above, its frozen input replayed here
        key = (e["seed"], e["households"], json.dumps(e.get("pins") or {}, sort_keys=True))
        seed_lines = by_seed[key][0]
        frozen_lines = replay(e["frozen"], e["stage"], stages, owned) if e.get("frozen") else []
        replays.append({"seed": e["seed"], "stage": e["stage"], "frozen": e.get("frozen"), "failures": frozen_lines})
        if seed_lines or frozen_lines:  # it stays until both pass: the seed, and the input its stage failed on
            kept.append({**e, "seed_passes": not seed_lines, **({} if frozen_lines else {"frozen": None})})
    for (seed, n, pins), (lines, stage, frozen) in by_seed.items():
        if lines and (seed, n, pins) not in seen_seeds:
            path = None
            if frozen is not None:
                os.makedirs(frozen_dir, exist_ok=True)
                path = os.path.join(frozen_dir, f"{seed}-{stage}.pkl")
                with open(path, "wb") as fh:
                    fh.write(frozen)
            kept.append({"seed": seed, "households": n, "pins": json.loads(pins), "stage": stage, "failure": lines[0], "frozen": path})
    os.makedirs(os.path.dirname(failing_path), exist_ok=True)
    with open(failing_path, "w", encoding="utf-8") as fh:
        json.dump(kept, fh, indent=1)
        fh.write("\n")
    for e in listed:
        if e.get("frozen") and not any(k.get("frozen") == e["frozen"] for k in kept) and os.path.exists(e["frozen"]):
            os.remove(e["frozen"])  # its replay passed: the fixture leaves with its entry
    failing = sum(1 for r in rows if r["verdict"] == "fail") + sum(1 for r in replays if r["failures"])
    return {"rust_stages": [stage_name(st) for st in stages], "start": start, "seeds": rows, "replays": replays, "failing": failing}


def write_record(record: dict[str, Any], log: str = LOG) -> str:
    """The run, with the engine it rolled (`ci.delta.engine_key_worktree`, what the landing asks a record by)."""
    from pathlib import Path  # noqa: PLC0415

    from l7r.diagram.ci.delta import engine_key_worktree  # noqa: PLC0415

    os.makedirs(log, exist_ok=True)
    path = os.path.join(log, f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({**record, "engine": engine_key_worktree(Path(HERE))}, fh, indent=1)
        fh.write("\n")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--start", type=int, required=True, help="the fresh block's first seed (cohort_gate.py fresh-seed)")
    args = ap.parse_args(argv)
    off = off_the_front(STAGES, rust_stages())
    if off:
        print(f"rust-gate: REFUSED - Rust stage(s) {', '.join(off)} are not the front of STAGES: port the stages in STAGES order (FR-019)", file=sys.stderr)
        return 1
    record = run(args.start)
    path = write_record(record)
    for r in [*record["seeds"], *record["replays"]]:
        for line in r["failures"]:
            print(f"rust-gate: seed {r['seed']} ({r['stage']}): {line}")
    print(
        f"rust-gate: {len(record['seeds'])} seed(s) through {', '.join(record['rust_stages']) or 'no Rust stage'}, {len(record['replays'])} frozen input(s); {record['failing']} failing - record {os.path.relpath(path, HERE)}"
    )
    return 1 if record["failing"] else 0


if __name__ == "__main__":
    sys.exit(main())

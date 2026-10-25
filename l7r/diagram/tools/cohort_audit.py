#!/usr/bin/env python3
"""Roll a cohort of scripted hamlets, gate every one, and report WHY each failure happened.

`hamletgen.py --batch N` answers "how many pass". This answers the next question - "what exactly is
colliding with what" - which is the one you need to fix them. For every failing map it prints the
check's own message (not a re-derivation of it) plus, for the overlap checks, the manifest keys and
coordinates of the offending pair, so a fix can be aimed rather than guessed at.

WHY THIS EXISTS RATHER THAN A GREP OVER THE GATE OUTPUT: the gate prints one line per check across
~185 checks per map, so a twelve-map cohort is ~2,200 lines of PASS to read a dozen FAILs out of.
And a diagnostic that re-implements a check drifts from it (the skill's dev notes have three
incidents on record), so this one only ever quotes what the gate said.

    python3 -m l7r.diagram.tools.cohort_audit                 # 12 hamlets from seed 1
    python3 -m l7r.diagram.tools.cohort_audit --count 24 --seed 1
    python3 -m l7r.diagram.tools.cohort_audit --only features_do_not_overlap   # just the maps failing one check
    python3 -m l7r.diagram.tools.cohort_audit --jobs 1        # serial (parallel across processes by default)
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import contextlib
import io
import os
import sys
from collections.abc import Sequence
from typing import Any

HERE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)  # the skill root; this module lives in l7r/diagram/tools/ - FOUR levels up since feature 119, not two
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from l7r.diagram import hamletgen as hg  # noqa: E402
from l7r.diagram.hamletgen.homesteads.row_rules import bamboo_mismatch, row_rules, water_rules  # noqa: E402
from l7r.diagram.hamletgen.ways.checks import track_ends_off_the_web  # noqa: E402
from l7r.diagram.hamletgen.ways.knots import lane_knots  # noqa: E402
from l7r.diagram.overlap import matrix_violations  # noqa: E402
from l7r.diagram.settlement._geom.water_index import crosses_a_stream  # noqa: E402 - the same-bank rule's one predicate (feature 417 T04)
from l7r.diagram.settlement.homestead_parts.grove_rules import fixtures_on_groves, gardens_east_shaded, grove_sides_missing, groves_crossed_by_lanes, groves_off_windward  # noqa: E402
from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT, CANOPY_SHADE_FT, bamboo_shading_plots, trees_shading_plots  # noqa: E402
from l7r.diagram.tools.cohort_roll import ROLL_TARGET, Refusal, roll_or_refusal  # noqa: E402 - imported by NAME, so one class in every process (cohort_roll's docstring)

_PART_KEYS = ("gardens", "threshing_yards", "farm_fixtures", "byres", "farm_sheds", "retirement_houses", "persimmons", "bamboo_stands")


def parts_across_brook(manifest: dict) -> int:
    """How many farmstead parts stand across a stream from the house they belong to (feature 261 FR-013 / SC-009): a part
    that names its house (`of`) whose straight line to it crosses a reach of any stream. Asked by the placers' own predicate,
    `crosses_a_stream` (feature 417 T04, D12: the audit's copy of the segment test was the rule coded a fourth time)."""
    streams = manifest.get("streams") or []
    parts = [r for k in _PART_KEYS for r in manifest.get(k) or [] if r.get("of")]
    return sum(1 for r in parts if crosses_a_stream(r["of"], (r["x"], r["y"]), streams))


# THE ROW VILLAGE'S KNOBS, EACH VALUE ROLLED FOR CERTAIN (feature 291 plan D19; SC-007, SC-008): with the linear form two
# in ten and flood ground forcing the dry edge, 24 seeds do not promise every value of `row_line`, `row_sides` and
# `row_water` - so the audit adds four PINNED linear hamlets, each line with each side count, the water alternating.
PINNED_ROWS: tuple[dict[str, str], ...] = (
    {"row_line": "street", "row_sides": "one", "row_water": "own"},
    {"row_line": "street", "row_sides": "both", "row_water": "shared"},
    {"row_line": "edge", "row_sides": "one", "row_water": "shared"},
    {"row_line": "edge", "row_sides": "both", "row_water": "own"},
    # ...AND THE DISPERSED FARM'S WATER (amendment 5; SC-008): the dispersed form one in ten, so a pinned hamlet per value
    {"settlement_form": "dispersed", "farm_water": "channel"},
    {"settlement_form": "dispersed", "farm_water": "well"},
)
PINNED_FIRST_SEED = 901


def refused_verdict(hspec: Any, refused: BaseException) -> tuple[str, list[str], list[str]]:
    """The verdict of a roll that raised (`roll_one`): its header - the form its plan rolled - and the refusal by name."""
    form = hg.plan_site(hspec).settlement_form
    name = type(refused).__name__
    return (f"{hspec.name} households={hspec.households} form={form} REFUSED", [f"refused:{name}"], [f"FAIL refused:{name} -> {str(refused)[:300]}"])


def _report_of(hspec: Any) -> tuple[Any, str]:
    """`generate(hspec)` through the roll cache (feature 375 amendment 7, FR-029): served when nothing the roll executes
    changed, rolled in a child otherwise, under the cohort's own subject - a refusal stored too (the plan review: 374's cohort
    had two refused seeds, which rolled again on every run). A cohort re-rolled every seed on every run: a feature's "before"
    leg rolled unchanged code again each wave, its "after" leg re-rolled seeds the change never reached (109 minutes of
    feature 374's tool time). Returns (the report or a `Refusal`, how); a crash raises."""
    from l7r.diagram.pipeline import rollcache  # noqa: PLC0415 - the engine's serving layer, imported where it is used

    payload, how = rollcache.obtain(f"cohort:{hspec!r}", lambda: roll_or_refusal(hspec), recorded=lambda: rollcache._in_child(ROLL_TARGET, hspec))  # noqa: SLF001
    return (payload if isinstance(payload, Refusal) else payload[2]), how


def roll_one(spec: tuple[int, int] | tuple[int, int, dict[str, str]]) -> tuple[str, list[str], list[str]]:
    """`roll_how`'s verdict alone."""
    return roll_how(spec)[0]


def roll_how(spec: tuple[int, int] | tuple[int, int, dict[str, str]]) -> tuple[tuple[str, list[str], list[str]], str]:
    """Roll and gate ONE audit hamlet: ((header line, sorted failures, the gate's own FAIL lines), how) - `how` is `served`
    (the roll cache had it, a stored refusal too) or `rolled`.

    Runs in a worker process. Safe to fan out because a map is a pure function of its spec - the
    seed fixes every draw (see "RANDOMNESS IS POSITIONAL OR SCOPED" in this skill's CLAUDE.md), so
    parallelism can only change the wall clock, never a verdict."""
    seed, households = spec[0], spec[1]
    pins: dict[str, str] = dict(spec[2]) if len(spec) > 2 else {}  # type: ignore[misc]
    from l7r.diagram.hamletgen.plan import beyond_the_band

    with beyond_the_band():  # a HOUSEHOLDS= cohort asks the scaling sizes past the hamlet band, as the perf snapshot does (feature 328)
        hspec = hg.HamletSpec(name=f"Audit-{seed:02d}", seed=seed, households=households, **({"settlement_form": "linear", **pins} if pins else {}))  # type: ignore[arg-type]  # a pin's own form wins
    # THROUGH `generate`, NOT `build` - the audit must measure the path that SHIPS. It called `build`
    # directly, which skips everything `generate` does around the stages: it finishes into a scratch
    # directory, gates in-process, and re-rolls a map whose finished manifest strands a farmhouse. So
    # a fix living in `generate` was invisible to the cohort - measured on seed 5, which passes
    # through `generate` and failed in the audit. A harness that exercises a different code path than
    # production reports on a map nobody will ever see.
    # A REFUSED SITE IS ONE SEED'S VERDICT, NOT THE AUDIT'S END (feature 291 on 287): since feature 287 a roll that cannot keep
    # its rules is refused by name (`SiteRefused`, `WebRefused`, `BrookRefused`, ...) rather than shipped, and the first one
    # raised through the process pool ended the whole cohort with no report of the other 29 seeds
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            report, how = _report_of(hspec)
    except Exception as refused:  # noqa: BLE001 - a roll that could not finish (a crash) is reported by its own name
        return refused_verdict(hspec, refused), "rolled"
    if isinstance(report, Refusal):  # the engine's refusal by name, served or rolled (feature 375 amendment 7)
        return refused_verdict(hspec, report.exception()), ("served" if how == "HIT" else "rolled")
    _breach = ((getattr(report, "manifest", None) or {}).get("meta") or {}).get("scatter_frame_breach")  # a test's stub report carries no manifest
    if _breach:  # feature 224: the scatter's predicted frame was too small - a strip inside the view may hold no scatter
        report.fail_lines.append(f"FAIL scatter_frame_breach -> the view reaches {_breach} px past the predicted scatter frame (left, top, right, bottom)")
        report.failures.append("scatter_frame_breach")
    # A ROLL THAT SEATS FEWER HOUSEHOLDS THAN IT DECLARED IS A FAILURE HERE TOO (feature 226): the roll's own verdict is
    # the reach count, the pool's gate holds `households_consistent` over the shipped maps, and nothing in between - a
    # cohort seed that quietly seated 13 of 20 read as a pass. The manifest carries `meta.roll_placed` since feature 215.
    _meta = (getattr(report, "manifest", None) or {}).get("meta") or {}
    _placed = _meta.get("roll_placed")
    if _placed is not None and int(_placed) < households:
        report.fail_lines.append(f"FAIL households_seated -> {int(_placed)} of {households} declared households seated")
        report.failures.append("households_seated")
    _across = parts_across_brook(getattr(report, "manifest", None) or {})
    if _across:
        report.fail_lines.append(f"FAIL farmstead_across_brook -> {_across} farmstead part(s) stand across the brook from their house")
        report.failures.append("farmstead_across_brook")
    # THE MATRIX OVER EVERY COHORT ROLL (feature 291). `features_do_not_overlap` was a seed test over the POOL's rolls
    # only (tests/gate/test_no_feature_overlaps.py), so a cohort seed whose grove lay on a lane or a crown on a byre read
    # as a pass here - the 24/24 feature 291 first measured with the dispersed and linear forms back in the roll, while
    # feature 126 had measured exactly those overlaps on the same forms.
    _mx = matrix_violations(getattr(report, "manifest", None) or {}) if getattr(report, "manifest", None) else []
    if _mx:
        report.fail_lines.append(f"FAIL features_do_not_overlap -> {len(_mx)} forbidden overlap(s), e.g. {_mx[:3]}")
        report.failures.append("features_do_not_overlap")
    # ...AND THE GROVE'S OWN RULES (feature 291, `grove_rules`): every rolled side planted at every farm, the deep stand on
    # the windward faces, no garden's morning sun cut off - the three feature 126 measured that the matrix cannot see - no
    # lane across a band, and no fixture standing inside one (the matrix abstains on VEGETATION).
    _M = getattr(report, "manifest", None) or {}
    # ...AND THE KNOT RULE THE POOL HOLDS (feature 328 wave 93, `ways.knots.lane_knots`): only the pool's seed test asked it, so
    # a change that left lane ends knotted on three pool maps read 54/54 here
    _knots = lane_knots(_M.get("lanes") or [], _M)
    if _knots:
        report.fail_lines.append(f"FAIL lane_knots -> {len(_knots)} knot(s), e.g. {_knots[:2]}")
        report.failures.append("lane_knots")
    # ...AND THE ROW VILLAGE'S AND THE GROVE FARM'S (feature 291 amendment 3, `homesteads/row_rules.py`).
    for name, found in (
        ("grove_sides_missing", grove_sides_missing(_M)),
        ("groves_off_windward", groves_off_windward(_M)),
        ("gardens_east_shaded", gardens_east_shaded(_M)),
        ("groves_crossed_by_lanes", groves_crossed_by_lanes(_M)),
        ("track_ends_off_the_web", track_ends_off_the_web(_M)),  # feature 417 D27: 0081, never stops in open country
        ("fixtures_on_groves", fixtures_on_groves(_M)),
        ("row_rules", row_rules(_M)),
        ("water_rules", water_rules(_M)),
        ("bamboo_mismatch", bamboo_mismatch(_M)),
        ("trees_shading_plots", trees_shading_plots(_M, CANOPY_SHADE_FT)),  # GM 2026-10-02, feature 310
        ("bamboo_shading_plots", bamboo_shading_plots(_M, BAMBOO_SHADE_FT)),  # GM 2026-10-02, feature 315
    ):
        if found:
            report.fail_lines.append(f"FAIL {name} -> {len(found)}, e.g. {found[:2]}")
            report.failures.append(name)
    plan = report.plan
    header = f"--- Audit-{seed:02d}  seed={seed} households={households} form={getattr(plan, 'settlement_form', '?')} sides={getattr(plan, 'grove_sides', '?')} fall={int(plan.down_deg)} sink={plan.water_sink} shape={plan.cluster_shape} lanes={plan.lane_skeleton}"
    if getattr(plan, "settlement_form", None) == "linear":
        header += f" row={getattr(plan, 'row_line', '?')}/{getattr(plan, 'row_sides', '?')}/{getattr(plan, 'row_water', '?')}"
    if getattr(plan, "settlement_form", None) == "dispersed":
        header += f" water={getattr(plan, 'farm_water', '?')}"
    if getattr(plan, "settlement_form", None) == "nucleated":
        drawn = sorted({str(w.get("form")) for w in _M.get("wells") or [] if w.get("form")})
        header += f" wells={getattr(plan, 'well_siting', '?')}/{'+'.join(drawn) or 'none'}"
    if _meta.get("seat_offwind"):
        header += " seat=OFFWIND"
    return (header, report.failures, report.fail_lines), ("served" if how == "HIT" else "rolled")


#: a rolled knob value is DEAD when it is rolled this many times or more and never drawn (the round arbiter's tooling fix on
#: ask:w154-lane-wells: the lane-side well form was rolled on five hamlets and drawn on none, caught only by an arbiter)
NEVER_DRAWN_ROLLS = 3


def never_drawn(headers: Any) -> list[str]:
    """Each per-settlement knob value the cohort ROLLED at least `NEVER_DRAWN_ROLLS` times and never DREW, as `knob=value`:
    a clustered hamlet's well siting (`wells=<rolled>/<forms drawn>`), drawn where a well of that form stands."""
    rolled: collections.Counter[str] = collections.Counter()
    drawn: set[str] = set()
    for h in headers:
        if " wells=" not in h:
            continue
        siting, forms = h.split(" wells=")[1].split()[0].split("/", 1)
        rolled[siting] += 1
        if siting in forms.split("+"):
            drawn.add(siting)
    return [f"well_siting={v}" for v, n in sorted(rolled.items()) if n >= NEVER_DRAWN_ROLLS and v not in drawn]


def fresh_specs(fresh: int, fresh_from: int | None) -> list[Any]:
    """THE FRESH BLOCK (feature 386, the GM 2026-10-17: "a block of fresh seeds that rotates each run, recorded as a failure rate
    rather than a pass/fail"): `fresh` seeds from `fresh_from`, a start the Makefile derives from the engine's content
    (`scripts/gates/cohort_gate.py fresh-seed`, 10000 or more), so no fixed seed, pinned row or hand roll is among them. Seeds 1-48
    all passed on main while 6 of 48 never-rolled seeds failed: fixes had been aimed at the fixed seeds, so only seeds nobody tuned
    on say how the generator does."""
    if not fresh or fresh_from is None:
        return []
    return [(fresh_from + i, 10 + ((fresh_from + i) * 7) % 11) for i in range(fresh)]


def fresh_line(specs: Sequence[Any], results: Sequence[tuple[str, list[str], list[str]]]) -> str:
    """The fresh block's RATE - printed, never counted in the pass count or the exit code (feature 386, FR-002)."""
    bad = [spec[0] for spec, (_h, failures, _l) in zip(specs, results, strict=True) if failures]
    return (
        f"fresh block from seed {specs[0][0]}: {len(bad)} of {len(specs)} failed ({100 * len(bad) / len(specs):.0f}%)"
        + (f" - seeds {', '.join(map(str, bad))}" if bad else "")
        + "; a rate, never a pass/fail (make cohort-seeds keeps the trend)"
    )


def audit(count: int, first_seed: int, only: str | None = None, jobs: int | None = None, households: int | None = None, fresh: int = 0, fresh_from: int | None = None) -> int:
    """Roll `count` hamlets, gate each, and print the failures with the gate's own messages.

    The rolls fan out across processes (the 2026-08-15 timings block flagged the serial cohort as
    the biggest available win: 24 maps x ~12 s on an idle 22-cpu box). Results are collected and
    printed in seed order, so the report reads identically to the serial one. `households` rolls every seed at that size,
    the scaling rolls' question (does a change refuse a larger hamlet?) asked without timing it (feature 328), and leaves
    the pinned rows out, as `only` does - and the fresh block with them. The fresh block rolls in the same pool and lands in the same
    record, each seed marked `fresh`; its failures print as a rate after the report and count in neither the pass count nor the exit."""
    specs: list[Any] = [(first_seed + i, households if households is not None else 10 + ((first_seed + i) * 7) % 11) for i in range(count)]
    specs += [(PINNED_FIRST_SEED + i, 10 + ((PINNED_FIRST_SEED + i) * 7) % 11, pins) for i, pins in enumerate(PINNED_ROWS)] if not (only or households) else []
    count = len(specs)
    extra = fresh_specs(fresh, fresh_from) if not (only or households) else []
    jobs = hg.default_jobs(count + len(extra)) if jobs is None else max(1, jobs)  # ONE courtesy rule, defined in the driver
    if jobs == 1:
        rolled = [roll_how(s) for s in [*specs, *extra]]
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
            rolled = list(ex.map(roll_how, [*specs, *extra]))
    write_record([*specs, *extra], rolled, first_seed, households, fresh=len(extra))
    rolled, fresh_rolled = rolled[:count], rolled[count:]
    results = [r for r, _how in rolled]

    tally: collections.Counter[str] = collections.Counter()
    failing = 0
    for header, failures, fail_lines in results:
        if only:
            failures = [f for f in failures if f.startswith(only)]
        if not failures:
            continue
        failing += 1
        tally.update(f.split("[")[0] for f in failures)
        print(f"\n{header}")
        for line in fail_lines:
            if not only or only in line:
                print("   ", line)
    # WHICH FORMS THE COHORT ROLLED (feature 291): a green cohort says nothing about a form none of its seeds drew
    forms = collections.Counter(h.split(" form=")[1].split()[0] for h, _f, _l in results if " form=" in h)
    print(f"\nforms rolled: {', '.join(f'{k} {v}' for k, v in sorted(forms.items()))}")
    sides = collections.Counter(h.split(" sides=")[1].split()[0] for h, _f, _l in results if " sides=" in h and " form=nucleated" not in h)
    print(f"grove sides among the farms that carry a grove: {', '.join(f'{k} sides {v}' for k, v in sorted(sides.items()))}")
    rows = [h.split(" row=")[1].split()[0].split("/") for h, _f, _l in results if " row=" in h]
    missing = [
        f"{knob}={v}"
        for i, (knob, space) in enumerate((("row_line", ("street", "edge")), ("row_sides", ("one", "both")), ("row_water", ("own", "shared"))))
        for v in space
        if v not in {r[i] for r in rows}
    ]
    waters = {h.split(" water=")[1].split()[0] for h, _f, _l in results if " water=" in h}
    missing += [f"farm_water={v}" for v in ("channel", "well") if v not in waters]
    print(f"row villages: {len(rows)}; knob values never rolled: {', '.join(missing) or 'none'}")
    if missing and not only:
        failing += 1
        tally.update(["row_knob_value_never_rolled"])
    dead = never_drawn(h for h, _f, _l in results)
    print(f"knob values rolled but never drawn: {', '.join(dead) or 'none'}")
    if dead and not only:
        failing += 1
        tally.update(["knob_value_never_drawn"])
    print(f"\n{count - failing}/{count} passed the whole gate")
    if extra:
        print(fresh_line(extra, [r for r, _how in fresh_rolled]))
    if tally:
        print("residue by check:")
        for name, n in tally.most_common():
            print(f"  {n:3d}  {name}")
    return 0 if failing == 0 else 1


#: where the per-seed records go: None means the clone's own `dev/cohort-log/` (`log_dir`)
LOG_DIR: str | None = None


def write_record(specs: Sequence[Any], rolled: Sequence[tuple[tuple[str, list[str], list[str]], str]], first_seed: int, households: int | None, fresh: int = 0) -> str:
    """The cohort's PER-SEED RECORD (feature 375 amendment 7, FR-029): one file a run under `dev/cohort-log/` - per seed,
    served or rolled, its verdict and the failures it found - so whether fewer seeds would find the same failures can be
    counted (feature 374's findings by seed lived only in its plan's prose). `make cohort` commits it, as `make done` does
    its run record. The last `fresh` specs are the fresh block (feature 386): each is marked `"fresh": true`, and the record names
    the block's first seed and size. Returns the path."""
    import json  # noqa: PLC0415
    import re  # noqa: PLC0415
    import subprocess  # noqa: PLC0415
    import time  # noqa: PLC0415

    def git(*a: str) -> str:
        p = subprocess.run(["git", "-C", HERE, *a], capture_output=True, text=True, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""

    seeds = []
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    # A "before" leg rolled in a detached worktree keeps its record in the CLONE (the plan review): the worktree is removed
    clone_root = os.path.dirname(common) if os.path.basename(common) == ".git" else HERE
    log_dir = LOG_DIR or os.path.join(clone_root, "dev", "cohort-log")
    first_fresh = len(specs) - fresh
    for i, (spec, ((header, failures, _lines), how)) in enumerate(zip(specs, rolled, strict=True)):
        verdict = "refused" if any(f.startswith("refused:") for f in failures) else ("fail" if failures else "pass")
        seeds.append(
            {
                "seed": spec[0],
                "households": spec[1],
                "pins": dict(spec[2]) if len(spec) > 2 else {},
                "how": how,
                "verdict": verdict,
                "failures": list(failures),
                # ...WITH EACH RULE'S COUNT (feature 385 T03, the round arbiter's tooling fix on hour:385-approach-checklist@6): a
                # seed failing at HEAD and after a change read as "pre-existing" though its lane knots went from 1 to 4 (seed 57)
                "counts": {m.group(1): int(m.group(2)) for line in _lines if (m := re.match(r"FAIL (\S+) -> (\d+)", line))},
                "form": header.split(" form=")[1].split()[0] if " form=" in header else "",
                **({"fresh": True} if i >= first_fresh else {}),
            }
        )
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    top = git("rev-parse", "--show-toplevel")
    where = top.split("/.clones/")[1].split("/")[0] if "/.clones/" in top else os.path.basename(top or HERE)
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, f"{stamp}-{where}-{os.getpid()}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "utc": stamp,
                "clone": where,
                # the feature whose change it was rolled on (feature 375 amendment 8, FR-038): `make cohort-seeds` counts the
                # changes the records span by it - the number of SPECIFY_FEATURE, which every spec-kit session exports
                "feature": (re.match(r"\d+", os.environ.get("SPECIFY_FEATURE", "")) or [""])[0],
                "commit": git("rev-parse", "--short", "HEAD"),
                "first_seed": first_seed,
                "households": households,
                "count": len(seeds),
                "served": sum(s["how"] == "served" for s in seeds),
                **({"fresh_first": specs[first_fresh][0], "fresh_count": fresh} if fresh else {}),
                "seeds": seeds,
            },
            fh,
            indent=1,
        )
        fh.write("\n")
    gitdir = git("rev-parse", "--absolute-git-dir") if LOG_DIR is None else ""  # a test's own directory names nothing
    if gitdir:  # named for `make cohort`'s commit of this one file (scripts/gates/commit-run-record.sh)
        with open(os.path.join(gitdir, "last-cohort-record"), "w", encoding="utf-8") as fh:
            fh.write(os.path.abspath(path))
    return path


def _reference_ok() -> list[str]:
    """Roll the REFERENCE settlement and return its failures - empty when it is clean.

    One map, about a minute. It is the cheapest question in the loop and it gates the most expensive
    answer, which is the whole point of the tier ladder (constitution VI)."""
    rep = hg.generate(hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", settlement_form="nucleated"), out_base=None, render=False)
    for f in rep.failures:
        print(f"  reference: {f}", flush=True)
    return list(rep.failures)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--count", type=int, default=10)  # the GM, 2026-10-12: ten (feature 375 amendment 8, FR-038)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--only", default=None, help="report only failures of this check")
    ap.add_argument("--jobs", type=int, default=None, help="worker processes (default: cpus - 2, capped at --count)")
    ap.add_argument("--households", type=int, default=None, help="roll every seed at this size (the scaling question, untimed)")
    ap.add_argument("--fresh", type=int, default=0, help="roll this many fresh seeds beside the fixed ones - a rate, never a pass/fail (feature 386)")
    ap.add_argument("--fresh-from", type=int, default=None, help="the fresh block's first seed (make cohort derives it from the engine)")
    ap.add_argument("--anyway", action="store_true", help="run even if the reference settlement is failing (say why in the same breath)")
    args = ap.parse_args(list(argv) if argv is not None else None)

    # THE REFERENCE SETTLEMENT IS A GATE, NOT A SUGGESTION (GM 2026-08-24).
    #
    # A cohort is 20-25 minutes. The reference hamlet is 60 SECONDS and answers the only question
    # worth asking while it is red: is the thing I just changed even coherent? Running the sweep
    # first is how a session spends two hours re-discovering that its tree is broken - which is
    # exactly what happened during feature 126: SIX cohorts in one sitting, most of them launched
    # when the failures were already known.
    #
    # `make maps` already gated on this. It did not help, because this module has its own entry
    # point and that is the one a session reaches for when it wants the seed list. A guard on one
    # door is not a guard. So the check lives HERE, in the expensive thing itself, where it cannot
    # be walked around by picking a different command.
    #
    # `--anyway` exists because a rule with no escape hatch gets worked around rather than used -
    # but it is deliberately awkward to type and it prints why it was wrong to need it.
    if not args.anyway:
        print("checking the reference settlement first (60 s) - the cohort is minutes, every unchanged seed served from the roll cache\n", flush=True)
        ref = _reference_ok()
        if ref:
            print(f"\n\033[1mREFERENCE SETTLEMENT IS FAILING\033[0m: {', '.join(ref)}")
            print("\nThe cohort is not run. Fix the reference map first - it rebuilds in about a minute,")
            print("and a sweep launched over a broken tree costs minutes and tells you what you already know.")
            print("Then: make cohort")
            print("(--anyway overrides, when you genuinely need the seed list from a red tree.)")
            return 2
        print("\033[1mreference settlement clean\033[0m - running the cohort\n", flush=True)
    return audit(args.count, args.seed, args.only, args.jobs, args.households, args.fresh, args.fresh_from)


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.cohort_audit")
    raise SystemExit(main())

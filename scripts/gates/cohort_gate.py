"""The landing cohort: 48 seeds when engine work lands, and a fresh-seed rate (feature 386).

    python3 scripts/gates/cohort_gate.py fresh-seed     the fresh block's first seed for this engine (plan D3)
    python3 scripts/gates/cohort_gate.py check          would the gated push take this engine? exit 0 yes, 1 no
    python3 scripts/gates/cohort_gate.py needs-baseline exit 0 when main's engine has no 48-seed record to be the baseline
    python3 scripts/gates/cohort_gate.py counter-only   exit 0 when the delta only adds counter blocks (feature 446)

WHY. The cohort is the hamlet generator's strongest test bed and nothing asked for one: sessions rolled it by hand, nearly always
at the ten-seed default. About 30 ten-seed cohorts passed on 2026-10-12/13 and the next 48-seed run failed on seeds 17, 21, 40
and 45; and seeds 1-48 all pass on main while 48 seeds nobody had rolled (400-447) failed 6 times (`specs/386-landing-cohort/`).
So the gated push (engine code in the delta) requires a landing record rolled on exactly the engine it lands - 48 fixed seeds,
the pinned rows and a FRESH block of 48 seeds from a start that rotates with the engine - refuses a fixed or pinned seed that
regressed against main (`cohort_known`'s own reading), and prints the fresh block's failure rate, never refusing on it. `make
cohort-landing` rolls it; every `make cohort` rolls a smaller fresh block beside its ten fixed seeds (`cohort_audit --fresh`).
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "measure"))  # the moved scripts it imports
import cohort_known  # noqa: E402

LOG = pathlib.Path("dev/cohort-log")
#: the pinned rows `cohort_audit` adds to every unscoped roll: seeds 901-906 (`PINNED_FIRST_SEED` and its six `PINNED_ROWS`)
PINNED = frozenset(range(901, 907))
#: the landing cohort's size, fixed and fresh alike - the 48 the GM's recommendation names, so a block's rate compares with 400-447's
SEEDS = 48
#: the fresh blocks start here: above the fixed range, the pinned rows and every hand roll the log holds
FRESH_BASE = 10000
FRESH_SPAN = 990000
COMMAND = "make cohort-landing"


def git(root: pathlib.Path, *a: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=False)


def fresh_seed(root: pathlib.Path, ref: str | None = None) -> int:
    """The fresh block's first seed: from the working tree's engine key (or `ref`'s - `make probe` rolls HEAD's block, feature
    426 D5), so one engine always rolls one block (plan D3) - and a docs, comment or docstring edit is the same engine
    (`cohort_known.engine_key`)."""
    h = hashlib.sha256(cohort_known.engine_key(root, ref).encode()).hexdigest()
    return FRESH_BASE + int(h[:12], 16) % FRESH_SPAN


def fixed(rec: dict[str, Any]) -> list[dict[str, Any]]:
    """The record's fixed seeds: neither a pinned row nor a fresh seed."""
    return [s for s in rec.get("seeds") or [] if int(s["seed"]) not in PINNED and not s.get("fresh")]


def fresh(rec: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in rec.get("seeds") or [] if s.get("fresh")]


def landing_shaped(rec: dict[str, Any], need_fresh: bool = True) -> bool:
    """48 fixed seeds from seed 1 at the rolled sizes, no uncommitted engine diff, every seed rolled (a FAILED_FIRST, LAST_FAILED
    or EXITFIRST run that skipped some is `partial`, feature 426 D4) - and, for the landing record, its fresh block."""
    return (
        int(rec.get("first_seed") or 0) == 1
        and rec.get("households") is None
        and len(fixed(rec)) >= SEEDS
        and not rec.get("engine_diff")
        and not rec.get("partial")
        and (len(fresh(rec)) >= SEEDS or not need_fresh)
    )


def on_engine(root: pathlib.Path, rec: dict[str, Any]) -> bool:
    """Was the record rolled on HEAD's engine (`cohort_known.same_key`: a docs, comment or docstring edit since is the same one)?"""
    c = str(rec.get("commit") or "")
    return bool(c) and git(root, "rev-parse", "-q", "--verify", f"{c}^{{commit}}").returncode == 0 and cohort_known.same_key(root, c, "HEAD")


def records(root: pathlib.Path) -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / LOG).glob("[0-9]*.json"))]


def pick(root: pathlib.Path, recs: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The newest landing record on HEAD's engine (plan D2)."""
    # ...its fixed seeds and pinned rows only: the fresh block rolls after the push since feature 415 (D5) - a rate, never a refusal
    return next((r for r in sorted(recs, key=lambda r: str(r.get("utc")), reverse=True) if landing_shaped(r, need_fresh=False) and on_engine(root, r)), None)


def rate_line(rec: dict[str, Any]) -> str:
    block = fresh(rec)
    if not block:  # the landing record since feature 415 (D5): its fresh block rolls after the push
        return "cohort-gate: the fresh block rolls after the push - a rate, never a refusal - the trend: make cohort-seeds"
    bad = [int(s["seed"]) for s in block if s.get("verdict") != "pass"]
    first = min(int(s["seed"]) for s in block)
    return (
        f"cohort-gate: fresh block from seed {first}: {len(bad)} of {len(block)} failed ({100 * len(bad) / len(block):.0f}%)"
        + (f" - seeds {', '.join(map(str, bad))}" if bad else "")
        + "; a rate, never a refusal - the trend: make cohort-seeds"
    )


def standing(root: pathlib.Path, landing: dict[str, Any], recs: list[dict[str, Any]]) -> list[str]:
    """`cohort_known`'s standing of the landing record against its baselines on main's engine (plan D4); it reads no fresh seed."""
    return cohort_known.standing(landing, cohort_known.baselines(landing, recs, lambda c: cohort_known.same_engine(root, c)))


REFUSING = (" NEWLY FAILING", " WORSENED", " NO BASELINE")


def check(root: pathlib.Path) -> tuple[list[str], list[str]]:
    """(refusals, notes): what the gated push refuses and what it prints."""
    recs = records(root)
    landing = pick(root, recs)
    if landing is None:
        why = f"no landing cohort ({SEEDS} seeds from seed 1 and the pinned rows) was rolled on the engine being landed - run: {COMMAND}"
        # 405 T125: the gate regenerates a pool map the change moved, which moves the engine key under a cohort already rolled -
        # T09's landing was refused so with 54/54 passed and nothing said of the map
        maps = [ln[3:] for ln in git(root, "status", "--porcelain", "--untracked-files=all", "--", "pool").stdout.splitlines() if ln[3:].endswith(".json")]
        if maps:
            why += f"; the tree has uncommitted pool maps ({', '.join(maps)}) - the gate regenerated what the change moved: read each diff, commit it, then land again"
        return [why], []
    refusals, notes = [], []
    for line in standing(root, landing, recs):
        (refusals if any(w in line for w in REFUSING) else notes).append(line)
    notes.append(rate_line(landing))
    return refusals, notes


def needs_baseline(root: pathlib.Path) -> bool:
    """Has main's engine no 48-seed record to be the landing record's baseline? `make cohort-landing` then rolls main's FIRST:
    `cohort_known.baselines` reads only records older than the one it judges (spec-fidelity, round 1)."""
    return not any(landing_shaped(r, need_fresh=False) and cohort_known.same_engine(root, str(r.get("commit") or "")) for r in records(root) if r.get("commit"))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = pathlib.Path(git(pathlib.Path("."), "rev-parse", "--show-toplevel").stdout.strip() or ".")
    what = args[0] if args else "check"
    if what == "fresh-seed":
        print(fresh_seed(root, args[1] if len(args) > 1 else None))
        return 0
    if what == "counter-only":
        # FEATURE 446: the delta against the merge base with origin/main only adds counter blocks (`cohort_known.counter_only`);
        # `make land` then rolls no fresh block after the push, and the same-engine test above already reads the landing as main's
        base = git(root, "merge-base", "HEAD", "origin/main").stdout.strip()
        return 0 if base and cohort_known.counter_only(root, base, "HEAD") else 1
    if what == "needs-baseline":
        return 0 if needs_baseline(root) else 1
    if what != "check":
        print(f"cohort_gate: unknown command {what!r} (fresh-seed | check | needs-baseline | counter-only)", file=sys.stderr)
        return 2
    refusals, notes = check(root)
    for line in notes:
        print(line)
    for line in refusals:
        print(f"cohort-gate: REFUSED {line}")
    return 1 if refusals else 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("cohort_gate", main()))

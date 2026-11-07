"""`scripts/measure/work_budget_rust.py` - `make work-budget` on the Rust driver (feature 443; feature 444 amendment 11).

The deleted Python roll counted the reference hamlet's stages; the Rust driver's `hamlet --budget`, built with the counters on,
now does, through the stages it runs (water frame, field, sink, seat, hem; waterward on a polder). Each stage's mean counted
operations at 10/20/40/80 households is set against its budget in `dev/work-budget.json` - per thing times the derivation's
items at that size (`items_at_<n>`, else the figure at 40 grown by the exponent) - and against an accepted stage's accepted
figure. `--write` replaces `dev/work-budget.md`, the standing record `work_budget_view.py` reads. Stdlib only.
"""

from __future__ import annotations

import datetime
import json
import math
import os
import subprocess
import sys
from pathlib import Path

SIZES = (10, 20, 40, 80)


def counted(root: Path, rows: dict[tuple[int, int], dict]) -> dict[str, dict[int, tuple[int, int]]]:
    """Each stage's mean operations and rolled seeds at each size, from the driver's `--budget` lines; each roll's stages, their
    totals and counters, filed in `rows` by (seed, households)."""
    env = {**os.environ, "HAMLET_ARGS": "--budget", "HAMLET_FEATURES": "counters"}
    run = subprocess.run(
        [sys.executable, str(root / "scripts/gates/rust_checks.py"), "hamlet", "--crate", str(root / "rust/phases")],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if run.returncode:
        sys.exit(f"work-budget: the driver's budget run failed:\n{run.stdout}{run.stderr}")
    totals: dict[str, dict[int, list[int]]] = {}
    for line in run.stdout.splitlines():
        cells = line.split("\t")
        if len(cells) == 4:  # `seed size stage ops`: a roll's stage
            seed, size, stage, ops = cells
            totals.setdefault(stage, {}).setdefault(int(size), []).append(int(ops))
            rows.setdefault((int(seed), int(size)), {}).setdefault(stage, {"total": int(ops), "ops": {}})
        elif len(cells) == 5:  # `seed size stage key n`: one of its counters
            seed, size, stage, key, n = cells
            rows[(int(seed), int(size))][stage]["ops"][key] = int(n)
    out = {k: {s: (sum(v) // len(v), len(v)) for s, v in per.items()} for k, per in totals.items()}
    return out


def budget_at(st: dict, size: int) -> float | None:
    """The stage's budget at `size`: per thing times the derivation's items there (the deleted `work_budget.py`'s), none unset."""
    items = st.get(f"items_at_{size}")
    return st["per_thing"] * items if items is not None and st.get("per_thing") is not None else None


def exponent(ops: list[int]) -> str:
    """The measured growth from 20 to 80 households, the old record's exponent column."""
    return f"{math.log(ops[3] / ops[1]) / math.log(4):.2f}" if ops[1] and ops[3] else "-"


def table(counts: dict[str, dict[int, tuple[int, int]]], budgets: dict) -> list[str]:
    """The record's table. `work_budget_view.py` reads it by header name and takes each row's last cell as its status and the one
    before as its ratio, so those two stay last."""
    head = "| stage | ops @10 | ops @20 | ops @40 | ops @80 | exponent | budget @40 | accepted @40 | ratio | status |"
    rows = [head, "|" + "---|" * 10]
    whole = dict.fromkeys(SIZES, 0)
    whole_budget = 0.0
    for stage, per in counts.items():
        st = budgets.get(stage, {})
        ops = [per.get(s, (0, 0))[0] for s in SIZES]
        for s, n in zip(SIZES, ops, strict=True):
            whole[s] += n
        b40 = budget_at(st, 40)
        whole_budget += b40 or 0.0
        ratio = f"{ops[2] / b40:.1f}x" if b40 and ops[2] else "-"
        acc = (st.get("accepted") or {}).get("40")
        cells = [stage, *(f"{n:,}" for n in ops), exponent(ops), f"{b40:,.0f}" if b40 else "-", f"{acc:,.0f}" if acc else "-", ratio]
        rows.append("| " + " | ".join([*cells, st.get("status", "unbudgeted")]) + " |")
    ratio = f"{whole[40] / whole_budget:.1f}x" if whole_budget else "-"
    cells = ["**the whole roll**", *(f"{whole[s]:,}" for s in SIZES), exponent(list(whole.values())), f"{whole_budget:,.0f}", "-", ratio]
    rows.append("| " + " | ".join([*cells, "through the cut"]) + " |")
    return rows


def run_file(counts: dict[str, dict[int, tuple[int, int]]], rows: dict[tuple[int, int], dict], when: str, head: str) -> dict:
    """The run's JSON in the deleted roll's shape: `work_budget_view.moved` reads `summary.stages.<stage>.per.<size>.ops`, the audit
    bundle `rows[].stages.<stage>.ops` (each counter)."""
    stages = {k: {"per": {str(s): {"ops": n, "rolled": r} for s, (n, r) in per.items()}} for k, per in counts.items()}
    rolls = [{"seed": seed, "households": size, "stages": st} for (seed, size), st in sorted(rows.items())]
    return {"meta": {"when": when, "engine": head, "driver": "rust"}, "rows": rolls, "summary": {"stages": stages}}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    budgets = json.loads((root / "dev/work-budget.json").read_text())["stages"]
    rolls: dict[tuple[int, int], dict] = {}
    counts = counted(root, rolls)
    lines = table(counts, budgets)
    print("\n".join(lines))
    over = [c[0] for c in (r.strip("| ").split(" | ") for r in lines[2:-1]) if c[-2].endswith("x") and float(c[-2][:-1]) > 2.0]
    if over:
        print(f"work-budget: past twice the budget at 40 (the audit's leeway, 444 FR-022): {', '.join(over)}")
    if "--write" in sys.argv:
        head = git_head(root)
        when = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        (root / "dev/work-budget.md").write_text(
            "# The work budget - the standing record (feature 443)\n\n"
            "Load this file when: you need what each stage of the hamlet roll costs in counted operations, against its budget.\n\n"
            f"Generated by `make work-budget` at {when} on engine {head} from the Rust driver (`hamlet --budget`, counters on), "
            "seeds 4, 25, 39, 47, the reference spec; each figure the mean over the seeds that rolled that size. Only the stages "
            "through the cut run (feature 444 amendment 11); the parked stages' last Python counts are in this file's git history. "
            "Budgets come from `dev/work-budget.json` (`make budget-set`).\n\n" + "\n".join(lines) + "\n"
        )
        stamp = when.replace("-", "").replace(":", "")
        run = root / "dev/work-budget" / f"{stamp}-rust-{head}.json"
        run.write_text(json.dumps(run_file(counts, rolls, when, head), indent=1, sort_keys=True) + "\n")
        print(f"work-budget: dev/work-budget.md and {run.relative_to(root)} written")
    return 0


def git_head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())

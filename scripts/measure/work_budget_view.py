"""`scripts/measure/work_budget_view.py` - the work budget's standing record, in view (feature 443 T04, FR-007, plan D8).

`make land` on engine code and `make speckit-todo` (under feature 444's row) print it, so every landing shows the distance from the
goal: the whole roll's line of `dev/work-budget.md`, every stage's status, and the stages whose counted operations at 40
households moved between the two newest runs in `dev/work-budget/`. Read from the files `make work-budget` writes; stdlib only,
so the landing and the todo list import it without the engine.
"""

from __future__ import annotations

import json
from pathlib import Path

RECORD = "dev/work-budget.md"
RUNS = "dev/work-budget"
ROLL = "| **the whole roll** |"


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _ops40(run: dict) -> dict[str, float]:
    out: dict[str, float] = {}
    for name, st in ((run.get("summary") or {}).get("stages") or {}).items():
        at = (st.get("per") or {}).get("40")
        if at:
            out[name] = at["ops"]
    return out


def moved(root: Path) -> list[str]:
    """`<stage> <before> -> <after>` for each stage whose operations at 40 households differ between the two newest runs."""
    runs = sorted((root / RUNS).glob("*.json"))
    if len(runs) < 2:
        return []
    old, new = (_ops40(json.loads(p.read_text(encoding="utf-8"))) for p in runs[-2:])
    return [f"{k} {old.get(k, 0):,.0f} -> {new.get(k, 0):,.0f}" for k in new | old if k != "roll" and old.get(k) != new.get(k)]


def lines(root: Path) -> list[str]:
    """The record's summary, or one line saying there is none yet."""
    path = root / RECORD
    if not path.is_file():
        return ["work budget: no standing record yet - `make work-budget` writes dev/work-budget.md"]
    rows = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("| ") and not ln.startswith(("| stage |", "|---"))]
    head = next((ln for ln in rows if ln.startswith(ROLL)), "")
    header = next((ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("| stage |")), "")
    cols = _cells(header)
    out = []
    if head:
        c = dict(zip(cols, _cells(head), strict=False))
        out.append(f"work budget (dev/work-budget.md): the whole roll {c.get('ops @40', '-')} counted operations @40, exponent {c.get('exponent', '-')}, budget {c.get('budget @40', '-')}, {c.get('status', '-')}")
    by: dict[str, list[str]] = {}
    for ln in rows:
        if ln.startswith(ROLL):
            continue
        c = _cells(ln)
        by.setdefault(c[-1], []).append(c[0] + (f" ({c[-2]})" if c[-2] != "-" else ""))
    out += [f"  {status} ({len(names)}): {', '.join(names)}" for status, names in by.items()]
    mv = moved(root)
    out.append("  moved since the previous run (@40): " + ("; ".join(mv) if mv else "none"))
    return out

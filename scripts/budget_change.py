#!/usr/bin/env python3
"""`scripts/budget_change.py` - the one writer of `dev/work-budget.json`, the hamlet roll's work budgets (feature 443 T03, plan D6).

THE TABLE: `{"program": {"ops_at_40": <ops>|null, "exponent": <e>|null}, "stages": {"<stage>": {...}}}`, one stage per entry of
`hamletgen.driver.STAGES` (named as `make work-budget` names them, `stage_` dropped). A stage is `unbudgeted`; `budgeted`, with
`per_thing` (basic operations per thing placed), `exponent` (its growth with households), `derivation` (the path of its
first-principles derivation) and `verdict` (the path of its `work-budget` MODE BUDGET verdict, whose first line is the verdict
word - T05's agent writes it so); or `accepted`, which adds `accepted` (its counted operations at 40 and 80 households - T04).

THE RULES (443 FR-005; the GM's approval of the design, 2026-10-28): a FIRST budget is set only from a SOUND verdict (`budget-set`;
LOOSE or UNDERIVED refuses); every later change, and the program's whole-roll budget, needs the GM's words (`budget-change`,
`budget-program`, WORDS checked against the session's transcript by `scripts/hooks/budget-change-hooks.sh`, which a make target
cannot do), and is logged with them in `dev/work-budget-changes.jsonl`. The table is a guard file: an edit other than through
these targets needs `GUARD_EDIT_OK`.

    budget_change.py set PHASE PER_THING EXPONENT DERIVATION VERDICT
    budget_change.py change PHASE TO [--exponent E] --words WORDS
    budget_change.py program OPS_AT_40 EXPONENT --words WORDS
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE = "dev/work-budget.json"
LOG = "dev/work-budget-changes.jsonl"
SOUND = "SOUND"


def load(root: Path) -> dict[str, Any]:
    return json.loads((root / TABLE).read_text(encoding="utf-8"))


def save(root: Path, table: dict[str, Any]) -> None:
    (root / TABLE).write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")


def verdict_of(path: Path) -> str:
    """The verdict word a MODE BUDGET verdict file opens with ('' when it is unreadable or empty)."""
    try:
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return ""
    return lines[0].split()[0].strip("*:`").upper() if lines else ""


def log(root: Path, row: dict[str, Any]) -> None:
    with (root / LOG).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"date": datetime.date.today().isoformat(), **row}) + "\n")


def _stage(table: dict[str, Any], phase: str) -> dict[str, Any] | str:
    st = table["stages"].get(phase)
    return st if st is not None else f"no stage `{phase}` in {TABLE} - the stages are: {', '.join(table['stages'])}"


ITEM_SIZES = (20, 40, 80)  # feature 444 D2: a budget is per_thing x the derivation's own items at each size


def set_budget(root: Path, phase: str, per_thing: float, exponent: float, derivation: str, verdict: str, items: dict[int, int] | None = None) -> str:
    """A first budget: '' when set, else why not."""
    table = load(root)
    st = _stage(table, phase)
    if isinstance(st, str):
        return st
    if st["status"] != "unbudgeted":
        return f"`{phase}` is {st['status']} already - a change needs the GM's words: make budget-change PHASE={phase} TO=<per thing> WORDS=\"<the GM's words>\""
    if not (root / derivation).is_file():
        return f"no derivation at {derivation}"
    got = verdict_of(root / verdict)
    if got != SOUND:
        return f"the verdict at {verdict} reads {got or 'nothing'}, not SOUND - a first budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}`)"
    if missing := [h for h in ITEM_SIZES if (items or {}).get(h) is None]:
        return f"no items at {', '.join(str(h) for h in missing)} households - a budget is per thing x the derivation's own items at each size: ITEMS_AT_20= ITEMS_AT_40= ITEMS_AT_80= (feature 444 D2)"
    table["stages"][phase] = {
        "status": "budgeted", "per_thing": per_thing, "exponent": exponent, "derivation": derivation, "verdict": verdict,
        **{f"items_at_{h}": (items or {})[h] for h in ITEM_SIZES},
    }
    save(root, table)
    return ""


def change_budget(root: Path, phase: str, to: float, exponent: float | None, words: str, items: dict[int, int] | None = None) -> str:
    """A budgeted stage's figure changed with the GM's words, and logged: '' when done, else why not."""
    if not words.strip():
        return "no WORDS - a budget changes only with the GM's own words"
    table = load(root)
    st = _stage(table, phase)
    if isinstance(st, str):
        return st
    if st["status"] == "unbudgeted":
        return f"`{phase}` has no budget yet - a first one is set from a SOUND verdict: make budget-set PHASE={phase} PER_THING= EXPONENT= DERIVATION= VERDICT="
    before = {"per_thing": st["per_thing"], "exponent": st["exponent"]}
    st["per_thing"] = to
    if exponent is not None:
        st["exponent"] = exponent
    for h, n in (items or {}).items():
        st[f"items_at_{h}"] = n
    save(root, table)
    log(root, {"what": "stage", "phase": phase, "from": before, "to": {"per_thing": st["per_thing"], "exponent": st["exponent"]}, "words": words})
    return ""


def set_program(root: Path, ops_at_40: int, exponent: float, words: str) -> str:
    """The whole roll's budget (444 FR-002), set with the GM's words and logged: '' when done, else why not."""
    if not words.strip():
        return "no WORDS - the program's budget is set only with the GM's own words"
    table = load(root)
    before = dict(table["program"])
    table["program"] = {"ops_at_40": ops_at_40, "exponent": exponent}
    save(root, table)
    log(root, {"what": "program", "from": before, "to": table["program"], "words": words})
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="budget_change.py")
    ap.add_argument("--root", default=str(ROOT))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set")
    for a in ("phase", "per_thing", "exponent", "derivation", "verdict"):
        s.add_argument(a)
    for h in ITEM_SIZES:
        s.add_argument(f"--items-at-{h}", type=int)
    c = sub.add_parser("change")
    c.add_argument("phase")
    c.add_argument("to", type=float)
    c.add_argument("--exponent", type=float)
    c.add_argument("--words", default="")
    for h in ITEM_SIZES:
        c.add_argument(f"--items-at-{h}", type=int)
    p = sub.add_parser("program")
    p.add_argument("ops_at_40", type=int)
    p.add_argument("exponent", type=float)
    p.add_argument("--words", default="")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if args.cmd == "set":
        items = {h: getattr(args, f"items_at_{h}") for h in ITEM_SIZES if getattr(args, f"items_at_{h}") is not None}
        why = set_budget(root, args.phase, float(args.per_thing), float(args.exponent), args.derivation, args.verdict, items)
        done = f"`{args.phase}` budgeted at {args.per_thing} per thing, exponent {args.exponent}"
    elif args.cmd == "change":
        items = {h: getattr(args, f"items_at_{h}") for h in ITEM_SIZES if getattr(args, f"items_at_{h}") is not None}
        why = change_budget(root, args.phase, args.to, args.exponent, args.words, items)
        done = f"`{args.phase}` changed to {args.to} per thing, logged in {LOG} with the GM's words"
    else:
        why = set_program(root, args.ops_at_40, args.exponent, args.words)
        done = f"the program's budget set to {args.ops_at_40} operations at 40 households, exponent {args.exponent}, logged in {LOG}"
    print(f"budget-{args.cmd}: {why or done}", file=sys.stderr if why else sys.stdout)
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())

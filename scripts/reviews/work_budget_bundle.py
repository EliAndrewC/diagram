#!/usr/bin/env python3
"""`make work-budget-bundle MODE=budget|audit PHASE=<stage> [DERIVATION=<file>]` - the `work-budget` agent's bundle (feature 443
T05, plan D10; FR-008).

MODE BUDGET judges a stage's derivation BEFORE its rebuild, blind to today's code and counts so today's waste cannot anchor the
target (the design the GM approved, 2026-10-28, section 4). The bundle holds the derivation, the stage's contract (its
`## Contract` section: the manifest keys it reads and writes) and the rubric, and REFUSES a derivation holding a fenced block of
Python, a path under `l7r/` or a figure tagged as a current count (`calls` or `ops` beside a number) - each would put today's
code or its numbers in front of the judge.

MODE AUDIT judges the landed code against its counters: the stage's modules (the file defining `stage_<name>`, and the files under
the stage's own package), the newest `make work-budget` run's counts for the stage at each size by kind and by function, its
call chains (the stage's section of the newest kept `make perf-fanout` report, `dev/perf-log/*-fanout-*.txt`) and its budget
(`dev/work-budget.json`, or `BUDGET=<file>` - the funnel fixture's, FR-009).

Written to `/tmp/l7r-check/work-budget-<mode>-<stage>/`, a `MANIFEST.md` naming each file. The agent's first line is its verdict;
save it as `verdict.txt` beside the derivation, and write its ledger row (`make ledger-owed`).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path("/tmp/l7r-check")
RUBRIC = "docs/work-budget-rubric.md"
TABLE = "dev/work-budget.json"
RUNS = "dev/work-budget"
FANOUT = "dev/perf-log"
HAMLET = "l7r/diagram/hamletgen"

#: what a MODE BUDGET derivation may not hold, each with why (D10)
FORBIDDEN = (
    (re.compile(r"^```\s*py(?:thon)?\b", re.M | re.I), "a fenced block of Python - today's code"),
    (re.compile(r"(?<![\w/])l7r/[\w./-]+"), "a path under l7r/ - today's code"),
    (re.compile(r"\b\d[\d,.]*\s*(?:[kKmM]\s*)?(?:calls|ops)\b|\b(?:calls|ops)\s*[:=]?\s*\d", re.I), "a figure tagged as a current count (calls or ops beside a number)"),
)
CONTRACT = re.compile(r"^## Contract\b.*?(?=^## |\Z)", re.M | re.S)


#: the derivation's FORM (feature 443 T13; the GM 2026-10-28: being careful means the checklist says what careful is) - each a field
#: an error of T05's grid fixture would have been refused at: round 2's "per disc" bound that held only over the run (SCOPE), round
#: 3's incremental update never considered (the ALTERNATIVES) and its "once" term with no bound (WORST CASE)
COUNT = re.compile(r"^## The count, factor by factor\b(.*?)(?=^## |\Z)", re.M | re.S)
ALTERNATIVES = re.compile(r"^## Cheaper algorithms considered\b(.*?)(?=^## |\Z)", re.M | re.S)
COLUMNS = ("factor", "scope", "value", "reason", "worst case")
SCOPES = ("per item", "over the run", "once")
STANDARD = ("sweep", "grid or spatial index", "priority queue", "incremental update", "memoizing what a scan does not change")
TEMPLATE = ".specify/templates/derivation.md"


TOTALS = re.compile(r"^## Totals\b(.*?)(?=^## |\Z)", re.M | re.S)
TOTAL_SIZES = (20, 40, 80)
_TOTAL = re.compile(r"^-\s*at\s+(\d+)\s*:\s*(.+?)\s*=\s*([\d,]+(?:\.\d+)?)\s*$", re.M)
_EXPR = re.compile(r"^[\d\s.,+\-*/x()]+$")
_AT = re.compile(r"([\d,]+(?:\.\d+)?)\s+at\s+(\d+)")
_NUM = re.compile(r"^\s*(?:at most\s+|about\s+)?([\d,]+(?:\.\d+)?)\b")


def row_values(text: str) -> dict[str, dict[int, str]]:
    """Each count row's figure at each size: `N at S` pairs where the value cell gives them, else its one leading number at every
    size; a row whose value is neither has no figure (and is refused by `total_problems`)."""
    count = COUNT.search(text)
    out: dict[str, dict[int, str]] = {}
    for ln in (count.group(1) if count else "").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not ln.strip().startswith("|") or len(cells) != len(COLUMNS) or cells[0].lower() in ("factor",) or set(cells[0]) <= set("-"):
            continue
        pairs = {int(sz): n for n, sz in _AT.findall(cells[2])}
        one = _NUM.match(cells[2])
        out[cells[0]] = {h: pairs.get(h, one.group(1) if one and not pairs else "") for h in TOTAL_SIZES}
    return out


def _arith(node: ast.AST) -> float:
    """The value of an expression of numbers and + - * / alone (the `_EXPR` match has kept everything else out)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_arith(node.operand)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add | ast.Sub | ast.Mult | ast.Div):
        a, b = _arith(node.left), _arith(node.right)
        return a + b if isinstance(node.op, ast.Add) else a - b if isinstance(node.op, ast.Sub) else a * b if isinstance(node.op, ast.Mult) else a / b
    raise ValueError(ast.dump(node))


def total_problems(text: str) -> list[str]:
    """The `## Totals` section's lines - `- at <size>: <expression> = <value>`, one per size - each evaluated EXACTLY, to the
    integer (feature 444 T07: a sum written wrong refused before any dispatch), and each holding every count row's figure at that
    size (a total leaving out a term refused); a row with no figure at a size is refused too, so nothing escapes the expression."""
    sec = TOTALS.search(text)
    if sec is None:
        return [f"a `## Totals` section: one line per size, `- at <{'|'.join(str(h) for h in TOTAL_SIZES)}>: <expression> = <value>`"]
    found = {int(m.group(1)): (m.group(2), m.group(3)) for m in _TOTAL.finditer(sec.group(1))}
    out = [f"`## Totals`: a line for {h} households" for h in TOTAL_SIZES if h not in found]
    rows = row_values(text)
    for h, (expr, value) in sorted(found.items()):
        if not _EXPR.match(expr):
            out.append(f"`## Totals` at {h}: `{expr}` is not arithmetic on the table's figures (digits, + - x / and brackets)")
            continue
        got = _arith(ast.parse(expr.replace(",", "").replace("x", "*"), mode="eval").body)
        if round(got) != round(float(value.replace(",", ""))):
            out.append(f"`## Totals` at {h}: `{expr}` is {round(got):,}, not {value}")
        # ...EACH ROW ITS OWN TERM (the round arbiter's note on ask:444-T07-plan-round-3): two rows sharing a figure owe it twice, so the
        # expression's numbers are counted, and each row takes one of its own
        tokens = Counter(t.replace(",", "") for t in re.findall(r"[\d,]+(?:\.\d+)?", expr))
        for name, at in rows.items():
            if not at[h]:
                out.append(f"`{name}`: no figure at {h} households - write its value as `N at 20, N at 40, N at 80`, or one number for every size")
            elif tokens[at[h].replace(",", "")] > 0:
                tokens[at[h].replace(",", "")] -= 1
            else:
                out.append(f"`## Totals` at {h}: `{name}`'s figure {at[h]} is not in the expression - every row of the count is a term of the total")
    return out


def cells_problems(text: str) -> list[str]:
    """A derivation that uses a grid or spatial index counts the cells it examines (the rubric: an index cell examined is a basic
    operation; feature 444 T07)."""
    alts = ALTERNATIVES.search(text)
    used = bool(alts and re.search(r"^-\s*grid or spatial index:\s*used\b", alts.group(1), re.M | re.I))
    count = COUNT.search(text)
    rows = [ln.strip().strip("|").split("|")[0].strip().lower() for ln in (count.group(1) if count else "").splitlines() if ln.strip().startswith("|")]
    if used and not any("cell" in r for r in rows[2:]):
        return ["`## The count, factor by factor`: a row counting the index cells examined - the derivation says a grid or spatial index is used"]
    return []


def form_problems(text: str) -> list[str]:
    """Each field of the derivation template a derivation lacks (`TEMPLATE`): the count's table with every column filled and a
    scope of its three, and a line for each standard cheaper algorithm saying whether it is used and why."""
    out: list[str] = []
    contract = CONTRACT.search(text)
    lines = {m.group(1).lower(): m.group(2).strip() for m in re.finditer(r"^-\s*(Reads|Writes|Keeps):[ \t]*(.*)$", contract.group(0) if contract else "", re.M)}
    # ...THE CONTRACT'S FOUR PARTS (feature 444 T01, the design's checklist box 1): what it reads, what it writes, and what it keeps -
    # the cohort properties and the research claims, each a rule asked of a candidate before it is placed, so each a check of the count
    out += [f"`## Contract`: its `{k}:` line, filled" for k in ("Reads", "Writes", "Keeps") if not lines.get(k.lower()) or lines[k.lower()].startswith("<")]
    count = COUNT.search(text)
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in (count.group(1) if count else "").splitlines() if ln.strip().startswith("|")]
    if not rows or tuple(c.lower() for c in rows[0]) != COLUMNS:
        out.append(f"the `## The count, factor by factor` table with the columns {' | '.join(COLUMNS)}")
    else:
        for r in rows[2:]:
            name = r[0] or "a factor"
            if len(r) != len(COLUMNS) or any(not c or c.startswith("<") for c in r):
                out.append(f"`{name}`: every column filled (scope, value, reason, worst case)")
            elif r[1].lower() not in SCOPES:
                out.append(f"`{name}`: its scope is one of {', '.join(SCOPES)} - not `{r[1]}`")
        if len(rows) < 3:
            out.append("a row for each factor of the count")
    alts = ALTERNATIVES.search(text)
    said = {m.group(1).strip().lower(): m.group(2).strip() for m in re.finditer(r"^-\s*([^:\n]+):[ \t]*(.*)$", alts.group(1) if alts else "", re.M)}
    out += [f"`## Cheaper algorithms considered`: a line for `{a}` - used, or why not" for a in STANDARD if not said.get(a)]
    return out + cells_problems(text) + total_problems(text)


def refusals(text: str) -> list[str]:
    """Why a derivation may not go to MODE BUDGET: each forbidden thing it holds, with its first match."""
    return [f"{why}: `{m.group(0).strip()[:60]}`" for pat, why in FORBIDDEN if (m := pat.search(text))]


def budget_bundle(root: Path, phase: str, derivation: str, out: Path) -> tuple[int, str]:
    src = root / derivation
    if not src.is_file():
        return 2, f"work-budget-bundle: no derivation at {derivation}"
    text = src.read_text(encoding="utf-8")
    if bad := refusals(text):
        return 1, "work-budget-bundle: REFUSED - a MODE BUDGET bundle holds no code and no counts of today's code:\n" + "\n".join(f"  {b}" for b in bad)
    contract = CONTRACT.search(text)
    if contract is None:
        return 1, "work-budget-bundle: REFUSED - the derivation has no `## Contract` section (what the stage reads and writes)"
    if short := form_problems(text):
        return 1, f"work-budget-bundle: REFUSED - the derivation is short of the template's fields ({TEMPLATE}):\n" + "\n".join(f"  {b}" for b in short)
    out.mkdir(parents=True, exist_ok=True)
    (out / "derivation.md").write_text(text, encoding="utf-8")
    (out / "contract.md").write_text(contract.group(0), encoding="utf-8")
    shutil.copy(root / RUBRIC, out / "rubric.md")
    (out / "MANIFEST.md").write_text(
        f"# work-budget MODE BUDGET - {phase}\n\n"
        "MODE BUDGET: judge the derivation before the rebuild. Read, beside this file:\n\n"
        "- `rubric.md` - the standards S1-S7 and the worked homestead reference;\n"
        "- `contract.md` - what the stage reads and writes;\n"
        "- `derivation.md` - the pseudocode and the operation count, factor by factor.\n\n"
        "The first line of your reply is the verdict: SOUND, LOOSE or UNDERIVED.\n",
        encoding="utf-8",
    )
    return 0, str(out / "MANIFEST.md")


def stage_files(root: Path, phase: str) -> list[Path]:
    """The file defining `stage_<phase>` under the hamlet package, and, when that file is in a subpackage, its siblings."""
    pat = re.compile(rf"^def stage_{re.escape(phase)}\(", re.M)
    found = [p for p in sorted((root / HAMLET).rglob("*.py")) if pat.search(p.read_text(encoding="utf-8"))]
    if not found:
        return []
    home = found[0].parent
    return sorted(home.glob("*.py")) if home != root / HAMLET else found


def fanout_section(root: Path, phase: str) -> str:
    """The stage's section of the newest kept `make perf-fanout` report, or why there is none."""
    reports = sorted((root / FANOUT).glob("*-fanout-*.txt"))
    if not reports:
        return f"no `make perf-fanout` report is kept: run `make perf-fanout STAGES={phase}`\n"
    text = reports[-1].read_text(encoding="utf-8")
    m = re.search(rf"^{re.escape(phase)}: .*?(?=^[a-z_]+: |\Z)", text, re.M | re.S)  # a stage's section opens `<stage>: ` at column 0
    return f"from {reports[-1].relative_to(root)}\n\n" + (m.group(0) if m else f"(the report has no section for {phase})\n")


def audit_bundle(root: Path, phase: str, out: Path, budget: str = "") -> tuple[int, str]:
    files = stage_files(root, phase)
    if not files:
        return 2, f"work-budget-bundle: no `stage_{phase}` under {HAMLET}"
    runs = sorted((root / RUNS).glob("*.json"))
    if not runs:
        return 2, "work-budget-bundle: no `make work-budget` run is recorded - run it first"
    run = json.loads(runs[-1].read_text(encoding="utf-8"))
    counts = [{"seed": r["seed"], "households": r["households"], **r["stages"][phase]} for r in run["rows"] if phase in r["stages"]]
    table = json.loads((root / TABLE).read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "code").mkdir(exist_ok=True)
    for p in files:
        shutil.copy(p, out / "code" / p.name)
    (out / "counts.json").write_text(json.dumps({"run": runs[-1].name, "summary": run["summary"]["stages"].get(phase), "rolls": counts}, indent=1), encoding="utf-8")
    (out / "chains.txt").write_text(fanout_section(root, phase), encoding="utf-8")
    pinned = json.loads((root / budget).read_text(encoding="utf-8")) if budget else table["stages"].get(phase)
    (out / "budget.json").write_text(json.dumps(pinned, indent=1), encoding="utf-8")
    shutil.copy(root / RUBRIC, out / "rubric.md")
    (out / "MANIFEST.md").write_text(
        f"# work-budget MODE AUDIT - {phase}\n\n"
        "MODE AUDIT: judge the landed code against its counters. Read, beside this file:\n\n"
        "- `rubric.md` - the standards S1-S7;\n"
        f"- `code/` - the stage's modules: {', '.join(p.name for p in files)};\n"
        "- `counts.json` - the newest run's counted operations for the stage at each size, by kind and by function;\n"
        "- `chains.txt` - the callers above each counted function;\n"
        "- `budget.json` - the stage's pinned budget.\n\n"
        "The first line of your reply is the verdict: WITHIN, OVER or UNCOUNTED.\n",
        encoding="utf-8",
    )
    return 0, str(out / "MANIFEST.md")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="work_budget_bundle.py")
    ap.add_argument("mode", choices=("budget", "audit"))
    ap.add_argument("phase")
    ap.add_argument("--derivation", default="")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default="")
    ap.add_argument("--budget", default="", help="MODE=audit: a budget file in place of the table's (the fixture's, FR-009)")
    a = ap.parse_args(argv)
    if not a.phase:
        print("work-budget-bundle: PHASE= is required", file=sys.stderr)
        return 2
    root = Path(a.root)
    out = Path(a.out) if a.out else OUT / f"work-budget-{a.mode}-{a.phase}"
    if out.exists():
        shutil.rmtree(out)
    if a.mode == "budget":
        if not a.derivation:
            print("work-budget-bundle: MODE=budget needs DERIVATION=<file>", file=sys.stderr)
            return 2
        rc, msg = budget_bundle(root, a.phase, a.derivation, out)
    else:
        rc, msg = audit_bundle(root, a.phase, out, a.budget)
    print(msg, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())

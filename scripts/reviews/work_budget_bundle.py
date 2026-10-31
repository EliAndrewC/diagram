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
RUST = "rust"  # the rebuilt phases' crates (feature 444 FR-010)

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
#: the sizes a derivation's totals may be given at: the standard three, or - for a stage whose form exists only over a BOUNDED n
#: (rubric S6), stated in its Contract's Bounds as `a bounded n: households 10-20` - those of these within it, at least two (the
#: round arbiter's ruling on ask:444-polder-sizes: a polder exists at 10-20 households alone, 0019)
ANY_SIZES = (10, 20, 40, 80)
_BOUNDED = re.compile(r"bounded n[^.;\n]*?households\s+(\d+)\s*(?:-|to)\s*(\d+)", re.I)


def sizes(text: str) -> tuple[int, ...]:
    """The household sizes this derivation's totals are owed at: its bounded n's, else the standard three."""
    m = _BOUNDED.search(text)
    if not m:
        return TOTAL_SIZES
    lo, hi = int(m.group(1)), int(m.group(2))
    within = tuple(h for h in ANY_SIZES if lo <= h <= hi)
    return within if len(within) >= 2 else TOTAL_SIZES
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
        out[cells[0]] = {h: pairs.get(h, one.group(1) if one and not pairs else "") for h in sizes(text)}
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
        return [f"a `## Totals` section: one line per size, `- at <{'|'.join(str(h) for h in sizes(text))}>: <expression> = <value>`"]
    found = {int(m.group(1)): (m.group(2), m.group(3)) for m in _TOTAL.finditer(sec.group(1))}
    out = [f"`## Totals`: a line for {h} households" for h in sizes(text) if h not in found]
    rows = row_values(text)
    for h, (expr, value) in sorted((h, v) for h, v in found.items() if h in sizes(text)):  # a size past a bounded n is owed nothing
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
                out.append(f"`{name}`: no figure at {h} households - write its value as `N at <size>` for each of {', '.join(str(s) for s in sizes(text))}, or one number for every size")
            elif tokens[at[h].replace(",", "")] > 0:
                tokens[at[h].replace(",", "")] -= 1
            else:
                out.append(f"`## Totals` at {h}: `{name}`'s figure {at[h]} is not in the expression - every row of the count is a term of the total")
    return out


REFERENCE_PER_THING = 4000  # the rubric's reference, a few thousand basic operations a house (request.md; a GUESS)
_REASON = re.compile(r"^-\s*reason above the reference:\s*\S", re.M | re.I)
_PRUNING = re.compile(r"^-\s*pruning:\s*\S", re.M | re.I)  # rubric S9 (the GM 2026-10-29, the notice board's 8,730 operations)


def reference_problems(text: str) -> list[str]:
    """THE REFERENCE ASKS A REASON (feature 444 FR-014, rubric S8; the GM 2026-10-28: "I thought the idea was to REDUCE the number of
    operations. Why would we be targeting something HIGHER?"): a derivation whose total at 40 over its items at 40 passes the
    reference's 4,000 a thing names why, `- reason above the reference: <why>`, and the bound that stops its search early or why none
    can, `- pruning: <why>` (rubric S9: the GM 2026-10-29, "Why do we think it should take 8,730-11,277 operations to place a single
    notice board?!" - "the stage is one thing" had passed as the reason); under it, nothing is asked. The agent judges the words.
    It refuses nothing a reason answers - the band is a GUESS worked for the homesteads."""
    items = row_values(text).get("items", {}).get(40, "")
    sec = TOTALS.search(text)
    total = next((m.group(3) for m in _TOTAL.finditer(sec.group(1)) if int(m.group(1)) == 40), "") if sec else ""
    try:
        per = float(total.replace(",", "")) / float(items.replace(",", ""))
    except (ValueError, ZeroDivisionError):
        return []
    if per <= REFERENCE_PER_THING:
        return []
    out = []
    if not _REASON.search(text):
        out.append(
            f"the cost per thing at 40, {per:,.0f} ({total} over {items} items), passes the reference's {REFERENCE_PER_THING:,} (rubric S8) - count the"
            " typical case, or name why: `- reason above the reference: <why>`"
        )
    if not _PRUNING.search(text):
        out.append(
            f"the cost per thing at 40, {per:,.0f}, passes the reference's {REFERENCE_PER_THING:,} - name the bound that stops the search before it"
            " visits the whole set, or why none can (rubric S9): `- pruning: <the bound, or why none applies>`"
        )
    return out


INDEXES = re.compile(r"^## Indexes\b(.*?)(?=^## |\Z)", re.M | re.S)
_INDEX = re.compile(r"^-\s*([^:\n]+):\s*(.*)$", re.M)
_CELL_FT = re.compile(r"\bcells?\s+(?:of\s+)?[\d,.]+\s*ft\b", re.I)
_SIDE = re.compile(r"\bside\b[^.]*?[\d,.]+\s*ft\b", re.I)
_PX = re.compile(r"(?<![\w.])[\d,.]+\s*px\b")
_PX_FT = re.compile(r"^[^.;\n]{0,40}?[\d,.]+\s*ft\b")


def index_problems(text: str) -> list[str]:
    """EVERY INDEX ITS OWN ROW (the round arbiter's tooling fix on ask:444-T02-water-round-6: T07's check held once a derivation, so
    one cells row passed while each index a rewrite added went unchecked - field round 5, pond_bank round 3): a derivation that uses a
    grid or spatial index lists each in `## Indexes` - its cell size in ft and its densest case from a smallest SIDE in ft, never an
    area - and counts each in a row of its own, the row's factor naming the index and its cells; and every px figure carries its ft."""
    out: list[str] = []
    alts = ALTERNATIVES.search(text)
    used = bool(alts and re.search(r"^-\s*grid or spatial index:\s*used\b", alts.group(1), re.M | re.I))
    sec = INDEXES.search(text)
    entries = [(m.group(1).strip(), m.group(2)) for m in _INDEX.finditer(sec.group(1))] if sec else []
    if used and not entries:
        out.append("an `## Indexes` section: one line per index the derivation uses - `- <name>: cells of <N> ft; densest <count>, from a smallest side of <S> ft`")
    count = COUNT.search(text)
    rows = [ln.strip().strip("|").split("|")[0].strip().lower() for ln in (count.group(1) if count else "").splitlines() if ln.strip().startswith("|")][2:]
    for name, line in entries:
        if not _CELL_FT.search(line):
            out.append(f"`## Indexes` - {name}: its cell size in ft (`cells of <N> ft`)")
        if not _SIDE.search(line):
            out.append(f"`## Indexes` - {name}: its densest case from a smallest side in ft, never an area")
        if not any(name.lower() in r and "cell" in r for r in rows):
            out.append(f"`## The count, factor by factor`: a row counting {name}'s cells - its factor naming `{name}` and its cells")
    for m in _PX.finditer(text):
        if not _PX_FT.match(text[m.end():].lstrip(" (")):
            out.append(f"`{m.group(0)}`: a px figure with no ft beside it - write its conversion, `{m.group(0)} (<N> ft)`")
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
    return out + cells_problems(text) + index_problems(text) + total_problems(text) + reference_problems(text)


_IDENT = re.compile(r"`([A-Za-z_][\w./]*)`|\b([A-Za-z]\w*_\w*|[A-Z][a-z0-9]+[A-Z]\w*)\b")  # a backticked dotted name or path splits
_KNOB = re.compile(r"Knob\(\s*\"([a-z0-9_]+)\"\s*,\s*\[([^\]]*)\]")


def _code_names(root: Path) -> tuple[set[str], set[str]]:
    """Today's names - every module and package, function, method, class, and module- or class-level name defined under `l7r/`
    (a local variable is not one) - and the names a derivation may still use:
    each knob's name and forms, each stage's name, and each key of the pool's hamlet manifests (their nested records' keys too)."""
    defined: set[str] = set()
    allowed: set[str] = set()
    for f in (root / "l7r").rglob("*.py"):
        src = f.read_text(encoding="utf-8")
        defined |= {f.stem, f.parent.name} - {"__init__"}
        allowed |= {n for m in _KNOB.finditer(src) for n in (m.group(1), *re.findall(r"\"([a-z0-9_]+)\"", m.group(2)))}
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        scopes = [tree.body] + [c.body for c in ast.walk(tree) if isinstance(c, ast.ClassDef)]  # module- and class-level names
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(n.name)
        for body in scopes:
            for n in body:
                targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AnnAssign) else []
                defined |= {x.id for x in targets if isinstance(x, ast.Name) and len(x.id) > 2}

    def keys(v: object) -> None:
        if isinstance(v, dict):
            allowed.update(k for k in v if isinstance(k, str))
            for w in v.values():
                keys(w)
        elif isinstance(v, list):
            for w in v[:50]:
                keys(w)

    budgets = root / "dev" / "work-budget.json"  # the budget units' names, the stages, stay a derivation's to use
    allowed |= set(json.loads(budgets.read_text(encoding="utf-8")).get("stages", {})) if budgets.is_file() else set()
    for f in (root / "pool" / "hamlets").glob("*/*.json"):
        try:
            keys(json.loads(f.read_text(encoding="utf-8")))
        except ValueError:
            continue
    return defined, allowed


def code_name_problems(root: Path, text: str) -> list[str]:
    """GREENFIELD (feature 444 FR-015; the GM 2026-10-29: "the ENTIRE point of what we're doing is to do a greenfield implementation
    unencumbered by the bad implementation chopices of our previous implementation"): a derivation names no module, function,
    method, class or module- or class-level name of today's code - 110 of them had carried today's design into 20 of the 23 derivations - other than a knob's name
    or form and a manifest key. A figure only today's code holds is a knob the derivation names as one, in its own words."""
    defined, allowed = _code_names(root)
    refs = [a or b for a, b in _IDENT.findall(text)]  # a document beside the derivation (`placer.py.txt`) is not a name of the code
    names = {w for r in refs if not re.search(r"\.(txt|md|json|html)$", r) for w in re.split(r"[./]", r) if w}
    found = sorted(names & defined - allowed)
    if not found:
        return []
    return [
        f"today's code's names ({len(found)}): {', '.join(found[:12])}{' ...' if len(found) > 12 else ''} - write the contract from the research"
        " and the reference manifests in your own words, a figure only the code holds as a knob you name (FR-015)"
    ]


def refusals(text: str) -> list[str]:
    """Why a derivation may not go to MODE BUDGET: each forbidden thing it holds, with its first match."""
    return [f"{why}: `{m.group(0).strip()[:60]}`" for pat, why in FORBIDDEN if (m := pat.search(text))]


ANSWERS = re.compile(r"^## Earlier findings\b(.*?)(?=^## |\Z)", re.M | re.S)
_ANSWER = re.compile(r"^-\s*verdict-(\d+),\s*finding\s+(\d+):\s*(fixed|disputed)\b\s*-\s*\S", re.M | re.I)


def findings_of(text: str) -> list[str]:
    """A recorded verdict's findings: its headline, then each `;`-separated item of its `(Also: ...)` note."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    also = re.search(r"\(Also:\s*(.*?)\)\s*$", text, re.S)
    return [lines[0]] + ([a.strip().rstrip(".") for a in also.group(1).split(";") if a.strip()] if also else [])


def answer_problems(src: Path, text: str) -> list[str]:
    """EVERY EARLIER FINDING ANSWERED (the round arbiter's tooling fix on ask:444-T02-field-round-8: a finding left open under one
    verdict's "Also" came back as the next verdict's headline): each finding of each earlier verdict recorded beside the derivation
    (`<stage>.verdict-<N>.txt`) has a line in `## Earlier findings`, `- verdict-<N>, finding <K>: fixed - ...` or `disputed - ...`."""
    stage = src.name.removesuffix(".derivation.md")
    have = {(int(m.group(1)), int(m.group(2))) for m in _ANSWER.finditer(sec.group(1))} if (sec := ANSWERS.search(text)) else set()
    out = []
    for v in sorted(src.parent.glob(f"{stage}.verdict-*.txt"), key=lambda p: int(re.sub(r"\D", "", p.name.rsplit("-", 1)[1]) or 0)):
        n = int(re.sub(r"\D", "", v.name.rsplit("-", 1)[1]))
        for k, f in enumerate(findings_of(v.read_text(encoding="utf-8")), 1):
            if (n, k) not in have:
                out.append(f"`## Earlier findings`: verdict-{n}, finding {k} unanswered - `- verdict-{n}, finding {k}: fixed - <how>` or `disputed - <why>` ({f[:80]})")
    return out


def budget_bundle(root: Path, phase: str, derivation: str, out: Path) -> tuple[int, str]:
    src = root / derivation
    if not src.is_file():
        return 2, f"work-budget-bundle: no derivation at {derivation}"
    text = src.read_text(encoding="utf-8")
    if bad := refusals(text) + code_name_problems(root, text):
        return 1, "work-budget-bundle: REFUSED - a MODE BUDGET bundle holds no code and no counts of today's code:\n" + "\n".join(f"  {b}" for b in bad)
    contract = CONTRACT.search(text)
    if contract is None:
        return 1, "work-budget-bundle: REFUSED - the derivation has no `## Contract` section (what the stage reads and writes)"
    if short := form_problems(text) + answer_problems(src, text):
        return 1, f"work-budget-bundle: REFUSED - the derivation is short of the template's fields ({TEMPLATE}):\n" + "\n".join(f"  {b}" for b in short)
    out.mkdir(parents=True, exist_ok=True)
    (out / "derivation.md").write_text(text, encoding="utf-8")
    (out / "contract.md").write_text(contract.group(0), encoding="utf-8")
    for v in sorted(src.parent.glob(f"{src.name.removesuffix('.derivation.md')}.verdict-*.txt")):  # the earlier verdicts, for the judge to confirm each closed
        shutil.copy(v, out / v.name)
    shutil.copy(root / RUBRIC, out / "rubric.md")
    (out / "MANIFEST.md").write_text(
        f"# work-budget MODE BUDGET - {phase}\n\n"
        "MODE BUDGET: judge the derivation before the rebuild. Read, beside this file:\n\n"
        "- `rubric.md` - the standards S1-S9 and the worked homestead reference;\n"
        "- `contract.md` - what the stage reads and writes;\n"
        "- `derivation.md` - the pseudocode and the operation count, factor by factor;\n"
        "- any `<stage>.verdict-<N>.txt` - the earlier verdicts; the derivation's `## Earlier findings` answers each - confirm each closed.\n\n"
        "The first line of your reply is the verdict: SOUND, LOOSE or UNDERIVED.\n",
        encoding="utf-8",
    )
    return 0, str(out / "MANIFEST.md")


def stage_files(root: Path, phase: str) -> list[Path]:
    """The file defining `stage_<phase>` under the hamlet package, and, when that file is in a subpackage, its siblings; and a
    Rust phase's source beside it (feature 444 T17, `dev/rust-tooling.md` "the work-budget audit bundle"): the `.rs` file under
    `rust/` defining `fn stage_<phase>`, with its siblings when it sits in a module directory of its own."""
    pat = re.compile(rf"^def stage_{re.escape(phase)}\(", re.M)
    found = [p for p in sorted((root / HAMLET).rglob("*.py")) if pat.search(p.read_text(encoding="utf-8"))]
    if not found:
        return []
    home = found[0].parent
    files = sorted(home.glob("*.py")) if home != root / HAMLET else found
    rs = re.compile(rf"^\s*(?:pub(?:\(crate\))?\s+)?fn\s+stage_{re.escape(phase)}\b", re.M)
    rust = [p for p in sorted((root / RUST).rglob("*.rs")) if rs.search(p.read_text(encoding="utf-8"))] if (root / RUST).is_dir() else []
    if rust:
        files += sorted(rust[0].parent.glob("*.rs")) if rust[0].parent.name != "src" else rust[:1]
    return files


def counted_files(root: Path, counts: list[dict]) -> list[Path]:
    """The modules under `l7r/` defining each function the stage's counters name (`<kind>@<function>`, a method's class dropped)
    - THE WORK IS AUDITED WHERE IT IS COUNTED (feature 444 T15's MODE AUDIT: the water frame's whole count sat in `plan.py`'s
    `_roll`, outside the stage's own module, so the audit could not see whether `plan_site` left a loop uncounted)."""
    names = {k.split("@", 1)[1].rsplit(".", 1)[-1] for r in counts for k in (r.get("ops") or {}) if "@" in k}
    found: list[Path] = []
    for p in sorted((root / "l7r").rglob("*.py")):
        text = p.read_text(encoding="utf-8")
        if any(re.search(rf"^\s*def {re.escape(n)}\(", text, re.M) for n in names):
            found.append(p)
    # ...AND IN THE RUST PHASES (feature 444 T19): a counter a Rust function keeps names it as a Python one does, and its `.rs`
    # file rides in the bundle beside the Python
    for p in sorted((root / RUST).rglob("*.rs")) if (root / RUST).is_dir() else []:
        if "target" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        if any(re.search(rf"^\s*(?:pub(?:\(crate\))?\s+)?fn {re.escape(n)}\b", text, re.M) for n in names):
            found.append(p)
    return found


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
    files = files + [p for p in counted_files(root, counts) if p not in files]
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
        "- `rubric.md` - the standards S1-S9;\n"
        f"- `code/` - the stage's modules and every module defining a function its counters name: {', '.join(p.name for p in files)};\n"
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

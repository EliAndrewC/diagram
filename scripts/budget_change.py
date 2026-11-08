#!/usr/bin/env python3
"""`scripts/budget_change.py` - the one writer of `dev/work-budget.json`, the hamlet roll's work budgets (feature 443 T03, plan D6).

THE TABLE: `{"program": {"ops_at_40": <ops>|null, "exponent": <e>|null}, "stages": {"<stage>": {...}}}`, one stage per entry of
`hamletgen.driver.STAGES` (named as `make work-budget` names them, `stage_` dropped). A stage is `unbudgeted`; `budgeted`, with
`per_thing` (basic operations per thing placed), `exponent` (its growth with households), `derivation` (the path of its
first-principles derivation) and `verdict` (the path of its `work-budget` MODE BUDGET verdict, whose first line is the verdict
word - T05's agent writes it so); or `accepted`, which adds `accepted` (its counted operations at 40 and 80 households - T04).

THE RULES (443 FR-005; the GM's approval of the design, 2026-10-28): a FIRST budget is set only from a SOUND verdict (`budget-set`;
LOOSE or UNDERIVED refuses); every later change, and the program's whole-roll budget, needs the GM's words (`budget-change`,
`budget-program`, WORDS checked against the session's transcript by `rust/guard/src/guards/budget_change_hooks.rs`, which a make target
cannot do), and is logged with them in `dev/work-budget-changes.jsonl`. The table is a guard file: an edit other than through
these targets needs `GUARD_EDIT_OK`.

    budget_change.py set PHASE PER_THING EXPONENT DERIVATION VERDICT [--reason WHY] [--lower]
    budget_change.py change PHASE TO [--exponent E] --words WORDS
    budget_change.py program OPS_AT_40 EXPONENT --words WORDS
    budget_change.py set ... --raise          (a re-derivation counting work the first missed, on its SOUND: feature 444 FR-022)
    budget_change.py accept PHASE AUDIT       (a rebuilt phase's MODE AUDIT WITHIN and its counts at 40 and 80 within budget, or
                                              LEEWAY and its counts at most twice it: feature 444 FR-022)

THE LEEWAY AND THE RAISE (feature 444 amendment 7, the GM 2026-11-03: "I would frankly be okay with things that are 50% higher or
even twice as high in terms of the number of operations than what we have budgeted ... if we end up with some kind of n squared
algorithm, then even in Rust that will become a problem"): a budget is an estimate, so a stage is accepted at up to `LEEWAY` times
it on the work-budget agent's LEEWAY, and a budget is raised without his words on a SOUND re-derivation that names the work the
first one missed, to at most `RAISE_CAP` times its first figure at 40; neither touches the growth caps.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import re
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
    """A stage's entry - or a FORM of one, `<stage>.<form>` (`field.polder`), budgeted at its own bounded n (the round arbiter's
    ruling on ask:444-polder-sizes), unbudgeted until its first pin."""
    st = table["stages"].get(phase)
    if st is None and "." in phase and phase.split(".", 1)[0] in table["stages"]:
        return {"status": "unbudgeted"}
    return st if st is not None else f"no stage `{phase}` in {TABLE} - the stages are: {', '.join(table['stages'])}"


def sizes_of(root: Path, derivation: str) -> tuple[int, ...]:
    """The sizes a derivation's budget is set at: its bounded n's (`work_budget_bundle.sizes`, the one reading), else 20, 40, 80."""
    sys.path.insert(0, str(Path(__file__).resolve().parent / "reviews"))
    import work_budget_bundle  # noqa: PLC0415

    path = root / derivation
    return work_budget_bundle.sizes(path.read_text(encoding="utf-8")) if path.is_file() else ITEM_SIZES


ITEM_SIZES = (20, 40, 80)  # feature 444 D2: a budget is per_thing x the derivation's own items at each size


def _stem(derivation: str) -> str:
    """The name a derivation's rounds run under: its file's name before `.derivation.md` (`web`, `web_greenfield`)."""
    return Path(derivation).name.removesuffix(".derivation.md")


def accepted_by(root: Path, derivation: str, phase: str, trigger: str) -> bool:
    """Does the round arbiter's log of the derivation's feature (`specs/<feature>/arbiter.jsonl`, beside its `phases/`) hold an ACCEPT
    at `trigger` naming `phase` - in its trigger or its instruction (feature 444 FR-013)? A greenfield derivation's rounds run under
    its own name (`<stage>_greenfield`, feature 444 FR-015), so an accept naming that names the stage too."""
    log = (root / derivation).parents[1] / "arbiter.jsonl"
    own = {phase, phase.split(".", 1)[1]} if "." in phase else {phase}  # a form (`field.polder`) answers to its own name (`polder`) too
    names = "|".join(re.escape(n) for n in own | ({_stem(derivation)} & {f"{n}_greenfield" for n in own}))  # its own greenfield name alone
    named = re.compile(rf"(?<![a-z_])(?:{names})(?![a-z_])")
    for line in log.read_text(encoding="utf-8").splitlines() if log.is_file() else []:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("trigger") == trigger and r.get("ruling") == "accept" and (named.search(trigger) or named.search(str(r.get("what", "")))):
            return True
    return False


def derivation_sha(root: Path, derivation: str) -> str:
    """The derivation's text as it was pinned: an accept-pinned budget is bound to it (feature 444 FR-013)."""
    return hashlib.sha256((root / derivation).read_bytes()).hexdigest()


RUNS = "dev/work-budget"  # `make work-budget`'s runs, `<stamp>-<code id>.json`, the newest last by name
REFERENCE_PER_HOUSE = 4000  # request.md: "a sensible design needs a few thousand basic operations per house" (2,000-4,000, a GUESS)


def today_at_40(root: Path, phase: str) -> float | None:
    """The stage's counted operations at 40 households in the newest `make work-budget` run, or None when no run counts it."""
    runs = sorted((root / RUNS).glob("*.json"))
    try:
        per = json.loads(runs[-1].read_text(encoding="utf-8"))["summary"]["stages"][phase]["per"]["40"]
        return float(per["ops"])
    except (IndexError, KeyError, TypeError, ValueError, OSError):
        return None


def budget_at(st: dict[str, Any], h: int) -> float:
    return float(st["per_thing"]) * float(st[f"items_at_{h}"])


def per_house(root: Path) -> str:
    """The program's sum at 40 households per household, against the design's reference - printed at every pin (ask:444-budget-standard)."""
    stages = load(root)["stages"].values()
    total = sum(budget_at(st, 40) for st in stages if st.get("status") != "unbudgeted" and st.get("items_at_40") is not None)  # a form at a bounded n holds no 40
    open_ = sum(1 for st in stages if st.get("status") == "unbudgeted")
    return (
        f"the program at 40 households: {total:,.0f} operations, {total / 40:,.0f} a household against the design's few thousand"
        f" ({REFERENCE_PER_HOUSE:,} at most, request.md){f'; {open_} stage(s) not yet budgeted' if open_ else ''}"
    )


def set_budget(
    root: Path,
    phase: str,
    per_thing: float,
    exponent: float,
    derivation: str,
    verdict: str,
    items: dict[int, int] | None = None,
    arbiter: str = "",
    spread: str = "",
    reason: str = "",
    lower: bool = False,
    growth_reason: str = "",
    raise_: bool = False,
    second: str = "",
) -> str:
    """A first budget, from a SOUND verdict or the round arbiter's accept of the derivation (feature 444 FR-013, the GM 2026-10-28):
    '' when set, else why not. `lower` re-pins a budgeted stage at no more than its standing budget at any size (no GM words: a
    lowering asks nothing of him, ask:444-budget-standard). A pin above the stage's counted operations at 40 in the newest `make
    work-budget` run is refused unless `reason` names why: a budget the stage already meets is no target (the GM 2026-10-28: "I
    thought the idea was to REDUCE the number of operations"); the count is read here, outside the bundle, so it anchors no
    derivation."""
    table = load(root)
    st = _stage(table, phase)
    if isinstance(st, str):
        return st
    if raise_ and lower:
        return "RAISE=1 and LOWER=1 together - a re-pin is one or the other"
    if raise_:
        if st["status"] != "budgeted":
            return f"`{phase}` is {st['status']} - RAISE=1 raises a budgeted stage, before its acceptance (feature 444 FR-022)"
        if not missed_work(root, derivation):
            return (
                f"{derivation} names no work its first derivation missed - a raise without the GM's words counts each item under"
                f" `{MISSED}` (feature 444 FR-022); a figure that is only an estimate off is the leeway's, at acceptance"
            )
    if st["status"] != "unbudgeted" and not (lower or raise_):
        return f"`{phase}` is {st['status']} already - a change needs the GM's words: make budget-change PHASE={phase} TO=<per thing> WORDS=\"<the GM's words>\"; a lowering re-pins with LOWER=1"
    if lower and st["status"] == "unbudgeted":
        return f"`{phase}` has no budget to lower - a first one is set without LOWER"
    if not (root / derivation).is_file():
        return f"no derivation at {derivation}"
    if arbiter:
        if not accepted_by(root, derivation, phase, arbiter):
            return f"the round arbiter's log holds no accept at {arbiter} naming `{phase}` - an accept pins a first budget only as the arbiter gave it (feature 444 FR-013)"
        if not re.fullmatch(r"[\d,]+-[\d,]+ at \d+", spread.strip()):
            return "an accept-pinned budget records its totals' spread across the rounds, for the program target: SPREAD=\"<low>-<high> at <households>\" (feature 444 FR-013)"
        got = SOUND
    else:
        got = verdict_of(root / verdict)
    if got != SOUND:
        return f"the verdict at {verdict} reads {got or 'nothing'}, not SOUND - a first budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}`)"
    sz = sizes_of(root, derivation)
    if missing := [h for h in sz if (items or {}).get(h) is None]:
        return f"no items at {', '.join(str(h) for h in missing)} households - a budget is per thing x the derivation's own items at each size: {' '.join(f'ITEMS_AT_{h}=' for h in sz)} (feature 444 D2)"
    new = {h: per_thing * (items or {})[h] for h in sz}
    if raise_:
        # ...AT THE DERIVATION'S TOP SIZE: 40 households, or a form's bounded n (`waterward.polder` at 10-20, feature 444 T29)
        top = 40 if 40 in sz else sz[-1]
        first = first_budget(st, top)
        if new.get(top, 0) <= budget_at(st, top):
            return f"`{phase}`'s re-derived budget at {top}, {new.get(top, 0):,.0f}, is no raise on {budget_at(st, top):,.0f} - a lowering re-pins with LOWER=1"
        if new[top] > RAISE_CAP * first:
            return (
                f"`{phase}`'s re-derived budget at {top}, {new[top]:,.0f}, is past {RAISE_CAP:g} times its first, {first:,.0f} - an order of magnitude"
                f" needs the GM's words (feature 444 FR-022): make budget-change PHASE={phase} TO=<per thing> DERIVATION= VERDICT= WORDS=\"<the GM's words>\""
            )
        # PAST TWICE THE FIRST, THE RIGOROUS ANALYSIS (FR-022 rule 2; the GM: "I don't want us to just think it's reasonable to have
        # things take an order of magnitude more operations than we estimated. Without extremely rigorous analysis"): a second
        # MODE BUDGET dispatch of the same bundle, blind to the first, judges it SOUND too
        if new[top] > LEEWAY * first and (not second or second == verdict or verdict_of(root / second) != SOUND):
            read = f" ({second} reads {verdict_of(root / second) or 'nothing'})" if second and second != verdict else ""
            return (
                f"`{phase}`'s re-derived budget at {top}, {new[top]:,.0f}, is {new[top] / first:.1f} times its first, {first:,.0f} - past {LEEWAY:g} times a raise"
                " needs a second SOUND, from an independent MODE BUDGET dispatch of the same bundle blind to the first: SECOND=<its verdict file>"
                f"{read}"
            )
    if lower and (raised := [h for h in sz if new[h] > budget_at(st, h)]):
        return (
            f"`{phase}` would rise at {', '.join(str(h) for h in raised)} households ({', '.join(f'{new[h]:,.0f} against {budget_at(st, h):,.0f}' for h in raised)})"
            f" - a raise needs the GM's words: make budget-change PHASE={phase} TO=<per thing> WORDS=\"<the GM's words>\""
        )
    # THE GROWTH CAP, HELD BY THE TOOL (the GM 2026-10-29: "if we allow polynomial growth but with a high exponent like n cubed on an
    # n which grows considerably with map size ... that is really going to not work in the long run"): S6's 1.15 was the work-budget
    # agent's judgment alone; a pin growing past it from 20 to 80 households names its reason, such as a bounded n
    if (g := growth(new[sz[0]], new[sz[-1]], sz[-1] / sz[0])) > GROWTH_CAP and not growth_reason.strip():
        return (
            f"`{phase}`'s budget grows at an exponent of {g:.2f} from 20 to 80 households, past rubric S6's {GROWTH_CAP} (n log n at most) -"
            " re-derive it, or name why its n is bounded: GROWTH_REASON=\"<why>\""
        )
    today = today_at_40(root, phase) if 40 in sz else None
    if today is not None and new[40] > today and not reason.strip() and not raise_:
        return (
            f"`{phase}`'s budget at 40 households, {new[40]:,.0f}, is above what the stage counts today, {today:,.0f} (the newest `make work-budget`"
            f" run) - a budget the stage already meets is no target (ask:444-budget-standard). Re-derive at the typical case, or name why:"
            f" REASON=\"<why this stage needs more than it does today>\""
        )
    table["stages"][phase] = {
        "status": "budgeted", "per_thing": per_thing, "exponent": exponent, "derivation": derivation, "verdict": arbiter or verdict,
        **{f"items_at_{h}": (items or {})[h] for h in sz},
        **({"sizes": list(sz)} if sz != ITEM_SIZES else {}),
        **(
            {
                "pinned_on": "accept",
                "derivation_sha": derivation_sha(root, derivation),
                "rounds": len(list((root / derivation).parent.glob(f"{_stem(derivation)}.verdict-*.txt"))),  # its recorded work-budget verdicts
                "spread": spread.strip(),
            }
            if arbiter
            else {}
        ),
        **({"reason": reason.strip()} if reason.strip() else {}),
        **({"growth_reason": growth_reason.strip()} if growth_reason.strip() else {}),
        **({"first": {str(h): first_budget(st, h) for h in sz}} if raise_ else {}),
        **({"second": second} if raise_ and second else {}),
    }
    save(root, table)
    if raise_:
        log(root, {"what": "raised", "phase": phase, "from": {h: budget_at(st, h) for h in sz}, "to": new, "verdict": verdict, "missed": missed_work(root, derivation)})
    if lower:
        log(root, {"what": "lowered", "phase": phase, "from": {h: budget_at(st, h) for h in sz}, "to": new, "verdict": arbiter or verdict})
    return ""


def change_budget(
    root: Path, phase: str, to: float, exponent: float | None, words: str, items: dict[int, int] | None = None, derivation: str = "", verdict: str = ""
) -> str:
    """A budgeted stage's figure changed with the GM's words, and logged: '' when done, else why not. With `derivation` and `verdict`,
    the stage is re-pointed at the derivation the raise comes from (feature 444 FR-015: a greenfield figure above its standing pin,
    raised on the GM's words, stands on its own derivation and SOUND verdict, no longer the one it replaces)."""
    if not words.strip():
        return "no WORDS - a budget changes only with the GM's own words"
    table = load(root)
    st = _stage(table, phase)
    if isinstance(st, str):
        return st
    if st["status"] == "unbudgeted":
        return f"`{phase}` has no budget yet - a first one is set from a SOUND verdict: make budget-set PHASE={phase} PER_THING= EXPONENT= DERIVATION= VERDICT="
    if bool(derivation) != bool(verdict):
        return "re-pointing a stage names both its DERIVATION= and its VERDICT="
    if derivation and not (root / derivation).is_file():
        return f"no derivation at {derivation}"
    if verdict and verdict_of(root / verdict) != SOUND:
        return f"{verdict} is no SOUND verdict - a stage is re-pointed only at a derivation its verdict judged SOUND"
    # ...and the item counts it moves, each named: a raise by items alone logged only the unchanged per-thing figure (444#3)
    moved = [f"items_at_{h}" for h in (items or {})]
    before = {"per_thing": st["per_thing"], "exponent": st["exponent"], **{k: st.get(k) for k in moved}}
    st["per_thing"] = to
    if exponent is not None:
        st["exponent"] = exponent
    for h, n in (items or {}).items():
        st[f"items_at_{h}"] = n
    if derivation:
        st.update(derivation=derivation, verdict=verdict)
        for k in ("pinned_on", "derivation_sha", "rounds", "spread"):
            st.pop(k, None)
    save(root, table)
    log(root, {"what": "stage", "phase": phase, "from": before, "to": {"per_thing": st["per_thing"], "exponent": st["exponent"], **{k: st[k] for k in moved}}, "words": words})
    return ""


LEEWAY = 2.0  # FR-022 rule 1: a stage accepted at up to twice its budget, on the MODE AUDIT's LEEWAY (the GM 2026-11-03: "even twice as high")
RAISE_CAP = 10.0  # FR-022 rule 2: a raise without the GM's words reaches at most ten times the first budget at 40 ("an order of magnitude")
MISSED = "## Work the first derivation missed"  # FR-022 rule 2: the section a raising re-derivation counts its missed items under


def first_budget(st: dict[str, Any], h: int) -> float:
    """The stage's budget at `h` households before its first raise (`first`, recorded at the raise), else its standing budget."""
    return float((st.get("first") or {}).get(str(h)) or budget_at(st, h))


def missed_work(root: Path, derivation: str) -> list[str]:
    """The items under the derivation's `MISSED` section - its `- ` lines up to the next heading - or [] when it has none."""
    try:
        text = (root / derivation).read_text(encoding="utf-8")
    except OSError:
        return []
    if MISSED not in text:
        return []
    body = re.split(r"\n## ", text.split(MISSED, 1)[1], maxsplit=1)[0]
    return [ln[2:].strip() for ln in body.splitlines() if ln.startswith("- ") and ln[2:].strip()]


GROWTH_CAP = 1.15  # rubric S6: a stage's exponent from 20 to 80 households, which allows n log n and no n squared
GROWTH_SLACK = 0.05  # an accepted stage's measured exponent may sit this far above its budget's: seed noise between two sizes


def growth(at20: float, at80: float, ratio: float = 4) -> float:
    """The exponent from 20 to 80 households of a figure at each (rubric S6) - or across a bounded n's sizes, `ratio` apart; 0 where
    either is 0."""
    return math.log(at80 / at20) / math.log(ratio) if at20 > 0 and at80 > 0 else 0.0


HELD = (40, 80)  # the sizes an accepted stage is held to (feature 443 T04; the push's ratchet, `work_budget.held`)


def accept_stage(root: Path, phase: str, audit: str, arbiter: str = "") -> str:
    """A rebuilt phase accepted (feature 444 FR-005, checklist boxes 6-8): its MODE AUDIT verdict WITHIN, and its counted operations at
    40 and 80 households in the newest `make work-budget` run at most its budget, recorded as `accepted` - the figures the push's
    ratchet then holds it to. '' when done, else why not.

    ...OR THE ROUND ARBITER'S ACCEPT IN ITS PLACE (`arbiter`, a trigger naming the phase in its log): feature 444 T16's sixth MODE AUDIT
    was made final for box 7, came back UNCOUNTED, and the arbiter accepted the cheaper rebuild that followed rather than owe a
    seventh (ask:444-T16-field-after-audit-6) - so `audit` is then the last audit, and every budget check below still holds."""
    table = load(root)
    st = _stage(table, phase)
    if isinstance(st, str):
        return st
    if st.get("status") not in ("budgeted", "accepted"):
        return f"`{phase}` has no budget to be accepted against"
    if arbiter:
        if not accepted_by(root, str(st.get("derivation") or ""), phase, arbiter):
            return f"the round arbiter's log holds no accept at {arbiter} naming `{phase}` - a phase is accepted on its MODE AUDIT's WITHIN or that accept"
    elif (word := verdict_of(root / audit)) not in ("WITHIN", "LEEWAY"):
        return f"{audit} reads {word or 'nothing'}, not WITHIN or LEEWAY - a phase is accepted on its MODE AUDIT's WITHIN, or LEEWAY at up to {LEEWAY:g} times its budget (`make work-budget-bundle MODE=audit PHASE={phase}`)"
    # A FORM AT ITS BOUNDED N (`waterward.polder`, feature 444 T29) is counted by its own audit's run, `make work-budget SPEC=`
    # (`<stamp>-<code id>-spec.json`), under its stage's name and at its own sizes; a stage, by the reference run alone - never a
    # form's, which rolls another form of the same stage
    form = "." in phase
    sizes = tuple(int(h) for h in st.get("sizes") or HELD) if form else HELD
    runs = sorted(r for r in (root / RUNS).glob("*.json") if r.name.endswith("-spec.json") == form)
    try:
        per = json.loads(runs[-1].read_text(encoding="utf-8"))["summary"]["stages"][phase.split(".", 1)[0] if form else phase]["per"]
    except (IndexError, KeyError, TypeError, ValueError, OSError):
        if form:
            return f"no `make work-budget SPEC=` run counts `{phase}` - run it with the form's spec at its sizes ({', '.join(map(str, sizes))}) first"
        return f"no `make work-budget` run counts `{phase}` - run `make work-budget` (all of 10,20,40,80) first"
    got: dict[str, float] = {}
    for h in sizes:
        row = per.get(str(h))
        if not row:
            return f"the newest run has no roll at {h} households for `{phase}` - run `make work-budget` at every size"
        ops, budget = float(row["ops"]), budget_at(st, h)
        # FR-022 rule 1: past the budget only on the audit's LEEWAY (the agent named the excess and judged it), never past twice it;
        # the arbiter's accept stands in for a WITHIN, never for a LEEWAY (FR-006: the arbiter accepts no phase over its budget)
        if ops > LEEWAY * budget or (ops > budget and (arbiter or verdict_of(root / audit) != "LEEWAY")):
            past = ops > LEEWAY * budget
            return (
                f"`{phase}`: {ops:,.0f} counted operations at {h} households, {ops / budget:.2f} times its budget {budget:,.0f}"
                + (f", past the leeway's {LEEWAY:g} times" if past else " - over it, a phase is accepted on the MODE AUDIT's LEEWAY")
                + " - rebuild it again, raise the budget on a SOUND re-derivation naming the work it missed (`make budget-set RAISE=1`, FR-022),"
                " or with the GM's words (`make budget-change`, FR-006)"
            )
        # FR-022 rule 2: raise and leeway together - within twice the FIRST budget on a raise judged by one SOUND, within ten
        # times it on one judged by two independent ones; past that, the GM's words
        cap = RAISE_CAP if st.get("second") else LEEWAY
        if st.get("first") and ops > cap * first_budget(st, h):
            return (
                f"`{phase}`: {ops:,.0f} counted operations at {h} households, past {cap:g} times its first budget {first_budget(st, h):,.0f}"
                + (" - an order of magnitude needs the GM's words (`make budget-change`, FR-022)" if st.get("second") else
                   " - past twice the first, its raise owes a second, independent SOUND (`make budget-set RAISE=1 SECOND=`) or the GM's words (FR-022)")
            )
        got[str(h)] = ops
    lo, hi = (sizes[0], sizes[-1]) if form else (20, 80)
    at_lo = float((per.get(str(lo)) or {}).get("ops", 0))
    if (g := growth(at_lo, got[str(hi)], hi / lo)) > (b := growth(budget_at(st, lo), budget_at(st, hi), hi / lo)) + GROWTH_SLACK:
        return (
            f"`{phase}` grows at an exponent of {g:.2f} from {lo} to {hi} households, past its budget's"
            f" {b:.2f} (rubric S6, FR-005) - rebuild it again, or raise the budget with the GM's words"
        )
    st.update(status="accepted", accepted=got, audit=audit, **({"accept": arbiter} if arbiter else {}))
    save(root, table)
    log(root, {"what": "accepted", "phase": phase, "accepted": got, "audit": audit, "run": runs[-1].name, **({"accept": arbiter} if arbiter else {})})
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
    s.add_argument("--arbiter", default="", help="the round arbiter's accept of the derivation, by its trigger (feature 444 FR-013)")
    s.add_argument("--spread", default="", help="with --arbiter: the totals' spread across the rounds, `<low>-<high> at <households>`")
    s.add_argument("--reason", default="", help="why a budget above the stage's count today at 40 is the target (ask:444-budget-standard)")
    s.add_argument("--lower", action="store_true", help="re-pin a budgeted stage at no more than its standing budget at any size")
    s.add_argument("--second", default="", help="with --raise past twice the first budget: the second, independent MODE BUDGET verdict (444 FR-022)")
    s.add_argument("--raise", dest="raise_", action="store_true", help="raise a budgeted stage on a SOUND re-derivation naming the work its first missed (444 FR-022)")
    s.add_argument("--growth-reason", default="", help="why a budget growing past rubric S6's 1.15 from 20 to 80 households has a bounded n")
    for h in (10, *ITEM_SIZES):  # 10: a form at a bounded n (ask:444-polder-sizes)
        s.add_argument(f"--items-at-{h}", type=int)
    c = sub.add_parser("change")
    c.add_argument("phase")
    c.add_argument("to", type=float)
    c.add_argument("--exponent", type=float)
    c.add_argument("--words", default="")
    c.add_argument("--derivation", default="", help="re-point the stage at the derivation the raise comes from (444 FR-015)")
    c.add_argument("--verdict", default="", help="with --derivation: its SOUND verdict")
    for h in ITEM_SIZES:
        c.add_argument(f"--items-at-{h}", type=int)
    p = sub.add_parser("program")
    p.add_argument("ops_at_40", type=int)
    p.add_argument("exponent", type=float)
    p.add_argument("--words", default="")
    a = sub.add_parser("accept")
    a.add_argument("phase")
    a.add_argument("audit")
    a.add_argument("--arbiter", default="")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if args.cmd == "set":
        items = {h: getattr(args, f"items_at_{h}") for h in (10, *ITEM_SIZES) if getattr(args, f"items_at_{h}") is not None}
        why = set_budget(
            root, args.phase, float(args.per_thing), float(args.exponent), args.derivation, args.verdict, items, args.arbiter, args.spread, args.reason, args.lower,
            args.growth_reason, args.raise_, args.second,
        )
        done = f"`{args.phase}` {'lowered to' if args.lower else 'raised to' if args.raise_ else 'budgeted at'} {args.per_thing} per thing, exponent {args.exponent}\nbudget-set: {per_house(root)}" if not why else ""
    elif args.cmd == "change":
        items = {h: getattr(args, f"items_at_{h}") for h in ITEM_SIZES if getattr(args, f"items_at_{h}") is not None}
        why = change_budget(root, args.phase, args.to, args.exponent, args.words, items, args.derivation, args.verdict)
        done = f"`{args.phase}` changed to {args.to} per thing, logged in {LOG} with the GM's words"
    elif args.cmd == "accept":
        why = accept_stage(root, args.phase, args.audit, args.arbiter)
        done = f"`{args.phase}` accepted at its counted operations at 40 and 80 households, logged in {LOG}"
    else:
        why = set_program(root, args.ops_at_40, args.exponent, args.words)
        done = f"the program's budget set to {args.ops_at_40} operations at 40 households, exponent {args.exponent}, logged in {LOG}"
    print(f"budget-{args.cmd}: {why or done}", file=sys.stderr if why else sys.stdout)
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())

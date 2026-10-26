#!/usr/bin/env python3
"""The GM's review after landing - `make gm-review`, `make gm-reviewed`, `make accept` (feature 375, FR-012, plan D12).

WHY (the GM, 2026-10-10): *"I tend to want things to land on main without needing my review. So that probably does suggest
either a post-feature thing or we allow things to land on main with that and only that category of box unticked. And then
just as we have a make target for our `make speckit-todo` we could have a separate target"*. So a feature lands with its
GM's review still open, and this lists, by feature, what waits on him:

- NEEDS YOUR DECISION - the QUESTIONS escalation-check kept (feature 432): a question is a `gm-review.jsonl` row of kind
  `question`, written OWED by the round arbiter's `for_gm` or a declined fix, and judged by `make gm-escalated` (KEEP holds
  it for the GM, CUT closes it with the reason). This is the ONE source of his decisions: 328's ranking (`audit/
  overrides.json`, edited by hand) no longer lists itself as one - its "Held behind" rows are listed as waiting on other work;
- OWED ESCALATION-CHECK - a question not yet judged: the session's, never the GM's;
- TO REVIEW - rows he may read and overturn: a finding accepted with a reason (`make accept`), a known drift (feature 430),
  and the rulings and fixes recorded before feature 432.

WHY ONE DOOR (the GM, 2026-10-26): *"right now I've basically concluded that I should just ignore it because it is almost purely
a distraction"* - feature 375 queued every round-arbiter ruling and fix (465 open rows, 443 of them not his; feature 432's
audit), and the residence question ruled held for him on 2026-10-12 never reached him: its override carried a `held` key and
this module read only a `flag` opening "Held".

A feature with a row of either kind carries ONE box, `- [ ] GM review (make gm-reviewed F=NNN) [lands-open]`, which this
adds; `make speckit-todo` reads such a feature `Done - GM review pending`; `make gm-reviewed F=NNN` marks its rows reviewed
and ticks the box, and `OVERTURN=<row> TO=<feature>` turns a ruling the GM overturns into an open row of that feature.
`ROW=<n>` marks that one row reviewed and leaves the rest waiting (the GM, 2026-10-19, of a declined fix another feature had
since built: *"since the declined fix is already built then please mark it as no longer waiting on me"* - before it, the
only ways to clear one row were to sign off the whole feature or to overturn the row into another).

A row the GM DISCUSSED with a session and agreed needs no more action is reviewed: the session runs `make gm-reviewed F=NNN
WORDS="<his words, verbatim>"` in that turn, and the words are kept on each row it marks (the GM, 2026-10-10: *"if we have a
discussion like the one we had and then we agree that it doesn't need any more action, then shouldn't that count as me
reviewing it"* - 370's one row sat pending after exactly that discussion).

    gm_review.py list                                   the held rows, and each feature's to-review rows counted
    gm_review.py list F                                 feature F's to-review rows, one line per reason
    gm_review.py explain [F [ROW]]                      what needs the GM; with F, each of its rows (or ROW) in full
    gm_review.py accept F FINDING REASON                a finding accepted with a reason: a to-review row
    gm_review.py reviewed F [ROW G]                     the GM has reviewed F's rows (GM_WORDS= in the environment: his words)
    gm_review.py reviewed-row F ROW                     the GM has reviewed row ROW of F alone
    gm_review.py question F TEXT SOURCE                 a question for the GM, owed escalation-check (feature 432)
    gm_review.py escalated F ROW KEEP|CUT REASON        escalation-check's verdict on question ROW of F
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import textwrap
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROWS = "gm-review.jsonl"
HELD = Path("specs/328-match-the-research/audit/overrides.json")


def box(d: Path) -> str:
    """The one GM-review box a feature carries, in the one form `speckit-todo.py --holding` honors."""
    return f"- [ ] GM review (make gm-reviewed F={int(d.name.split('-', 1)[0])}) [lands-open]"


def rows(d: Path) -> list[dict]:
    f = d / ROWS
    out = []
    for line in (f.read_text(encoding="utf-8").splitlines() if f.is_file() else []):
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def ensure_box(d: Path) -> bool:
    """Add the GM-review box to `tasks.md` when the feature has an open row and no box yet; True when added."""
    tasks = d / "tasks.md"
    if not tasks.is_file() or not any("reviewed" not in r for r in rows(d)):
        return False
    text = tasks.read_text(encoding="utf-8")
    ticked = box(d).replace("- [ ] ", "- [x] ")
    if ticked in text:  # ...a new row after the GM reviewed the rest reopens his box (feature 432: a question carried into
        tasks.write_text(text.replace(ticked, box(d)), encoding="utf-8")  # a closed feature must not sit behind a ticked box)
        return True
    if "GM review (make gm-reviewed" in text:
        return False
    tasks.write_text(text.rstrip("\n") + "\n" + box(d) + "\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n",
                     encoding="utf-8")
    return True


def held(root: Path, full: bool = False) -> list[str]:
    """The rows of 328's ranking held behind another row (`Held behind ...`), which wait on other work (`full`: the whole flag,
    and the fix it would make). A ranking row's own "Held" flag or `held` key is NOT a decision of the GM's: those come only
    from the questions escalation-check kept (feature 432, FR-004; `questions`)."""
    f = root / HELD
    data = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    # a row the ranking closed (`audit/waves.json`, the wave that closed it) waits on nothing, whatever its flag still says:
    # the tubs row stayed "Held behind" after 374's wave 115 closed it and the row it waited on (the GM, 2026-10-12)
    w = f.parent / "waves.json"
    closed = json.loads(w.read_text(encoding="utf-8")) if w.is_file() else {}
    data = {k: v for k, v in data.items() if k not in closed}
    return [f"{k}: {v.get('flag', '') if full else v.get('flag', '')[:160]}" + (f". The fix it would make: {v['fix']}." if full and v.get("fix") else "")
            for k, v in sorted(data.items()) if str(v.get("flag", "")).startswith("Held behind")]


QUESTION = "question"


def question(d: Path, text: str, source: str, now: str | None = None) -> int:
    """A question for the GM, written OWED escalation-check (feature 432, FR-002); returns its row number."""
    if len(text.split()) < 4:
        raise ValueError("a question for the GM is a sentence he can answer - four words or more")
    row = {"kind": QUESTION, "status": "owed", "question": text, "source": source, "utc": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    n = len(rows(d))
    with (d / ROWS).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    ensure_box(d)
    return n


def questions(root: Path, status: str) -> list[tuple[Path, int, dict]]:
    """Every open question of `status` (owed or kept), by feature and row."""
    return [(d, i, r) for d, o in open_rows(root) for i, r in o if r.get("kind") == QUESTION and r.get("status") == status]


def owed_in_delta(root: Path) -> list[str]:
    """The questions still owed escalation-check in the features this push changes (`specs/<f>/gm-review.jsonl` in the delta
    against `origin/main`, committed or not): a feature does not land with one unjudged (feature 432, FR-002)."""
    import subprocess  # noqa: PLC0415

    def names(*args: str) -> set[str]:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        return set(out.stdout.split()) if out.returncode == 0 else set()

    base = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", "origin/main"], capture_output=True, text=True).stdout.strip()
    paths = (names("diff", "--name-only", base) if base else set()) | names("ls-files", "--others", "--exclude-standard")
    feats = sorted({p.split("/")[1] for p in paths if p.startswith("specs/") and p.endswith("/" + ROWS)})
    return [f"{_num(root / 'specs' / f)}#{i}: {r.get('question', '')}" for f in feats for i, r in enumerate(rows(root / "specs" / f))
            if r.get("kind") == QUESTION and r.get("status") == "owed" and "reviewed" not in r]


def escalated(d: Path, row: int, verdict: str, reason: str, now: str | None = None) -> str:
    """`make gm-escalated`: escalation-check's verdict on an owed question. KEEP holds it for the GM (his decision, named in the
    session's final message - `escalation-hooks.sh`); CUT closes it, the reason kept on the row (feature 432, FR-002)."""
    rs = rows(d)
    if not 0 <= row < len(rs) or rs[row].get("kind") != QUESTION:
        raise ValueError(f"ROW={row} is no question of {d.name} - make gm-review lists the owed ones")
    if rs[row].get("status") != "owed":
        raise ValueError(f"ROW={row} of {d.name} is already {rs[row].get('status')}")
    if verdict not in ("KEEP", "CUT"):
        raise ValueError("VERDICT is KEEP or CUT, escalation-check's")
    if len(reason.split()) < 2:
        raise ValueError("REASON is escalation-check's, two words or more")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if verdict == "KEEP":
        rs[row] = {**rs[row], "status": "kept", "kept": when, "escalation": reason}
    else:
        rs[row] = {**rs[row], "status": "cut", "escalation": reason, "reviewed": when[:10]}
    (d / ROWS).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8")
    if verdict == "KEEP":
        return (f"question {row} of {d.name} KEPT - it is the GM's decision now: name it in this turn's final message as "
                f"\"{_num(d)}#{row}\" with the question")
    return f"question {row} of {d.name} CUT - closed, not the GM's: {reason}"


KINDS = {"arbiter": "arbiter rulings", "accepted": "findings accepted with a reason",
         "arbiter-fix-done": "tooling fixes the arbiter asked for, made",
         "arbiter-fix-declined": "tooling fixes the arbiter asked for, declined to the GM",
         "known-drift": "known drifts landed on their open fixing task (feature 430)"}
SHORT = {"arbiter": "rulings", "accepted": "accepted", "arbiter-fix-done": "fixes made", "arbiter-fix-declined": "fixes DECLINED", "known-drift": "known drifts"}


def _num(d: Path) -> int:
    return int(d.name.split("-", 1)[0])


def _fit(line: str, width: int) -> str:
    return line if len(line) <= width else line[: width - 3].rstrip() + "..."


def _subject(r: dict) -> tuple[str, str]:
    """A row's trigger as (check, subject): `round:modal-form|modal:sheet/kitchen@3` -> (`modal-form`, `sheet/kitchen`),
    `red-gate@<utc>` -> (`red-gate`, `<utc>`), a reversal -> its file's name; an accepted finding is its own subject."""
    t = str(r.get("trigger") or "")
    if not t:
        return "", str(r.get("finding", ""))
    m = re.fullmatch(r"round:([^|]+)\|[a-z]+:(.+?)(?:@\d+)?", t)
    if m:
        return m.group(1), m.group(2)
    m = re.fullmatch(r"([a-z-]+)[:@](.+?)", t)
    if m:
        return m.group(1), m.group(2).rsplit("/", 1)[-1] if m.group(1) == "reversal" else m.group(2)
    return "", t


def _ids(ids: list[int]) -> str:
    """Row numbers as runs: [0, 1, 2, 5] -> `0-2,5`."""
    runs: list[list[int]] = []
    for i in ids:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return ",".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def open_rows(root: Path) -> list[tuple[Path, list[tuple[int, dict]]]]:
    """Each feature with rows the GM has not reviewed, and those rows with their numbers (OVERTURN= takes the number)."""
    out = [(d, [(i, r) for i, r in enumerate(rows(d)) if "reviewed" not in r]) for d in sorted((root / "specs").glob("*/"))]
    return [(d, o) for d, o in out if o]


def _counts(o: list[tuple[int, dict]]) -> str:
    """`49 rulings (2 continue), 34 fixes made` - the feature's rows by kind; a ruling other than accept is counted by verdict."""
    parts = []
    for kind in sorted({r.get("kind", "") for _, r in o}, key=lambda k: list(KINDS).index(k) if k in KINDS else 99):
        of = [r for _, r in o if r.get("kind", "") == kind]
        verdicts = {}
        for r in of:
            verdicts[r.get("ruling", "")] = verdicts.get(r.get("ruling", ""), 0) + 1
        by = ", ".join(f"{n} {v}" for v, n in sorted(verdicts.items(), key=lambda x: -x[1]) if v != "accept") if kind == "arbiter" else ""
        parts.append(f"{len(of)} {SHORT.get(kind, kind)}" + (f" ({by})" if by else ""))
    return ", ".join(parts)


def _detail(d: Path, o: list[tuple[int, dict]], width: int) -> list[str]:
    """One feature's rows by kind; rows sharing one reason are one line naming every subject."""
    out = [f"{d.name}: {len(o)} row(s) - {_counts(o)}"]
    for kind in sorted({r.get("kind", "") for _, r in o}, key=lambda k: list(KINDS).index(k) if k in KINDS else 99):
        out += ["", f"  {KINDS.get(kind, kind)}"]
        groups: dict[tuple[str, str], list[tuple[int, dict]]] = {}
        for i, r in o:
            if r.get("kind", "") == kind:
                groups.setdefault((r.get("ruling", ""), r.get("why") or r.get("tooling_fix") or ""), []).append((i, r))
        for (verdict, why), g in groups.items():
            subjects = sorted({" ".join(x for x in _subject(r) if x) for _, r in g})
            head = f"    [{_ids([i for i, _ in g])}] " + (f"{verdict}: " if verdict else "")
            out.append(_fit(head + "; ".join(subjects), width))
            out += [_fit(f"        {why}", width)] if why else []
    return out


def listing(root: Path, feature: str = "", width: int = 0) -> str:
    width = width or max(80, shutil.get_terminal_size((140, 24)).columns)
    features = open_rows(root)
    if feature:
        d = _feature(root, feature)
        o = next((o for f, o in features if f == d), [])
        if not o:
            return f"gm-review: nothing of {d.name} waits on the GM\n"
        return "\n".join(_detail(d, o, width) + ["", f"  reviewed:     make gm-reviewed F={_num(d)}",
                                                 f"  overturn one: make gm-reviewed F={_num(d)} OVERTURN=<row> TO=<feature>"]) + "\n"
    hs = held(root)
    kept, owed = questions(root, "kept"), questions(root, "owed")
    features = [(d, [(i, r) for i, r in o if r.get("kind") != QUESTION]) for d, o in features]
    features = [(d, o) for d, o in features if o]
    if not hs and not features and not kept and not owed:
        return "gm-review: nothing waits on the GM\n"
    n = sum(len(o) for _, o in features)
    out = [f"GM REVIEW - {len(kept)} decision(s) for the GM, {len(owed)} question(s) owed escalation-check, {len(hs)} waiting on "
           f"other work, {n} landed row(s) to review in {len(features)} feature(s)", ""]
    for title, group in (("NEEDS YOUR DECISION - the questions escalation-check kept (feature 432)", kept),
                         ("OWED ESCALATION-CHECK - the session's, not the GM's: judge each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"", owed)):
        if group:
            out.append(title)
            out += [_fit(f"  * {_num(d)}#{i}: {r.get('question', '')}", width) for d, i, r in group]
            out.append("")
    if hs:
        out.append("WAITING ON OTHER WORK - held in the ranking behind another row, not on the GM")
        for h in hs:
            key, _, flag = h.partition(": ")
            out += [_fit(f"  * {key}", width), _fit(f"      {re.sub(r'^Held behind[:,]?\s*', 'waits on ', flag)}", width)]
        out.append("")
    if features:
        out.append("TO REVIEW - landed; the GM may overturn any row")
        out += [_fit(f"  {_num(d):>3}  {_fit(d.name.split('-', 1)[1], 40):<40} {len(o):>3}  {_counts(o)}", width) for d, o in features]
        declined = sum(r.get("kind") == "arbiter-fix-declined" for _, o in features for _, r in o)
        out += ["", f"  needs a decision: {len(kept)} question(s), {declined} fix(es) declined to the GM - in full: make gm-review EXPLAIN=1",
                "  a feature's rows:  make gm-review F=NNN   (each in full: add EXPLAIN=1, one row: ROW=n)",
                "  reviewed:          make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS=\"<his words>\")"]
    return "\n".join(out) + "\n"


#: what each ruling DID, in the words the GM reads it in (hm_arbiter.py's docstring: continue lifts a cap by one round, accept
#: and process-fault close the unit)
VERDICTS = {"accept": "ACCEPT - stop checking; the work stands as it is now and this check runs no further round on it",
            "continue": "CONTINUE - allow one more round of the check",
            "process-fault": "PROCESS FAULT - the tooling, not the work, was at fault; the fix below is what it asks for"}


def _check_says(root: Path, check: str) -> str:
    """What a check judges, from its agent file's description (the text before ` - run`)."""
    f = root / ".claude" / "agents" / f"{check}.md"
    m = re.search(r"^description:\s*(.+)$", f.read_text(encoding="utf-8"), re.M) if f.is_file() else None
    return m.group(1).split(" - run")[0].strip().rstrip(".") if m else ""


def _where(root: Path, trigger: str) -> str:
    """The file a trigger's subject lives in: a research question's page, a pop-up's write-up, a reversal's file."""
    m = re.search(r"\|q:(\d{4})", trigger)
    if m:
        pages = sorted(p for p in (root / "research" / "questions").glob(f"{m.group(1)}-*.html") if p.name.count(".") == 1)
        return str(pages[0].relative_to(root)) if pages else ""
    m = re.search(r"\|modal:(.+?)(?:@\d+)?$", trigger)
    if m:
        return f"l7r/diagram/interactive/assets/modals/{m.group(1)}.md"
    return trigger.split(":", 1)[1].split("/.clones/", 1)[-1].split("/", 1)[-1] if trigger.startswith("reversal:") else ""


def _happened(root: Path, r: dict) -> str:
    """What fired the ruling, in plain words."""
    t, asked = str(r.get("trigger", "")), str(r.get("asked", ""))
    m = re.fullmatch(r"round:([^|]+)\|[a-z]+:(.+?)(?:@(\d+))?", t)
    if m:
        says = _check_says(root, m.group(1))
        return (f"The {m.group(1)} check" + (f" ({says[0].lower() + says[1:]})" if says else "")
                + f" was owed a round {m.group(3) or 3} on {m.group(2)}. Three rounds on one thing can mean a loop, so the"
                " round arbiter rules before the third runs." + (f" As it fired: {asked}" if asked else ""))
    kind = re.split(r"[:@]", t, maxsplit=1)[0]
    return {"reversal": "An edit put back text that an earlier edit of the same file in this feature had replaced (A -> B -> A):"
                        " checks may be pulling the text two ways.",
            "red-gate": "`make done` went red twice in a row: the arbiter rules on whether the session is stuck.",
            "cascade": "Checks were dispatched faster than one per changed line: reviews may be triggering reviews.",
            "ask": "The session put a process question to the round arbiter instead of to the GM."}.get(kind, f"Trigger {t}.") + (
        f" As it fired: {asked}" if asked else "")


def _wrap(label: str, text: str, width: int) -> list[str]:
    return textwrap.wrap(f"{label}{text}", width=width, initial_indent="    ", subsequent_indent="      ") if text else []


def _fix_lines(i: int, fx: dict, width: int, f: int) -> list[str]:
    status = fx.get("kind", "").removeprefix("arbiter-fix-")
    out = [f"    [{i}] the tooling fix: {status.upper()}"]
    out += _wrap("Done: " if status == "done" else "Declined because: ", fx.get("note", ""), width)
    out += _wrap("Test: ", fx.get("test", ""), width)
    if status == "declined":
        out += _wrap("YOUR DECISION: ", f"should this fix be made after all? Mark it reviewed (make gm-reviewed F={f}) to leave it "
                     f"declined, or OVERTURN={i} TO=<an open feature> to have it built.", width)
    return out


def _explain_row(root: Path, f: int, i: int, r: dict, fixes: list[tuple[int, dict]], width: int) -> list[str]:
    check, subject = _subject(r)
    out = [_fit(f"[{i}] {check} {subject}".rstrip() + f" - {r.get('utc', '')[:16].replace('T', ' ')} UTC", width)]
    if r.get("kind") == "accepted":
        out += _wrap("A session accepted this finding without fixing it: ", str(r.get("finding", "")), width)
        out += _wrap("Its reason: ", str(r.get("why", "")), width)
    else:
        out += _wrap("What happened: ", _happened(root, r), width)
        out += _wrap("Where: ", _where(root, str(r.get("trigger", ""))), width)
        ruled = VERDICTS.get(r.get("ruling", ""), str(r.get("ruling", "")))
        if r.get("ruling") == "continue" and not str(r.get("trigger", "")).startswith("round:"):  # no round to add: work goes on
            ruled = "CONTINUE - nothing is stuck; the work carries on as it was"
        out += _wrap("The arbiter ruled: ", ruled, width)
        out += _wrap("Why: ", str(r.get("why", "")), width)
        out += _wrap("It set the next step: ", str(r.get("what", "")), width)
        out += _wrap("It asked for a tooling fix: ", str(r.get("tooling_fix", "")), width)
    for j, fx in fixes:
        out += _fix_lines(j, fx, width, f)
    if not any(fx.get("kind") == "arbiter-fix-declined" for _, fx in fixes):
        out += _wrap("Your call: ", f"nothing to do if you agree. To overturn: make gm-reviewed F={f} OVERTURN={i} TO=<an open "
                     "feature> (it becomes open work there).", width)
    return [*out, ""]


def _detail_of(root: Path, d: Path) -> dict[tuple[str, str], dict]:
    """The arbiter's own record of each ruling (`arbiter.jsonl`: the next step, the question as fired), by trigger and time."""
    f = d / "arbiter.jsonl"
    out = {}
    for line in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            a = json.loads(line)
        except ValueError:
            continue
        out[(a.get("trigger", ""), a.get("utc", ""))] = a
    return out


def explain(root: Path, feature: str = "", row: str = "", width: int = 0) -> str:
    """Each open row in full: what fired it, what the arbiter ruled and why, the tooling fix and its fate, and what the GM is
    asked. With no feature: only what NEEDS the GM - the held questions and the fixes declined to him."""
    width = min(110, width or shutil.get_terminal_size((110, 24)).columns)
    if not feature:
        return _needs_you(root, width)
    d = _feature(root, feature)
    o = next((o for f, o in open_rows(root) if f == d), [])
    if not o:
        return f"gm-review: nothing of {d.name} waits on the GM\n"
    extra = _detail_of(root, d)
    o = [(i, {**extra.get((r.get("trigger", ""), r.get("utc", "")), {}), **r}) for i, r in o]
    fixes = [(i, r) for i, r in o if str(r.get("kind", "")).startswith("arbiter-fix-")]
    rulings = [(i, r) for i, r in o if (i, r) not in fixes]
    out = [*textwrap.wrap(f"{d.name}: {len(o)} row(s) - {_counts(o)}", width=width, subsequent_indent="  "), ""]
    head, shown = len(out), set()
    for i, r in rulings:
        mine_ = [(j, fx) for j, fx in fixes if fx.get("trigger") and fx.get("trigger") == r.get("trigger")]
        if not row or row in {str(i), *(str(j) for j, _ in mine_)}:
            out += _explain_row(root, _num(d), i, r, mine_, width)
        shown |= {j for j, _ in mine_}
    for j, fx in fixes:
        if j not in shown and (not row or row == str(j)):
            out += [_fit(f"[{j}] {' '.join(x for x in _subject(fx) if x)}", width), *_wrap("The fix asked for: ", fx.get("tooling_fix", ""), width),
                    *_fix_lines(j, fx, width, _num(d)), ""]
    return "\n".join(out) + "\n" if len(out) > head else f"gm-review: no open row {row} in {d.name}\n"


def _behind(h: str) -> bool:
    """A held row that waits on another row of the ranking (`Held behind #...`), not on a decision of the GM's."""
    return h.partition(": ")[2].startswith("Held behind")


def _needs_you(root: Path, width: int) -> str:
    waits = held(root, full=True)
    asks = questions(root, "kept")
    declined = [(d, i, r) for d, o in open_rows(root) for i, r in o if r.get("kind") == "arbiter-fix-declined"]
    out = ["WHAT NEEDS YOUR DECISION" + ("" if asks or declined else ": nothing - no question kept for you and no fix declined to you"), ""]
    for n, (d, i, r) in enumerate(asks, 1):
        out += [_fit(f"{n}. QUESTION {_num(d)}#{i} ({d.name})", width), *_wrap("", str(r.get("question", "")), width),
                *_wrap("Why it is yours (escalation-check): ", str(r.get("escalation", "")), width),
                *_wrap("Answered: ", f"make gm-reviewed F={_num(d)} ROW={i} WORDS=\"<your answer>\"", width), ""]
    for n, (d, i, r) in enumerate(declined, len(asks) + 1):
        out += [_fit(f"{n}. A TOOLING FIX DECLINED TO YOU: feature {_num(d)} row [{i}], {' '.join(x for x in _subject(r) if x)}", width),
                *_wrap("The arbiter asked: ", r.get("tooling_fix", ""), width), *_wrap("Declined because: ", r.get("note", ""), width),
                *_wrap("Decide: ", f"leave it declined (make gm-reviewed F={_num(d)}) or have it built (make gm-reviewed F={_num(d)} "
                       f"OVERTURN={i} TO=<an open feature>).", width), ""]
    if waits:
        out += ["WAITING ON OTHER WORK - held in the ranking until another row is done; nothing for you to decide", ""]
        for h in waits:
            key, _, flag = h.partition(": ")
            out += [_fit(f"  * {key}", width), *_wrap("", re.sub(r"^Held behind\s*", "Waits on ", flag), width), ""]
    rest = sum(len(o) for _, o in open_rows(root)) - len(declined) - len(asks) - len(questions(root, "owed"))
    out += textwrap.wrap(f"The other {rest} row(s) are decisions already made that you may overturn; nothing waits on them. "
                         "Each in full: make gm-review F=NNN EXPLAIN=1 [ROW=n].", width=width)
    return "\n".join(out) + "\n"


def accept(d: Path, finding: str, reason: str) -> dict:
    """A finding accepted with a reason - the work goes on, and the GM may overturn it after landing (FR-012)."""
    if len(reason.split()) < 2:
        raise ValueError("REASON needs two words or more - the GM reads it")
    row = {"kind": "accepted", "finding": finding, "why": reason, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with (d / ROWS).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    ensure_box(d)
    return row


def reviewed(root: Path, d: Path, overturn: int | None = None, to: Path | None = None, words: str = "") -> list[str]:
    """The GM has reviewed `d`'s rows: each marked reviewed; an overturned one becomes an open row of the feature `to`; the
    GM-review box is ticked - through the closing check, since it may close the feature (FR-009). `words`, when a session marks
    the review on the GM's behalf after discussing it with him, are his words, kept on each row it marks."""
    if words and len(words.split()) < 2:
        raise ValueError("WORDS are the GM's own, two words or more")
    rs = rows(d)
    msgs = []
    if overturn is not None:
        if to is None or not (0 <= overturn < len(rs)):
            raise ValueError("OVERTURN=<row number> needs TO=<an open feature>")
        with (to / "found.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"check": "gm-review", "file": d.name, "block": rs[overturn].get("trigger") or rs[overturn].get("finding"),
                                 "finding": "overturned by the GM: " + " - ".join(x for x in (rs[overturn].get("why") or rs[overturn].get("tooling_fix", ""),
                                                                                     rs[overturn].get("note", "")) if x), "status": "open"}, ensure_ascii=False) + "\n")
        msgs.append(f"row {overturn} overturned - an open row of {to.name}")
        # the overturned row ALONE is reviewed: the rest of the feature's rows still wait on the GM (2026-10-12, overturning
        # 343's two declined fixes would have marked its 83 other rows reviewed by the GM)
        rs[overturn] = {**rs[overturn], "reviewed": time.strftime("%Y-%m-%d", time.gmtime()), "overturned_to": to.name}
        (d / ROWS).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8")
        if any("reviewed" not in r for r in rs):
            return msgs
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8") if tasks.is_file() else ""
    if re.search(rf"^- \[ \] GM review \(make gm-reviewed F={_num(d)}\)", text, re.M) and text.count("- [ ] ") == 1:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "gates"))
        import close_check  # noqa: PLC0415

        why = close_check.reasons(d, root / "specs")
        if why:
            raise ValueError("the GM's box closes the feature, and: " + "; ".join(why))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    (d / ROWS).write_text("".join(json.dumps({**r, "reviewed": r.get("reviewed", today), **({"gm_words": words} if words and "reviewed" not in r else {})}, ensure_ascii=False) + "\n" for r in rs),
                          encoding="utf-8")
    # ...THE BOX AS WRITTEN, with or without its `[lands-open]` (feature 432: 415's box was written without it, so this marked
    # its rows reviewed, said so, and left the box open)
    open_box = re.compile(rf"^- \[ \] (GM review \(make gm-reviewed F={_num(d)}\).*)$", re.M)
    if open_box.search(text):
        tasks.write_text(open_box.sub(r"- [x] \1", text, count=1), encoding="utf-8")
    msgs.append(f"{len(rs)} row(s) of {d.name} reviewed")
    return msgs


def reviewed_row(d: Path, row: int, words: str = "") -> str:
    """Row `row` of `d` alone is reviewed; the feature's other rows still wait on the GM, and its box stays open while they do."""
    if words and len(words.split()) < 2:
        raise ValueError("WORDS are the GM's own, two words or more")
    rs = rows(d)
    if not 0 <= row < len(rs):
        raise ValueError(f"ROW={row}: {d.name} has rows 0-{len(rs) - 1}")
    rs[row] = {**rs[row], "reviewed": time.strftime("%Y-%m-%d", time.gmtime()), **({"gm_words": words} if words else {})}
    (d / ROWS).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs), encoding="utf-8")
    return f"row {row} of {d.name} reviewed; {sum('reviewed' not in r for r in rs)} still wait on the GM"


def _feature(root: Path, f: str) -> Path:
    hits = sorted((root / "specs").glob(f"{int(f):03d}-*")) if f.isdigit() else [root / "specs" / f]
    if not hits or not hits[0].is_dir():
        raise SystemExit(f"gm-review: no specs/{f}* directory")
    return hits[0]


def main(argv: list[str]) -> int:
    root = Path(".").resolve()
    try:
        if argv[:1] == ["list"] and len(argv) <= 2:
            sys.stdout.write(listing(root, *argv[1:]))
        elif argv[:1] == ["explain"] and len(argv) <= 3:
            sys.stdout.write(explain(root, *argv[1:]))
        elif argv[:1] == ["accept"] and len(argv) == 4:
            accept(_feature(root, argv[1]), argv[2], argv[3])
            print("accept: recorded - a row the GM may read and overturn (make gm-review)")
        elif argv[:1] == ["reviewed"] and len(argv) in (2, 4):
            ov = int(argv[2]) if len(argv) == 4 else None
            to = _feature(root, argv[3]) if len(argv) == 4 else None
            for m in reviewed(root, _feature(root, argv[1]), ov, to, os.environ.get("GM_WORDS", "").strip()):
                print(f"gm-reviewed: {m}")
        elif argv[:1] == ["question"] and len(argv) == 4:
            d = _feature(root, argv[1])
            n = question(d, argv[2], argv[3])
            print(f"gm-question: row {n} of {d.name} - owed escalation-check before it reaches the GM (make gm-escalated F={_num(d)} ROW={n})")
        elif argv[:1] == ["owed-check"] and len(argv) == 1:
            owed = owed_in_delta(root)
            for line in owed:
                print(f"gm-review: owed escalation-check - {line}", file=sys.stderr)
            if owed:
                print("gm-review: dispatch escalation-check on each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"", file=sys.stderr)
                return 1
        elif argv[:1] == ["escalated"] and len(argv) == 5:
            print(f"gm-escalated: {escalated(_feature(root, argv[1]), int(argv[2]), argv[3], argv[4])}")
        elif argv[:1] == ["reviewed-row"] and len(argv) == 3:
            print(f"gm-reviewed: {reviewed_row(_feature(root, argv[1]), int(argv[2]), os.environ.get('GM_WORDS', '').strip())}")
        else:
            print(__doc__.split("\n\n")[-1], file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"gm-review: refused - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

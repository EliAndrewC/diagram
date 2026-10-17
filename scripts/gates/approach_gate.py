"""A task's Approach is answered before it is ticked, and answered again after a trigger (feature 385 T02, plan D8 and D9).

    python3 scripts/gates/approach_gate.py owed <feature> <task>     why `make tick` may not tick the task, or nothing
    python3 scripts/gates/approach_gate.py ruled <trigger>           the round arbiter ruled: an `hour:` or `red-gate@` ruling owes part B
    python3 scripts/gates/approach_gate.py cohort                    the newest cohort record: a seed newly failing owes part B

WHY (the GM, 2026-10-17): sessions hyper-focused - hours defending the 700 ft reach, an angle rule applied where an obstruction
forced the shape, houses proposed to move for a tidy footpath - because nothing made them ask, in time, where a constraint came
from and whether it described the world there. The checklist asks; this makes the asking happen.

D8 (FR-003). A plan opts in with the line `**Approach checklist**: <path>`. Each task then has a `### Txx Approach` block
answering every numbered item of the checklist's part A (`1. ...` lines); `make tick` refuses a task whose block is missing or
answers fewer, naming the missing numbers. A plan that does not opt in is not asked.

D9 (FR-004). A trigger writes `<git dir>/approach-owed.json` - the task, the trigger, its time and the part it owes - and its
message names that part. `make tick` refuses the task until the plan holds the owed block stamped (a UTC time in its heading)
at or after the trigger, answering every item of that part: `### Txx part B (2026-10-17T21:40Z)`, or for a re-decided plan
section `### Txx Approach (re-answered 2026-10-17T21:40Z)`. The triggers, each with a floor so it never fires on correct work:
a round-arbiter ruling on an `hour:` or `red-gate@` trigger (`ruled`); a cohort seed failing that passed at the baseline - the
newest earlier record, at a commit on main, that rolled the same seed (`cohort`; a seed failing at the baseline too fires
nothing, and one with no baseline fires nothing); a re-review of a task's Decisions block after an earlier CLEAR on it, its
change more than a typo (`plan_gate.record_blocks`, by `owe`).
"""

from __future__ import annotations

import calendar
import json
import pathlib
import re
import subprocess
import sys
import time

OPT_IN = re.compile(r"^\*\*Approach checklist\*\*:\s*`?([^\s`]+)`?", re.M)
STAMP = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d)(?::(\d\d))?Z")
_ITEM = re.compile(r"^(\d+)\.\s+\S", re.M)
OWED = "approach-owed.json"
#: what each part's block is headed, and what its trigger's message calls it
HEADS = {"A": "Approach", "B": "part B"}
PART_TITLE = {"A": "part A - at task start", "B": "part B - when the work resists"}


def parse_utc(text: str) -> float | None:
    m = STAMP.search(text or "")
    if not m:
        return None
    return float(calendar.timegm(time.strptime(m.group(1) + ":" + (m.group(2) or "00"), "%Y-%m-%dT%H:%M:%S")))


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def checklist(root: pathlib.Path, plan_text: str) -> pathlib.Path | None:
    """The checklist a plan opts in to (None when it does not)."""
    m = OPT_IN.search(plan_text)
    return root / m.group(1) if m else None


def part_items(checklist_text: str, part: str) -> list[int]:
    """The numbers of the items under the checklist's `## <part>.` heading."""
    m = re.search(rf"^## {part}\..*?(?=^## |\Z)", checklist_text, re.M | re.S)
    return [int(n) for n in _ITEM.findall(m.group(0))] if m else []


def task_blocks(plan_text: str, task: str, part: str) -> list[tuple[str, str]]:
    """(heading, body) of every `###`/`####` block headed `<task> Approach` (part A) or `<task> part B`."""
    head = re.compile(rf"^#{{3,4}}\s+{re.escape(task)}\s+{re.escape(HEADS[part])}\b.*$", re.M | re.I)
    out = []
    for m in head.finditer(plan_text):
        nxt = re.compile(r"^#{2,4}\s", re.M).search(plan_text, m.end())
        out.append((m.group(0), plan_text[m.end(): nxt.start() if nxt else len(plan_text)]))
    return out


def unanswered(body: str, items: list[int]) -> list[int]:
    got = {int(n) for n in _ITEM.findall(body)}
    return [n for n in items if n not in got]


def _best(plan_text: str, task: str, part: str, items: list[int], since: float | None) -> tuple[bool, list[int]]:
    """(a block exists, the items the most complete block stamped at or after `since` leaves unanswered)."""
    found = [(h, b) for h, b in task_blocks(plan_text, task, part)
             if since is None or ((t := parse_utc(h)) is not None and t >= since)]
    if not found:
        return False, items
    return True, min((unanswered(b, items) for _h, b in found), key=len)


def git_dir(root: pathlib.Path) -> pathlib.Path:
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--absolute-git-dir"], capture_output=True, text=True).stdout.strip()
    return pathlib.Path(out) if out else root / ".git"


def owed_entries(root: pathlib.Path) -> list[dict]:
    try:
        data = json.loads((git_dir(root) / OWED).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def owe(root: pathlib.Path, feature: str, task: str, trigger: str, part: str, now: str | None = None) -> str:
    """Record that `task` owes `part` after `trigger`; returns the message naming the part and the block to write."""
    when = now or now_utc()
    rows = owed_entries(root)
    if not any(r.get("feature") == feature and r.get("task") == task and r.get("trigger") == trigger for r in rows):
        rows.append({"feature": feature, "task": task, "trigger": trigger, "part": part, "utc": when})
        (git_dir(root) / OWED).write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    head = f"### {task} part B ({when[:16]}Z)" if part == "B" else f"### {task} Approach (re-answered {when[:16]}Z)"
    return (f"approach owed: {trigger} - {task} owes the checklist's {PART_TITLE[part]}, answered before the next attempt: add "
            f"`{head}` to specs/{feature}/plan.md, every item of part {part} numbered; `make tick` refuses {task} until it is there")


def refusal(spec_dir: pathlib.Path, root: pathlib.Path, task: str) -> str | None:
    """Why `make tick` may not tick `task` (D8 and D9), or None."""
    plan = spec_dir / "plan.md"
    text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    path = checklist(root, text)
    if path is None:
        return None
    if not path.is_file():
        return f"the plan opts in to the approach checklist at {path.relative_to(root)}, which does not exist"
    lines = path.read_text(encoding="utf-8")
    items = part_items(lines, "A")
    exists, missing = _best(text, task, "A", items, None)
    if not exists:
        return (f"{task} has no `### {task} Approach` block in {spec_dir.name}/plan.md - answer every item of the checklist's part "
                f"A ({', '.join(map(str, items))}) before it is ticked (feature 385 D8)")
    if missing:
        return f"{task}'s Approach block leaves part A item(s) {', '.join(map(str, missing))} unanswered (feature 385 D8)"
    for row in owed_entries(root):
        if row.get("feature") != spec_dir.name or row.get("task") != task:
            continue
        part = str(row.get("part") or "B")
        exists, missing = _best(text, task, part, part_items(lines, part), parse_utc(str(row.get("utc"))))
        if not exists or missing:
            what = "no block stamped after it" if not exists else f"item(s) {', '.join(map(str, missing))} unanswered"
            return (f"{row.get('trigger')} at {row.get('utc')} owes {task} the checklist's {PART_TITLE.get(part, part)}: {what} - "
                    f"add `### {task} {HEADS.get(part, part)} (<UTC>)` stamped at or after it (feature 385 D9)")
    return None


# ---- the triggers -------------------------------------------------------------------------------------------------------

#: the round-arbiter triggers whose ruling owes part B (D9): the hourly step-back and a second red gate
RULED_PREFIXES = ("hour:", "red-gate@")


def _active(root: pathlib.Path) -> tuple[pathlib.Path | None, str]:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import plan_gate  # noqa: PLC0415

    return plan_gate.active_task(root)


def _opted_in(root: pathlib.Path, d: pathlib.Path | None) -> bool:
    plan = d / "plan.md" if d is not None else None
    return plan is not None and plan.is_file() and checklist(root, plan.read_text(encoding="utf-8")) is not None


def ruled(root: pathlib.Path, trigger: str, now: str | None = None) -> str | None:
    if not trigger.startswith(RULED_PREFIXES):
        return None
    d, task = _active(root)
    if d is None or not task or not _opted_in(root, d):
        return None
    return owe(root, d.name, task, trigger, "B", now)


def _on_main(root: pathlib.Path, commit: str) -> bool:
    """Rolled on main's engine (`cohort_known.same_engine`): a baseline rolled in a detached worktree at the clone's HEAD counts
    (feature 385 T03: seed 49's HEAD roll sat on a clone commit, so D9 had no floor for it)."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "measure"))
    import cohort_known  # noqa: PLC0415

    return cohort_known.same_engine(root, commit)


def newly_failing(record: dict, earlier: list[dict], on_main) -> list[int]:  # noqa: ANN001 - a predicate on a commit
    """The seeds `record` fails that passed in the newest earlier record at a commit on main rolling the same seed and
    households (the baseline). A seed failing there too, or with no such record, is not new."""
    out = []
    for s in record.get("seeds") or []:
        if s.get("verdict") == "pass":
            continue
        for r in sorted(earlier, key=lambda r: str(r.get("utc")), reverse=True):
            if str(r.get("utc")) >= str(record.get("utc")) or r.get("households") != record.get("households"):
                continue
            base = next((b for b in r.get("seeds") or [] if b.get("seed") == s.get("seed")), None)
            if base is None or not r.get("commit") or not on_main(str(r["commit"])):
                continue
            if base.get("verdict") == "pass":
                out.append(int(s["seed"]))
            break
    return out


def cohort(root: pathlib.Path, now: str | None = None) -> str | None:
    logs = sorted((root / "dev/cohort-log").glob("[0-9]*.json"))
    if not logs:
        return None
    records = [json.loads(p.read_text(encoding="utf-8")) for p in logs]
    seeds = newly_failing(records[-1], records[:-1], lambda c: _on_main(root, c))
    d, task = _active(root)
    if not seeds or d is None or not task or not _opted_in(root, d):
        return None
    return owe(root, d.name, task, f"cohort@{records[-1].get('utc')}: seed(s) {', '.join(map(str, seeds))} newly failing", "B", now)


def main(argv: list[str]) -> int:
    root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or ".")
    if argv[:1] == ["owed"] and len(argv) == 3:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import plan_gate  # noqa: PLC0415

        d = plan_gate.resolve(argv[1], root)
        why = refusal(d, root, argv[2]) if d is not None else None
        print(why or "", end="\n" if why else "")
        return 1 if why else 0
    if argv[:1] == ["ruled"] and len(argv) == 2:
        msg = ruled(root, argv[1])
    elif argv == ["cohort"]:
        msg = cohort(root)
    else:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    if msg:
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

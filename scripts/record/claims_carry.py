"""A finding a page edit surfaced on code left unchanged is CARRIED, not refused (feature 385 amendment 3, FR-013, plan D26-D29).

    python3 scripts/record/claims.py carry --feature <n> [--task Txx]     (`make claims-carry F=<n> [T=<Txx>]`)

WHY (the GM, 2026-10-17, "Yes, please lock in option three."): at T03's landing a one-paragraph edit to page 0246 re-owed
the claims that cite it, and the three findings that came back - all on code T03 never touched - refused the push as
INTRODUCED. Option 3: such a finding never blocks the landing; it is filed as an open task of the feature being landed, so that
feature cannot close while it stands.

`claims.classify` decides what is carried (D26). This module keeps the record: `specs/<feature>/claims-carried.jsonl`, one row
`{"task", "keys", "utc"}` a filing. A key is FILED while a row of the ACTIVE feature's record names it and that row's task is
still an open box in its `tasks.md` (D27): ticking the task un-files it, so a finding still standing refuses again; another
feature's record never files it, so a finding cannot be parked in a long-lived feature while this one closes (spec-fidelity,
T13 round 1). `speckit-todo.py`'s open-task refusal honors a `[lands-open]` box a row names (D28).
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

RECORD = "claims-carried.jsonl"
_BOX = re.compile(r"^- \[( |x)\] (T\d+)\b(.*)$", re.M)
_LANDS_OPEN = " [lands-open]"


def _plan_gate() -> Any:  # noqa: ANN401 - the module
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gates"))
    import plan_gate  # noqa: PLC0415 - the moved scripts it imports

    return plan_gate


def active_feature(root: Path) -> Path | None:
    """The feature being landed: the active task's (`plan_gate.active_task`), or None."""
    return _plan_gate().active_task(root)[0]


def rows(d: Path) -> list[dict[str, Any]]:
    f = d / RECORD
    lines = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
    return [json.loads(ln) for ln in lines if ln.strip()]


def open_ids(d: Path) -> set[str]:
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8") if tasks.is_file() else ""
    return {m.group(2) for m in _BOX.finditer(text) if m.group(1) == " "}


def carried_ids(d: Path) -> set[str]:
    """The task ids the record names - the boxes the tooling put there, which the open-task refusal honors."""
    return {str(r.get("task")) for r in rows(d)}


def filed(root: Path) -> dict[str, str]:
    """key -> its open task, for every key the active feature's record files (none with no active feature)."""
    d = active_feature(root)
    if d is None:
        return {}
    live = open_ids(d)
    return {k: str(r["task"]) for r in rows(d) if r.get("task") in live for k in r.get("keys") or []}


def _ruled(d: Path, ruling: str) -> bool:
    """Is `ruling` a `trigger` the feature's round-arbiter record holds (`arbiter.jsonl`)?"""
    f = d / "arbiter.jsonl"
    for ln in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("trigger") == ruling:
            return True
    return False


def _file_into(text: str, task: str, keys: list[str], by: str = "the claims gate (FR-013)") -> str:
    """`text` (a tasks.md) with `keys` appended to open box `task`'s line, before its closing `[lands-open]`."""
    for m in _BOX.finditer(text):
        if m.group(2) != task:
            continue
        if m.group(1) != " ":
            raise ValueError(f"{task} is ticked; file into an open task, or leave T= off for a new one")
        line = m.group(0)
        tail = _LANDS_OPEN if line.endswith(_LANDS_OPEN) else ""
        body = line[: len(line) - len(tail)] if tail else line
        return text[: m.start()] + f"{body}; carried by {by}: {', '.join(keys)}{tail}" + text[m.end() :]
    raise ValueError(f"no task {task} in tasks.md")


def _new_box(text: str, keys: list[str], ruling: str = "") -> tuple[str, str]:
    """(`text` with a new open box for `keys`, the box's id): numbered after the highest task, before the GM-review box."""
    task = f"T{max((int(m.group(2)[1:]) for m in _BOX.finditer(text)), default=0) + 1:02d}"
    by = f"the round arbiter's ruling {ruling}: findings it carried" if ruling else "the claims gate (FR-013): findings on code the change left unchanged"
    box = f"- [ ] {task} Carried by {by} - fix the code or the claim and re-check each: {', '.join(keys)}{_LANDS_OPEN}\n      research: rendering\n"
    gm = re.search(r"^- \[[ x]\] GM review\b", text, re.M)
    if gm:
        return text[: gm.start()] + box + text[gm.start() :], task
    return text.rstrip("\n") + "\n" + box, task


def carry(root: Path, feature: str, task: str, keys: list[str], now: str | None = None, ruling: str = "") -> str:
    """File `keys` into the feature being landed (D27); returns what was done. Raises ValueError naming what to do instead.

    `ruling` (feature 385 T45, D59): `keys` are findings the gate counts as introduced, which that round-arbiter ruling carried;
    it must be a `trigger` in the feature's `arbiter.jsonl`, and the record's row names it. The box and its row are written
    together, so `holding` honors the box by its id - never a box that merely cites a trigger."""
    d = _plan_gate().resolve(feature, root)
    here = active_feature(root)
    if d is None or here is None or d.resolve() != here.resolve():
        raise ValueError(f"a carried finding is filed only into the feature being landed - the active task's ({here.name if here else 'none: `make task-start F=<n> T=<Txx>` first'}), not {feature}")
    if ruling and not _ruled(d, ruling):
        raise ValueError(f"RULING={ruling} is no trigger in {d.name}/arbiter.jsonl - name the round arbiter's recorded ruling that carried these findings")
    if not keys:
        return "claims-carry: no carried finding is unfiled"
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8")
    by = f"the round arbiter's ruling {ruling}" if ruling else "the claims gate (FR-013)"
    if task:
        text = _file_into(text, task, keys, by)
    else:
        text, task = _new_box(text, keys, ruling)
    tasks.write_text(text, encoding="utf-8")
    row: dict[str, Any] = {"task": task, "keys": keys, "utc": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if ruling:
        row["ruling"] = ruling
    with (d / RECORD).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return f"claims-carry: {len(keys)} finding(s) filed into {d.name} {task}; commit tasks.md and {RECORD} with the landing"


def gate(cx: Any, root: Path) -> tuple[list[str], list[str]]:  # noqa: ANN401 - `cx` is the claims module, passed to avoid a cycle
    """(refusals, warnings) for the push: owed units, introduced findings and carried ones not yet filed (FR-013, D28);
    pre-existing and filed carried findings warn."""
    refuse, intro, pre, carried = classified(cx, root)
    done = filed(root)
    d = active_feature(root)
    how = f"`make claims-carry F={d.name.split('-', 1)[0]}`" if d is not None else "`make task-start F=<n> T=<Txx>`, then `make claims-carry F=<n>`"
    unfiled = [f"carry: {line} - a finding on code the change left unchanged: file it with {how} (make land files it itself)" for k, line in carried if k not in done]
    warn = [f"carried ({d.name if d else ''} {done[k]}): {line}" for k, line in carried if k in done]
    return refuse + [f"introduced: {x}" for x in intro] + unfiled, [f"pre-existing: {x}" for x in pre] + warn


def classified(cx: Any, root: Path) -> tuple[list[str], list[str], list[str], list[tuple[str, str]]]:  # noqa: ANN401
    """(owed refusals, introduced, pre-existing, carried) at `root` against its merge base with origin/main."""
    cur = cx.current(root)
    index = cx.load_index(root / cx.INDEX)
    due = cx.owed(cur, index, root / "research" / "questions", cx.load_store(root / cx.STORE))
    mb = (cx._git(root, "merge-base", "HEAD", "origin/main") or cx._git(root, "rev-parse", "HEAD") or "").strip()
    base_index = json.loads(cx._git(root, "show", f"{mb}:{cx.INDEX}") or "{}") if mb else {}
    with tempfile.TemporaryDirectory() as tmp:
        bskill = cx.base_tree(root, mb, Path(tmp)) if mb else Path(tmp)
        cores = cx.base_cores(bskill, keep=root) if mb else {}
        answered = frozenset(k for k, v in index.items() if k in cur and cx.relabel_answered(v, cur[k], root))
        intro, pre, carried = cx.classify(
            cur, index, base_index, cores, bskill / "research" / "questions", cx.load_deferred(root / cx.DEFERRED), answered
        )
    return [f"owed ({why}): {key}" for key, why in due], intro, pre, carried

"""A held feature's tasks refused at `make task-start` - feature 417 T02 (plan D4, D9; FR-010).

WHY. The GM, 2026-10-24: "we might want to put our claims work on hold and then open a new feature whose goal is 'all seeds
passing'" - and 417's FR-010: no task of a claims feature that changes the engine starts until 417 closes. A hold written
only in a status line is remembered, not made; `make task-start` is the one place a task becomes active (a landing needs the
active task), so the hold is asked there.

A feature is HELD when its spec's `**Status**:` line says `ON HOLD` and `until feature NNN`, while NNN is open by `make
speckit-todo`'s own rule. A held feature's task is refused, naming NNN. `HOLD_OK="<reason>"` admits a task that does not
change the engine; an ENGINE task has no escape. A task is an engine task when its lines in `tasks.md`, or its section of
`plan.md`, name a path under `l7r/` or `pool/` or an engine module by its name (`fixture_seats`, `knots.py` - 405's tasks
name modules so, never by path), or its `research:` line is `physical`. A task is NOT an engine task only when it is sure:
it names a path outside the engine (`scripts/`, `tests/`, `research/`, `docs/`, `specs/`, `dev/`, `.claude/`, the Makefile) and
no engine file or module; anything else - a task not found, a task that names nothing - is unsure, and unsure counts as engine
(plan D9).
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys
from typing import Any

_HOLD = re.compile(r"ON HOLD\b.*?\buntil feature (\d{3,})", re.S)
#: the status PARAGRAPH, not its first line: 384's wraps, and its hold is on the second (a test pins it)
_STATUS = re.compile(r"^\*\*Status\*\*:\s*(.*?)(?:\n\s*\n|\Z)", re.M | re.S)
_ENGINE = re.compile(r"(?<![\w/.-])(?:l7r|pool)/")
_OUTSIDE = re.compile(r"(?<![\w/.-])(?:scripts|tests|research|docs|specs|dev|\.claude)/|\bMakefile\b")
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _engine_modules(root: pathlib.Path = _ROOT) -> frozenset[str]:
    """Every engine module's name: `l7r/**/*.py` and `pool/**/*.py` stems (`fixture_seats`), packages included, `__init__` not."""
    names = {p.stem.removesuffix(".gen") for top in ("l7r", "pool") for p in (root / top).rglob("*.py") if p.stem != "__init__"}
    names |= {p.name for p in (root / "l7r").rglob("*") if p.is_dir() and (p / "__init__.py").is_file()}
    return frozenset(n for n in names if len(n) > 3)


def _todo() -> Any:
    path = pathlib.Path(__file__).resolve().parents[1] / "speckit-todo.py"
    spec = importlib.util.spec_from_file_location("speckit_todo", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("speckit_todo", mod)
    spec.loader.exec_module(mod)
    return mod


def holder(d: pathlib.Path) -> pathlib.Path | None:
    """The open feature that `d` waits on, or None."""
    spec = d / "spec.md"
    s = _STATUS.search(spec.read_text(encoding="utf-8", errors="replace")) if spec.is_file() else None
    m = _HOLD.search(s.group(1)) if s else None
    if not m:
        return None
    found = sorted(d.parent.glob(f"{m.group(1)}-*"))
    if len(found) != 1:
        return None
    return found[0] if _todo().feature(found[0]).state != "closed" else None


def task_lines(d: pathlib.Path, task: str) -> str:
    """The task's line in `tasks.md` and the indented lines under it ('' when the task is not there)."""
    tasks = d / "tasks.md"
    out: list[str] = []
    for line in tasks.read_text(encoding="utf-8", errors="replace").splitlines() if tasks.is_file() else []:
        if re.match(rf"^\s*- \[[ xX]\] {re.escape(task)}\b", line):
            out = [line]
        elif out and line.startswith((" ", "\t")) and not line.lstrip().startswith("- ["):
            out.append(line)
        elif out:
            break
    return "\n".join(out)


def is_engine_task(d: pathlib.Path, task: str, section: str | None, modules: frozenset[str] | None = None) -> bool:
    lines = task_lines(d, task)
    if not lines:
        return True  # unsure counts as engine (plan D9)
    text = lines + "\n" + (section or "")
    names = modules if modules is not None else _engine_modules()
    if _ENGINE.search(text) or re.search(r"research:\s*physical", lines) or any(w in names for w in _WORD.findall(text)):
        return True
    return not _OUTSIDE.search(text)  # sure only when it names somewhere outside the engine


def refusal(d: pathlib.Path, task: str, section: str | None, hold_ok: str) -> str:
    """'' when the task may start, else why not and what to do."""
    by = holder(d)
    if by is None:
        return ""
    if is_engine_task(d, task, section):
        return (f"task-start: REFUSED - {d.name} is ON HOLD until {by.name} closes, and {task} changes the engine (its task or "
                f"plan section names an engine path or module, or names nothing outside the engine, or it is research: physical). An engine task of a held feature has no escape "
                f"(feature 417 FR-010): work {by.name} first.")
    if not hold_ok.strip():
        return (f"task-start: REFUSED - {d.name} is ON HOLD until {by.name} closes. {task} does not change the engine, so it "
                f'may start with a reason: make task-start F={d.name.split("-", 1)[0]} T={task} HOLD_OK="<why it cannot wait>"')
    return ""

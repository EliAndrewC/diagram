#!/usr/bin/env python3
"""Tick ONE task in a spec-kit feature's tasks.md, with its verify note - `make tick`.

WHY (feature 188, GM 2026-09-05: *"The idea of a make tick helper. does indeed seem good. So we should
go ahead and do that."*). The session that measured the cost of a one-line CSS change found about a
third of its own model turns were bookkeeping: hand-rolled regex scripts to tick a task, two of which
matched nothing and wrote nothing, and one heredoc that truncated a task file before reading it. A
single-purpose tool that REFUSES rather than guesses removes the class.

    tick-task.py <feature> <task> <note> [--boxes]

`feature` is a spec number (`188`) or directory name (`188-page-check-and-the-tweak-lane`); `task` is
the id as written (`T03`, `T04a`); `note` becomes `verify: DONE. <note>`, replacing whatever the task's
`verify:` said; `--boxes` ticks the three research boxes of a physical task. `--note-from-env` takes the
note from `$TICK_NOTE` instead of the argument - how `make tick` passes it, because a note quoting code
in backticks must never pass through a shell that would run it. Refusals (exit 2, nothing
written): no such feature, no tasks.md, no such task, task already ticked, empty note. Success prints
the ticked line and how many tasks remain open.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

#: A RESEARCH-BOX LINE IS MATCHED BY SHAPE, NEVER BY ITS TEXT (feature 229). This held the literal
#: three-box line of constitution v2.12.0 - `research pass`, `source-reader confirmed`, `recorded and
#: cited` - and the roster has been FIVE since features 194 and 211 added `quote-check confirmed` and
#: `source-applicability confirmed`. So the literal matched nothing, and `BOXES=1` reported a ticked
#: task while ticking no box at all: silent, and the gate caught it only at the end, on seven tasks at
#: once (`tests/test_task_research_boxes.py`). A boxes line is an INDENTED line that is a checkbox - one box or
#: several, which stays true however many boxes the constitution grows.
def _is_boxes_line(line: str) -> bool:
    # ...AND ONE BOX A LINE, AS A TASK MAY BE WRITTEN (feature 291): its ten physical tasks listed the five boxes one per
    # indented line, which `tests/test_task_research_boxes.py` accepts, and `BOXES=1` refused all ten as having none. An
    # indented line that is a checkbox is a box: a task line itself starts at the margin.
    return line[:1].isspace() and line.lstrip().startswith("- [")


def _tick_boxes(line: str) -> str:
    return line.replace("- [ ]", "- [x]") if _is_boxes_line(line) else line


def repo_root(start: Path | None = None) -> Path:
    """The repository root: git's answer, or the nearest ancestor holding `specs/`."""
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True, cwd=start)
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        here = (start or Path.cwd()).resolve()
        for cand in (here, *here.parents):
            if (cand / "specs").is_dir():
                return cand
        return here


def spec_dir(root: Path, feature: str) -> Path | None:
    """`specs/<feature>` when that exists, else the ONE `specs/<feature>-*` - None when neither, or several."""
    exact = root / "specs" / feature
    if exact.is_dir():
        return exact
    hits = sorted(p for p in (root / "specs").glob(f"{feature}-*") if p.is_dir()) if (root / "specs").is_dir() else []
    return hits[0] if len(hits) == 1 else None


def tick(text: str, task: str, note: str, boxes: bool = False) -> tuple[str, str]:
    """(the new file text, the ticked task line) - or raises ValueError with the refusal."""
    if not note.strip():
        raise ValueError("the verify note is empty - say what was verified (NOTE=...)")
    lines = text.splitlines(keepends=True)
    open_re = re.compile(rf"^- \[ \] {re.escape(task)}\b")
    done_re = re.compile(rf"^- \[x\] {re.escape(task)}\b")
    start = next((i for i, ln in enumerate(lines) if open_re.match(ln)), None)
    if start is None:
        if any(done_re.match(ln) for ln in lines):
            raise ValueError(f"{task} is already ticked")
        raise ValueError(f"no open task {task} in tasks.md")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith(("- [", "## "))), len(lines))
    block = lines[start:end]
    block[0] = "- [x]" + block[0][len("- [ ]") :]
    # the blank lines that separate this task from a section heading are not part of it
    trail: list[str] = []
    while len(block) > 1 and not block[-1].strip():
        trail.insert(0, block.pop())
    verify_at = next((i for i, ln in enumerate(block) if ln.lstrip().startswith("verify:")), None)
    indent = "      "
    if verify_at is None:
        # a task written without a verify line gets one, after its last line
        if not block[-1].endswith("\n"):
            block[-1] += "\n"
        block.append(f"{indent}verify: DONE. {note.strip()}\n")
    else:
        indent = block[verify_at][: len(block[verify_at]) - len(block[verify_at].lstrip())]
        # the verify text runs to the block's end (it may wrap); it is replaced whole - but NOT the research boxes below it,
        # which are the task's own lines (feature 315: a tick cut T24's and T30's five boxes, and `BOXES=1` then found none)
        block = block[: verify_at + 1] + [ln for ln in block[verify_at + 1 :] if _is_boxes_line(ln)]
        block[verify_at] = f"{indent}verify: DONE. {note.strip()}\n"
    block.extend(trail)
    if boxes:
        ticked = [_tick_boxes(ln) for ln in block]
        # AND IT SAYS SO WHEN IT DOES NOTHING. The failure this replaces was silent: asked to tick the
        # boxes, the script found no line to tick and still reported the task ticked.
        if ticked == block:
            raise SystemExit(f"--boxes: no research-box line found in {block[0].strip()!r} - is this a `research: physical` task?")
        block = ticked
    new = lines[:start] + block + lines[end:]
    return "".join(new), block[0].rstrip("\n")


_WAITS = re.compile(r"^\*\*Waits on\*\*:\s*(\d+)", re.M)


def waits_or_marks(root: Path, d: Path) -> str:
    """Why `make tick` may not tick in `d`, or '' (feature 375, plan D18): its spec waits on a feature still open
    (`**Waits on**: NNN`), or its tasks carry a `[lands-open]` mark the tooling did not put there."""
    todo = _todo()
    spec = d / "spec.md"
    m = _WAITS.search(spec.read_text(encoding="utf-8")) if spec.is_file() else None
    if m:
        other = spec_dir(root, m.group(1))
        if other is not None and todo.feature(other).state != "closed":
            return (f"{d.name} waits on feature {m.group(1)} ({other.name}), which is still open - its spec says "
                    f"`**Waits on**: {m.group(1)}`; take its tasks once that one has closed")
    marks = [ln for ln in todo.holding(d) if "[lands-open] honored only" in ln]
    return ("a [lands-open] mark the tooling did not put here: " + "; ".join(marks)) if marks else ""


def _todo():  # noqa: ANN202 - `speckit-todo.py` by path (its name has a hyphen)
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("speckit_todo", Path(__file__).resolve().parent / "speckit-todo.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    boxes = "--boxes" in argv
    from_env = "--note-from-env" in argv
    args = [a for a in argv if a not in ("--boxes", "--note-from-env")]
    if from_env and len(args) == 2:
        args.append(os.environ.get("TICK_NOTE", ""))
    if len(args) != 3:
        print("usage: tick-task.py <feature> <task> <note> [--boxes]   (make tick F=188 T=T03 NOTE=...)", file=sys.stderr)
        return 2
    feature, task, note = args
    root = repo_root()
    d = spec_dir(root, feature)
    if d is None:
        print(f"tick: no single specs/{feature}* directory under {root}", file=sys.stderr)
        return 2
    path = d / "tasks.md"
    if not path.is_file():
        print(f"tick: {path} does not exist", file=sys.stderr)
        return 2
    # A PLAN'S DECISIONS ARE REVIEWED BEFORE ITS TASKS ARE TICKED (feature 243). Asked before the task is
    # even looked up, so a refused tick writes nothing; the push asks the same question of hand edits.
    sys.path.insert(0, str(Path(__file__).resolve().parent / "gates"))
    import plan_gate as _plan_gate

    permitted, message = _plan_gate.tick_permitted(d, root, os.environ.get("PLAN_REVIEW_OK"))
    if message:
        print(message, file=sys.stderr if not permitted else sys.stdout)
    if not permitted:
        return 2
    refusal = waits_or_marks(root, d)
    if refusal:
        print(f"tick: refused - {refusal}", file=sys.stderr)
        return 2
    try:
        new, line = tick(path.read_text(encoding="utf-8"), task, note, boxes)
    except ValueError as e:
        print(f"tick: refused - {e} ({path})", file=sys.stderr)
        return 2
    path.write_text(new, encoding="utf-8")
    remaining = sum(1 for ln in new.splitlines() if ln.startswith("- [ ] "))
    print(f"ticked {line[:90]}\n{remaining} task(s) still open in {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

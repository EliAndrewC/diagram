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

BOXES = "- [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited"
BOXES_TICKED = BOXES.replace("[ ]", "[x]")


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
        # the verify text runs to the block's end (it may wrap); it is replaced whole
        block = block[: verify_at + 1]
        block[verify_at] = f"{indent}verify: DONE. {note.strip()}\n"
    block.extend(trail)
    if boxes:
        block = [ln.replace(BOXES, BOXES_TICKED) for ln in block]
    new = lines[:start] + block + lines[end:]
    return "".join(new), block[0].rstrip("\n")


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

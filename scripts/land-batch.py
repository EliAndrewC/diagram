#!/usr/bin/env python3
"""Land two or three small engine fixes under ONE gate and ONE landing cohort, then tick each - `make land-batch`.

WHY (feature 385 T117, D135; the GM 2026-10-19, amendment 10: "I would also like to implement all 3 of your suggestions" - the
second, "batch the gate and the landing cohort across two or three small engine fixes"). A gated landing cost about 15 minutes
(`make done` 9.1 min, `make cohort-landing` 4-6 min, the push 2.8 min, measured from the session's transcripts on 2026-10-19),
paid once per engine task, because `make tick` takes one task and its landed check waits for that task's own landing.

    land-batch.py <feature> "<T1 T2 ...>"      (the note from $LAND_NOTE: `make land-batch F= T= NOTE=`)

Every task's tick is asked first, with every refusal `make tick` makes but the landed one; any refusal stops the batch before
anything lands. Then `scripts/sync-with-main.sh done` runs ONCE (the gated route: the green gate, the landing cohort, the claims
gate); on its success each task is ticked `landed in batch T1+T2: <note>`, the landed check now asked of each as `make tick`
asks it. A failed landing ticks none.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _tick_task():  # noqa: ANN202 - `tick-task.py` by path (its name has a hyphen)
    spec = importlib.util.spec_from_file_location("tick_task", HERE / "tick-task.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def land(root: Path) -> int:
    """The gated route, once: `scripts/sync-with-main.sh done` from the clone, its output passed through."""
    return subprocess.run([str(root / "scripts" / "sync-with-main.sh"), "done"], cwd=root).returncode


def main(argv: list[str]) -> int:
    if len(argv) != 2 or len(tasks := argv[1].split()) < 2:
        print('usage: land-batch.py <feature> "<T1 T2 ...>"   (make land-batch F=385 T="T106 T108" NOTE=...) - two tasks or more; one lands by scripts/sync-with-main.sh done', file=sys.stderr)
        return 2
    note = os.environ.get("LAND_NOTE", "").strip()
    if not note:
        print("land-batch: refused - NOTE= is empty; say what was verified, as make tick asks", file=sys.stderr)
        return 2
    tt = _tick_task()
    root = tt.repo_root()
    d = tt.spec_dir(root, argv[0])
    if d is None or not (d / "tasks.md").is_file():
        print(f"land-batch: no single specs/{argv[0]}* directory with a tasks.md under {root}", file=sys.stderr)
        return 2
    text = (d / "tasks.md").read_text(encoding="utf-8")
    stops = []
    for task in tasks:
        try:
            tt.tick(text, task, note)
        except ValueError as e:
            stops.append(f"{task}: {e}")
            continue
        why, _msg = tt.refusal(root, d, task, note, landed=False)
        if why:
            stops.append(f"{task}: {why}")
    if stops:
        print("land-batch: refused before landing - nothing landed, nothing ticked:\n  " + "\n  ".join(stops), file=sys.stderr)
        return 2
    rc = land(root)
    if rc:
        print(f"land-batch: the landing failed (exit {rc}) - no task ticked; fix it and run make land-batch again", file=sys.stderr)
        return rc
    batch = "+".join(tasks)
    failed = [task for task in tasks if tt.main([argv[0], task, f"landed in batch {batch}: {note}"])]
    if failed:
        print(f"land-batch: landed, but {', '.join(failed)} refused its tick (above) - answer it, then make tick", file=sys.stderr)
        return 2
    print(f"land-batch: {batch} landed under one gate and ticked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

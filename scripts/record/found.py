#!/usr/bin/env python3
"""A feature's `found.jsonl`: the findings its checks raised outside the change, each row `open` until it is FILED as a task or
SETTLED with a reason (feature 405 T29: a row filed with `make task-add` or settled kept `open`, so the log could not say what
was unfiled - 385's 63 rows all read open).

    found.py list  --feature <dir>                         every open row, numbered from 1 in file order
    found.py close --feature <dir> --rows 3,7 --task T61   the rows FILED as that task
    found.py close --feature <dir> --rows 4 --why "<reason>"  the rows SETTLED, with the reason

A closed row keeps every field it had and gains `status` (`filed` or `settled`), `task` or `why`, and `closed_utc`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)


def load(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()] if path.is_file() else []


def save(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def open_rows(rows: list[dict]) -> list[tuple[int, dict]]:
    """(1-based row number in the file, row) for every open row."""
    return [(i + 1, r) for i, r in enumerate(rows) if r.get("status", "open") == "open"]


def close(rows: list[dict], numbers: list[int], task: str = "", why: str = "", now: str | None = None) -> int:
    """Close the numbered rows (1-based, file order): filed as `task`, or settled with `why`. Refuses a row already closed."""
    if bool(task) == bool(why):
        raise ValueError("one of --task (filed) or --why (settled)")
    if task and not re.fullmatch(r"(?:\d{3} )?T\d+", task):
        raise ValueError(f"--task names a task id (T61, or 385 T12 for another feature's), not {task!r}")
    if why and len(why.split()) < 3:
        raise ValueError("--why says why the row is settled, three words or more")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for n in numbers:
        if not 1 <= n <= len(rows):
            raise ValueError(f"no row {n} (the file has {len(rows)})")
        if rows[n - 1].get("status", "open") != "open":
            raise ValueError(f"row {n} is already {rows[n - 1]['status']}")
    for n in numbers:
        rows[n - 1].update({"status": "filed", "task": task} if task else {"status": "settled", "why": why}, closed_utc=when)
    return len(numbers)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("verb", choices=("list", "close"))
    ap.add_argument("--feature", required=True, help="the feature's directory (specs/NNN-name)")
    ap.add_argument("--rows", default="")
    ap.add_argument("--task", default="")
    ap.add_argument("--why", default="")
    a = ap.parse_args(argv)
    path = Path(a.feature) / "found.jsonl"
    rows = load(path)
    if a.verb == "list":
        left = open_rows(rows)
        for n, r in left:
            print(f"{n:3d}  {r.get('check', '?')}  {r.get('file', '?')}  {r.get('finding', '')[:160]}")
        print(f"found: {len(left)} open of {len(rows)} row(s) in {path}")
        return 0
    try:
        n = close(rows, [int(x) for x in a.rows.replace(" ", "").split(",") if x], a.task, a.why)
    except ValueError as e:
        print(f"found: refused - {e}", file=sys.stderr)
        return 2
    save(path, rows)
    print(f"found: {n} row(s) {'filed as ' + a.task if a.task else 'settled'} in {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

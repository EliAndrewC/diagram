#!/usr/bin/env python3
"""The GM's review after landing - `make gm-review`, `make gm-reviewed`, `make accept` (feature 375, FR-012, plan D12).

WHY (the GM, 2026-10-10): *"I tend to want things to land on main without needing my review. So that probably does suggest
either a post-feature thing or we allow things to land on main with that and only that category of box unticked. And then
just as we have a make target for our `make speckit-todo` we could have a separate target"*. So a feature lands with its
GM's review still open, and this lists, by feature, what waits on him:

- HELD - work on the item cannot go on until the GM decides: the rows 328's ranking flags `Held` (`audit/overrides.json`);
- TO REVIEW - the work went on and landed, and the GM may overturn it: every round-arbiter ruling and every finding accepted
  with a reason (`specs/NNN/gm-review.jsonl`, written by `make arbiter-ruled` and `make accept`).

A feature with a row of either kind carries ONE box, `- [ ] GM review (make gm-reviewed F=NNN) [lands-open]`, which this
adds; `make speckit-todo` reads such a feature `Done - GM review pending`; `make gm-reviewed F=NNN` marks its rows reviewed
and ticks the box, and `OVERTURN=<row> TO=<feature>` turns a ruling the GM overturns into an open row of that feature.

    gm_review.py list                                   every feature's held and to-review rows
    gm_review.py accept F FINDING REASON                a finding accepted with a reason: a to-review row
    gm_review.py reviewed F [--overturn ROW --to G]     the GM has reviewed F's rows
"""

from __future__ import annotations

import json
import re
import sys
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
    if "GM review (make gm-reviewed" in text:
        return False
    tasks.write_text(text.rstrip("\n") + "\n" + box(d) + "\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n",
                     encoding="utf-8")
    return True


def held(root: Path) -> list[str]:
    """The rows held for the GM today: 328's ranking rows flagged `Held`."""
    f = root / HELD
    data = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    return [f"{k}: {v.get('flag', '')[:160]}" for k, v in sorted(data.items()) if str(v.get("flag", "")).startswith("Held")]


def listing(root: Path) -> str:
    out = []
    hs = held(root)
    if hs:
        out.append(f"HELD - work cannot go on until the GM decides ({len(hs)}, feature 328's ranking, carried by 374)")
        out += [f"  {h}" for h in hs]
    for d in sorted((root / "specs").glob("*/")):
        open_rows = [(i, r) for i, r in enumerate(rows(d)) if "reviewed" not in r]
        if open_rows:
            out.append(f"TO REVIEW - {d.name} (landed; the GM may overturn): make gm-reviewed F={int(d.name.split('-', 1)[0])}")
            out += [f"  [{i}] {r.get('kind')}: {r.get('trigger') or r.get('finding', '')} - {r.get('ruling', 'accepted')}: {r.get('why', '')[:140]}"
                    for i, r in open_rows]
    return "\n".join(out) + "\n" if out else "gm-review: nothing waits on the GM\n"


def accept(d: Path, finding: str, reason: str) -> dict:
    """A finding accepted with a reason - the work goes on, and the GM may overturn it after landing (FR-012)."""
    if len(reason.split()) < 2:
        raise ValueError("REASON needs two words or more - the GM reads it")
    row = {"kind": "accepted", "finding": finding, "why": reason, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with (d / ROWS).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    ensure_box(d)
    return row


def reviewed(root: Path, d: Path, overturn: int | None = None, to: Path | None = None) -> list[str]:
    """The GM has reviewed `d`'s rows: each marked reviewed; an overturned one becomes an open row of the feature `to`; the
    GM-review box is ticked - through the closing check, since it may close the feature (FR-009)."""
    rs = rows(d)
    msgs = []
    if overturn is not None:
        if to is None or not (0 <= overturn < len(rs)):
            raise ValueError("OVERTURN=<row number> needs TO=<an open feature>")
        with (to / "found.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"check": "gm-review", "file": d.name, "block": rs[overturn].get("trigger") or rs[overturn].get("finding"),
                                 "finding": f"overturned by the GM: {rs[overturn].get('why', '')}", "status": "open"}, ensure_ascii=False) + "\n")
        msgs.append(f"row {overturn} overturned - an open row of {to.name}")
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8") if tasks.is_file() else ""
    if box(d) in text and text.count("- [ ] ") == 1:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "gates"))
        import close_check  # noqa: PLC0415

        why = close_check.reasons(d, root / "specs")
        if why:
            raise ValueError("the GM's box closes the feature, and: " + "; ".join(why))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    (d / ROWS).write_text("".join(json.dumps({**r, "reviewed": r.get("reviewed", today)}, ensure_ascii=False) + "\n" for r in rs),
                          encoding="utf-8")
    if box(d) in text:
        tasks.write_text(text.replace(box(d), box(d).replace("- [ ] ", "- [x] ")), encoding="utf-8")
    msgs.append(f"{len(rs)} row(s) of {d.name} reviewed")
    return msgs


def _feature(root: Path, f: str) -> Path:
    hits = sorted((root / "specs").glob(f"{int(f):03d}-*")) if f.isdigit() else [root / "specs" / f]
    if not hits or not hits[0].is_dir():
        raise SystemExit(f"gm-review: no specs/{f}* directory")
    return hits[0]


def main(argv: list[str]) -> int:
    root = Path(".").resolve()
    try:
        if argv[:1] == ["list"]:
            sys.stdout.write(listing(root))
        elif argv[:1] == ["accept"] and len(argv) == 4:
            accept(_feature(root, argv[1]), argv[2], argv[3])
            print("accept: recorded for the GM's review after landing")
        elif argv[:1] == ["reviewed"] and len(argv) in (2, 4):
            ov = int(argv[2]) if len(argv) == 4 else None
            for m in reviewed(root, _feature(root, argv[1]), ov, _feature(root, argv[3]) if len(argv) == 4 else None):
                print(f"gm-reviewed: {m}")
        else:
            print(__doc__.split("\n\n")[-1], file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"gm-review: refused - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

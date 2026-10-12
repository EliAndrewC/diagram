#!/usr/bin/env python3
"""What each review check yields for its cost - feature 375 amendment 8, FR-037 (plan D50).

    python3 scripts/measure/review_yield.py [--since 2026-09-26] [--ledger dev/review-ledger.md] [--record <measurements.json> --key <key>]

Reads the review ledger's measured rows (`| date | check | subject | verdict | finding | class | author missed? | acted on |
wall | tokens |`) from `--since` on - 2026-09-26 is the first full day the rows carry their cost - and prints, per check: its
passes; the passes with a finding, and of those the DISMISSED (the free-text "acted on" cell opens with verified, accepted,
spec/plan accepted, declined, no change, none, nothing, answered, or a bare left), the DEFERRED (put to the GM, left for, not
applied - unless the cell says it was filed, carried or sent to a follow-up, which FR-037 counts as acted on) and the ACTED ON
(any other cell but empty, "-" or "re-dispatched": something changed or was filed - "applied" opens 248 cells and "recorded" 66
since 2026-09-26, so a list of acted-on words would miss most; the plan review found "nothing" in 64); those the author had MISSED (that cell opens yes); its hours (wall) and tokens
written; the features its rows name (a three-digit number in the subject); and its yield - findings acted on per hour. A row
with no wall time is skipped. Sorted by hours. Nothing about a check changes here: the table is put to the GM, whose choice it is.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
DISMISSED = ("verified", "accepted", "spec accepted", "plan accepted", "declined", "no change", "no-change", "none", "nothing", "answered", "left")
DEFERRED = ("put to the gm", "left for", "not applied")
FILED = ("filed", "carried", "follow-up")  # FR-037 counts a finding filed as acted on, whatever the cell opens with
NOT_AN_ACT = ("", "-", "re-dispatched")
_WALL = re.compile(r"(\d+(?:\.\d+)?)\s*s\b")
_OUT = re.compile(r"/\s*([\d.]+)\s*k\s+out")
_FEATURE = re.compile(r"\b(\d{3})\b")


def rows(text: str, since: str) -> list[list[str]]:
    """The measured rows from `since` on, each its ten cells; a row with another count, or no wall time, is not one."""
    out = []
    for line in text.splitlines():
        if not re.match(r"^\| 20\d\d-\d\d-\d\d \|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 10 and cells[0] >= since and _WALL.search(cells[8]):
            out.append(cells)
    return out


def has_finding(cells: list[str]) -> bool:
    return cells[5].lower() not in ("nothing", "-", "") and not cells[4].startswith("- ") and cells[4] not in ("-", "")


def outcome(acted: str) -> str:
    """What became of a finding, from its free-text "acted on" cell: dismissed, deferred, or acted on (something changed)."""
    a = acted.strip().lower()
    if a.split(";")[0].strip() in NOT_AN_ACT:
        return "not acted on"
    if a.startswith(DEFERRED):  # before DISMISSED: "left for the GM" defers, a bare "left" dismisses
        return "deferred" if not any(w in a for w in FILED) else "acted on"
    if a.startswith(DISMISSED):
        return "dismissed"
    return "acted on"


def table(rs: list[list[str]]) -> dict[str, dict[str, Any]]:
    t: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"passes": 0, "with a finding": 0, "acted on": 0, "dismissed": 0, "deferred": 0, "not acted on": 0, "author missed": 0, "hours": 0.0, "k tokens out": 0.0, "features": set()}
    )
    for c in rs:
        r = t[c[1]]
        r["passes"] += 1
        found = has_finding(c)
        r["with a finding"] += found
        if found:
            r[outcome(c[7])] += 1
        r["author missed"] += c[6].lower().startswith("yes")
        r["hours"] += float(_WALL.search(c[8]).group(1)) / 3600  # type: ignore[union-attr]  # rows() kept only rows with one
        k = _OUT.search(c[9])
        r["k tokens out"] += float(k.group(1)) if k else 0.0
        r["features"].update(_FEATURE.findall(c[2]))
    return {
        k: {
            **v,
            "hours": round(v["hours"], 2),
            "k tokens out": round(v["k tokens out"], 1),
            "features": len(v["features"]),
            "acted on per hour": round(v["acted on"] / v["hours"], 1) if v["hours"] else 0.0,
        }
        for k, v in t.items()
    }


def render(t: dict[str, dict[str, Any]], since: str, n: int) -> str:
    cols = ("passes", "with a finding", "acted on", "dismissed", "deferred", "not acted on", "author missed", "hours", "k tokens out", "features", "acted on per hour")
    lines = [f"review yield since {since}: {n} measured rows", "", "| check | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for check, r in sorted(t.items(), key=lambda kv: -kv[1]["hours"]):
        lines.append(f"| {check} | " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--since", default="2026-09-26")
    ap.add_argument("--ledger", default=str(ROOT / "dev" / "review-ledger.md"))
    ap.add_argument("--record", default="")
    ap.add_argument("--key", default="")
    a = ap.parse_args(argv)
    rs = rows(pathlib.Path(a.ledger).read_text(encoding="utf-8"), a.since)
    t = table(rs)
    print(render(t, a.since, len(rs)))
    if a.record:
        if not a.key:
            print("review_yield: --record needs --key", file=sys.stderr)
            return 2
        path = pathlib.Path(a.record)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault(a.key, {})["value"] = {"since": a.since, "rows": len(rs), "by check": t}
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

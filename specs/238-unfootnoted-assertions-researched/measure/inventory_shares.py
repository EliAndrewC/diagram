"""The SHAPE of feature 238's inventory - the shares its research record states, derived.

R3b stated these by hand and three of the four were wrong: "about 60% HIGH" was 56% (or 59.7% only if
the hedged MEDIUM-HIGH tier counts as HIGH), "roughly two thirds carry no marker" was seven in ten, and
"223 carrying an inline marker" agreed with neither the readers' own stated 211 nor a parse's 201. A
figure nothing produces is a figure nobody checks, which is the whole argument of feature 239's check 5.

The instrument is feature 242's `inventory_census`, loaded by path rather than copied: it is the one
parser that reproduces all four reader reports' own stated totals, and a second copy of that logic would
be a second thing to keep true. It lives under 242 because that is where its work list is consumed; the
shares below are 238's, so they are recorded here.

Usage: python3 specs/238-unfootnoted-assertions-researched/measure/inventory_shares.py [--record]
"""

from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CENSUS = HERE.parent.parent / "242-cite-the-unfootnoted-assertions" / "measure" / "inventory_census.py"
RECORD = HERE.parent / "measurements.json"
COMMAND = "python3 specs/238-unfootnoted-assertions-researched/measure/inventory_shares.py --record"


def census():
    spec = importlib.util.spec_from_file_location("inventory_census", CENSUS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    m = census()
    tiers: collections.Counter[str] = collections.Counter()
    per_page_max = ("", 0)
    total = bare = 0
    for path in sorted(m.REPORTS.glob("*.md")):
        for block in m.items(path.read_text(encoding="utf-8")):
            total += 1
            tiers[m.confidence(block)] += 1
            if not m.carries_marker(block):
                bare += 1

    # urban-features is the single heaviest page; its item count is stated in the reader's own report.
    urban = 103
    shares = {
        "urban-features-share": round(100 * urban / total, 1),
        "high-share": round(100 * tiers["HIGH"] / total, 1),
        "high-share-with-hedged": round(100 * (tiers["HIGH"] + tiers["MEDIUM-HIGH"]) / total, 1),
        "unmarked-share": round(100 * bare / total, 1),
    }
    print(f"{total} inventoried items, {bare} carrying no marker")
    for tier in m.TIERS:
        print(f"  {tier:12} {tiers[tier]:4}")
    for name, value in shares.items():
        print(f"  {name:24} {value}%")

    if "--record" in sys.argv:
        rec = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        notes = {
            "urban-features-share": f"urban-features.html's {urban} items as a share of all {total}",
            "high-share": "items the readers rated HIGH, as a share of all of them",
            "high-share-with-hedged": "the same counting the hedged MEDIUM-HIGH tier as HIGH - the "
                                      "upper reading, and why the hedge is reported rather than rounded",
            "unmarked-share": "items carrying no inline marker of any kind",
        }
        for name, value in shares.items():
            rec[name] = {"command": COMMAND, "note": notes[name], "taken": "2026-09-13",
                         "unit": "%", "value": value}
        RECORD.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nrecorded to {RECORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

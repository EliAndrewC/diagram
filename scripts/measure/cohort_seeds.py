#!/usr/bin/env python3
"""Which cohort seeds found which failure, and how few would have found them all - feature 375 amendment 8, FR-038 (plan D51).

    python3 scripts/measure/cohort_seeds.py [--log dev/cohort-log] [--record <measurements.json> --key <key>]

Reads every cohort run's per-seed record (`cohort_audit.write_record`, amendment 7) and prints, per failure (its name, e.g.
`refused:WebRefused`), the seeds that found it and the changes they were rolled on; how many changes the records span; and the
FEWEST FIRST SEEDS that find every failure: the largest, over failures, of the smallest seed that found it. The pinned seeds
(901 on) are rolled every time and left out of that count. A record's change is its `feature`; a record written before that
field is attributed by `features.json` beside the records (commit -> feature), else counted as unattributed, by its commit.
The seed count is the GM's choice with this: ten, and the six pinned (2026-10-12, feature 375 amendment 8); nothing here changes it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
PINNED_FIRST = 901


def load(log: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    names = sorted(p for p in log.glob("*.json") if p.name != "features.json")
    known = json.loads((log / "features.json").read_text(encoding="utf-8")) if (log / "features.json").is_file() else {}
    return [json.loads(p.read_text(encoding="utf-8")) for p in names], known


def change_of(rec: dict[str, Any], known: dict[str, str]) -> str:
    feature = str(rec.get("feature") or known.get(str(rec.get("commit", "")), ""))
    return f"feature {feature}" if feature else f"unattributed ({rec.get('commit', '?')})"


def summary(records: list[dict[str, Any]], known: dict[str, str]) -> dict[str, Any]:
    failures: dict[str, dict[str, set[Any]]] = {}
    changes = set()
    for rec in records:
        change = change_of(rec, known)
        changes.add(change)
        for s in rec.get("seeds", []):
            for f in s.get("failures", []):
                name = f.split("[")[0]
                entry = failures.setdefault(name, {"seeds": set(), "changes": set()})
                entry["seeds"].add(s["seed"])
                entry["changes"].add(change)
    unpinned = [min(x for x in e["seeds"] if x < PINNED_FIRST) for e in failures.values() if any(x < PINNED_FIRST for x in e["seeds"])]
    return {
        "records": len(records),
        "changes": sorted(changes),
        "failures": {k: {"seeds": sorted(v["seeds"]), "changes": sorted(v["changes"])} for k, v in sorted(failures.items())},
        "fewest first seeds finding every failure": max(unpinned) if unpinned else 0,
        "failures only a pinned seed found": sorted(k for k, v in failures.items() if all(x >= PINNED_FIRST for x in v["seeds"])),
    }


def render(s: dict[str, Any]) -> str:
    lines = [f"cohort seeds: {s['records']} record(s) over {len(s['changes'])} change(s): {', '.join(s['changes']) or 'none'}"]
    for name, f in s["failures"].items():
        lines.append(f"  {name}: seeds {', '.join(map(str, f['seeds']))} - on {', '.join(f['changes'])}")
    if not s["failures"]:
        lines.append("  no failures recorded")
    lines.append(
        f"the fewest first seeds that find every failure: {s['fewest first seeds finding every failure']}"
        + (f" (and the pinned rows for {', '.join(s['failures only a pinned seed found'])})" if s["failures only a pinned seed found"] else "")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--log", default=str(ROOT / "dev" / "cohort-log"))
    ap.add_argument("--record", default="")
    ap.add_argument("--key", default="")
    a = ap.parse_args(argv)
    s = summary(*load(pathlib.Path(a.log)))
    print(render(s))
    if a.record:
        if not a.key:
            print("cohort_seeds: --record needs --key", file=sys.stderr)
            return 2
        path = pathlib.Path(a.record)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault(a.key, {})["value"] = s
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

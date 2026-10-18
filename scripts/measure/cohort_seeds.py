#!/usr/bin/env python3
"""Which cohort seeds found which failure, and how few would have found them all - feature 375 amendment 8, FR-038 (plan D51).

    python3 scripts/measure/cohort_seeds.py [--log dev/cohort-log] [--record <measurements.json> --key <key>]

Reads every cohort run's per-seed record (`cohort_audit.write_record`, amendment 7) and prints, per failure (its name, e.g.
`refused:WebRefused`), the seeds that found it and the changes they were rolled on; how many changes the records span; and the
FEWEST FIRST SEEDS that find every failure: the largest, over failures, of the smallest seed that found it. The pinned seeds
(901-906) are rolled every time and left out of that count. A FRESH record (feature 386: the landing cohort's block of 48 seeds
from a start that rotates with the engine, `first_seed` 10000 or more, or marked `"fresh": true`) is left out of all of that -
its seeds are never rolled twice, so they say nothing about how few fixed seeds suffice - and reported as what it is: a failure
RATE, per record and pooled, on seeds the generator was never tuned on. So is a record's own fresh block (each seed marked
`"fresh": true`, rolled beside the fixed seeds by every `make cohort` since feature 386). A record's change is its `feature`; a record written before that
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
#: the pinned rows `cohort_audit` adds to every unscoped roll - six seeds, not "901 on": a fresh seed is far above them (feature 386)
PINNED = frozenset(range(901, 907))
#: where the landing cohort's fresh blocks start (scripts/gates/cohort_gate.py, feature 386)
FRESH_BASE = 10000


def is_fresh(rec: dict[str, Any]) -> bool:
    return bool(rec.get("fresh")) or int(rec.get("first_seed") or 0) >= FRESH_BASE


def fresh_seeds(rec: dict[str, Any]) -> list[dict[str, Any]]:
    """A record's fresh seeds: every unpinned seed of a fresh record, else those marked fresh."""
    return [s for s in rec.get("seeds", []) if s["seed"] not in PINNED and (is_fresh(rec) or s.get("fresh"))]


def fresh_rate(rec: dict[str, Any]) -> dict[str, Any]:
    """A record's failed and rolled fresh seeds."""
    rolled = fresh_seeds(rec)
    bad = [s["seed"] for s in rolled if s.get("failures") or s.get("verdict", "pass") != "pass"]
    return {
        "utc": rec.get("utc", "?"),
        "commit": rec.get("commit", "?"),
        "first_seed": min((x["seed"] for x in rolled), default=rec.get("first_seed")),
        "failed": len(bad),
        "rolled": len(rolled),
        "seeds": bad,
    }


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
    fresh = [fresh_rate(r) for r in records if fresh_seeds(r)]
    for rec in (r for r in records if not is_fresh(r)):
        change = change_of(rec, known)
        changes.add(change)
        for s in (x for x in rec.get("seeds", []) if not x.get("fresh")):
            for f in s.get("failures", []):
                name = f.split("[")[0]
                entry = failures.setdefault(name, {"seeds": set(), "changes": set()})
                entry["seeds"].add(s["seed"])
                entry["changes"].add(change)
    unpinned = [min(x for x in e["seeds"] if x not in PINNED) for e in failures.values() if any(x not in PINNED for x in e["seeds"])]
    return {
        "records": len(records),
        "changes": sorted(changes),
        "failures": {k: {"seeds": sorted(v["seeds"]), "changes": sorted(v["changes"])} for k, v in sorted(failures.items())},
        "fewest first seeds finding every failure": max(unpinned) if unpinned else 0,
        "failures only a pinned seed found": sorted(k for k, v in failures.items() if all(x in PINNED for x in v["seeds"])),
        "fresh": fresh,
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
    fresh = s.get("fresh") or []
    lines.append(f"fresh seeds (feature 386 - a rate on seeds never tuned on, never a refusal): {len(fresh)} record(s)")
    for f in fresh:
        lines.append(
            f"  {f['utc']} {f['commit']} from {f['first_seed']}: {f['failed']} of {f['rolled']} failed ({100 * f['failed'] / max(f['rolled'], 1):.0f}%)"
            + (f" - seeds {', '.join(map(str, f['seeds']))}" if f["seeds"] else "")
        )
    if fresh:
        k, n = sum(f["failed"] for f in fresh), sum(f["rolled"] for f in fresh)
        lines.append(f"  pooled: {k} of {n} failed ({100 * k / max(n, 1):.0f}%)")
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

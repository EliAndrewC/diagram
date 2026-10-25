#!/usr/bin/env python3
"""How often a seed nobody has used fails, by settlement form and by cause - feature 417 T01 (plan D2, D8; FR-001).

    python3 scripts/measure/fresh_tally.py [--log dev/cohort-log] [--commit <sha prefix>] [--since <UTC stamp>]

WHY. The fixed cohort passes because it is the landing gate; the generator's real failure rate is on seeds it was never tuned
on (feature 417's gap: 360 of 2,544 since 2026-10-20). `make cohort-seeds` prints that rate per record; this pools it: every
record's fresh seeds (`cohort_seeds.fresh_seeds` - a fresh block, or every unpinned seed of a roll started at or above
`FRESH_BASE`), each seed counted once per engine commit (the latest record wins: a seed rolled twice on one engine rolled the
same map), then the failed share overall, by form (`form`) and by cause (each name in `failures`; a seed may fail more than
one). `--commit` keeps the records of one engine commit; `--since` those at or after a UTC stamp (`20261024T000000Z`).
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys
from collections import Counter
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def _cohort_seeds() -> Any:
    spec = importlib.util.spec_from_file_location("cohort_seeds", HERE / "cohort_seeds.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = _cohort_seeds()


def failed(seed: dict[str, Any]) -> bool:
    return bool(seed.get("failures")) or seed.get("verdict", "pass") != "pass"


def cause(name: Any) -> str:
    """A failure's cause without its count: `lane_knots 2` and `lane_knots` are one cause."""
    return str(name if isinstance(name, str) else (name or {}).get("check", name)).split(" ")[0]


def pooled(records: list[dict[str, Any]], commit: str = "", since: str = "") -> dict[tuple[str, int], dict[str, Any]]:
    """Each fresh seed once per engine commit, from the latest record that rolled it."""
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for rec in sorted(records, key=lambda r: str(r.get("utc", ""))):
        if commit and not str(rec.get("commit", "")).startswith(commit):
            continue
        if since and str(rec.get("utc", "")) < since:
            continue
        for seed in cs.fresh_seeds(rec):
            out[(str(rec.get("commit", "")), int(seed["seed"]))] = seed
    return out


def tally(seeds: list[dict[str, Any]]) -> dict[str, Any]:
    forms: dict[str, list[int]] = {}
    causes: Counter[str] = Counter()
    for s in seeds:
        row = forms.setdefault(str(s.get("form") or "?"), [0, 0])
        row[1] += 1
        if failed(s):
            row[0] += 1
            causes.update({cause(f) for f in s.get("failures") or ["verdict " + str(s.get("verdict"))]})
    return {"failed": sum(1 for s in seeds if failed(s)), "rolled": len(seeds), "forms": forms, "causes": causes}


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "-"


def render(t: dict[str, Any]) -> str:
    lines = [f"fresh seeds: {t['failed']} of {t['rolled']} failed ({pct(t['failed'], t['rolled'])})", "", "by form:"]
    lines += [f"  {form:11} {n} of {m} ({pct(n, m)})" for form, (n, m) in sorted(t["forms"].items(), key=lambda kv: -kv[1][1])]
    lines += ["", "by cause (a seed may fail more than one):"]
    lines += [f"  {n:5}  {name}" for name, n in t["causes"].most_common()] or ["  none"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--log", type=pathlib.Path, default=ROOT / "dev" / "cohort-log")
    ap.add_argument("--commit", default="")
    ap.add_argument("--since", default="")
    a = ap.parse_args(argv)
    records, _ = cs.load(a.log)
    print(render(tally(list(pooled(records, a.commit, a.since).values()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""How many rounds a clone's pop-up checks took - feature 375 amendment 3, SC-012 (`m:375-a3-popup-rounds-before`).

WHY. Amendment 3 orders a pop-up's checks (form, research, depiction) and lets a later check's applied edits settle the
earlier ones, as a speculative fix measured afterwards (the GM, 2026-10-11). The baseline was counted from the kept dispatch
records of two clones; this script is that count, kept, so the after is counted by the same method.

    python3 scripts/measure/popup_rounds.py <clone> [--since <ISO time>] [--json]

It reads `<clone's git dir>/checks-open.json` (the record checks' state, `scripts/hooks/lib/hm_checks.py`): every dispatch of
`modal-form`, `modal-research` or `modal-depiction`, each counted once per pop-up it names. A UNIT is a (pop-up, check) pair;
its rounds are its dispatches. `--since` counts only dispatches at or after a time (the next wave's start).
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import subprocess
import sys
from collections.abc import Iterable, Mapping
from typing import Any

MODAL_CHECKS = ("modal-form", "modal-research", "modal-depiction")


def counts(dispatches: Iterable[Mapping[str, Any]], since: float = 0.0) -> dict[str, Any]:
    """Units, dispatches, dispatches per unit, and the units with a second and a third round, overall and per check."""
    n: collections.Counter[tuple[str, str]] = collections.Counter()
    for d in dispatches:
        if d.get("check") in MODAL_CHECKS and float(d.get("t", 0)) >= since:
            for subject in d.get("subjects", []):
                n[(subject, d["check"])] += 1

    def row(values: list[int]) -> dict[str, Any]:
        return {"units": len(values), "dispatches": sum(values), "per unit": round(sum(values) / len(values), 2) if values else 0.0,
                "units with a 2nd round": sum(v >= 2 for v in values), "units with a 3rd": sum(v >= 3 for v in values)}

    out = row(list(n.values()))
    out["pop-ups"] = len({s for s, _c in n})
    out["by check"] = {c: row([v for (_s, cc), v in n.items() if cc == c]) for c in MODAL_CHECKS if any(cc == c for _s, cc in n)}
    return out


def state_of(clone: pathlib.Path) -> dict[str, Any]:
    p = subprocess.run(["git", "-C", str(clone), "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False)
    common = pathlib.Path(p.stdout.strip() or ".git")
    path = (common if common.is_absolute() else clone / common) / "checks-open.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("clone")
    ap.add_argument("--since", default="", help="count only dispatches at or after this ISO time")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    since = datetime.datetime.fromisoformat(args.since).timestamp() if args.since else 0.0
    state = state_of(pathlib.Path(args.clone))
    c = counts(state.get("dispatches", {}).values(), since)
    if args.json:
        print(json.dumps(c, indent=1))
        return 0
    print(f"popup-rounds: {state.get('feature', '?')}: {c['dispatches']} dispatches over {c['units']} units ({c['per unit']} per unit), "
          f"{c['units with a 2nd round']} with a second round, {c['units with a 3rd']} with a third; {c['pop-ups']} pop-ups")
    for check, r in c["by check"].items():
        print(f"  {check}: {r['dispatches']} over {r['units']} ({r['per unit']}), {r['units with a 2nd round']} second, {r['units with a 3rd']} third")
    return 0


if __name__ == "__main__":
    sys.exit(main())

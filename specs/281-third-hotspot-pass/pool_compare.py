"""Feature 281, SC-011's second half: each live pool hamlet's manifest at the base against the working tree's.

    python3 specs/281-third-hotspot-pass/pool_compare.py [base commit]

Reads the committed manifests with `git show` and the regenerated ones from disk - no engine run. Per map: households
seated and any shortfall, the settlement form, the headman's house, the house kinds, the paddies and their area, the ways
and their length, and the marsh's recorded outlines - what 276's FR-006 condition asks a moved map to keep.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOL = Path(".claude/skills/diagram/pool/hamlets")
MAPS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")


def _area(poly: list) -> float:
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2


def summary(M: dict) -> dict:
    houses = [h for h in M.get("houses") or [] if isinstance(h, dict)]
    meta = M.get("meta") or {}
    lanes = M.get("lanes") or []
    plots = M.get("plots") or M.get("paddies") or []
    return {
        "households": len(houses),
        "shortfall": meta.get("households_short") or meta.get("shortfall") or 0,
        "form": meta.get("form") or meta.get("settlement_form") or ("nucleated" if meta.get("nucleated") else None),
        "headman": sum(1 for h in houses if h.get("headman") or h.get("kind") == "headman"),
        "kinds": dict(Counter(str(h.get("kind") or h.get("type") or "house") for h in houses)),
        "plots": len(plots),
        "plot_area": round(sum(_area(p["poly"]) for p in plots if isinstance(p, dict) and len(p.get("poly") or []) >= 3)),
        "ways": len(lanes),
        "way_len": round(sum(math.dist(a, b) for ln in lanes for a, b in zip(ln.get("pts") or [], (ln.get("pts") or [])[1:], strict=False))),
        "marshes": len(M.get("marshes") or []),
    }


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "c13a6ebe6"
    out = {}
    for m in MAPS:
        rel = POOL / m / f"{m}.json"
        before = json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{base}:{rel}"], check=True, capture_output=True, text=True).stdout)
        after = json.loads((ROOT / rel).read_text())
        out[m] = {"before": summary(before), "after": summary(after)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

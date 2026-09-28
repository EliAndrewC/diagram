"""The pool hamlets' counts FR-006 is judged on, read from their committed manifests.

    python3 specs/276-engine-hotspots-and-test-scans/pool_counts.py [OUT.json]

With no argument it compares against `pool-before.json` (written by this same reading on the unmodified engine's
manifests) and prints each hamlet as SAME or with its differences; with an argument it also writes the counts there.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POOL = HERE.parents[1] / ".claude" / "skills" / "diagram" / "pool" / "hamlets"


def counts(manifest: Path) -> dict:
    m = json.loads(manifest.read_text())
    houses = m.get("houses", [])
    kinds: dict[str, int] = {}
    for h in houses:
        kinds[h.get("kind", "?")] = kinds.get(h.get("kind", "?"), 0) + 1
    return {
        "houses": len(houses),
        "house_kinds": kinds,
        "nucleated": bool(m.get("meta", {}).get("nucleated")),
        "paddy_plots": sum(len(f.get("plots", [])) for f in m.get("fields", []) if isinstance(f, dict)),
        "flooded_plots": len(m.get("flooded_plots", [])),
        "dry_plots": len(m.get("dry_plots", [])),
        "lanes": len(m.get("lanes", [])),
        "households_asked": m.get("meta", {}).get("households"),
    }


def main() -> int:
    before = json.loads((HERE / "pool-before.json").read_text())
    now = {name: counts(POOL / name / f"{name}.json") for name in before}
    for name, row in now.items():
        diff = {k: (before[name][k], row[k]) for k in row if before[name].get(k) != row[k]}
        print(name, "SAME" if not diff else diff)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(now, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Feature 287's scope, joined by owning placer - re-runnable from the three census files.

    python3 specs/287-placer-guarantees/scope_join.py   # writes scope-by-owner.json beside it

R1 `census.json` (every map-rule row, the 118 - FR-001 takes them all, not only the unguarded), R2 `fallbacks.json` (the
`breaks-rule` rows; `town-only` rows are recorded, not converted), R3 `excused.json` (the `in` rows not `fixed`). A row's
owner is its `owner` (R1, R3) or its `where` (R2), reduced to the module path.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _module(s: str | None) -> str:
    s = (s or "?").replace("l7r/diagram/", "")
    m = re.search(r"([a-z_/]+\.py)", s)
    return m.group(1) if m else s[:40]


def main() -> None:
    by: dict[str, list[list[str]]] = {}
    for r in json.loads((HERE / "census.json").read_text()):
        if r["kind"] == "map-rule":
            by.setdefault(_module(r.get("owner")), []).append(["R1", r["test"].split("::")[-1], str(r.get("guaranteed"))])
    for r in json.loads((HERE / "fallbacks.json").read_text()):
        if r["compromise"] == "breaks-rule":
            by.setdefault(_module(r.get("where")), []).append(["R2", str(r.get("what")), "breaks"])
    for r in json.loads((HERE / "excused.json").read_text()):
        if r["verdict"] == "in" and r.get("still_open") != "fixed":
            by.setdefault(_module(r.get("owner")), []).append(["R3", str(r.get("what")), str(r.get("still_open"))])
    (HERE / "scope-by-owner.json").write_text(json.dumps(dict(sorted(by.items())), indent=1) + "\n")


if __name__ == "__main__":
    main()

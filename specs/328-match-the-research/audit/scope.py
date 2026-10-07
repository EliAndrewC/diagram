"""Which ranked rows feature 328 fixes (amendment 8, the GM 2026-10-07): the code a scripted hamlet runs, and the Mode A
procedures and sheets (magistracies, country shrines - permanently drawn by hand); the code only the legacy hand-authored
villages, towns and cities run is DEFERRED - ranked, never taken by a wave.

    python3 specs/328-match-the-research/audit/scope.py <hamlet module list> <ranking.json> <out scope.json>

A row is in scope when its file is
  - on the hamlet path: the module set `tools/hamlet_floor.module_set` derives from the pool's scripted rolls (passed in as a
    file, one path per line, as `make test-file` can write it), or anywhere under `l7r/diagram/hamletgen/`;
  - a Mode A file: `buildings.md`, `buildings/**`, the compound placer (`compound*.py`);
  - or its own unit (the function or method the key names) is called from `hamletgen/` code - a shared helper a hamlet
    reaches though the pool's five rolls do not (`edge_seat`, the shrine `hill`).
Two name matches are struck by hand because they hit only comments (`roll_village`, the castle's `wall`).
"""

from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[3] / ".claude" / "skills" / "diagram"
FALSE_HITS = {"roll_village", "wall"}  # named in hamletgen comments only, never called


def scope_of(key: str, mods: set[str], hamletgen: str) -> str:
    path, unit = key.split("::", 1)
    path = path.replace(".claude/skills/diagram/", "")
    name = unit.split("#")[0].split(".")[-1]
    if path.startswith("buildings") or "compound" in path:
        return "mode-a"
    if path in mods or path.startswith("l7r/diagram/hamletgen/"):
        return "hamlet"
    if name not in FALSE_HITS and re.search(r"\b" + re.escape(name) + r"\(", hamletgen):
        return "hamlet"
    return "deferred"


def main(argv: list[str]) -> int:
    mods = {line.strip() for line in Path(argv[1]).read_text().splitlines() if line.strip()}
    hamletgen = "".join(Path(f).read_text() for f in glob.glob(str(SKILL / "l7r/diagram/hamletgen/**/*.py"), recursive=True))
    rows = json.loads(Path(argv[2]).read_text())
    out = {r["key"]: scope_of(r["key"], mods, hamletgen) for r in rows}
    Path(argv[3]).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print({s: sum(1 for r in rows if not r["wave"] and out[r["key"]] == s) for s in ("hamlet", "mode-a", "deferred")})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

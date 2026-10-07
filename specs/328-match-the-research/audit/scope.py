"""Which ranked rows feature 328 fixes (amendment 8, the GM 2026-10-07): the code a scripted hamlet runs, and the Mode A
procedures and sheets (magistracies, country shrines - permanently drawn by hand); the code only the legacy hand-authored
villages, towns and cities run is DEFERRED - ranked, never taken by a wave.

    python3 specs/328-match-the-research/audit/scope.py <hamlet module list> <ranking.json> <out scope.json>

A row is in scope when its file is
  - on the hamlet path: the module set `tools/hamlet_floor.module_set` derives from the pool's scripted rolls (passed in as a
    file, one path per line, as `make test-file` can write it), or anywhere under `l7r/diagram/hamletgen/`;
  - a Mode A file: `buildings.md`, `buildings/**`, the compound placer (`compound*.py`);
  - or its own unit (the function or method the key names), or any function of its module, is called from `hamletgen/` code -
    a shared helper a hamlet reaches though the pool's five rolls do not (`edge_seat`, the shrine `hill`, `grove_rules`).
Two name matches are struck by hand because they hit only comments (`roll_village`, the castle's `wall`), and three modules
that match only through a common helper name (`FALSE_MODULES`).
"""

from __future__ import annotations

import functools
import glob
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[3] / ".claude" / "skills" / "diagram"
FALSE_HITS = {"roll_village", "wall"}  # named in hamletgen comments only, never called
# modules matched only through a common helper name (`ring(`, `_blocked(`): the castle and city wall code and the legacy village
# roller, which no scripted hamlet runs
FALSE_MODULES = {"l7r/diagram/settlement/castle_civic.py", "l7r/diagram/settlement/city/walls.py", "l7r/diagram/settlement/rolling/roll.py"}


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
    if path in called_modules(hamletgen) and path not in FALSE_MODULES:
        return "hamlet"
    return "deferred"


@functools.cache
def called_modules(hamletgen: str) -> set[str]:
    """The settlement modules `hamletgen/` calls into: a module any of whose top-level functions or methods `hamletgen/` code
    calls by name (a constant beside them, `grove_rules.EAST_REACH_PX`, is the same module's), the comment-only hits struck."""
    import ast

    out: set[str] = set()
    for f in glob.glob(str(SKILL / "l7r/diagram/settlement/**/*.py"), recursive=True):
        rel = str(Path(f).relative_to(SKILL))
        try:
            tree = ast.parse(Path(f).read_text())
        except SyntaxError:
            continue
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith("__") and len(n.name) > 3}
        if any(nm not in FALSE_HITS and re.search(r"\b" + re.escape(nm) + r"\(", hamletgen) for nm in names):
            out.add(rel)
    return out


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

"""Which code feature 328 fixes (amendment 8, the GM 2026-10-07): the code the kept maps actually EXECUTE - the scripted
hamlets, the magistracies and the country shrines - and the Mode A procedures; code only the legacy hand-authored villages,
towns and cities run is DEFERRED: ranked, never taken by a wave, and shown DEFERRED by `make claims-report`.

    python3 specs/328-match-the-research/audit/scope.py <skill dir> <ranking.json> <claims-index.json> <scope.json> <claims-deferred.json>

THE MEASURE IS THE EXECUTION RECORD, not a name: each KEPT map's own gen-cache entry (`KEPT_MAPS`: the pool hamlets, the
magistracy sheets, the country shrine; taken on today's engine with `make map`) records each function that RAN as
`(path, qualname)`, the record `tools/hamlet_floor` reads. No other entry counts: `.gencache/rolls` holds the gate's tests of
the legacy village roller, unit tests' rolls and stale rolls of older code. A unit is in scope when
  - it is a Mode A procedure (`buildings.md`, `buildings/**`);
  - it is under `hamletgen/` - the scripted hamlet's own code, which only a scripted hamlet (any seed, any form) runs;
  - it is a function or method a recorded run executed;
  - it is a class one of whose methods a recorded run executed;
  - it is a module-level constant an executed function of the engine reads by name;
  - it is a check the gate runs against the kept maps' finished output (`KEPT_CHECKS`, each with its reason).
Everything else is DEFERRED. The deferred list (`claims-deferred.json`) is derived over EVERY claimed unit, not only the units
with a finding today, so a legacy-only unit that drifts later reads DEFERRED too; re-run this when a wave lands or the pool
gains a kept map (the cache must hold each kept map's entry - `make map GEN=<gen>`).
"""

from __future__ import annotations

import ast
import glob
import json
import sys
from pathlib import Path


KEPT_MAPS = (
    "pool/hamlets/*/*.gen.py",  # the scripted hamlets
    "pool/magistracies/*/*.gen.py",  # the magistracy sheets
    "pool/country-shrines/*/*.gen.py",  # the country shrine
)


def executed(skill: Path) -> set[tuple[str, str]]:
    """Every `(path, qualname)` a kept map's own gen-cache entry records as executed - never a gate test's roll (the legacy
    village roller's), a unit test's, or an entry of the code as it stood weeks ago (`.gencache/rolls`, `h10`, `h20`)."""
    out: set[tuple[str, str]] = set()
    entries = [skill / ".gencache" / Path(g).name[: -len(".gen.py")] / "meta.json" for pat in KEPT_MAPS for g in glob.glob(str(skill / pat))]
    for meta in (str(e) for e in entries if e.is_file()):
        deps = json.loads(Path(meta).read_text()).get("deps") or {}
        out |= {(str(p), str(q)) for p, q, *_ in deps.get("functions", []) if q != "<module>"}
    return out


def names_read(skill: Path, ran: set[tuple[str, str]]) -> set[str]:
    """Every bare or attribute name the executed functions read."""
    by_file: dict[str, set[str]] = {}
    for p, q in ran:
        by_file.setdefault(p, set()).add(q)
    out: set[str] = set()
    for p, quals in by_file.items():
        try:
            tree = ast.parse((skill / p).read_text())
        except (OSError, SyntaxError):
            continue

        def walk(node: ast.AST, prefix: str, quals: set[str] = quals) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    q = f"{prefix}{child.name}"
                    if not isinstance(child, ast.ClassDef) and q in quals:
                        out.update(n.id for n in ast.walk(child) if isinstance(n, ast.Name))
                        out.update(n.attr for n in ast.walk(child) if isinstance(n, ast.Attribute))
                    walk(child, q + ".")

        walk(tree, "")
    return out


KEPT_CHECKS = {
    # a check the gate and `tools/cohort_audit` run against the scripted hamlets' finished maps (tests/gate/test_farm_groves.py),
    # so no generation record holds it though the kept maps are what it judges
    "l7r/diagram/settlement/homestead_parts/grove_rules.py::gardens_east_shaded",
}


def scope_of(uid: str, ran: set[tuple[str, str]], read: set[str]) -> str:
    path, unit = uid.split("::", 1)
    path = path.replace(".claude/skills/diagram/", "")
    if path.startswith("buildings"):
        return "mode-a"
    if f"{path}::{unit}" in KEPT_CHECKS or path.startswith("l7r/diagram/hamletgen/"):
        return "kept"  # hamletgen/ is the scripted hamlet's own code: no legacy map reaches it, whatever seed or form runs it
    if (path, unit) in ran or any(p == path and q.startswith(unit + ".") for p, q in ran):
        return "kept"
    if unit.replace("_", "").isupper():
        return "kept" if unit in read else "deferred"
    return "deferred"


def main(argv: list[str]) -> int:
    skill, ranking, index, out_scope, out_deferred = (Path(a) for a in argv[1:6])
    ran = executed(skill)
    read = names_read(skill, ran)
    rows = json.loads(ranking.read_text())
    scope = {r["key"]: scope_of(r["key"].rsplit("#", 1)[0], ran, read) for r in rows}
    out_scope.write_text(json.dumps(scope, indent=1, sort_keys=True) + "\n")
    uids = sorted({k.rsplit("#", 1)[0] for k in json.loads(index.read_text())})
    deferred = [u for u in uids if u.split("::")[0].endswith(".py") and scope_of(u, ran, read) == "deferred"]
    doc = json.loads(out_deferred.read_text()) if out_deferred.is_file() else {}
    doc |= {"why": doc.get("why", "feature 328 amendment 8"), "units": deferred}
    out_deferred.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(ran)} executed functions; open rows by scope:", {s: sum(1 for r in rows if not r["wave"] and scope[r["key"]] == s) for s in ("kept", "mode-a", "deferred")}, f"; {len(deferred)} of {len(uids)} claimed units deferred")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

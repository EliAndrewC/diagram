"""Feature-family census: what one manifest records that another does not.

WHY (feature 134, GM 2026-08-27): *"when I look at Kuwabata I do not See many of the features which
we have incorporated into our reference hamlet. For example, I do not see bamboo groves, and the
sheds look like the old style sheds."* The conversion of a hand-authored map to the scripted
generator owes the GM a MEASURED answer to "does it carry every family the reference hamlet does?",
not an impression from the render. A family here is a manifest key that records something (a
non-empty list or a set value), plus the KINDS inside the keys whose records carry one - farmstead
fixtures, sheds, groves, marshes, bamboo stands - so "privy present, bath present, woodpile absent"
is visible, not only "farm_fixtures present".

A diagnostic OBSERVES (tools/CLAUDE.md): it prints what each manifest records and the difference,
and it says nothing about whether an absence is right. That judgment - archetype reason and research
pointer per absence - is the feature's to record (spec 134 "Decisions Recorded").

    make family-census A=pool/hamlets/inashiro.json B=pool/hamlets/kuwabata.json
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Keys that are drawing bookkeeping or the sheet's furniture, not features a reader sees on the map.
_NOT_FAMILIES = frozenset({"meta", "labels", "title", "scalebar", "water_bed_zmax", "water_sheen_zmin", "pond_layer", "lane"})

# Where a record carries a KIND worth listing, which field names it.
_KIND_FIELDS: dict[str, tuple[str, ...]] = {
    "farm_fixtures": ("kind",),
    "farm_sheds": ("kind", "form", "role"),
    "village_groves": ("role",),
    "marshes": ("role",),
    "bamboo_stands": ("role",),
    "land_use": ("overlay",),
    "channels": ("role",),
    "field_ditches": ("role",),
}


def families(manifest: dict[str, Any]) -> dict[str, set[str]]:
    """Every recorded family -> the set of kinds inside it ('*' when the records carry no kind)."""
    out: dict[str, set[str]] = {}
    for key, val in manifest.items():
        if key in _NOT_FAMILIES or not val:
            continue
        kinds: set[str] = set()
        if isinstance(val, list) and key in _KIND_FIELDS:
            for rec in val:
                if isinstance(rec, dict):
                    for f in _KIND_FIELDS[key]:
                        if rec.get(f):
                            kinds.add(str(rec[f]))
                            break
        out[key] = kinds or {"*"}
    return out


def census(a: dict[str, Any], b: dict[str, Any]) -> dict[str, list[str]]:
    """Families (and kinds, as `family:kind`) present in A and absent in B, and the reverse."""
    fa, fb = families(a), families(b)

    def flat(f: dict[str, set[str]]) -> set[str]:
        return {k for k in f} | {f"{k}:{kind}" for k, ks in f.items() for kind in ks if kind != "*"}

    sa, sb = flat(fa), flat(fb)
    return {"only_a": sorted(sa - sb), "only_b": sorted(sb - sa), "both": sorted(sa & sb)}


def report(a_path: Path, b_path: Path) -> str:
    a = json.loads(a_path.read_text())
    b = json.loads(b_path.read_text())
    c = census(a, b)
    na, nb = a.get("meta", {}).get("name", a_path.stem), b.get("meta", {}).get("name", b_path.stem)
    lines = [f"family census: A = {na} ({a_path}), B = {nb} ({b_path})", f"  in both: {len(c['both'])} families/kinds"]
    lines.append(f"  in {na} only ({len(c['only_a'])}):" + ("" if c["only_a"] else " none"))
    lines += [f"    - {x}" for x in c["only_a"]]
    lines.append(f"  in {nb} only ({len(c['only_b'])}):" + ("" if c["only_b"] else " none"))
    lines += [f"    - {x}" for x in c["only_b"]]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--a", required=True, help="the reference manifest (json)")
    ap.add_argument("--b", required=True, help="the manifest to compare (json)")
    args = ap.parse_args(list(argv) if argv is not None else None)
    print(report(Path(args.a), Path(args.b)))
    return 0


if __name__ == "__main__":  # pragma: no cover - the make target is the entry point
    raise SystemExit(main())

"""Feature 287's census selection, re-runnable (FR-008): every test that asserts on a generated map.

    python3 specs/287-placer-guarantees/census_select.py > specs/287-placer-guarantees/census-raw.txt

A test is selected when it lives where finished-map tests live (`tests/gate/`, `tests/full/`, `tests/soak/`, a
`tests/hamletgen/test_pool_*.py` file) or when its body reads a roll, a pool map or a generated sheet (the pattern below).
Left out, on purpose: `tests/tooling/` and every `pipeline/` directory (the cache and the gate's own machinery - they roll
maps to test caching, not to test what a map draws). Prints `file::name | docstring start`, sorted, one per line.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parents[2] / ".claude" / "skills" / "diagram"
READS_A_MAP = re.compile(r"rolled_map|rolled_report|_manifest\(|rollcache|\bGENS\b|pool_manifest|_pool\.|cohort\(|generate\(|poolmaps|compound\.place|\bplace\(PROGRAM|mode_a|\.gen\.py")


def main() -> int:
    out: list[str] = []
    for p in sorted((SKILL / "tests").rglob("test_*.py")):
        rel = p.relative_to(SKILL)
        if "tooling" in rel.parts or "pipeline" in rel.parts:
            continue
        whole = any(d in rel.parts for d in ("gate", "full", "soak")) or p.name.startswith("test_pool_")
        src = p.read_text()
        lines = src.split("\n")
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
                body = "\n".join(lines[n.lineno - 1 : n.end_lineno])
                if whole or READS_A_MAP.search(body):
                    doc = " ".join((ast.get_docstring(n) or "").split())[:160]
                    out.append(f"{rel}::{n.name} | {doc}")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

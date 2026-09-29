"""The commons' mark counts on the five pool maps, read from their SVGs (feature 278, FR-008's density check).

    python3 specs/278-second-hotspot-pass/commons_marks.py OUT.json

Blades are the subpaths of the `<g stroke="#A7A860">` groups (one `M` each); brush dots carry `#94A063`; pine trunks
`#7A6A48`. Written before the vectorized scatter lands (the maps then still draw the base's marks) and after it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

POOL = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "diagram" / "pool" / "hamlets"
BLADES = re.compile(r'<g stroke="#A7A860" stroke-width="[0-9.]+">(.*?)</g>', re.S)


def counts(svg: str) -> dict[str, int]:
    return {"blades": sum(g.count("M") for g in BLADES.findall(svg)), "dots": svg.count("#94A063"), "pines": svg.count("#7A6A48")}


if __name__ == "__main__":
    out = {m: counts((POOL / m / f"{m}.svg").read_text()) for m in ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out))

#!/usr/bin/env python3
"""Feature 368 item 1: the privy figures on 0047's drawing page, re-derived from the five pool hamlets as drawn today.

Usage: privy_reach.py > privy-reach.txt

Reads each pool hamlet's recorded manifest (`pool/hamlets/<name>/<name>.json`; the project reads derived data from the
manifest, never by re-running a generator) - one foot a unit (`meta.ftpx` 1.0). For every privy in `farm_fixtures` (its
`of` is its house's position):
- its center and its house's center (each `x + w/2`, `y + h/2`; rotation, a few degrees, ignored);
- the distance between them, and whether it is beyond 45 ft;
- its bearing from its house in the HOUSE's frame (its `rot` taken off; 0 = the back, +y the sunny front - the frame of
  `fixture_seats.py`), and whether it lies in the sunny-side sector, 112.5 to 202.5 degrees, which that code seats in;
- whether its center is nearer ANOTHER house's center than its own (center to center - a reader's "whose is it").
Then one row per map and a total, in the drawing page's columns.
"""

import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
SECTOR = (112.5, 202.5)


def center(o: dict) -> tuple[float, float]:
    return o["x"] + o["w"] / 2, o["y"] + o["h"] / 2


def row(name: str) -> dict:
    d = json.loads((ROOT / "pool" / "hamlets" / name / f"{name}.json").read_text())
    assert d["meta"].get("ftpx", 1.0) == 1.0, f"{name}: not one foot a unit"
    houses = [h for h in d["houses"]]
    by_pos = {(round(h["x"], 1), round(h["y"], 1)): h for h in houses}
    out = {"privies": 0, "sunny": 0, "nearer_other": 0, "beyond_45": 0}
    for f in d.get("farm_fixtures", []):
        if f.get("kind") != "privy" or not f.get("of"):
            continue
        own = by_pos.get((round(f["of"][0], 1), round(f["of"][1], 1)))
        if own is None:
            continue
        px, py = center(f)
        hx, hy = center(own)
        dist = math.hypot(px - hx, py - hy)
        rot = math.radians(own.get("rot") or 0.0)
        # into the house's unturned frame, where +y is the sunny front; bearing clockwise from -y (the back)
        dx, dy = px - hx, py - hy
        ux, uy = dx * math.cos(-rot) - dy * math.sin(-rot), dx * math.sin(-rot) + dy * math.cos(-rot)
        bearing = (math.degrees(math.atan2(ux, -uy)) + 360) % 360
        others = [math.hypot(px - center(h)[0], py - center(h)[1]) for h in houses if h is not own]
        out["privies"] += 1
        out["sunny"] += SECTOR[0] <= bearing <= SECTOR[1]
        out["nearer_other"] += bool(others) and min(others) < dist
        out["beyond_45"] += dist > 45.0
    return out


names = sorted(p.name for p in (ROOT / "pool" / "hamlets").iterdir() if (p / f"{p.name}.json").is_file())
total = {"privies": 0, "sunny": 0, "nearer_other": 0, "beyond_45": 0}
print("| map | privies seated | in the sunny sector | nearer another house | beyond 45 ft |")
print("|---|---|---|---|---|")
for n in names:
    r = row(n)
    for k in total:
        total[k] += r[k]
    print(f"| {n} | {r['privies']} | {r['sunny']} ({r['sunny'] / max(r['privies'], 1):.1%}) | {r['nearer_other']} | {r['beyond_45']} |")
t = total
print(f"| all five | {t['privies']} | {t['sunny']} ({t['sunny'] / max(t['privies'], 1):.1%}) | {t['nearer_other']} | {t['beyond_45']} |")

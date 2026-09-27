#!/usr/bin/env python3
"""The measurements behind feature 261 - read from the pool manifests, never by re-rolling.

    python3 specs/261-northwest-wind-by-default/measure.py

Per scripted hamlet: its recorded wind and wind source, households seated against declared, whether the seat
fell back off the wind, the windbreak's clump count, and the bearing from the house cluster's center to the
belt's center in COMPASS degrees (0 = north, 315 = northwest), with its angle off the windward bearing.
"""

from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.normpath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram", "pool", "hamlets"))
COMPASS = {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}


def compass(dx: float, dy: float) -> float:
    """Screen vector (y down) to a compass bearing."""
    return math.degrees(math.atan2(dx, -dy)) % 360.0


def main() -> None:
    for name in sorted(os.listdir(POOL)):
        path = os.path.join(POOL, name, f"{name}.json")
        if not os.path.exists(path):
            continue
        m = json.load(open(path))
        meta = m["meta"]
        hs = m["houses"]
        cx, cy = sum(h["x"] for h in hs) / len(hs), sum(h["y"] for h in hs) / len(hs)
        belt = [c for g in m["village_groves"] if g["role"] == "windbreak" for c in g["clumps"]]
        line = f"{name:10} wind={meta.get('windward')} source={meta.get('wind_source')} houses={len(hs)}/{meta['households']} offwind={meta.get('seat_offwind')} belt={len(belt)}"
        if belt:
            b = compass(sum(c[0] for c in belt) / len(belt) - cx, sum(c[1] for c in belt) / len(belt) - cy)
            off = abs((b - COMPASS[meta["windward"]] + 180.0) % 360.0 - 180.0)
            # the ARC the belt subtends around its own cluster: 360 less the widest empty gap between clump bearings
            angs = sorted(compass(c[0] - cx, c[1] - cy) for c in belt)
            gap = max([b2 - b1 for b1, b2 in zip(angs, angs[1:], strict=False)] + [angs[0] + 360.0 - angs[-1]])
            line += f" belt-bearing={b:.0f} off-wind={off:.0f} arc={360.0 - gap:.0f}"
        # the side of its field the hamlet stands on: from the field outline's mean vertex to the houses' middle
        field = [p for f in m.get("fields") or [] for p in f.get("outline") or []]
        if field:
            line += f" field-to-houses={compass(cx - sum(p[0] for p in field) / len(field), cy - sum(p[1] for p in field) / len(field)):.0f}"
        print(line)


if __name__ == "__main__":
    main()

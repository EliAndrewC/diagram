"""DOES A OVERLAP B - asked once, not for the twelfth time (feature 149, US2).

WHY THIS EXISTS. Across features 150's T50-T55 the same point-in-polygon script was hand-written twelve
times: is a farmhouse on marsh, is a garden on the reed fringe, does a parcel lie across its ditch, is
reed INK drawn over a mulberry bank, does haze wash over open water. Each rewrite cost a model turn and
carried the risk of measuring the wrong thing - and twice it did, reading vertices where the answer needed
the run sampled (the shipped fix records both).

THE INK HALF IS NOT OPTIONAL. Half the questions those features asked were about MARKS, not records: a
tint circle centered a foot outside a pond rim still paints 27 ft of haze over the water, and no manifest
knows that. So the families split in two - RECORDED geometry read from the manifest, and DRAWN ink read
from the SVG beside it, each mark measured by its own reach.

WHAT IT IS NOT: a gate. It never decides what ships; it answers a question and names its offenders. A
family whose inputs a map does not carry reports `unmeasured`, never `0` - a zero that means "I could not
look" is the failure mode this tool exists to remove.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
from typing import Any

from l7r.diagram.settlement._geom import point_in_poly, seg_dist

# The drawn marks, by the ink they are made of and the reach each has from its own point (feature 150
# T54: a keep-out that reads a mark's CENTER lets its body lap the thing it is supposed to keep off).
INK = {
    "marsh tint": (re.compile(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)" fill="#9FBBAE"'), None),
    "marsh glint": (re.compile(r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)"[^>]*fill="#C2D6CE"'), 4.6),
}
# A BLADE IS A LINE, NOT A DISC. Read with both ends: a reed blade leans up from its base, so a disc of
# its length round the base reports ink over water that is drawn away from it - measured on Kuwabata,
# one tuft beside the inlet, reported four times (once per blade) at 0.5 px inside a threshold the
# engine's own keep-out already satisfies. The segment is the honest question and the engine's own shape.
BLADE = re.compile(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"')
FOOTPRINT_KEYS = ("houses", "gardens", "threshing_yards", "farm_sheds", "byres", "farm_fixtures", "wells", "persimmons", "kosatsuba", "pig_sties", "duck_pens")
WATER_KEYS = ("streams", "channels", "field_ditches", "drawn_channels")
FAMILIES = ("footprints-water", "footprints-marsh", "parcels-channels", "ink-mounds", "ink-water")


def _pts(rec: Any) -> list[tuple[float, float]]:
    """A record's outline, whatever key it keeps it under; a rect record is read as its four corners."""
    for key in ("poly", "pts", "outline", "bank", "water"):
        if isinstance(rec, dict) and rec.get(key):
            return [(float(x), float(y)) for x, y in rec[key]]
    if isinstance(rec, dict) and "x" in rec:
        x, y = float(rec["x"]), float(rec["y"])
        w = float(rec.get("w", rec.get("r", 0.0)) or 0.0)
        h = float(rec.get("h", rec.get("d", w)) or w)
        return [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
    return []


def _bands(M: dict[str, Any], intake: bool = True) -> list[tuple[list[tuple[float, float]], float]]:
    """Every drawn watercourse as (polyline, half-width) - records AND the drawn strokes.

    `intake=False` drops the SOURCE HAIRLINE, the channel whose `to` is the field itself. It is excluded
    from the parcel family and from nothing else: the gate REQUIRES that channel to end inside the crop
    (`channel_field_anchored` wants its mouth >= 10 px in, "so the field paints over the end"), so on a
    comb field, whose plots tile the fan, the last stretch necessarily lies over a plot - measured, every
    comb map in the pool has exactly one such plot. Reporting it would be a permanent false positive, and
    a diagnostic that cries wolf on every map is one nobody reads.
    """
    out = []
    for key in WATER_KEYS:
        for rec in M.get(key) or []:
            if not intake and isinstance(rec, dict) and (rec.get("to") or {}).get("kind") == "field":
                continue
            pts = _pts(rec)
            if len(pts) >= 2:
                w = max(float(rec.get("w", 0) or 0), float(rec.get("w0", 0) or 0), float(rec.get("w1", 0) or 0), 2.5)
                out.append((pts, w / 2))
    return out


def _marks(svg: str) -> list[tuple[str, float, float, float]]:
    """Every drawn marsh mark as (kind, x, y, reach) - a disc round its point, for the symmetric marks."""
    out: list[tuple[str, float, float, float]] = []
    for kind, (pat, reach) in INK.items():
        for m in pat.finditer(svg):
            g = m.groups()
            out.append((kind, float(g[0]), float(g[1]), float(g[2]) if reach is None else reach))
    return out


def _blades(svg: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Every reed blade as the SEGMENT it is drawn as, base to tip."""
    grouped = "".join(re.findall(r'<g stroke="#6E9377" stroke-width="0.8">(.*?)</g>', svg, re.S))
    return [((float(a), float(b)), (float(c), float(d))) for a, b, c, d in BLADE.findall(grouped)]


def _hits_band(pts: list[tuple[float, float]], bands: list[tuple[list[tuple[float, float]], float]], pad: float = 0.0, step: float = 2.0) -> tuple[float, float] | None:
    """Where this shape meets a channel band (+ pad), or None.

    BOTH DIRECTIONS, and it has to be: a stream nine feet wide runs BETWEEN a farmhouse's corners, so a
    test that only asks "is a corner in the water" reports a clean map. That vertex-only trap has now been
    walked three times in this engine - twice inside feature 150 (the T55 parcel clip and the polder
    probe's first cut) and once here, caught by this tool's own test.
    """
    for q in pts:
        for line, hw in bands:
            for i in range(len(line) - 1):
                if seg_dist(q[0], q[1], line[i], line[i + 1]) < hw + pad:
                    return (round(q[0]), round(q[1]))
    if len(pts) >= 3:  # ...and the band's own run against the shape
        for line, hw in bands:
            for i in range(len(line) - 1):
                a, b = line[i], line[i + 1]
                n = max(1, int(math.dist(a, b) / step))
                for k in range(n + 1):
                    x, y = a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n
                    for off in (-hw - pad, 0.0, hw + pad):
                        dx, dy = b[0] - a[0], b[1] - a[1]
                        ln = math.hypot(dx, dy) or 1.0
                        if point_in_poly(x - dy / ln * off, y + dx / ln * off, pts):
                            return (round(x), round(y))
    return None


def _inside_any(q: tuple[float, float], polys: list[list[tuple[float, float]]], pad: float = 0.0) -> bool:
    """Is the point inside any polygon - or, with a pad, within `pad` of one's edge (a mark's own reach)?"""
    for poly in polys:
        if point_in_poly(q[0], q[1], poly):
            return True
        if pad and min(seg_dist(q[0], q[1], poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))) <= pad:
            return True
    return False


def _crossed_by(ring: list[tuple[float, float]], bands: list[tuple[list[tuple[float, float]], float]], step: float = 3.0, floor: float = 1.0) -> tuple[int, int] | None:
    """Where a channel RUNS THROUGH this parcel - entering and leaving - or None.

    A channel that enters and STOPS is not a defect: the source hairline's mouth is required to end inside
    the crop (`channel_field_anchored` wants it >= 10 px in, "so the field paints over the end"), and on
    the reference hamlet it lies 15 px inside a paddy by design. Only a run that goes in one side and out
    the other is the T55 defect - a ditch carried through a holding. A run that never gets `floor` px past
    the outline is the third case: a ditch drawn ALONG a plot edge, which is where the fabric puts it.
    """
    for line, _hw in bands:
        pts: list[tuple[float, float]] = []
        for i in range(len(line) - 1):
            a, b = line[i], line[i + 1]
            n = max(1, int(math.dist(a, b) / step))
            pts += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
        pts.append((line[-1][0], line[-1][1]))
        inside = [point_in_poly(q[0], q[1], ring) for q in pts]
        if not any(inside):
            continue
        first, last = inside.index(True), len(inside) - 1 - inside[::-1].index(True)
        if first == 0 or last == len(inside) - 1:
            continue  # the run reaches an END of the channel: a mouth, not a crossing
        deep = max(min(seg_dist(q[0], q[1], ring[j], ring[(j + 1) % len(ring)]) for j in range(len(ring))) for q, ins in zip(pts, inside, strict=True) if ins)
        if deep >= floor:
            q = pts[(first + last) // 2]
            return (round(q[0]), round(q[1]))
    return None


def audit(M: dict[str, Any], svg: str | None, families: tuple[str, ...] = FAMILIES) -> dict[str, Any]:
    """Every requested family's offenders. `unmeasured` where this map carries none of the inputs."""
    out: dict[str, Any] = {}
    bands = _bands(M)
    marsh = [_pts(m) for m in M.get("marshes") or []]
    mounds = [_pts(d) for d in M.get("dikes") or []] + [_pts(p) for p in M.get("dikeponds") or []]
    foots = [(k, rec) for k in FOOTPRINT_KEYS for rec in (M.get(k) or []) if isinstance(rec, dict)]
    rings = [[(float(x), float(y)) for x, y in r] for f in M.get("fields") or [] for r in f.get("plot_rings") or []]
    pond = M.get("pond")

    def record(name: str, inputs: bool, hits: list[Any]) -> None:
        out[name] = {"status": "unmeasured", "hits": []} if not inputs else {"status": "ok" if not hits else "FAIL", "hits": hits}

    if "footprints-water" in families:
        record("footprints-water", bool(foots and bands), [(k, at) for k, rec in foots for at in [_hits_band(_pts(rec), bands)] if at])
    if "footprints-marsh" in families:
        record("footprints-marsh", bool(foots and marsh), [(k, (round(p[0]), round(p[1]))) for k, rec in foots for p in _pts(rec) if _inside_any(p, marsh)][:200])
    if "parcels-channels" in families:
        field_bands = _bands(M, intake=False)
        hits = [(f"plot {idx}", at) for idx, ring in enumerate(rings) for at in [_crossed_by(ring, field_bands)] if at]
        record("parcels-channels", bool(rings and field_bands), hits)
    if "ink-mounds" in families:
        marks = _marks(svg) if svg else []
        hits = [(kind, (round(x), round(y))) for kind, x, y, reach in marks if _inside_any((x, y), mounds, reach)]
        hits += [("reed blade", (round(a[0]), round(a[1]))) for a, b in _blades(svg or "") if _inside_any(a, mounds) or _inside_any(b, mounds)]
        record("ink-mounds", bool((marks or svg) and mounds), hits[:200])
    if "ink-water" in families:
        marks = _marks(svg) if svg else []
        hits = []
        for kind, x, y, reach in marks:
            if pond and ((x - pond[0]) / (pond[2] + reach)) ** 2 + ((y - pond[1]) / (pond[3] + reach)) ** 2 < 1.0:
                hits.append((kind, (round(x), round(y)), "pond"))
            elif _hits_band([(x, y)], bands, reach):
                hits.append((kind, (round(x), round(y)), "channel"))
        for a, b in _blades(svg or ""):  # both ends of the blade itself, not a disc round its base
            if pond and any(((q[0] - pond[0]) / pond[2]) ** 2 + ((q[1] - pond[1]) / pond[3]) ** 2 < 1.0 for q in (a, b)):
                hits.append(("reed blade", (round(a[0]), round(a[1])), "pond"))
            elif _hits_band([a, b], bands):
                hits.append(("reed blade", (round(a[0]), round(a[1])), "channel"))
        record("ink-water", bool((marks or svg) and (bands or pond)), hits[:200])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="does A overlap B, on a finished map (feature 149)")
    ap.add_argument("manifest", help="pool/<tier>/<map>.json - the SVG beside it is read for the ink families")
    ap.add_argument("--families", default=",".join(FAMILIES), help=f"comma-separated: {', '.join(FAMILIES)}")
    a = ap.parse_args(argv)
    man = pathlib.Path(a.manifest)
    M = json.loads(man.read_text())
    svg_path = man.with_suffix(".svg")
    svg = svg_path.read_text() if svg_path.exists() else None
    res = audit(M, svg, tuple(f.strip() for f in a.families.split(",")))
    bad = False
    for name, r in res.items():
        if r["status"] == "unmeasured":
            print(f"  {name:20s} \033[2munmeasured\033[0m - this map carries none of its inputs")
            continue
        if r["status"] == "ok":
            print(f"  {name:20s} \033[32mok\033[0m")
            continue
        bad = True
        print(f"  {name:20s} \033[1;31mFAIL\033[0m {len(r['hits'])} hit(s): {r['hits'][:4]}")
    if svg is None:
        print("  (no SVG beside the manifest - the ink families could not be read)")
    return 1 if bad else 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.tools.overlap_audit")
    raise SystemExit(main())

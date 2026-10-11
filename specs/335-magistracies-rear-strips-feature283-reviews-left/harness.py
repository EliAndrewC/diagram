"""Feature 335's measurement harness: the hand sheets' doors, Hayakawa's landing steps and each sheet's arches.

    make spec-harness SPEC=specs/335-magistracies-rear-strips-feature283-reviews-left OUT=<json>

Run as a test node (the engine refuses in-process calls outside make). Nothing is changed. Per hand sheet:

- every `data-kind="door"` rect against the building it opens through (the built footprint it overlaps most, or the
  nearest one): INSIDE (wholly within it, the 0117 rule's flush door), STRADDLE (across its wall line) or OUTSIDE (a
  slab standing outside the wall) - with the share of the door's area inside;
- Hayakawa's landing steps (`data-id="landing-steps"`) against the revetment rect: how far they run past the
  revetment's river face (east) and past its land face (west);
- every `data-kind="torii"` group: IN PLAN (it declares the `id="arch"` bounding rect docs/buildings.md asks of a
  plan arch) or SILHOUETTE (lines only, no arch rect).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from l7r.diagram.tools.pack_audit.parse import parse_svg

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h335.json")
SHEETS = (
    "pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.svg",
    "pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg",
    "pool/magistracies/ubame-magistracy/ubame-magistracy.svg",
    "pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg",
)


def _overlap(a, b) -> float:
    w = min(a.x2, b.x2) - max(a.x, b.x)
    h = min(a.y2, b.y2) - max(a.y, b.y)
    return max(w, 0.0) * max(h, 0.0)


def _gap(a, b) -> float:
    dx = max(b.x - a.x2, a.x - b.x2, 0.0)
    dy = max(b.y - a.y2, a.y - b.y2, 0.0)
    return (dx * dx + dy * dy) ** 0.5


def doors(text: str) -> list[dict]:
    plan = parse_svg(text)
    ds = [r for r in plan.fills if plan.label_kinds.get(r.pos) == "door"]
    dpos = {d.pos for d in ds}
    hosts = [s for s in plan.structures if s.pos not in dpos and s.area_px > 4 * 30]
    out = []
    for d in ds:
        host = max(hosts, key=lambda s: (_overlap(d, s), -_gap(d, s)))
        share = _overlap(d, host) / d.area_px if d.area_px else 0.0
        form = "INSIDE" if share > 0.99 else "OUTSIDE" if share < 0.01 else "STRADDLE"
        line = text.count("\n", 0, d.pos) + 1
        out.append({"line": line, "x": d.x, "y": d.y, "w": d.w, "h": d.h, "form": form, "inside_share": round(share, 2), "host": [host.x, host.y, host.w, host.h]})
    return out


def steps(text: str) -> dict | None:
    m = re.search(r'data-id="landing-steps">\s*<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"', text)
    r = re.search(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"[^>]*data-kind="revetment"', text)
    if not (m and r):
        return None
    sx, sw, rx, rw = (float(v) for v in (*m.groups(), *r.groups()))
    return {"steps_x": [sx, sx + sw], "revetment_x": [rx, rx + rw], "past_river_face_px": max(sx + sw - (rx + rw), 0.0), "past_land_face_px": max(rx - sx, 0.0)}


def arches(text: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<g[^>]*data-kind="torii"[^>]*>(.*?)</g>', text, re.S):
        out.append({"line": text.count("\n", 0, m.start()) + 1, "form": "IN PLAN" if 'id="arch"' in m.group(1) else "SILHOUETTE"})
    return out


def test_measure() -> None:
    res = {}
    for rel in SHEETS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        ds = doors(text)
        res[rel] = {
            "doors": ds,
            "door_counts": {f: sum(1 for d in ds if d["form"] == f) for f in ("INSIDE", "STRADDLE", "OUTSIDE")},
            "steps": steps(text),
            "arches": arches(text),
        }
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")


EXAMPLE = "pool/magistracies/county-magistracy-example/county-magistracy-example.svg"


def caption_moves(text: str, tol: float = 1.0) -> list[dict]:
    """Feature 340: the example sheet's captions as `compound.py` seated them, against where `hand_sheet.placed` - the
    one placer reading the sheet as the hand sheets are read - seats the same declarations. A caption whose first line
    moves more than `tol` px is a disagreement."""
    from l7r.diagram import compound as C
    from l7r.diagram.labels.hand_sheet import placed

    del text
    program = C.county_magistracy_program()
    src = C.emit_svg(program, C.place(program))
    pat = re.compile(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*data-kind="([^"]+)"[^>]*>(.*?)</text>', re.S)
    before = [(float(m.group(1)), float(m.group(2)), m.group(3), re.sub(r"<[^>]+>", " ", m.group(4)).split()) for m in pat.finditer(src)]
    after = [(float(m.group(1)), float(m.group(2)), m.group(3), re.sub(r"<[^>]+>", " ", m.group(4)).split()) for m in pat.finditer(placed(src))]
    out = []
    for b, a in zip(before, after, strict=True):
        d = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        if d > tol:
            out.append({"kind": b[2], "text": " ".join(b[3]), "from": b[:2], "to": a[:2], "moved_px": round(d, 1)})
    return out


def test_caption_moves() -> None:
    res = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    res["caption_moves"] = caption_moves("")
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")

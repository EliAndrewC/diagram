"""The farmstead grove's rules, read off a FINISHED map's manifest (feature 291, plan D7).

Feature 126 measured four defects in the per-house grove - on a lane, on the lee side, shading a garden's morning sun,
over a byre - and feature 166 then retired the check battery that had measured them, so a cohort roll's own verdict no
longer saw any of them. The overlaps are the matrix's (`overlap.matrix_violations`, which classifies `groves` as
VEGETATION against every structure and lane). These three are the rest, pure functions of the manifest, run by
`tools/cohort_audit` on every roll and by the gate on every pool roll whose farms carry their own grove:

- `grove_sides_missing`: every farm of a non-nucleated map carries a band on every face its settlement rolled
  (FR-010: no farm on fewer sides);
- `groves_off_windward`: every deep band stands on a windward face, on that side of its own house;
- `gardens_east_shaded`: no grove band stands hard against a garden's east across its height (the reach
  `_east_trees` reads).

Each returns the offending records, empty when the map keeps the rule - and says what it FOUND, so a caller can assert
the rule was not vacuous (`grove_farms`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .grove_sides import grove_faces

EAST_REACH_PX = 22.0  # at the village grain; scaled by the map's `bscale` (`_east_trees`)

Pt = tuple[float, float]


def _key(p: Sequence[float]) -> Pt:
    return (round(float(p[0]), 1), round(float(p[1]), 1))


def grove_farms(M: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """The farms that carry their own grove: every house whose homestead bundle was laid with one (a dispersed or linear
    map's farmsteads; a nucleated map has none, a ruin no bundle)."""
    return [h for h in M.get("houses") or () if (h.get("geom") or {}).get("groves")]


def expected_faces(meta: Mapping[str, Any]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """(deep faces, thin faces) the map's recorded wind, side count and flank call for."""
    deep, thin, _front = grove_faces(str(meta.get("windward", "NW")), int(meta.get("grove_sides", 2)), int(meta.get("grove_flank", -1)))
    return set(deep), set(thin)


def _bands_by_farm(M: Mapping[str, Any]) -> dict[Pt, list[Mapping[str, Any]]]:
    out: dict[Pt, list[Mapping[str, Any]]] = {}
    for g in M.get("groves") or ():
        if g.get("of"):
            out.setdefault(_key(g["of"]), []).append(g)
    return out


def grove_sides_missing(M: Mapping[str, Any]) -> list[tuple[Pt, list[tuple[int, int]]]]:
    """Each farm whose drawn grove lacks a face its settlement rolled, as (farm, the faces missing)."""
    meta = M.get("meta") or {}
    if meta.get("settlement_form", "nucleated") == "nucleated" or meta.get("grove_sides") is None:
        return []
    deep, thin = expected_faces(meta)
    bands = _bands_by_farm(M)
    out: list[tuple[Pt, list[tuple[int, int]]]] = []
    for h in grove_farms(M):
        drawn = {tuple(g["face"]) for g in bands.get(_key((h["x"], h["y"])), ())}
        missing = sorted((deep | thin) - drawn)
        if missing:
            out.append((_key((h["x"], h["y"])), missing))
    return out


def groves_off_windward(M: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Each deep band on a face the wind does not blow on, or not on that side of its own house."""
    meta = M.get("meta") or {}
    if meta.get("grove_sides") is None:
        return []
    deep, _thin = expected_faces(meta)
    out = []
    for g in M.get("groves") or ():
        if g.get("depth", "deep") != "deep" or not g.get("of"):
            continue
        face = tuple(g["face"])
        dx, dy = g["x"] - g["of"][0], g["y"] - g["of"][1]
        if face not in deep or (face[0] and dx * face[0] <= 0) or (face[1] and dy * face[1] <= 0):
            out.append(g)
    return out


def gardens_east_shaded(M: Mapping[str, Any]) -> list[tuple[Pt, Mapping[str, Any]]]:
    """Each (garden, band) where a grove band's west edge stands within the east reach of the garden's east edge and
    overlaps its height - the garden's morning sun cut off."""
    meta = M.get("meta") or {}
    bscale = 1.0 / float(meta.get("ftpx", 1.0)) if meta.get("toscale") else 1.0
    reach = EAST_REACH_PX * bscale
    out = []
    for gd in M.get("gardens") or ():
        gx1 = gd["x"] + gd["w"] / 2
        gy0, gy1 = gd["y"] - gd["h"] / 2, gd["y"] + gd["h"] / 2
        for g in M.get("groves") or ():
            west = g["x"] - g["w"] / 2
            if gx1 - 2 <= west < gx1 + reach and g["y"] - g["h"] / 2 < gy1 and gy0 < g["y"] + g["h"] / 2:
                out.append((_key((gd["x"], gd["y"])), g))
    return out

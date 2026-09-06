"""Scatter audit (feature 108) - adjudicate drawn ground-cover BASES against the engine's keep-outs.

The manifest does not record scatter (each tuft is draw-time ink), so the rendered SVG is the only
source of truth for where ground cover actually stands - which is why the 2026-08-16 cut-bank
review had to hand-build this parse across ~21 tool uses. This script is that parse made permanent:
it extracts every scatter base point from a pool map's SVG and tests each against the SAME keep-out
geometry the engine's scatter skips at draw time.

OBSERVE-DON'T-RESTATE (diagram CLAUDE.md "A DIAGNOSTIC that restates what it observes will lie to
you, or die"): the keep-outs are obtained by executing the ENGINE'S OWN code on the recorded
manifest - `Settlement._watercourse_segs(..., channel_margin=px(_BANK_MARGIN_FT))` for water + the
irrigation cut-bank margin, and the manifest's `fields[].outline` + `dry_plots[].poly` padded by
`Settlement._CROP_MARGIN_FT` through the same `boxed_*` helpers the scatter uses. No margin rule is
re-implemented here, so a future rule change moves this audit's verdicts automatically.

Families: blade / dot / pine / crown are adjudicated; reed is REPORT-ONLY (reeds are the water
fringe by doctrine - research/vegetation.html). Bases only - blade TIPS may lean a few real feet by
the disclosed departure. Zero bases parsed is a LOUD failure (exit 2), never a clean pass: a
styling drift in the engine's emission must read as "the audit is broken", not "the map is clean".

CLI contract (exit 0 clean / 1 violations / 2 unusable):
specs/108-review-loop-efficiency/contracts/scatter-audit-cli.md.
"""

from __future__ import annotations

import re

from l7r.diagram.settlement._geom import CROWN_FILLS

Base = tuple[float, float]

_NUM = r"(-?[\d.]+)"
# Anchors are the engine's exact emission styling (the grass bucket in settlement/land/cover.py, the
# reed bucket in settlement/land/wet.py; research.md R2). Attribute
# order is stable because one code path emits each family.
_BLADE_GROUP = re.compile(r'<g stroke="#A7A860"[^>]*>(.*?)</g>', re.S)  # commons grass bucket
_REED_GROUP = re.compile(r'<g stroke="#6E9377"[^>]*>(.*?)</g>', re.S)  # marsh reed bucket
_LINE_BASE = re.compile(rf'<line x1="{_NUM}" y1="{_NUM}"')  # a blade/reed line's root
_TRANSLATE_G = re.compile(rf'<g transform="translate\({_NUM},{_NUM}\)[^"]*"[^>]*>')  # grove clumps draw their canopy in a translated group
_DOT = re.compile(rf'<circle cx="{_NUM}" cy="{_NUM}" r="[\d.]+" fill="#94A063"')  # brush dot
_PINE = re.compile(rf'<line x1="{_NUM}" y1="{_NUM}" x2="{_NUM}" y2="{_NUM}" stroke="#7A6A48"')  # trunk (branches are #6E8452 - canopy ink, not a base)
# THE CROWN FILLS COME FROM THE ENGINE, not from a copy here (2026-08-17). This pattern used to
# hardcode #6E8B4A / #7C9856 / #87A45C - none of which the engine has painted for some time - so the
# audit parsed ZERO crowns on maps recording thousands and still reported "crown checked". A family
# that sees nothing looks exactly like a family with nothing wrong, which is the same shape as a
# check that never runs, one level down inside the tool reviewers quote as evidence.
_CROWN = re.compile(rf'<circle cx="{_NUM}" cy="{_NUM}" r="{_NUM}" fill="(?:{"|".join(c.lstrip("#") and re.escape(c) for c in CROWN_FILLS)})"')

# Coordinate-quantization slack: the engine adjudicates scatter at full float precision and then
# WRITES the SVG at %.1f, so a base the engine legally seated a hair outside a keep-out can parse
# back a few hundredths INSIDE it. 0.15 px is the same slack the engine's own margin unit tests
# use (tests/settlement/test_homestead_parts.py); a real defect stands whole pixels deep.


def _translated_spans(svg: str) -> list[tuple[int, int, float, float]]:
    """Every `<g transform="translate(tx,ty)">...</g>` span, as (start, end, tx, ty).

    Nested groups are not produced by this engine's emitters, so a flat scan of matched pairs is
    enough; a span is closed at the first `</g>` after its opening tag."""
    spans: list[tuple[int, int, float, float]] = []
    for m in _TRANSLATE_G.finditer(svg):
        end = svg.find("</g>", m.end())
        spans.append((m.end(), len(svg) if end < 0 else end, float(m.group(1)), float(m.group(2))))
    return spans


def parse_bases(svg: str, families: tuple[str, ...] | None = None) -> dict[str, list[Base]]:
    """Every scatter BASE point per family, in document order, in WORLD coordinates.

    Most element coords already are world coords - `crop_to_content` crops via the viewBox and never
    rewrites coordinates, which `crop_map.py` relies on too. But GROVE CLUMPS are not: `_draw_grove`
    emits its canopy inside `<g transform="translate(cx,cy)">`, so a crown's `cx`/`cy` are LOCAL to
    the clump. Reading them raw put a crown at world (710.9, 1815.8) on the map at (4.9, -14.2).

    THE COUNT GUARD COULD NOT SEE THAT, which is the transferable half (settlement-review, Mizuguchi
    2026-08-18). `tests/tools/test_scatter_audit.py` asserted `parsed >= recorded`, and 1,446 >= 1,446
    passed while ~78% of the crown family was being adjudicated in the wrong place - the audit
    reported 0 violations on a map that really had 5 crown bases inside the crop margin. A coverage
    guard that counts is blind to a family that sees the right NUMBER of things somewhere else; the
    guard is positional now, and this parser resolves the transform."""
    fams: dict[str, list[Base]] = {"blade": [], "dot": [], "pine": [], "crown": [], "reed": []}
    want = set(families) if families else set(fams)  # `families` limits the parse to the ones asked for (a crown guard need not scan 220k blades)
    for group, fam in ((_BLADE_GROUP, "blade"), (_REED_GROUP, "reed")):
        if fam not in want:
            continue
        for body in group.findall(svg):
            fams[fam] += [(float(x), float(y)) for x, y in _LINE_BASE.findall(body)]
    if "dot" in want:
        fams["dot"] = [(float(x), float(y)) for x, y in _DOT.findall(svg)]
    if "pine" in want:
        fams["pine"] = [(float(x), float(y)) for x, y, _, _ in _PINE.findall(svg)]
    if "crown" not in want:
        return fams
    spans = _translated_spans(svg)

    def _offset(at: int) -> tuple[float, float]:
        for lo, hi, tx, ty in spans:
            if lo <= at < hi:
                return tx, ty
        return 0.0, 0.0

    for m in _CROWN.finditer(svg):
        ox, oy = _offset(m.start())
        fams["crown"].append((float(m.group(1)) + ox, float(m.group(2)) + oy))
    return fams

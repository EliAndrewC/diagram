"""The check REGISTRY (feature 254, D5): every pass/fail question the audit asks of a Mode A sheet, with
the building types it applies to, the red fixture that proves it fires, and the compliant fix its
failure names.

WHY A REGISTRY. The GM (2026-09-19): "some of those automated checks will likely just be the same for
all types of buildings, like whether different shapes end up overlapping with each other, and some of
them may be specific to individual building types." A check is shared when `types` is None and the
type's own when it lists tiers; the sweep (`tests/test_mode_a_sheets.py`) runs each sheet through the
checks whose types cover its tier, the report prints them in this order, and a test holds every row
to its fixture: a check with no red fixture, or one that does not fire on it, is not merged.

The measured figures that are NOT pass/fail (the vacant rectangles, the per-region density, the
aligned gaps) stay the report's and are not registered; coverage and hugging ARE (the plan review of
2026-09-19 ruled the spec names them as checks).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ...buildings.types import BuildingType
from . import checks as c
from . import shared as s
from .grids import FTPX
from .parse import ParsedPlan

MAGISTRACY = "magistracies"
SHRINE = "country-shrines"
BOTH = frozenset({MAGISTRACY, SHRINE})


@dataclass(frozen=True)
class Context:
    """What a check is handed: the parsed sheet, its source text, its declared type and its notes' form."""

    plan: ParsedPlan
    text: str = ""
    btype: BuildingType | None = None
    form: str | None = None


@dataclass(frozen=True)
class Check:
    name: str
    run: Callable[[Context], list[str]]
    types: frozenset[str] | None  # None = the shared layer, every sheet
    fixture: str  # a red fixture under tests/fixtures/ on which the check FIRES
    fix: str  # the compliant fix a failure prints

    def applies_to(self, tier: str | None) -> bool:
        return self.types is None or tier in self.types


def _tub_adrift(ctx: Context) -> list[str]:
    return [f"tub at svg({t.x:.0f},{t.y:.0f}) is {t.gap_ft:.1f} ft from the nearest building" for t in c.fire_water_adrift(ctx.plan)]


def _tub_in_building(ctx: Context) -> list[str]:
    return [f"a fire-water tub at svg({t.x:.0f},{t.y:.0f}) reaches {t.into_ft:.1f} ft INTO a building" for t in c.tubs_in_buildings(ctx.plan)]


def _tub_on_well(ctx: Context) -> list[str]:
    return [f"a fire-water tub at svg({t.x:.0f},{t.y:.0f}) overlaps a well" for t in c.tubs_on_wells(ctx.plan)]


def _occluded(ctx: Context) -> list[str]:
    return [f"{o.kind} {(repr(o.text) + ' ') if o.text else ''}at svg({o.x:.0f},{o.y:.0f}) is under a feature drawn later" for o in c.occluded_foreground(ctx.plan)]


def _orphan(ctx: Context) -> list[str]:
    return [f"{o.text!r} at svg({o.x:.0f},{o.y:.0f}) is {o.gap_ft:.1f} ft from the nearest glyph it names" for o in c.orphan_group_labels(ctx.plan)]


def _passage(ctx: Context) -> list[str]:
    return [f"a {b.w_ft:.1f} x {b.h_ft:.1f} ft object at svg({b.x:.0f},{b.y:.0f}) stands in a {b.opening_ft:.1f} ft opening" for b in c.passage_blockers(ctx.plan)]


def _board(ctx: Context) -> list[str]:
    return [f"notice board at svg({b.x:.0f},{b.y:.0f}) is {b.gap_ft:.1f} ft from the nearest gate opening" for b in c.notice_board_adrift(ctx.plan)]


def _dark(ctx: Context) -> list[str]:
    return [
        f"{d.text!r} at svg({d.x:.0f},{d.y:.0f}) - black ink over a dark feature; "
        + (f"nudge ({d.nudge_dx_ft:+.0f},{d.nudge_dy_ft:+.0f}) ft clears it" if d.fixable else "no small nudge clears it - relocate")
        for d in c.dark_on_dark_labels(ctx.plan)
    ]


def _clash(ctx: Context) -> list[str]:
    return [f"{lc.a!r} and {lc.b!r} overlap at svg({lc.x:.0f},{lc.y:.0f})" for lc in c.overlapping_labels(ctx.plan)]


def _doors(ctx: Context) -> list[str]:
    return [f"a door at svg({d.x:.0f},{d.y:.0f}) floats {d.gap_ft:.1f} ft inside the building" for d in c.floating_doors(ctx.plan)]


def _on_wall(ctx: Context) -> list[str]:
    return [f"a {w.w_ft:.0f} x {w.h_ft:.0f} ft structure at svg({w.x:.0f},{w.y:.0f}) reaches {w.into_ft:.1f} ft into the {w.wall}" for w in c.structures_on_walls(ctx.plan)]


CHECKS: tuple[Check, ...] = (
    # --- the shared layer: pure geometry, every sheet ---
    Check(
        "structures_overlap",
        lambda ctx: s.structures_overlap(ctx.plan),
        None,
        "ochiba-overlap-red.svg",
        "move one footprint clear of the other, or draw a contained part (an engawa, a porch) fully inside its building",
    ),
    Check("structures_on_walls", _on_wall, None, "ubame-privy-in-wall-red.svg", "set the structure against the wall's inner face, or break the wall around it if it IS part of the wall"),
    Check("occluded_foreground", _occluded, None, "ubame-occlusion-red.svg", "move the buried label or glyph to the top layer"),
    Check("overlapping_labels", _clash, None, "ochiba-label-clash-red.svg", "move one label apart so neither smears the other"),
    Check("dark_on_dark_labels", _dark, None, "hayakawa-layout-red.svg", "nudge the label off the dark feature or give it a light fill"),
    Check("floating_doors", _doors, None, "ochiba-layout-red.svg", "set the door glyph on the wall it opens through"),
    Check("orphan_group_labels", _orphan, None, "ochiba-layout-red.svg", "put the group label beside a glyph it names"),
    Check("passage_blockers", _passage, None, "ochiba-stones-in-passage-red.svg", "move the object clear of the track - stones and posts FLANK a passage"),
    Check(
        "gate_widths", lambda ctx: s.gate_widths(ctx.plan), None, "ochiba-capped-gates-red.svg", "draw the opening at passage width from the INK (pull each flanking endpoint back by half a stroke)"
    ),
    Check("scale_bar_present", lambda ctx: s.scale_bar_present(ctx.plan), None, "ochiba-no-scale-red.svg", "add the 90 px scale bar with its `30 ft` and `(3 px = 1 ft)` labels"),
    Check("viewbox_cropped", lambda ctx: s.viewbox_cropped(ctx.text, ctx.plan), None, "ochiba-wide-viewbox-red.svg", "crop the viewBox to ~15-25 px of parchment around the ink"),
    # --- fire-water: required by BOTH programs, so declared for both (spec 254 FR-003, round-1 item 2) ---
    Check("fire_water_adrift", _tub_adrift, BOTH, "ochiba-tub-adrift-red.svg", "move the tub to a wall or eaves corner - a tensuioke is gutter-fed"),
    Check("tubs_in_buildings", _tub_in_building, BOTH, "ubame-tubs-inside-red.svg", "move the tub OUT, clear of the wall"),
    Check("tubs_on_wells", _tub_on_well, BOTH, "ochiba-tub-on-well-red.svg", "move the tub to a different eaves corner"),
    # --- the magistracy's own ---
    Check("notice_board_adrift", _board, frozenset({MAGISTRACY}), "ochiba-layout-red.svg", "move the notice board to within 20 ft of a gate opening"),
    Check("coverage_band", lambda ctx: s.coverage_band(ctx.plan), frozenset({MAGISTRACY}), "ochiba-coverage-red.svg", "consolidate loose slack or add a program building - never shrink the envelope"),
    Check(
        "perimeter_hugging", lambda ctx: s.perimeter_hugging(ctx.plan), frozenset({MAGISTRACY}), "ochiba-hugging-red.svg", "move the building against its wall - the center of each court stays open"
    ),
    Check(
        "two_court_zoning",
        lambda ctx: s.two_court_zoning(ctx.plan),
        frozenset({MAGISTRACY}),
        "ochiba-zoning-red.svg",
        "put the hearing court on the gate's side of the divider and the residence behind it",
    ),
    # --- the country shrine's own (fixtures cut from the exemplar once it exists; synthetic until then) ---
    Check("sanctuary_on_axis", lambda ctx: s.sanctuary_on_axis(ctx.plan), frozenset({SHRINE}), "shrine-sanctuary-off-axis-red.svg", "set the sanctuary on the approach axis behind the hall"),
    Check("arch_on_approach", lambda ctx: s.arch_on_approach(ctx.plan), frozenset({SHRINE}), "shrine-arch-adrift-red.svg", "stand the arch over the approach where it crosses the fence"),
    Check("well_clear_of_arch", lambda ctx: s.well_clear_of_arch(ctx.plan), frozenset({SHRINE}), "shrine-well-on-approach-red.svg", "move the well beside the approach, clear of the way and the arch"),
    Check(
        "fence_not_wall", lambda ctx: s.fence_not_wall(ctx.text, ctx.plan), frozenset({SHRINE}), "shrine-walled-red.svg", "bound the precinct with a fence or hedge group, not a compound wall stroke"
    ),
)


def checks_for(tier: str | None) -> tuple[Check, ...]:
    """The registered checks that apply to a sheet of `tier` (None: the shared layer only)."""
    return tuple(ch for ch in CHECKS if ch.applies_to(tier))


def run_checks(ctx: Context, tier: str | None) -> list[tuple[Check, list[str]]]:
    """Every applicable check with its findings, in registry order (an empty list = it passed)."""
    return [(ch, ch.run(ctx)) for ch in checks_for(tier)]


def ft(px: float) -> float:
    return px / FTPX

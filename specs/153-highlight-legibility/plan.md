# Implementation Plan: five things about highlighting

**Feature**: 153-highlight-legibility | **Spec**: [spec.md](spec.md) | **Date**: 2026-08-29

## Summary

Five small, independent changes, all on the PAGE side of a Mode B map. Nothing touches placement,
geometry, or the SVG/PNG - feature 134's FR-010 (the drawn map is byte-identical) holds throughout,
and the one engine-file edit (`landuse.py`) changes a side-list tag, not a drawn string.

## Technical Context

**Language**: Python 3.14 | **Touched**: `l7r/diagram/interactive/{tags,page,classes}.py`,
`interactive/assets/page.css`, `settlement/fields/landuse.py` |
**Testing**: `tests/interactive/` (registry, page, browser) | **Scale**: one HIT_WIDEN row, one tag
subclass, two CSS rules, five sibling pairs, one name string.

## Constitution Check

| principle | how this feature satisfies it |
|---|---|
| VI (verification) | `make done` green; the two dike-pond pool maps regenerated and gated; the feature-148 page-vs-SVG check re-run (it must stay ~0.03%, since a new CSS rule that leaked into the default state would show there) |
| X (files at human scale) | no file grows materially; `tags.py` gains one 12-line class |
| XII (record the why) | every change carries the GM's own words at the point of change; the FR-002 rendering decision is recorded in `research.md` R1 and in `page.css` |
| XIII (no regressions) | baseline in a detached worktree before the gate |
| XVI (do the literal thing) | the one place this reads past the GM's words - four crop dikes where they said "the two different dike modals" - is declared in the spec's Assumptions and was put to `spec-fidelity` |

## Design

**FR-001 - the sluice's hit box.** `HIT_WIDEN` already exists and already does exactly this for the
field ditch. One row, the ditch's own factors. Nothing else to decide: the GM said "similar to what we
are doing with the field ditches", and the sluice's mark is THINNER (2.4 px against the ditch's), so
the same factors give it a slightly smaller absolute box than the ditch's but the same character.

**FR-002/FR-003 - the planted dike.** The crowns already carry the dike's class, so they already light;
the problem is that they light in the SAME color as the bank and the plant shape disappears. The fix is
a second highlight tone for the planting, keyed off a marker on the group.

The tag is the natural carrier: `Planted(str)` is a `str` subclass, so every `isinstance(tag, str)`
path in the page keeps working unchanged and no call site outside `landuse.py` needs to know it exists.
`_open()` adds a `planted` token to the group's class list; two CSS rules (placed AFTER the global
highlight rules, so specificity is decided by order rather than by counting selectors) paint that group
in `--hl-planted`. A class with no `Planted` tag emits exactly the string it emitted before, which is
what keeps FR-003 true for everything else.

**FR-004/FR-005 - the siblings.** `_PAIRS` rows. `_install_siblings` installs both directions and
`explanations()` already drops a sibling whose class is absent from this map, so a rice hamlet with no
ponds never shows the sluice link.

**FR-006 - the name.** `FeatureClass.name` is the modal heading; `key` is what the ink carries and what
`all_ink_is_ruled_on` reads. Only the name moves. This makes `windbreak` the FIRST class whose name and
key differ, which is why `tests/interactive/test_classes.py` had to stop asserting they are equal - the
replacement rule is that the name CONTAINS the key, which still catches a typo or a mismatched row.

## Phases

1. the sluice hit box (FR-001)
2. the planted highlight: tag, marker, CSS, emit site (FR-002/003)
3. the siblings and the name (FR-004/005/006)
4. tests, the pool maps, the page-vs-SVG check, the gate

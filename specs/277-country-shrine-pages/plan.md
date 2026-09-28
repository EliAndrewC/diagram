# Implementation Plan: 277 - country shrine sheets as interactive pages

**Branch**: none (`export SPECIFY_FEATURE=277-country-shrine-pages`) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

## Summary

Apply feature 262's magistracy process to the country-shrine tier: the tracked sheet SVG is the one source, every
element tagged with its kind; the kinds the shrine draws or its program names get write-ups in the shared Mode A
registry; the tier's `types.json` items name their kinds and keep no label, class or why; the sheet's generator renders
the PNG and writes the page from the one SVG; tests hold every country-shrine sheet complete and the registry closed.

## Technical context

- **Surface**: `l7r/diagram/interactive/compound_kinds/shrine.py` (new) and `__init__.py`; `l7r/diagram/buildings/types.json`
  (the country-shrines items); `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg` (tags only, no ink) and
  `.gen.py`; `tests/interactive/test_compound_kinds.py`; `buildings/programs.md` (regenerated, `make building-programs`).
- **No Mode B engine change**; no map rolls.

## Constitution check

- VI: PASS - the census on write; pool tests; `make done`. IX: PASS - no canon touched. X: PASS - tests red-first on a
  seeded fault. XII: PASS - every write-up is written from a named research section or says it is silent. XIII: PASS -
  the PNG and the pack audit identical before and after (SC-004). XVI: PASS - the magistracy process, applied whole.

## Decisions

- **D1 - one module of shrine kinds** (`compound_kinds/shrine.py`): the 7 kinds the sheet draws that no magistracy does
  (hall and dwelling, sanctuary, the monk's rooms, writing room, approach, basin, sacred tree), the 2 for its untagged
  ink (swept clearing; footpath - a guess, silent in the record), and the 7 its program names but no sheet draws
  (guardian figures, lanterns, strength stones, stage, sumo ring, bell tower, burial ground). Kinds both tiers draw
  (torii, shrine grove, well, kitchen, genkan, latrine, vegetable garden, fire-water tubs) stay in their magistracy
  families, written once (FR-002, FR-006).
- **D2 - carry-over** (262's FR-005): each new kind takes its folded item's class and reason - the dwelling (the monk's
  rooms) and the bell tower stay `guess`. A shared kind keeps the classification feature 262 gave it; the one that
  differs is the well - the shrine item called it accurate, the shared kind labels it a drawing convention because the
  curb is drawn larger than true - and the shared kind's label is the one definition (not a re-decision: the drawing
  convention applies to the shrine's well as drawn).
- **D3 - the fold** (FR-006): each country-shrines item becomes `id`, `kind`, `band_ft` plus its `forms`, `site`,
  `optional`; item -> kind: sanctuary, hall -> hall and dwelling, dwelling -> the monk's rooms, arch -> torii,
  approach, well, grove -> shrine grove, sacred_tree -> sacred tree, guardian_figures, lanterns, strength_stones,
  stage, sumo_ring, burial_ground, kitchen_garden -> vegetable garden, privy -> latrine, fire_water -> fire-water tubs,
  bell_tower. The pack audit already resolves a kinded item through the tags (feature 262), and `programs.md` from the
  registry.
- **D4 - the untagged ink**: the background and the precinct's layout rect `-`; the grove's ragged outline `shrine
  grove`; the clearing polygon `swept clearing`; the well path `footpath`. Tags only - the PNG is compared pixel for
  pixel.
- **D5 - the generator**: `hoshigaoka-shrine.gen.py` gains the magistracy gens' `write_sheet_page(SVG, COMPOUND_CLASSES)`
  and fails on an unclean census.
- **D6 - the tests**: `test_compound_kinds.py` reads every `pool/country-shrines/*/` sheet beside the magistracies (every
  element tagged and known), and the closure covers the kinds the sheets draw or the programs name; a seeded fault (an
  untagged element, an unknown kind) is proved red.
- **D7 - the shrine's own reading of a shared kind** (the spec's Edge Case: "the page's own notes carry the difference,
  not a second kind"; plan review round 1): `hoshigaoka-shrine.notes.md` gains the "Map notes" `### Features` block
  (feature 262's FR-010, read by `write_sheet_page`) keyed by kind, for every shared kind the sheet draws - `torii`,
  `shrine grove`, `well` (the folded item's reason and the 5 ft curb), `kitchen`, `genkan`, `latrine`, `vegetable
  garden`, `fire-water tubs`. Each line is read off the sheet and its design notes; nothing from the monk's Obsidian
  Portal record. The shared `Torii` write-up's stale "20 ft" becomes the 12 ft pitch (feature 268) and names the
  country shrine in its What and Covers.

## Phases

T01 kinds; T02 fold; T03 tags and gen; T04 tests; T05 `make done`, push.

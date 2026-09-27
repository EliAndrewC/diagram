# Implementation Plan: A feature inside a feature is its own kind

**Feature**: `264-nested-features-own-kinds` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

Feature 262's reader already lets the nearest `data-kind` win, so a part becomes its own kind by carrying its own
tag. What is new is (a) the tags on every inventoried part, (b) thirty-odd registry entries written from the record,
(c) a room drawn as its own floor so it lights across its area, and (d) the reverse link - a lit parent lights its
parts - which the reader derives from the drawing's own nesting.

## Decisions

- **D1 - Parts are tagged on the sheet, nothing else.** A part inside its parent's group carries its own
  `data-kind`; the reader already gives it that kind (262 FR-002). No side list. (spec FR-001)
- **D2 - The reader derives "part of" from the drawing.** `sheet.pieces()` returns, beside each fragment's kind, the
  distinct kinds of its tagged ancestors (its lineage); a part drawn outside its parent's group for paint order (the
  genkan after the garden, the nakamon posts, Ubame's torii) declares `data-part-of="<parent kind>"`, read exactly as
  an enclosing group. `flatten()` keeps its two-list shape for every existing caller. (FR-003)
- **D3 - The page carries the link as `data-in` on the part's class group.** `render_page(within=...)` - a parameter
  defaulting to None, so no hamlet caller changes and no hamlet page draws, counts or behaves differently (FR-008;
  its inlined script gains the indexing branch, inert where no group carries `data-in`) - adds `data-in="k1|k2"` to each wrapped group;
  `page.js`, when it indexes the groups once at load, files a group under every key its `data-in` names, so lighting
  the kitchen lights its hearth and well and lighting `well` lights no kitchen. In raster mode the lit groups are the
  vector layer over the picture, as for any lit kind. (FR-003)
- **D4 - A room is its own floor.** The building's rect splits into three: its fill alone, one fill per room in the
  same color tagged with the room's kind, then its outline with `fill="none"`. Measured on Ochiba's west block before
  any edit: 0 px differ from the one rect (resvg, 2400 px). The shuttered wing, already its own rect, is tagged as is.
  (FR-002, FR-006)
- **D5 - The pack audit folds a room into its building.** A rect of a building's own fill wholly inside an earlier
  building rect is a room, not a second building (`pack_audit/parse.py` `rooms_folded`); without it every room edge
  read as a gap between buildings (Ochiba +1 finding, Ubame +1/-1, measured; plan review re-measured it). With it the three hand sheets' audit
  output is identical before and after, and the old sheets' output is unchanged by the fold. (FR-006)
- **D6 - The placer draws the practice ground's rack and posts as parts** inside a group of the ground's kind, so
  the two generated sheets light them as themselves and with the ground. (FR-001, FR-003)
- **D7 - The registry grows by family.** New kinds go in the existing family modules (`household`, `office`,
  `grounds`, `particulars`), written from `coverage.md` in the 262 docstring form; each parent's `Covers:` and prose
  drop the parts that became kinds (FR-005). `court divider and nakamon` splits into `court divider` and `nakamon`.
  A family module past 1,000 lines is split by family, never excused.
- **D8 - Research owed is written down, not run.** Every kind `coverage.md` finds uncovered, and every
  contradiction, is appended to `future-work/compounds.md` "Research owed" (FR-004; GM 2026-09-26).
- **D9 - Verification** is a browser probe script (spec SC-001, SC-002) run by hand over the five pages - per part,
  the kind named at its position in both modes; per parent, a point that names it and a click that opens its
  write-up; per parent, the parts lit with it - with its result written into `research.md`. No browser test is
  added (GM 2026-09-07); the reader and the page get unit tests, and a standing unit test over `sheet.pieces()` of
  the three hand sheets holds each inventoried part's kind and its parent, so FR-001 and FR-003 stay enforced
  after the probe (plan review's aside).

- **D10 - The id map's palette grows a second channel** (found by the probe, `research.md` R4). Ubame's 69 kinds are
  past the red-only palette's 63; green counts the rows past it, the first 63 keep their colors and keys (no hamlet
  id map changes), and `page.js` reads both channels. `data-in` rides after `data-k` so `raster._GROUP` finds a part.
  (FR-001, FR-002: a part must answer as itself zoomed out too)
- **D11 - The id map draws text unblended** (`--text-rendering optimizeSpeed`; R4): a blended glyph edge snapped to
  the kind one palette step away, so a label beside a new neighbor in the palette answered as it. Every label on
  every page now answers on its whole glyphs; no picture changes. (FR-001)

## Constitution check

- XII (research): every new kind is written from the record or says it is silent; no new finding. Classification
  carried from `coverage.md`.
- XIII (no regressions): PNG pixel-identical and pack audit identical, measured per sheet; hamlet pages untouched.
- XVI (the literal thing): every part per the definition; the fabric line and the rooms were put to `spec-fidelity`
  and ruled faithful.
- Files: `page.py` 971 lines after the parameter (under 1,000).

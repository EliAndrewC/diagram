# Implementation Plan: Labels placed by the cartographic standard

**Feature**: `266-label-placement-standard` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

One mode-neutral package, `l7r/diagram/labels/`, implements the standard (spec FR-002 to FR-009): the ranked
positions, the preferred offset measured edge to edge, nearest-first search with a leader for any seat beyond the
preferred offset, the 0/500/1,000 weights with free space first, area and line captions, upright rotation, and the
wrap layouts. Three adaptors feed it: the settlement engine's label phase (the board, `place_caption`, the road
caption, the field names), `compound.py`'s sheet writer, and a `make seat-label` tool that reads a hand-drawn sheet's
tagged SVG. The board's annulus search, `_best_label_spot`, `pull_caption_toward` and the board's hand-seat
parameters are deleted.

## Technical Context

Python 3.14, the skill's existing stack; no new dependency (the SVG reader uses `xml.etree`). The placer is pure
geometry over plain tuples so both modes and the tool can call it. Performance: one caption per hamlet today; the
obstacle index is a uniform grid of obstacle bounding boxes built once per label phase (FR-009, constitution X
clause 15), so a candidate costs a grid read plus exact tests on the few obstacles in its cells. Candidates per
caption: 8 positions x 3 layouts x (1 + rings) with rings up to the reach - a few hundred, each O(nearby obstacles).

## Constitution Check

- **XII (research)**: the standard is read and quoted (research.md R1); rendering-only, so every task is
  `research: rendering`; the calibrations are labeled (spec D2, D3, D4) at the point of change, in the record and in
  the spec.
- **XIII (no regressions)**: every existing caption gate test stays (hug, alignment, notch); the baseline is the
  shipped pool; the gate runs the whole suite.
- **XIV (fix where found)**: the review-round hook routed a NOT-REVIEWABLE pass as a completed round (found this
  feature, round 1); fixed here (T13).
- **XVI (literal)**: scope exceptions D8 and D9 were put to `spec-fidelity` and ruled legitimate; both are enforced
  by tests (FR-012, FR-013).
- **X clause 15 (index once)**: FR-009.
- 1,000-line bar: the new package is split by concern (below); `boards.py` shrinks by about 560 lines.

## Design

### `l7r/diagram/labels/` (new, mode-neutral)

- `standard.py` - the standard's constants, each with its source or its calibration beside it:
  - `POSITIONS`: the eight ranked point positions (QGIS / Krygier and Wood order), each a pair `(sx, sy)` in the
    subject's frame, `sx` in {-1, 0, +1} (left, center, right), `sy` in {-1, 0, +1} (above, level, below), plus the
    two "slightly" positions as fractional `sx` (+0.25 above, -0.25 below: our reading of "slightly", a calibration).
  - `PREFERRED_OFFSET_EM = 0.5` (D2), `RING_STEP_EM = 0.5`, `REACH_EM = 8.0` (calibration: 64 ft for the board's
    8 pt caption - past the old ladder's 53 px reach and inside the gate's 120 px hug cap).
  - `WEIGHT_OBSTACLE = 1000`, `WEIGHT_WAY = 500`, `WEIGHT_FREE = 0` (D4).
  - `CLEAR_EM = 0.5`: a block nearer than the preferred offset to an obstacle other than its own subject counts as
    covering it - a caption as close to a neighbor as to its subject is not plainly its subject's (PSU's
    "association"); a calibration.
  - Text metrics, the ones `label()` already draws with (`0.55` em per character, `1.05` em one-line height, `1.15`
    em pitch, baseline `0.275` em below the block center) - moved here and imported by `settlement/finish.py`, one
    source.
  - `upright(angle)`: an angle normalized into (-90, 90] so text never reads upside down.
- `geom.py` - convex-polygon SAT overlap, polygon-to-polygon gap, segment distance, rotation; pure.
- `layout.py` - `cut(words, n)` (lifted out of `finish._caption_lines`, which then calls it: one body) and
  `layouts(text)`: one line, then the best two-line and three-line cuts.
- `obstacles.py` - `Obstacle(poly, weight, oid)`, `Way(pts, half_width, wid)`, and `ObstacleIndex`: a grid built
  once; `cost(block, ignore)` returns the summed weight of every obstacle within `CLEAR_EM` of the block (excluding
  `ignore`, the subject's own id for an area caption) plus `WEIGHT_WAY` per distinct way the block comes within
  half-width + notch of; `add()` for each placed caption.
- `placer.py` - `Subject` (`kind` point | line | area, the drawn polygon or polyline, `angle`, `oid`, optional
  `hint`), `Placement` (anchor x, y as `label()` takes it, angle, lines, block quad, ring, rank, cost, leader), and
  `place(text, size, subject, index, frame)`:
  - point: candidates ring by ring from the preferred offset outward, all positions and layouts within a ring, block
    placed so its nearest edge stands the ring's distance off the subject's box in the subject's (upright) frame;
  - line: along the line near its hint, above then below, parallel and upright, the gap from the drawn edge;
  - area: the centroid first, then interior seats by distance from it, inside the polygon;
  - choice: the first free candidate in that order; else the least cost (ring, rank, layout as tie-breaks); never
    empty (FR-007); a candidate whose block leaves `frame` is skipped;
  - leader: when a point or line caption's ring is beyond the first, the segment from the block's nearest point to
    the subject's nearest point, trimmed by 1 px at each end.

### Settlement adaptor (`settlement/structures/captions.py`)

- `seat_caption(text, subject, size, italic, weight, color, cls)` queues a `caption` request; `place_labels` drains
  it through `_draw_seated_caption`, which builds the index once per phase from the manifest (`label_obstacles`:
  `label_blocker_quads`, the radius fixtures, torii, walls and the moat as obstacles; lanes, the road, streams and
  drawn channels as ways; placed captions and the title placard as obstacles; ground keys free), places, draws with
  `label(..., lines=, angle=)` and draws the leader (a `<line>` in the label layer, the caption's class and color,
  recorded in `M["caption_leaders"]`).
- `label()` gains `lines=` and `angle=` (the placer's choice, bypassing the wrap probe and the rotation fold); the
  recorded referent is the subject's box.
- Callers: `_draw_board_caption` (a rotated-box point subject) shrinks to building the subject; `place_caption`
  queues a box subject (its `hint`/`slides` parameters and the four callers' arguments go); `_finish_road_label` a
  line subject with the authored anchor as its hint; `field_name_label` an area subject (the field's rectangle) with
  its own markup kept.
- Deleted: the annulus search in `boards.py`, `_best_label_spot`, `pull_caption_toward`, `kosatsuba`'s `label_above`
  and `label_xy` (callers: one frozen gen, two tests - the tests are rewritten), the old ladder constants no longer
  read.

### Mode A adaptor (`compound.py`)

`_render_svg` builds an index from what it draws - building rects and point features and walls as obstacles, zone
grounds free - and seats every caption through the placer: zone and building names and "bath" as area subjects, the
striking posts, well, latrine, tubs and notice board as point subjects. The title, the draft note and the scale-bar
text are not captions (spec FR-001) and stay where they are.

### Hand-drawn sheets (`l7r/diagram/tools/seat_label.py`, `make seat-label SHEET=<svg> [KIND=<k>] [WRITE=1]`)

Reads the SVG with `xml.etree`, applying `translate`/`rotate`/`matrix` transforms, into shapes: `rect`, `circle`,
`ellipse`, `polygon`, `polyline`, `line` (a stroke of width 4 or more is a wall - an obstacle - a thinner one a way),
`path` (its coordinates' hull) and `text` (its block from the shared metrics). A caption is a `<text>` inside a
`data-kind` group (or carrying the tag); its subject is the non-text shapes of that kind; a shape containing the
subject whose area is at least 20 times the caption block's is ground (weight 0), the rest obstacles. `--check`
lists every caption not at its standard seat (1 px tolerance); `WRITE=1` rewrites those `<text>` positions (and
transforms) in place, tagging an untagged board caption.

### Enforcement (FR-012, FR-013)

- `tests/labels/test_caption_paths.py`: an AST walk of `settlement/` whose `self.label(...)` calls must fall in the
  D8 list (file, function) or the placer's own drawing call; a walk of `compound.py` whose `<text` literals must fall
  in the title / note / scale-bar functions. A planted call fails it (SC-002).
- `tests/gate/test_hand_sheet_captions.py` + `tests/fixtures/caption_ledger.json` (each hand-drawn sheet's sha256 and
  its captions as they stood when this feature landed): a caption off its standard seat fails unless the ledger
  holds it AND the sheet's hash is unchanged (SC-006).

### Record and doctrine

- research/presentation: questions 040 (rewritten on the standard) and 050 (the standard's rotation and line rules),
  with notes; eight registry entries; `quote-check`, `record-format`, `source-applicability` over them.
- `buildings.md` (Mode A doctrine) and `.claude/agents/building-review.md`: captions seated with `make seat-label`,
  revising a sheet re-seats all of its captions.
- `future-work/cities.md`: D8's 47 calls, to convert when their tier is scripted.
- `dev/placement.md`, the label-phase notes, and the captions CLAUDE.md index updated.

## Decisions (plan level)

- **P1 - A block's clearance to a neighbor is the preferred offset** (`CLEAR_EM`): a caption must stand no closer to
  any other obstacle than to its own subject, which is what "association" means in practice. Calibration.
- **P2 - Reach 8 em**: calibration; past it the least-cost seat within reach is taken (FR-007).
- **P3 - "Slightly" = a quarter of the block's width** off center for the last two positions. Calibration (the
  sources name the position, not the amount).
- **P4 - A wall stroke 4 px or wider is an obstacle on a hand-drawn sheet, a thinner line a way.** Calibration from
  the sheets (compound walls 9 px, dividers 6 px; lanes and paths drawn thinner).
- **P5 - Ground on a hand-drawn sheet = a shape that contains the subject and is at least 20 times the caption's
  block.** The sheets draw courts and grounds as large rects under their contents; a heuristic, recorded.

## Project Structure

```text
.claude/skills/diagram/
  l7r/diagram/labels/{__init__,standard,geom,layout,obstacles,placer}.py   new
  l7r/diagram/tools/seat_label.py                                        new
  l7r/diagram/settlement/structures/captions.py                          the adaptor
  l7r/diagram/settlement/structures/fixtures/boards.py                   the board caption, shrunk
  l7r/diagram/settlement/castle_civic.py                                 place_caption; _best_label_spot gone
  l7r/diagram/settlement/structures/ground.py                            the road caption
  l7r/diagram/settlement/finish.py                                       label(lines=, angle=); metrics imported
  l7r/diagram/compound.py                                                captions through the placer
  tests/labels/                                                          new: the placer's unit tests, the path test
  tests/gate/test_hand_sheet_captions.py, tests/fixtures/caption_ledger.json
  research/presentation/*, research/sources/010-works-cited/94x0-*
  buildings.md, dev/placement.md, future-work/cities.md
.claude/agents/building-review.md
scripts/review-round-hooks.sh                                            T13
```

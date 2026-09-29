# Plan - feature 286, a hand-drawn sheet's labels placed by the one placer

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Request: [`request.md`](request.md).

## What is there today

- The one placer, `l7r/diagram/labels/place` (feature 266), seats every generated map's caption.
- A hand sheet's captions are seated by `tools/seat_label.py` (`make seat-label WRITE=1`), run by hand, which reads the
  SVG, finds each caption's subject and calls `place`. Its verdict is checked by `tests/gate/test_hand_sheet_captions.py`
  against `tests/fixtures/caption_ledger.json`, and by four sheet-audit checks (`overlapping_labels`,
  `dark_on_dark_labels`, `orphan_group_labels`, the label half of `occluded_foreground`).
- It reads a caption's position three ways: a hand seat kept where the placer found no free one
  (`hand_seat_if_no_better`); in a group with several captions, the part a caption lies in or is nearest names its
  subject; a caption tagged on its own names the nearest shape of its kind; and whether a caption lies inside its
  subject makes it an inside (area) caption.
- Measured (spec, Decisions Recorded): 8 captions where the hand seat beats the placer, 7 of them free seats the
  placer's search does not reach. The causes, one diagnostic run: mixed-size captions measured at the head's size
  (Hayakawa's bath, HEARING COURT); a large area's inside search sampled only near its centroid (the forecourt); too few
  positions around a small point subject (the Ebisu altar note, Ubame's Fox-border notes, the guardroom); a stepped
  building searched round one block (RESIDENCE).
- Position-dependent captions today (observed 2026-09-28; method: the subject reader instrumented): about 31 in groups
  with several captions and 54 tagged on their own, across the three magistracies; the shrine has none.

## Decisions

- **D1 - a caption declares its subject, never its seat** (FR-002). A caption names the non-text shapes of the tagged
  group it stands in when that group has one caption; otherwise it carries `data-names="<id> ..."`, the ids of the
  shapes it names (one of several like parts, a caption tagged on its own). Its text and lines are content; it carries
  no coordinates - the sheet's `<text>` for a caption has no `x`/`y` and its leader is not drawn by hand. A one-time
  migration (`tools/caption_decl.py`, run once and kept tested) writes the ids and `data-names` from today's subject
  reading, strips the coordinates and the hand leaders, so no caption changes what it names.
- **D2 - inside or beside, the placer's call** (FR-002). For every caption the placer tries its subject's inside seats
  first (the standard: an area's name inside it), then the ranked seats beside it; the first free seat wins. A subject
  too small for its name, or whose inside is its own dark ink (a well's shaft, a tub), costs its inside seats and goes
  beside. Done in `seat_label` as two calls to `place` (area, then point), no change to the engine's own calls.
- **D3 - the fallback that finds the free seats a person found** (FR-003). When the standard search finds no free
  seat, `place` searches further before it settles for least cost: an area's inside sampled over its whole extent (the
  step set by its area, not one em); around a point subject, positions slid along each side between the ranked ones;
  around a stepped building (feature 283's `stepped_subject`), each block. The standard's order stands wherever it
  already finds a free seat. It lives in `labels/placer.py`, so the generated maps take it too; measured on the
  scripted maps (a caption that moves there owes the settlement-review the pair guard asks for).
- **D4 - a caption's lines at their own sizes** (FR-003). A caption with smaller sub-lines (a building's name over its
  gloss) is measured and written line by line at each line's size, not at the head's.
- **D5 - placed in the render pipeline** (FR-001, FR-005). `hand_sheet.placed(svg_text)` (D10) returns the sheet with every
  caption placed; each hand sheet's gen renders its PNG and its page from that text (a temporary file), so the tracked
  SVG is the drawing and the declarations and the picture is always placed. `make sheet-render SHEET=<svg> OUT=<png>`
  renders any sheet placed, for a session or a review agent that wants to look at one.
- **D6 - no check of the placement** (FR-004). Removed: `tests/gate/test_hand_sheet_captions.py`, the caption ledger,
  the `make seat-label` target and its report (`judge`), the four sheet-audit checks and their red fixtures and tests,
  the label half of `trees_overlap` (a canopy over a caption is the placer's to avoid, not a check's to report - the
  tree's checks against buildings, fences, wells, glyphs and tubs stay), and `building-review`'s caption-seat step. The placer's unit tests carry correctness, and `seat_label`'s own tests
  cover the declarations, inside-or-beside, the fallback cases above and the stripped-coordinate reading.
- **D7 - readers use tags, not positions** (FR-005). `pack_audit/labels.py` pairs a required item with its structure
  by the sheet's `data-kind` tags, not by the nearest label; any other reader of a caption's coordinates is moved to the
  placed text or the tags.
- **D8 - the docs** (FR-006): `SKILL.md`'s Mode A usage, `buildings.md`, research presentation 040's note that names
  `make seat-label`, and the `building-review` and `size-audit`
  contracts say a sheet declares a caption's text and subject and the pipeline places it; the contracts judge a label's
  wording, not its position.
- **D9 - verification**: `make quick` while building; the one-time SC-002 measurement (each caption's cost at its
  hand seat before, and at its placed seat after) in `measurements.json`; the scripted maps' captions compared before
  and after D3; `make done`; the GM's blind test at hand-back, with the line that the 18 legacy exhibits are untouched.

## Decisions made in implementation (2026-09-28)

Each found by rendering the four sheets and looking, then measuring (`measurements.json`).

- **D10 - the module lives beside the placer.** `seat_label` became `l7r/diagram/labels/hand_sheet.py`: `tools/` holds
  what no generator imports (its `CLAUDE.md`), and every sheet's gen now imports `placed`. D5's `seat_label.placed` is
  `hand_sheet.placed`; `make sheet-render` runs its `main`.
- **D11 - a declaration names by `data-id`, not the SVG `id`.** The magistracy sheets give three court rects one `id`,
  `precinct`, which the pack audit reads; named by it, INNER COURT and OUTER COURT named all three and were set on the
  bank street outside the wall. `data-names` lists `data-id`s, which the migration writes.
- **D12 - a wall is a leader's obstacle.** With no hand seat to fall back on, the bath's and the granary's names were
  led across the court divider and the compound wall from ground on the far side. A dark stroke 4 px or wider
  (`WALL_HALF_PX`) is in the leader index; a wall the caption names is not (Ubame's east wall IS the Fox border).
- **D13 - a caption of several texts wraps by the standard's rule.** Each one-line text may take the placer's own
  two- or three-line layouts (`hand_sheet.wraps`), one line first: the granary's `staging store - tax grain` and the
  tally office's `barge manifests & seals` fit inside their buildings only wrapped. A text the sheet breaks into lines
  keeps its breaks.
- **D14 - the order, then a repair.** Captions are placed beside-only first, then those that fit inside, then glyphs
  in a named ground, each in document order (Imhof: points before areas). In document order alone a building's name
  took Ochiba's garrison latrine's one free seat; smallest-first stranded Hayakawa's RESIDENCE; a glyph named before its
  ground took the ground's inside and the ground's name went into an empty building. Then `repair`: a caption left
  covering ink is re-placed with one near neighbor lifted (`REPAIR` ems plus its length), kept where it is freer and the
  neighbor no worse. The lift tries the standard's seats only (`place(extended=False)`): a full search per lift ran past
  ten minutes on Hayakawa.
- **D15 - the declarations the old reading found nothing for** are written by hand, each recorded in its map's notes:
  Hayakawa's `river landing` names the landing's steps; the alcove notes on Hayakawa and Ubame continue the reception's
  caption, under which they stood; Ubame's three border names name the east wall with the border line.

- **D16 - what has an inside.** One closed outline holding the caption's other parts is its area (a garden and the
  lantern in it: Ochiba's inner garden, read as a scatter, was named from outside with a leader across the kitchen). A
  scatter of like glyphs has none, and is named beside the group, else beside any one glyph, largest first; the ORDER's
  "fits inside" asks only of a subject that has an inside (the tubs' box spans the compound).
- **D17 - D12 widened: a leader crosses no building** it does not name, nor one holding what it names (a room's
  range), as it crosses no wall.
- **D18 - D14 amended: a repair is kept where the pair together cover less**, not only where the neighbor is no worse.
  A chain of three lifts was built for Ochiba's tubs and freed nothing more; it was taken out and says so at the point
  of change.
- **D19 - the index skips by boxes** (`labels/obstacles.py`): an obstacle whose box is clear of the block's is clear,
  and two level rectangles are measured by their boxes. Exact - the boxes' gap bounds the outlines' from below, and is
  theirs for level rectangles (a unit test holds both against the outline test) - so no generated caption moves; the
  outline test was nine tenths of placing a hand sheet (observed 2026-09-28; method: cProfile of `hand_sheet.seat` on
  Ochiba, under load - 114 s before, 9.5 s after; each sheet's gen now 4-16 s, `make map`).
- **D20 - SC-002 measured on the drawing** (`sc002_drawing.py`, in `measurements.json`): the hand seat (block and its
  hand leader) and the placed seat priced against the drawing alone, each as the kind of seat it is. The first reading
  scored the hand seat the old tool's way - block alone, among captions since moved - and so flagged seats that were
  equal (the Ebisu note: `ebisu_probe.py`). Ochiba's and Hayakawa's `fire-water tubs` are declared against every tub, as
  D15's hand declarations are: the migration had named the one nearest the caption.
- **D21 - D7's readers, as built.** A program item is measured on the largest structure tagged with its kind; the
  notice-board fallback to a caption is gone; `_size_table.py` names each rect by its `data-kind`. The crop check
  (`ink_bounds`) skips a declared caption - it has no position - rather than render the placed sheet (observed 2026-09-28 by the T05 agent; method: the pack-audit sweep timed with
  `placed()` wired in, before D19: 10-62 s a sheet
  in `make quick`, over its budget); the placer keeps every caption inside the frame. What it costs: a margin that only
  a caption fills would read as slack. None of the four sheets has one. Chosen by the session, 2026-09-28.

- **D22 - two captions keep the larger of their gaps** (`Obstacle.keep`): a placed caption is added to the next one's
  index with its own clearance, so a small name set beside a large one keeps the large one's gap. The round-4 review's
  full-context measure (`sc002_ctx.py`, adopted unchanged as SC-002's) found three captions inside a larger neighbor's
  clearance; none after.
- **D23 - a named thing weighs as a name.** Ink that carries a name of its own - a room or ground inside what a caption
  names, a building anywhere, another named ground under a ground's name - weighs as a caption does
  (`WEIGHT_TEXT`): a caption set on it reads as naming it (Ubame's RESIDENCE set in the guest room, its OUTER COURT on
  the practice ground and then on the gate range's roof). A thing's name beside it on open ground is free as before.
- **D24 - D14's order amended: open ground's names first**, as a cartographer sets the major area names before the
  small ones fill in (placed after them, Ubame's OUTER COURT found its open ground taken and was led out past the wall);
  and a ground's name stays in its ground unless every seat there would cover another name (Imhof: an area is named
  inside it). A building too small for its name still goes beside it. A tie rule (beside wins a tie) was tried and taken
  out: it set the family rowhouse's name on the hearing court.
- **D25 - D12 raised: a leader across a wall weighs as a name** - a leader from beyond a boundary names the wrong side.
- **D26 - D15 extended:** Ubame's `OUTER COURT` names the outer court, as on the other two sheets; the migration had
  named the forecourt apron it stood on, too narrow once smaller names were placed there. Recorded in its notes.

## Constitution Check

- XIII (no regressions): the placer's change measured on every scripted map's captions against HEAD.
- XIV: the defects the measurement found are fixed in the placer, not excused.
- XVI (the literal thing): every hand-sheet caption placed by the pipeline; no placement check left, per the GM.

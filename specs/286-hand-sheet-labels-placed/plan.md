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
- **D5 - placed in the render pipeline** (FR-001, FR-005). `seat_label.placed(svg_text)` returns the sheet with every
  caption placed; each hand sheet's gen renders its PNG and its page from that text (a temporary file), so the tracked
  SVG is the drawing and the declarations and the picture is always placed. `make sheet-render SHEET=<svg> OUT=<png>`
  renders any sheet placed, for a session or a review agent that wants to look at one.
- **D6 - no check of the placement** (FR-004). Removed: `tests/gate/test_hand_sheet_captions.py`, the caption ledger,
  the `make seat-label` target and its report (`judge`), the four sheet-audit checks and their red fixtures and tests,
  and `building-review`'s caption-seat step. The placer's unit tests carry correctness, and `seat_label`'s own tests
  cover the declarations, inside-or-beside, the fallback cases above and the stripped-coordinate reading.
- **D7 - readers use tags, not positions** (FR-005). `pack_audit/labels.py` pairs a required item with its structure
  by the sheet's `data-kind` tags, not by the nearest label; any other reader of a caption's coordinates is moved to the
  placed text or the tags.
- **D8 - the docs** (FR-006): `SKILL.md`'s Mode A usage, `buildings.md`, and the `building-review` and `size-audit`
  contracts say a sheet declares a caption's text and subject and the pipeline places it; the contracts judge a label's
  wording, not its position.
- **D9 - verification**: `make quick` while building; the one-time SC-002 measurement (each caption's cost at its
  hand seat before, and at its placed seat after) in `measurements.json`; the scripted maps' captions compared before
  and after D3; `make done`; the GM's blind test at hand-back, with the line that the 18 legacy exhibits are untouched.

## Constitution Check

- XIII (no regressions): the placer's change measured on every scripted map's captions against HEAD.
- XIV: the defects the measurement found are fixed in the placer, not excused.
- XVI (the literal thing): every hand-sheet caption placed by the pipeline; no placement check left, per the GM.

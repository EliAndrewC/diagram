# Feature 245 - lit beads at low zoom

**Status**: IMPLEMENTED - FAITHFUL (`spec-fidelity`, round 1 of 5, 2026-09-13; its three asides taken in the same round: FR-003, D2, SC-002); the plan BLOCKED at round 1 (the plan named page-lit as SC-002's check where the spec names the contact sheet) and CLEAR at round 2. No pool manifest moved, so no settlement-review was owed (feature 231).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the measurement of the lit bead under the wash and without it, and the page-lit tool's vector path.
**Predecessors**: 134 (the highlight; the wheel scrolls, the keys zoom), 200 (raster mode), 201 (the 0.45 wash), 231 (`make page-lit`).

## Summary

The GM: on the Inashiro HTML map the bund beans do not visibly light up when highlighted while zoomed out;
they can be clicked, so it is a visual matter - the highlighting needs more contrast - and it is not an
issue zoomed in. The cause is raster mode's wash (feature 201): below the raster switch a lit class's
filled shapes are drawn at 0.45 opacity so the ink above a lit paddy shows through, and the beads - dark
green discs with no stroke, a few screen pixels across at the opening view - take the wash too, which turns
them from dark green to a dull olive the eye does not register as lit (research R1). So the beads are drawn
lit at full strength in raster mode, as they already are in vector mode; the wash stays on every other
class. While measuring this, the tool that measures a lit class on a page (`make page-lit`, feature 231)
was found never to reach the vector page on a real map: its `--vector` loop turns the wheel, which the
page scrolls by ruling, and its browser test ran on a page that opens in vector mode already. That defect
is fixed in this feature (Principle XIV), and its test made to open in raster mode.

## Functional requirements

- **FR-001 The beads light at full strength in raster mode.** In raster mode the lit bund-beans class's
  filled shapes take no wash: their fill opacity is the same as on the vector page. The group's own 0.85
  opacity - the bead's drawing convention - is untouched, and the class's hit discs (drawn with no fill,
  for the pointer) stay unpainted, lit or not.
- **FR-002 Every other class keeps the wash.** The 0.45 wash of feature 201 (its D2, the GM's constant to
  move) is unchanged for every other lit class in raster mode, and the vector page is unchanged for every
  class, the beads included.
- **FR-003 The exemption says why, at the point of change.** The stylesheet states beside the rule why the
  beads, and only the beads, are exempt: the wash exists so that what is drawn ABOVE a lit area shows
  through it; the beads are that ink, and nothing is drawn above them; and they are a fill-only mark a
  few screen pixels across, which is what the wash dims to nothing - with the measurement's pointer
  (research R1). The comment claims only what was measured - the beads - and says that a second class
  found the same way is added beside them.
- **FR-004 The page-lit tool's `--vector` reaches the vector page.** `page_lit.measure(vector=True)`
  zooms with the page's own zoom key (Ctrl with the plus key, feature 134's one way of zooming) instead
  of turning the wheel, until the page reports vector mode or the step cap is reached; the mode the tool
  reports is the mode it measured.
- **FR-005 Proved in a browser on a page that opens in raster mode.** The tool's browser test measures a
  page whose opening view is raster mode (a small viewport over the two-class synthetic map) and asserts
  raster mode measured; its `--vector` case asserts vector mode reached and a zoom above the opening view
  on that same page; the stub test mirrors the key presses. The synthetic map gains one bund-beans
  element, and a browser test reaches raster mode on it (a small viewport, then the fit button), asserts
  the lit paddy's computed fill opacity is the wash and the lit beads' is full, and that on the vector
  page both are full.
- **FR-006 The record.** `research.md` R1 carries the measurement - the unlit and lit bead color under the
  wash and without it, the contrast between the two states, and what the contact sheet showed the eye -
  and the interactive index's raster row and the tools index's page-lit row say the new thing.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-005): the synthetic raster-mode test passes - lit beads at full fill
  opacity and the lit paddy at the wash in raster mode; both at full on the vector page.
- **SC-002** (FR-001): on Inashiro's shipped page at its opening view, the R1 contact sheet re-taken on
  the shipped stylesheet shows the beads gold rather than olive - a by-hand check, the GM's eye final.
  `make page-lit CLASS="bund beans"` still reports no other class moved; it cannot decide this criterion,
  because a washed bead already moves past the tool's threshold.
- **SC-003** (FR-004, FR-005): the tool's browser test reaches vector mode on a page that opened in
  raster mode; on Inashiro, `make page-lit ... VECTOR=1` reports `mode: vector`.
- **SC-004** (FR-003, FR-006): the stylesheet's comment, research R1 and the two index rows exist and say
  what the FRs say.
- **SC-005** (spec-wide): `make page-check` green for the stylesheet; `make done` green for the tool; no
  pool manifest moved, so no settlement-review is owed; lands GATED.

## Decisions recorded

- **D1 - the exemption is by class name, in the stylesheet, not a derived token.** Nothing in the markup
  separates a point mark from an area - a bead's group has the same shape as a paddy's - so a derived
  token would mean the writer measuring element extent at write time, an engine change with a threshold
  to defend, for a set that today has one member. Priced and declined: (a) a positive roster of the area
  classes that take the wash - it fails open: a new crop class would miss the roster and cover the bunds
  when lit, the defect feature 201 fixed; (b) the derived `mark` token above; (c) raising the wash for
  every class - the constant is the GM's (201 D2) and the paddy wash is right. The negative roster fails
  safe - a new mark class gets the wash, dimmer but never covering - and the reason to add a class is
  written beside it (FR-003).
- **D2 - the group's 0.85 opacity stays.** A lit-only override of it as well measured near-identical to
  the exemption alone (R1: 1.89 against 1.75 between the two states), so the smaller change is taken.
- **D3 - no stroke ring.** Tried (R1): the class's hit discs took the stroke and every bead grew a ring
  several times its size, and the rule that only a shape drawn with a stroke takes the highlight stroke
  is the GM's (2026-08-28).
- **D4 - the tool zooms by the page's key, not by Ctrl+wheel.** Both are the page's own zoom; the key
  needs no pointer position and is the one way feature 134 documents.
- **D5 - the tool defect is fixed here, not filed** (Principle XIV: a defect found in the course of other
  work is fixed in that work). Its browser test opened in vector mode already, so the loop it names was
  never exercised in a browser; a small viewport makes the same page open in raster mode, and the test
  now proves the loop.
- **D6 - raster mode's other rulings stay untested in a browser.** The rolled-page tests retired on
  2026-09-07 were the only browser coverage of raster mode (leaf hiding, the placard, the id map hit);
  the small-viewport technique this feature uses makes each cheap to add on the synthetic page, and that
  is recorded here rather than done, because it is not what was asked.

## Out of scope

- Moving the 0.45 wash (feature 201 D2, the GM's constant).
- A browser sweep of raster mode's other rulings (D6).
- Any change to the beads' own drawing (color, size, the 0.85 opacity), to the highlight color, or to
  the vector page.

## Review history

- **Round 1 (2026-09-13, MODE 2): FAITHFUL.** Every clause of the request carried; the page-lit fix judged
  in scope under Principle XIV; nothing unrequested; scope not larger. Three asides, all taken in this
  round: FR-003 no longer asserts a census of fill-only mark classes nobody ran (the comment claims what
  R1 measured); D2's reason is the measurement rather than the drawing convention, since a lit-only
  override would not touch the unlit map; SC-002 says the contact sheet decides, not the tool's changed
  count.

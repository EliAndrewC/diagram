# Feature 203 - the placard stays on top

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the mechanism (the lit scrub above the image, not the
card's z-order) and why the fix reaches the scale bar.
**Predecessors**: feature 201 (raster mode hides leaf ink outside the lit class; the wash); 200 (the
lit class above the image); 156 (the placard is the `place` class; the scale bar keeps `cls="-"`).

## Summary

The GM: after hovering the title card and moving away, *"suddenly the scrub land is laid over top"*.
The card's z-order does not change (R1): in raster mode the lit class is drawn above the image, the
image holds the card, and the scrub has blades under the card that the vector page hides beneath it -
so once the pointer sits on the scrub around the card, the lit blades paint over the image's card. The
fix keeps the placard on top in raster mode as it is on the vector page: its card, its name and its
scale bar are always vector, drawn after everything, so a lit class beneath stays beneath.

## Functional requirements

- **FR-001** In raster mode the placard's ink is never hidden: the `place` class's leaves (the card's
  two rectangles, the name) and the scale bar's lines are displayed in both modes, above every lit
  class - they are the last things drawn. Visually the card is what it was on the vector page: opaque
  parchment, nothing lit shows through it, the scale bar and its captions on it.
- **FR-002** The writer marks the scale bar's group `class="scale"` so the stylesheet can name it. It
  stays `cls="-"` - not highlighted, no `data-k` - as the GM ruled on 2026-08-29; the SVG text gains one
  attribute, and the PNG is unchanged.
- **FR-003** Hovering the card still lights it (the wash on the card, the name in ink - feature 201)
  and clicking it still opens the place card's modal; leaving it leaves the card exactly as it was.
- **FR-004** Tests: the browser test on the Kuwabata fixture, in raster mode - light the scrub, and
  the pixel at the card's center is the card's parchment, not the highlight; a pixel on the scale
  bar's line is the bar's ink, not the card's; the card's and bar's leaves are displayed with nothing
  lit; after lighting and unlighting the card the same holds. A unit test that the writer's scale bar
  carries the marker. With FR-001's stylesheet exemption reverted, the scrub-lit pixel assertion
  fails - shown once (SC-002).
- **FR-005** Nothing else changes: not the wash, not the id map, not the vector page.

## Success criteria

- **SC-001** On Kuwabata in raster mode with the scrub lit, no highlight color inside the card.
- **SC-002** With the exemption reverted the assertion fails; shown once.
- **SC-003** `make done` green; the page opened by the session, the card hovered, left, the scrub lit.

## Decisions Recorded

- **D1 - the placard is vector in both modes**, the one element exempt from raster mode's hiding: it is
  the map's decal, drawn last on purpose, and the wash cannot protect it from a lit stroke class.
- **D2 - the scale bar gets a marker, not a class.** The GM's ruling that the bar is not the place
  stands; a `class="scale"` on its group is a name for the stylesheet, not a hover target.

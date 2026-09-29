# Feature 290 - the perceptual label order

**Feature**: 290-perceptual-label-order | **Created**: 2026-09-29 | **Status**: Draft
**Input**: the GM's ruling, verbatim in [`request.md`](request.md).

## Summary

The one caption placer names a small thing from beside it at the first free place in a ranked list. Feature 289 set
that list by the GM's deviation (above, below, left, right, then the textbook's corners). The GM now adopts the
published, user-tested order instead - PerceptPPO, from Bobák, Čmolík and Čadík's 2024 study: top, bottom, right, top
right, bottom right, left, top left, bottom left - and the record calls it a standard, not a deviation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The ranked positions around a point subject MUST be PerceptPPO's eight, in its order: directly above,
  directly below, right, upper right, lower right, left, upper left, lower left - and no others (the two "slightly"
  positions of the textbook order are not in it).
- **FR-002**: The fallback search's sides MUST follow the same order where it walks them in an order (above, below,
  right, left). Everything else about placement is unchanged.
- **FR-003**: The research record's entry on where a caption sits MUST say the maps follow the published user-tested
  order, cite it, and no longer call the order a deviation; the placer's standard says the same where the order is
  defined.
- **FR-004**: The maps MUST be regenerated with it: the four hand sheets now, the generated maps at their next render.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): unit tests prove the order with positions blocked in turn - above, below, right, upper
  right, lower right, left, upper left, lower left - and the placer's other tests pass with only position names changed.
- **SC-002** (FR-003): the record's entry names PerceptPPO as the order followed, cited, and calls nothing a deviation
  in its place; `make done` is green.
- **SC-003** (FR-004): the four sheets are regenerated.

## Decisions Recorded

- **The standard as published.** PerceptPPO is an eight-position order; the textbook order's two "slightly" positions
  are not part of it and are dropped, rather than kept after it (a mix would be neither standard).
- **Supersedes feature 289's order**; 289's research and citations stand, and its record paragraph is rewritten.
- **A correction to 289** (found by this feature's quote-check, confirmed on Mapbox's style specification, which says of
  the anchor `top`: "The top of the text is placed closest to the anchor"): the Mapbox example's anchors top, bottom,
  left, right put the label below, above, right and left of its point - not above, below, left, right as feature 289
  recorded, so the GM's order was never that example's. The record now says only that the example tries the four
  places beside the point and no corner; told to the GM at hand-back.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-29): FAITHFUL. Dropping the two "slightly" positions is the standard as
published - the study says so itself: *"with current advancements in typesetting, the necessity for these auxiliary
positions has become obsolete"*; appending them would mix two orders. The fallback's sides follow PerceptPPO (right
before left); leaving 289's left-before-right would keep part of the deviation the GM dropped.

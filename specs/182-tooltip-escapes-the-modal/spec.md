# Feature 182 - the glossary tooltip escapes the modal

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessor**: feature 134 (the glossary tooltips, GM 2026-08-28: every occurrence of a defined term in a
modal is a hover tooltip)

## The defect

A glossary term's definition is drawn as a CSS `::after` box on the term's own `<span class="gl">`,
positioned absolutely below the word. The explanation dialog scrolls its own content (`overflow: auto`),
so a box that extends past the dialog's edge is CLIPPED by the dialog and, being content inside it,
GROWS the dialog's scrollable width - the horizontal scroll bar the GM saw. A term near the right edge
therefore shows a cut-off definition and a scroll bar.

## Functional requirements

- **FR-001** The tooltip MUST NOT be clipped by the modal and MUST NOT give the modal a horizontal scroll
  bar. It may extend past the modal's left or right edge (the GM: *"it is okay for the tool tip to
  extend off the right or the left of the model"*).
- **FR-002** The tooltip MUST stay within the page: its left and right edges MUST lie inside the viewport
  (the GM: *"it should not extend off the right or left of the page itself"*). Where a definition placed
  at the word would cross the viewport's edge, it is shifted along the word's line until it fits, with a
  small margin from the edge.
- **FR-003** The tooltip shows the same definition, for the same terms, in the same modals, on the same
  hover, as today: what changes is WHERE the box is drawn, not what it says or when. The dotted underline
  and the help cursor on a defined term are unchanged.
- **FR-004** The tooltip is drawn as ONE element OUTSIDE both dialogs, positioned in viewport coordinates
  from the hovered word's box, and it disappears when the pointer leaves the word, when the content
  under it scrolls, and when the dialog closes - so a stale box is never left floating over the page.
- **FR-005** The browser test MUST assert the new behavior: hovering a defined term shows the tooltip
  with its definition, the tooltip lies inside the viewport, and the explanation dialog has no horizontal
  overflow while it is shown - in a viewport narrow enough that a box placed at the word would have
  crossed the edge, so the clamp is exercised rather than assumed.
- **FR-006** The SVG and the PNG are untouched (feature 134 FR-010). Only `interactive/assets/page.js`,
  `page.css` and the markup `page.py` writes change.

### What this feature does not do

- **FR-007** It does not change the glossary's terms or definitions, which terms are wrapped, the
  modals' text, or anything about the references modal.

## Decisions Recorded

- **D1 - a DOM element outside the dialogs, positioned from JavaScript, rather than a CSS-only fix.** The
  dialogs are centered with `transform: translate(-50%, -50%)`, and a transformed ancestor becomes the
  containing block of every `position: fixed` descendant - so a fixed-position `::after` INSIDE the
  dialog would still be clipped by the dialog's `overflow: auto`. Nothing drawn inside the dialog can
  escape it; the box has to live outside, and then it needs the word's viewport box to sit under it,
  which is what the script supplies. Declined: `overflow: visible` on the dialog (it would lose the
  dialog's own scrolling for long explanations) and `overflow-x: hidden` (it would hide the scroll bar
  and still clip the tooltip).
- **D2 - the box goes BELOW the word, and ABOVE it when below would leave the viewport.** The GM spoke
  only of the left and right edges; the bottom edge is the same failure in the other axis and costs one
  comparison, so it is handled the same way rather than left for a second report. Rendering decision;
  nothing physical behind it.
- **D3 - the margin from the viewport edge is 8 px.** Enough that the box does not touch the window's
  edge; a guess at a legibility constant, labeled as one.

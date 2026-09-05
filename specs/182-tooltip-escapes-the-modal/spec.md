# Feature 182 - the glossary tooltip escapes the modal

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5) - cleared for implementation (constitution XVI).
Round 1 returned two items: hide-on-scroll would have changed WHEN the box shows (FR-003 promised it
would not), so the box is repositioned on scroll instead; and the bottom-edge rule was argued from
convenience and carried by no requirement - it now rests on the GM's *"remain visible on the page"* and
the fact that a fixed dialog's page does not scroll, and FR-002 carries it. Round 2 returned none; its
aside (the vertical case where neither below nor above fits) is settled in FR-002.
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
- **FR-002** The tooltip MUST stay within the page: its box MUST lie inside the viewport (the GM: *"the
  tooltip should remain visible on the page, and so it should not extend off the right or left of the
  page itself"*). Where a box placed at the word would cross the viewport's left or right edge it is
  shifted along the word's line until it fits, with a small margin from the edge; where it would cross
  the bottom it is placed above the word instead (D2). When the definition is wider than the viewport
  can hold at any offset - a very narrow window - the box is capped to the viewport's width less the
  margins, so it wraps rather than overflows. Vertically, when neither below nor above the word fits,
  the box's top is clamped inside the viewport (it then overlaps the word - the one case where reading
  the definition costs seeing the word, accepted over a box that cannot be read at all).
- **FR-003** The tooltip shows the same definition, for the same terms, in the same modals, on the same
  hover, as today: what changes is WHERE the box is drawn, not what it says or when. The dotted underline
  and the help cursor on a defined term are unchanged.
- **FR-004** The tooltip is drawn as ONE element OUTSIDE both dialogs, positioned in viewport coordinates
  from the hovered word's box. It disappears when the pointer leaves the word and when the dialog closes
  (an element outside the dialog would otherwise be left floating over a closed modal - a defect the fix
  itself would introduce). While the pointer stays on the word and the dialog's content scrolls under
  it, the box is REPOSITIONED from the word's new place, so it stays attached to the word exactly as the
  CSS box did - FR-003's "not when" holds as written.
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
- **D2 - the box goes BELOW the word, and ABOVE it when below would leave the viewport.** The GM's
  requirement is that *"the tooltip should remain visible on the page"*; the left and right edges are the
  cases they saw. Once the box lives outside a `position: fixed` dialog in viewport coordinates, a box
  hanging below the bottom of the window is not on the page at all - nothing scrolls it into view, since
  the page itself does not scroll - so the same requirement decides the bottom edge, and above-the-word
  is the placement that keeps it visible. Rendering decision; nothing physical behind it.
- **D3 - the margin from the viewport edge is 8 px.** Enough that the box does not touch the window's
  edge; a guess at a legibility constant, labeled as one.

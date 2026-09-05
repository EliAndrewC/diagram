# Tasks - feature 182

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 2). Request: [`request.md`](request.md).

Every task is `research: rendering` - a page convention with nothing physical behind it.

- [x] T01 FR-001/FR-002/FR-004/D1/D2: `page.js` positions one `#tip` element outside the dialogs from the hovered term's box, clamped to the viewport; hidden on leave, scroll and close. `page.css` styles it and drops the `::after` rule
      research: rendering
      verify: DONE. One `#tip` sibling of the dialogs; `placeTip()` from the word's viewport box, TIP_MARGIN 8 px, below-then-above, max-width capped to the viewport, top clamped; repositioned on scroll (capture), hidden on leave, on `openRefs`, in `closeDialog` synchronously and in the explanation's `close` listener. `.gl:hover::after` gone
- [x] T02 FR-005: the browser test hovers a term in a narrow viewport and asserts the tooltip is shown, inside the viewport, with no horizontal overflow on the dialog
      research: rendering
      verify: DONE. In a 420 x 640 viewport the test picks the RIGHTMOST defined term in the bund's modal, proves the box placed at the word would have crossed the edge (so the clamp acted), and reads: not hidden, its text is the definition, not inside a dialog, all four edges inside the viewport, `scrollWidth == clientWidth` on the dialog; hidden on leave and on Escape. 20 passed in the browser file; `make quick` clean
- [x] T03 FR-006: regenerate the reference hamlet's page; `make done` green; the answer to the GM
      research: rendering
      verify: DONE. Reference page regenerated (17.8 s) and carries `#tip`. `make done` GREEN in 543 s: 2,960 passed, 2 skipped, 1 xfailed, 22,618 statements 0 uncovered 100%, hamlet floor 100%. `PAIR_OK` given: only the tooltip's placement changed, no drawn ink. Landing deferred to feature 183's push: the clone already held 183's research entries and spec, and neither route lands a feature with open tasks
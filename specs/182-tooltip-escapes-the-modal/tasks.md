# Tasks - feature 182

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Every task is `research: rendering` - a page convention with nothing physical behind it.

- [ ] T01 FR-001/FR-002/FR-004/D1/D2: `page.js` positions one `#tip` element outside the dialogs from the hovered term's box, clamped to the viewport; hidden on leave, scroll and close. `page.css` styles it and drops the `::after` rule
      research: rendering
      verify: the browser test (T02)
- [ ] T02 FR-005: the browser test hovers a term in a narrow viewport and asserts the tooltip is shown, inside the viewport, with no horizontal overflow on the dialog
      research: rendering
      verify: `make test-file` on the browser file green; `make quick` clean
- [ ] T03 FR-006: regenerate the reference hamlet's page; `make done` green; the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (no drawn ink moved)

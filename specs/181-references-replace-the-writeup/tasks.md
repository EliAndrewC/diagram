# Tasks - feature 181

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 1). Request: [`request.md`](request.md).

Every task is `research: rendering` - a page convention with nothing physical behind it.

- [ ] T01 FR-001/FR-002/FR-005: `page.js` - opening the references hides the explanation (a class, not a close); closing them by any route shows it again; shade and pin kept
      research: rendering
      verify: the browser test drives button, title link and Escape, and reads the explanation's computed display each time
- [ ] T02 FR-003/FR-004: the title "<Name> references" with `<Name>` a link sharing the button's handler; `page.css` for the hidden state and the link
      research: rendering
      verify: the browser test reads the title text and the link's text; `test_page.py` sees the markup
- [ ] T03 FR-006: the browser test and the page tests updated
      research: rendering
      verify: `make quick` clean; the browser test green at the gate
- [ ] T04 FR-007: regenerate the reference hamlet's page and look; `make done` green; the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (no drawn ink moved)

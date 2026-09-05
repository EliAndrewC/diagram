# Tasks - feature 184

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

- [x] T01 FR-001/FR-002: `page.css` - the three link rules take `text-decoration: none`
      research: rendering
      verify: DONE. `a.sib`, `a.q`, `dialog#references h2 a.back` -> `text-decoration: none`; colors and hover colors untouched; the why at the point of change
- [x] T02 FR-003: the browser test reads the computed `text-decoration-line` of a sibling link, a question link and the title link
      research: rendering
      verify: DONE. The references test reads `textDecorationLine` of the title link and a question link, the sibling-link test reads it on `a.sib`: all "none". Browser file green
- [ ] T03 FR-004: regenerate the reference hamlet's page; `make done` green; the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (no drawn ink moved)

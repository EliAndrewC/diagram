# Tasks - feature 184

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

- [ ] T01 FR-001/FR-002: `page.css` - the three link rules take `text-decoration: none`
      research: rendering
      verify: the browser test (T02)
- [ ] T02 FR-003: the browser test reads the computed `text-decoration-line` of a sibling link, a question link and the title link
      research: rendering
      verify: `make test-file` on the browser file green
- [ ] T03 FR-004: regenerate the reference hamlet's page; `make done` green; the answer to the GM
      research: rendering
      verify: green gate; `PAIR_OK` with the reason (no drawn ink moved)

# Tasks - feature 244

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Phase 1 - the knob and the glyph (FR-001, FR-002, FR-007)

- [x] T01 `caravan_inn_form` registered beside `byre_form` with its why; `inn(form=None)` pins or
      resolves it, draws both forms, writes the form to meta and the record; tests per form, the
      refusal, two seeds differing
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. The research pass is 238 R2/R2a and 244 R1; source-reader READ kotobank at HTTP 200; quote-check and source-applicability in R3 and T03. Knob registered with both rulings in its why; inn() pins a passed form or resolves the knob; wagon one window row, hatago two rows and the inter-story eave; form in meta and the record. Tests: 44 pass in test_civic_grounds.py - both forms' window counts, the refusal, twelve seeds rolling both values, a map-level pin honored. make done green, 3871 passed, floor held, 101 s.

## Phase 2 - the record (FR-003, FR-004, FR-005)

- [x] T02 `towns.html`'s caravan-inn section: the ruling replaces the open question; both forms accurate
      to their analogues; the umayado leg at R1's strength with fn-30 from `kotobank-umayado`; the form
      rule as a spec paragraph; `make citations`; the docstring
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. The open-question sentence and the Evidence comment's line are gone; both forms stated accurate to fn-25 and fn-26; the umayado leg split as the applicability judgment split it (definition carries the institution, the 1913 sentence alone the arrangement, earliest-example-of-the-sense dating it late); the cart yard under hatago labeled a guess; fn-30 with both passages; fn-31 an absence note on the trade-route premise the section had carried unfootnoted (R3); the form rule as the first spec paragraph, knob name in a comment; citations derived; docstring names both analogues and both rulings.

## Phase 3 - the checks (FR-006)

- [x] T03 `source-applicability` on the new key before it is relied on; `quote-check` and
      `record-format` on the changed section; `_entry_owed.py` consulted
      research: rendering
      verify: DONE. DONE. kotobank-umayado APPLICABLE-WITH-LIMITS, seven limits named, every one now in its write-up. quote-check: fn-30 READABLE / VERBATIM / SUPPORTS, two PARTIALs applied, one unfootnoted assertion found and noted (R3). record-format: seven vocabulary items applied, one session note commented, no history; two neighbors fixed under Principle XIV. _entry_owed.py names no pair - no modal is written from this section.

## Phase 4 - the close (FR-007)

- [x] T04 `make done` green, the push clean, 242's amendment landing with it
      research: rendering
      verify: DONE. DONE. make done green on the engine content (3871 passed, floor held, 101 s); page-check 777 passed after the record and glossary changes. 242's amendment does NOT land with it after all: a feature with open tasks may land only its own specs/ alone, so it was set aside in a forward commit (R2) and is pushed by itself immediately after this feature - the plan's phase 4 said with, and the mechanics said after.

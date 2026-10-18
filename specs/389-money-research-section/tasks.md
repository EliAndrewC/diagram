# Tasks - feature 389, a money section of the research record

Every task is about how the record is organized and how a request is worked, not about what was built, farmed or lived in:
each is `research: rendering`. The research questions themselves come later, each under its own feature.

## Occasions

- none: no glyph, caption, placement rule, modal or map changes

## Tasks

- [x] T01 The `money` subject tag (plan D1; FR-001)
      research: rendering
      verify: DONE. the money tag in research/tags.json; make record CHECK=1 builds cleanly
- [x] T02 The loader accepts a section `awaiting` its first question and refuses a stale `awaiting` (`contents.py`), and the `money` section with its `awaiting` line in `research/contents.json` (plan D2; FR-001, FR-002, FR-005)
      research: rendering
      verify: DONE. contents.py Section.awaiting + idle_rules exemption and stale refusal; money section with awaiting in contents.json; test_money_section 4 passed, make done green
- [x] T03 The protocol file `research/money-requests.md`, including that the first money question's feature deletes the section's `awaiting` line, and its row in `research/CLAUDE.md` (plan D3; FR-003, FR-004)
      research: rendering
      verify: DONE. research/money-requests.md (request 3 parts, answer 3 parts, impl-check line, awaiting deletion) + research/CLAUDE.md load-table row; pinned by test_money_section
- [x] T04 The test (plan D4; SC-001 - SC-003), then `make quick` and land (plan T01)
      research: rendering
      verify: DONE. tests/interactive/test_money_section.py 4 passed; tests/interactive 5151 passed; make done green (344 s)

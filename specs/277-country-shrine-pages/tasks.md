# Tasks - feature 277, country shrine sheets as interactive pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D7).

- [x] T01 The shrine kinds in `compound_kinds/shrine.py`, registered (D1, D2; FR-002)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. 16 kinds in compound_kinds/shrine.py, each carried from its folded item's class and reason and citing the record's existing sections (254/268/270/272/273 research, already read, quoted and checked); no new source; test_compound_kinds green
- [x] T02 The country-shrines items in `types.json` folded to kinds; `programs.md` regenerated (D3; FR-006)
      research: rendering
      verify: DONE. 18 country-shrines items folded to kinds with forms/site/optional kept; programs.md regenerated; declaration tests follow the fold
- [x] T03 The sheet's untagged ink tagged; the gen writes the page; the Map notes block (D4, D5, D7; FR-001, FR-003, FR-005)
      research: rendering
      verify: DONE. 5 elements tagged; gen writes the page with a clean census; Map notes block for 8 shared kinds read by the page; PNG pixel-identical
- [x] T04 The tests over every country-shrine sheet and the widened closure, red on a seeded fault (D6; FR-004)
      research: rendering
      verify: DONE. shrine sheets in the census, closure over drawn or program-named kinds, program kinds registered; red on an untagged element, an unknown sheet kind and an unknown program kind
- [x] T05 PNG and pack audit identical before and after; `make done`; push (SC-004)
      research: rendering
      verify: DONE. PNG pixel-identical to the baseline (ImageChops bbox None), pack audit output identical; make done green 2026-09-28

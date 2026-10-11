# Tasks: Rename the `grave island` class to `field grave` (feature 349)

**Input**: plan.md (D1-D6). Tooling-free rename; no map moves.

## Occasions

- none: a class key renamed over an unchanged glyph - no element new to a map, no glyph redrawn or re-placed

- [x] T01 the key renamed in the engine, the registry and the page data; the modal moved with its Name (D1, D2, D5)
      research: rendering
      verify: DONE. make test-file tests/interactive green (5132), page-check green
- [x] T02 the snapshot's renaming table carries it (D3)
      research: rendering
      verify: DONE. SINCE_189 carries grave island -> field grave; test_classes_docstrings green
- [x] T03 Kashikawa and Mizuguchi regenerated; Kashikawa's notes key follows (D4)
      research: rendering
      verify: DONE. make map on kashikawa and mizuguchi; kashikawa.json differs from main only in ink_classes (field grave 3); notes key moved
- [x] T04 the checks (D6) and the gate
      research: rendering
      verify: DONE. impl-drift IN-STEP 6 of 6 (one claim added for its UNCLAIMED); modal-form PASS; make done green

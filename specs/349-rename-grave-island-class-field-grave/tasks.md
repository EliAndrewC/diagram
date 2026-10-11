# Tasks: Rename the `grave island` class to `field grave` (feature 349)

**Input**: plan.md (D1-D6). Tooling-free rename; no map moves.

## Occasions

- none: a class key renamed over an unchanged glyph - no element new to a map, no glyph redrawn or re-placed

- [ ] T01 the key renamed in the engine, the registry and the page data; the modal moved with its Name (D1, D2, D5)
      research: rendering
      verify: make test-file FILE=tests/interactive/ green
- [ ] T02 the snapshot's renaming table carries it (D3)
      research: rendering
      verify: tests/interactive/test_classes_docstrings.py green
- [ ] T03 Kashikawa and Mizuguchi regenerated; Kashikawa's notes key follows (D4)
      research: rendering
      verify: make map on both; Kashikawa's manifest differs only in ink_classes, which names field grave
- [ ] T04 the checks (D6) and the gate
      research: rendering
      verify: impl-drift IN-STEP on every owed claim; modal-form PASS; make done green

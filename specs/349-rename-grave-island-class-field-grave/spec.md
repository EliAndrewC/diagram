# Feature Specification: Rename the `grave island` class to `field grave` (settlement-review, Kashikawa 2026-09-28)

**Status**: Filed - from future-work/farming-communities.md, "Rename the `grave island` class to `field grave` (settlement-review, Kashikawa 2026-09-28)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

Feature 267 made the field grave a knob - an island inside a plot (the Chinese form) or a grave in a plot's corner (the
Japanese form) - but the page class is still keyed and named `grave island`, so a corner-form hamlet's hover says
"grave island" while its own feature note says the grave is "not an island". Kashikawa's review raised it twice; it was
accepted for 267 with that note standing in. The rename touches 17 files: the ink tags in `settlement/fields/features.py`,
`GraveIsland` in `interactive/classes/water_and_ways.py`, the glossary term, `place.json`, `siblings.json`,
`overlap/taxonomy.py`, `tools/placement_stages.py`, the Mizuguchi and Kashikawa manifests' `ink_classes`, and the pinned
snapshot `tests/fixtures/classes_before_189.json` (through `SINCE_189`, the renaming table the snapshot test keeps).

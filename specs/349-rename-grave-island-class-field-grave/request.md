The entry as filed (feature 330, from the settlement-review of Kashikawa, 2026-09-28):

Feature 267 made the field grave a knob - an island inside a plot (the Chinese form) or a grave in a plot's corner (the
Japanese form) - but the page class is still keyed and named `grave island`, so a corner-form hamlet's hover says
"grave island" while its own feature note says the grave is "not an island". Kashikawa's review raised it twice; it was
accepted for 267 with that note standing in. The rename touches 17 files: the ink tags in `settlement/fields/features.py`,
`GraveIsland` in `interactive/classes/water_and_ways.py`, the glossary term, `place.json`, `siblings.json`,
`overlap/taxonomy.py`, `tools/placement_stages.py`, the Mizuguchi and Kashikawa manifests' `ink_classes`, and the pinned
snapshot `tests/fixtures/classes_before_189.json` (through `SINCE_189`, the renaming table the snapshot test keeps).

The GM, 2026-10-10, on the session's review of the open hamlet features - its proposal: "349: the rename is mechanical (17
files, no judgment) - I'd do it as a tweak rather than a feature", among three merges - and its question "Do you want me to
do the three merges and the 349 rename?":

Yes, please.

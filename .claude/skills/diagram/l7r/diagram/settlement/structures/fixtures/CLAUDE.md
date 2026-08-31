# `fixtures/` - the public fixtures and their siting

Split from the 1,212-line `fixtures.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

`PublicFixturesMixin` exists ONLY to preserve the single import and the position in the `class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs no import and the partition can be re-cut later without touching core.py.

## Look here when

| file | look here when |
|---|---|
| `_helpers.py` (191) | the module-level helpers lifted out for unit testing (GM 2026-08-28) - `pick_caption_seat`, `kosatsuba_affordances`, `kosatsuba_anchor` |
| `boards.py` (618) | the drawn fixtures themselves - the fire tower, the kosatsuba notice board, and the caption engine the board carries |
| `siting.py` (429) | WHERE a fixture goes: the water and lane-clearance probes, and the two placement passes (`place_kosatsuba`, `place_punishment_spot`) |
| `__init__.py` | the composed surface only - the class this package exists to provide, plus the module-level helpers the tests import by name. Never add logic here |

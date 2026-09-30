# `homestead_parts/` - yards, gardens, groves and stands

Split from the 1,353-line `homestead_parts.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

`HomesteadPartsMixin` exists ONLY to preserve the single import and the position in the `class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs no import and the partition can be re-cut later without touching core.py.

## Look here when

| file | look here when |
|---|---|
| `_helpers.py` (34) | the module-level helper `_belt_axis` |
| `yards.py` (169) | the threshing yard: its size from the house's, whether it fits, where it goes, and how it is drawn |
| `gardens.py` (110) | the kitchen garden and the farm shed it shares a corner with - dimensions, fit, and the spot search |
| `groves.py` (252) | the homestead grove (yashikirin): which way the wind comes from, whether this house gets one, the L-belt arms, and the drawing |
| `stands.py` (545) | the two big stands - the household bamboo stand and `village_grove`, the settlement-scale windbreak |
| `bamboo_keepout.py` | the copse's keep-out round a bamboo stand (`grown_ring`, `copse_bamboo_reach`, feature 280) and `stand_spares_seats`, the one predicate every bamboo placer reads to leave the reserved copse seats free (feature 287 woods W25) - split out of `stands.py` at the 1,000-line bar |
| `grove_blocks.py` | the keep-outs of ONE grove fill indexed once and asked per candidate clump (`GroveBlocks`, `Seats`; feature 218), and `BankNear`, a reach that stops at the brook (feature 261; moved here from `stands.py` at the 1,000-line bar, feature 287) - open it when `village_grove` refuses or accepts a seat you did not expect, or when a new keep-out joins the fill |
| `keepouts.py` (265) | what a grove or a stand may NOT cover: corridor buffers, watercourses, canopy crowns and the urban keepouts |
| `farmstead.py` (39) | the three farmstead helpers feature 120 moved here - attaching a grove, finding appurtenances, and the nudge sequence |
| `__init__.py` | the composed surface only - the class this package exists to provide, plus the module-level helpers the tests import by name. Never add logic here |

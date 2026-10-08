# `homestead_parts/` - yards, gardens, groves and stands

Split from one `homestead_parts.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens). **Load only the file the task calls for**; this index is the map.

`HomesteadPartsMixin` exists ONLY to preserve the single import and the position in the `class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs no import and the partition can be re-cut later without touching core.py.

## Look here when

| file | look here when |
|---|---|
| `_helpers.py` | the module-level helper `_belt_axis` |
| `yards.py` | the threshing yard: its size from the house's, whether it fits, where it goes, and how it is drawn |
| `gardens.py` | the kitchen garden and the farm shed it shares a corner with - dimensions, fit, and the spot search |
| `groves.py` | the homestead grove (yashikirin): which way the wind comes from, whether this house gets one, the L-belt arms, and the drawing |
| `grove_sides.py` | how many sides a farmstead grove takes and which (feature 291): the roll tables (`GROVE_SIDES`, the flood table), `grove_faces` (deep, thin, the front) for any wind and side count, and `bundle_turn` - the square's symmetry carrying the canonical farmstead to the map's wind. A pure leaf |
| `grove_rules.py` | the grove's rules read off a FINISHED manifest (feature 291): every rolled side planted, the deep stand windward, no garden's morning sun cut - run by `tools/cohort_audit` on every roll |
| `stands.py` | the two big stands - the household bamboo stand and `village_grove`, the settlement-scale windbreak |
| `stocking.py` | the windbreak's stocking rules - `grove_stocked`, `stocked_copse`, `main_stand`, `stocked_box`, `record_box` - open it when a grove's clumps are dropped as stragglers or its recorded box looks wrong; split out of `stands.py` at the 1,000-line bar (feature 328), re-exported there |
| `bamboo_keepout.py` | the copse's keep-out round a bamboo stand (`grown_ring`, `copse_bamboo_reach`, feature 280) and `stand_spares_seats`, the one predicate every bamboo placer reads to leave the reserved copse seats free (feature 287 woods W25) - split out of `stands.py` at the 1,000-line bar |
| `wood_goal.py` | the homesteads' wood drawn at its roll (feature 294 B9): the part of the register's range the ground can hold (`attainable_band`), the roll over it, the copse's goal, and the trim back to it (`trim_to_goal`) - open it when a map's `homestead_wood_ft2` drawn and rolled disagree |
| `grove_blocks.py` | the keep-outs of ONE grove fill indexed once and asked per candidate clump (`GroveBlocks`, `Seats`; feature 218), and `BankNear`, a reach that stops at the brook (feature 261; moved here from `stands.py` at the 1,000-line bar, feature 287) - open it when `village_grove` refuses or accepts a seat you did not expect, or when a new keep-out joins the fill |
| `keepouts.py` | what a grove or a stand may NOT cover: corridor buffers, watercourses, canopy crowns and the urban keepouts |
| `farmstead.py` | the three farmstead helpers feature 120 moved here - attaching a grove, finding appurtenances, and the nudge sequence |
| `belt_law.py` | the windbreak's law, read and repaired where the belt is planted (feature 287) |
| `fixture_seats.py` | a household's farmstead fixtures laid as PARTS of its homestead bundle (feature 287): the bath room joined to the house, the wood shed a ken off a wall |
| `tree_shade.py` | does a tree stand in a threshing yard's or a garden bed's sun? (GM 2026-10-02: *"no canopy trees should be exempt"*) |
| `wood_share.py` | the household's share of the wood floor, reserved at its seat (feature 287) |
| `__init__.py` | the composed surface only - the class this package exists to provide, plus the module-level helpers the tests import by name. Never add logic here |

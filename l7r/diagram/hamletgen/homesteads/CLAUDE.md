# `homesteads/` - the homesteads and what stands among them

Split from one `homesteads.py` by feature 173, as LAYERS emitted bottom-up (every cross-module reference points backwards, so no import cycle). **Load only the file the task calls for**; this index is the map.

## Look here when

| file | look here when |
|---|---|
| `seats.py` | where a homestead may sit - the front row, the lane frontage that fronts it, the cluster's aspect ratio, and whether a seat is allowed at all |
| `bamboo.py` | the household bamboo strip: whether a strip is blocked, and the per-household placement |
| `fixtures.py` | what stands in a farmstead's yard - the hamlet's fixture shares and forms (`fixture_quota`, `fixture_forms`, handed to the seating) and `farmstead_fixtures`, which DRAWS each fixture where the bundle laid it (feature 287, homes H32: `settlement/homestead_parts/fixture_seats.py` lays them - the bath room joined to the house, the wood shed a ken off a wall, feature 280; the field pit takes its own form at the hinterland call where it can) |
| `retirement.py` | the retirement house (269 B42, 0004): the `family_form` knob (one roof, or a retirement house in some yards), its share, size and seat off the farmhouse's back or flank, recorded under `retirement_houses` - never a household - and seated after the byres in `stage_appurtenances` |
| `wells.py` | the public wells - how many a settlement of this size wants, and the pass that seats them |
| `growth.py` | how a NUCLEATED cluster is seated (feature 308): grown from its first house, each next house offered from a standing one at the distance their footprints part - the envelope, the woodlot, the path out and the sun its yard and beds are owed - jittered, widening while households are left (`grow_the_margin`, `footprint`, `seat_toward`, `GROW_LEVELS`) |
| `capacity.py` | the DISPERSED form's last pass - the exhaustive offer of the free ground, its dry-spell cap and the near-miss rescue - and the margin ladder every form shares (`margin_ladder`, `seating_mark`, `unseat_to`, `SiteRefused`) |
| `household_ways.py` | THE TRACK OUT CHOSEN ONCE, when the last house stands (feature 320, FR-008): `chose_the_track` asks `track.choose_track_out` with the homesteads as seated standing in for the undrawn farmsteads (`seated_parts`, wood seats included); `near_the_cluster` gives the stretch the households' ways are laid to - nothing of a way is reserved while houses are seated |
| `stages.py` | STAGES 5 and 6 - the homesteads themselves and what stands among them. Read this first |
| `seat_geometry.py` | the seating's leaf geometry (feature 316 split it from `stages.py`, which re-exports it): the brook push, the seat's turn, the drawn cluster band and the declared cluster shape |
| `boundary.py` | THE SITE BOUNDARY (feature 226): the ground a homestead may stand on, computed ONCE |
| `region.py` | THE SEAT REGION (feature 297): where a homestead can stand and a door can reach the access tree, computed once per change to what stands; every round's seats are drawn only from it |
| `holds.py` | the parts the seating laid, held in the registry of what stands until they are drawn (feature 287) |
| `rows.py` | THE ROW VILLAGE (feature 291): a linear hamlet's farms in rows along their streets, never in ranks behind a row |
| `row_rules.py` | the row village's and the grove farm's rules, read off a finished manifest - pure functions, each returning what breaks its rule |
| `farm_water.py` | a DISPERSED farm's own water as a channel led into its grounds (feature 291) |
| `persimmon_reseat.py` | the persimmon a household could not keep, given to one that has room (feature 315) |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

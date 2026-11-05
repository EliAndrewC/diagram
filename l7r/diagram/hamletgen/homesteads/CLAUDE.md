# `homesteads/` - the homesteads and what stands among them

Split from one `homesteads.py` by feature 173, as LAYERS emitted bottom-up (every cross-module reference points backwards, so no import cycle). **Load only the file the task calls for**; this index is the map.

## Look here when

| file | look here when |
|---|---|
| `seats.py` | a seated cluster's drawn aspect, read on its own axis (`cluster_aspect`); the front row and the lane frontage are the Rust's since feature 444 T30 (`rust/phases/src/homesteads/grove_seat.rs`) |
| `bamboo.py` | the household bamboo strip: whether a strip is blocked, and the per-household placement |
| `fixtures.py` | what stands in a farmstead's yard - the hamlet's fixture shares and forms (`fixture_quota`, `fixture_forms`, handed to the seating) and `farmstead_fixtures`, which DRAWS each fixture where the bundle laid it (feature 287, homes H32: `settlement/homestead_parts/fixture_seats.py` lays them - the bath room joined to the house, the wood shed a ken off a wall, feature 280; the field pit takes its own form at the hinterland call where it can) |
| `retirement.py` | the retirement house (269 B42, 0004): the `family_form` knob (one roof, or a retirement house in some yards), its share, size and seat off the farmhouse's back or flank, recorded under `retirement_houses` - never a household - and seated after the byres in `stage_appurtenances` |
| `wells.py` | the public wells - how many a settlement of this size wants, and the pass that seats them |
| `growth.py` | which plans GROW their cluster (`grows`) and the built share a grown map reports (`built_share`); the growth itself is the Rust's since feature 444 T30 (`rust/phases/src/homesteads/place.rs` `grow`) |
| `capacity.py` | the margin ladder every form shares (`margin_ladder`, `seating_mark`, `unseat_to`, `SiteRefused`); the exhaustive pass is the Rust's since feature 444 T30 (`grove_rounds.rs`) |
| `household_ways.py` | THE TRACK OUT CHOSEN ONCE, when the last house stands (feature 320, FR-008), and EVERY HOUSEHOLD'S WAY laid in the gaps - both in Rust since feature 444 T30 (`l7r_phases.track_out`, `households_ways`): `track_inputs` and `ways_inputs` gather what they read, `chose_the_track` and `lay_the_ways` record what they return; `near_the_cluster` gives the stretch the households' ways are laid to |
| `stages.py` | STAGES 5 and 6 - the homesteads themselves and what stands among them. Read this first. The seating, the track out and the households' ways are the Rust's since feature 444 T30 (`rust_seating.py`, `household_ways.py` hand them over and record them) |
| `seat_geometry.py` | the seating's leaf geometry: the brook's bank a point is on, and the declared cluster shape (`declare_cluster_shape`, `shapes_drawn_at`) |
| `boundary.py` | THE SITE BOUNDARY (feature 226): the ground a homestead may stand on, computed ONCE |
| `region.py` | THE SEAT REGION (feature 297): where a homestead can stand and a door can reach the access tree, computed once per change to what stands; every round's seats are drawn only from it |
| `rust_seating.py` | THE HOMESTEADS SEATED IN RUST (feature 444 T30): what each seating form reads gathered and handed to `l7r_phases` (`rust_grow`, `rust_scatter`, `rust_rows`), each household it seats recorded as `_try_place_bundle` recorded one (`record_seated`) |
| `holds.py` | the parts the seating laid, held in the registry of what stands until they are drawn (feature 287) |
| `rows.py` | THE ROW VILLAGE'S HOLDINGS DRAWN (feature 291): each far-row farm's holding as dry-field plots (`draw_holdings`); the rows themselves are the Rust's since feature 444 T30 (`rows.rs`, `row_seat.rs`) |
| `row_rules.py` | the row village's and the grove farm's rules, read off a finished manifest - pure functions, each returning what breaks its rule |
| `sties.py` | the plain paddy farm's pig sty (feature 374 wave 151, 0049): `stage_sties`, seated against its farmstead's walls in the house's frame once the ways stand, never in the bundle |
| `farm_water.py` | a DISPERSED farm's own water as a channel led into its grounds (feature 291) |
| `persimmon_reseat.py` | the persimmon a household could not keep, given to one that has room (feature 315) |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

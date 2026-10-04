# `homesteads/` - the homesteads and what stands among them

Split from the 1,330-line `homesteads.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.

## Look here when

| file | look here when |
|---|---|
| `seats.py` (162) | where a homestead may sit - the front row, the lane frontage that fronts it, the cluster's aspect ratio, and whether a seat is allowed at all |
| `bamboo.py` (144) | the household bamboo strip: whether a strip is blocked, and the per-household placement |
| `fixtures.py` | what stands in a farmstead's yard - the hamlet's fixture shares and forms (`fixture_quota`, `fixture_forms`, handed to the seating) and `farmstead_fixtures`, which DRAWS each fixture where the bundle laid it (feature 287, homes H32: `settlement/homestead_parts/fixture_seats.py` lays them - the bath room joined to the house, the wood shed a ken off a wall, feature 280; the field pit takes its own form at the hinterland call where it can) |
| `retirement.py` (135) | the retirement house (269 B42, 0004): the `family_form` knob (one roof, or a retirement house in some yards), its share, size and seat off the farmhouse's back or flank, recorded under `retirement_houses` - never a household - and seated after the byres in `stage_appurtenances` |
| `wells.py` (314) | the public wells - how many a settlement of this size wants, and the pass that seats them |
| `growth.py` | how a NUCLEATED cluster is seated (feature 308): grown from its first house, each next house offered from a standing one at the distance their footprints part - the envelope, the woodlot, the path out and the sun its yard and beds are owed - jittered, widening while households are left (`grow_the_margin`, `footprint`, `seat_toward`, `GROW_LEVELS`) |
| `capacity.py` | the DISPERSED form's last pass - the exhaustive offer of the free ground, its dry-spell cap and the near-miss rescue - and the margin ladder every form shares (`margin_ladder`, `seating_mark`, `unseat_to`, `SiteRefused`) |
| `household_ways.py` | THE WAY OUT'S GATE once the last house stands (feature 320): `way_out_gate` (on the cluster's edge along the lawful bearing out, clear of every box and wood seat, out of the field, on the canvas) and `root_at_the_gate` (the track out's first leg, which the households' ways join) - nothing of a way is reserved while houses are seated |
| `stages.py` (334) | STAGES 5 and 6 - the homesteads themselves and what stands among them. Read this first |
| `seat_geometry.py` | the seating's leaf geometry (feature 316 split it from `stages.py`, which re-exports it): the brook push, the seat's turn, the drawn cluster band and the declared cluster shape |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

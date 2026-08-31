# `tests/settlement/structures/` - the suite for the `settlement/structures/` package

Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174, under the same rule
that split `tests/hamletgen/ways/` (constitution Principle X clause 13, which covers a TEST file
exactly as it covers source - v1.6.1, GM 2026-08-16). The subject has been a PACKAGE since feature
114; the suite had stayed one file, and the coverage work of feature 174 pushed it over the bar.

**One file per submodule of the subject**, and the mapping is DERIVED rather than chosen: each test
went to the submodule that defines the majority of the package names it exercises (`rowpack` ->
`packing.py`, `servant_ranges` -> `servants.py`, `_estate_wall_clear` -> `compounds.py`). A test that
names nothing from the package follows the test above it, which keeps a banner's run together. So the
way to find a test is to name the thing it tests, and a new test goes beside the ones for its subject.

Runs in the quick tier, unchanged: the tier is decided by the top-level tree, so a nested directory
under `tests/settlement/` is selected exactly as the flat file was.

## Look here when

| file | look here when |
|---|---|
| `_builders.py` | a fixture factory or stub shared across these files |
| `test_captions.py` | a caption's seat on a structure - the label ladder's clear-seat probes |
| `test_compounds.py` | a walled compound: its wall's clearance of water, the street net and the watch's tower |
| `test_fixtures.py` | the mounted fixtures - notice boards, their anchors and their seats (`fixtures/`) |
| `test_ground.py` | open ground drawn under structures - pastures and their captions |
| `test_packing.py` | the multi-building placers, their row cadence and their shortfall bookkeeping |
| `test_servants.py` | servant ranges: the ward fence, the neighbor closer than the host, a doorway |
| `test_urban.py` | the urban packs - merchant residences, flophouses, the town works |
| `test_urban_fixtures.py` | the fixtures only a town or city draws |

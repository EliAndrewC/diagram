# `tests/settlement/structures/` - the suite for the `settlement/structures/` package

Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174, under the same rule
that split `tests/hamletgen/ways/` (constitution Principle X clause 13, which covers a TEST file
exactly as it covers source - v1.6.1, GM 2026-08-16). The subject has been a PACKAGE since feature
114; the suite had stayed one file, and the coverage work of feature 174 pushed it over the bar.

**One file per submodule of the subject**, and the mapping is DERIVED rather than chosen: each test
went to the submodule that defines the majority of the package names it exercises (`place_labels` ->
`captions.py`, `place_kosatsuba` -> `fixtures/`). A test that
names nothing from the package follows the test above it, which keeps a banner's run together. So the
way to find a test is to name the thing it tests, and a new test goes beside the ones for its subject.

Runs in the quick tier, unchanged: the tier is decided by the top-level tree, so a nested directory
under `tests/settlement/` is selected exactly as the flat file was.

## Look here when

| file | look here when |
|---|---|
| `_builders.py` | a fixture factory or stub shared across these files |
| `test_captions.py` | the label phase and the one placer's index: deferred and withdrawn captions, a field name's caption, the index's families, the fallback where no seat is clear |
| `test_fixtures.py` | the mounted fixtures - notice boards, their anchors and their seats (`fixtures/`) |
| `test_board_seat.py` | the notice board's one siter and its rules' predicates (`fixtures/board_seat.py`, feature 287) |
| `test_packing.py` | no tests: its subject was retired by feature 392 |
| `test_urban.py` | the urban halo `commons` and `marsh` clear around buildings, and a tilted board caption's fallback ladder |
| `test_urban_fixtures.py` | the composed-surface guard: no pre-split member lost, no two sub-mixins defining one name, every member resolving on `Settlement` |

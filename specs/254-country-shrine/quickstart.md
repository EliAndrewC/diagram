# Quickstart - feature 254

Adding a Mode A building type after this feature lands (the process `buildings.md` states):

1. Research pass first; the record entry with footnotes; the agents (`source-reader`, `quote-check`,
   `record-format`, `source-applicability`).
2. Declare the type: one object in `l7r/diagram/buildings/types.json` (see `contracts/types.schema.json`).
3. `make building-programs` renders its required-items table into `buildings/programs.md`; write the
   knobs and anchors in prose beside it.
4. Per-type checks, if any, in `tools/pack_audit/checks.py`, registered in `registry.py` with a red
   fixture each under `tests/fixtures/`.
5. The exemplar under `pool/<tier>/<name>/` (`.svg` with `id="precinct"`, `.gen.py` rasterizing,
   `.notes.md` with `**Program type**` and `**Form**`), `building-review` and `size-audit`, ledger rows.
6. `make quick` - the sweep picks the tier up from the declaration; nothing else is edited.

Running the checks by hand on one sheet: `make pack-audit ARGS=pool/<tier>/<name>/<name>.svg`.

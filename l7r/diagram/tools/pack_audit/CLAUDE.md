# `pack_audit/` - the Mode A sheet audit

Split from one `pack_audit.py` by feature 173, as LAYERS emitted bottom-up (every cross-module reference points backwards, so no import cycle). **Load only the file the task calls for**; this index is the map. Run it as `make pack-audit`.

## Look here when

| file | look here when |
|---|---|
| `parse.py` | the SVG reader: the fill/stroke/pattern vocabulary, the four record types (`Rect`, `Label`, `ParsedPlan`), and `parse_svg`, which turns a Mode A sheet into them |
| `grids.py` | the raster measurements - the occupancy grids and everything derived by counting cells: coverage, perimeter hugging, the largest vacant rectangles, per-region density |
| `checks.py` | the audits themselves - one function per question asked of a plan, each with its own result record. Add a new check here |
| `registry.py` | the check REGISTRY (feature 254): every pass/fail question the audit asks of a Mode A sheet, with the building types it applies to, the red fixture that proves it fires, and the compliant fix its failure names. Register a new check here |
| `shared.py` | the checks feature 254 added: three for every Mode A sheet, three for the magistracy alone |
| `labels.py` | a program item paired with the footprint that draws it, by the sheet's own tags (feature 254) - the pairing the band check makes |
| `sun.py` | a kitchen garden's sun on a hand-drawn sheet (feature 283) |
| `report.py` | the printed report and the CLI entry point - the only place the checks above are composed into an order |
| `tagged.py` | the second reader (feature 294): every drawn element with its `data-kind`, the kinds it is a part of (`data-part-of`, its groups) and its inherited paint - what a check needs when it asks what a mark BELONGS to |
| `program_rules.py` | the building-review's sweep as registry checks (feature 294 B16-B20): lodging entrances, privies by zone, fire-water distribution, the size hierarchy, the sheet's furniture |
| `roads.py`, `palette.py` | a road leaves the frame or arrives somewhere, and is no wider than the gate it feeds (B21, B23); a kind is painted in its palette role (B22, the kind -> fill table) |
| `size_marks.py` | the sized marks the rect size table misses - circles, paths, lines, polygons - and the tagged kinds no row carries (B15c) |
| `mapmatch.py`, `onmap.py` | a sheet on a map matches the map (feature 257; feature 294 B24: the compound as one glyph, the gate, roads under every key, the required declaration) |
| `__main__.py` | the module entry point the package must keep (`make pack-audit` runs it) |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

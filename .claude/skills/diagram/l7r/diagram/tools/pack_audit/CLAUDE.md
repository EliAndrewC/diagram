# `pack_audit/` - the Mode A sheet audit

Split from the 1,225-line `pack_audit.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.

## Look here when

| file | look here when |
|---|---|
| `parse.py` (298) | the SVG reader: the fill/stroke/pattern vocabulary, the four record types (`Rect`, `Label`, `ParsedPlan`), and `parse_svg`, which turns a Mode A sheet into them |
| `grids.py` (244) | the raster measurements - the occupancy grids and everything derived by counting cells: coverage, perimeter hugging, the largest vacant rectangles, per-region density |
| `checks.py` (542) | the twenty audits themselves - one function per question asked of a plan, each with its own result record. Add a new check here |
| `report.py` (143) | the printed report and the CLI entry point - the only place the checks above are composed into an order |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

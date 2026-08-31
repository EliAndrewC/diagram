# `seams/` - closing a carved comb fan into one shared-bund fabric

Split from the 1,069-line `seams.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. Read the last row first if you want the entry point.

## Look here when

| file | look here when |
|---|---|
| `pockets.py` (416) | a pocket's geometry: despiking, rings, the water body, the outside-command band, and `_absorb` - the merge of a thin pocket into its neighbors |
| `plots.py` (377) | what becomes of a pocket: `_plant` lays plots in it, `_tab_cut`/`_unjog` straighten their edges, `_trade` hands a corner to the neighbor that can use it |
| `close.py` (262) | the driver - `close_seams`, which runs the pass end to end and is the only name the engine calls |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

# `hinterland/` - the ground between everything

Split from the 1,100-line `hinterland.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.

## Look here when

| file | look here when |
|---|---|
| `frame.py` (101) | the drawn frame's own geometry - the content box and the pocket the title sits in, which both the bamboo seats and the windbreak must keep clear of |
| `parcels.py` (576) | open ground: whether a parcel fits, how big a square one can be, its drawn outline, and `open_ground_patches` - the search that places them all |
| `bamboo.py` (137) | where a bamboo thicket may stand and the seats found for it |
| `belt.py` (151) | the shelter belt's polygon - the one shape the woodland and windbreak stages both draw from |
| `stages.py` (162) | STAGES: the four entry points the roll calls, in the order it calls them. Read this first to see what the modules above are for |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

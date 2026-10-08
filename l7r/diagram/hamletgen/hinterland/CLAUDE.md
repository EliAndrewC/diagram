# `hinterland/` - the ground between everything

Split from one `hinterland.py` by feature 173, as LAYERS emitted bottom-up (every cross-module reference points backwards, so no import cycle). **Load only the file the task calls for**; this index is the map.

## Look here when

| file | look here when |
|---|---|
| `frame.py` | the drawn frame's own geometry - the content box and the pocket the title sits in, which both the bamboo seats and the windbreak must keep clear of |
| `parcels.py` | open ground: whether a parcel fits, how big a square one can be, its drawn outline, and `open_ground_patches` - the search that places them all |
| `crossing.py` | whether a walk from the houses crosses the field - `reached_across` (the outline) and `crossed_through` (through it, on the level) - lifted out of `parcels.py` at the 1,000-line bar (feature 328), re-exported there |
| `bamboo.py` | where a bamboo thicket may stand and the seats found for it |
| `belt.py` | the shelter belt's polygon - the one shape the woodland and windbreak stages both draw from |
| `stages.py` | STAGES: the four entry points the roll calls, in the order it calls them. Read this first to see what the modules above are for |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |

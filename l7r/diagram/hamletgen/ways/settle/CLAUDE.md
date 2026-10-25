# `ways/settle/` - the web settles itself

Split from one `settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule: a package of submodules near two thirds
of the bar, never a file trimmed to just under it). `settle/__init__.py` carries the whole account (the package docstring)
and re-exports every name the module had, so `from .settle import X` and `settle.X` still resolve. **A test patches a name
where it is looked up**: `settle.ends.street_anchors`, not `settle.street_anchors`. Layers, each importing only those above:

| file | look here when |
|---|---|
| `shapes.py` | the bookkeeping (`apply_pieces`, `SETTLE_ROUNDS`), the crossing and foul cuts, `settle_shapes`, `settle_way_outs`, an end re-aimed (`reaimed`) |
| `lawful.py` | `Lawful` - the one question asked before a tree lane is drawn - and `corridor_on_lawful_ground` |
| `ends.py` | the repairs of the ends and joins: `settle_ends`, `settle_dangling`, `settle_street_ends` and `settle_joins` (asked by the last resort only since feature 417 T31), `settle_fragments`, `settle_widths`, `settle_network` (`settle_shadows` and `settle_needles` went in T31: measured needless) |
| `stage.py` | the driver: `settle_reach`, `settle_husks`, the step order `STEPS`, `settle_the_web` |

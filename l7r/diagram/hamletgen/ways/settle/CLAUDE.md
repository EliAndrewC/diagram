# `ways/settle/` - the web settles itself

Split from one `settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule: a package of submodules near two thirds
of the bar, never a file trimmed to just under it). `settle/__init__.py` carries the whole account (the package docstring)
and re-exports every name the module had, so `from .settle import X` and `settle.X` still resolve. **A test patches a name
where it is looked up**: `settle.ends.settle_ends`, not `settle.settle_ends`. Layers, each importing only those above:

| file | look here when |
|---|---|
| `shapes.py` | the bookkeeping (`apply_pieces`, `SETTLE_ROUNDS`), the crossing and foul cuts, an end re-aimed (`reaimed`) (`settle_shapes` and `settle_way_outs` went in feature 417 T31) |
| `lawful.py` | `Lawful` - the one question asked before a tree lane is drawn - and `corridor_on_lawful_ground` |
| `ends.py` | the repairs of the ends and joins: `settle_ends` (no longer a step since feature 417 T06: its rules are asked at lay, `ways/lay.py`), `settle_dangling`, `settle_fragments` (asked by the last resort only since feature 417 T48), `settle_network` (`settle_shadows`, `settle_needles` and `settle_street_ends` went in T31, `settle_widths` in T42, `settle_joins` in T44: measured needless) |
| `stage.py` | the driver: `settle_reach`, the step order `STEPS`, `settle_the_web` |

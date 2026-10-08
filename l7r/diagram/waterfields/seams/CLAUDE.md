# `seams/` - what is left of the seam pass

`close_seams` reconciled a CARVED comb fan into one shared-bund fabric. Feature 302 lays the plots as a partition of the planted
region instead (`../partition.py`, which carries the shared-bund research), and deleted the pass and everything only it reached
(`plots.py` whole, the pocket machinery, `_absorb`, `_plant`, `_unjog`, `_shed_necks`, `_visible_parts`, ...). **Load only the
file the task calls for.**

| file | look here when |
|---|---|
| `pockets.py` | the water body and its banks (`_water`) or the band a fan cannot command (`_outside_command`) - the planted region is the envelope less both; `_parts` / `_ring`, read by the grave cut |
| `close.py` | `hold_ring_rules` - every ring a later cut leaves breaking a rule is split (a staircase, cut on its hop: `_split_steps`, which `../settle.py` also uses), welded, or left bare; the grave cut in `settlement/fields/features.py` is its caller |
| `geoms.py` | `ring_polygons`, `GeomTree` |
| `__init__.py` | the composed surface only. Never add logic here |

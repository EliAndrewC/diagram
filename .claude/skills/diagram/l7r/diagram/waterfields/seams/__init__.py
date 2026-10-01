"""The fabric's pocket geometry and its re-hold - what is left of the seam pass (feature 302).

`close_seams` reconciled a CARVED comb fan into one shared-bund fabric, planting or absorbing every scrap of bare ground the
carve left. Feature 302 lays the plots as a partition of the planted region instead (`waterfields/partition.py`, which now
carries the shared-bund research and the GM's ruling this package's docstring held), so the pass and every function only it
reached are gone. What stays:

- `pockets.py` - the water body and its banks (`_water`) and the band the fan cannot command (`_outside_command`), which the
  planted region is cut from; `_parts` and `_ring`, read by the grave cut;
- `close.py` - `hold_ring_rules`, the re-hold a later cut owes the rules (`settlement/fields/features.py` cuts a grave island
  from a plot and re-holds), with `_weld_within_rules` and `_split_steps` / `_cut_on_hop` (which `waterfields/settle.py` also
  splits a staircase with);
- `geoms.py` - `ring_polygons` and `GeomTree`.
"""

from .pockets import _parts as _parts
from .pockets import _ring as _ring
from .pockets import _water as _water

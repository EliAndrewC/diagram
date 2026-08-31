"""close_seams - reconcile a carved comb fan into ONE shared-bund fabric.

TWO ADJACENT BASINS SHARE ONE BUND (GM 2026-08-17, on Inashiro: *"a tiny little standalone
rectangle of earthen walls is just smack dab in the middle of where the field should be ... it
should basically always be the case that two adjacent rice paddies share a single earthen wall
rather than two different earthen walls"*).

THE RESEARCH BEHIND THE RULE (see `research/fields.md`, "Bunds are shared, and the fabric is
continuous"). An *aze* is a puddled-mud ridge 1-2 ft wide, re-plastered every spring (*azenuri*)
so each basin holds its shallow sheet of standing water. It is the WALL BETWEEN two basins, and it
is built once: a second parallel ridge would double the annual azenuri, drain neither basin, and
strand the strip between them - inside an irrigated command area, the most valuable land there is.
Real paddy fabric is therefore one CONNECTED bund network whose lines meet at T-junctions; a
free-standing four-sided ring floating inside it is not a paddy at all. (The odd-shaped,
piecemeal parcels that fabric produces are the honest look - the tidy detached rectangle is a
modern land-consolidation read, which `research/fields.md` already flags as anachronistic.)

WHAT THIS REPLACES, and why the old pass could not get there. `_fill_wedges` sampled the fan on a
12 px grid, boxed each cluster of bare cells, and then SHRANK the box toward its own centroid
until it lapped its neighbors only shallowly. Three consequences, all of them the defect above:

- the box was sized from where the SAMPLES were, not from where the pocket's walls are, so a
  fitted tile stopped a few px short of the surrounding bunds on every side - a rectangle with its
  own four walls and a ribbon of bare floor around it;
- the shrink was uniform, so a tile lapping one neighbor retreated from all four;
- the acceptance test allowed every probe to sit up to 12 real ft INSIDE a neighbor as long as
  one probe stood on bare ground, which drew bund rings in the middle of other people's basins.

Measured on the pre-fix pool (2026-08-17, by `paddy_plot_seams_shared`): 52 doubled-bund plots on
Inashiro, 57 on Kashikawa, 64 on Mizuguchi, 81 on Sawada, plus a nested ring on each of the last
two. All four are at zero after this pass.

THE REPLACEMENT IS A DIFFERENT QUESTION, not a better search. Instead of guessing a rectangle and
retreating, take the bare ground EXACTLY as the carve left it - the command area, minus everything
already planted, minus the water and its banks - and give every piece of it to the fabric:

- a pocket wide enough to hold a basin is PLANTED, subdivided at the fan's own grain. Its outer
  boundary IS the surrounding plots' boundary, so the bunds coincide by construction rather than
  by tolerance, and its interior seams are cut from one box so they coincide too.
- a pocket too thin to hold a basin is ABSORBED into the neighbor it shares the most bund with.
  That is what welds a doubled bund into a single one: the strip stops being ground between two
  walls and becomes part of the basin on one side of it.

So the pass has one postcondition - every square foot inside the command area is planted, is
water, or is outside the fan - and `paddy_plot_seams_shared` is the gate that holds it.

IT RUNS LAST, after `_comb_toe_and_hem`. That order is load-bearing: the toe pass DROPS slivers
too acute to bund and re-hems every bund onto the drain bank, so anything that ran before it would
have its work reopened as fresh bare ground. Running afterwards means this pass reconciles what
the whole pipeline actually left, whichever stage left it.
"""

from .close import close_seams as close_seams
from .plots import _plant as _plant
from .pockets import MIN_PLOT_SIDE as MIN_PLOT_SIDE
from .pockets import _absorb as _absorb
from .pockets import _despike as _despike
from .pockets import _min_apex as _min_apex
from .pockets import _open_to as _open_to
from .pockets import _parts as _parts
from .pockets import _ring as _ring
from .pockets import _water as _water

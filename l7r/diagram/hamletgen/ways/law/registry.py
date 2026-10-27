"""the lane law's REGISTRY: `LAW`, every rule by name, and `violations`, what the acceptance sweep reads (split from `law.py` at the 1,000-line bar, feature 417 T54).

Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at

from ..checks import unreached_houses
from ..forced import lazy_ground
from ..law_water import (
    deck_seats as deck_seats,
)
from ..law_water import (
    oblique_crossings as oblique_crossings,
)
from ..law_water import (
    off_ford_crossings as off_ford_crossings,
)
from ..law_water import (
    over_and_back as over_and_back,
)
from ..law_water import (
    plank_faults as plank_faults,
)
from ..law_water import (
    short_decks as short_decks,
)
from ..law_water import (
    unbridged_crossings as unbridged_crossings,
)
from ..law_water import (
    undeckable_crossings as undeckable_crossings,
)
from .ends import (
    breaks_mid_run,
    dangling_ends,
    doorstep_ends,
    field_unreached,
    lanes_over_fixtures,
    short_fragments,
    unreached_targets,
    way_outs_crossing,
)
from .meet import (
    connector_hairpins,
    doubled_tails,
    folded_joints,
    lane_networks,
    near_misses,
    needle_joins,
    needle_loops,
    shallow_crossings,
    width_steps,
)
from .shape import (
    hooked_ends,
    husks,
    lanes_that_kink,
)

# ---- the registry --------------------------------------------------------------------------------------------------

LAW: dict[str, Callable[[Mapping[str, Any]], Any]] = {
    "bends": lanes_that_kink,
    "hooks": hooked_ends,
    "husks": husks,
    "folded_joints": lambda M: folded_joints(M.get("lanes") or [], lazy_ground(M)),
    "connector_hairpins": lambda M: connector_hairpins(M.get("lanes") or [], lazy_ground(M)),
    "needle_joins": lambda M: needle_joins(M.get("lanes") or [], lazy_ground(M)),
    "shallow_crossings": shallow_crossings,
    "doubled_tails": doubled_tails,
    "networks": lambda M: max(0, lane_networks(M) - 1),
    "joins_short": near_misses,
    "fragments": short_fragments,
    "width_steps": lambda M: width_steps(M.get("lanes") or []),
    "dangling_ends": dangling_ends,
    "doorstep_ends": doorstep_ends,
    "over_fixtures": lanes_over_fixtures,
    "needle_loops": lambda M: [[round(v) for v in face.centroid.coords[0]] for face, _lanes in needle_loops(M)],
    "field_unreached": field_unreached,
    "breaks_mid_run": breaks_mid_run,
    "over_and_back": over_and_back,
    "off_ford": off_ford_crossings,
    "oblique_brook": oblique_crossings,
    "oblique_channel": lambda M: oblique_crossings(M, "channel"),
    "unbridged": unbridged_crossings,
    "undeckable": undeckable_crossings,
    "short_decks": short_decks,
    "planks": lambda M: [x for part in plank_faults(M) for x in part],
    "way_outs": way_outs_crossing,
    "unreached_houses": unreached_houses,
    "unreached_targets": unreached_targets,
}
"""Every lane rule a finished map is asked, by name - the acceptance sweep's (M9) reading of this module. A rule's value is
falsy when the map keeps it. `deck_seats` is asked of one candidate way, not of a manifest, and is reached here through
`undeckable_crossings`."""


def violations(M: Mapping[str, Any]) -> dict[str, Any]:
    """Every rule of `LAW` this map breaks, with what breaks it."""
    return {name: v for name, rule in LAW.items() if (v := rule(M))}

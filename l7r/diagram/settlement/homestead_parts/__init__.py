"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index.

Research: plumbing - NONE: the composed mixin; its parts carry their own claims
"""

from .gardens import GardensMixin
from .groves import GrovesMixin
from .keepouts import KeepoutsMixin
from .stands import StandsMixin
from .yards import ThreshingYardsMixin


class HomesteadPartsMixin(
    ThreshingYardsMixin,
    GardensMixin,
    GrovesMixin,
    StandsMixin,
    KeepoutsMixin,
):
    """The composed surface. No members of its own - see this package's CLAUDE.md."""

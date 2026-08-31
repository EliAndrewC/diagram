"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index."""

from .farmstead import FarmsteadMixin
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
    FarmsteadMixin,
):
    """The composed surface. No members of its own - see this package's CLAUDE.md."""

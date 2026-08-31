"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index."""

from ._helpers import _angle_between as _angle_between
from ._helpers import _pull_back as _pull_back
from ._helpers import fan_rival as fan_rival
from ._helpers import junction_floor as junction_floor
from .clipping import WaterClipMixin
from .focal import FocalMixin
from .kido import KidoMixin
from .lanes import LanesMixin
from .wards import WardsMixin
from .water import WaterBodiesMixin


class WaterWaysMixin(
    FocalMixin,
    WaterBodiesMixin,
    WaterClipMixin,
    LanesMixin,
    KidoMixin,
    WardsMixin,
):
    """The composed surface. No members of its own - see this package's CLAUDE.md."""

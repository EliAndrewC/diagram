"""The settlement's public street furniture and civic fixtures, and the two auto-siters that place them on the traffic.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.
"""

from ..._knobs import KOSATSUBA_MARKER_MIN_PX as KOSATSUBA_MARKER_MIN_PX
from ._helpers import CAPTION_LANE_FLOOR_FT as CAPTION_LANE_FLOOR_FT
from ._helpers import CAPTION_LANE_TARGET_FT as CAPTION_LANE_TARGET_FT
from ._helpers import KOSATSUBA_ANCHOR_BAND_FT as KOSATSUBA_ANCHOR_BAND_FT
from ._helpers import KOSATSUBA_ENTRANCE_REACH_FT as KOSATSUBA_ENTRANCE_REACH_FT
from ._helpers import KOSATSUBA_VERGE_FT as KOSATSUBA_VERGE_FT
from ._helpers import kosatsuba_affordances as kosatsuba_affordances
from ._helpers import kosatsuba_anchor as kosatsuba_anchor
from ._helpers import pick_caption_seat as pick_caption_seat
from .boards import BoardsMixin
from .siting import FixtureSitingMixin


class PublicFixturesMixin(
    BoardsMixin,
    FixtureSitingMixin,
):
    """The composed surface. No members of its own - see this package's CLAUDE.md."""

"""The lane web as a package: `skeleton`, `tidy` and `stage` - split from `ways/web.py` at the 1,000-line bar (feature 405 T57,
the GM 2026-10-21: every name the module had is re-exported here, so no importer changes). See CLAUDE.md for the index.

Research: web plumbing - NONE"""

from . import skeleton, stage, tidy  # noqa: F401 - the submodules by name: a test patches a name where it is looked up
from .skeleton import (
    SKELETON_ARM_WIDTH as SKELETON_ARM_WIDTH,
)
from .skeleton import (
    _lay_skeleton as _lay_skeleton,
)
from .skeleton import (
    _web_cut_lines as _web_cut_lines,
)
from .skeleton import (
    lane_skeleton_for as lane_skeleton_for,
)
from .skeleton import (
    oriented_skeleton as oriented_skeleton,
)
from .skeleton import (
    served_arm as served_arm,
)
from .skeleton import (
    water_along_side as water_along_side,
)
from .stage import (
    _reachable_runs as _reachable_runs,
)
from .stage import (
    lay_reachable_runs as lay_reachable_runs,
)
from .stage import (
    seat_wall_reach as seat_wall_reach,
)
from .stage import (
    stage_web as stage_web,
)
from .tidy import (
    kept_connector as kept_connector,
)
from .tidy import (
    tidy_lane_ends as tidy_lane_ends,
)
from .tidy import (
    unsplitting_drops as unsplitting_drops,
)

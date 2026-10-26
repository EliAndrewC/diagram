"""STAGE 4b: the lanes, the connector track, and what makes a path legal.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.

Research: re-exports - NONE
"""

from __future__ import annotations

# `from .x import Name` binds `x` itself as an attribute of this package, so a `from <pkg> import *`
# in a parent carries the SUBMODULE NAMES too. Feature 173 made that bite: `hamletgen/__init__.py`
# star-imports both `hinterland` and `homesteads`, and both packages have a `bamboo.py` and a
# `stages.py` - so the second star silently shadowed the first, which
# `tests/hamletgen/test_surface.py::test_no_public_name_clashes` caught. `__all__` says what this
# package actually exports; it is DERIVED here rather than listed, per clause 14.
import types as _types

from l7r.diagram.settlement import seg_dist as seg_dist

from ..consts import WEB_REACH_FT as WEB_REACH_FT
from .bund import a_way_onto_the_bund as a_way_onto_the_bund
from .bund import run_lanes_on_to_the_bund as run_lanes_on_to_the_bund
from .checks import crossing_lands_on_crop as crossing_lands_on_crop
from .checks import drawn_water_segs as drawn_water_segs
from .checks import lanes_share_tread as lanes_share_tread
from .checks import path_violations as path_violations
from .checks import served_network as served_network
from .checks import shallow_crossing as shallow_crossing
from .checks import stream_segs as stream_segs
from .checks import unreached_houses as unreached_houses
from .clearance import _clear_link as _clear_link
from .clearance import clear_runs as clear_runs
from .clearance import clip_to_clear as clip_to_clear
from .clearance import route_around as route_around
from .fabric import _crosses_fabric as _crosses_fabric
from .fabric import _draw_web as _draw_web
from .fabric import _fabric_hits as _fabric_hits
from .fabric import _hits_a_steading as _hits_a_steading
from .fabric import _homestead_polys as _homestead_polys
from .fabric import _margin_frame as _margin_frame
from .geom import _TOUCH_GAP as _TOUCH_GAP
from .geom import WorkedGround as WorkedGround
from .geom import _components as _components
from .geom import _net_reach as _net_reach
from .geom import _reach as _reach
from .geom import _trim_to_service as _trim_to_service
from .geom import _turn_deg as _turn_deg
from .geom import end_serves as end_serves
from .geom import polyline_len as polyline_len
from .geom import push_clear_of_fabric as push_clear_of_fabric
from .geom import push_out_of as push_out_of
from .geom import steading_footprints as steading_footprints
from .geom import worked_ground as worked_ground
from .geom import worked_ground_rings as worked_ground_rings
from .route import _EASE_FT as _EASE_FT
from .route import _EASE_STEPS as _EASE_STEPS
from .route import _ease_corner as _ease_corner
from .route import _route as _route
from .route import _unjog as _unjog
from .serve import _lay_web_lane as _lay_web_lane
from .smooth import web_pieces as web_pieces
from .track import _cluster_gateway as _cluster_gateway
from .track import _thread_the_fabric as _thread_the_fabric
from .track import connector_track as connector_track
from .track import stage_seat as stage_seat
from .track import stage_track as stage_track
from .web import _lay_skeleton as _lay_skeleton
from .web import _reachable_runs as _reachable_runs
from .web import stage_web as stage_web
from .web import tidy_lane_ends as tidy_lane_ends

__all__ = [_n for _n, _v in sorted(globals().items()) if not _n.startswith("_") and not isinstance(_v, _types.ModuleType)]

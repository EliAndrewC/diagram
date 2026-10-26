"""The web settles itself: the LAST pass of `stage_web` (feature 287, M4).

WHY IT EXISTS. The web is some forty passes, each with its own partial guard - "no worse than it was", "the least bad",
"keep the orphan" - and nothing after them re-asks the rules the finished-map tests assert. So a rule held on the seeds the
tests roll and nothing stopped the next seed breaking it. This pass asks every rule of the lane law (`law.py`, the ONE
predicate per rule that the tests call too) of the web as it stands, and repairs what breaks one, until a whole round
changes nothing. It is the guarantee; the passes before it are best-effort drawing.

WHAT A REPAIR MAY DO. It only takes material AWAY from an ordinary lane - cuts a crossing, a fold or a foul out of it,
shortens an end, re-aims an end's last leg at the foot of its own previous vertex (never longer than the leg it replaces),
drops a piece that no longer joins the connector's network. It never cuts the TREE (`corridors.
is_tree`: the connector, whose hook alone it takes off, and the lanes step 4 draws); the one tree edit is step 3's, which
takes a tree lane away WHOLE where it alone carries a way out over the brook and back, and step 4 lays that reach again
only where it adds no such way out (`Lawful`); and a tree lane shorter than `law.FRAGMENT_FT` that earns nothing goes whole
as any lane does (`settle_fragments`, homes H40) - it reaches nothing step 4 owes. That is the termination argument:
every repair strictly shortens the non-tree web, and step 4 adds a tree lane at most once per house, way target and field. Should the rounds run out, or a round change
nothing, with a rule still broken (`unsettled`, the whole law asked at the exit), the ORDINARY lanes still breaking one are
dropped whole, round by round, until none is (FR-005: a lane that cannot
be repaired is dropped; it is never kept as "the least bad"); a rule the tree alone still breaks is refused by name, never
mended by dropping a tree lane (`last_resort.py`).

THE REACH IS DRAWN HERE (step 4; ways W01, W03, homes H36). A lane a repair cuts may have been some farmhouse's only way,
and the web may never have reached one at all. The seating reserved a corridor from every door to the exit strip the
connector starts on (`settlement/rolling/access.py`, `track._cluster_gateway`) and judged the whole tree as lanes with
each (`tree.admits`), so the tree lanes owed - every unreached farmhouse's chain and the field's corridor - are drawn as
judged (`tree.settle_tree`), the ordinary lanes deferring to them (`tree.settle_defer`); a spur is laid to each way target
the network misses (a burial ground's edge), the shortest run that keeps the law (`Lawful`); the step that pruned a tree
lane the map no longer needed went in feature 417 T31, measured needless. This replaced the driver's re-roll (feature 287, FR-002).

THE CROSSINGS ARE SQUARED AS LAID (ways W11): every placer squares the run it lays (`squaring.square_run`), so every
guarantee here is judged on the squared lane; the step that squared every lane here went in feature 417 T48.

Research: settle plumbing - NONE: rounds, step order and bookkeeping; each rule is claimed at its predicate in law.py, and a split piece's room and width at `apply_pieces`"""

from l7r.diagram.overlap.registry import forbidden_segment as forbidden_segment
from l7r.diagram.settlement import rot_rect as rot_rect
from l7r.diagram.settlement import seg_closest as seg_closest
from l7r.diagram.settlement import seg_dist as seg_dist
from l7r.diagram.settlement._knobs import bridge_crossed_waters as bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import flooded_ground as flooded_ground
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes as departure_routes

from ...consts import WEB_CLEARANCE as WEB_CLEARANCE
from ...consts import WEB_FABRIC_GAP as WEB_FABRIC_GAP
from ...consts import Poly as Poly
from ...consts import Pt as Pt
from .. import law as law
from ..arcs import arc_at as arc_at
from ..arcs import cut_around as cut_around
from ..arcs import sub_run as sub_run
from ..checks import square_crossings as square_crossings
from ..checks import unreached_houses as unreached_houses
from ..corridors import ACCESS_ROLE as ACCESS_ROLE
from ..corridors import ACCESS_WIDTH as ACCESS_WIDTH
from ..corridors import MEET_REACH_FT as MEET_REACH_FT
from ..corridors import GroundIndex as GroundIndex
from ..corridors import _box as _box
from ..corridors import _poly_box as _poly_box
from ..corridors import building_quads as building_quads
from ..corridors import is_tree as is_tree
from ..corridors import open_ground_rings as open_ground_rings
from ..corridors import through_a_building as through_a_building
from ..fabric import _crosses_fabric as _crosses_fabric
from ..fabric import house_hit as house_hit
from ..fabric import lane_fabric as _fabric  # noqa: F401 - the old module's alias
from ..forced import lazy_ground as lazy_ground
from ..geom import _TOUCH_GAP as _TOUCH_GAP
from ..geom import _components as _components
from ..geom import _trim_to_service as _trim_to_service
from ..geom import lane_owner as lane_owner
from ..geom import memo_ground as memo_ground
from ..geom import polyline_len as polyline_len
from ..geom import steading_footprints as steading_footprints
from ..geom import worked_ground as worked_ground
from ..joints import joints as joints
from ..joints import rank_width as rank_width
from ..keeper import NOT_THE_SETTLES as NOT_THE_SETTLES
from ..keeper import unsettled as unsettled
from ..knots import settle_knots as settle_knots
from ..reach import _draw_tree_lane as _draw_tree_lane
from ..reach import settle_field as settle_field
from ..reach import settle_targets as settle_targets
from ..serve import shadowed_by as shadowed_by
from ..squaring import SQUARE_MARGIN_FT as SQUARE_MARGIN_FT
from ..squaring import SQUARE_PASSES as SQUARE_PASSES
from ..squaring import _pts as _pts
from ..squaring import cut_at_shallow_crossing as cut_at_shallow_crossing
from ..squaring import square_run as square_run
from ..squaring import square_waters as square_waters
from ..sweeps import _DOUBLED_DEG as _DOUBLED_DEG
from ..sweeps import along_tail as along_tail
from ..sweeps import cut_at_tail as cut_at_tail
from ..tree import set_corridor as set_corridor
from ..tree import settle_defer as settle_defer
from ..tree import settle_tree as settle_tree
from ..tree import tree_faults as tree_faults
from . import ends, lawful, shapes, stage  # noqa: F401 - the submodules by name: a test patches a name where it is looked up
from .ends import TRIM_GRAIN_FT as TRIM_GRAIN_FT
from .ends import connector_component as connector_component
from .ends import settle_dangling as settle_dangling
from .ends import settle_ends as settle_ends
from .ends import settle_fragments as settle_fragments
from .ends import settle_network as settle_network
from .lawful import Lawful as Lawful
from .lawful import corridor_on_lawful_ground as corridor_on_lawful_ground
from .shapes import CROSSING_GAP_FT as CROSSING_GAP_FT
from .shapes import SETTLE_ROUNDS as SETTLE_ROUNDS
from .shapes import Yards as Yards
from .shapes import _as_end as _as_end
from .shapes import _back as _back
from .shapes import _crossing_fault as _crossing_fault
from .shapes import _cut_gap as _cut_gap
from .shapes import _foot as _foot
from .shapes import _ordinary as _ordinary
from .shapes import _rounded as _rounded
from .shapes import apply_pieces as apply_pieces
from .shapes import fouled_segment as fouled_segment
from .shapes import meets_clean as meets_clean
from .shapes import reaimed as reaimed
from .shapes import theirs as theirs
from .stage import STEPS as STEPS
from .stage import settle_reach as settle_reach
from .stage import settle_the_web as settle_the_web

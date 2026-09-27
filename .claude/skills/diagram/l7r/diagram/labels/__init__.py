"""The ONE caption placer (feature 266) - owned by neither mode, used by both and by `make seat-label`.

Load `placer.py` first: its docstring is the standard in the order it decides. `standard.py` holds every number, each
with its source or its calibration; `obstacles.py` the index; `layout.py` the line cuts; `geom.py` the plain geometry.
"""

from .layout import cut as cut
from .layout import layouts as layouts
from .obstacles import CIVIC_GROUPS as CIVIC_GROUPS
from .obstacles import Obstacle as Obstacle
from .obstacles import ObstacleIndex as ObstacleIndex
from .obstacles import Way as Way
from .placer import Placement as Placement
from .placer import Subject as Subject
from .placer import place as place
from .standard import upright as upright

"""What is left of the seam pass (feature 302): `pockets.py`'s `_water` - the water body and its banks - with `_parts` and `_ring`,
which a gate check of every shipped comb field reads (`tests/gate/test_field_302.py`). Feature 444 T16 deleted the rest with the
Python field engine."""

from .pockets import _parts as _parts
from .pockets import _ring as _ring
from .pockets import _water as _water

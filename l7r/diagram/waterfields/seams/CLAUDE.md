# `seams/` - what is left of the seam pass

`pockets.py` holds `_water` (the water body and its banks), with `_parts` and `_ring`: a gate check of every shipped comb field
(`tests/gate/test_field_302.py`) reads it. Feature 302 retired the seam pass; feature 444 T16 deleted the rest with the Python field
engine (`close.py`'s re-hold went with the old grave cut). `__init__.py` is the composed surface only - never add logic there.

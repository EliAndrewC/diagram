# `water_ways/` - water, lanes, kido and wards

Split from the 1,130-line `water_ways.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

`WaterWaysMixin` exists ONLY to preserve the single import and the position in the `class Settlement(...)` base list - the split is meant to be invisible above this line. Sub-mixin methods reach each other through `self.` on the composed Settlement, so a cross-submodule call needs no import and the partition can be re-cut later without touching core.py.

## Look here when

| file | look here when |
|---|---|
| `_helpers.py` (145) | the module-level helpers the mixins and the tests share - `junction_floor`, `fan_rival`, `_pull_back` and the two angle/length measures |
| `focal.py` (52) | the focal features a settlement is built around - the mill, the secondary shrine, and the block they reserve |
| `water.py` (112) | the water bodies themselves: `stream`, `river`, `channel`, and the flow record every one of them writes |
| `clipping.py` (250) | clipping a way or a channel to water it must not cross - pond, moat, river and stream, plus `field_channel` |
| `lanes.py` (235) | lanes and streets: drawing one, re-inking it, and `trim_lane_stubs`, the pass that pulls back the ends that serve nothing |
| `kido.py` (202) | the kido barrier - its rectangles, its seat, the reservation it keeps clear, and the mesh that places them all |
| `wards.py` (207) | wards and quarters - the boundary that must end on a wall, the ward itself, and the reserves a quarter draws |
| `__init__.py` | the composed surface only - the class this package exists to provide, plus the module-level helpers the tests import by name. Never add logic here |

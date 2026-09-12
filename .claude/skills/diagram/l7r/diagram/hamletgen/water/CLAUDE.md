# hamletgen/water/ - stages 1 and 2, and the brook that feeds them

Split from the 1,175-line `hamletgen/water.py` by feature 230 (constitution Principle X clause 13 -
the cost being managed is context-window tokens), following the [`ways/`](../ways/CLAUDE.md)
exemplar. Bodies are verbatim. **Load only the file the task calls for**; this index is the map.

`from .water import stage_field` and `hamletgen.stage_water_frame` resolve exactly as they did: the
package's `__init__.py` re-exports every public name by star import (clause 14 - a re-export
`__init__` is derived, never a maintained roster), plus an explicit block for the two underscore
names the unit tests consume, which a star import would drop.

| file | look here when |
|---|---|
| `frame.py` | STAGE 1 - the sluice, the fall and the canvas the field is fitted into (`stage_water_frame`) |
| `fit.py` | the field comes out the wrong SIZE, or a fan is refused as illegal: the acreage search (`fit_field`, `_fit_at_aspect`, `_predict_k`), `head_sluice`, and the two predicates that disqualify a fan before its acreage is scored (`tail_dangles`, `net_bends_acutely`) |
| `brook.py` | the stream's own COURSE, its intake or the weir glyph (feature 230): `brook_skirt` and its four helpers - the crop's true cross-section (`_crop_edge`), the reflecting wander (`_wander`), the frame bound in MAP coordinates (`_v_within`) and the axis backstop (`_off_the_axes`) - plus `feed_brook` and `draw_intake` |
| `comb.py` | STAGE 2 itself: the fitted comb drawn, the head race taken off the brook's bank at the offtake angle, the intake set on it (`stage_field`). Named `comb` rather than `field` because `field` is already a public name in `driver` (dataclasses) and the surface guard fails on a clash |
| `polder.py` | anything about the reclaimed block: both polder archetypes (`stage_polder`, `fit_polder`), the perimeter dike and its channel gaps, the flanks (`polder_flanks`, `waterward_flanks`, `dike_face`), the waterward reed fringe (`stage_waterward`) and `polder_crossing_caps` |

## Monkeypatching

Each submodule binds its helpers at import (`from l7r.diagram.waterfields import carve_comb`), so
patching `hamletgen.water.carve_comb` reaches nothing - patch the DEFINING submodule
(`water.fit.carve_comb`, `water.polder.build_polder`). `tests/hamletgen/test_water.py` is the worked
example; it was the one consumer the split broke, and it broke loudly rather than silently because
the names it patched no longer existed on the package.

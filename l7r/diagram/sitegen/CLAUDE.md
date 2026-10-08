# `sitegen/` - the machinery the settlement TIERS share

**The three rules first, because they are what this package is for.** The full reasoning is in
`__init__.py`'s docstring; this is the operational form.

1. **Membership** - a module belongs here only if its LOGIC is tier-independent, *parameterized by
   scale rather than assuming one*. A hard-coded household count, hamlet band, headman, ward or
   wall means it belongs to that tier's generator instead. "Does it say hamlet?" is a first filter,
   not the test: `net_acres` mentions a village grain AND a hamlet grain and takes `ftpx` as a
   parameter so it is right at either - that mention is the record of someone checking it against
   two tiers. `hamletgen/frame.py` says "hamlet" nowhere and stays out, because all three of its
   members take a `SitePlan`.
2. **Direction, one-way** - `hamletgen` (and `villagegen`, `towngen` after it) import `sitegen`.
   `sitegen` NEVER imports a tier generator. `tests/sitegen/test_direction.py` asserts it.
3. **Growth: MOVE, never copy** (GM 2026-08-17, feature 119) - when a later tier needs a stage that lives in a tier
   generator, move it down here and have both tiers import it; never copy it. Copying is how two tiers quietly drift
   apart, invisibly, until the maps disagree. This is the one home of the rule.

## Look here when

| file | look here when |
|---|---|
| `geom.py` | you need a geometry predicate or measure - `poly_area`, `net_acres`, `centroid`, `unit`, `crop_polys`, `pull_clear`, `crosses_disc`, `crosses_poly` - or one of them is giving a wrong answer |
| `types.py` | you need `Pt`, `Poly`, or the `SQ_FT_PER_ACRE` conversion |
| `jobs.py` | you are fanning a cohort roll out across cpus and need the courtesy rule |
| `__init__.py` | you are deciding whether something belongs in this package at all |

`from l7r.diagram.sitegen import centroid` works (star-import re-exports, clause 14), and so does
reaching into a submodule directly.

## Extract on the second consumer

A module moves down here when a second tier REALLY consumes it, never on a predicted need: extracting on the second use
means the seam is observed; extracting on the first means it is predicted, and a predicted seam has to be re-cut. The
standing candidates - `WIND_VECTORS`, `FALL_BEARINGS`, `CARDINAL_BEARINGS`, `DEFAULT_WINDWARD`, terrain doctrine a
village shares - move when the village tier consumes them.

## Tests

`tests/sitegen/` mirrors this directory and is deliberately self-contained - it must not import
from `tests/hamletgen/`, for the same reason the source must not. `SQUARE` is duplicated in
`tests/sitegen/_builders.py` rather than shared: four numbers against a dependency that would
undo the point of the package.

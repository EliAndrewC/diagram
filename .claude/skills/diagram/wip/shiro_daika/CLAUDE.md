# `shiro_daika/` - the domain capital of the Daika house, part by part

Split from the 1,592-line `wip/shiro-daika.gen.py` by feature 173, when constitution Principle X
clause 13's ~1,000-line bar became a gate. `wip/shiro-daika.gen.py` is still the entry point and
still runs the same way - it is a 19-line driver now, and importing this package draws the map.

**THE ONE LINEAR SCRIPT of the ten files that feature 173 split.** 346 of the monolith's statements
were drawing calls at module level and only 358 of its 1,592 lines sat inside a function, so these
parts are SEQUENTIAL, not a library: importing a part EXECUTES it. Each part imports `s` from the
part IMMEDIATELY above it, which is what enforces the order; `__init__.py` states the same order
readably, behind `# isort: off`. Cut at the file's own section banners, and the table below is in
execution order.

**THAT CONTRACT WAS BROKEN ON THE FIRST CUT, and the way it broke is the thing to remember.** Every
part imported from `frame`, which constrains only that `frame` runs first - so the real order came
from the list in `__init__.py`, and `ruff`'s isort sorted that list ALPHABETICALLY. `fields`, which
holds `s.finish()`, ran fourth of seven, and the wharf, the yashiki band and the trade works drew
into a map that had already been written to disk. The gate was green throughout: no test rolls a wip
map, so the only symptom was a wrong picture. Found by settlement-review, 2026-08-31.

The spec first proposed exempting this file under clause 13's ordered-data carve-out.
`spec-fidelity` rejected that: it defines six functions with real algorithms, and "execution order is
a contract" is true of nearly every imperative module in this repository - `hamletgen/ways.py`
included, the file the GM named as the worked example of one that must be split. Admitting it would
have let the carve-out swallow the rule. See `specs/173-files-at-human-scale/spec.md` FR-007.

**A DEFECT WAS FIXED IN PASSING** (Principle XIV). The engine bootstrap walked up looking for
`settlement.py`, which became the `settlement/` package on 2026-08-16 (feature 025) - so the walk
never terminated, because `os.path.dirname("/")` is `"/"`. This map has been an INFINITE LOOP rather
than a failing script since that day, and it went unnoticed because it hangs instead of raising
(measured 2026-08-31: 45 minutes of `make map`, no output, no traceback). `__init__.py` looks for
the directory holding `l7r/diagram` now, and raises at the filesystem root.

## Look here when

| file | look here when |
|---|---|
| `frame.py` (156) | the wall and what it is an OUTPUT of - the budget, the rampart and its four gates, the river, the moat and patrol road, the ways and the kagi-no-te, the ote-suji |
| `castle.py` (212) | the castle and the sovereign ground around it - its two gates, the circulating moat, the aqueduct and towpath, the bridges, the government ward, the Imperial Magistrate's compound, the eight lineage compounds, the two sovereign temples and the teramachi rim |
| `wharf.py` (68) | the collecting-and-disbursing end of the domain's rice - the wharf, its jetties and granaries, the quay face, and the budget reconciliation that closes feature 020 |
| `housing.py` (149) | FEATURE 021: the machi street mesh and the yashiki band - 53 walled compounds of Ranks 8-12 wrapping the castle, and the retainer terraces |
| `trades.py` (166) | the private dojos, the merchant estates, the trade works and the gate caravan program, and the castle's firebreak ring |
| `civic.py` (420) | what the packs must flow around - the kido mesh, the fire towers, and the public wells on their derived grids |
| `fields.py` (424) | the farmland outside the wall - the comb fields, the ring fields, the furrows and topographic channels, and the finish |
| `__init__.py` | the engine bootstrap and the part order - the only two things that are not drawing |

Feature 021's remaining work (the rank-graded samurai districts, the commoner machi) is `housing.py`
and `civic.py`; `wip/shiro-daika.notes.md` holds the review handoffs.

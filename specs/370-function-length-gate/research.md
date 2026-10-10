# Research: feature 370

## R1. What projects set `max-statements` to - the GitHub survey (2026-10-10)

**Method.** Fifteen GitHub code-search API calls (`gh api search/code`, text-match snippets, no page fetched): the query
`max-statements` in each of `pyproject.toml`, `.pylintrc`, `pylintrc`, `setup.cfg` and `ruff.toml`, three pages of 100
each. 1,417 files came back; the value was read from each snippet with `max[-_]statements\s*[=:]\s*(\d+)`, the first per
repository kept: **1,209 repositories**. Not exhaustive and not random (the API's own relevance order); a sanity check.

| value | repositories |
|---|---|
| below 50 | 127 (30: 68, 25: 17, 20: 13, 40: 13) |
| **50** (pylint's and ruff's default) | **638** |
| 51-75 | 172 (60: 97, 75: 24, 70: 14, 58: 12) |
| 76-100 | 168 (**100: 131**, 80: 26) |
| 101-150 | 30 |
| above 150 | 74 (1000: 11, 9999: 7 - the rule switched off) |

**Reading.** 50 is the default, and `pylint --generate-rcfile` writes it into every generated config, so many of the 638
are a template copied, not a choice. **100 is the second most common value overall and the most common value a project
chose over the default** (131 of the 571 that set something else), ahead of 60 (97) and 30 (68).

## R2. What the cap fails here (ruff's own count, 2026-10-10)

`ruff check --select PLR0915 --config lint.pylint.max-statements=N`:

| N | over it, the linted tree (`l7r/`, `tests/`) | `scripts/` (outside the lint fence) |
|---|---|---|
| 50 | 52 | 9 |
| 75 | 23 | 2 |
| **100** | **10** | **2** |
| 150 | 2 | 0 |
| 200 | 0 | 0 |

The ten at 100: `settlement/homestead_parts/stands.py` `village_grove` (190), `hamletgen/homesteads/stages.py`
`_seat_households` (169), `hamletgen/ways/touch.py` `_touch_junctions` (144), `settlement/finish.py` `finish` (133),
`compound.py` `emit_svg` (127), `hamletgen/hinterland/parcels.py` `open_ground_patches` (118), `settlement/land/cover.py`
`commons` (115), `settlement/fields/paddy.py` (106), `compound_parts.py` (105), `hamletgen/ways/web.py` (103). In
`scripts/`: `record/uncited.py:831` (122), `record/claims.py:786` (104).

Per tree at 100 (2026-10-10, the spec review re-running the same command): `l7r` 10, `tests` 0, `scripts` 2,
`pool` 0, `tests/hooks` 0; outside the cap, `specs` 3 and `legacy-hand-authored-pool` 0.

## R3. The constitution's measure, and why ruff's statement count stands for it

Principle X clause 12 measures a function "in logic units (statements/expressions), never raw lines" and names ~1,000 as
a defect. Counted as statements nothing here comes near it (2026-10-10, over `l7r/`: the largest is 190 by ruff's
count and 217 by an `ast` walk counting every `ast.stmt` node); counted as `ast.expr` nodes by the same walk,
16 functions pass 1,000, but an expression count is inflated by every attribute and name (`a.b(c)` is
four nodes). Ruff's `PLR0915` counts statements - the unit pylint and ruff define, deterministic and already in the
linter the gate runs - so the clause's measure becomes ruff's statement count and its threshold the GM's 100.

# Feature 173 - what was measured before specifying

Every number here was taken in the clone `diagram-tooling` at `3b1cb01a`, on 2026-08-31, before a
line of the feature was written. The GM's request rests on two claims - that the guidelines
prescribe the split, and that ten files have drifted past the bar - and both are checked here rather
than inherited.

## R1 - IS the manner prescribed? (the GM's explicit question)

**Yes, but it is one sentence plus fourteen worked exemplars, not a procedure.**

The prescription is constitution Principle X **clause 13** (added v1.6.0, GM-directed 2026-08-15;
extended v1.6.1 to cover test files):

> The target shape is a directory-module whose CLAUDE.md indexes the subfiles with a "look here
> when" line each, per the project's slim-index / load-on-demand doc pattern, so a future session
> loads only the part it needs.

with two carve-outs stated in the same clause and the next one:

- **ordered data** - "a file that is one cohesive ordered dataset (a registry whose row order IS the
  execution contract) may stay large - with an inline justification at the top saying why";
- **clause 14** - a file whose bulk is a roster RESTATING what code elsewhere declares is DERIVED,
  not split, because "duplicated information does not shrink by being divided".

`CLAUDE.md` mirrors this operationally under "Files stay at human scale", and the phrase
"slim-index / load-on-demand doc pattern" appears **only in the constitution** - there is no doc
behind the name. What actually carries the detail is the exemplars, of which the tree holds
**fourteen** package indexes under the skill (`settlement/`, `settlement/_geom/`, `city/`,
`civic_grounds/`, `fields/`, `land/`, `rolling/`, `shrines_wells/`, `structures/`, `hamletgen/`,
`waterfields/`, `interactive/`, `pipeline/`, `sitegen/`, `tools/`, `ci/`, `tests/`,
`tests/settlement/`), every one of them carrying a "look here when" table.

**So the answer to the GM is: present, and by example excellent; as instruction, one sentence.**
Since this feature's failure message will send a session to the prescribed manner, the manner has to
be readable in one place. FR-006 writes it down.

There is also a **retired mechanical toolchain** nobody wrote down: six one-shot splitters under
`specs/`, each deleted-in-place at the end of its feature -
`024-human-scale-files/split_package.py` (388 lines, the most general: verbatim contiguous line
ranges, per-module import regeneration from free-name analysis, a hard failure on any forward
cross-module reference so the package cannot cycle), plus `025`'s `split_settlement.py`, `116`,
`117`, `118`, `120`. Each was rebuilt from scratch. That is the second undocumented thing, and the
reason the ten refactors below are cheaper than they look.

## R2 - the census, and how it differs from what the tooling says

Every `*.py` under `.claude/skills/diagram/` outside `legacy-hand-authored-pool/`, raw lines:

| lines | file | what it is |
|---|---|---|
| 4,369 | `l7r/diagram/hamletgen/ways.py` | the lane-web engine: ~100 functions in six clear passes |
| 1,592 | `wip/shiro-daika.gen.py` | a work-in-progress capital map's draw script (feature 021) |
| 1,541 | `tests/hamletgen/test_ways.py` | the suite for the above, in feature-numbered sections |
| 1,353 | `l7r/diagram/settlement/homestead_parts.py` | `HomesteadPartsMixin` - yards, gardens, groves |
| 1,330 | `l7r/diagram/hamletgen/homesteads.py` | stages 5 and 6 + the well pass |
| 1,225 | `l7r/diagram/tools/pack_audit.py` | the Mode A SVG audit: a parser plus ~20 independent checks |
| 1,212 | `l7r/diagram/settlement/structures/fixtures.py` | `PublicFixturesMixin` - board, tower, punishment spot |
| 1,130 | `l7r/diagram/settlement/water_ways.py` | `WaterWaysMixin` - water, clipping, lanes, kido, wards |
| 1,100 | `l7r/diagram/hamletgen/hinterland.py` | stage 7 + bamboo, woodland, windbreak, the title pocket |
| 1,069 | `l7r/diagram/waterfields/seams.py` | the seam/pocket closer |

**`make audit` already reports this section and its wording is stale**: it says *"five files already
exceed it"* against ten, and *"Reported rather than gated on purpose"*, which is the sentence this
feature retires. It also scans `l7r tests` only, so `wip/` and `scripts/` are invisible to it.

The three frozen exhibits are correctly excluded and stay excluded: `minami` (1,272), `nagahara`
(1,381) and `tango` (1,572) `.gen.py` are write-once legacy, already outside ruff
(`extend-exclude`), outside coverage (`omit`) and never re-run (feature 161).

Outside the skill nothing is close: the largest live `.py` in `scripts/` is `gate-stamp.py` at 346.
The four largest files in the repository outside the skill are all **retired splitters under
`specs/`** (584, 388, 345, 326) - dead one-shot tools kept as a record, which is why FR-002 excludes
`specs/`.

## R3 - where the check belongs, and what it must not become

Three candidate homes were priced:

| home | verdict |
|---|---|
| a pytest under `tests/tooling/` | **rejected as the SOLE home.** `make quick` selects by testmon, and a static scan executes only its own module - so growing `ways.py` past the bar would not re-run it, and the session learns at the gate rather than at the edit |
| a `make` phase of its own | rejected: a new phase for a check that costs milliseconds, when an existing phase already holds exactly this class of thing |
| **the `lint` phase, beside `check-duplicate-defs.py`** | **chosen.** That guard is the precedent in every respect: a repo-wide static structural rule, a `scripts/*.py` with a `--selftest` that runs FIRST, invoked both by the Makefile's `lint` and by `sync-with-main.sh` at push time. It runs on every `make done` regardless of selection, and it also holds the DIRECT route, which no pytest does |

Cost, measured: `find`+`wc` over the 415 `.py` files in the tree is **0.04 s**. The lint phase runs
first at the gate (feature 168), so an oversize file is reported before the map roll is paid for.

**What it must not become**: a guard whose escape is free. Feature 170 established that an escape
must STATE a reason, and feature 169 that a mention is not an invocation. The carve-out here is a
FILE annotation rather than a command token, so the equivalent discipline is: the marker must carry a
reason of substance, and every file taking it must be visible in `make audit` - a carve-out nobody
can enumerate is a carve-out nobody can revisit.

## R4 - what the split can break, and what it cannot

Read before proposing the ten refactors, because two of the three risks are real:

- **Draw order is a runtime contract** (`settlement/CLAUDE.md`): features are layered by the record
  streams and assembled by `finish()`. A mixin split changes where a method's TEXT lives, never when
  it runs - the existing five settlement splits are the proof. Real, and handled by moving verbatim.
- **The module-level coverage floors are real and they MOVE with a split.** `pyproject.toml` names
  measured modules one by one; the Makefile holds every module except `settlement/`,
  `waterfields/`, `interactive/` and `overlap/` at 100%, those four at the settlement ratchet, and
  `tools/hamlet_floor.py` holds every hamlet-path module at 100% on a derived set. A split that puts
  a town-only function in a module a hamlet executes changes what the floor demands (feature 145's
  rule, stated in `settlement/CLAUDE.md`). Total coverage is unchanged by a verbatim move, so the
  risk is per-module, not global.
- **The floors are DEFERRED to `make done FULL=1`** (`COV_FLOORS` is empty at reference scope), and
  `FULL=1` has never been green in four recorded runs. So a per-module coverage consequence of a
  split will not surface at the ordinary gate. This is a KNOWN limit being inherited, not created;
  it is stated in the spec rather than discovered later.
- **Path patterns outside the walk**: `pyproject.toml` (`extend-exclude`, coverage `source`/`omit`,
  per-file-ignores), `.gitignore`, `scripts/gate-stamp.py`'s globs and `_hookdeps.py`'s roster all
  name paths as literals. A file becoming a directory changes those literals silently - the lesson
  recorded after feature 161 nearly let ruff rewrite eighteen frozen exhibits.

## R5 - the ordered-data question, for the two files where it is live

Eight of the ten are ordinary code and split cleanly. Two are worth stating in advance:

- **`wip/shiro-daika.gen.py`** is a hand-authored Mode B draw script for one map - a linear sequence
  of drawing calls whose statement ORDER IS the draw order, unreferenced by the Makefile, unmeasured
  by coverage, and parked mid-feature (021). This is the clause-13 ordered-data carve-out almost
  verbatim. Splitting it would fragment one map's draw order across files for no token saving, since
  a session resuming feature 021 loads the whole thing either way.
- **`l7r/diagram/tools/pack_audit.py`** is a parser plus ~20 INDEPENDENT audit checks, each a
  dataclass and a function. That is the opposite: not one ordered thing, twenty unordered ones.

The spec proposes the carve-out for the first and a split for the second, and flags the first to
`spec-fidelity` explicitly, because the GM's request says *"we will need to actually do these
refactors"* and taking a carve-out on one of the ten is the kind of quiet "X except where Y" that
constitution Principle XVI exists to catch. **Using a carve-out the rule itself states is applying
the rule; the check is whether this file is really the case the carve-out describes.**

**Sources**: this is a TOOLING finding, not a physical one - nothing here concerns how a place was
built, farmed or lived in, so the constitution XII source obligation does not attach. Every claim
above is a measurement of this repository at `3b1cb01a`, reproducible by the command beside it.

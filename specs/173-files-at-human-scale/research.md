# Feature 173 - what was measured before specifying

Every number here was taken in the clone `diagram-tooling` at `3b1cb01a`, on 2026-08-31, before a
line of the feature was written. The GM's request rests on two claims - that the guidelines
prescribe the split, and that ten files have drifted past the bar - and both are checked here rather
than inherited.

## R1 - IS the manner prescribed? (the GM's explicit question)

**Yes, but it is one sentence plus eighteen worked package indexes, not a procedure.**

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
behind the name. What actually carries the detail is the exemplars: **eighteen** package `CLAUDE.md`
indexes, counted as those sitting beside an `__init__.py`.

**Thirteen use the clause's literal wording**, a two-column table headed `| file | look here when |`:
`hamletgen/`, `interactive/`, `settlement/`, `settlement/_geom/`, `city/`, `civic_grounds/`,
`fields/`, `land/`, `rolling/`, `shrines_wells/`, `structures/`, `sitegen/`, `waterfields/`. **Five
route the reader under a different header** and are worth naming rather than glossing, because the
GM's question was whether the convention is really there: `ci/` (`| module | what it is for |`),
`pipeline/` (`| module | what it is | measured for coverage |`), `tools/`
(`| You are asking | Reach for |`), `tests/` (`| tree | runs under | put a test here when |`) and
`tests/settlement/` (`| module | tests for |`). Every one is a routing table answering "which file
do I load"; four of the five are indexes over things that are not subsystems of one engine, which is
why their columns differ.

**And the check is already OWED.** The constitution's v1.6.1 deferred-TODO block, GM-directed
2026-08-16, records it: *"Automated file-length check (flags source files past the threshold lacking
a justification header) - recorded alongside clause 12's deferred expression-counting gate check"*
(`.specify/memory/constitution.md:328`). So the marker-with-a-reason design of FR-004 is the shape
the constitution itself specified, not one this session invented, and this feature closes half of a
two-week-old TODO.

**So the answer to the GM is: present, and by example excellent; as instruction, one sentence.**
That is enough to follow, and the failure message can point at it - which is what FR-006 does, after
spec review cut back a first draft that proposed writing a new procedure document the GM had not
asked for.

There is also a **retired mechanical toolchain** nobody wrote down: **fourteen** one-shot splitters
under `specs/`, across thirteen features (023, 024 x2, 025 x2, 112, 113, 114, 115, 116, 117, 118,
120, 122), 3,392 lines in total, each written for one split and left behind as a record. Two
lineages, and this feature needs both:

- `024-human-scale-files/split_package.py` (388 lines, the most general) for a MODULE-LEVEL file:
  everything moves verbatim by contiguous line ranges, so concatenating the generated bodies
  reproduces the monolith's definition order exactly; only imports are regenerated, per module,
  from free-name analysis - deliberately over-importing rather than under-importing, with `ruff
  --fix` removing the excess and a genuine miss exploding as `NameError` on the next run; and a
  cross-module reference that points FORWARD is a hard failure, so the package cannot cycle.
- `025-human-scale-splits/split_settlement.py` (253 lines) for a MIXIN file: methods split into
  mixin classes by contiguous ranges, each gaining an explicit `self: "Settlement"` annotation and
  `if TYPE_CHECKING: from .core import Settlement`; class-body attribute assignments stay with the
  composed class. Three of this feature's ten files are exactly this shape.

Each was rebuilt from scratch, thirteen times. That is the second undocumented thing, and the
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

- **`wip/shiro-daika.gen.py`** looked like the clause-13 ordered-data carve-out: a hand-authored Mode
  B draw script for one map, unreferenced by the Makefile, unmeasured by coverage, parked mid-feature
  (021). **The spec proposed the carve-out for it and `spec-fidelity` rejected it, correctly.** The
  file is not a dataset: it defines six functions with real logic (`_well_blocks`, a 55-line
  algorithm with a nested helper; `_point_in`, a point-in-polygon routine) and threads mutable
  engine state through itself. "Execution order is a contract" is true of nearly every imperative
  module in this repository - `hamletgen/ways.py` above all, the file the GM named as the worked
  example of one that MUST split - so admitting it here would let the carve-out swallow the rule.
  Two of the supporting claims also failed checking: the file is tracked, is NOT gitignored (only
  `wip/*.svg|png|json|html` are) and has no `pyproject.toml` entry, so unlike the three frozen
  exhibits it is live source inside the lint and type toolchain. It splits.
- **`l7r/diagram/tools/pack_audit.py`** is a parser plus ~20 INDEPENDENT audit checks, each a
  dataclass and a function. Not one ordered thing, twenty unordered ones - it splits easily.

**The lesson worth keeping**: using a carve-out the rule itself states IS applying the rule, but the
test is whether the file is really the case the carve-out describes, and the author of the split is
not a reliable judge of that. Ten of ten split; the FR-004 mechanism ships with nothing using it.

**Sources**: this is a TOOLING finding, not a physical one - nothing here concerns how a place was
built, farmed or lived in, so the constitution XII source obligation does not attach. Every claim
above is a measurement of this repository at `3b1cb01a`, reproducible by the command beside it.

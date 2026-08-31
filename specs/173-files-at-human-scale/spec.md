# Feature 173 - Files Stay at Human Scale, Enforced

**Status**: Draft - specified 2026-08-31. [`request.md`](request.md) is the authority;
[`research.md`](research.md) holds the measurements taken BEFORE specifying.

## The feature, in one sentence

The ~1,000-line file rule stops being a question `make audit` prints and becomes a gate that fails,
and the ten files that have drifted past it are split into packages with `CLAUDE.md` indexes.

## Why this exists (the GM's words)

> This project has a set of guidelines that revolve around not letting files grow too large, but it
> looks like we have allowed that to drift ... I think the solution is to build checks for this into
> our tooling. one of the things that can run whenever we do a make done can be to check the size of
> our files. And if any of them are too large, which is to say over one thousand lines of code, then
> we fail the gate with a message that explains that the clone responsible for this work must split
> up the file in the manner prescribed in our project guidelines.

And on the scope of the work:

> Of course, in addition to building this tooling, we will need to actually do these refactors in
> order for the tooling to pass, since we won't be able to merge the tooling into main until the
> check actually passes. That's fine, since this is a fairly straightforward refactor we have done a
> number of times already; this change is merely about enforcing it at the project level.

The GM also asked a question, which R1 answers: whether the guidelines really do prescribe the split
and the per-directory `CLAUDE.md` index. **They do - in one sentence of constitution clause 13, plus
fourteen worked exemplars.** That is enough to follow and not enough to point a failure message at,
which is why FR-006 exists.

## Scope, stated exactly

**IN**: the check, its wiring, the written procedure, the constitution and `CLAUDE.md` amendments
that follow from gating a rule that was explicitly not gated, and the ten refactors.

**OUT**: clause 12 (functions past ~1,000 logical statements), which the constitution also describes
as an automated check and which nothing implements - a separate rule, a separate measurement, not
asked for. Non-Python files: the census, the constitution's wording ("a source file", "a test
file") and the GM's own command are all about code, and `CLAUDE.md` and the constitution are
themselves far past 1,000 lines by the GM's own hand. Splitting anything not over the bar.

## Requirements

### FR-001 - the bar is 1,000 RAW lines, and passing it FAILS

A Python file of more than 1,000 raw lines fails the check. Raw lines, per clause 13's own words -
"deliberately unlike clause 12's logic units - because the motivating cost is token economy" - so
blank lines, comments and docstrings all count, exactly as `make audit` counts them today and
exactly as the GM's own census did. 1,000 passes; 1,001 fails.

### FR-002 - what is scanned

Every `*.py` in the repository, excluding:

- `legacy-hand-authored-pool/` - frozen write-once exhibits, already outside ruff, coverage and
  every re-run (feature 161). Three of them are over the bar and must stay untouched.
- `.clones/` - other sessions' working trees, which this clone does not judge.
- `specs/` - the feature record, including six retired one-shot splitters kept as history (R2). A
  record of what was done is not code that a session loads to work.
- `.git/`, `__pycache__/`, and any path already ignored by git.

`pool/`, `wip/`, `scripts/`, `.claude/` and `.specify/scripts/` ARE scanned. The scan is by
extension and path only - never by whether a file is imported - so nothing hides by being unused.

### FR-003 - the failure message routes the reader, and names the clone's obligation

On failure the check prints, for each offending file: its path, its line count, and how far over.
Then one message that says the responsible clone must split the file before this work can merge,
names the prescribed shape (a directory-module whose `CLAUDE.md` indexes the subfiles with a "look
here when" line each), points at the written procedure of FR-006, gives the worked example the GM
gave - `hamletgen/ways.py` becomes `hamletgen/ways/` with sub-modules - and names the two carve-outs
so a reader whose file is genuinely ordered data or a derived roster is not sent to do the wrong
work. It states no duration (feature 171's rule).

### FR-004 - the carve-out is stated IN the file, with a reason, and is auditable

Clause 13's ordered-data carve-out survives, because removing it would be a constitution change
nobody asked for. A file over the bar passes only if it carries, in its first 40 lines, a line
matching `FILE_SIZE_OK:` followed by a reason. The reason must be **at least 40 characters** - a
file-level exemption is argued, not tokenized, and 40 characters excludes `FILE_SIZE_OK: ordered`
while admitting a sentence. A marker with no reason, or a reason under the floor, FAILS with a
message saying so; that is the feature-170 rule (an escape must say why) applied to a file
annotation rather than a command.

Every file taking the carve-out is listed by `make audit` with its stated reason. **This is what
makes the soft floor honest**: a carve-out nobody can enumerate is a carve-out nobody revisits.

**Accepted limitation, with the alternatives priced** (the project's "record a decision to ACCEPT a
limitation" rule). No machine can judge whether a file really is one cohesive ordered dataset, so a
determined session can write a plausible sentence and pass. Two stricter designs were considered and
declined: (a) a recorded roster of permitted files, which is clause 14's own antipattern - a
hand-maintained list restating what the files already say - and which goes stale silently; (b) no
carve-out at all, which contradicts the constitution clause this feature enforces and would force
`wip/shiro-daika.gen.py`'s draw order to be fragmented across files for no token saving. What is
kept instead is VISIBILITY: the reason is in the file, in git history, and in `make audit`. Chosen
by the session, 2026-08-31; reopen it if the census of carve-outs ever grows past a handful.

### FR-005 - where it runs

The check is `scripts/check-file-scale.py`, following `check-duplicate-defs.py` in every respect
(R3): a `--selftest` that runs first and fails loudly if the checker itself is broken, then the
repo scan. It is wired into

- the skill Makefile's `lint` phase, which `make done` runs first (feature 168), so an oversize file
  is reported before the map roll is paid for; and
- `scripts/sync-with-main.sh` at push time, beside `check-duplicate-defs.py`, so the DIRECT route
  cannot land one either.

It carries its own suite (`scripts/test-check-file-scale.sh` for the guard tree, plus
`tests/tooling/test_file_scale.py` for the unit assertions), and each assertion is proven to FIRE by
deleting the rule and watching a test go red.

### FR-006 - the prescribed manner is written down, once

`docs/file-splitting.md`: the procedure a session follows when the check fires. It records what
already exists rather than inventing - the target shape and the two carve-outs from clause 13/14,
the "look here when" index format taken from the fourteen exemplars, the four residue-bucket vs
chain shapes those exemplars fall into, the verbatim-move discipline and import regeneration from
the six retired splitters (R1), and the four things a split can break from R4 (draw order, the
per-module coverage floors, the deferred-floor limit, and the path literals in `pyproject.toml` /
`.gitignore` / `gate-stamp.py` that stop matching silently). The check's failure message points here
and the constitution's clause 13 gains the pointer.

### FR-007 - the ten refactors

Every file in R2's census is brought under the bar. The move is VERBATIM - a split changes where a
definition's text lives, never what it does - and each new package gets a `CLAUDE.md` with a "look
here when" table naming every module. Nine are splits; one takes the FR-004 carve-out:

| file | disposition |
|---|---|
| `hamletgen/ways.py` (4,369) | -> `hamletgen/ways/` - the GM's own worked example |
| `tests/hamletgen/test_ways.py` (1,541) | -> `tests/hamletgen/ways/`, tracking the package above |
| `settlement/homestead_parts.py` (1,353) | -> `settlement/homestead_parts/` |
| `hamletgen/homesteads.py` (1,330) | -> `hamletgen/homesteads/` |
| `tools/pack_audit.py` (1,225) | -> `tools/pack_audit/` - a parser plus ~20 independent checks |
| `settlement/structures/fixtures.py` (1,212) | -> `settlement/structures/fixtures/` |
| `settlement/water_ways.py` (1,130) | -> `settlement/water_ways/` |
| `hamletgen/hinterland.py` (1,100) | -> `hamletgen/hinterland/` |
| `waterfields/seams.py` (1,069) | -> `waterfields/seams/` |
| `wip/shiro-daika.gen.py` (1,592) | **the FR-004 carve-out** - see the decision below |

**The one carve-out, argued rather than assumed.** `wip/shiro-daika.gen.py` is one map's
hand-authored draw script: a linear sequence of drawing calls whose statement order IS the draw
order, parked mid-feature (021), named by no Makefile target and measured by no coverage floor. It
is clause 13's "one cohesive ordered dataset ... whose row order IS the execution contract" as
nearly as a file can be, and splitting it would scatter one map's draw order across modules while
saving a resuming session nothing, since that session loads the whole map either way. It therefore
takes the marker and the written reason, and appears in `make audit` forever after. **This is put to
`spec-fidelity` explicitly**, because the GM said "we will need to actually do these refactors" and
a session quietly exempting one of ten is the exact shape Principle XVI exists to catch.

### FR-008 - the doctrine that said "not gated" is amended, not left contradicting itself

Three places currently say, in terms, that this rule is deliberately unenforced. All three are the
GM's own prior rulings and all three are superseded by this request:

- **constitution Principle X clause 13** - "this is an ask-the-question line, not a mandate". It
  becomes a gated line, with the carve-outs intact and a pointer to `docs/file-splitting.md`. A
  MINOR version bump with the amendment recorded in the constitution's own history block.
- **`CLAUDE.md`'s "Deliberately NOT enforced" paragraph** - which names file size explicitly: "File
  size past ~1,000 lines is REPORTED by `make audit`, never gated". It moves to the enforcement
  table as a new row.
- **`make audit`'s own printed blurb** - "Reported rather than gated on purpose: five files already
  exceed it". Rewritten to report the carve-outs of FR-004 instead, and its scan widened past
  `l7r tests` so `wip/` and `scripts/` stop being invisible to it.

### FR-009 - no regressions, measured

The refactors are verbatim moves, so the gate must be as green after as before, and every map
manifest byte-identical. The baseline is taken in a detached worktree at the merge base before the
first split, per Principle XIII, and the ten splits are verified against it - not against memory.
A split that changes a manifest is a defect in that split, not an accepted cost.

## Success criteria

1. `make done` fails, with the FR-003 message, on a tree containing a 1,001-line Python file - proven
   by deleting the rule and watching a test go red, not by assertion.
2. `make done` passes on the tree as this feature leaves it.
3. Every file in the repository outside the FR-002 exclusions is at or under 1,000 lines, or carries
   an FR-004 marker with a reason `make audit` prints.
4. Nine new packages exist, each with a `CLAUDE.md` "look here when" table naming every module.
5. Every map manifest in the pool is byte-identical to the pre-split baseline.
6. A reader who hits the failure message can complete the split from `docs/file-splitting.md` alone.

## Decisions recorded

| # | decision | class |
|---|---|---|
| D1 | raw lines, not logical statements - clause 13's own unit, because the cost is tokens | prescribed |
| D2 | the `lint` phase beside `check-duplicate-defs.py`, not a pytest and not a new phase (R3) | decided |
| D3 | the carve-out survives, needs a 40-character reason, and is printed by `make audit` | decided |
| D4 | `wip/shiro-daika.gen.py` takes the carve-out; the other nine split | **flagged to review** |
| D5 | `specs/` is excluded - a record of past work, including six retired splitters, is not loaded code | decided |
| D6 | clause 12 (function size) is out of scope; it is also unimplemented and was not asked for | deferred |
| D7 | the per-module coverage consequence of a split lands at `FULL=1`, which has never been green - inherited limit, stated not created (R4) | accepted |

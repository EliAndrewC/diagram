# Feature 173 - Files Stay at Human Scale, Enforced

**Status**: Draft - specified 2026-08-31; revised after `spec-fidelity` round 1 (four required changes, all applied: the one proposed carve-out reversed, FR-006 cut back to pointing at what exists, three counts corrected, the GM's census restored verbatim to `request.md`). [`request.md`](request.md) is the authority;
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
eighteen worked package indexes**, thirteen of which use the literal "look here when" wording the
clause names and five of which route the reader under a different header (`ci/`, `pipeline/`,
`tools/`, `tests/`, `tests/settlement/`). So: present, followable, and prescribed by example rather
than by instruction. FR-006 records what the failure message points AT, and deliberately writes no
new document.

**And the check itself is already owed.** The constitution's own v1.6.1 deferred-TODO block, added
GM-directed on 2026-08-16, records exactly this work: *"Automated file-length check (flags source
files past the threshold lacking a justification header) - recorded alongside clause 12's deferred
expression-counting gate check"* (`.specify/memory/constitution.md:328`). This feature closes a TODO
the constitution has carried for two weeks, and the marker-with-a-reason design of FR-004 is the
shape that TODO names, not one this session invented.

## Scope, stated exactly

**IN**: the check, its wiring, the written procedure, the constitution and `CLAUDE.md` amendments
that follow from gating a rule that was explicitly not gated, and the ten refactors.

**OUT**: clause 12 (functions past ~1,000 logical statements), the OTHER half of the same
deferred-TODO block, which nothing implements - a separate rule, a separate measurement, not asked
for. Non-Python files: the census, the constitution's wording ("a source file", "a test
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
- `specs/` - the feature record, including fourteen retired one-shot splitters kept as history (R2). A
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
carve-out at all, which would delete a clause of the constitution nobody asked to delete, and which
the constitution's own deferred TODO forecloses by specifying a check that "flags source files past
the threshold LACKING A JUSTIFICATION HEADER". What is kept instead is VISIBILITY: the reason is in
the file, in git history, and in `make audit`.

**The mechanism ships with ZERO files using it, and that is the point.** Spec review round 1 rejected
this feature's one proposed carve-out (below), so nothing in the tree takes the marker on the day it
lands. A carve-out that is available and unexercised is a rule with a stated exit; a carve-out
exercised by its own author on the day it ships is a rule with a hole. Chosen by the session,
2026-08-31; reopen it if the census of carve-outs ever grows past a handful.

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

### FR-006 - the failure message points at what already exists; no new document is written

The GM asked to be TOLD whether the prescription is present. It is (R1), so the message routes the
reader to the three things that already carry it - constitution Principle X clause 13, `CLAUDE.md`'s
"Files stay at human scale", and one named exemplar package (`settlement/structures/`, whose own
docstring explains the residue-bucket shape and why `StructuresMixin` exists) - and this feature
writes no procedure manual.

**This is a scope REDUCTION made at spec review.** The first draft specified a new
`docs/file-splitting.md` gathering the split discipline and the fourteen retired splitters' method.
The reviewer's objection stands: the GM asked a question, not for a manual, and a substantial new
engineering document is scope the request does not contain. The material is not lost - it is in
`research.md` R1 and R4, where the next session that splits a file will find it, and where the GM
can read it and ask for the document if they want one.

### FR-007 - the ten refactors

Every file in R2's census is brought under the bar - **all ten of them, by splitting**. The move is
VERBATIM - a split changes where a definition's text lives, never what it does - and each new
package gets a `CLAUDE.md` with a "look here when" table naming every module.

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
| `wip/shiro-daika.gen.py` (1,592) | -> `wip/shiro_daika/` - see the reversed decision below |

**The carve-out this spec first proposed was PUT TO REVIEW AND REJECTED, and the rejection is
recorded rather than quietly dropped.** The first draft gave `wip/shiro-daika.gen.py` the FR-004
marker on the argument that a hand-authored map draw script is clause 13's "one cohesive ordered
dataset". `spec-fidelity` read the file instead of the description and returned NOT LEGITIMATE on
three grounds, all of which check out:

- **It is not what the carve-out describes.** It defines six functions with real logic - `_well_blocks`
  is a 55-line algorithm with a nested helper that cuts street bands out of a quarter's bbox and grids
  each surviving rectangle; `_point_in` is a point-in-polygon routine - and threads mutable engine
  state through the file (`s.bound` saved and restored twice, `s.placed`, `s.block_polys`). That is a
  program in which statement order matters, which is true of nearly every imperative module here,
  `hamletgen/ways.py` included. **If "execution order is a contract" qualifies a file, the carve-out
  swallows the rule.**
- **It fails the purpose test.** The GM's "we will need to actually do these refactors" refers to the
  census they had just pasted, in which this file sits second. Exempting one of ten is the "X except
  where Y" Principle XVI names.
- **Two supporting claims did not survive checking.** The file is tracked and NOT gitignored (only
  `wip/*.svg|png|json|html` are), and `pyproject.toml` has no `wip` entry - so unlike the three
  `legacy-hand-authored-pool` exhibits FR-002 excludes by path, it is live source inside the lint and
  type toolchain. It is not frozen; it is unfinished.

**So it splits like the other nine**, into `wip/shiro_daika/` (the hyphen cannot be a package name).
The session's own argument is left standing above so the next reader can see what was tried and why
it was wrong - the answer to "is a work-in-progress draft a different case?" was that the GM invited
that as a QUESTION in this very request, not as a carve-out written into the spec.

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
4. Ten new packages exist, each with a `CLAUDE.md` "look here when" table naming every module.
5. Every map manifest in the pool is byte-identical to the pre-split baseline.
6. A reader who hits the failure message is routed to clause 13, `CLAUDE.md`'s "Files stay at human
   scale", and a named exemplar package - each of which exists today and none of which this feature
   writes.
7. No file in the tree carries an `FILE_SIZE_OK:` marker on the day this lands.

## Decisions recorded

| # | decision | class |
|---|---|---|
| D1 | raw lines, not logical statements - clause 13's own unit, because the cost is tokens | prescribed |
| D2 | the `lint` phase beside `check-duplicate-defs.py`, not a pytest and not a new phase (R3) | decided |
| D3 | the carve-out survives, needs a 40-character reason, and is printed by `make audit` - the shape the constitution's own v1.6.1 TODO specified ("lacking a justification header") | prescribed |
| D8 | no new procedure document; the message points at clause 13, `CLAUDE.md` and one exemplar package | reduced at review |
| D4 | `wip/shiro-daika.gen.py` splits like the other nine - the carve-out this spec proposed for it was put to `spec-fidelity` and REJECTED; FR-004's mechanism ships with zero files using it | **reversed at review** |
| D5 | `specs/` is excluded - a record of past work, including fourteen retired splitters, is not loaded code | decided |
| D6 | clause 12 (function size) is out of scope - the other half of the same deferred TODO, not asked for | deferred |
| D7 | the per-module coverage consequence of a split lands at `FULL=1`, which has never been green - inherited limit, stated not created (R4) | accepted |

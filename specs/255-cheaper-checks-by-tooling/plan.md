# Plan - 255 cheaper checks by tooling

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). The measurements behind it:
`specs/251-tiered-subagent-checks/research.md` R5, R7, R8, R9.

## Constitution Check

- **XVI**: spec FAITHFUL at round 2; this plan reviewed (MODE 4) before any tick.
- **I / VI**: no check's judgment is touched; each change to how a check is FED is proven on recorded findings
  before it stands (FR-001), and a candidate that misses leaves its agent as it was.
- **X**: no engine code; each new script is stdlib, under the 1,000-line bar, with a test module in
  `tests/tooling/`.
- **Guard files**: the skill Makefile is one; each new target's edit carries `GUARD_EDIT_OK` with a reason.
- **Route**: `scripts/`, `.claude/agents/`, the skill Makefile, `tests/tooling/`, docs -> DIRECT.

## Design

- **P0 the harness is feature 251's, reused as it stands**: `measure/seeded.py prepare` (a recorded run's prompt, a
  worktree at the commit it saw, the current agent files copied in), `measure/run_seeded.sh` (headless, hooks off,
  three at a time), the weight arithmetic of 251's R5. A candidate's agent-file change is made in the CLONE, so the
  worktree copy carries it; a candidate NOT ADOPTED is reverted in the clone before the next batch. Each batch's
  run count and rough weight are stated in the session's report BEFORE it is launched. The recorded cases are
  251's: `source-applicability` has none prepared yet - two are picked from its 26 recorded runs by
  `seeded.py catalog`, one with a NOT-APPLICABLE or MISSING verdict and one clean.
- **P1 `scripts/_source_entries.py`, `make source-entries KEYS=a,b`** (FR-002): parses `research/SOURCES.html` for
  the entry whose anchor or `<code>` key matches, prints its citation line, write-ups and `Used for:` line, then
  every footnote on `research/citations/**/*.html` whose key matches, with its assertion (reusing
  `_quote_verbatim.footnotes` and `assertions` by import). Contract: a "step 0" in `source-applicability.md`.
- **P2 scoped text** (FR-003): `_record_prepass.py --section` gains `--text`, which prints the section's visible
  text and its numbered HTML source lines after the candidate list; `_quote_verbatim.py --notes` already writes
  passage and assertion per note. Contracts: for a scoped check the handed text is the reading list.
- **P3 the batching line** (FR-004), one sentence, identical in the seven contracts, placed directly under each
  file's opening paragraph: "Send the reads, greps and fetches you already know you need in ONE message, and do
  not spend a turn on a single lookup whose result does not decide the next one." Tested on the twin with
  251's `verify-250-cr` and `verify-clean` cases; turns and weight compared with R7's medium-and-high runs of
  the same cases and with the recorded runs.
- **P4 `scripts/_source_pages.py`, `make source-pages OUT=<dir> URL=<u1> [URL=...]`** (FR-006): the page-text saver
  of 253's `measure/fetch_text.py`, promoted to a script with a manifest (`pointer | file | state`); the contract
  tells the reader to Grep then Read around hits. R5's three `source-reader` cases; the URLs are taken from each
  recorded prompt by the session, not by a model.
- **P5 the fixed-context probes** (FR-007): `--agents` JSON probes on Haiku run from `/diagram` itself (so the
  session memory index is in play), varying one thing at a time: the tool list; a copy of the repository with
  `CLAUDE.md` removed (a scratch worktree, never the clone); `--append-system-prompt` present or absent; and the
  memory index present or moved aside IN A SCRATCH COPY of the project's memory directory only if the harness
  allows pointing at one - otherwise its size is reported from its character count and the measured per-token
  ratio of the other probes. Trims: memory index lines shortened to a hook of at most 120 characters; a tool an
  agent's recorded runs never called (R9's per-tool counts) removed from its `tools:` line.
- **P6 `scripts/_review_facts.py`, `make review-facts MAP=<pool map>`** (FR-005): one call that runs the
  measurements `settlement-review.md`'s "Tooling" section already names and prints them together; the
  `Validated examples` section moves to `.claude/agents/settlement-review-examples.md`, which the agents-directory
  test must not mistake for an agent (it carries no frontmatter; `tests/test_agent_models.py`'s roster is files
  WITH a `name:` - checked before the move, and the move is dropped if that test cannot tell them apart without
  changing what it asserts). Two recorded `settlement-review` runs with findings, picked by `seeded.py catalog`
  from the smallest of the 123.

## Order

T01 source-entries -> T02 scoped text -> T03 the batching line -> T04 source-pages -> T05 the probes and the two
trims -> T06 review-facts and the shorter contract -> T07 the record -> T08 gates and landing. Each of T01-T06
ends with its seeded batch scored in `research.md` and the candidate ADOPTED or NOT ADOPTED.

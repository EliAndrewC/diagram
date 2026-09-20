# Plan - 256 defined subagents launch without the root `CLAUDE.md` and the memory index

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). The measurements behind it:
`specs/255-cheaper-checks-by-tooling/research.md` R2, R3, R5, R7.

## Constitution Check

- **XVI**: the spec is reviewed against the GM's words before any of this is done; this plan is reviewed (MODE 4)
  before a task is ticked. The field is set on all twelve agents in every case (FR-002, FR-004) - no exception at the
  first landing; Amendment 2's P10 carries the one exception the GM approved on the session's
  measured recommendation, `spec-fidelity`, named in the tier test.
- **I / VI**: no check's judgment is touched. What changes is what a check is handed at launch, and it is proven on
  recorded findings with a same-setting control (FR-003).
- **X**: no engine code, no new Python under `l7r/`. One shell harness under the feature's `measure/`, as 251 and
  255 kept theirs.
- **Guard files**: none edited at the first landing. Amendment 1 edits two on the GM's word of 2026-09-20:
  `tests/test_agent_models.py` gains the field's test (P6) and the skill Makefile gains `make scatter-bases` (P8),
  each with `GUARD_EDIT_OK` where the guard asks for it.
- **Route**: `.claude/agents/`, root `CLAUDE.md`, `docs/`, `specs/` -> DIRECT.

## Design

- **P1 the reading (FR-001).** Every rule of the root `CLAUDE.md` - house style, research, development workflow,
  verification and iteration, session clones, what is enforced, key paths - is put to EACH of the twelve contracts,
  one rule and one agent at a time, with one question: does this check's JOB depend on it, and does the contract
  already say it? No class of rule is settled in advance. Several checks do session-shaped work - `perf-audit`
  reads the gate's bands and writes its record with `make perf-confirm`, both fidelity agents run `make figures` and
  `spec-fidelity` records `make plan-verdict`, `settlement-review` and `size-audit` run make targets - so a rule
  about make, the gate, the clones or spec-kit is read against them like any other and may come out "moved".
  `research.md` holds the table: a row per rule, a column per agent, each cell `stated`, `moved` or `does not bear`.
  The two nested files are read the same way for every check that works under either tree, and the table says per
  agent which tree it reads: the skill's `CLAUDE.md` for every agent that reads or runs anything under
  `.claude/skills/diagram/` (which includes the five research agents, whose pages live inside the skill tree,
  `entry-drift`, whose subject is the docstrings under `l7r/diagram/interactive/`, and both fidelity agents, which
  run `make figures` from there), and `research/CLAUDE.md` for every agent that reads under `research/`
  (`escalation-check` among them). A moved rule is written once, short, in the contract's own voice, in the section
  that already covers its subject, or under `## House rules you check against` where none does.
- **P2 the field (FR-002).** `omitClaudeMd: true` on its own line in each frontmatter, after `effort:`. (P10 takes it
  off `spec-fidelity.md` again, approved by the GM on the session's recommendation (2026-09-20).)
- **P3 the proof (FR-003, FR-004).** `measure/dispatch_seeded.sh`: a headless Sonnet session in the case's worktree
  reads `prompt.txt` and dispatches the agent ONCE with it; the SUBAGENT's transcript gives the reply, the turns,
  the usage folded per message id, the first-turn input, and whether the prompt it received is the recorded one
  character for character (a run whose prompt is not verbatim is discarded and re-run, not scored). Case
  directories are made by 251's `seeded.py prepare`; the control tree gets the clone's agent files with the field
  removed, the candidate tree gets them with it. Cases: `tw-250` and `tw-clean` (255 R3's transcripts
  `79288e26/3fc3f084` and `79288e26/427f9b4c`) on `spec-fidelity-verify`; the homesteads "garden's sun" section
  (`881af52a/abea4bd5`, cut as in 255 R2, with the pre-pass listing but WITHOUT 255's rejected scoped text) on
  `record-format`. Scoring is against the control first and the recorded findings second.
- **P4 the measurement (FR-006), taken where the index actually loads.** A scratch worktree is its own project and
  loads no memory index (feature 255, R5), so it cannot show the index leaving. Both legs are therefore dispatched
  from `/diagram`, the way 255 R7's probe was: `measure/probe.sh`-style, a headless session started in `/diagram`
  with the agent defined inline (`--agents`) from `entry-drift`'s REAL frontmatter and contract body - its pinned
  model and tools - once as it stands and once with `omitClaudeMd: true`, on a one-line prompt; the subagent's
  first-turn input is read from its own transcript. Nothing is written under `/diagram`. Two short Opus runs. The
  same limit is stated for P3: its worktree legs, candidate and control alike, run with no memory index, so the
  proof is of the `CLAUDE.md` files leaving; the index leaving is covered by FR-001's finding that no contract
  refers to it, and by this measurement.
- **P5 the record (FR-006).** Root `CLAUDE.md`'s review-subagents bullet gains one sentence; `docs/efficiency-
  tooling.md`'s feature-255 row gains the outcome; `docs/make-targets.html` is unaffected (no target added).

## Order

T01 the reading and the moved rules -> T02 the field in twelve files -> T03 the proof (six runs) and, if needed,
FR-004's second pair -> T04 the before-and-after measurement -> T05 the record -> T06 gates and landing.

## Amendment 1 (2026-09-20)

- **P6 the guard (FR-007).** One test in `tests/test_agent_models.py`, `test_every_agent_launches_without_the_claude_md_files`:
  for every file in the derived roster, `frontmatter(...)["omitClaudeMd"] == "true"`, its message naming the field,
  the GM's ruling of 2026-09-19 and this feature. The module docstring gains that ruling. The tier table is untouched. It is a
  gate guard already listed in root `CLAUDE.md`'s table (`test_agent_models.py`), so that row gains the clause.
- **P7 the fidelity contracts (FR-008).** In `spec-fidelity.md`, question 4's "extra verification the GM did not
  request" becomes "verification of something the GM did not ask for", and a paragraph after question 5 states the
  distinction with this feature's round 1 as the worked example; `spec-fidelity-verify.md` gains the same paragraph
  beside its four questions. The seeded run: `dispatch_seeded.sh` on round 1's recorded prompt
  (`6a88965e.../agent-ac47419e8b1d79dc7`), the tree at the spec's first commit, the amended contract copied in; one
  run, scored on four items - old FR-003 must NOT be cut, and the failure branch, the memory-index sentence and
  SC-004 must still be raised.
- **P8 the leftovers (FR-009).** `make scatter-bases MAP=<pool map>` in the skill Makefile (`GUARD_EDIT_OK`, a new
  read-only diagnostic) running `l7r.diagram.tools.scatter_audit` on the map's SVG; the contract's paragraph names
  the target. The `(Tools: ...)` tails cut from three descriptions. `tests/test_agent_models.py` ->
  `.claude/skills/diagram/tests/test_agent_models.py` in the seven contracts that cite it.
- **P9 the eight pairs (FR-010, FR-011).** FR-003's harness and rule. Cases, each a recorded run with known findings, cut to a
  slice where the recorded run was large: `entry-drift` farmhouse (251 R5, DRIFTED); `escalation-check` 242 (251 R5,
  3 KEEP 1 REWRITE 2 CUT); `quote-check` capitals fn-235..240 with its `make quote-verbatim` report (255 R2);
  `source-applicability` Shanghai (255 R1, the two MISSING limits); `source-reader` 09-12 with its saved pages (255
  R4, the two partial passages); `spec-fidelity` feature 251's MODE 2 round 1 (`6a88965e/23035d6f`, CHANGES
  REQUIRED). And two pairs with no recorded run, scored against the control and the fixture's KNOWN defect:
  `building-review` on `tests/fixtures/ochiba-no-scale-red.svg` (a sheet with its scale bar removed - an ERROR that
  review names) and `size-audit` on `tests/fixtures/ochiba-big-bath-red.svg` (an oversized bath), each staged in a
  HEAD worktree as a pool subject `pool/magistracies/ochiba-red/` beside a copy of the Ochiba magistracy's notes, and
  rendered to PNG by the engine's rasterizer. Sixteen runs; the batch's size is stated before launch.
  `settlement-review` and `perf-audit` are priced in `research.md` with their reasons (FR-010).

Order: T07 -> T08 -> T09 -> T10 -> T11.

## Amendment 2 (2026-09-20)

- **P10 the GM's approval of three recommendations (FR-012 to FR-014).** No new machinery. The contract wording is sharpened in place
  (P7's paragraph gains the test-versus-guard sentence); `omitClaudeMd` is deleted from `spec-fidelity.md` alone and
  the tier test gains `KEEPS_CLAUDE_MD`, a name-to-reason table the guard skips and asserts is not stale, so the hole
  in FR-007's guard is exactly the size of what the GM approved and cannot silently grow; root `CLAUDE.md`, the guard table's
  gate row, `docs/efficiency-tooling.md` and `research.md` R8 say so. `settlement-review` and `perf-audit` get no
  harness at all - FR-014 is watching, and FR-004 is already the route for what watching finds.

Order: T07 -> T08 -> T09 -> T10 -> T11 -> T12.

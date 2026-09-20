# Plan - 256 defined subagents launch without the root `CLAUDE.md` and the memory index

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). The measurements behind it:
`specs/255-cheaper-checks-by-tooling/research.md` R2, R3, R5, R7.

## Constitution Check

- **XVI**: the spec is reviewed against the GM's words before any of this is done; this plan is reviewed (MODE 4)
  before a task is ticked. The field is set on all twelve agents in every case (FR-002, FR-004) - no exception.
- **I / VI**: no check's judgment is touched. What changes is what a check is handed at launch, and it is proven on
  recorded findings with a same-setting control (FR-003).
- **X**: no engine code, no new Python under `l7r/`. One shell harness under the feature's `measure/`, as 251 and
  255 kept theirs.
- **Guard files**: none edited. `tests/test_agent_models.py` is not touched.
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
- **P2 the field (FR-002).** `omitClaudeMd: true` on its own line in each frontmatter, after `effort:`.
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

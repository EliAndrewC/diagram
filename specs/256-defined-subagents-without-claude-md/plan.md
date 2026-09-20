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

- **P1 the reading (FR-001).** The root `CLAUDE.md` is taken section by section - house style, research, development
  workflow, verification, session clones, what is enforced - and each rule is put to each of the twelve contracts
  with one question: does this check's JOB depend on it? A rule about how a SESSION works (clones, make, the gate,
  spec-kit) bears on no check, because a check edits nothing and lands nothing. The candidates are the rules about
  what the record and the maps must SAY: hyphens only and American spellings with the quotation exemption; the caste
  sense of "people"; "domain", never "demesne"; gender-neutral office-holders; the kanji triangle; the four decision
  classes and the knob-or-liberty rule; a citation's form and the GM's notes as canon. A first grep (2026-09-20)
  shows which contracts already carry which; the reading confirms each by eye and `research.md` holds the table.
  The two nested files are read the same way for the checks that work under them: `research/CLAUDE.md` for
  `source-reader`, `quote-check`, `record-format`, `source-applicability`, `entry-drift`; the skill's `CLAUDE.md`
  for `settlement-review`, `building-review`, `size-audit`, `perf-audit`. A moved rule is written once, short, in
  the contract's own voice, under a heading `## House rules you check against` (or folded into the section that
  already covers it).
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
- **P4 the measurement (FR-006).** The first-turn input of `entry-drift` - the smallest real contract - dispatched
  by the same harness from a worktree, with the field and without it, on a one-line prompt; both legs are rows in
  `research.md`. Haiku cannot stand in here because the agent file pins its model, so this is two short Opus runs.
- **P5 the record (FR-006).** Root `CLAUDE.md`'s review-subagents bullet gains one sentence; `docs/efficiency-
  tooling.md`'s feature-255 row gains the outcome; `docs/make-targets.html` is unaffected (no target added).

## Order

T01 the reading and the moved rules -> T02 the field in twelve files -> T03 the proof (six runs) and, if needed,
FR-004's second pair -> T04 the before-and-after measurement -> T05 the record -> T06 gates and landing.

# L7R Diagram - the settlement and building map generator

<!-- container-mounts: ..:/host-l7r-repo -->

This repository is the `/diagram` skill of the GM's L5R worldbuilding project: building plans
(Mode A) and settlement maps (Mode B), deliberately one skill and one package at
`.claude/skills/diagram/` (why one, and what would change it: `dev/skill-boundary.md`). Usage is
`.claude/skills/diagram/SKILL.md`; the engine dev loop is `.claude/skills/diagram/CLAUDE.md`, which
auto-loads under that tree.

The GM's setting notes that the research cites live in gm-assistant, mounted at
`/host-l7r-repo/gm-assistant` (`setting/`, `cosmology/`, `campaigns/`; on GitHub at
<https://github.com/EliAndrewC/gm-assistant/tree/main/setting>). The canonical campaign notes are
`/host-l7r-repo/setting/l7r.md`; nothing here edits them, and nothing here runs git against
`/host-l7r-repo`. The webapp, the content skills and Obsidian Portal are gm-assistant's; a session
here does none of that.

**A feature is REPOSITORY + number.** This repository's numbers continue from 132 (gm-assistant
restarts at 200); features 001-131 that concern the diagram live here.

## Core rules

### House style

Enforced by `scripts/house-style-hooks.sh`, which corrects the text rather than refusing the edit.

- Hyphens only: no em-dashes or en-dashes anywhere in the project.
- American spellings, never British ones, in everything - prose, docs, generated content, tests,
  comments and code identifiers.
- Both rules stop at a quotation: a passage quoted from another source, and the GM's own writing
  (`<!-- SOURCE: GM NOTES -->` blocks, `l7r.md`, `specs/*/request.md`), keep their own dashes and
  spellings.
- "People" has caste meaning: only samurai are "people". In demographic, statistical or analytical
  writing use humans / inhabitants / population / a caste term. `people` is fine for samurai and in
  narrative, lore, dialogue, vow and folktale voice. Full rule: `docs/l7r-style.md`.
- "Domain", never "demesne"; silently fix it in any text you edit.
- Gender-neutral office-holders: they / their / them for a generic daimyo, governor, magistrate,
  minister or samurai; named characters keep their own pronouns.
- Kanji in generated content passes the kanji - romaji - meaning triangle (constitution XI): real
  characters, a plausible reading, a meaning that maps back.
- Never invent setting details that contradict the GM's notes.

### Research

Constitution XII. The full record with the GM's rulings is `docs/research-doctrine.md`; the
operative form of the citation rules (the footnote shape, the citations pages, the download list)
is `.claude/skills/diagram/research/CLAUDE.md`, which auto-loads when a session edits the record.

- A question about how a place was built, farmed, planted or lived in is a RESEARCH question. Run
  the search pass before deciding, before asking the GM, and before writing "guess". The GM is asked
  only when the record is silent or contradictory, and the ask says what was searched and found.
- Where the research supports more than one form, it becomes a knob with per-settlement variance
  rolled from the map's seed, never a choice. A degree along a continuum is calibrated liberty; a
  choice between distinct forms is a knob.
- Every rendering decision is recorded in one of four classes - historically accurate, deliberate
  deviation, map drawing convention, guess - in `research/` (the finding), the operative doc (the
  rule), the point of change (the pointer) and the feature's spec under "Decisions Recorded". An
  unlabeled guess is the one failure.
- Record the why of every research-driven rule and magic number beside the rule. Record a decision to
  ACCEPT a limitation with what it costs, the alternatives that were priced, and who chose.
- A citation is a footnote at the assertion quoting the passage verbatim from a public page the
  reader can open, in English translation marked as one. A source that cannot be read is not cited;
  the claim may stand with an absence note saying what was searched. The GM's own campaign notes are
  canon, not evidence, and need no citation. A source only the GM can fetch goes at the END of
  `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, in their format.
- The record is HTML under `research/`, each heading the question a reader would ask from the map,
  each entry written for a casual reader: glossary tooltips for terms, session notes in HTML
  comments, nothing about what the entry used to say. A modal's explanation is written from a research
  section its `Entry:` names. It is written PER ENTRY and ASSEMBLED into the pages a reader opens
  (feature 258): a question is `research/<page>/NNN-<heading id>.html`, its footnotes are the
  `.notes.html` beside it, a source is `research/sources/NNNN-<key>.html`, and `make record` writes the
  pages, `research/citations/<name>.html` among them. Find an entry with a glob on the key or a grep over
  the page's directory - there is no index - and never edit an assembled page; footnote numbers are
  allocated at assembly and are typed nowhere.
- Reading and checking are dispatched to agents, in the background: `source-reader` (read what you
  cite), `quote-check`, `record-format`, `source-applicability` (judged BEFORE a source's numbers
  reach a map or a rule), `entry-drift`. What is mechanical runs FIRST, as a script, and its output goes
  in the agent's prompt: `make source-pages OUT=<dir> URL=<u>` before `source-reader` (the page itself, saved
  to grep, where a fetch gives an extract), `make quote-verbatim PAGE=<name> [NOTES=<ids>]` before `quote-check` (is the
  passage on the page, character for character), `make record-prepass PAGE=<name>` before
  `record-format`, `make size-table PLAN=<svg>` before `size-audit`.

## Development workflow

Spec-driven development under `.specify/memory/constitution.md`; this file operationalizes it. The
full doctrine with the GM's rulings and the incidents behind them: `docs/spec-kit-and-reviews.md`.

- Feature work (a new generator, tier, tool or guard) is a spec-kit feature: `/speckit-specify` ->
  plan -> tasks -> implement. A tweak (a wording fix, one bug, one regenerated map) is done directly.
  Ask before chain-firing on an ambiguous case.
- A spec number comes from `make claim SLUG=<slug>` (one lock over every clone; `PEEK=1` looks
  without claiming). It prints the `SPECIFY_FEATURE` and `SPECIFY_FEATURE_DIRECTORY` exports; export
  BOTH. Commit and push the spec directory as soon as `spec.md` exists. No feature branches: commit on
  `main` inside the clone.
- Every task is `research: rendering` or `research: physical`; a physical task carries the boxes
  `research pass`, `source-reader confirmed`, `recorded and cited`, `quote-check confirmed` and
  `source-applicability confirmed`, ticked before the task is (`tests/test_task_research_boxes.py`).
- Run the chain end to end, unattended. The GM starts work and leaves: answer each stage's own
  questions, record each decision in the artifact where it arose, and stop only when a wrong guess
  would cost an hour-plus to unwind or the thing genuinely cannot be done. Persistence means
  PROGRESS, not changes: when stuck, the next step is a measurement.
- Do the literal thing (constitution XVI). Asked for X, build X, never "X except where Y". An
  exception that still looks necessary is put to an independent `spec-fidelity` subagent with the
  GM's request verbatim; if it agrees, carry on and raise it with the GM once the implementation
  works.
- A spec is reviewed against the GM's own words by `spec-fidelity` before implementation
  (`scripts/review-gate.sh` refuses the push otherwise): up to five rounds on the initial acceptance,
  then stop and escalate; an amendment after acceptance resets the counter. A plan's decisions are
  reviewed by the same agent before a task is ticked (`make tick`, `scripts/plan-gate.sh`). A later
  round is handed the previous verdict and the diff by `scripts/review-round-hooks.sh`.
- No known regressions (constitution XIII). A regression is measured, never remembered: the baseline
  is taken in a detached worktree (`git worktree add --detach /tmp/base HEAD`, never a stash) and
  each failure is checked against the clone, because a worktree carries no gitignored artifacts.
  Pre-existing failures are ledgered, not fixed under someone else's feature. Three exits: fix it,
  revert it with a written impossibility investigation, or an explicit GM waiver; fixing is the
  expected one. A regressed state stays in the clone, unpushed.
- Fix defects where you find them (constitution XIV), in the same work with the same verification.
  The only deferrable fix is a complete overhaul, and deferring one delivers the measurement, the
  mechanism and a sketch. Record a fix that FAILED at the point of change.
- Review subagents (`settlement-review`, `building-review`, `size-audit`) run at acceptance, in the
  background, one map per agent; every pass is a row in `docs/review-ledger.md`. To improve one, add
  the general rule, prove it fires on the unfixed artifact, then fix the artifact. Findings for the
  GM go through `escalation-check` first. Every check runs on the TIER its file pins - a model and an
  effort, never inherited (`tests/test_agent_models.py` holds the table; judgment is on Opus, and a
  downgrade stands only after seeded-fault runs on known findings - THREE a leg, because one run of a
  judging agent is not a stable oracle). An ad-hoc agent is dispatched with
  an explicit `model` - `sonnet` to read, fetch, translate or extract, `opus` for anything that judges -
  and never with none: with none it runs on the session's model, and `agent-model-hooks.sh` refuses it
  (`haiku` only for a plain description of a page - it misread a table's columns where sonnet did not). A DEFINED agent launches without this file, the nested `CLAUDE.md` files and the memory index
  (`omitClaudeMd: true`, feature 256, GM 2026-09-19: *"If there's something that a subagent should know, it should be in
  the subagent specification"*) - a rule a check needs is written in its contract, and a new agent file carries the field;
  an ad-hoc agent keeps all three, and so does `spec-fidelity` alone, which the GM approved on the session's
  measured recommendation, 2026-09-20 (the tier test
  names the exception and enforces the field on every other agent file). The review agents are pre-authorized through
  `container-scripts/append-system-prompt.md`; if one is skipped, check `type claude` first.

## Verification and iteration

The machinery in one picture, with the GM's rulings and the measurements: `docs/efficiency-tooling.md`.

- Everything runs through `make`; the hooks refuse or rewrite anything else. The ladder in the skill:
  `make quick` while iterating (testmon selects by change; `ALL=1` runs every quick test), `make done`
  once at the end (the whole gate: lint, the static checks, the pool roll, 100% coverage over the
  whole engine), `make done FULL=1` (prompts; adds the perf bookends). What each costs is asked of
  the record (`make audit`, `scripts/_gatecost.py <target>`), never written here.
- `make done` reports every failure together: fix them all, re-run once. Background the final gate
  and act on its notification; never poll.
- Python: ruff, ruff format, pyrefly, and 100% coverage owed by everything the day it lands, held as a
  floor on the gate (never `fail_under` in `pyproject.toml`). An inner function that is hard to test
  is lifted to module level and tested with plain inputs; dropping the test is not an option. A
  Python file past 1,000 raw lines fails the gate.
- An overlap check against the features already on the map builds an index once
  (`settlement/_geom/indexes.py`) and asks it per candidate; a plan that adds one says how it is
  indexed.
- Edit with `Edit`, not heredoc'd Python; a mechanical sweep uses `scripts/_patch.py`.
  Foreground-regenerate only the motivating map. Read derived data from the recorded manifest, not by
  re-running the generator.
- Batch: send the lookups you already know you need in one message; the batching hook blocks a run
  of single-call recon turns.

## Session clones

The full spec and every failure mode: `docs/session-clones.md`.

- Every session that modifies this repo works in `/diagram/.clones/<session-name>` (the session's
  name, kebab-cased; `diagram` and `gm-assistant` are forbidden; an unnamed session asks the GM to
  `/rename` it). Create it with `git clone /diagram .clones/<name>`; reuse it on resume.
- GitHub `main` is main; `/diagram` is a mirror that fast-forwards from it and is never a workspace
  (render-sync is the one thing that runs there). `scripts/sync-with-main.sh sync-in` at the start of
  every piece of work; the prompt hook runs it.
- Stop-work procedure, every time you stop: commit in the clone, then `scripts/sync-with-main.sh
  done` from inside it. The route is chosen from the delta, never by you: no engine code -> DIRECT (a
  locked fast-forward push); engine code (`l7r/**/*.py`, `pool/*.gen.py|*.json`; a comment-only or
  formatting edit does not count) -> GATED on a green local `make done`, with a CodeBuild build only
  when `remote` is on and main moved on engine paths. A feature with an open task lands nothing
  except its own `specs/` claim.
- Never rewrite history (no rebase, squash, amend or force push); never commit or push against
  `/host-l7r-repo`. `git -C <path>` for every git call, one tree per command, no bare `cd`.
- A paid prompt (`make ci-image`, any `FULL=1` dispatch) may be answered by the session; the logged
  reason says so and quotes the GM's 2026-08-25 authorization.

## What is enforced

Every guard has a test companion that `make hooks-test` runs, and its message names the compliant
command. The full record - rule, mechanism, the measurement and the ruling behind each - and the
doctrine for writing a guard: `docs/guards.md`.

| guard | what it does | escape |
|---|---|---|
| `repo-safety-hooks.sh` | no force push, no history rewrite; no git writes to `/host-l7r-repo` | none; `HOST_GIT_OK` |
| `source-block-hooks.sh`, `readme-hooks.sh` | the GM's SOURCE blocks and READMEs are theirs to write | - |
| `house-style-hooks.sh` + `check-house-style-delta.py` | corrects dashes and spellings in Edit, Write and Bash payloads; `make quick` fails on one in the delta | - |
| `make-only-hooks.sh` | refuses a bare interpreter or pytest; rewrites a targeted pytest to `make test-file` | - |
| `guard-file-hooks.sh` | a guard-file edit carries `GUARD_EDIT_OK` and a reason; a Makefile recipe comment must not run | - |
| `clone-sync-hooks.sh` | forbidden names, name-routing, a live claim, a stale clean HEAD (synced in), a stray mirror commit | - |
| `main-tree-hooks.sh` | a write that would land in the mirror is moved to the clone; one naming it is refused | `MAIN_TREE_OK` |
| `discard-hooks.sh` | a checkout or restore that would discard uncommitted work | `DISCARD_OK` |
| `conflict-marker-hooks.sh` | a `git add` or commit that would stage conflict markers | `CONFLICT_MARKERS_OK` |
| `shell-check-hooks.sh` | a command that does not parse, an executing backtick, a `-m` with a quote or newline, a foreign co-author | `SHELL_CHECK_OK` |
| `no-branch-hooks.sh` | no branches | `NO_BRANCH_OK` |
| `no-poll-hooks.sh` | no busy-wait; corrects a self-matching `pgrep`; a file-watching loop is backgrounded and given a proof of life | `POLL_OK` |
| `batching-hooks.sh` | blocks a run of single-call recon turns, warning one turn early | - |
| `measure-hooks.sh` | a second expensive run with nothing changed between | `MEASURE_OK` |
| `gate-hooks.sh` | no `-k` subset as the only run before the gate | `GATE_OK` |
| `pair-hooks.sh` + `_review_owed.py` | the gate and the settlement-review run together when a pool map's layout moved; one map per agent | `PAIR_OK` |
| `escalation-hooks.sh` | a review dispatch arms, an `escalation-check` dispatch disarms, before the turn ends | `ESCALATION_OK` |
| `review-round-hooks.sh` | a later `spec-fidelity` round is handed the diff and routed to `spec-fidelity-verify`; refused first when the feature still carries the OLD value of something the change moved (`make stale-terms`) | `REVIEW_ROUND_OK`, `STALE_TERMS_OK` |
| `agent-model-hooks.sh` | an ad-hoc agent dispatch (no file under `.claude/agents/`) that names no `model` is refused, with the rule for choosing one | none - name the model |
| `record-edit-hooks.sh` | an Edit aimed at an assembled record page is re-aimed at the one fragment holding its text; refused where none or several hold it, and a Write always | none - the guard hands you the edit |
| `finished-run-hooks.sh` | a finished run is reported; a live `make` is not abandoned; a waiter on a dead producer is reported | - |
| `agent-stall-hooks.sh` | a stalled background agent is reported | - |
| `idle-tests-hooks.sh` | an idle session runs `make idle-tests` | - |
| at push, in `sync-with-main.sh` | `gate-stamp.py` (a green gate saw it), `review-gate.sh`, `plan-gate.sh`, `entry-gate.sh`, `check-file-scale.py`, `spec-lint.py`, `_hm_conflict.py --tracked`, `perf_review.py --check`, the open-task refusal | per script, each with a reason |
| the gate | the 100% floor, the 1,000-line bar, `_ratchet.py` (a target that gets slower fails), the perf bands, `test_agent_models.py` (the pinned tiers, and `omitClaudeMd` on every agent file but the one the test names) | `FILE_SIZE_OK` in the file |

Every escape states a reason of two words or more, and every firing is recorded (`make audit`,
`make guard-log GUARD=<name>`). A guard that can produce the compliant command produces it; a refusal
is for a destructive action or a decision only the session can supply. When you add one: match
invocations, not mentions; check the escape first; prove it fires by deleting it and watching a test
go red.

Deliberately NOT enforced, because a guard that fires on correct work teaches a session to bypass
every guard: the caste sense of "people", gender-neutral office-holders, the kanji triangle, and the
behavioral principles XII, XIV and XV.

## Key paths

- `.specify/memory/constitution.md` - the constitution; `.specify/templates/plan-template.md` - the
  Constitution Check gate.
- `.claude/skills/diagram/SKILL.md` - usage; `.claude/skills/diagram/CLAUDE.md` - the dev loop and the
  index over `dev/` (the draw order and the keep-clear contract are in `dev/placement.md`).
- `.claude/skills/diagram/migration-plan.md` - the standing plan for converting hand-authored maps to
  scripted generation; read it before drawing or scripting a settlement map, and update its status
  table when a conversion lands.
- `.claude/agents/` - the review and verification agents; `docs/review-ledger.md` - every review pass.
- `docs/` - the on-demand references: `session-clones.md`, `spec-kit-and-reviews.md`,
  `efficiency-tooling.md`, `guards.md`, `research-doctrine.md`, `iteration-loop.md`, `container.md`,
  `l7r-style.md`.
- `specs/NNN-*/` - the features. There is deliberately no single active-plan pointer; current status
  is the highest-numbered spec, its `tasks.md` and `git log`.

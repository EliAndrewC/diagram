# L7R Diagram - the settlement and building map generator

<!-- container-mounts: ..:/host-l7r-repo -->

This repository is the diagram project of the GM's L5R worldbuilding: building plans (Mode A) and settlement maps
(Mode B), deliberately one package (why one, and what would change it: `docs/package-boundary.md`). It was a Claude
Code skill (under `.claude/skills/`) until feature 329 moved it to the root: nothing invoked it as a skill any
more, and the prefix cost every pointer. What to read next:

| you are | read |
|---|---|
| drawing a map or a building plan | `docs/usage.md` (Mode A detail: `docs/buildings.md`) |
| changing the engine, a pool generator or a test | `l7r/diagram/CLAUDE.md` - the dev loop; it auto-loads under `l7r/diagram/`, `pool/` and `tests/` |
| writing or checking the research record | `research/CLAUDE.md` - it auto-loads under `research/` |

`docs/` is the repository's process; `dev/` is engine development and the append-only run records.

The GM's setting notes that the research cites live in gm-assistant, mounted at
`/host-l7r-repo/gm-assistant` (`setting/`, `cosmology/`, `campaigns/`; on GitHub at
<https://github.com/EliAndrewC/gm-assistant/tree/main/setting>), and in the `l7r` checkout's own
`/host-l7r-repo/setting/` (`budgets.md`; `make canon` searches both). The canonical campaign notes are
`/host-l7r-repo/setting/l7r.md`; nothing here edits them, and nothing here runs git against
`/host-l7r-repo`. The webapp, the content skills and Obsidian Portal are gm-assistant's; a session
here does none of that.

**A feature is REPOSITORY + number.** This repository's numbers continue from 132 (gm-assistant
restarts at 200); features 001-131 that concern the diagram live here.

## Core rules

### House style

Enforced by `scripts/hooks/house-style-hooks.sh`, which corrects the text rather than refusing the edit.

- Hyphens only: no em-dashes or en-dashes anywhere in the project.
- American spellings, never British ones, in everything - prose, docs, generated content, tests,
  comments and code identifiers.
- Both rules stop at a quotation: a passage quoted from another source, and the GM's own writing
  (`<!-- SOURCE: GM NOTES -->` blocks, `l7r.md`, `specs/*/request.md`), keep their own dashes and
  spellings.
- "People" has caste meaning: only samurai are "people". In demographic, statistical or analytical
  writing use humans / inhabitants / population / a caste term. `people` is fine for samurai and in
  narrative, lore, dialogue, vow and folktale voice. Full rule: `/host-l7r-repo/gm-assistant/docs/l7r-style.md` (gm-assistant's, the one copy).
- "Domain", never "demesne"; silently fix it in any text you edit.
- Gender-neutral office-holders: they / their / them for a generic daimyo, governor, magistrate,
  minister or samurai; named characters keep their own pronouns.
- Kanji in generated content passes the kanji - romaji - meaning triangle (constitution XI): real
  characters, a plausible reading, a meaning that maps back.
- Never invent setting details that contradict the GM's notes.

### Research

Constitution XII. The full record with the GM's rulings is `docs/research-doctrine.md`; the
operative form of the citation rules (the footnote shape, the notes and the works cited) is `research/CLAUDE.md`, which
auto-loads when a session edits the record; the archive and the download list are `research/downloads.md`.

- A question about how a place was built, farmed, planted or lived in is a RESEARCH question. Run
  the search pass before deciding, before asking the GM, and before writing "guess". The GM is asked
  only when the record is silent or contradictory, and the ask says what was searched and found.
- The search pass looks in the ARCHIVE before the web (feature 309): `make archive-inbox` first (the GM's downloads in
  `academic-sources/` archived, then removed - what is left there is unprocessed), then `make archive-find` for each
  source. Every cited page is archived in the PRIVATE repository `EliAndrewC/diagram-research`; never
  link or copy it anywhere public.
- Geography resolves China first, Japan as tiebreaker, and the GM's canon overrides both (`docs/research-doctrine.md`).
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
  canon, not evidence, and need no citation. A source only the GM can fetch is appended to the canonical
  download list `research/to-download.md` with `make download-add FILE=<draft>` (feature 313); the GM's
  `academic-sources/TO-DOWNLOAD.md` is their marked copy, written only by `make downloads-sync`.
- The record is HTML under `research/`, each heading the question a reader would ask from the map,
  each entry written for a casual reader: glossary tooltips for terms, session notes in HTML
  comments, nothing about what the entry used to say. A modal's explanation is written from a research
  section its `Entry:` names. It is written PER ENTRY and BUILT into the site a reader opens
  (features 258, 301, 303): a question is one stem in one flat directory, `research/questions/NNNN-<heading id>.html`
  with how our maps draw it beside it as `.drawing.html`, each page's footnotes in the `.notes.html` beside it; a
  source is `research/sources/NNNN-<key>.html`, tagged (period of its evidence, region, kind) from `research/source-tags.json`
  and grouped by `research/source-sections.json` (feature 305). Each question carries TAGS (subjects - the first primary - settings,
  one level) from `research/tags.json`, and `research/contents.json` declares the sections, their order and the tag
  rule each takes: a question lives in the first section that takes it, ordered by level then number, so regrouping
  is an edit to `contents.json` alone. `make record` builds `research/site/` - a page per question with its notes
  numbered from 1 at its foot, a page per section of each half and per tag, and the whole record on one page
  (`all.html`) - never committed, built on main by render-sync. A POINTER to the research - a code comment, a doc, a
  spec, an `Entry:` - names the FILE (`research/questions/NNNN-<heading id>.html`, or
  `research/contents.json#<section>` for a whole section), never a built page; `scripts/gates/check-research-pointers.py`
  holds it at the gate and the push, and `make fragment-move FROM= TO=` renames a question with every pointer to it.
  Find a question with a glob on its heading id or a grep over `research/questions/` - there is no index - and never
  edit a built page; footnote numbers are allocated at build and are typed nowhere.
- Reading and checking are dispatched to agents, in the background: `source-reader` (read what you
  cite), `quote-check`, `record-format`, `source-applicability` (judged BEFORE a source's numbers
  reach a map or a rule), `entry-drift`. What is mechanical runs FIRST, as a script, and its output goes
  in the agent's prompt: `make source-pages OUT=<dir> URL=<u>` before `source-reader` (the page itself, saved
  to grep, where a fetch gives an extract), `make quote-verbatim Q=<NNNN> [NOTES=<ids>]` before `quote-check` (is the
  passage on the page, character for character), `make record-prepass Q=<NNNN>` (or `IN=<section>`) before
  `record-format`, `make size-table PLAN=<svg>` before `size-audit`. `make source-pages` also prints each page's
  earlier reads from the sources-consulted ledger and saves it once in the host's page cache; record every page's
  outcome with `make source-outcome` (feature 288).
- A record check reads a BUNDLE: `make check-bundle Q=<NNNN>` (or `KEY=<k>`) copies what it
  needs, prepass output included, OUT of the repository, and the dispatch names its `MANIFEST.md` - an
  agent reading a file here is handed every `CLAUDE.md` above it, ~28,000 tokens (feature 250). The agent's
  reply is compact: counts first, then only what to act on. A research page is worked in two fresh sessions, write then
  check-and-apply, from briefs (`make page-session BRIEF="<1> <2>"`); `make notes` prints only the notes you name.
  A write session takes at most four questions and ten new registry keys (feature 274: its cost grows with the square
  of its length); the runner refuses a larger brief unless it declares `<!-- page-load: kind=check|assertions|split|handover -->`,
  and `make reserve`'s eleventh key sends the rest to a continuation brief. Coordination files are read by line
  (`make lines`) and written without reading (`make append`); a page session loads `scripts/container/page-session-rules.md`
  in place of this file.

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
- Open work lives in `specs/` only (feature 330: the old backlog directory became features). Defer work by filing a
  feature - `make claim`, then a `spec.md` whose `**Status**: Filed` says what it is - and ask `make speckit-todo` what
  is open: filed, planned, in progress, each grouped by its spec's `**Owed at**:` stage (`now`, `village`, `town`,
  `provincial city`, `capital`: the earliest not-yet-scripted tier it concerns, code included; `make speckit-todo CHECK=1` holds it). A feature closes when every task is ticked, or when its status line opens
  `Done`, `Superseded by NNN` or `Withdrawn` with the evidence beside it.
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
  (`scripts/gates/review-gate.sh` refuses the push otherwise): up to five rounds on the initial acceptance,
  then stop and escalate; an amendment after acceptance resets the counter. A plan's decisions are
  reviewed by the same agent before a task is ticked (`make tick`, `scripts/gates/plan-gate.sh`). A later
  round is handed the previous verdict and the diff by `scripts/hooks/review-round-hooks.sh`.
- No known regressions (constitution XIII). A regression is measured, never remembered: the baseline
  is taken in a detached worktree (`git worktree add --detach /tmp/base HEAD`, never a stash) and
  each failure is checked against the clone, because a worktree carries no gitignored artifacts.
  A pre-existing failure does not block a push, but one you find is fixed in the work at hand
  (XIV; GM 2026-10-01: "We should definitely fix the pre-existing failure"). Three exits: fix it,
  revert it with a written impossibility investigation, or an explicit GM waiver; fixing is the
  expected one. A regressed state stays in the clone, unpushed.
- Fix defects where you find them (constitution XIV), in the same work with the same verification.
  The only deferrable fix is a complete overhaul, and deferring one delivers the measurement, the
  mechanism and a sketch. Record a fix that FAILED at the point of change.
- Review checks (`glyph-check`, `settlement-review`, `fix-check`, `building-review`, `size-audit`) run ON
  THEIR OCCASION (feature 294): an element new to a map, a glyph redrawn or re-placed, a map or sheet new to the
  pool, or an occasion the feature declares in its `tasks.md` `## Occasions` - never because a manifest moved
  (`review_owed.py`; `docs/reviews.md` has the table). One unit per agent, on a green gate,
  two rounds at most; every pass is a row of the ledger's measured table with its cost (`make review-cost`). To improve one, add
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
  `scripts/container/append-system-prompt.md`; if one is skipped, check `type claude` first.

## Verification and iteration

The machinery in one picture, with the GM's rulings and the measurements: `docs/efficiency-tooling.md`.

- Everything runs through `make`; the hooks refuse or rewrite anything else. The ladder in the skill:
  `make quick` while iterating (testmon selects by change; `ALL=1` runs every quick test), `make done`
  once at the end (the whole gate: lint, the static checks, the pool roll, 100% coverage over the
  whole engine), `make done FULL=1` (prompts; adds the perf bookends). What each costs is asked of
  the record (`make audit`, `scripts/measure/gatecost.py <target>`), never written here.
- `make done` reports every failure together: fix them all, re-run once. Background the final gate
  and act on its notification; never poll.
- Python: ruff, ruff format, pyrefly, and 100% coverage owed by everything the day it lands, held as a
  floor on the gate (never `fail_under` in `pyproject.toml`). An inner function that is hard to test
  is lifted to module level and tested with plain inputs; dropping the test is not an option. A
  Python file past 1,000 raw lines fails the gate.
- An overlap check against the features already on the map builds an index once
  (`settlement/_geom/indexes.py`) and asks it per candidate; a plan that adds one says how it is
  indexed.
- Edit with `Edit`, not heredoc'd Python; a mechanical sweep uses `scripts/patch.py`.
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
| `download-copy-hooks.sh` | a write to the GM's copy of the download list (`academic-sources/TO-DOWNLOAD.md`) is refused with `make download-add` / `make downloads-sync` (feature 313) | `DOWNLOAD_COPY_OK` |
| `house-style-hooks.sh` + `check-house-style-delta.py` | corrects dashes and spellings in Edit, Write and Bash payloads; `make quick` fails on one in the delta | - |
| `make-only-hooks.sh` | refuses a bare interpreter or pytest; rewrites a targeted pytest to `make test-file` | - |
| `guard-file-hooks.sh` | a guard-file edit carries `GUARD_EDIT_OK` and a reason; a Makefile recipe comment must not run | - |
| `clone-sync-hooks.sh` | forbidden names, name-routing, a live claim, a stale clean HEAD (synced in), a stray mirror commit | - |
| `main-tree-hooks.sh` | a write that would land in the mirror is moved to the clone; one naming it is refused | `MAIN_TREE_OK` |
| `discard-hooks.sh` | a checkout or restore that would discard uncommitted work | `DISCARD_OK` |
| `conflict-marker-hooks.sh` | a `git add` or commit that would stage conflict markers | `CONFLICT_MARKERS_OK` |
| `ledger-hooks.sh` | a commit staging the review ledger with a measured row short of its check, class or cost | `LEDGER_LINT_OK` |
| `shell-check-hooks.sh` | a command that does not parse, an executing backtick, a `-m` with a quote or newline, a foreign co-author | `SHELL_CHECK_OK` |
| `no-branch-hooks.sh` | no local branches. The remote-only `backup/<clone-name>` branches on GitHub are not local branches: `sync-with-main.sh` pushes the clone's HEAD there (fast-forward, never forced) at every `done`/`push`, landed or refused, and deletes each once `main` contains it - its own at landing, any other by the sweep at the same step (feature 321) | `NO_BRANCH_OK` |
| `no-poll-hooks.sh` | no busy-wait; corrects a self-matching `pgrep`, and scopes a wait on a make run to this tree (`own-make.sh`); refuses a pattern that matches its own command (launch-and-wait); a file-watching loop is backgrounded and given a proof of life; every wait loop gets a 90-minute ceiling (WAIT TIMED OUT, exit 4); a backgrounded periodic report is refused with its exact `CronCreate` call | `POLL_OK`, `CRON_OK` |
| `batching-hooks.sh` | blocks a run of single-call recon turns, warning on every loaded turn before it | - |
| `measure-hooks.sh` | a second expensive run with nothing changed between; a full gate within 3 h of a GREEN one, once, edits and commits notwithstanding (batch the gate; quick tests between); a `make perf` outside a pair's legs is reminded of `make cohort HOUSEHOLDS=` (untimed) | `MEASURE_OK` |
| `gate-hooks.sh` | no `-k` subset as the only run before the gate | `GATE_OK` |
| `pair-hooks.sh` + `review_owed.py` | the review checks a delta owes (its occasions) dispatched on a green gate, one unit per agent, two rounds per unit | `PAIR_OK`, `REVIEW_ROUNDS_OK` |
| `escalation-hooks.sh` | a review dispatch arms, an `escalation-check` dispatch disarms, before the turn ends | `ESCALATION_OK` |
| `wakeup-hooks.sh` | a `ScheduleWakeup` outside a live `/loop` is refused (background work wakes a session by itself; a reminder the GM asks for is `CronCreate`); a turn cannot end with a stale wakeup pending, and the block names the `CronDelete` | none - cancel the wakeup |
| `review-round-hooks.sh` | a later `spec-fidelity` round is handed the diff and routed to `spec-fidelity-verify`; refused first when the feature still carries the OLD value of something the change moved (`make stale-terms`) | `REVIEW_ROUND_OK`, `STALE_TERMS_OK` |
| `agent-model-hooks.sh` | an ad-hoc agent dispatch (no file under `.claude/agents/`) that names no `model` is refused, with the rule for choosing one | none - name the model |
| `check-bundle-hooks.sh` | a record check (`quote-check`, `record-format`, `source-applicability`, `source-reader`, `entry-drift`, `intro-check`, ...) dispatched into the repository instead of at a bundle is refused, with the `make check-bundle` command; and one its bundle's MANIFEST does not owe (feature 311: a check runs only where the words it reads changed, `make record-owed`) | `CHECK_BUNDLE_OK`, `CHECK_NOT_OWED_OK` |
| `canon-read-hooks.sh` | a direct read of the GM's setting canon (grep, sed, cat, Read, Grep on `setting/`) is refused with `make canon TERMS="a\|b\|c"`, which answers every term at once; a second `make canon` within three tool calls is refused unless it folds the earlier terms | `CANON_OK` |
| `new-file-hooks.sh` | a new glossary file or registry entry written without a reserved prefix is refused with `make reserve KIND=glossary\|registry KEY=<k>`, which allocates under a host-wide lock so parallel queues never collide | `RESERVE_OK` |
| `claims-gate.sh` (push) + `test_claims_coverage.py` (gate) | every unit of the hamlet's code and the Mode A procedures carries a `Research:` claim; a claim owed an `impl-drift` check, or a finding the delta introduced, is refused at the push; a pre-existing finding warns (feature 316: `make claims-owed`, `claims-bundle`, `claims-checked`, `claims-report`; a page edit re-owes only the claims resting on the blocks it changed, the rest go through one `make claims-triage` - feature 318) | `CLAIMS_OK` |
| `record-edit-hooks.sh` | an Edit aimed at a built record page (the site's, or an old assembled page) is re-aimed at the one fragment holding its text; refused where none or several hold it, and a Write always | none - the guard hands you the edit |
| `~/.claude/hooks/missing-program-hook.sh` (USER-LEVEL, every project) | in a container, a Bash command that finds a program missing - `command not found`, an empty `which` / `command -v` / `type` / `hash` / `whereis`, a `dpkg` / `apt` / `pip` miss, a missing module - adds a note that the container has passwordless sudo to install it; silent on the host. Self-test beside it, run by `make hooks-test` | - |
| `finished-run-hooks.sh` | a finished run is reported; a live `make` is not abandoned; a waiter on a dead producer is reported - each only for the session's own working tree | - |
| `agent-stall-hooks.sh` | a stalled background agent is reported | - |
| `stall-watchdog-hooks.sh` | one loop outside every session: a session silent an hour with unfinished work, not waiting on the GM, gets its tab marked and the bell, and a nudge typed when its own input line is empty (once per stall); a paneless one is marked on its host's tab, never nudged | - |
| `idle-tests-hooks.sh` | an idle session runs `make idle-tests` | - |
| at push, in `sync-with-main.sh` | `gate-stamp.py` (a green gate saw it), `review-gate.sh`, `plan-gate.sh`, `entry-gate.sh` (the record gate: every record check a delta owes answered, feature 311), `claims-gate.sh` (feature 316), `check-file-scale.py`, `spec-lint.py` (a spec directory that existed before the push is judged on what the push adds), `check-research-pointers.py`, `downloads.py check` (the download list append-only), `make record CHECK=1` (the record builds cleanly), `hm_conflict.py --tracked`, `perf_review.py --check`, the open-task refusal; at push and sync-in, a clone whose history shares no commit with main's | per script, each with a reason |
| the gate | the 100% floor, the 1,000-line bar, `ratchet.py` (a target that gets slower fails), the perf bands, `test_agent_models.py` (the pinned tiers, and `omitClaudeMd` on every agent file but the one the test names) | `FILE_SIZE_OK` in the file |

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
- `docs/usage.md` - usage; `l7r/diagram/CLAUDE.md` - the dev loop and the index over `dev/` (the draw order and the
  keep-clear contract are in `dev/placement.md`).
- `docs/migration-plan.md` - the standing plan for converting hand-authored maps to
  scripted generation; read it before drawing or scripting a settlement map, and update its status
  table when a conversion lands.
- `.claude/agents/` - the review and verification agents; `dev/review-ledger.md` - every review pass.
- `docs/` - the on-demand references: `session-clones.md`, `spec-kit-and-reviews.md`,
  `efficiency-tooling.md`, `guards.md`, `research-doctrine.md`, `iteration-loop.md`, `container.md`. The L7R style
  guide is gm-assistant's `docs/l7r-style.md`, its one copy.
- `specs/NNN-*/` - the features. There is deliberately no single active-plan pointer; current status
  is the highest-numbered spec, its `tasks.md` and `git log`. A path in a spec before 329 that starts with
  the old skill directory (`.claude/skills/` + the project's name) now drops that prefix (the specs are history and keep their words); the Markdown that
  feature 329 moved or retired is listed in `specs/329-unskill-the-repo/audit.md`.

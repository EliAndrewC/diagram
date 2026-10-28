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

Constitution XII. One line each here; the full text of every rule, with its feature and the GM's words, is
`docs/research-doctrine.md` ("The research rules of the root CLAUDE.md, in full"); the citation rules' operative form is
`research/CLAUDE.md`, which auto-loads under `research/`.

- A question about how a place was built, farmed, planted or lived in is a RESEARCH question: run the search pass (the
  `research-pass` agent runs one) before deciding, before asking the GM, and before writing "guess".
- Whether a finding APPLIES to a case, form or map is the record's and the reviewers' to rule, never the GM's; where the record is
  silent on a choice, take a knob or the algorithmically easier route and say which (GM 2026-10-25; `escalation-check` tests 4-5).
- A `GUESS`, `UNRESEARCHED` or `CONVENTION` value, and a number no claim states, is a goal and a knob, never a target to defend:
  `make tunables` (GM 2026-10-25, feature 417 T28).
- The ARCHIVE before the web: `make archive-inbox`, then `make archive-find`. Every cited page is archived in the PRIVATE
  `EliAndrewC/diagram-research`; never link or copy it anywhere public.
- Geography resolves China first, Japan as tiebreaker; the GM's canon overrides both.
- Several attested forms are a KNOB rolled from the map's seed, never a choice.
- **Room before packing** (GM 2026-10-12): when features will not fit, more room first; an unresearched number is a knob to
  move, never a target to defend.
- Every rendering decision is labeled - historically accurate, deliberate deviation, map drawing convention, guess - in
  `research/`, the operative doc, the point of change and the spec. An unlabeled guess is the one failure.
- Record the why of every research-driven rule and magic number beside the rule. Record a decision to ACCEPT a limitation
  with what it costs, the alternatives that were priced, and who chose.
- A citation quotes the passage verbatim from a public page, English translation marked as one; an unreadable source is not
  cited. A source only the GM can fetch goes on `research/to-download.md` with `make download-add`.
- The record is HTML fragments under `research/questions/` and `research/sources/`, BUILT by `make record`; a pointer names
  the fragment FILE, never a built page.
- Reading and checking go to agents, in the background, on a BUNDLE (`make check-bundle`), the mechanical script first.
- A research page is worked in two fresh sessions, write then check-and-apply (`make page-session`), at most four questions
  and ten new registry keys a write (`make reserve`'s eleventh key sends the rest to a continuation brief); coordination files
  are read with `make lines` and written with `make append`; a page session loads `scripts/container/page-session-rules.md`.
- A `research record` feature closes only with its findings checked against the code (`make impl-check F=<n>`).
- **The claims switch is at `report`** (feature 445, the GM 2026-10-28): a claims finding refuses no landing and files no task while
  it is checked and listed by `make claims-report`; only an owed claim or a form problem refuses. `make claims-clean REASON=` throws
  it to the long-run rule - no landing while the report lists an open finding - when the claims feature after the rewrite closes.

## Development workflow

Spec-driven under `.specify/memory/constitution.md`. One line each here; the full text, with the GM's rulings, is
`docs/spec-kit-and-reviews.md` ("The development workflow of the root CLAUDE.md, in full").

- Feature work is a spec-kit feature (`/speckit-specify` -> plan -> tasks -> implement); a tweak is done directly. Ask before
  chain-firing on an ambiguous case.
- A number comes from `make claim SLUG=<slug>`; export both lines it prints; commit and push the spec directory as soon as
  `spec.md` exists; no branches - commit on `main` in the clone.
- **A feature is filed only with the GM's approval** (GM 2026-10-10), proposed in the turn's FINAL message; its `spec.md`
  carries `**Approved**: the GM, YYYY-MM-DD, "<their words, verbatim>"`. A feature the GM asked to be filed - including a
  money research request gm-assistant opens for him - is approved by asking; file it without an approval round, its
  `**Approved**:` line quoting *"you should treat features that I have asked to be filed as automatic approval, and
  therefore you should not ask in the future"* (GM 2026-10-18). `make speckit-todo` lists what is open. Each spec carries an `**Affects**:` line; its stage is derived from it
  (`make speckit-todo BY=affects`, `CHECK=1` at the push). An item owed at a tier goes into that tier's placeholder (380 village,
  381 town, 382 provincial city), never filed alone. A feature closes when every task is ticked, or when its status line opens
  `Done`, `Superseded by NNN` or `Withdrawn` with the evidence beside it.
- A question a measurement answers, before any decision to build, is a TRIAL (`make trial SLUG=`): measured first, reviewed
  once when Done, no engine code on net while it runs (`docs/spec-kit-and-reviews.md`, "The trial form", feature 438).
- Every task is `research: rendering` or `research: physical` (the physical one carries its five boxes).
- A feature ends with `make feature-report F=NNN WRITE=1`; a row the GM agreed in the session is
  `make gm-reviewed F=NNN WORDS="<his words>"`.
- Decide first, then check: a task's decisions carry a verdict before its checks run (`make decide`). The TRIPWIRES -
  a check's third round on one subject, a block an earlier version had and a later dropped coming back,
  a second red gate in a row, check dispatches past 1.0 a changed line - each owe the `round-arbiter`'s ruling
  (`make arbiter-bundle`) before the next check or gate. A ruling stays in the arbiter's log; the ONE door to the GM is a
  `for_gm` question, owed escalation-check until `make gm-escalated` keeps or cuts it (feature 432). `make gm-review` lists his
  kept questions first.
- Run the chain end to end, unattended: stop only when a wrong guess would cost an hour-plus to unwind or the thing genuinely cannot be done; when stuck, the next
  step is a measurement. A PROCESS stop goes to the round arbiter (`make arbiter-ask`), what to build to the GM.
- Do the literal thing (constitution XVI); an exception goes to `spec-fidelity` with the GM's words.
- A spec and a plan's changed blocks are reviewed by `spec-fidelity` (`make plan-delta F=<n>`) before implementation and ticks.
- No known regressions (XIII), measured in a detached worktree; fix defects where you find them (XIV).
- Review checks run ON THEIR OCCASION (`docs/reviews.md`), one unit per agent; every pass is a ledger row with its cost
  (`make review-cost`); findings for the GM go through `escalation-check` first; to improve a check, add the general rule,
  prove it fires on the unfixed artifact, then fix the artifact. Each runs on the tier its file pins; an ad-hoc
  agent names its `model` (`sonnet` to read, fetch, translate or extract; `opus` for anything that judges). A defined agent launches without the CLAUDE.md files (`omitClaudeMd: true`); **what every
  dispatch of a check shares lives in its agent file** - only that is reused across launches (feature 383 research R16) -
  and a wave of 4 or more of one type runs as ONE `Workflow` call, `check-wave`, which wakes the session once and puts each unit
  through the Agent guards (feature 383 amendment 7; `agent-prefix-hooks.sh`, `workflow-hooks.sh`). The review agents, and
  Workflow for those waves, are pre-authorized through `scripts/container/append-system-prompt.md`.

## Verification and iteration

One line each here; the full text is `docs/efficiency-tooling.md` ("Verification and iteration, from the root CLAUDE.md, in
full").

- Everything runs through `make`: `make quick` while iterating, `make done` once at the end, backgrounded, never polled.
- `make done` reports every failure together: fix them all, re-run once.
- **Speed work may ALWAYS change maps** (the GM, 2026-10-18: *"anytime we are trying to make things faster, it's always okay
  for maps to change, so long as the changes don't violate our research findings"*): hold it to the rules and the research
  claims rather than to identical output.
- Python: ruff, ruff format, pyrefly, 100% coverage held as a floor; a Python file past 1,000 raw lines fails the gate - split it into a package of ~650-line submodules whose `__init__.py`
  re-exports every name, never trim it to just under (405 T53).
- Edit with `Edit`; a large file through its make target; batch the lookups you already know you need.
- An overlap check builds an index once (`settlement/_geom/indexes.py`) and asks it per candidate; a plan that adds one says
  how it is indexed.
- Foreground-regenerate only the motivating map; read derived data from the recorded manifest, never by re-running the
  generator.

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
  when `remote` is on and main moved on engine paths. **`make land F= T=<task(s)> NOTE=` lands a task and ticks it**: every
  cheap refusal first and together, then `make done` and `make cohort-landing` only where needed (side by side, 405 T48) with the claims round beside them, the
  tick and ONE push carrying both (405 T50, T51).
  Only the task being worked (`make task-start`) holds a landing; a task nobody has started holds nothing. A feature's TOOLING
  also lands alone: `make land-tooling FILES="<paths>"` lands the named `scripts/`,
  `tests/`, agent-instruction, Makefile or settings files as a new commit on main, so a guard fix made mid-feature reaches
  every session's hooks (feature 379; an arbiter's fix is not done until it has).
- Never rewrite history (no rebase, squash, amend or force push); never commit or push against
  `/host-l7r-repo`. `git -C <path>` for every git call, one tree per command, no bare `cd`.
- A paid prompt (`make ci-image`, any `FULL=1` dispatch) may be answered by the session; the logged
  reason says so and quotes the GM's 2026-08-25 authorization.

## What is enforced

Every guard has a test companion that `make hooks-test` runs, and its message names the compliant command. The table of
every guard - what it does, its escape - is `docs/guards.md` ("The guard table of the root CLAUDE.md, in full"), with the
rule, the measurement and the ruling behind each.

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
  `efficiency-tooling.md`, `guards.md`, `gm-rulings.md` (his words no spec records), `research-doctrine.md`, `iteration-loop.md`, `container.md`. The L7R style
  guide is gm-assistant's `docs/l7r-style.md`, its one copy.
- `specs/NNN-*/` - the features. There is deliberately no single active-plan pointer; current status
  is the highest-numbered spec, its `tasks.md` and `git log`. A path in a spec before 329 that starts with
  the old skill directory (`.claude/skills/` + the project's name) now drops that prefix (the specs are history and keep their words); the Markdown that
  feature 329 moved or retired is listed in `specs/329-unskill-the-repo/audit.md`.

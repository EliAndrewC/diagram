# Implementation Plan: an efficient process, enforced and measured by the tooling (feature 375)

**Spec**: `spec.md` | **Request**: `request.md` | **Model**: feature 311's plan (owing logic, an answer record, a guard per
rule, a replay over history) and 318's claims triage (one cheap agent over the changed blocks).

## Summary

Fourteen requirements in three groups, each enforced where it can bite: the **owing logic** (FR-001, FR-002, FR-006), the
**guards** at dispatch, edit and stop (FR-003, FR-007, FR-010), the **gates** at tick, gate and push (FR-004, FR-005, FR-009,
FR-012, FR-014), and one new defined agent (FR-011). The measurement (FR-008, FR-009) comes first: every later task is then
measured by it, and 375's own report is its first real use.

Everything here is tooling, so every task is `research: rendering`. One engine module changes: `l7r/diagram/tools/claims.py`
(FR-002's claim text), which makes the landing GATED and owes 100% coverage on it.

## Technical Context

Python 3 scripts under `scripts/` (stdlib only, as today) and bash guards under `scripts/hooks/`, each with a suite in
`tests/hooks/` run by `make hooks-test`; Python tooling tests under `tests/tooling/` and `tests/hooks/`. State that belongs to
one clone lives in its git dir (as `review-rounds.json`, `record-checks/` do); state that must outlive a clone or be read by
the GM is committed under the feature's directory.

**A hard limit of this session**: the guards run from `/diagram/scripts/hooks/` (the mirror) and agents load from the mirror's
`.claude/agents/`, so nothing built here fires in this session until it lands. Every proof is a hooks-test fixture or a
replay over recorded history (SC-001, SC-006), never "seen firing"; and 375's own report (FR-009) is built from the
transcript backfill (D8), not from hook events.

## Performance bookends

N/A - no generator change; `tools/claims.py` is read by the claims gate, not by generation.

## Constitution Check

- I, II, III, IV, V: N/A - no UI, no pool content, no SOURCE blocks.
- VI (performance): N/A for maps. The per-call hook cost is measured instead (D7): the event-log hook adds one process to
  every tool call; its median is measured and recorded (`m:event-hook-cost`), and a cost past the slowest existing per-call
  guard's is a finding of this feature.
- X (coverage): 100% on `tools/claims.py` as changed; the scripts are tested to the project's habit (every branch a guard
  takes has a suite case).
- XII (research): N/A - no physical decision.
- XIII (no known regressions): baseline `make done` and `make hooks-test` in a detached worktree before the first engine edit.
- XIV (fix where found): FR-005(a)'s parser case is located before it is fixed (D5).
- XVI (the literal thing): every FR built as written; where a mechanism had to be chosen, it is a decision below.

## Decisions

**D1 - FR-001: a modal triage, the claims triage's shape.** A modal unit owed ONLY because a page its `Drawing:` or `Entry:`
names moved (the modal's own words unchanged) is owed a TRIAGE, not the check. `make modal-triage` writes one bundle: per
moved page, its blocks new, changed or removed since the unit was last answered, and each kind naming that page with its
About and Depiction. One ad-hoc agent (model opus) replies `TOUCHES <uid> - <block>` per kind a change bears on;
`make modal-triaged BUNDLE= REPLY=` owes the named units in full and answers every other at its current fingerprint, result
`triage: untouched` - "cleared on the record". The "before" of a page is the blob recorded with the unit's last answer
(`git hash-object -w` at answer time, so an uncommitted state is kept), else the merge base. The units owed by the modal's
own words are unchanged.

**D2 - FR-002: a procedure claim is owed by its own line; the rest of its section by a triage.** The claim markers do not
sit beside their rule text: in both procedure documents they stand in a cluster at the head of each section (counted
2026-10-10 by grep: 174 markers in `docs/buildings.md`, 106 in `docs/building-programs.md`, e.g. lines 17-62 of the latter
all markers), so "the rule text it sits beside" cannot be found by position. So in `tools/claims.py` a section claim's code
fingerprint becomes its own normalized line alone, and the section's text becomes a second fingerprint (`section`) on its
index row, with the section's block digests kept in the snapshot store (`dev/claims-pages.json`, as 318 keeps a page's).
Own line changed: owed `impl-drift` in full. Section text changed elsewhere: owed a TRIAGE, folded into `make claims-triage`,
whose bundle shows the section's blocks new, changed or removed (a table row is a block, so a regenerated
`building-programs.md` shows only the rows whose text changed) and sends on only the claims a change bears on. The old
blocks' words come from the document's history, as `removed_words` does for pages. **Migration**: changing the fingerprint
would read every section claim "code changed"; a one-time `claims.py backfill-sections` rewrites `code` and adds `section`
for every row not owed under the old scheme (an owed row stays owed), so the change owes nothing by itself. Code units
(functions, constants) keep their fingerprint: it is already per unit.

**D3 - FR-003(a): the task is named, its decisions reviewed first.** The active task is `.git/active-task` (set by
`make task-start F= T=`, defaulting to the first open task of `.specify/feature.json`'s feature). A check dispatch
(`check-bundle-hooks.sh` for the record checks and impl-drift, `pair-hooks.sh` for the review checks) is refused unless
`plan-review.json` carries a CLEAR verdict current under D6 that covers that task: a `## <task id>` section of `plan.md` ruled
by a per-task decision preflight (`make decide F= T=` builds a bundle of that section, the request and the spec;
`spec-fidelity` in its plan-review mode, D19, records `tasks.<id>` in `plan-review.json`), or, where the plan has no
section for the task, the plan-stage verdict. Escape `DECIDE_OK="<reason>"`.

**D4 - FR-003(b)(c): check state from the hook events.** `.git/checks-open.json` holds every record, claims and modal check
dispatched: its subject (a question number or a modal uid, from the MANIFEST's `unit:` lines - an impl-drift or claims-triage dispatch is
counted for D10 and D11 but has no frozen subject, below), and its state. PreToolUse(Agent) opens it; PostToolUse(Agent) pairs `tool_use_id` with the launched `agentId`; SubagentStop (or a
foreground PostToolUse) marks it returned; `make record-checked`, `claims-checked`, `modal-triaged` close it. A subject's
ROUND is open from its first dispatch until every check in it has returned. While a round is open: an Edit or Write to the
subject's files (`research/questions/NNNN-*`, the modal's `.md` file) is refused (`record-edit-hooks.sh`), and a dispatch of a
check already in the round is refused (`check-bundle-hooks.sh`). Once all have returned the apply pass opens; the next
dispatch opens the next round. **Returned** is the first of: SubagentStop for its agent id (it fires for a background agent: `m:subagent-stop-probe`), a foreground PostToolUse, or the
check's answer (`make record-checked` / `claims-checked` / `modal-triaged`) - so a missing hook event never deadlocks a
subject. A check silent past the no-poll guard's 90-minute wait ceiling is reported stale by `agent-stall-hooks.sh` and can be
closed with `make check-closed SUBJECT= REASON=`. Escape `FREEZE_OK`.
**What the apply pass admits: the checks' own EDIT blocks.** A check's proposals are already machine-readable: seven
contracts (quote-check, record-format, entry-drift, source-applicability and the three modal checks) end each finding they
can word with an `EDIT <path> <<< old === new >>>` block, which `make apply-edits` applies. At SubagentStop the hook reads
the returned agent's last reply (`agent_transcript_path`) and keeps its EDIT blocks on the subject's round. In the apply
pass `make apply-edits` on a reply of this round is admitted (`record-edit-hooks.sh` gains a Bash matcher for it), and a
hand Edit to the subject is admitted only when its `old_string` lies inside the old text of one of the round's EDIT blocks
AND its `new_string` lies inside that block's new text (the session applying a block `apply-edits` refused, or a part of
one - never a different replacement at a proposed place); any other Edit to the subject is refused, naming
the round's blocks. The three page checks that write no EDIT blocks today - intro-check, record-style and
translation-check - are given them in their contracts (a task of batch 3), so every check that proposes words on a frozen
subject proposes them as blocks. impl-drift's subject is a claim in code or a procedure section, never a frozen page or
modal, so the freeze does not reach it (its findings are recorded by `make claims-checked`).

**D5 - FR-005(a): located - the parser was not the defect.** Today's parser already reads only lines that open with
`TOUCHES ` (`record_triage`'s anchored pattern), and the test pins that, with a mid-line `TOUCHES` and a prose mention ignored.
372's wave 108 record shows what happened instead (its transcript, 2026-10-10 14:19 UTC): a bullet drafted on 0105's drawing
page and withdrawn before any commit left the page back at its old words, the triage reply named no claim, and
`claims-triaged` reported "3 of 3 sent on" - the three were `forced`, because the withdrawn block's words were in no version
of the page's history and `removed_words` could not show them. The fix (XIV, a defect found in the work): every snapshot's
page text is kept as a git blob in the clone (`keep_texts`, `<git dir>/claims-page-blobs.json`) and read first, so a removed
block is shown even when it never reached a commit; and `claims-triaged` reports the claims a reply named apart from those
owed in full, so the count says which.

**D6 - FR-005(b): a decision edit is any edit that is not a typo.** `plan-review.json` keeps the reviewed plan's text
(`plan_text`, beside its hash). A plan whose hash differs keeps its verdict only when its word-level diff from that text is
typo-scale: whitespace, re-wrapping and punctuation, and single-word replacements within edit distance two, neither word
holding a digit, a number word or ordinal (`one`-`twenty`, `hundred`, `thousand`, `first`-`tenth`, `half`, `twice`) or a
negation (`not`, `no`, `never`, `except`, `unless`, `only`). The cost, accepted with FR-005(b)'s wording: a plain rewording
voids the verdict and owes a re-review. Any added or removed word, number or
negation voids it - the conservative side, since a missed decision is the incident the plan gate exists for. A
D3 task section is judged the same way against its own preflight text.

**D7 - FR-008: the event log.** One hook, `event-log-hooks.sh`, on PreToolUse, PostToolUse, SubagentStart, SubagentStop,
UserPromptSubmit and Stop, matcher-less, appends one JSON line to `<git common dir>/l7r-events/<feature>.jsonl`: UTC time,
session, event, tool, `tool_use_id`, category (D9's table); for a Bash call its make target; for an Edit or Write its path
and the digests of `old_string` and `new_string` (D10's reversal wire); for an agent its type, id, the MANIFEST its prompt
names (D11's cascade chain) and, at stop, its duration. The
feature is `.specify/feature.json`'s. It never blocks and never prints. The gap from a PostToolUse to the next PreToolUse is
the model's time. A clone's git dir outlives its sessions and compactions; `make feature-report` reads every clone's log for
the feature, so a spec written in one clone and built in another is one report.

**D8 - FR-009: the report, from four sources.** `make feature-report F=NNN` (`scripts/measure/feature_report.py`) writes
`specs/NNN/report.md`: wall time by category (thinking, editing, quick tests, test files, gates, waiting on each subagent
type, spec-kit steps), dispatches, rounds per checked thing, red gates and BLOCKED reviews, tasks and rows closed, and the
cascade ratio (check dispatches per line of the feature's own diff, `git diff --numstat` over its commits). Sources: the
event log; `dev/run-log/` (gates); the review ledger and plan-review history (BLOCKED); the record-check answers
(`<git dir>/record-checks/`, each clone's, for the checks answered and their results); the commits whose message names the
feature. Where the event log is missing (any feature before this one, and 375 itself) a session transcript fills it:
`TRANSCRIPT=<jsonl>` converts a Claude Code transcript to the same events, Edit digests included, so the SC-006 replay
and 375's own report run on converted events. Closing routes refuse without the report (D13).

**D9 - Categories.** From the tool call alone: Edit/Write/NotebookEdit = edit; Bash running `make quick` = quick test,
`make test-file` = test file, `make done` = gate, `make tick`/`claim`/`plan-verdict`/a `/speckit-*` skill = spec-kit step;
Agent by `subagent_type`: the record checks and the modal checks = record check (an ad-hoc modal triage too, known by the
MANIFEST its prompt names); impl-drift and the claims triage (an ad-hoc agent on a `claims-triage` MANIFEST) = claims
check, FR-008's own category; the review checks = review check; `spec-fidelity*` = spec review; `round-arbiter`; anything
else = other subagent; the rest = other tool, which the report breaks down by make target.

**D10 - FR-010: tripwires, each where its event is seen.**
- round cap: record and claims checks get the review checks' cap of two rounds per subject per feature (a round being a
  dispatch at a new fingerprint), counted in `.git/review-rounds.json` as the review checks are;
- A -> B -> A: an Edit whose `new_string` equals an earlier Edit's `old_string` on the same file in the feature (from the
  event log), checked at PreToolUse(Edit); AND, for a page or pop-up, a block that an earlier version had, a later one
  dropped, and the latest has again (by words, so a re-wording counts), over the versions each check dispatch found
  (amendment 1, from T19: 372's bath bullet was added by a script, withdrawn by a `git checkout` and re-added re-worded - no
  Edit, so the digest wire alone could not see it; the spec's "computed from the file's history" asks for this);
- a second red gate in a row: `l7r/diagram/ci/state.py` records each gate's outcome apart from the one slot a quick run
  overwrites, and a red after a red writes the trigger (amendment 1: where the gate's outcome is already recorded);
- A -> B -> A over commits too: the report and the SC-006 replay run the same comparison on the converted events;
- the cascade ratio past a threshold set from the SC-006 replay (`m:cascade-threshold`: the ratio of 372's waves 106 and
  108 and of a sample of ordinary tasks, the wire set between them), checked at each check dispatch;
- a heavy run the quick tier covers: `make test-file` on a file with no `rolls_map` test, or `make done` with no engine path
  changed since the last green gate, refused-with-the-cheaper-command by `measure-hooks.sh`.
A tripwire writes `.git/arbiter-owed.json` and prints the arbiter's command. Until a ruling is recorded, the next check
dispatch on that unit (or, for a feature-wide wire, the next gate or check dispatch) is refused with that command. Nothing
else stops.

**D11 - FR-011: `round-arbiter`.** `.claude/agents/round-arbiter.md`, Opus at high effort (it judges), `omitClaudeMd: true`,
its row in `tests/test_agent_models.py`. `make arbiter-bundle TRIGGER=<id>` writes its bundle out of the repository: each
round's findings marked new / repeated / reversing (each check's reply kept at `make record-checked REPLY=`, compared
round to round by the finding's block and words), the diffs between rounds, the cascade chain from the event log, the
oscillation flags, `request.md` and `spec.md`. It replies one of `continue <what to look at>` / `accept <reason>` /
`process-fault <fault>`. `make arbiter-ruled TRIGGER= FILE= AS=round-arbiter` records it in `specs/NNN/arbiter.jsonl`
(committed): continue lifts the cap by one round; accept closes the unit (later dispatches on it refused) and files what
is left; process-fault closes the unit and appends a tooling row to the feature's `found.jsonl`. A second arbiter dispatch
on a ruled trigger is refused (`pair-hooks.sh`). `REVIEW_ROUNDS_OK` is retired from the cap.

**D12 - FR-012: the GM's review after landing.** `specs/NNN/gm-review.jsonl` holds the to-review rows (every arbiter
ruling and every finding accepted with a reason - `make accept` writes them); the held rows are read where they are today
(328's `audit/overrides.json` `Held`). `make gm-review` lists both by feature. A feature with a row of either kind, held or
to-review, gets one task
`- [ ] GM review (make gm-reviewed F=NNN) [lands-open]`, added by the tooling and exempt from the open-task refusal by its
`[lands-open]` mark (D18); `make speckit-todo`
shows such a feature as `Done - GM review pending`; the task carries `research: rendering`; `make gm-reviewed F=NNN [OVERTURN=<row> TO=<feature>]` ticks it, and an
overturned ruling becomes a row of an open feature.

**D13 - FR-009/FR-014: one closing check.** `scripts/gates/close_check.py` is asked by every closing route - `make tick` on
the last open task, `make gm-reviewed`, and the push for each feature THE DELTA TOUCHES (`plan_gate.touched_features`) that reads closed - its status line opening
any of `speckit-todo.py`'s closing words (`Done`, `Superseded by`, `Withdrawn`: `closed_by_status`) or its tasks all ticked.
Moving a carried key to another feature is an amendment to the declaring feature's spec, reviewed like any other. A feature already CLOSED when the closing check lands is not
asked: the check's own landing commit writes `scripts/gates/closed-before-375.txt`, the features `make speckit-todo` reads
closed at that commit, and nothing else is exempt - 372 (Draft) and 374 (Filed) are asked. The report must exist and the feature's carried keys (`Carried: SC-nnn -> NNN key` in any spec) must be in its
`measurements.json`. `make speckit-todo` lists the carries.

**D14 - FR-004: the preflight phase.** `make done` runs `preflight` first - ahead of the `verified-done` short-circuit too,
since a stale derived file is invisible to that key - `make building-programs`,
`make glossary`, `make record CHECK=1`, `check-research-pointers.py`, `spec-lint.py` on the delta's spec directories, and
`make quick` with coverage over the engine files the delta changed (100% on each). It stops on a failure. "Seconds" is measured, not promised (`m:preflight-cost`); if the record build or the quick tier
makes it longer, the measurement says which, and keeping a slower step in the preflight is put to a MODE 1 exception check. The tree check:
the gate hashes `git ls-files -m -o --exclude-standard` contents at its start (after the preflight) and end; any tracked
file that differs fails the gate naming it - the files the gate itself writes measured first and excluded by name.

**D15 - FR-006: file, don't fix.** Every check bundle's MANIFEST lists the blocks the delta changed (`changed-blocks:`), and
each check contract says to put a finding on any other block under `OUTSIDE THE CHANGE`. `make record-checked REPLY=` reads
that section into `specs/NNN/found.jsonl` as open rows. While a page's apply pass is open (D4), an Edit to a block whose words
equal the merge base's is refused as "filed as row N"; `make found-take ROW=` makes the row the active task's own change.

**D16 - FR-007: armed until the findings are disposed.** `escalation-hooks.sh` still arms at a review's dispatch (so a
review whose row is never written stays armed), and now disarms on either path: `escalation-check` dispatched, or the review
ledger holding that unit's row from this dispatch with every finding disposed - its `acted on` column one of the disposals
(fixed, verified, accepted with a reason, filed as a row, or `nothing` - which the ledger lint admits only on a row whose
verdict found nothing, so it can never switch off an open finding). The ledger lint holds that vocabulary.

**D17 - FR-013.** `CLAUDE.md`'s enforcement table gains the new guards and a three-line note naming FR-010's patterns, and
says that a session asking the advisor about a loop hands it `make arbiter-bundle`'s MANIFEST.

**D18 - Landing by batch, open between them.** A feature with an open task lands nothing, and 375 is too large to sit in one
clone for its whole length. So every decision is reviewed here once, and `tasks.md` holds the current batch's tasks plus one
standing task, `- [ ] T99 Batches 2-4 (plan D18) [lands-open]`. An open box marked `[lands-open]` does not hold the landing
and keeps the feature open in `make speckit-todo` and to every closing route (D13), so 375 lands each batch and never reads
closed until its last box is ticked. **The mark is honored only where it was put by the tooling or a reviewed plan**:
D12's GM-review line, written by `make gm-review`'s tooling in its one fixed form; and a task the plan names on a
`**Lands open**: <task ids>` line, read only while `plan-review.json` is CLEAR and current for that plan. A `[lands-open]`
mark on any other open box is itself refused - at the push (the box holds the landing as an ordinary one, and the refusal
names the line) and by `make tick` - so the mark cannot become an unlogged escape. This plan's line:

**Lands open**: T99

**Amendment 1 (2026-10-10, batch 4; round 2 after the plan review of round 1):** D10's reversal and red-gate wires as built
(above). `make check-closed` (D4) closes only a dispatch SILENT past the 90-minute ceiling - a running check is never closed -
and records each use with its reason in the guard census; it is the fourth escape. The escapes reach their own rule only, each
recorded with its reason and held to the census's floor: `DECIDE_OK` the decide-first refusal (D3), `FREEZE_OK` the freeze and
the apply-once hold (D4), `ARBITER_OK` the arbiter's holds and the round cap, on a check's prompt or a gate (D10). A current
CLEAR plan-stage verdict covers a task section its reviewer read unchanged (D3). The cascade wire (D10) stays live after ANY
ruling: its trigger id advances (`cascade@<rulings + 1>`) and it fires again only when CASCADE_MIN further dispatches since the
last ruling find the ratio still past 1.0 - one round's worth of checks, after a `continue` or an `accept` alike. Batch 4 then
delivers D12, D13, D14 and D17 as planned.

**Amendment 2 (2026-10-10, batch 4, as built):** `ARBITER_OK` (D10) also re-opens a unit an `accept` or `process-fault` closed;
`CLOSE_OK` is the fifth escape, from D13's closing check at the push, reason-floored and recorded. D14 as built, two narrowings:
(1) the preflight keeps the record build (`make record CHECK=1`), which the spec lists among its derived files, though it is
43 of the phase's 51 s at load 7.4 (`m:preflight-cost`) - every other step takes seconds, and the phase costs about a tenth of
a gate where a red it prevents costs a whole one; (2) "100% on each" changed engine file is judged on the CHANGED LINES, and
stops only on a line OFF the hamlet path (`tools/claims.scope`): a line on the path may be reached only by a rolled map, which
the preflight does not roll, so it is reported and left to the gate's floor; and `ci/`, which the project counts as no engine
code (feature 132 FR-025) and tests only in the tooling tree, is left to the gate. `PREFLIGHT_OK="<reason>"` skips the phase,
reason-floored and recorded in the guard census through LOGESCAPE - the sixth escape. A changed line in a module that a test
outside the quick tier reaches - a `tooling`-marked test under `tests/tools/`, a town or city tier test, found by the mirrored
layout, a whole package where the test names one - is reported and left to the gate's floor whether or not a quick test also
reaches the module, as a hamlet-path line is: within seconds the preflight cannot tell whether such a test runs the line. The
reach, listed by the plan review (2026-10-10): `citybudget.py`, `settlement/core.py`, `trades.py`, `castle_civic.py`, eight
whole `settlement/` packages (87 files: structures, city, civic_grounds, homestead_parts, shrines_wells, land, water_ways,
rolling) and five audits (cache_audit, cohort_audit, roll_audit, perf_profile, mapcheck). Wave 106's two untested lines
(`compound.py`, `tools/pack_audit/`) are outside it and still stop the preflight. The tree check excludes the tracked files the gate itself writes (`GATE_WRITES`,
measured on this batch's gate run). D13's list of features closed when the check landed includes 372, closed by its ticks.

A later spec that
must wait declares `**Waits on**: 375`, and `make tick` refuses a task of it while 375 is open - 374's spec carries the line,
so its first task waits for the last batch. Adding a batch's tasks that carry decisions already reviewed is not a plan
change; a batch that needs a new decision amends this plan and is reviewed again.

**D19 - The decision preflight is a plan review of one section.** It is dispatched as `MODE 4: PLAN REVIEW` of the named
task's section, so `review-round-hooks.sh`'s classifier passes it as a plan review and never reroutes it to the verify
twin; `make plan-verdict TASK=<id>` records it under `tasks.<id>`.

### Amendment 1 (FR-015, FR-016)

**D20 - The triage names the page, and a unit is owed only for its own pages (FR-015).** `modal_triage.bundle` already lists
the changed blocks per page and the pop-ups under each; `triage.json` now also records, per unit, the pages it reads
(`_pages_of`: a research unit its `Entry:` pages, `modal-depiction` its `Drawing:` pages). The MANIFEST asks for one line per
(pop-up, page): `TOUCHES <uid> @ <page file name> - <which block>`. `record()` marks a unit touched only when a line names its
uid at one of ITS pages; a line naming no page (the old form), or a page the bundle never showed (misnamed, bare, unchanged),
still names all of that uid's units in the bundle - failing toward checking - so a malformed reply never clears what it meant
to keep (plan review round 1). One bundle and one dispatch, as
now (the advisor's split-by-family alternative costs a second dispatch whenever both families are owed, as in 343's triage).
The SC-007 replay restates the kept reply's 14 lines with the pages they name in their own words ("0099 ..." the question
page, "0104 drawing: ..." the drawing page): `tests/fixtures/modal-triage-343/`.

**D21 - Depiction owed by the words it reads (FR-015).** In `modal_owed.owed`, `modal-depiction` is owed when the pop-up is new
to the About form, or its `depiction` (the Depiction tab and the `Drawing:` list), its About or its `Entry:` changed, or a page
its `Drawing:` names moved (the triage then decides) - no longer when only its Guesses (or Name, Form) changed. About and
`Entry:` stay because the check reads them (About for drawing statements that belong in Depiction, `Entry:` for the candidate
drawing pages `modal_bundle.drawing_candidates` builds - feature 319's plan-review case); the comment at the rule says so.
The unit's answer follows the same words: `depiction_fingerprint` digests exactly what the check reads - About, `Entry:`, the
Depiction tab, the `Drawing:` list and those pages - not Guesses, Name or Form, so a Guesses edit after the check answered
leaves it answered and an `Entry:` edit re-owes it (plan review round 1: owing is judged against the merge base, the answer by
the fingerprint, so the fingerprint is what decides a later edit). Changing the digest re-owes, once, the depiction units
already owed against a clone's base.
The SC-007 replay's restated reply attributes each kept line by where its quoted block stands: a block on both 0104 pages
(garden, genkan) or only on the drawing page (nakamon's divider gate) keeps depiction owed.

**D22 - The clones' view in `make speckit-todo`, display only (FR-016).** Which clones are read is measured first (FR-016): the
listing's wall time reading every clone under `.clones/` against only the active ones - a clone whose event log
(`.git/l7r-events/`, a line per tool call of its session) was written in the last 12 hours, no process scan - recorded as
`m:375-a1-speckit-todo-clones` in `measurements.json`; the active-only limit is kept only if it saves a measurable share of
the listing's time, else every clone is read (measured: about 0.14 s against 0.9 s, the same rows - kept). 12 hours: a
session idle overnight drops out, a session paused for a meal stays. A clone's work is any file under `specs/<feature>/`
(spec, plan, plan review, tasks) committed past its `origin/main` or not yet committed (`git diff --name-only`) - so a clone
BEHIND main shows nothing (the first run listed two abandoned clones' older copies), and a feature closed on main but reopened
in a clone (an amendment in progress) is shown. For each such feature, the listing shows
the clone's state in that state's section, `[in <clone>, not landed]`, one row per differing clone. Only the listing does
this: `--holding`, `--closed-by-status`, `CHECK=1` and `tick-task.py` read the directory they are given, as before.

### Amendment 2 (FR-017, FR-018)

**D23 - One bundle and one ruling for the round triggers owed together (FR-017).** `make arbiter-bundle BATCH=1`
(`arbiter_bundle.batch`) bundles THE BATCH, defined once in `hm_arbiter.batch_triggers`: every round trigger owed now
(`arbiter-owed.json`, kind `round` - the red gate, a reversal, a cascade or an `ask:` stay their own), but a spec review's own
rounds (one spec, ruled alone), plus the rounds the session names as asked ahead (`TRIGGERS=`); each trigger's own bundle in
a subdirectory, under one MANIFEST asking for ONE
ruling with an `exceptions` map; every missing record is reported at once. `make arbiter-ruled BATCH=1 FILE=`
(`hm_arbiter.record_batch`) checks the whole reply first (its `triggers`, no stray exception, the declaration, none already
ruled) and then records each trigger through `record_ruling` - the batch's ruling, or its exception - so holds, closures,
continues and GM-review rows stay per unit. A batch `tooling_fix` is ONE fix: recorded (and opened) on the first trigger
under the batch's ruling - else the first trigger - with every other row under the batch naming the trigger that holds it
(`tooling_fix_on`, which satisfies a `process-fault` row only inside a batch); every row and exception is checked (a ruling,
a `why`, a `process-fault`'s fix) before any is written (plan review round 1: a batch `process-fault` failed on its second
trigger, and an exception on the first dropped the fix). A trigger named twice is refused before writing; the batch's fix
never overwrites an exception's own - with no trigger under the batch's ruling it goes on the first exception without a fix,
and a reply whose every exception carries its own fix while the batch carries one is refused as ambiguous (round 2). "Together" is
"owed now": the triggers a batch of dispatches tripped are owed at the same time, and nothing older lingers because each
holds its unit until ruled. The tooling steers to it: `hm_arbiter.refusal(triggers, root)` - called by the record checks'
cap (`hm_checks`) and the review checks' (`pair-hooks.sh`) with the clone root - names the batch command whenever more than
one trigger of the batch is owed, and `record_ruling` refuses a single trigger's ruling while others of its batch are owed
(`record_batch` passes `batch=True`); a unit is ruled alone only when it is the batch. The round arbiter's contract gains the
batch reply. A ruling row reads its unit from the trigger when the guard never recorded it (`hm_arbiter.unit_of`, the one
parser the bundle uses too - the spec review's aside: 15 of 343's rows had no unit).

**D24 - A round bundle reads its unit from the trigger (FR-018).** `arbiter_bundle.unit_of` parses `round:<check>|<subject>@N`;
`bundle()` uses the owed record's unit, else this, so a round asked about ahead of the cap still carries its rounds, replies
and edits (343's 13 form-check bundles had none).

### Amendment 3 (FR-019, FR-020, FR-021)

**D25 - The order, held at the bundle (FR-019a).** `modal_owed.ORDER = ("modal-form", "modal-research",
"modal-depiction")`, with the units each answers (`modal-research`: the three `modal-accuracy`/`-references`/`-gaps`).
`modal_bundle.bundle` refuses a bundle (exit 3, before anything is copied) when a check EARLIER in the order has a unit on
the pop-up that is owed now (`record_owed.units`) and not answered at its fingerprint (`record_owed.answered`); the refusal
names the first such check's command, `make modal-bundle KIND="<uid>" FOR=<check>`. The escape is `CHECK_ORDER_OK="<why>"`
in the environment (make passes a command-line variable to its recipes); it needs two words or more, and the MANIFEST then
carries a `check-order-escape: <why>` line. A check with nothing owed before it is not held (a pop-up owed only
`modal-depiction`, a page its `Drawing:` names having moved): the rule is read off the owed units, never off the check asked
for. The hold sits at the bundle because every modal dispatch reads a bundle (`check-bundle-hooks.sh` refuses one without);
no hook changes.

**D26 - Settling the checks before (FR-019b, c).** `apply_edits.Round` fingerprints, before the blocks, the units of the
reply's own checks (as today) AND the units of every check EARLIER in `ORDER` than the replying one (`record_owed.earlier`,
from `ORDER`; empty for a check outside it). After the blocks, a unit of the reply's own checks settles as today (answered,
or pending until `make record-checked`); an earlier check's unit settles ONLY where its answer already stands at the words
before the blocks (`record_owed.answered`) - never pending, because an answer recorded later would be an answer to words that
check never read. Its result line says whose blocks settled it. A reply settles nothing of a check LATER in the order (c):
`earlier("modal-form")` is empty, and `modal-research`'s blocks leave `modal-depiction` owed.

**D27 - One parse per content (FR-020a, d).** `record_cache.ParseCache`: a mapping from `sha256(file text [+ its
originals])` to the parsed `Page`, notes triple (notes, cites, readings) or write-up words, held in memory for the run and on
disk as one pickle per version of the parsing code (`<git common dir>/l7r-cache/record-parse-<code sha>.pickle`, written
atomically, only when the run added entries; an older version's file is deleted when a newer one is written). The code sha is
over `record_units.py` and every project module it imports, transitively (`record_cache.code_sha_of`: an `ast` walk of
`import`/`from` statements resolved to files beside it or under the repository; `record_units.py` imports only the standard
library today, so its set is itself, and a test adds an import to prove the walk follows it). `Record.of(files, sources,
cache=None)` reads through it; `record_owed.read_at` passes the clone's. A corrupt or unreadable cache is an empty one;
`L7R_CACHE_OFF=1` disables the disk cache. A command builds only what it prints (FR-020(d)): `record_owed.units(root,
families=, uid=)` computes only the families asked for (`record`, `translation`, `entry-drift`, `modal`) and, for the
pop-ups, one uid (`modal_owed.owed(root, base, uid)`). `modal_bundle.bundle` asks once for its pop-up's modal units and
hands them to the triage refusal, the D25 hold and `owed_lines` (today it computed the whole delta twice to print one
pop-up's lines); `check-bundle Q=` (`bundle_owed.owed_for_question`) asks for the record and translation families (and
entry-drift for `FOR=entry-drift|all`), `check-bundle KEY=` / `KEYS=` (`owed_for_key`, once per batch) and `FOR=intro-check`
(`intro_bundle`, once per batch) for the record family alone, and each computes the whole delta only for a refusal's list of
what IS owed - the one consumer that needs other subjects' units. `claims.py`'s command freezes its heap before exiting
(`gc.freeze()`, in the `__main__` block only): measured 2026-10-11, the interpreter's final collection spent 3.2 s of a cold
run walking the engine parse's objects (`m:375-a3-record-tooling-after`).

**D28 - One `git` batch per revision (FR-020b).** `modal_owed._read_at(root, rev)` returns a reader backed by ONE `git
ls-tree -r` of the directories it serves and ONE `git cat-file --batch` of their blobs (`record_owed._cat`, moved to
`record_cache.cat_blobs` so all three import it), filled on the first read; a path outside them falls back to `git show`.
`modals_at` and `owed` use it in place of their per-file `git show` calls (299 at the base on 374's delta), and
`entry_owed` its own per-file calls the same way (177).

**D29 - The claims kept by their sources (FR-020c).** `scripts/record/claims.current(skill, qdir)` keys the units and
claims it builds from `all_units` on `sha256` over every `l7r/diagram/**/*.py` under `skill` (path and content) and the
`PROCEDURES` documents, and on the code sha (`record_cache.code_sha_of`) of `scripts/record/claims.py` and every project
module it imports, transitively (`record_units`, `claims_triage`, `record_cache` and what they import; the engine's claim
reader is under `l7r/diagram/` already). A hit loads them from `<git common dir>/l7r-cache/claims-<key>.pickle` and
recomputes only `research_fp` (it reads question pages, which change independently). Only the newest key is kept. Wrapping
at `scripts/record/claims.py` keeps the engine untouched and the landing DIRECT.

**D30 - The script tests by what they touch (FR-021).** `tests/hooks/hookdeps.py --pydeps <test file>` prints the test's
freshness set: the file; each `conftest.py` from its directory up to `tests/`; the `tests/` modules it imports; every file
of `scripts/` and `tests/hooks/` it reaches, transitively through any file (`py_closure`): a Python file reaches what it
imports and what a string literal of its code names (a literal equal to a file's stem, `_sibling("record_owed")`, or
ending in its file name), a shell or text file every file whose name stands in its code, as the guard suites' scan does;
and all of `scripts/` and `tests/hooks/` - failing toward running - when the test builds a script path at run time
(`"scripts"` joined to a non-literal, or `scripts/` inside an f-string's braces), names the `scripts` directory itself as a
path's end (`(REPO / "scripts").rglob`, `os.path.join(REPO, "scripts")`, `SCRIPTS = REPO / "scripts"`), globs the tree, or
reaches no file under `scripts/` or `tests/hooks/` at all (a selected file is selected because it reads `scripts/`). The Makefile's pytest step
hashes each selected file's set, runs only the files whose hash differs from their stamp
(`<git dir>/hooks-test/py/<test path with / as __>`), and stamps every file it ran when the run is green; a red run stamps
none. `HOOKS_ALL=1` runs all; under `make done` the step is skipped as today.

**D31 - Measured, not assumed (SC-012, SC-013, SC-014).** SC-013 is run by a scratch script on two detached worktrees at
61a52f3c8, one with today's code and one with the new, the backlog's answer store copied: each command alternately on each,
three runs apiece, cold (the cache directory removed) and warm, the load average recorded at the start and end; the medians
go into `375-a3-record-tooling-after`, and each command's output is compared byte for byte between the two (and with
`L7R_CACHE_OFF=1` on the new). SC-014's count runs `hookdeps.py --pydeps` against main's last ten commits touching `scripts/`
and counts the files each would run; key `375-a3-hooks-test-after`. SC-012 is carried to 374: 374's next
pop-up wave counts its dispatches per unit with `scripts/measure/popup_rounds.py <clone> --since <the wave's start>`, as
`m:375-a3-popup-rounds-before` did.

### Amendment 4 (FR-022)

**D32 - The sync suite in parallel parts (FR-022).** `tests/hooks/test-sync-with-main.sh` keeps its fixture (`topology`,
`syncmain`, `stamp_hooks`, `check`, `expect_out`) and moves the helpers several cases share (`yes_`, `no_`, `rref`,
`in_progress`, defined mid-file until now) above the cases, so a case finds them whichever part runs it. Each of the 26
headed cases becomes a function (`case_01` ... `case_26`, in file order, its measured seconds beside it), its body
unchanged; no case reads a variable another sets (checked by a scan of each body against its own assignments and the
header's). The runner deals the cases into `SYNC_PARTS` parts (default 4), longest first onto the lightest part by the
measured times (`WEIGHT`; a case without one counts 10 s); each part is a background subshell with its own `$T`, `HOME`
and `GUARD_LOG_DIR`, prints `@@reported <case>` after each case and writes its PASS and FAIL counts to a file; the runner
waits for all, prints each part's output in order without the markers, sums the counts, and for a part with no counts
file fails once for each case that never reported, naming it. The suite's last line is unchanged (`all sync-with-main tests
passed (N checks)`), so `hookrun.sh` and the stamps are untouched. `SYNC_PARTS=1` runs the cases in order in the suite's
own shell. SC-015 is measured by a scratch script: today's file at bfe25f2da in a detached worktree and the new one,
alternately, three runs each, the load at both ends, every run's check count against 123; then five runs in parts and one
with `SYNC_PARTS=1`; the two failure cases by a scratch copy with one case's body made to fail and one made to `exit`. Key
`375-a4-sync-suite-parts`.

### Amendment 5 (FR-023 to FR-027)

**D33 - A flag, never a refusal (FR-023).** `perf_review.check` returns True always and prints, per environment, the pair's
band, the records made (if any) and, at band 1 or more, `perf_bands.flag(v)`: the seeds over the line, the metric, both
snapshots' machine state at their two ends, the load caveat and "mention it when you report the landing; nothing waits on
it". `perf_review main check` exits 0; `sync-with-main.sh`'s step keeps calling `make perf-review` (so the flag prints at the
push) and dies only if the command itself fails to run. `arbiter_signed` loses its one caller and is removed; the record
commands (`explain`, `confirm`, `audit`, `signoff`, `arbiter-subject`) are unchanged, for an investigation. `perf-gate` already
exits 0 on any band (it requires the `-start` bookend, a measurement, not a verdict) - its help line says so. `perf_bands.OWES`
says what each band means, not what it owes.

**D34 - The machine's state and CPU time (FR-024).** `perf_snapshot.machine_state()` reads `/proc/meminfo` (MemAvailable,
MemTotal, in MB), `os.getloadavg()` and `shutil.disk_usage(SKILL)`, each field left out where the machine cannot give it.
`record` takes it before the first roll and after the last (`machine_before`, `machine_after`) and writes `total_cpu_seconds`.
`measure` times each stage with `time.process_time()` beside `time.time()` (`cpu_stages`, `cpu_seconds` on a row) and, with
`warm=True` (the reference leg), rolls the first seed once untimed first. `perf_bands.metric_of` picks `cpu_seconds` when every
compared row on both sides carries it, else `seconds`; `_judge` reads that key and its stage map; the Verdict carries `metric`
and `machines`; `render` names the metric.

**D35 - 5% (FR-025).** `BAND1_PCT = {"local": 5.0, "codebuild": 5.0}`, `BAND1_DEFAULT_PCT = 5.0`, with the GM's words and
R4 beside them; bands 2 and 3 unchanged.

**D36 - The scaling leg on request, and the trend (FR-026, FR-027).** `record(label, seeds, scaling_leg=False)` rolls the legs
only when asked; `--scaling` on the CLI; `make perf SCALING=1`. `report` prints, per snapshot, the CPU total and the 1-minute
load and free RAM at start and end (`_ends`, dashes for a snapshot from before), and the pair's comparison is
`perf_bands.render` alone (the old wall-only table and its "DIAGNOSE in writing" line go: one reading of a pair, the bands').

**D37 - The texts (FR-023's closing bullet).** Constitution VI's performance clause rewritten (2.30.0, MINOR); root
`CLAUDE.md`'s push and gate rows; `l7r/diagram/CLAUDE.md`; `dev/performance.md`; `docs/guards.md`'s two rows;
`docs/efficiency-tooling.md`; `scripts/container/append-system-prompt.md`'s standing order; `perf-audit.md` and
`round-arbiter.md`; `docs/make-targets.html` regenerated from the Makefile.

### Amendment 7 (FR-029 to FR-034)

**D38 - The cohort through the roll cache (FR-029).** `cohort_audit._report_of` obtains each seed's roll by
`rollcache.obtain("cohort:<spec>", ..., recorded=rollcache._in_child(cohort_roll.ROLL_TARGET, spec))` - the gate's own
roll (`rollcache._roll_payload`, `generate` in a child), keyed by the engine functions it executed and the files it read, served
when that key is unchanged - in place of calling `generate` itself; its own checks (households seated, farmstead across the
brook, the matrix, ...) run on every report as before. A REFUSAL is stored like a report (the plan review: 374's cohort had
two refused seeds, which rolled again each run): `cohort_roll.roll_or_refusal` returns the engine's refusal - a ValueError or
RuntimeError, the classes every `...Refused` derives from - as a `Refusal(module, name, message)` payload, which also carries
its NAME across the child (whose own failure is one generic RuntimeError); `roll_how` names it as before, served or rolled.
`Refusal`, `roll_or_refusal` and the child's target `ROLL_TARGET` live in their own module, `l7r/diagram/tools/cohort_roll.py`,
which every process imports by its real name (plan review round 2): `make cohort` runs `cohort_audit` as `__main__` and its
pool workers as `__mp_main__`, so a class defined in `cohort_audit` was not the class the child unpickled, and a target named
from `__name__` could not be imported by the child (the first measurement's legs, 2026-10-12, refused 54 of 54 seeds - their
cohort-log records, discarded). Tests: a refusal
crosses a REAL roll child as `cohort_roll.Refusal` (`tests/tools/_cohort_child.py`); `cohort_audit` run under `__mp_main__`
in a fresh interpreter holds that one class and a target the child imports.
A crash - the child dies, memory, a timeout - is no refusal: it raises, is reported by its name, and is never stored. The
gate's own `roll:` subjects and `rollcache.report` roll and are served exactly as before, sharing the store and its kept
versions (below). The store: `rollcache`'s directory is the clone's `.gencache/rolls`; in a LINKED worktree
(`git rev-parse --git-common-dir` is not the worktree's own `.git`) it is the main worktree's, so a "before" leg rolled in a
detached worktree at the merge base reads and writes the clone's store (`rollcache.roll_store_dir()`, asked of git once per
tree by `_main_worktree` and read from `gencache.CACHE_DIR` on every call, redirected only while that is the tree's own
`.gencache`; keys are path-independent since feature 167).
`GATE_NO_CACHE=1` and the FULL test run bypass serving as they do for the gate. THE STORE KEEPS SEVERAL VERSIONS OF A SUBJECT
(measured 2026-10-12, the second measurement): with one entry per subject, the two legs - the merge base's code and the
clone's, rolling the same subjects - evicted each other, and the second wave served 0 of 54 in either new-code leg while the
leg that wrote last was served 8 of 8 when asked again. So `_produce_and_store` moves a different version already in
`_entry(subject)` beside it as `<entry>.v-<key>` before writing the new one (`_shelve`), keeping `KEPT_VERSIONS` = 4 (both
legs and two earlier; an entry is at most ~0.85 MB, median 0.6 MB, the store 60 MB over 119 entries - `du`, 2026-10-12); `obtain` and `report_deps` serve the newest entry whose key matches
the code as it stands (`_current`), else an older kept one, newest first. This holds for the gate's `roll:` subjects too: a
clone switching between two engine states (a reverted edit) is served its earlier roll. A reader racing a move finds no entry,
which is doubt, and doubt produces. Tests: two code versions alternating are each served; the oldest beyond the cap is
dropped; an unreadable newest entry is overwritten, never moved; red on today's code.

**D39 - The cohort's per-seed record (FR-029).** `cohort_audit.audit` writes `dev/cohort-log/<UTC stamp>-<clone>-<pid>.json` in
the CLONE (from a linked worktree, the main worktree's - a "before" leg's worktree is removed, the plan review's note): the
run's count, first seed, households, commit and, per seed, `served` or `rolled`, `pass`/`fail`/`refused`, its failures (a
refusal's by name) and its form. It names the file in `<git dir>/last-cohort-record`, and `make cohort` commits that one file
(`scripts/gates/commit-run-record.sh <result> last-cohort-record`; the spec review's aside, round 2).

**D40 - The census on request (FR-030).** `make perf` no longer runs `make census`; `make census` is unchanged.

**D41 - The suites in parallel processes (FR-031).** `test-batching-hooks.sh` and `test-pair-hooks.sh`: the helpers and the
constants several cases share are defined once before the cases; each case is a function `case_NN`, its measured seconds
beside it (traced 2026-10-12); with no `CASES` the suite deals the cases into `SUITE_PARTS` (default 4) processes of itself,
each re-running the setup (its own fixture, temporary files and guard log) and then only its `CASES`, longest first onto the
lightest part; each part prints `@@reported <case>` and `@@counts <pass> <fail>`; the parent prints every part's output,
sums the counts, fails a part that ended before a case reported, naming it, and prints the suite's own pass line. The scan
(each case alone in a fresh process; for each that fails alone, the shortest run of its predecessors that passes):
batching, all 15 pass alone; pair, 12 of 15 pass alone, `case_07` needs `case_06`, `case_08` needs `06` and `07`, `case_13`
needs `case_12` - dealt as chains, one unit each, in order. `test-entry-gate.sh` stays serial: it is one sequence of edits to
one page in one throwaway clone: of its eight cases, `case_04` needs `case_03` and `case_06` needs `case_03` to `case_05`, one
chain over half the suite, and the whole suite took 22 s alone (`m:375-a7-suites-scan`, 2026-10-12; its 67 s in R3 was taken
with the other suites running beside it) - under the split pair and batching suites' times.

**D42 - The shortcut earns the hooks stamp (FR-032).** In `make done`'s "already verified" branch: when `gate-stamp.py --fresh
hooks` fails, `make hooks-test` runs first; red, the gate logs `failed:hooks-test`, commits its record and fails.

**D43 - The gate commits its own record (FR-033).** `LOGRUN` names the record it wrote in `<git dir>/last-run-record`;
`scripts/gates/commit-run-record.sh <result> [pointer]` commits exactly the file its pointer names (default `last-run-record`;
`last-cohort-record` for D39), in the work tree holding it, with `git add` and `git commit --only -- <it>` as `the gate's run
record (<result>)` - no other file under `dev/run-log/` (`ci/runlog.py` writes there too; the plan review), nothing the session
staged; the pointer is spent; skipped inside a CodeBuild build and outside a work tree; never fails the caller. Called after
each of `make done`'s SIX record writes: already verified, its hooks failure, the reference step's failure, the two red
sites, green.

**D44 - Measured (SC-022, SC-024, SC-027).** SC-022: the cohort on 374's delta - four detached worktrees: the merge base
a41ab2e0f and 374's 61a52f3c8, each once with today's code and once with the new `cohort_audit.py`, `cohort_roll.py` and `rollcache.py` copied in
(the store is shared only where the new `rollcache.py` runs), the backlog's own store not copied - `make cohort N=48 JOBS=4`
(4 = `L7R_ROLL_SLOTS`' default, the child rolls allowed at once), a "before" and an "after" leg each, twice, old and new
alternating; key `375-a7-cohort-after`. SC-024: the two split suites, today's file (a detached worktree at the commit before) against
the new, alternating, three runs each, the check counts compared; key `375-a7-suites-parts`. SC-027 is
`m:375-a7-turn-time`, re-derived by `scripts/measure/turn_time.py`.

### Amendment 6 (FR-028)

Handed to this session by the Diagram tooling session after amendment 7's decisions were reviewed, so its decisions follow them.

**D45 - About leaves the depiction rule (FR-028; T44).** `modal_owed.depiction_owed_by(was, m)` - the pop-up new to the About
form, or its `depiction` (the Depiction tab and the `Drawing:` list) or its `Entry:` changed - is the one predicate: `owed()`
emits a `modal-depiction` row on it (with "its Depiction, Drawing: or Entry: changed" as the occasion), or on a page its
`Drawing:` names moving, as before; and the replay (`scripts/measure/depiction_replay.py`, SC-021) counts with it, so the rule
and its measurement cannot drift apart. `depiction_fingerprint` drops About: `[uid, Entry:, Depiction + Drawing:, the drawing
pages]`. The ORDER comment (depiction last "because it reads About") says instead that depiction reads the `Entry:` a research
round may move. No round counter changes: `hm_checks.dispatch` counts a round per dispatch let through, the bundle hook refuses a
dispatch whose MANIFEST owes the check nothing (`CHECK_NOT_OWED_OK`, feature 311), and the MANIFEST's owed lines are
`record_owed.units`, which `owed()` now leaves without the depiction unit after an About-only edit - so that edit adds no round.
Tests (in `tests/tooling/test_modal_triage.py`, red on today's code): an About edit alone owes `modal-form` and the research
checks and not `modal-depiction`; an `Entry:`, Depiction or `Drawing:` edit still owes it; after a depiction answer, an About
edit leaves `record_owed.unanswered` with no depiction unit for the pop-up (the round count's input). SC-007's About case in
`test_depiction_is_owed_by_the_words_it_reads` is turned around with it (FR-015's About clause is superseded).

**D46 - Answers recorded under amendment 1's formula stand (FR-028; T44).** `modal_owed.amendment1_depiction_fingerprint` keeps
amendment 1's formula (About in it). `record_owed.amendment1_depiction_answered(root, store, slug)`: the pop-up as its file stood
when the answer was recorded (the last commit before the answer's `utc`, as `legacy_depiction_answered` finds it - the helper
`_modal_then` is lifted out of that function and shared) has an answer under amendment 1's formula, and its fingerprint under
the new formula equals today's. So an About edit since keeps the answer and an `Entry:`, Depiction, `Drawing:` or drawing-page
change since does not. `unanswered` accepts it beside `legacy_depiction_answered`. Without it the formula change would owe every
About-form pop-up's depiction once, in every clone (amendment 1's change did exactly that on 2026-10-11: 31 units). Test in
`tests/tooling/test_record_owed.py`, beside the legacy one.

**D47 - The contract, the closing rows (FR-028; T44, T45).** `.claude/agents/modal-depiction.md`: the sentence "Anything about
how the map draws the thing that sits in About instead belongs here (M13): report it" becomes "About is in your bundle for
context: a drawing statement there is `modal-form`'s finding (M13), not yours - report nothing from About." The bundle keeps
rendering About (`modal_bundle.render`, every check's `modal.md`); `modal-form`'s M13 line is already the amended rule (landed
2026-10-12). SC-021's "a `modal-form` bundle carries M13's About rule": a test that `make modal-bundle FOR=modal-form`'s
`guidelines.md` holds M13 and its contract the About sentence (passes today). 343's rows 83 and 84 close in `found.jsonl` on
their About part: each row's `status` becomes `closed`, with the date and T44's commit beside it. No found row has been closed
before (all 80 on main are open) and nothing reads the field, so there is no tool to build for two rows: an edit in place.

### Amendment 8 (FR-035 to FR-038)

**D48 - The claims cached per module (FR-035; T51).** `tools/claims.all_units` and `claimed_outside` take an optional `memo`
(a mutable mapping; None keeps today's behavior, so a test or a one-off caller is unchanged). Two kinds of entry:
`parse:<sha of the module's source, its name, is-package, the sorted known-module set>` holds what the scope walk and the
constants need of a module - its in-scope imports (`_imports_of`), `module_constants`, `import_table`, and the modules its
`import`/`from` statements name - so an unchanged module is not parsed; `units:<sha of the source, its path, name,
is-package, every_module_unit, the known-module set, and the constants of every module it names>` holds `module_units`'
(claims, errors, units). A module's units read only its own constants and those of modules its imports name (`module_units`'
`values`, through `import_table` and `module_aliases`), so keying on exactly those recomputes a module when a constant it reads
changes, and not otherwise; a module whose source changed is parsed once. `scripts/record/claims.units_of` keeps today's
whole-scope cache as the first layer (1.0 s warm) and, on its miss, passes a memo loaded from one file
(`<common dir>/l7r-cache/claims-modules.pickle`, through `record_cache.ParseCache`), saved after, holding only the entries this
run used, so the file does not grow. The procedure documents (`doc_units`, a few files) are recomputed as today. Tests (red on
today's code): an edit to one module recomputes that module's units alone (the memo's misses counted); an edit to a constant
another module imports recomputes that module too; the memoized units equal an uncached `all_units`; a second run is all hits.
SC-028's time is `make claims-owed` after a one-line comment, today's code against the new, three runs each, key
`375-a8-claims-after`.

**D49 - The word frequencies and the translation pairs kept (FR-036; T52).** `record_prepass.corpus_frequency` keeps each
fragment's word set by the sha of its bytes in `<common dir>/l7r-cache/prepass-words.pickle` (`ParseCache`; the walk and the
reads stay, the parse of an unchanged fragment does not), and sums them as today, so the counts are the same; entries not used
in a run are dropped on save. `translation_owed.record_pairs(root, rev)` for a revision keeps its result by that revision's
`research/questions` tree id (`git rev-parse <rev>:research/questions`) in `<common dir>/l7r-cache/translation-pairs.pickle`,
the newest four trees kept; the working tree's pairs are read as today. Both are keyed by content, never by time (amendment
3's rule), and a cache that cannot be read or written costs time, never a wrong answer. `check_bundle.run_script` and the
helpers stay as they are (Decisions Recorded). Tests (red on today's code): a second count with one fragment edited parses
that fragment alone and equals an uncached count; the pairs for a revision are read from git once. SC-029: `make check-bundle`
on question 0021 then 0022, today's code against the new, alternating, three runs each, key `375-a8-check-bundle-after`; the
two bundles' files compared with an uncached run's (`L7R_CACHE_OFF=1`).

**D50 - The review checks' yield (FR-037; T53).** `scripts/measure/review_yield.py`, run by `make review-yield [SINCE=<date>]`
(default 2026-09-26, the ledger's cost columns' first full day), reads `dev/review-ledger.md`'s measured rows and prints per
check: passes; passes with a finding; findings acted on (the "acted on" cell opens with fixed or filed) and dismissed (verified,
accepted, declined, left for the GM, no change); the author had missed it (the "missed" cell yes); hours (wall) and tokens out;
and the features the rows name (a three-digit number in the subject). Sorted by hours; a check's yield is acted-on findings per
hour. `--record <file> --key <k>` writes it to `measurements.json` (`375-a8-review-yield`), as `turn_time.py` does. The GM is
given the table and the lowest-yield checks for their cost at landing; nothing about a check changes. Tests on a small ledger
fixture: each column counted from its cells, a row with no cost cells skipped.

**D51 - The cohort's seeds (FR-038; T54).** `scripts/measure/cohort_seeds.py`, run by `make cohort-seeds`, reads
`dev/cohort-log/*.json` and prints per failure (its name, e.g. `refused:WebRefused`) the seeds that found it and the changes
they were rolled on; how many changes the records span; and the fewest first seeds that find every failure (the largest, over
failures, of the smallest seed finding it; the pinned seeds, 901 on, are rolled every time and left out). A change is a record's
`feature`: `cohort_audit.write_record` adds `"feature": $SPECIFY_FEATURE` (empty when unset); the records written before that
field are attributed by `dev/cohort-log/features.json`, a commit -> feature map holding the two commits rolled before it
(61a52f3c8, 374's head, and a41ab2e0f, its merge base: both feature 374). The GM is given today's output at landing (one
change: seeds 10 and 20, `refused:WebRefused`), and `make accept` files the row that carries the choice past the close. Tests:
a fixture of records from three changes names the failures, their seeds, the span and the fewest first seeds; a record with no
feature and no mapping is counted as unattributed, by its commit.

**D52 - Measured, raised and closed (T55).** SC-028 and SC-029 as D48 and D49 say; SC-030 the table's key; SC-031 the command's
output over today's records. At landing two `make accept F=375` rows: FR-036's deviation (the cache in place of the helpers
folded in) and the seed count's choice (FR-038), so `make gm-review` holds both for the GM; FR-037's table goes in the landing
message. Tests, `make hooks-test`, the gate, the report.

## Batches

1. **Measurement, the two fixes and staying open**: D7, D8, D9 (the event log, the report, the transcript converter; SC-005
   on 372 and a one-task feature; 375's report so far), D5, D6, D18's `[lands-open]` mark and `**Waits on**:`.
2. **The owing logic**: D1, D2 (with its migration), D15; the SC-001 replay.
3. **The guards and the arbiter**: D3, D19, D4 (with the EDIT blocks added to intro-check, record-style and
   translation-check), D10, D11, D16; the SC-006 replay.
4. **The gates and the doctrine**: D12, D13, D14, D17; FR-014's carry; SC-002's audit (each FR's old-behavior test listed);
   375's own report written; the feature closes.

## Project Structure

```text
specs/375-enforced-wave-process/   plan.md, tasks.md, measurements.json, plan-review.json, report.md
scripts/measure/feature_report.py, event_log.py      (D7-D9)
scripts/record/modal_triage.py                       (D1)
scripts/record/claims.py, claims_triage.py (split)   (D2, D5; claims.py 890 lines on 2026-10-10, wc -l)
scripts/gates/close_check.py, plan_gate.py           (D6, D13)
scripts/hooks/event-log-hooks.sh, lib/hm_checks.py   (D4, D7, D10)
.claude/agents/round-arbiter.md                      (D11)
l7r/diagram/tools/claims.py                          (D2)
```

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
closed with `make check-closed ID= REASON=`. Escape `FREEZE_OK`.
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
  event log), checked at PreToolUse(Edit); the report also finds it from the commits;
- a second red gate in a row: the gate's own failure exit reads the previous run's state;
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

**Lands open**: T99 A later spec that
must wait declares `**Waits on**: 375`, and `make tick` refuses a task of it while 375 is open - 374's spec carries the line,
so its first task waits for the last batch. Adding a batch's tasks that carry decisions already reviewed is not a plan
change; a batch that needs a new decision amends this plan and is reviewed again.

**D19 - The decision preflight is a plan review of one section.** It is dispatched as `MODE 4: PLAN REVIEW` of the named
task's section, so `review-round-hooks.sh`'s classifier passes it as a plan review and never reroutes it to the verify
twin; `make plan-verdict TASK=<id>` records it under `tasks.<id>`.

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

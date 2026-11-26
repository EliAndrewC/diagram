# Morning handoff: the talk before the port resumes (written 2026-11-26, overnight)

For the FRESH session that holds the talk with the GM (449 T437). Everything below is on GitHub `main`, and the tooling state is in its private repository (step 2). What does NOT outlive the
old container: the sessions' transcripts under `~/.claude/projects/` (the measurement scripts that read them keep their
result tables beside them in `dev/measurements/`) and the build caches. Read this, then `specs/449-rust-codebase/port-talk-agenda.md` (the 14 items with their measurements)
and `docs/process-decisions.md` (what is already decided, and declined, with the numbers and what would reopen each).

## To pick up in a new container

1. Clone into `/diagram/.clones/<session-name>` as `docs/session-clones.md` says; `scripts/sync-with-main.sh sync-in`.
2. `make state-restore FROM=diagram-backlog` - the old session clone's tooling state (the check answers and the event logs
   `make task-time` reads) from the private `EliAndrewC/diagram-tooling-state` (never link or copy it anywhere public; the
   same for `EliAndrewC/diagram-research`). The state is kept per clone NAME, so a bare `make state-restore` in a clone of
   another name restores nothing. Rehearsed 2026-11-26 in a throwaway clone: 2,755 answers and 578,276 log lines restored
   in 8 s, and `make task-time SINCE=24h` then read 47 landed tasks. NOT in the saved state: the page sessions' handoff
   files (`.git/l7r-handoffs/`; P16-P18's are spent, their results on main) and the sessions' transcripts.
3. `make switches` - the research switch is OPEN (the GM, 2026-11-25: "We can also handle those open research tasks
   overnight as well, whenever it is convenient."); the claims switch is at `report`.
4. `make speckit-todo`, `make audits` (the register, the overdue first), `make task-time SINCE=48h` (the task time breakdown).

## Where the port stands

- 449's pre-port tasks are all landed. Open in 449: **T437** (this talk - not a build task; it closes only with the GM's
  words), **T438** (the grove at each farm; waits for the homesteads port), T158 (the deletion close).
- The port has NOT resumed. Nothing in the engine was ported overnight. The next stage and the process for it are the talk's.

## What the talk decides (the GM's, not pre-approved)

- **The porting process itself**, and before it a larger structural change to how development is done in this project that
  the GM wants to discuss before the mapping work resumes (he will refer to trial 456 for it).
- DECIDED 2026-11-26, item 8: clones for sessions, pooled worktrees for builders (`docs/process-decisions.md`).
- DECIDED 2026-11-26, the output style: the conversational style stays (his words in the declined entry).
- **Item 10** long-running against small features: trial `specs/456-feature-size-friction/` re-measures it, not before
  2026-11-28, on the landings since the fixes.
- **Two tiers of checking** (adopted as a trial 2026-11-26; `docs/process-decisions.md`): round two of the worktree fixes
  runs under it, at three builders and then a batch at four. Trial `specs/458-second-tier-threshold/` reads the second tier's
  threshold again, and weighs the continuous gate, not before 2026-11-28.
- **Several sessions at once**: feature `specs/459-multi-session-builders/`, filed to be thought about, not worked before the
  port resumes (his words).
- **The builders' context cap and brief sizing**: trial `specs/457-builder-handoff-rate/` re-measures the handoff rate, not
  before 2026-11-28 (7% on 2026-11-26 against 28% before sizing; the rule tightened that day). The GM wants both trials
  talked about before the port resumes.
- **Item 11** whether everything must be a spec-kit feature: a measurement of what the task route adds over a direct tweak was
  started 2026-11-26 (its result in `dev/measurements/2026-11-26/` when done).
- **Extending the early build to the SPEC review**: his (it amends constitution XVI); a measurement of how often a first spec
  review reverses work is owed before it is put to him.

## Before the port resumes (the GM, 2026-11-26)

- "I agree that all of our tooling fixes around work trees need to land before we resume the port." The set: 451 T159, T275,
  T281, T284, T286, T288, T294, T295, T296, T297, T300, T302, T303, T304, T305, T104 (the test that fails under load: "I agree with prioritizing the
  test that fails under load being fixed"), and the disk follow-ups T278 and T301 ("we should make sure to fix all of this as part of our
  tasking that we are doing before resuming our port. But after we talk about the most efficient way to parallelize") (landed already: T285 the warm pool, T292 the landing refusals and
  `make carry`).
- The sequence he approved ("Your proposed sequence ... sounds right to me, so yes, please proceed with that"): (1) the pool
  lands - done; (2) round one, three builders at once in warm pool trees with no build slot yet, on T284, T295 and T281, the
  memory and load sampler running; (3) the numbers are looked at together and the builder count settled, with the file-overlap
  measurement (`dev/measurements/2026-11-26/file-overlap/m15-results.md`); (4) round two, the rest of the worktree fixes at the
  settled count with the build slot in.

## Closed overnight under the GM's pre-approval of 2026-11-25

- **Item 6**: building begins while a feature's plan review runs (decided 2026-11-25).
- **Item 12**: the builders' context cap stays 300k, builders stay, briefs are sized (decided 2026-11-25).
- **Item 9, the disk and time levers**: none adopted - lighter debug info was already in (451 T246); incremental-off, a
  shared compiler cache and an eager drop of coverage builds declined on measurement; stale coverage variants are 451 T278.
- **Items 1-5 and 7**: two code builders at once in REUSED worktrees (decided 2026-11-26). Landed per wall hour 1.71 at one
  builder, 2.02 at two; memory measured that morning - two builders and a landing peaked at 6.3 GiB anonymous against the
  container's 10 GiB limit, no sample over the 7 GiB margin, no OOM kill; three code builders, run later that day, peaked at 6.4 GiB,
  the same, so memory does not cap the count. Processor does: load median 42, peak 94 on 22 cores at three, and a cold
  worktree's first closing checks took 14 to 30 minutes. Two is the measured default until the warm worktree pool (451 T285,
  the GM's instruction that the tooling enforce reuse) and the build slot (451 T284, his synchronization point) are in; then
  three and four are re-measured. Items 2-5 and 7 have no measurement of their own.
- **Still open of the pre-approved set - item 14**: its cost is measured (the agenda's item 14: 26 escalation-check runs,
  1.85M tokens in), but neither pre-approved lever has been - a shorter builder report format (adopt if shorter with nothing
  lost) and escalation-check on a narrower bundle (adopt if its verdicts do not change). A Sonnet-tier seeded test was
  discussed beside them and is NOT in his pre-approval's words. Each closes with a Decided entry and an audit entry.
- **Item 13, the audit register**: built and in force (451 T259; `make audits`), its backfill 451 T260. It was not in the
  pre-approved set and is not a question for the talk; it is where the talk's decisions get their audit entries.

## The GM's canon answers (recorded in `docs/gm-rulings.md`), and what the record did with them

- 2026-11-26: Ryusei had no provincial lineages until the Lion/Unicorn war and has since acquired some (0138 and 0140 restated).
- 2026-11-26: burakumin neighborhoods stand inside a city's walls, at the edge. The search he asked for found a quarter inside the wall
  attested for China (Zhending 1551, Shaoxing) and outside by a gate elsewhere; Japan at the edge or beyond. 0156 and 0193 no
  longer call the placement a deviation; the siege reason is labeled the setting's own. The maps did not move.
- 2026-11-24 (not a new answer; applied overnight): a provincial city's 3,000 include the samurai country estates (0173
  restated by P16; 0001 and 0174 by P18).
- NOT an answer of his: 0142 now reasons the Emperor's granaries' siting from Imperial oversight, which his notes
  (`budgets.md`) state; the brigands reasoning was this project's writing.

## For the GM, small (read by `escalation-check` 2026-11-26: 2 kept, 2 rewritten as below, none cut)

- ANSWERED 2026-11-26, three or four builders for work that compiles nothing: covered by his pre-approval ("I thought I
  already pre-approved whatever number and arrangement of parallel builders our measurements support."); it stands on weak
  measurement and is re-measured, with memory sampled, at the next such batch (`docs/process-decisions.md`).
- ANSWERED 2026-11-26, the disk trade: time over disk - the coverage builds stay (`docs/process-decisions.md`, "Declined so
  far", his words).
- ANSWERED 2026-11-26, 0141's aqueduct banks: 2 px wider for legibility is fine, anything else to scale
  (`docs/gm-rulings.md`, "The aqueduct's banks drawn 2 px wider for legibility are fine").
- ANSWERED 2026-11-26, 0181's share outside the wall: he accepts 2.8% as canon (`docs/gm-rulings.md`, "2.8% of a capital's
  row-house households live outside its wall").

## What landed overnight in 451 (tooling and the record)

- **T250**: the 351 attributions to the GM that no record backed are at 0 (ten batches; comments now point at his recorded
  words, name the file that holds them, or say whose rule it is; several misquotations corrected). The baseline
  `dev/gm-attribution-baseline.jsonl` stays as an EMPTY file on purpose.
- **T251** (the 10 claims), **T265** (the dedication knob relabeled UNRESEARCHED; the check accepts dated
  `rulings-YYYY-MM-DD.md` files), **T263** (a flaky guard test: its fixture), **T267** (claims-checked in a worktree).
- Page sessions P16, P17 and P18 (the canon fixes above; P18 also 0140's "provincial chancellors" and 0238's monks'
  funerary rites, from his recorded words), every owed check answered.
- Earlier the same day: T226-T249, T252-T259, T262 (see `git log` and `make task-time`).

## Open in 451, by kind (none blocks the talk)

- Found overnight: T264 (restated: probably nothing to change), T266 (comments count toward the page size cap; five pages
  within 20 bytes), T268-T273, T274 (memory sampler), T275 (`.git` state paths in a worktree), T276-T278, T279 (the restore's two rough edges),
  T280 (two footnotes that do not yet quote their line of his notes).
- T260: the audit register's backfill (254 mechanisms with no entry; `make audits` lists them), by cost order, small builders.
- T159: a fresh worktree's gate is red on one `rust/mode_a` test (missing gitignored renders) - every parallel builder meets it.
- The research backlog: `make research-backlog` (UNRESEARCHED decisions; the switch is open).
- Feature 455 (research beside the build) is the GM's to work; untouched.
- Stale, harmless: T251's archived plan section says T264 and T265 "land before T250" (T250 landed first; T265 has landed).
  The branch `backup/diagram-backlog-land` on GitHub holds one superseded ledger-row commit whose rows are on main.

## Records

- Measurements: `dev/measurements/2026-11-25/` (context cap, reversals, trials, task time, the talk's tables) and
  `dev/measurements/2026-11-26/` (builder count, build levers). Session records: `dev/session-records/c6fd72d1/`.
- The audit register: `dev/audits/` (`make audits`).

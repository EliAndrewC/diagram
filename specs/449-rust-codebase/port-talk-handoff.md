# Morning handoff: the talk before the port resumes (written 2026-11-26, overnight)

For the FRESH session that holds the talk with the GM (449 T437). Everything below is on GitHub `main`, and the tooling state is in its private repository (step 2). What does NOT outlive the
old container: the sessions' transcripts under `~/.claude/projects/` (the measurement scripts that read them keep their
result tables beside them in `dev/measurements/`) and the build caches. Read this, then `specs/449-rust-codebase/port-talk-agenda.md` (the 14 items with their measurements)
and `docs/process-decisions.md` (what is already decided, and declined, with the numbers and what would reopen each).

## To pick up in a new container

1. Clone into `/diagram/.clones/<session-name>` as `docs/session-clones.md` says; `scripts/sync-with-main.sh sync-in`.
2. `make state-restore` - the tooling state (event logs `make task-time` reads, handoffs, records) from the private
   `EliAndrewC/diagram-tooling-state` (never link or copy it anywhere public; the same for `EliAndrewC/diagram-research`).
3. `make switches` - the research switch is OPEN (the GM, 2026-11-25: "We can also handle those open research tasks
   overnight as well, whenever it is convenient."); the claims switch is at `report`.
4. `make speckit-todo`, `make audits` (the register, the overdue first), `make task-time SINCE=48h` (the task time breakdown).

## Where the port stands

- 449's pre-port tasks are all landed. Open in 449: **T437** (this talk - not a build task; it closes only with the GM's
  words), **T438** (the grove at each farm; waits for the homesteads port), T158 (the deletion close).
- The port has NOT resumed. Nothing in the engine was ported overnight. The next stage and the process for it are the talk's.

## What the talk decides (the GM's, not pre-approved)

- **The porting process itself**: how the next stages run, given what follows.
- **Item 8** worktrees against clones (measured: a clone 3.0 s and 615 MB, a worktree 2.2 s and 288 MB; builders already run
  in worktrees; what assumes a clone is in the agenda and in 451 T275's census of `.git` paths).
- **Item 10** long-running features against small ones; **item 11** whether everything must be a spec-kit feature
  (the measurements are under each item; the plan-gate cause was corrected - see the agenda, and 451 T261's withdrawal).
- **The terse output style** (declined so far; the GM's to reopen).
- **Extending the early build to the SPEC review** (constitution XVI would need his word; `docs/process-decisions.md`,
  "Building begins before a new feature's plan review returns").
- **A disk trade**: dropping the gate's coverage build at every landing frees about 65 GB for about 6 minutes a landing
  (declined under his pre-approval, his to take if the disk presses; `docs/process-decisions.md`, "Declined so far").

## Closed overnight under the GM's pre-approval of 2026-11-25

- **Item 6**: building begins while a feature's plan review runs (decided 2026-11-25).
- **Item 12**: the builders' context cap stays 300k, builders stay, briefs are sized (decided 2026-11-25).
- **Item 9, the disk and time levers**: none adopted - lighter debug info was already in (451 T246); incremental-off, a
  shared compiler cache and an eager drop of coverage builds declined on measurement; stale coverage variants are 451 T278.
- **Still open of the pre-approved set - items 1-5 and 7**: a PROVISIONAL working default, for the GM to confirm - two code
  builders at once in REUSED worktrees, three or four only for work that compiles nothing (that second rule is the session's
  addition, not in the pre-approval). Landed per wall hour 1.71 at one builder and 2.02 at two; three and four untested on
  comparable work. The pre-approval's memory condition is NOT met: memory was not measured, the container's limit is 10 GiB
  with no swap and its peak has touched it (451 T274 is the sampler). Items 2-5 and 7 have no measurement of their own.
- **Still open of the pre-approved set - item 14** (the builder report format; escalation-check on a narrower bundle; a
  Sonnet-tier seeded test): not measured overnight. Each closes with a Decided entry and an audit entry.

## The GM's canon answers (recorded in `docs/gm-rulings.md`), and what the record did with them

- 2026-11-26: Ryusei had no provincial lineages until the Lion/Unicorn war and has since acquired some (0138 and 0140 restated).
- 2026-11-26: burakumin neighborhoods stand inside a city's walls, at the edge. The search he asked for found a quarter inside the wall
  attested for China (Zhending 1551, Shaoxing) and outside by a gate elsewhere; Japan at the edge or beyond. 0156 and 0193 no
  longer call the placement a deviation; the siege reason is labeled the setting's own. The maps did not move.
- 2026-11-24 (not a new answer; applied overnight): a provincial city's 3,000 include the samurai country estates (0173
  restated by P16; 0001 and 0174 by P18).
- NOT an answer of his: 0142 now reasons the Emperor's granaries' siting from Imperial oversight, which his notes
  (`budgets.md`) state; the brigands reasoning was this project's writing.

## For the GM, small (each to pass `escalation-check` before it is put to him)

- 0141's aqueduct banks are drawn "darker and wider than life" as a labeled drawing convention; his true-size ruling says a
  feature that seems too small is raised with him. No record shows it was.
- 0181's "2.8% outside the wall" carries a setting-canon label with no recorded words.

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
  within 20 bytes), T268-T273, T274 (memory sampler), T275 (`.git` state paths in a worktree), T276-T278.
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

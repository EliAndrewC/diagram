# How we work, and why: the process decisions with their reasoning and numbers

**Load this file when:** you are about to change how work is organized - running builders, landings, claims rounds or page
sessions in parallel; clones against worktrees; starting work before a plan review is final; the tooling's run time;
long-running against small features; what must be a spec-kit feature - or the GM asks why we work the way we do, or
reopens one of these questions.

The GM, 2026-11-25: *"we also want to make sure that these decisions are stored somewhere that the next time we talk about
them, then it will be obvious to that new other session where it is that they can go in order to [look] up this reasoning
and measurement and such."*

Each decision is recorded here once it is made: the question, the GM's words deciding it, the measurements it rested on
(each dated, with its method and the command that reproduces it), the alternatives weighed, and what followed - a task
filed, a rule changed (where), or nothing and why. A later session that reopens a question starts from its entry and
re-measures with the same command before arguing for a change.

## Open: the talk before the port resumes (449 T437)

The questions raised by the GM on 2026-11-25 (fourteen that day), are listed with their context and the measurements each needs in
`specs/449-rust-codebase/port-talk-agenda.md`. The figures come from `make task-time` (the task time breakdown, 451
T243) and `make where-time`. When the talk decides an item, its entry moves here, and the agenda keeps one line pointing
at it. The fresh session that holds the talk starts from `specs/449-rust-codebase/port-talk-handoff.md` (what landed
overnight, what is closed under the pre-approval, what is the GM's to decide, how to restore a new container).

## The audit register (451 T259)

Every optimization or procedure that costs time or tokens has an entry under `dev/audits/` (one Markdown file each: what it is
for, the measurement that justified it with its date and command, its falsifier and threshold, its cost source in `make task-time`,
when it was last audited and its cadence). `make audits` lists them, the overdue first. A decision here that adds such a mechanism
adds its entry; the push refuses a new guard module, threshold constant, gate-chain target, landing step (a push check, a
`make land` phase, a landing gate script or one more first-pass refusal) or agent file without one. An option declined (the next section) gets a
`kind: declined` entry, its falsifier what would reopen it, audited on its cadence like the rest; the mechanisms in force that
no entry names yet are `make audits`' BACKFILL list (451 T260).

## Decisions NOT to do something are recorded the same way (the GM, 2026-11-25)

The GM: *"We should also make sure our processes record decisions about what NOT to implement for future reference in the
same way we record decisions about the processes and tooling we DO implement."* An option weighed and declined gets an entry
here like any decision: the question, the option, the GM's words or the measurement that declined it (dated, with its
reproducing command), and **what would reopen it** - the measurement or change that would make it worth doing (the declined
option's falsifier). A later session that wants the option starts from its entry and shows the reopening condition holds.
This file is loaded on demand, so a declined option recorded here costs no auto-loaded context (the user-level rule to drop
"we considered X" from auto-loaded docs still holds for those files).

### Declined so far

- **Raising the builders' context cap to 600k** (declined 2026-11-25 on measurement: across 61,271 builder turns since
  2026-11-19, time a wash at every size from 300k to 800k and tokens favoring the handoff, 33% fewer at 300k; method in
  specs/449-rust-codebase/port-talk-agenda.md item 12). Reopens if the handoffs' re-read minutes exceed the slow-turn minutes
  they save by more than noise AND tokens stop favoring the handoff.
- **A terse output style for the main session** (not adopted 2026-11-25: the main session is about 8% of output tokens, most of
  it reasoning, briefs and commands, and the GM likes the conversational style). Reopens if the main session's visible reply
  tokens become a significant share of the day's output.
- **Shallow clones** (not adopted 2026-11-25: a clone's git history is 404 MB; the disk was the build caches). Reopens if the
  object store grows past a gigabyte or so.

- **Three build levers for disk and time** (declined 2026-11-26 on measurement, the talk's item 9; the GM's pre-approval of
  2026-11-25 adopts a lever only where no build or test time is lost beyond noise). Measured on a worktree of main, 22 cores,
  the gate family (28 crates) and the guard family, cold and a one-file warm rebuild, median of 3:
  `dev/measurements/2026-11-26/build-levers/` (`m9-results.md` the table and each command, `m9-run.sh` the runner).
  - *Line-table debug info* in place of today's none (`rust/Cargo.toml` `[profile.dev] debug = 0`, 451 T246, already the
    lighter setting): cold +12-14%, warm +1-25%, target disk +76-114%. Reopens if a tool comes to need DWARF (coverage does
    not: it instruments).
  - *Incremental builds off* (`CARGO_INCREMENTAL=0`): target disk -81%, cold -5-9%, but a one-file rebuild 55 s to 363 s
    (gate) and 24 s to 100 s (guard). Reopens only for a tree that builds once and is thrown away.
  - *A shared compiler cache* (sccache 0.13.0, installed, unused): 0 hits of 18 cacheable calls in a fresh target directory
    after priming, cold +23%, no disk saved (guard family only). Reopens if a run shows hits across worktrees - why a fresh
    directory misses was not found.
  - *Dropping a tree's coverage build at each landing*: free for a worktree that ends at its landing (the sweep already takes a
    removed worktree's build directory, 451 T245); for a tree that lands again each drop costs a cold coverage build, up to
    512 s against 123 s warm, to free about 41 GB (the session clone) and 24 GB (the landing tree). Declined under the
    pre-approval; the trade - about 6 minutes a landing for about 65 GB - is the GM's if the disk presses again. What the
    measurement found instead: 20 of cover-gate's 21 GB of incremental data is stale variants (the sweep keeps 16 a crate,
    after 12 idle hours); pruning them sooner is 451 T278.

## Decided

### What counts as blocking time (decided 2026-11-25)

**Question.** The task time breakdown (451 T243) reports each kind of work twice: its minutes, and its BLOCKING minutes.
What makes a minute blocking?

**Decided** - the GM, 2026-11-25: *"a minute should count as blocking. When something else is waiting on it to be done before
it can be started. because that is a different standard than whether or not a different unrelated piece of work is able to be
done at the same time ... if we need to decide which of two implementations to perform, and then in order to do that, we must
perform research in order to know what is even correct, such that that research must complete prior to us beginning our
implementation work, then that research is blocking. And that research would be blocking even if there was a different
unrelated task happening in a different subagent at the same time."*

**Reasoning.** Two readings were tried and rejected the same day: a session's own idle waits summed (it booked a headless page
session's turns as blocking - 949 min, half the working time - and could exceed the clock), and the project's wall clock with
nothing working anywhere (it hides research a decision truly waits on whenever unrelated work runs elsewhere). Blocking is a
DEPENDENCY: work blocks a task when that task's next step waits on its result. Research run beside other work to clarify
wording or labels blocks nothing; research a choice of implementation waits on blocks that task.

**How it is measured.** The tooling cannot know the dependency from a make target, so the data carries a clue where the
session knows it: a `Blocks: <feature> T<n>` or `Blocks: none` line in a dispatch (builder, page-session brief, research pass,
review agent) and an `L7R_BLOCKS` variable on a make run; where none is given, stated defaults decide (a builder's foreground
command blocks its task; a background run only from when its task waits on it; a page session or research pass blocks
nothing unless its brief names a task). Accuracy of about 90% is enough - the GM: *"it doesn't have to be 100% exact ...
what we're looking for here is just a broad understanding of where our time goes when we are implementing tasks."*

**What followed.** 451 T243 builds it (`make task-time`); the builder brief and the page-session briefs carry the `Blocks:`
line. **Falsifier:** a sample of tasks read by hand where the booked blocking disagrees with what actually waited more than
about one time in ten - then the clues or the defaults are wrong.


### Building begins before a new feature's plan review returns (decided 2026-11-25)

**Question.** A spec-kit feature's plan review ran before any task started, and the session waited on it. May
the first task be built while it runs, once the spec review is FAITHFUL (the talk's item 6)?

**Decided** - adopted. The GM, 2026-11-25, raising it: *"if our plan review takes, let's say, 4 minutes, then we could probably
just do the first 4 minutes of implementation ... and then we can adjust ... maybe we will need to undo or change some aspects
... but that this will still save time"*; and pre-approving the item on its measurement: *"Yes I pre-approve the items in the
table above, so that you can close them out after implementing whatever the measurements say make sense."*

**Reasoning.** The wait buys nothing unless a plan review's verdict throws built work away, and it rarely does: three plan reviews in
four are CLEAR on their first round, and a BLOCKED round mostly asks for a measurement, for wording, or for code that builds on
what is there. The alternative weighed was the rule as it stood (no code before the reviews return), which pays the whole wait
every time to save a reversal about once in fourteen blocked rounds. What the reviews protect - nothing unreviewed is ticked or
reaches main - does not depend on when the code was written, so the review still gates the TICK and the landing.

**How it was measured.** 2026-11-25, a read-only pass over `dev/review-ledger.md`'s MODE 4 spec-fidelity rows since 2026-11-19,
the verdict files, the plan-done notes and the `plan.md` diffs (features 449 and 451): of 301 tasks with a task-level plan
review, 224 (74%) were CLEAR on the first round; of the 69 blocked tasks whose first BLOCKED round could be read, 6 asked for a
measurement, 13 for wording or form only, 45 for code that built on what was there, and 5 (about 7%; 451 T79, T186, T46, T102
and T197, each of low or medium confidence) reversed built work; 18 more could not be read, their verdict files overwritten.
The scripts and the table are `dev/measurements/2026-11-25/reversals/` (`summary.txt` the counts, `table.tsv` each blocked task's class). Its limit: these are task-level plan reviews, where the code already preceded the review; a
feature's first plan review is taken to behave alike, and the falsifier is what tests that.

**What followed.** The root `CLAUDE.md`'s "Development workflow" line and its full text in `docs/spec-kit-and-reviews.md` now say
a spec is reviewed before implementation, the plan review gates ticks and landings, and that once the spec is FAITHFUL a feature's first task may be BUILT while its plan review runs, the
builder adjusting to the verdict. No guard refused building before the review, so none changed: `scripts/gates/review-gate.sh`
refuses the PUSH, `make tick` and `scripts/gates/plan-gate.sh` the TICK, decide-first (`rust/guard/src/guards/pair_hooks/review.rs`)
holds a task's CHECKS and not its code, and the plan hold (`rust/guard/shared/src/checks/planhold.rs`) holds the plan block under
review and not the code. Open question for the GM: extending the early build to the SPEC review would amend constitution XVI ("reviewed against the GM's own words before
implementation begins") and needs his explicit word and a measurement of first spec reviews (ruled by spec-fidelity 2026-11-25). The audit entry is `dev/audits/building-before-review-clears.md`. **Falsifier:** on a later sample, the share
of BLOCKED rounds that reverse built work passing about one in five - then the wait is cheaper than the rework and the old
order comes back.

### The builders' context cap stays at 300k, builders stay, and briefs are sized (decided 2026-11-25)

**Question.** Builders kept hitting the 300k context cap and handing off, each handoff a fresh builder's re-read (the talk's
item 12). Raise the cap, drop builders for the coordinating session's own hands, or change what a builder is given?

**Decided** - the cap stays at 300k, builders stay, and a builder's brief is sized. The GM, 2026-11-25: *"Yes I pre-approve the
items in the table above, so that you can close them out after implementing whatever the measurements say make sense."* (item
12 as pre-approved: the cap stays at 300k; builders stay unless the coordinator doing the work itself costs fewer minutes and
tokens per landed task). Raising the cap to 600k is the declined entry above ("Declined so far").

**Reasoning.** The cap is not what costs: from 300k to 800k the time is a wash and the tokens favor the handoff, so a higher
cap buys nothing. What predicts a handoff is the size of the brief - the jobs in it, the files it will edit, a measurement at
its head - so the lever is the brief. And the coordinator's own hands are cheaper than a builder only for the smallest work: a
one-turn edit, and no further, because everything the coordinator writes is re-read on each of its later turns. So three
rules: one task a builder and at most three jobs a brief; a task past about three files or opening on a measurement split into
builders that hand results along, a measuring agent first; and a one-turn edit done by the coordinating session itself.

**How it was measured.** 2026-11-25. The cap: across 61,271 builder turns since 2026-11-19 (634 general-purpose builder
transcripts since 2026-11-18), time a wash at every context from 300k to 800k (within 2.5 min) and tokens favoring the handoff,
33% fewer at 300k and 62% fewer at 800k (`dev/measurements/2026-11-25/ctxcap/`). The brief (the M1 method,
`dev/measurements/2026-11-25/talk-measures/` `m1.py` and `m1b.py`: the 97 general-purpose builders dispatched since 2026-11-24,
each brief's jobs counted and its transcript read for a handoff - refused at the cap, a handoff written, or context at 290k or
more; 27 of the 97, 28%): a brief of 4 or more jobs handed off 52% of the time (12 of 23) against 16% at 1-2 jobs (4 of 25) and
22% at 3 (11 of 49); 4 to 8 files edited 39% and 9 or more 45%, against 22% at three or fewer; a brief that began with a measurement 46%
(6 of 13) against 25%. The coordinator (the same directory, `m2b.txt`): a one-turn edit costs about half a small builder's tokens, 0.3-0.4M against
0.65M with the brief and the report counted; past 5 minutes or several files it costs about 1.5M. Caveats: the six one-job
briefs handed off half the time (3 of 6), so the job count is a rule of thumb and not a law; the groups are
small; and whether builders beat no builders PER LANDED TASK - the condition in the pre-approval - is still unmeasured as
such (`dev/audits/delegating-to-builders.md` stays open, its three-way comparison owed), builders staying on the one-turn
figures alone.

**What followed.** `scripts/container/builder-brief.md` gained its SIZING rule, read before a brief is written, and the root
`CLAUDE.md` one line pointing at it. No guard: the rule is the coordinating session's judgment of a task's size, which a hook
cannot count without firing on correct work. The cap's guard and constant are unchanged. The audit entries are
`dev/audits/builder-brief-sizing.md` (new) and `dev/audits/builders-context-cap.md` (its measurement brought up to these
figures). **Falsifier:** over a week of builders briefed under the rule, measured by the M1 method, the handoff rate not
falling below about one in five (it was 28%) - then sizing the brief is not the lever, and the task's own size or the cap is
looked at again.

### Two code builders at once, in reused worktrees; three or four only for work that compiles nothing (decided 2026-11-26)

**Question.** How many builders run at once, each in its own worktree, landings still one at a time through main (the talk's
items 1-5 and 7)?

**Decided** - two code builders at once, in worktrees that are REUSED so their build caches are warm; three or four at once
only for batches that compile nothing (comment and doc edits, page work). The GM, 2026-11-25: *"Yes I pre-approve the items in
the table above, so that you can close them out after implementing whatever the measurements say make sense."* (items 1-5 and
7 as pre-approved: the standard count is the largest that the 1-4 test shows still shortens total time with peak memory under
a margin).

**Reasoning.** Two is the largest count the data supports, and only weakly: tasks landed per wall hour rose from 1.71 with one
builder to 2.02 with two (1.18x), while pace per builder was between level and 1.6x depending on the measure. Most of what a
builder lost at two was not the second builder but its fresh worktree - 21 of 22 code builders at two ran in a new, cold tree
against 1 of 16 at one - and contention itself was about 1.2x on a later closing-checks run. So the lever beside the count is
the warm tree. Three and four were not tested on comparable work (52 wall minutes, 8 of 10 builders on comment or doc edits),
so they are allowed only where nothing compiles. Memory is the unmeasured half of the pre-approval's condition: the container's
limit is 10 GiB with no swap (cgroup `memory.max`; `free` shows the host's 15 GB), `memory.peak` has touched it at some time in
30 hours with no OOM kill, and the peak during the 3- and 4-at-once runs was not recorded. Alternatives weighed: one at a time
(the queue is the cost: 385 of a day's minutes waiting on builders, the agenda's context) and three code builders as the
standard (untested, and unsafe to adopt blind against a 10 GiB limit).

**How it was measured.** 2026-11-26, read-only, over this session's builder dispatches from 2026-11-25 12:00 to 2026-11-26
06:10 UTC, each builder's concurrency taken from the other builders alive across its life, with the make targets' spans from the
guard's event log: `python3 dev/measurements/2026-11-26/builder-count/m1-concurrency.py -v` (the table and caveats:
`m1-results.md` beside it). Under load at two: hook suites 1.67x, rust lint 2.3x, rust test and coverage runs 1.27x; a
builder worktree's first closing-checks run 142 s against 62 s (one builder) and 76 s (two) for a later run. Caveats: small
groups; tasks differ in size; the one-builder baseline is 8 landings; both code builders at three ran a different model from
every builder at one; one builder alone in a fresh tree against one in a warm tree (the control that separates cold cache from
contention) was not run.

**What followed.** `scripts/container/builder-brief.md`'s SIZING paragraph names the count; the frictions of running several
were fixed by 451 T245-T247 and T252-T257, with T271 (shared scratch and plan-review bundle directory) open. A memory sampler
at dispatch is owed before any count is certified on memory (filed with this entry). The audit entry is
`dev/audits/parallel-builder-count.md`. **Falsifiers:** down to one - over the next 20 code tasks at two in warm trees, tasks
landed per wall hour at or under 1.71, or a later closing-checks run over 1.5x its one-builder median; up to three - a planned
run of six or more compile tasks at three landing more per wall hour than at two, pace per 10k output tokens within 15% of the
pace at two, and anonymous memory's peak at or under 7 GiB of the 10.

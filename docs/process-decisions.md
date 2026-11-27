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
`make land` phase, a landing gate script, one more first-pass refusal, or a script newly called from `make land`'s or
`make land-tooling`'s recipe or the push's scripts, 451 T269) or agent file without one. An option declined (the next section) gets a
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
  tokens become a significant share of the day's output. The GM, 2026-11-26: *"I affirm the
  decision to keep the current output style given how little it appears to matter."*
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
    pre-approval, and by the GM's own word, 2026-11-26: *"I agree that time is more important than disk space, and we
    definitely want those extra 6 minutes more than we want the 65G"*. Reopens only on his word.
  - THE PRINCIPLE, for every disk rule (the GM, 2026-11-26, on an idle cache the host session's scan had found): *"the guiding
    principle is still time saved is more important than disk usage. So we definitely don't want to clean things up if it is
    going to cost us time later."* A cache is evicted for being unreusable (its tree removed, its hashes no live build
    configuration can produce) or under real disk pressure (below 20% free), never for being idle (451 T278, T301). What the
    measurement found instead: 20 of cover-gate's 21 GB of incremental data is stale variants (the sweep keeps 16 a crate,
    after 12 idle hours); pruning them sooner is 451 T278.

- **Building the fix beside its reproduction** (declined 2026-11-26 on measurement; the GM's question that day: *"whether
  the tasks that we are looking at, where we have a known failure, are things where we already have enough information to be
  working on the fix ... while a different worktree is reproducing"*). Over 47 defect fixes of 2026-11-24..26 (42 builder
  chains; `dev/measurements/2026-11-26/split-reproduction/m16-results.md`, its scripts beside it): the diagnosis in the brief was
  confirmed in 18, narrowed or widened in 13, wrong in 8 and no defect in 3; the reproduction is 2 to 4 minutes of a 34-minute
  median; a split would have saved 4 to 38 wall minutes of 1,440 builder-minutes (0.3% to 2.6%) for about 480 extra
  builder-minutes, about 200 of them thrown away. A brief that states its cause as fact was still wrong one time in six; the
  15 tasks whose cause an earlier builder had measured were never wrong but had the least reproduction to skip. What the
  measurement found instead: 65% of builder-minutes fall after the fix is first written (the plan section, review rounds,
  checks, rework) - 451 T308. Reopens if reproduction comes to be a large share of a task (a class of defect that takes tens of
  minutes to reproduce) - then for that class only, and only where the cause is already measured.
- **The escalation check on Sonnet** (not adopted 2026-11-26 on its trial; the GM had pre-approved it *"if your measurements
  show that it is just as effective"*). By the project's model-trial method, four recorded drafts replayed three times a tier
  (`dev/measurements/2026-11-26/escalation-levers/m14-results.md`): Sonnet cut a question the recorded verdict had sent to the
  GM, and that he did answer (the aqueduct's banks), in 3 of 3 runs - the strict rule is no such miss - and it was not cheaper:
  2.7 times the input tokens and 2.7 times the seconds. Reopens on a new trial after the check itself is made steadier (next
  entry's finding), with drafts that hold several recorded CUTs.
- **The escalation check on a narrower bundle** (not adopted 2026-11-26 on the same trial; pre-approved *"if the metrics we
  gather demonstrate their effectiveness"*, the rule being that its verdicts do not change). Input fell 42% and 69% on the two
  drafts tried, and item rulings were no further from the recorded verdict than the full-repository control, but three catches
  the full runs made were lost in every bundle run (two of them gaps in how the bundle was built). Reopens with a bundle
  builder that takes whole heading sections and always includes the decision entry and the pre-approval paragraph, tried again.
  THE FINDING THAT MATTERS MORE, open for the GM: on its pinned tier the check agreed with its own recorded rulings on 53% of
  items across twelve replays and cut something the recorded verdict had sent to him in 5 of 12 runs - the filter that decides
  what reaches him varies run to run.
- **A merge driver for a feature's `tasks.md` and `plan.md`, and one file a task** (declined 2026-11-26 by the GM: *"every
  circumstance under which I would have multiple sessions running is one in which they would be working different features"*).
  Within one session `make carry` keeps both sides (451 T289); across sessions no two append to one feature's files. One file a
  task stays a question of how features are laid out, for the structural discussion, not of conflicts.
- **A session's own edits in a pool tree ("worktrees always")** (declined 2026-11-26, talked through with the GM): the rule is
  one writer a tree, not everything in a worktree - the clone is the session's tree and must exist as the place work is carried
  into and landed from; a tree for a one-line edit would add a handout, a carry and a release to the cheapest changes; the
  danger was two writers in one tree, which one writer a tree removes (451 T302). Reopens if the session's own edits come to
  collide with carries or gates in the clone.
- **Keeping a builder alive for follow-up** (declined 2026-11-26 by the GM: *"being able to close out builders as they
  complete has some advantages from a simplicity and design perspective. So I want to be wary of needing to keep them around for
  any reason"*): a later fix, a gate failure or even a design that proved wrong, goes to a fresh agent briefed from the plan
  section, the commit and the report. That day two fresh builders closed out others' work in 8 and 22 minutes while the
  originals had ended at 230k to 296k of their 300k. Reopens if a fresh builder is measured to cost markedly more than the
  original would have on a class of follow-up.
- **Five levers on a builder's test run** (declined 2026-11-26 on 451 T315's measurement; the session's reading, on the GM's
  standing rule that a lever is built where the numbers show it pays): the tests' temp files on an in-memory disk (at most
  0.3 s a run of the `land` crate, and the container's `/dev/shm` is `noexec`), an empty git template (under 0.02 s), a shared
  fixture repository copied per test (0.04 to 0.13 s), more test threads (already 22; no gain at 44) and a faster linker (under
  0.25 s of a build). Alone, a gate crate's tests run in 0.8 to 1.9 s and its build after a one-line edit in 0.8 to 2.9 s; the
  seconds a builder loses are elsewhere - a 2.3 to 4.0 s build waited up to 57.3 s for a build slot beside two builders (filed
  as T347), and the guard crates lose 5 to 7 s a run to a timer test, stray processes and the tool's own start (T339, T340,
  T341). This CORRECTS the session's earlier reading that the tests' own run time dominates a builder's test run. Reopens for
  a crate whose tests pass about 10 s alone with most of it in repository setup. Audit: `dev/audits/declined-test-run-levers.md`.

## Decided

### The builders' report has a fixed format (decided 2026-11-26)

**Question.** A builder's report enters the coordinating session's context and is re-read on every later turn (the talk's item
14). Would a fixed short format be shorter with nothing lost?

**Decided** - adopted: `scripts/container/builder-report-format.md`, read by a builder at its stop point. The GM, 2026-11-25:
*"Yes I pre-approve the items in the table above, so that you can close them out after implementing whatever the measurements
say make sense."* (item 14's report format, adopted if shorter with nothing lost), and 2026-11-26: *"The first two already
have my pre-approval if the metrics we gather demonstrate their effectiveness"*.

**Measurement** (2026-11-26, read-only over the coordinating session's transcript; `dev/measurements/2026-11-26/report-format/`,
`m14r-results.md` the tables, `m14r-reports.py` and the scripts beside it the method): 38 builder reports of 2026-11-25/26,
median 4,415 characters (about 1,100 tokens at four characters a token, uncalibrated), range 1,459 to 14,469 - the agenda's
"2k-5k tokens" was high. By what the session went on to USE: the state, what was built, the plan review's verdict and open
objections, candidates (16 of 19 filed) and caveats were used; the list of modified paths never was (0 of 32: `git add -u`),
nor a passing check's own line (0 of 26), nor "how to test" (0 of 5). Fourteen reports re-expressed in the format: the eight
longest came to 55% of their length, four typical to 69%, two short to 98%; no used item lost after one correction (a first
draft's six-row table cap lost rows the session had relayed to the GM, so the first table is kept whole). The saving is small:
each report is re-read over a median 204 turns, the 38 cost 2.0% of the session's input tokens, and the format saves about
0.74% of input raw, a tenth of that weighted for cached reads. Pasted into every brief it would cost about half its saving,
which is why it is one file read once.

**What followed.** The builder brief's "Then report" line points at the file. **Falsifier:** a report in the format from
which the session lacked something it needed (a successor's brief written without an objection, a file left out of a commit,
a candidate unfiled) - counted over the next twenty reports; one such loss in twenty reopens the capped fields.


### Two tiers of checking: a fast one in the builder's tree, the full gate once where work reaches main (TRIAL, from 2026-11-26)

**Question.** Where does the full rigor run - at a builder's tree, at the session clone, or where work reaches main?

**Adopted as a trial, round two of the worktree fixes** - the GM, 2026-11-26: *"we are undergoing extremely rigorous checks at
the point where a builder in a work tree is bending over backwards to make sure that absolutely nothing wrong can land in the
session clone, when in fact the correct place for that level of rigor is checking whether something in the session clone can
land back in the main checkout and in the main branch on GitHub"*; and, asked whether round two runs under it and at what
count: *"Yes, I agree that round two should run under two-tier checking as described. And yes, I agree that we should start it
at 3 builders with a batch of 4 if the first goes well."*

**The arrangement.** FIRST TIER, in a builder's pool tree: `make builder-checks CRATE="..."` - the changed crates' tests, lint
and format; a changed guard's own hook suite; no coverage build, no hook-suite fan-out. The builder ENDS at its report and is
not kept (*"being able to close out builders as they complete has some advantages from a simplicity and design perspective. So
I want to be wary of needing to keep them around for any reason"*). STAGING: `make carry` brings each finished commit into the
session clone, and `scripts/sync-with-main.sh backup` pushes the clone's head to `backup/<session>` after every carry, deleted
when its work lands on main (*"pushing to a `diagram-backlog` branch to ensure work is not lost"*). SECOND TIER: `make land`
over the batch - one full gate, one push. A gate failure is repaired in the clone by whoever is cheapest (the tooling for
format, the session or a small fresh agent for a lint finding or an uncovered line, a fresh builder briefed from the plan
section, the commit and the failure for anything larger). The plan review stays where it is.

**The second tier's threshold** (the GM: *"your suggestion for the threshold seems sensible for now"*): the gate runs when the
pipeline DRAINS - a batch of builders has reported and been carried in - with the next batch started beside it; always before
the session stops; and at a ceiling of about six tasks or ninety minutes staged without a gate (GUESS knobs). Reasoning: with
one session, waiting costs little that grows - the deferred checks name their file, repairs grow in step with the batch and do
not interact, and the one real cost, work standing only on this machine, is met by the backup branch - but there is nothing to
gain by waiting past a moment when the gate is free. With several sessions main moves under the staged work, and a gate that
runs continuously on a snapshot may be the better form (trial 458 weighs it; feature 459 is the several-sessions arrangement).

**REVERSED the same night - coverage stays in the second tier only.** The paragraph below records an amendment the session
made on its own reading and the GM then questioned: *"Why is a builder's closing step also running coverage? Like, isn't the
whole point of running coverage later that it's not really that much of a problem if we have a few coverage failures that we
have to fix later? I mean, our goal is not to minimize that happening. Our goal is to maximize task throughput."* The session
had decided on the wrong number: it counted batch gates that failed, where the goal is tasks through. By that goal the
amendment costs each builder 7 to 111 s on its own critical path (about a minute of a 17 to 35 minute run, on every builder),
to save repairs that block no builder: a failed batch gate delays the landing on main, while the builders go on from the
clone's HEAD, which already holds the carried work. What a gate failure does cost - a fixer's tokens and the session's turns -
was not measured against that minute, and is not throughput unless the session is the bottleneck, which was not shown. So:
the first tier is tests, lint and format, as adopted; a builder runs no coverage; 451 T381 is withdrawn. Reopens only on a
measurement that the repairs after a gate hold builders back (trees idle waiting on the session) by more than the coverage
step would cost them.

**The amendment as the session recorded it (reversed, kept for its figures): the builder's closing step also runs coverage on the crates it changed** (recorded 2026-11-26 by the
session, under the GM's standing pre-approval of what the measurements support - *"I thought I already pre-approved whatever
number and arrangement of parallel builders our measurements support"* covers the arrangement; this is the session's reading,
his to overturn). Under the first tier as first built, 4 of the first 9 batch gates failed on lines no test reached (an
assertion's message on a line of its own, a closure no fixture drove), each costing a fixer or a hand repair and a second gate,
5 to 15 minutes. From 21:40 UTC each builder's brief added `make crate-checks CRATE="<its crates>"` after its first tier was
green: 7 to 111 s a builder (a warm crate 7 to 28 s; eight crates 88.5 s), and the next 6 batch gates had no coverage failure
(T274, T334 with T339 and T336, T340, T347; two of those builders' own runs caught a line the gate would have). What the
batch gate still catches is what only integration shows: a field one task added that another task's test did not set, a
recipe a hook suite the first tier does not run refuses, a test that fails only beside four other crates' tests. DECLINED
with it: the first tier flagging a multi-line assertion message (T343's first half) - coverage names those lines and more.
Falsifier: a batch gate failing on an unreached line of a crate whose builder ran its coverage, twice in a week; or the
coverage step passing a median of 3 minutes a builder. Built into the brief's block by 451 T381.

**Measurement it rests on** (2026-11-26, one tier): the full checks ran twice a task (a builder's closing checks, two to four
runs, then the landing's gate); closing checks were 63% of a small task's builder clock
(`dev/measurements/2026-11-26/task-route/m11-results.md`); of a three-builder run's compile minutes coverage builds were 57.9
and coverage runs 19.8 against lint 33.2 and test builds 6.2, every memory and compiler peak falling where three trees were in
a coverage build at once (`dev/measurements/2026-11-26/builder-count/slot-coincide.py`); in round one (three warm builders,
one tier) five landing attempts failed on something other than the task landed. Two fresh builders that day closed out others'
work, coverage gaps among them, in 8 and 22 minutes.

**What followed.** `make builder-checks` (the Makefile); the builder brief's TWO TIERS paragraph; 451 T308 builds what the
trial shows is wanted; trial 458 reads the threshold again not before 2026-11-28. **Falsifier:** against round one - builder
minutes a task and tasks landed a wall hour no better, or gate failures a batch costing more to repair than the closing checks
they replaced, or a defect reaching main that a builder's closing checks would have caught.


### Clones for sessions, pooled worktrees for builders (decided 2026-11-26)

**Question.** Worktrees against clones as the working copies (the talk's item 8).

**Decided** - a session works in its own clone and its builders in worktrees of it, handed out from the standing pool (451
T285). The GM, 2026-11-26: *"For the work trees versus clones, then I agree with your findings and conclusions about keeping
clones for sessions and worktrees for builders"*.

**Reasoning and measurement.** 2026-11-25: a fresh `git clone` of /diagram took 3.0 s and 615 MB, a worktree 2.2 s and 288
MB with its history shared; a cold Rust build cache is 13-14 GB either way, which dwarfs both, so what matters is whether a
copy's cache is warm, not which kind of copy it is. Converting sessions to worktrees would be a large change to tooling keyed
on the clone (the session-clone guards, the sync script) for 300 MB and under a second. 2026-11-26: a warm pool tree's first
closing checks took 43 s and 165 s against 14 to 30 minutes in cold worktrees; a renamed worktree's cache goes cold (0.11 s
to 66.5 s), so trees keep their names.

**What followed.** The defects of tooling that assumed a clone are fixed as found (451 T254-T257, T267, T271) or filed (451
T159, T275, T281, T288, T295, T297). **Falsifier:** a class of worktree defect that cannot be fixed in the tooling at
reasonable cost, or the object store sharing causing a lost or corrupted commit - then builders move to clones of their own.


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

**The second tier's blocking (451 T298)** - the GM, 2026-11-26, on booking a batch landing apart: the second tier's blocking
minutes stand on their own line, expected near zero since no new task waits on the gate - a rise is the signal that something
has begun to wait on it (a carry behind a running gate, a repair, a build slot); the words are the task line's, relaying him. So a batch's gate in flight blocks nothing
while any task's own work in flight blocks that task, and nothing beside the session's own turn; it blocks the batch - no task -
where the session waits on it alone, where it ran in the foreground, and through a repair (the session's time from a task's
carry to the landing, and what that waited on). A builder whose brief says `Blocks: none` does not make a wait on the gate
any less a wait on it alone, and where a batch's own landing run is in flight the wait is booked to it - its gate, its push -
whatever else in flight ends later (another task's leftover background loop took 12.1 min of one batch's gate waits as `wait
loops` on 2026-11-26, the window from 17:00Z, before that rule). These are defaults like the others, a GUESS at about the same accuracy; a carry
held behind a running gate and a build slot the gate holds are not yet told apart (451 T319). The rule is
`rust/gate/crates/measure/src/measure/task_time/book/tier.rs`.

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

### A plan review's later rounds: what a script can see is refused at decide; the verdict stays on the whole section (decided 2026-11-26)

**Question.** Under two tiers nothing runs beside a plan review round, and more than half of the tasks took two or more. What is
each later round owed for, which causes can `make decide` refuse before a review is dispatched, and can a verdict be kept across a
section edit that changes no decision (a digest over the decisions rather than the section)?

**Decided** (feature 451 T308's plan-review part; the builder's, on the measurement, the plan review ruling on it). Built: decide
refuses the GM's words quoted on the task's own line of tasks.md that request.md does not hold, and two figure forms the lint did
not read (a `k`/`M`-suffixed count, "N-odd <unit>"); it says, with the dispatch, which later edits void the verdict - any edit of
a reviewed section not yet committed, a typo-scale one kept only once it is (proved by a test; the tolerance for an uncommitted
section is filed as 451 T337); the T55 order notice names `make builder-checks` to a builder. DECLINED: the digest over decisions, and "N of M" read as a count.

**Reasoning.** Of 56 later rounds (169 minutes), 26 were a real objection (78.6 minutes), the review doing its job; 16 followed an
edit after a CLEAR (31.5); 8 a NOT-REVIEWABLE return (40.6, and 20.6 more in the unreviewable rounds themselves); 4 an unfiled
found-and-left id (11.0; 8 rounds, 23.0 minutes, counting every round with that root, closed since by 451 T289); 2 a section edited while it was reviewed
(7.4). The mechanical share is the NOT-REVIEWABLE one: today's decide refused none of those sections. The digest over decisions
was declined because none of the 132 reviewed sections marks a decision in a form a script can read (no `**D<n> - ` line, no
Decisions block), so a kept verdict could cover a changed decision - the one thing the plan gate promises cannot happen - and
because it would have saved at most 5 rounds, 6.1 minutes (the touch-ups and the filed ids; 9 of the 16 were real changes). "N of
M" was declined on its replay: 47 unlabeled sentences in 26 of 124 reviewed sections, of which the reviews objected to 1. What
would reopen the digest: sections that mark their decisions, so a test can show a changed decision line voids the verdict.

The task-line refusal, replayed as built over the 77 tasks' first-round sections, refuses 11: 6 whose first review said his
words were missing, 3 whose words stood uncommitted in the builder's request.md (the replay's artifact) and 2 false refusals,
each cured by correcting the task line - accepted against a round of minutes for each of the 6.

**How it was measured.** 2026-11-26, from the coordinating session's `spec-fidelity` subagent transcripts for feature 451,
2026-11-24 to 26 (135 rounds over 79 units), each later round classed by hand from the round before it; each candidate rule replayed
over the sections those reviews read. The record, its scripts and every round's row: `dev/measurements/2026-11-26/plan-review-rounds/`
(`t308-results.md`).

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
cannot count without firing on correct work. Tightened 2026-11-26 on the GM's word ("go ahead and make whatever
tweaks you think are necessary there to the process of handing things off based on these measurements, findings, and
guesses"): a new guard or a new command is a builder of its own, and a brief of more than one job names the order and where to
stop. The day's figures: one of about fifteen builders reached the cap (the pool task, 307k, three jobs of that size) and one
ended at 296k (two), the rest at 122k to 174k - about 7% against the 28% before sizing; the two additions are a judgment from
those two cases, labeled GUESS, and trial 457 re-measures the rate. The cap's guard and constant are unchanged. The audit entries are
`dev/audits/builder-brief-sizing.md` (new) and `dev/audits/builders-context-cap.md` (its measurement brought up to these
figures). **Falsifier:** over a week of builders briefed under the rule, measured by the M1 method, the handoff rate not
falling below about one in five (it was 28%) - then sizing the brief is not the lever, and the task's own size or the cap is
looked at again.

**Amended 2026-11-27: a wrap-up band** (451 T417, T352). The GM: *"Does it make sense to enforce such an abrupt cutoff?  Like I
understand wanting to hand off to a new builder, but if our builders are prevented from even finishing their handoff, then is
that really the most efficient thing to do?"* The cap's figures above priced NEW work against a fresh builder; none looked at a
builder with a few mechanical commands left. The night's three cases, of about 35 builders: T315's (308k) could not dispatch its
plan review's second round and T325's (310k) could not run `make plan-delta`, `make claims-triage` or file the task it had found -
in both the coordinating session ran those steps - while T359's closing half (311k) had two code fixes owed, which a fresh builder
rightly took. So from the cap to a ceiling, `WRAP_UP_CEILING_TOKENS` (340k, a GUESS knob), a builder may run only its stop point's
own steps - `make decide`, `plan-delta`, `plan-verdict`, `claims-triage`, `claims-owed`, `task-add`, `task-withdraw`,
`builder-checks`, `git status` and `git diff`, a read, the one plan review's dispatch, and its handoff's Write - each recorded as
the guard's `wrap-up` rule; code and any other dispatch stay refused, the refusal saying what is left; past the ceiling the guard
is as before. The handoff's exit also takes the file the builder's brief names (`<task>-build.md`, `done-pending-<task>.md`), which
it refused before (T352). Still the cap at 300k: the band is for finishing, never for new work. **What would reopen it:** a builder
in the band spending more than a few turns there (the guard log's `wrap-up` passes, counted by agent), or a fresh builder
measured cheaper than the band for the same remaining steps; either is `dev/audits/builders-context-cap.md`'s second falsifier.

### Two code builders at once, in reused worktrees; three or four only for work that compiles nothing (decided 2026-11-26)

**Question.** How many builders run at once, each in its own worktree, landings still one at a time through main (the talk's
items 1-5 and 7)?

**Decided, and to be re-measured** - two code builders at once is what was measured to shorten total time, in worktrees
that are REUSED so their build caches are warm. The reuse is now the tooling's (451 T285): `make builder-tree` hands a builder a tree of the clone's standing pool, `make land` frees it with its cache in place, and a guard refuses a hand-made worktree and the removal of a pool tree or its cache. Two is NOT a memory cap (three fit; below) and not the conclusion: the GM,
2026-11-26, *"wouldn't it be better to address that with some synchronization rather than pre-emptively limiting builders just
in case?"* - so the count is re-measured at three and four once the warm pool (451 T285) and the build slot (451 T284) are in,
and the number recorded then is the largest that still shortens total time. Both halves of the
pre-approval's condition are measured: total time (below) and peak memory under a margin (the memory paragraph below). Three or four
at once only for batches that compile nothing (comment and doc edits, page work) is the arrangement beside it. The session
first recorded that second rule as outside the pre-approval; the GM, 2026-11-26: *"I thought I already pre-approved whatever number and arrangement of parallel builders our measurements support."* So the
arrangement is covered too, as far as the measurements support it - and for three or four they support it only weakly: on
2026-11-26 the comment batches ran three and four at once for 52 wall minutes with nothing failing and 2.44 tasks landed per
wall hour (three and four together, against 2.02 at two), on work not comparable to code tasks, with memory unsampled. It
stands on that, with its own falsifier below. Items 2-5 and 7 (a landing,
a claims round, a page session or a plan review beside the next build) were run this way through the night and are covered
by the same default; none has a measurement of its own. The GM, 2026-11-25: *"Yes I pre-approve the items in
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

Memory, measured 2026-11-26 12:39-13:19 UTC with two code builders compiling and testing the guard crate (451 T268 and
T272) and a landing's gate beside them for part of it, sampled every 10 s from the container's cgroup (236 samples,
`dev/measurements/2026-11-26/builder-count/mem-samples-two-builders.log`): anonymous memory median 1.9 GiB, 95th percentile
5.7, peak 6.3 GiB against the 10 GiB limit - no sample over the 7 GiB margin, no OOM kill, 4.4 s of memory stall in 40
minutes; `memory.current` reached 9.5 GiB, which is page cache and is given back. Load median 32 and peak 67 on 22 cores. Three
code builders were then run the same day (13:37-14:27 UTC; 451 T269, T270 and T271, each cold-compiling in a fresh worktree,
two landings' gates beside them; 292 samples, `mem-samples-three-builders.log` beside the other): anonymous memory median 2.5
GiB, peak 6.4 GiB - the same peak as two, no sample over 7, no OOM kill, 6.1 s of memory stall. The session had first
concluded, without running it, that a third builder would pass the margin; the run says otherwise: the peak follows how many
heavy compiles coincide, not the number of builders. Checked 2026-11-26 from `memory.stat` that anonymous is the in-use figure
here: shmem 0 (`/tmp` is on disk), unreclaimable slab 0; the rest of `memory.current` is page cache, which is given back.
What three builders do cost is PROCESSOR: load median 42 and peak 94 on 22 cores, up to 46 compilers at once, and a first
closing-checks run of 14 to 30 minutes in those cold trees (about a minute warm and alone).

ROUND ONE, three builders in WARM pool trees, one tier of checking, no build slot (2026-11-26, 451 T281, T284 and T295;
`mem-samples-round1-three-warm.log` beside the others, one sample every 10 s, 317 samples 15:43-16:36 UTC): over the 190
samples to 16:15, while all three builders were alive, anonymous memory median 1.1 GiB and peak 3.9 GiB, load median 16.0 and
peak 52.2, at most 22 compilers at once, no OOM kill, 15 s of memory stall; over the whole file the load median is 13.8 and
the anonymous median 1.0. A builder's first closing-checks run took 191 to 531 s and its final one 55 to 74 s. Against the
cold run above, warm trees roughly halved memory and load.

The build slot (451 T284, 2026-11-26; audited as `dev/audits/build-slot.md`). What coincides at those peaks was then read from
the same samples joined with the checks' `Phase` lines (`dev/measurements/2026-11-26/builder-count/slot-coincide.py`): all
twelve of the highest memory samples and seven of the eight highest compiler counts fell where all three trees were in a
COVERAGE BUILD at once, the machine ran three compiling steps at once for 1,396 of the run's 2,602 s, and one tree's own closing
checks never ran two compiling cargo calls at once. So each cargo call of the checks that compiles (a coverage build, a test
build, a `cargo test`, clippy, a stage's `cargo run`; not `cargo fmt`) now holds one of `L7R_BUILD_SLOTS` machine-wide slots
(`rust/gate/crates/rustc/src/rustc/slot.rs`: a `flock` under `~/.cache/l7r-build-slots/`, freed when its holder dies, no
daemon), a builder's checks and a landing's gate alike, and a wait is booked by `make task-time` as `waiting on a build slot`.
The count is 2, a GUESS: the third coinciding compile is the measured peak and added load, not throughput, on 22 cores. Chosen by
the building session under the GM's words above; not yet measured is whether it shortens three builders' closing checks, which
is the re-measurement this entry owes at three and four builders (falsifier: slot waits plus compile exceeding the unslotted
compile minutes, or closing checks at three builders no faster with it than at `L7R_BUILD_SLOTS=0`). Not covered: the wrapper's
own tool build and a hook suite's guard build, which were not at the peaks (at most 2.6 GiB and 13 compilers where no check's
phase ran).

The small lane (451 T347, 2026-11-26; the same audit). A test build the checks can tell compiles its crate alone - its
dependencies' files and their times unmoved since the same build last passed in that target directory - takes a lane of its
own, `L7R_BUILD_SLOTS_SMALL` wide (1, a GUESS: 0.19 to 1.42 GiB a build against the 1.6 GiB left beside two wide builds), and
never a wide slot: with both wide slots held it waited 60 s before and 1 to 2 ms after
(`dev/measurements/2026-11-26/small-build-memory/lane-results.md`). Chosen by the building session; the day's `waiting on a
build slot` minutes with the lane live are not yet read.

**What followed.** `scripts/container/builder-brief.md`'s SIZING paragraph names the count; the frictions of running several
were fixed by 451 T245-T247 and T252-T257, with T271 (shared scratch and plan-review bundle directory) open. 451 T274 keeps the sampler as
tooling (the first run was a hand-started loop): every `make builder-tree` starts the clone's sampler where none runs, and
`make sampler-report` gives a window's figures by the count of pool trees held (`dev/audits/memory-sampler.md`). The audit entry is
`dev/audits/parallel-builder-count.md`. **Falsifiers:** down to one - over the next 20 code tasks at two in warm trees, tasks
landed per wall hour at or under 1.71, or a later closing-checks run over 1.5x its one-builder median; up to three - a planned
run of six or more compile tasks at three landing more per wall hour than at two, pace per 10k output tokens within 15% of the
pace at two, and anonymous memory's peak at or under 7 GiB of the 10; three or four on non-compiling work - the next such
batch, sampled (451 T274), passing 7 GiB anonymous or landing no more per wall hour than two at once.

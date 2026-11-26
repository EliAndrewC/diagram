# Possibilities to discuss before resuming the port (the GM, 2026-11-25)

Not tasks: options to weigh at the talk, once 451 T243's task time breakdown gives the blocking minutes for each.
The GM: "record those 5 items as not as like a task to definitely be done, but as a set of possibilities to discuss as we
talk about the way forward."

Measured context (2026-11-25, `make where-time` F=449 and F=451 over 24 hours): the coordinating session waited 385 min on
agents, 251 on background commands, 148 on nothing; agents used 2,147 agent-minutes, builders and coordinators 1,692 of them
(79%), plan review 131 (6%), the round arbiter 24 (1%).


**Order (the GM, 2026-11-25: "should we move that item up to or near the front, so it can apply to all of the other
optimizations we're building at the moment?"):** item 13, the audit register, comes first and is built before the other
items' changes (451 T259), so each optimization arrives with its entry and falsifier. Its first entries: the builders'
context cap and handoff, delegating to builders at all, the disk budget and its trigger, the blocking definition, the research
switch, and the parallel-builder fixes (451 T254-T257).


**Pre-approved 2026-11-25 (the GM: "Yes I pre-approve the items in the table above, so that you can close them out after
implementing whatever the measurements say make sense."):** item 6 (adopt building a new feature's first task while its
reviews run - narrowed to the plan review by spec-fidelity's ruling, see item 6); items 1-5 and 7 (the standard builder count is the largest that the 1-4 test shows still shortens total time,
peak memory under a safety margin); item 9 and the disk levers (adopt each lever whose measurement shows no build or test time
lost beyond noise); item 12 (the cap stays at 300k; builders stay unless the coordinator doing the work itself costs fewer
minutes and tokens per landed task); item 14 (the builder report format if it shortens reports with nothing needed lost; the
escalation check's narrower bundle if its verdicts do not change). Each closes with its Decided: entry in
docs/process-decisions.md, and an option the measurement declines gets its declined entry there too.

1. Several builders at once, each in its own working copy (a worktree per builder), landings still one at a time through
   main. The largest: most of the 385 min waiting on agents was builders run one at a time, because two writers in one
   clone collided (2026-11-24 parallel builders; 2026-11-25 a landing beside a builder, 451 T242).
    Trial before the talk (the GM, 2026-11-25: "giving a try to what our new approach might be seems like something that
    would be good to do in advance of deciding whether or not to switch over ... if that works, then you can parallelize
    other things between now and then in the meantime to gather more data, and then we can decide whether to lock that in"):
    after 451 T244, T228 and T234 build side by side, each in its own worktree; recorded per trial - what broke (guards
    keyed on the clone's path, the started-task mark, landings of one feature back to back), a second copy's start cost (the
    cold build), and the wall clock saved; if it holds, the rest of the queue runs two or three at a time and adds data.
    Decided: 2026-11-26, on the GM's pre-approval - two code builders at once in reused worktrees (landed per hour 1.71 at
    one, 2.02 at two; memory at two with a landing beside them peaked at 6.3 GiB of the 10 GiB limit, no sample over 7; three code
    builders the same day peaked at 6.4 GiB, the same - memory does not cap the count, processor does); to be re-measured at
    three and four once the warm pool (451 T285) and the build slot (451 T284) are in; three or four for work that compiles nothing is covered by the same pre-approval (the GM, 2026-11-26) on
    weak measurement, re-measured at the next such batch; items 2-5 and 7 ran under the same default with no measurement of their own (`docs/process-decisions.md`, "Two code builders at
    once").
    Trial 1, measured 2026-11-25 (451 T228 and T234, one builder each in its own worktree, landed together as 4cd58860ab;
    the builders' logs were in the session scratchpad, summarized here): each builder about 44 min, side by side, against
    about 88 min one after the other - about 40 min of wall clock saved. Costs and frictions: a worktree in 2 s and 288 MB, but
    its own cold Rust build cache (first build 2-2.5 min, a cold coverage run about 9 min, 13-14 GB each within the trial);
    the started-task mark lives in the shared .git, so the second `make task-start` overwrote the first, and a push of the
    feature's other commits stayed refused while either task was in progress; the static-runs guard read the session's clone,
    not the worktree, and said the task changed no Rust crate (both builders used its escape); two gitignored map renders were
    missing in a fresh copy (a test failed until drawn); the pop-up checks' answer store is shared; both tasks edited 451's
    tasks.md Occasions block and plan-review.json, merged by hand in minutes. What would make it routine: per-worktree task
    marks, guards that read the tree they run in, a shared build cache, cleanup on landing (451 T245). Both worktrees and
    their caches were removed after landing.
    How many at once (the GM, 2026-11-25: "is the number 2 here something that was picked deliberately ... Presumably there is a
    point at which things like CPU contention or available RAM make it inadvisable to spin up additional parallelized threads
    ... doing some actual measurements on that is something that we should do as part of determining what our standard
    workflow should be"). Two was a default, held by disk (13-14 GB of build cache per copy). The machine on 2026-11-25 with
    two builders: 22 cores at a load of about 16, 15 GB of memory with about 9 GB available, 60 GB of disk free. CPU slows
    compiles when shared (one rustc ran at 900%); memory is the hard limit (an out-of-memory kill, not a slowdown); disk caps
    copies until 451 T245 or a shared build cache. Measure: comparable small tasks at 1, 2, 3 and 4 builders, each builder's
    minutes to its stop point and its compile and test minutes from the task time breakdown, peak memory and load; the count
    is where total time stops improving or memory nears a safety margin.
    Trials 2-5, measured 2026-11-25 (451 T235+T242, T245+T231, T227+T229, T232/T247/T246/T233, T248+T249: eleven tasks, two
    builders at a time, each in its own worktree, carried into the clone by cherry-pick and landed one at a time; all
    landed). New frictions beyond trial 1: the shared started-task mark refused a landing while the other task was started
    (worked around by moving the mark for each landing; a task builds fine without it); parallel builders filing tasks
    collided on task numbers twice (T247, T248 - renumbered by hand; builders now give titles and the coordinator files);
    every carry-over conflicted on plan-review.json (merged as JSON, both sides kept) and sometimes plan.md and request.md;
    plan reviewers recorded verdicts from the session clone instead of the worktree (brief now names the tree); closing
    checks run after a commit set a task's own lint red aside as another task's; one closing-checks test flaked with two
    runs side by side (451 T252); a worktree's fetch was logged into the session clone's attempts file; coverage-instrumented
    gate binaries dropped profraw files (fixed, 451 T247); disk peaked at 91% with two cold caches (fixed by 451 T245/T246,
    63% free at the end). What would make it routine, beyond trial 1's list: a mark per task, task numbers reserved by one
    writer, plan-review.json written per task (or merged by a tool), and the verdict's tree named in the review bundle.

2. A landing beside the next build: the landing's gate already runs in its own worktree; only its tick and push touch the
   clone (451 T242 fixes the late failure).
3. The claims round beside the next build, in its own copy.
4. Page sessions beside code builders: different files, serialized today only by the one clone.
5. Plan review beside closing checks inside a builder: start the closing checks, then dispatch the plan review while they
   run, instead of one after the other.
6. Implementation begun before the plan review is final (the GM: "if our plan review takes, let's say, 4 minutes, then we
   could probably just do the first 4 minutes of implementation ... and then we can adjust ... maybe we will need to undo or
   change some aspects ... but that this will still save time"). Measure first: how often a review's BLOCKED round changed
   the code direction (backed work out) versus asked for a measurement or wording, across 449 and 451's plan reviews; and
   which reviews block work today (a builder's closing plan review, which already follows the code, vs a spec-kit feature's
   spec and plan review before any task starts, and the decide-first guard, which holds the CHECKS, not the code).
   Measured 2026-11-25 (a read-only pass over dev/review-ledger.md's MODE 4 spec-fidelity rows since 2026-11-19, the verdict
   JSONs, plan-done notes and plan.md diffs; method and table in the session scratchpad, reversals/): of 301 tasks with a
   task-level plan review, 224 (74%) were CLEAR on the first round; of the 69 blocked tasks whose first BLOCKED round could be
   read, 6 asked for a measurement, 13 for wording or form only, 45 for code that built on what was there, and 5 (about 7%,
   all of low or medium confidence: 451 T79, T186, T46, T102, T197) reversed built work; 18 more could not be read (the
   verdict files are overwritten). So building before the review clears would rarely be thrown away.
   Decided 2026-11-25 (docs/process-decisions.md, "Building begins before a new feature's plan review returns"): adopted for
   the PLAN review, once the spec is FAITHFUL. Spec-fidelity ruled the GM's words and the measurement cover the plan review
   only; building during the SPEC review would amend constitution XVI and stays an open question for the GM.

Items 1-4 share one root: one writable clone per session (docs/session-clones.md).
7. Every other block that could overlap with the next round of work (the GM: "places where we currently block on things where
   we could begin the next round of whatever it is that we're doing in parallel to waiting for tests to run or things to
   compile"): from T243's blocking table, each blocking bucket over a threshold, and whether its waiter could start the next
   step meanwhile - in the same copy only where the next step touches no file the running step reads (no code edit under a
   compile), else in another copy.
8. Worktrees against clones (the GM: "perhaps work trees make more sense than clones ... all of our tooling kind of
   revolves around the fact that we are using clones ... at least take a look at the costs and benefits"). Known facts to
   start from: the project already uses one worktree, the landing worktree /diagram/.clones/diagram-backlog-land (make
   land's land-alone, 451 T55-era), and builders' replays use `git worktree add --detach`; a worktree shares the clone's
   object store and refs (cheap to make, no fetch) but also its stash, its hooks' view of "the clone", the session-clone
   guards keyed on the clone's path (clone_sync_hooks, main_tree_hooks), the cargo target dir per tree (a cold build each,
   unless shared - measure), and the .git/ state files the tooling keeps per clone (.git/l7r-events, page-sessions,
   closing-checks, handoffs). Price both: creation time, disk, the first build's time, and which guards and gates assume
   one writer per clone.
   Measured 2026-11-25: a fresh `git clone` of /diagram took 3.0 s and 615 MB; a worktree 2.2 s and 288 MB, its history
   shared; either way a cold Rust build cache is 13-14 GB, which dwarfs both - the choice that matters is whether copies share
   one build cache.
   Decided: 2026-11-26 - clones for sessions, pooled worktrees for builders (`docs/process-decisions.md`).

9. The tooling's own run time, every part of it (the GM: "whether there are additional improvements that we need to make to
   the time it takes for any of our tooling to run, whether that is compiling or running tests or generating maps or
   performing landings or performing git actions or our hooks ... in total, we do spend more than 50% of our time in our
   tooling ... the closer to free that we can make our tooling, the closer we are to literally doubling our throughput").
   From T243's per-target table: each make target and program ranked by blocking minutes, and for the top of the list what
   a faster version would take (caching, incremental runs, narrowing, a lighter hook path); git actions and the hooks'
   per-call cost included (the guard's event log times every hook). First check the premise against T243's figures: the
   share of blocking time in tooling versus model turns writing code.
    Measured 2026-11-25 (M4; tables in dev/measurements/2026-11-25/talk-measures/ALL-TABLES.txt): of 1,310 blocking minutes outside the GM's wait in 24 hours (task-time
    records, each minute assigned to one cause), tooling execution was 39%, model turns 45%, waiting 14% and review agents 2%.
    Top blocking targets: make closing-checks 105 min, make land 97, make rust-test 77; compile 145 as a category. The
    earlier "about 8%" read from a provisional run is superseded.
    Decided (the disk and time levers): 2026-11-26, on the GM's pre-approval - none adopted; lighter debug info was already
    in (451 T246), incremental-off, a shared compiler cache and an eager drop of coverage builds declined on measurement,
    stale coverage variants to be pruned sooner (451 T278) (`docs/process-decisions.md`, "Declined so far").
10. Long-running features against small spec-kit features filed and closed (the GM: "whether to have long-running features
    like the ones that we have been working for the last few weeks, or whether it is better to have small SpecKit features
    that get filed and then completely closed out ... there are real implications ... for which tooling gets run and what
    the review process is like ... wall clock time and also ... tokens and ... the amount of overhead"). Measure: what a
    feature's lifecycle costs per task in each shape - spec and plan reviews, the plan gate's stale blocks and their escapes
    (every landing today carried a PLAN_REVIEW_OK for 449's 17 moved tasks and unfilled sections), feature-report, archive
    moves, claims and record rounds keyed per feature - from 449 and 451's records against the small features in specs/.
    Measured 2026-11-25: see the M3 paragraph under item 11 (escapes per landing 1.85 in 449 and 1.13 in 451 against 0.0 in
    25 small features; plan reviews per task 0.83 and 1.51; tables in dev/measurements/2026-11-25/talk-measures/ALL-TABLES.txt).
11. Whether everything must go through a spec-kit feature (the GM: "I think on balance, this is probably for the best, but
    that is an assumption worth questioning ... whether there are categories of changes for which it would make sense to
    bypass those requirements ... tooling changes or minor bug fixes that we notice while working on something else ... if I
    had to guess ... adding a new task to a feature that we are already in the middle of is probably fairly low overhead").
    Start from the rule as written: the root CLAUDE.md already says "Feature work is a spec-kit feature ...; a tweak is done
    directly", and make land-tooling lands tooling alone; measure what a task added mid-feature costs (task-add, plan
    section, decide, spec-fidelity MODE 4, the landing) against a direct tweak, from today's 451 T226-T243.
    Measured 2026-11-25 (M3; tables in dev/measurements/2026-11-25/talk-measures/ALL-TABLES.txt): escapes per landing 1.85 in 449 and 1.13 in 451 against 0.0 in 25 small
    features. Of 636 plan-gate escapes since 2026-11-19, 60% were unfilled template sections of tasks filed and not started
    (451 T261 fixes that) and 31% were blocks reviewed CLEAR and touched since. Plan reviews per task: 0.83 and 1.51. A task
    added mid-feature (451 T226-T259, from the task-time records): median 57 machine minutes, 40 blocking minutes, 177
    minutes from filing to landing.
    CORRECTED 2026-11-26 (451 T261's builder, replaying 12 escape records at their commits with the push's scope): the
    60% counted the WORDING of the session's escape reasons, not what the gate held. Since 451 T84 the gate never counts an
    unstarted task's stub; in 7 of 12 replays feature 451 owed nothing and the escape was a standing reason; what the gate
    truly held was 449's 17 withdrawn tasks' edited, never-reviewed sections (34 blocks), three ticked tasks' untouched
    stubs and one renumbered block. So the per-landing escape counts stand, their cause does not; T261 is withdrawn, 451
    T262 refuses an escape the gate does not owe, and 449 T439 reviews the withdrawn sections.

12. A builder's context: handoff against compaction, and the cap itself (the GM: "I thought that we had done something to fix
    that issue with builders hitting their context limit ... our builder is not able to do automatic context compaction? Or
    would that not be the correct thing to do regardless?"). Today: 451 T12's guard stops a builder at 300k tokens of context
    (a GUESS knob, spec FR-006: past 400k a builder's calls ran 14.8 s per 1,000 output tokens against 11.9 s below, observed
    2026-11-19) and has it write a handoff; a fresh builder re-reads it, 10 to 20 minutes each. 451 T237 took the claims
    round out of builders; T432 and T243 still hit the cap on a large sweep or a large build. Measure: each handoff's cost
    (the fresh builder's minutes and tokens before its first new edit), how often builders hit the cap by task size, whether
    a subagent's automatic compaction is available in this harness and what it costs and loses (a summary drops the
    measurements and paths a handoff names), and the cap's own setting against T243's per-turn data.
    Measured 2026-11-25 (method and scripts: a read-only pass over the 634 general-purpose builder transcripts since
    2026-11-18, 61,271 turns since 11-19, context as rust/guard/shared/src/context.rs reads it; cache read 0.1x, cache write
    1.25x, output 5x fresh input, assumed): turn speed barely moves with context (7.3 s per 1,000 output tokens under 300k,
    7.8 over, total seconds over total tokens; medians 4 against 6-8); per-turn cost rises about 2.5x from 100k to 300k and
    1.6x more to 600k. Handoffs since 11-19: 135 with a successor, 107 at the cap; the fresh builder re-reads for a median
    3.7 min (p90 12.5) and 326k tokens before its first edit, 421 min in all, against about 215 min the old builder would
    have spent running slower - a net of about 205 min over six days. Break-even: time a wash at every context from 300k to
    800k (within 2.5 min); tokens favor the handoff everywhere, 33% less at 300k, 62% less at 800k. So raising the cap buys
    little time and costs tokens; the lever is the re-read (handoffs that name what to read; tasks sized to finish). Caveats:
    the band past 300k is small and survivor-biased (the guard refuses there), and long-context builders run the heaviest
    tasks. The session's recommendation to move the stop to 600k was withdrawn on these numbers.
    Measured 2026-11-25 (M1 and M2; tables in dev/measurements/2026-11-25/talk-measures/ALL-TABLES.txt): handoff rate by brief size - 16% at 1-2 jobs, 22% at 3 jobs and
    52% at 4 or more; 22% at 1-3 files edited, 39% at 4-8, 45% at 9 or more (builder transcripts since 11-19, grouped by the
    brief's job count and the files the builder edited). Past one in three, a builder hands off at 4 or more jobs, 4 or more
    files, about 120 tool calls or 80k output tokens. Arm (c), the coordinator editing directly: a one-turn edit costs about
    0.3-0.4M weighted tokens against 0.65M for a small builder and finishes in under a minute; past 5 minutes or several
    files it costs about 1.5M, where a builder's small context wins. Samples are unmatched (the tasks differ by arm).
    Three-way measurement (the GM, 2026-11-25: "we should make sure to measure whether the complexity of the handoffs actually saves time and/or tokens relative to either letting the builders grow or not using them in the first place"): three arms, each in minutes (blocking and total) and tokens per landed task, from the task time breakdown and the transcripts: (a) builders capped at 300k with handoffs (today's way); (b) builders let grow past the cap (no handoff); (c) no builders - the coordinating session builds in its own context. Arm (a) against (b) has a first measurement (2026-11-25: time a wash, tokens favor the handoff); arm (c) has none, and its cost lands on the coordinator's own context, re-read every turn. Also the handoff's own overhead: writing the handoff, the brief, the coordinator's reading of the report.
    Decided 2026-11-25 (docs/process-decisions.md, "The builders' context cap stays at 300k, builders stay, and briefs are
    sized"): the cap stays; builders stay; scripts/container/builder-brief.md carries the sizing rule (at most three jobs a
    brief, a split past about three files, one-turn edits the coordinating session's own).

13. An audit register for every optimization and procedure that costs time or tokens (the GM: "when we make this kind of
    optimization, then we should be documenting the logic behind it, the measurements that we took, and then also crucially
    what we would look at that would falsify the notion that this is a good idea ... a list of all of the auditable
    optimizations and processes and procedures, and then each one would know the last time that it was audited ... re-audit
    to see if they still make sense or if they need to be tweaked or redone or eliminated"). The session's proposal: one
    register (a file per entry, as the glossary keeps a file per term), each entry naming what it is for in outcomes, the
    measurement that justified it (dated, with the command that reproduces it), its FALSIFIER (the measurement that would
    show it costs more than it saves, and the threshold), its cost source in the task time breakdown, the date last audited
    and its cadence; `make audits` lists the overdue ones; a new guard, cap, gate step, mandatory check or procedure is
    refused without its entry (the way a guard is refused without its test companion), and each port stage's end audits the
    overdue entries. What warrants an entry: anything that runs on every task or blocks work - guards that refuse or
    re-route, caps and thresholds, gate and landing steps, mandatory review checks and their rounds, the builder split; not
    pure corrections that cost nothing (house-style rewriting). Backfill ordered by cost, from T243's per-target and per-hook
    minutes. The first entry is the builders' context cap, audited 2026-11-25 (item 12: time a wash, tokens favor it; the
    falsifier: re-read minutes past the slow-band minutes saved AND tokens no better).
    Finding the hidden ones (the GM: "some things are easy to identify as a measurable and auditable part of our tooling ...
    something like this limit on builder token window context size might not even show up as an optimization ... after the
    initial backfill, we can backfill as we go, as we find things that we missed"). The backfill enumerates from sources
    that hold rules, not only from make targets: every guard module and every numeric threshold in rust/guard and the gate
    (CAP_TOKENS, POLL_CHECK_S, the static-run limit, round caps); every rule line in the CLAUDE.md files and docs/ that
    tells a session to wait, serialize or always do a step ("one builder at a time", "foreground-regenerate only the
    motivating map"); the agent files' standing orders and the builder brief; and the escape log, where a rule escaped often
    is a rule fighting the work. Missed ones are added as found: a session that notices a rule costing it time or tokens
    files its entry with a first measurement.
14. The conversation's own token cost: the escalation check and the builders' reports (the GM, asking about the Stop hook's
    escalation-check firings and output styles, 2026-11-25). Measured 2026-11-25: 26 escalation-check runs over two days,
    1.85M tokens in (72% cached) and 79k out, about 70k in a run, about half of the day's visible firings on statements, not
    questions (451 T235); output tokens on 2026-11-25: subagents 5.6M, the main session 0.5M (about 8%, most of it reasoning,
    briefs and commands rather than replies). Levers: T235's fix and a mechanical pre-filter (only a sentence put to the GM,
    or an offer, reaches the agent); a narrower bundle for the check (the draft and the norm it cites); a cheaper tier for
    the check (by the 2026-09-19 tier ruling, rust/gate/crates/checks/src/checks/documents/agent_models.rs: escalation-check
    is pinned opus/medium and moves to sonnet if a seeded run on drafts with known findings catches them, as message-check,
    settlement-review and fix-check did); a terse output style (small: about 8%
    of output, the GM likes the conversational style); a fixed short report format for builders (their 2k-5k-token reports
    enter the coordinator's context, re-read every later turn).
    The GM, 2026-11-26: "For those three levers on the escalation cost, then yes, please go ahead and run them. The first two
    already have my pre-approval if the metrics we gather demonstrate their effectiveness, and I also pre-approve Sonnet if
    your measurements show that it is just as effective." The output style: "I affirm the decision to keep the current output
    style given how little it appears to matter."
    Decided (the builders' report format): 2026-11-26, adopted on its measurement - shorter (55% to 98% of fourteen reports'
    length) with no used item lost; the saving is small, under 1% of the session's input (`docs/process-decisions.md`).

## How each item closes (the GM, 2026-11-25) - its decision is recorded in `docs/process-decisions.md`

Every item above is decided in the talk and its decision captured with its logic, its reasoning and the numbers that support
it (the GM: "capture our logic and our reasoning and ideally the numbers that we gathered in order to support these
decisions, not only for this specific item, but for also all of the other 9 items"): under each item, a `Decided:` line
with the GM's words, the measurements it rested on (each dated, with its method), and what follows - a task filed (its
number), a rule changed (where), or nothing, and why.

Once an item is decided, its entry (question, decision, reasoning, numbers and what followed) is written into
`docs/process-decisions.md`, the one place a later session looks; this agenda keeps a line pointing at it.

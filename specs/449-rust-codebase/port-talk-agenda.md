# Possibilities to discuss before resuming the port (the GM, 2026-11-25)

Not tasks: options to weigh at the talk, once 451 T243's task time breakdown gives the blocking minutes for each.
The GM: "record those 5 items as not as like a task to definitely be done, but as a set of possibilities to discuss as we
talk about the way forward."

Measured context (2026-11-25, `make where-time` F=449 and F=451 over 24 hours): the coordinating session waited 385 min on
agents, 251 on background commands, 148 on nothing; agents used 2,147 agent-minutes, builders and coordinators 1,692 of them
(79%), plan review 131 (6%), the round arbiter 24 (1%).

1. Several builders at once, each in its own working copy (a worktree per builder), landings still one at a time through
   main. The largest: most of the 385 min waiting on agents was builders run one at a time, because two writers in one
   clone collided (2026-11-24 parallel builders; 2026-11-25 a landing beside a builder, 451 T242).
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
9. The tooling's own run time, every part of it (the GM: "whether there are additional improvements that we need to make to
   the time it takes for any of our tooling to run, whether that is compiling or running tests or generating maps or
   performing landings or performing git actions or our hooks ... in total, we do spend more than 50% of our time in our
   tooling ... the closer to free that we can make our tooling, the closer we are to literally doubling our throughput").
   From T243's per-target table: each make target and program ranked by blocking minutes, and for the top of the list what
   a faster version would take (caching, incremental runs, narrowing, a lighter hook path); git actions and the hooks'
   per-call cost included (the guard's event log times every hook). First check the premise against T243's figures: the
   share of blocking time in tooling versus model turns writing code.
10. Long-running features against small spec-kit features filed and closed (the GM: "whether to have long-running features
    like the ones that we have been working for the last few weeks, or whether it is better to have small SpecKit features
    that get filed and then completely closed out ... there are real implications ... for which tooling gets run and what
    the review process is like ... wall clock time and also ... tokens and ... the amount of overhead"). Measure: what a
    feature's lifecycle costs per task in each shape - spec and plan reviews, the plan gate's stale blocks and their escapes
    (every landing today carried a PLAN_REVIEW_OK for 449's 17 moved tasks and unfilled sections), feature-report, archive
    moves, claims and record rounds keyed per feature - from 449 and 451's records against the small features in specs/.
11. Whether everything must go through a spec-kit feature (the GM: "I think on balance, this is probably for the best, but
    that is an assumption worth questioning ... whether there are categories of changes for which it would make sense to
    bypass those requirements ... tooling changes or minor bug fixes that we notice while working on something else ... if I
    had to guess ... adding a new task to a feature that we are already in the middle of is probably fairly low overhead").
    Start from the rule as written: the root CLAUDE.md already says "Feature work is a spec-kit feature ...; a tweak is done
    directly", and make land-tooling lands tooling alone; measure what a task added mid-feature costs (task-add, plan
    section, decide, spec-fidelity MODE 4, the landing) against a direct tweak, from today's 451 T226-T243.

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

## How each item closes (the GM, 2026-11-25) - its decision is recorded in `docs/process-decisions.md`

Every item above is decided in the talk and its decision captured with its logic, its reasoning and the numbers that support
it (the GM: "capture our logic and our reasoning and ideally the numbers that we gathered in order to support these
decisions, not only for this specific item, but for also all of the other 9 items"): under each item, a `Decided:` line
with the GM's words, the measurements it rested on (each dated, with its method), and what follows - a task filed (its
number), a rule changed (where), or nothing, and why.

Once an item is decided, its entry (question, decision, reasoning, numbers and what followed) is written into
`docs/process-decisions.md`, the one place a later session looks; this agenda keeps a line pointing at it.

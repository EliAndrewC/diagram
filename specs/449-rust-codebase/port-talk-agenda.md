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

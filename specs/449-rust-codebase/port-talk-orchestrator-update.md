# Orchestrator: what the night measured, and what current practice says (2026-11-27)

A plain note for the talk, beside `port-talk-orchestrator-research.md` (2026-11-26, its options and sources). Written by the
coordinating session from two read-only agents' reports of 2026-11-27: one measured the night's records, one rechecked that note's
quotes (all hold word for word) and read what it had left unread. Their full reports are in the session's scratchpad
(`orchestrator-measured.md`, `orchestrator-sources.md`); nothing here went through the research record's checks, by the GM's word
("I'm not expecting you to do all of the adversarial subagent checks on your summaries or have citations").

## What the night measured (2026-11-27, 02:00Z to 15:00Z)

- **Carries:** 93 builder commits; 15 (16%) stopped on a real conflict and were resolved by the coordinator by hand, 8 of them in
  `plan.md`, the rest in `tasks.md`, `plan-review.json`, `dev/guard-messages.tsv`, a hook suite and a few Rust files.
- **Landing attempts:** 50, of which 18 landed. 19 were refused before a gate ran (plan review owed 6, audit entry 5, tripwire 4,
  ledger row 3, unclear 2); 10 gates went red (coverage 6, hook suites 4, a failing unit test 3, the regex-scan check 2 - some
  red for more than one); 3 passed the gate and were refused at the tick. The 63-task batch took 14 attempts over about 5 hours.
  The causes are partly inferred: several attempts overwrote one log.
- **The integration lane:** a landing ran in the clone 44% of the window (344 of 780 min), the full gate 20% of it; 74% of the
  lane's busy minutes were attempts that did not land. A builder's finished commit waited a median 4.7 min to be carried, at most
  170 (the 63-task batch's hours).
- **The pool trees:** busy 93%, 98% and 83% of the window (t269, t270, t271); b1 idle from 10:20 (the three-builder knob).
- **Blocking (`make task-time`):** 568 of 680 working blocking minutes were the second tier - the coordinator's own turns, foreground
  repairs and waits on landings - not builders waiting. T510 (in flight) splits the report so the two have their own denominators.
- **Tokens:** builders 4.88M output and 1,026M cache-read tokens over 105 transcripts; the coordinator 0.58M output and 616M
  cache-read over 1,007 calls; review and check agents 1.1M output. The coordinator's context ran 540k to 966k tokens a call, grew
  about 100k an hour, and was summarized once (06:32Z). A landed batch cost the coordinator a median 15k output tokens between
  landings; the 63-task batch alone 279k output over 484 calls.

## What current practice says (sources in the two notes)

- **The lead plans and dispatches; it does not do the integration work.** Anthropic's research system: a waiting lead means "the
  entire system can be blocked while waiting for a single subagent". Cursor built an integrator and dropped it: "it created more
  bottlenecks than it solved. Workers were already capable of handling conflicts themselves."
- **Merge queues eject a failing change and its author repairs it** (Mergify, bors, Chromium's commit queue). No source gives a
  repair time; none has the queue itself repair.
- **Token cost:** Claude Code's docs - "running ten agents in parallel uses quota roughly ten times as fast as running one"; a
  subagent's first request does not read the parent's cache; the main conversation's cache lasts an hour on a subscription. Fowler:
  a coordinator's status check pulled a worker's raw transcript into its context, and every later turn carried it. One practitioner:
  about 1.5x the tokens for about 4x the speed with three builders and one coordinator.

## The session's reading (not the sources')

1. The night's cost was integration in one actor: the coordinator carried, merged, repaired and fixed refusals in its own tree and
   turns, so its context grew about 100k tokens an hour and every turn re-read it. Practice says move that out of the lead.
2. The lane was busy mostly with attempts that failed. Batches that waited grew; a large batch met more refusals and more reds. Smaller
   batches landed more often on the first try (after 10:00Z, typically first or second).
3. Most refusals were bookkeeping a tool could have produced up front (audit entries, ledger rows, plan reviews of moved stubs).
4. 16% of carries conflicted, mostly in the plan; the merge-by-heading and the review record's driver resolved most, but each
   remaining one cost a coordinator turn.
5. Options worth weighing, from both notes: the coordinator dispatches only; carrying and the batch gate run as tooling in a landing
   tree of their own; a red change goes back to the builder (which must commit before it ends) rather than to the coordinator; a
   fresh integration agent per batch if judgment is needed, not a standing one (one more long-lived context is the cost to avoid).

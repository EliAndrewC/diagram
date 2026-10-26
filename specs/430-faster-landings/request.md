# The GM's request (verbatim), 2026-10-26

## The question

> Yes, I approve that, so please mark that as having been reviewed. And then, yes, I would like to review the landing costs next, because it sounds like that is still a significant cost that we need to fix before we move on in order to be able to address other things more efficiently. So what do you suggest? What review agents are we currently running at landing, and which of them do you think we could skip or make more efficient or change from being review agents to being a mechanical check, etc? what in general do you think would make things faster with either no cost to fidelity or an acceptable minimum cost to fidelity?

> Oh, also, since we're talking about landing, is it still the case that doing a push takes 10 seconds? I remember that was true at one point, and that surprised me and leads me to believe that something about the way that we're doing things in Git is inefficient and that we might need to clean up our Git history or something.

## The approval

> Please file all 7 as one feature and then work all of them start to finish. Thank you.

"All 7" are the session's proposals, in its reply's order:

1. Keep the gate incremental when only pool maps change: run just the tests that read them (`pool-readers.py` already finds those for `make quick`).
2. A doc file under `tests/` triggers nothing; a fixture change runs only its own directory's tests.
3. A fast coverage check on the changed modules, measured the way the full floor measures them, before the 4-5 minute gate (after confirming whether today's `cover-changed` actually missed those lines).
4. The push's checks exit at once when the delta touches nothing they judge, cache their answer for an unchanged delta, and run in parallel.
5. A plan-lint before any plan review (figure labels, red exit, approach block present); skip spec-fidelity for an approach block that matches the template and decides nothing, as already done for part B notes.
6. Accept a "known" departure (its claim names the open task carrying the fix) without an arbiter round, and list it for the GM's review; skip claims-triage for bundles of a few claims.
7. Run the claims triage beside the plan review instead of after it.

The measurements behind them (observed 2026-10-26, method: `dev/run-log/2026-10/20261026*.json` and `dev/review-ledger.md`,
checked by escalation-check): 24 `make done` runs, 101 min, 9 red (49 min), 6 of the 9 on the coverage floor; 21 full and 3
incremental - 11 full only because `pool/hamlets/inashiro/inashiro.json` changed, 8 for a non-module file under `tests/`;
incremental runs 38-149 s, full 126-688 s. Review passes: spec-fidelity 19 (52 min), its verify 6 (11 min), impl-drift 11
(12.5 min), escalation-check 4 (4 min). A records-only push 10.9 s: `claims-gate.sh` 5.7 s, `entry-gate.sh` 2.3 s,
`cohort-gate.sh` 8.8 s on engine landings; a GitHub round trip 0.19 s.

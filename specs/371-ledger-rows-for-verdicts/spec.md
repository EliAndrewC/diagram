# Feature 371: a ledger row for every recorded review verdict

**Status**: Filed (2026-10-09, by feature 328's session) - not started.

## What and why

Every review pass is owed a row of `dev/review-ledger.md`'s measured table with its cost (`docs/reviews.md`, feature 294),
but nothing checks it. Feature 328 ran 26 glyph checks across its batches 2-4 (2026-10-08/09) and wrote none of their rows;
they were found missing at batch 5's close and backfilled by hand from the agents' transcripts and `make review-cost`. The
verdict each check writes (`make review-verdict` -> `scripts/reviews/review_prereq.py` `verdict_dir/<unit>.json`) is the
record a guard can read - but it holds only the unit's LATEST round, so a round overwritten before its row is written is lost.

## Sketch

1. `review-verdict` appends each record (unit, verdict, engine key, gate, time, agent id when known) to an append-only
   `.git/review-verdicts.jsonl` beside the per-unit file.
2. `ledger-hooks.sh` (or `make quick`) lists every verdict in that log with no ledger row naming its unit and date, and prints
   the row to add with its cost from `make review-cost AGENT=<id>`, so a session pastes it rather than reconstructs it.
3. A test proves the check fires on a verdict with no row (deleted, the test goes red).

## Done when

A recorded verdict with no ledger row is reported at the commit that should carry it, with the row to add.

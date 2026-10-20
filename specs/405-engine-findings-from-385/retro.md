# Retros - feature 405

One row per closed task.

## T12 - the retro row

The first round of FR-004: one claim, through the whole route. The fix was two deleted loops: `_trim_to_service` now walks
every end in 4 ft at a time instead of popping a whole last segment first. Its test was red at HEAD (the end stopped at
(450, 0), 50 ft short of the house); the ways package (574 tests) and the cohort (16/16) were green. The process around it
cost more than the fix did. The feature had never had its spec reviewed (two rounds, the first CHANGES REQUIRED: today's
scope, a miscount, 63 unfiled findings), the first plan review stopped without a verdict because 405 had no request.md, the
claims round named an UNCLAIMED rule in the same function that the gate would refuse (a second impl-drift round on the new
claim), and five tooling or record findings were filed rather than worked (T28-T31 and the found.jsonl rows). **The habit it
changes:** none yet; the numbers go to the GM before a second task starts.

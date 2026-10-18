# T08 - two red gates (2026-10-18)

1. **16:39Z** (`dev/run-log/2026-10/20261018T163918500495-565938.json`): `tests/gate/test_review_rules_294.py::test_every_see_through_mark_is_declared`
   on Inashiro and Mizuguchi - the new pond-bank tree drawn at 0.92 opacity and declared nowhere in `settlement/see_through.py`.
   Fixed by drawing the crown solid (a tree reads solid; the table is for marks meant to be faint); the two maps re-rolled, the
   test file green (32 passed).
2. **16:44:54Z** (`.../20261018T164454209276-582368.json`): coverage - `hamletgen/pondbank.py` line 97 (the drawer's early return
   for a planted bank with no free seat) unreached on the hamlet path, every pool and cohort bank having every seat free. Fixed
   by a unit test (`test_a_planted_bank_with_no_free_seat_draws_nothing`, 7 passed). Every other phase of that gate was green.
3. **16:45:47Z** (`.../20261018T164547353413-586333.json`, 2 s, "failed: tree moved"): not a gate - my `make done --dry-run`,
   typed to find the tripwire's trigger name, recorded a red run. A dry run should record nothing.

Two different causes, each fixed once; no edit made and unmade. Next: one gate on the stable tree.

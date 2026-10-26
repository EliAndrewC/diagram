# Research - feature 432

## R3 - the price of clearing triage-owed claims mechanically (T05, FR-005 a, D7)

- **Finding** (`m:triage-price`): over every commit that changed `dev/claims-index.json` from 2026-10-04 to 2026-10-26, a claim
  whose code stood and whose cited page moved was re-judged 6,419 times. In 5,304 the blocks it rests on stood (the TRIAGE
  route): 5,297 kept their verdict, and 7 became a finding - 4 DRIFTED, 3 MISLABELED, on 6 claims (a polder claim twice):
  `ways/bund.py::RUN_ON_REACH_FT`, `ways/geom.py::_trim_to_service`, `ways/settle.py::settle_street_ends`,
  `ways/sweeps.py::_sweep_dangling_ends`, `homesteads/wells.py::shared_row_wells`, `water/polder.py::polder_crossing_caps`.
  In 1,115 a rested-on block moved (the route D7 keeps): 66 became a finding.
- **So** the mechanical clearing would have let 7 findings in 5,304 through (0.13%) - about one finding in 760 triage-route
  re-checks, each a claim whose cited page gained a passage that bore on it without the passage it rests on changing - and
  saved the triage of all 5,304 (one agent per page edit, the 0081 edit's 217 claims among them).
- **Method**: `python3 specs/432-gm-review-signal/measure/triage_price.py` - each commit against its first parent, a claim's
  `code`, `pages` and `rests` compared; the triage route is `pages` changed with `rests` the same.
- **The 0081 edit (385#0), before and after** (observed 2026-10-26, method: today's `dev/claims-index.json`, the claims whose
  `pages` name page 0081 and whether each has `rests`): 271 claims cite 0081 today, 236 with the blocks they rest on recorded and
  35 without. Before this change a two-bullet edit off every rested-on block owed all of them one triage (217 on 2026-10-17);
  after it, the 236 are cleared mechanically and only the 35 with no `rests` are triaged - a triage of 35 claims in place of 271.
  A claim whose rested-on block the edit changed is owed impl-drift on either rule.
- **Ruled**: the round arbiter, `ask:432-t05-triage-price`, 2026-10-26: the price is not material - the clearing removes 83% of
  the re-checks and forgoes 10% of the findings, a yield of 0.13% on the cleared route against 5.9% on the kept one; land it as
  specified, the cleared claims recorded as such (each row's `cleared`), where a later sweep would sample them.

## R2 - the pop-up cascade the audit named (T04, FR-005 b, D6)

- **Finding** (observed 2026-10-26, method: the 2026-10-13 rows of `dev/review-ledger.md` for modal-form, modal-research,
  modal-depiction and quote-check naming a bamboo, shelter or grove pop-up): 47 checks on 9 choice pop-ups and 2 hamlet
  pop-ups of 374's batch 17. 18 of them were a second or later round, and 15 of those 18 still found something
  (`ACCURACY 1`, `TRUTH 2`, a `FIX`); the rounds tracked real findings, as the arbiter's hour-2 ruling said ("The checks did
  catch real errors").
- **Finding** (observed 2026-10-26, method: every `l7r/diagram/interactive/assets/modals/**/*.md`, split at blank lines,
  paragraphs over 80 characters compared): of 293 pop-up files, 17 paragraphs appear in 2 or more, 51 placements in all, and
  none of them in the bamboo, shelter or grove family. The premise behind E(b) - that the batch re-checked one shared paragraph
  pop-up by pop-up - is not what happened: each pop-up has its own text, and its three checks each judged it.
- **So** FR-005 (b) as filed (a shared paragraph checked once) would cover 51 placements of 17 paragraphs across the whole
  registry and none of the batch that prompted it.
- **SC-004's pop-up half** (from R2's counts): before and after identical - nothing built; the premise false for 374#81.
  Ruled by the round arbiter, `ask:432-t04-shared-paragraphs`, 2026-10-26: FR-005 (b) waived, T04 closed on R2.

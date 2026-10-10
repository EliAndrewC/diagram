# Feature Specification: MEASURE feature 274's write cap and line reads on the groups that run after it landed (owed by 274 FR-004)

**Status**: Done 2026-10-10 - the table and the verdict are `specs/274-leaner-research-sessions/research.md` R3, from `measure/run_all.sh` (its output `measure/results.txt`) and `measure/cap.py` (`measure/cap.txt`); the follow-up it found is filed as feature 376. Filed from future-work/cross-cutting.md, "MEASURE feature 274's write cap and line reads on the groups that run after it landed (owed by 274 FR-004)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: research process

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

Feature 274 capped a research WRITE session at four questions and ten new registry keys (the runner and
`make reserve`), and moved coordination files to `make lines` / `make append`. Neither can be measured before
groups run under it, so the measurement is owed here. **Method**: `specs/274-leaner-research-sessions/measure/`
- `collect.py` (edit its `CLONES` list to the clones that ran, and keep only sessions whose first record is after the
landing commit's time - it has no cut-off of its own) writes `sessions.json` from the transcripts listed in each
clone's `.git/page-sessions/index.txt`, folded per message id as 250's `tokens.py` folds them; `analyze.py` prints the per-group table in
the shape of `groups-table.txt`; `decomp.py` splits the main context into floor, reads and tool results. Take every
complete group started after the landing. **The figures to beat** (274's research R1, 282 sessions in 65 groups
before it): per thing checked a median of 1.02 M (IQR 0.86-1.20); the largest context of any turn 246 K; write
sessions a median of 74 turns (mean turn 147 K, peak 237 K); about 60 M carried by whole reads of coordination
files. **Expected**: write sessions under ~40 turns, the peak back inside 250's 102-171 K band, per-thing cost
10-20% lower, and coordination reads near zero - and `grep continued .git/page-sessions/run-*.log` says how often the
key cap split a session. A continuation brief sits at `.git/page-sessions/<sid>/continue.md`, which `collect.py`'s `specs/NNN-` match does not read: attribute it to its parent's group through the run log's `continued <sid> -> <sid>` line. Close this entry with the table and the verdict in 274's research.md as R3.

## Decisions Recorded

- **The comparable groups** (deliberate deviation, stated): the entry says "take every complete group started after
  the landing". R3 reports that row, and also two like-for-like rows (feature 269 before and after the landing, and
  the research groups 269, 280, 291 and 317), because the 292 restyle sweep and the 319 modal write-ups are not R1's
  kind of work. The session raised this with the GM on 2026-10-10 before starting, and the GM said go ahead. The verdict
  states every figure to beat against the every-group row too.
- **A new collector** (method): 274's `collect.py` reads a check
  brief's own question list, which briefs after the landing no longer carry. 347's `measure/collect.py` counts a
  group's things from its handoff and was validated against R1 on R1's own window before any comparison.
- **The counter fix**: `scripts/pages/brief_load.py` counted every item id on an item line, so a line citing another
  item's finding counted twice (269's FX1: four items, six counted). It now counts the ids that lead the line. Test
  first, red, then green: `tests/tooling/test_brief_load.py`.

## Review history

- spec-fidelity, Mode 2, round 1 (2026-10-10): **FAITHFUL**. The spec is the filed entry word for word, and the GM's
  "Please go ahead and knock out that feature" approves doing it as written. Three items, all applied in R3:
  - Measure whether the cap held, not only whether it split a session (`measure/cap.py`).
  - Judge every figure to beat against the every-group row too.
  - Run `decomp.py` or say that no figure rests on it (said).

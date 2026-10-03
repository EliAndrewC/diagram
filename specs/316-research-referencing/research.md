# Research - feature 316, the implementation cross-referenced with the research, claim by claim

Every figure here was measured on the clone on the date given; none is an estimate.

## R1 - The scope, measured (2026-10-02)

`claims.scope` walks every `import`/`from` statement from `l7r.diagram.hamletgen` outward: 245 modules, of which 241 are reached
by name and four are parent packages whose `__init__` an import of a submodule runs (found by the first scope test, which a
fixture of `other.b` failed until parents were added). 74,331 lines (the spec Context's count, by the same walk). Units before
inheritance: 1,654 functions, 800 methods, 237 classes, 1,019 constants, 18 procedure sections (`claims.all_units`).

## R2 - Coverage speed (2026-10-02)

`claims.all_units` over the scope took 9.1 s with a copy of every unit's syntax tree before dumping it; stripping docstrings
in place once per module and parsing once (the scope walk hands its trees on) took it to 4.2 s. The coverage test runs once per
gate. (Observed 2026-10-02; method: the scope's `all_units` timed on the clone before and after the change.)

## R3 - What the claims cost the generation cache (2026-10-02)

`pipeline/gencache.py` hashes each function's raw source and the module-level text (`_split_sources`), docstrings included, so
the claims invalidate every scripted map's roll cache once. No map's output changes: an AST comparison with docstrings and
string-literal statements removed, run over every changed `.py` file before each commit of claims (238 files on the writers'
commit, 123 on the second round's), found executable code changed only in the files this feature meant to change.

## R4 - The writers and the file bar (2026-10-02/03)

Fifteen writer agents (14 code groups of 3,800-6,500 lines, one for the procedures) wrote the claims. Five files could not take
theirs under the 1,000-line bar and were split, a mechanical move each, the moved names re-exported where callers import them
and nothing a test monkeypatches moved: `ways/track.py` (1,000 -> 939, `gateway.py`), `ways/settle.py` (1,000 -> 900,
`runs.py`), `water/brook.py` (999 -> 806, `brook_course.py`; a first attempt moved `bar_on_race`, which a test patches with
`mock.patch.object`, and was put back), `homesteads/stages.py` (999 -> 920, `seat_geometry.py`), `consts.py` (999 -> 881,
`consts_water.py`). The hamlet suite (1,251 tests) passed before and after each.

## R5 - The bundles (2026-10-03)

Per-file bundles with each cited question's page inline measured 23 MB in all, nearly all of it whole question pages repeated
per file. Writing each question once per bundle as its reader meets it (heading and blocks, no markup), only the files a claim
cites, and showing a class as its own statements (its methods were inlined twice) brought the round-1 batches to 44 of at most
393 KB (12.1 MB in all). (Observed 2026-10-03; method: the bundles' MANIFEST and question files summed with `stat`.)

## R6 - The audit (2026-10-03)

Round 1, 44 batches, every claim: IN-STEP 4,724, DRIFTED 283, MISLABELED 175, UNCLAIMED 160, NEEDS-RESEARCH 84, CANNOT-TELL 36.
The mislabeled, needs-research and unclaimed findings (419 on 122 files) were applied to the claims by fourteen agents; round 2
re-checked the 557 claims that owed it (270 new, 251 changed, the 36 CANNOT-TELL again). Final index, 5,558 claims: IN-STEP
5,115, DRIFTED 378, UNCLAIMED 48, MISLABELED 36, CANNOT-TELL 22, NEEDS-RESEARCH 7; owed 0 (`make claims-report`). The findings
left after round 2 stand, by the two-round rule; DRIFTED is recorded, never fixed in the code, by the GM's direction.

## R7 - The seeded runs (SC-005, 2026-10-03)

One bundle of four known units: IN-STEP (`place.py PER_HOUSEHOLD`, five a household, 0004), DRIFTED (feature 296's far-row
dry-field share, round 1's verdict), MISLABELED (the `stage_hinterland` rough-grazing claim reverted to UNRESEARCHED although
0078's drawing page answers it), UNCLAIMED (`stage_web` with its 30 ft pad claim removed). Three runs on the contract as written:
the IN-STEP, MISLABELED and UNCLAIMED seeds 3/3; the DRIFTED seed 1/3 - two runs named the mismatch (depth from the frame's
shorter side where the page says its width) in an IN-STEP note. The subagent-check procedure (`docs/spec-kit-and-reviews.md`):
a general rule added to the contract - a mismatch you can name is a finding, never a note on a pass - and the same unfixed
bundles run three times again: all four seeds 3/3. (Observed 2026-10-03; method: the six seeded runs' replies read against the four known verdicts.)

## R8 - Defects the audit found, fixed in the work (constitution XIV)

Observed 2026-10-02/03; method: each defect reproduced or read in the code, then its fix tested:
- `claims.py`: a docstring whose first line is `Research:` is dedented whole by `inspect.cleandoc`, so its indented claims were
  lost (found by writer G11); the flat section reads them.
- `claims.py`: module-level `register_knob(...)` calls belonged to no unit, so `_knobs.py`'s knob claims fingerprinted nothing
  (G11); a module that calls at import is a unit of its own claims.
- `claims.py`: a constant re-exported through another module (22 such reads, `hamletgen/plan` reading `GROVE_SIDES` through
  `consts`) was not followed to its definition (plan review, round 2).
- `claims.py`: `@overload` stubs took their implementation's key (audit batch 19, `labels/placer.py::place`).
- `settlement/shrines_wells/torii.py::torii_even`: one arch, the commonest roll, divided by zero (round 2); fixed, tested, its
  claims re-checked.
- `settlement/land/cover.py`: `WOODLAND_MIN_CROWNS`'s literal sat under `PINE_SPREAD_BS` (G09).
- `hamletgen/consts.py`: `POLDER_CELL_FT` read by nothing, and contradicting its question (110 ft against the 190 ft module);
  deleted.

(Observed 2026-10-02/03; method: each defect reproduced or read in the code, then its fix tested.)

## R9 - An acreage figure that is not a defect (2026-10-03)

Writer G12 found `waterfields/` recording `acres` at a fixed 2 ft/px, four times too high on a 1 ft/px hamlet. The hamlet engine
does not read it: `hamletgen/water/comb.py` and `polder.py` take `net_acres(net, plan.ftpx)`, which scales. Only tests read the
`acres` field (`grep` of `l7r/`, `tests/`, `pool/`). Left as recorded, the claims stating the assumption. (Observed 2026-10-03; method: a grep of every reader of the `acres` field in `l7r/`, `tests/` and `pool/`.)

## R10 - Feature 296's two rows

Both DRIFTED in the index on `hamletgen/homesteads/rows.py::seat_rows`. The far-row dry-field share drifts on the depth's
measure (round 1, and the seeded runs). For the row farm's orientation the check read the drawing page's "the map draws only the
first" as a recorded deviation and returned MISLABELED; the session kept DRIFTED, because the research doctrine makes two
attested forms a rolled knob and the GM asked for 296's findings as drifted rows (spec FR-014) - the check's reading is kept in
the row's note.

## R11 - Cost (2026-10-03, `make review-cost`)

The 63 `impl-drift` passes (44 round-1 batches, 12 round-2, six seeded, one targeted): 17,470 s of agent wall time, 105.3M
tokens in (94.5M cached), 1.41M out. The writer, fix and split agents are not in this figure. (Observed 2026-10-03; method: `make review-cost` per agent, summed.)

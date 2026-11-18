# Feature 449: the engine slices (S7-S13), a plan for the GM to read before S7

Written 2026-11-17, after S1-S6, T159-T166. What is left is the Mode A building engine and what serves it: the six pool sheets
(`pool/country-shrines/hoshigaoka-shrine`, `pool/magistracies/*`: county-magistracy-example, hayakawa, ochiba, ochiba-roundtrip-test,
ubame) and their pages, labels, audit, generators and pipeline. The five hamlets are already Rust (feature 444) and are not touched.

## What "the same" means for any port (the GM, 2026-11-17 and 2026-11-18)

The GM: "the resulting maps do NOT need to be bitwise identical" (request.md), his standing rule: "it's always okay for maps to
change, so long as the changes don't violate our research findings", and on 2026-11-18, of every port and every change, not maps
alone: "And whyyyyy did the arbitur rule that things must match exactly when I keep saying they don't have to so long as everything
works?!?!" (T180, constitution XIII "A differing output is not a regression", FR-002). So:

- **A ported check must still do its job.** The audit (`pack_audit`), the size table, the notes-type and map-record checks are the
  yardstick everything else is judged by, so a port of one is shown to work: its red fixtures still fail and the sheets it passed
  still pass. That is not an exactness standard (the GM, 2026-11-18, on T180's wording: "When you say "the audit checks pass/fail must match exactly", then surely you mean "the audit checks must pass" right?!"): a drawn output must pass its checks and hold its research claims, and nothing about its bytes, pixels or positions must match. A check fixed or improved on purpose changes as fixed (FR-002's exception), and a ported check is shown to work by catching what it is meant to catch.
- **Fix as we go** (the GM, 2026-11-18: "gotcha; yeah we want to use this port to fix broken things as we find them, so it needs to be okay to have checks pass as we make those fixes; in general we should fix all known bugs in each step before moving on to porting the next step"). Each step's known defects - found by the port, its claims rounds or its reviews - are fixed before the next step's port begins, each in every copy that still lives (the Rust and any kept Python). A check's verdicts changing as a bug is fixed - a sheet a buggy check refused now passing - or an engine bug fixed changing a map, is expected, never a regression.
- **Everything else is held to working, not to its bytes.** A ported piece passes its tests, does its job for its callers, and keeps
  its research claims; a drawn sheet passes every check its Python sheet passed (`test_every_mode_a_sheet_passes_its_checks` and
  its siblings, ported) and every research claim it rests on, carried onto the Rust (T166) and checked IN-STEP there. A geometry,
  rendering, wording or ordering difference that keeps all of that is accepted with no ask: shapely against `geo` (S8), the
  `resvg` library against the binary (S11), PIL/numpy against the image crate (S7), a diagnostic's formats, a message's words.
- **The byte comparison stays as a signal.** Each slice's differential (`make diff-run`) still compares the written SVG and the
  other outputs, so what moved is listed; a difference is shown and read for whether everything still works, never a stop.
- **Shown to the GM every slice:** a page with every pool sheet before and after, side by side, published even when nothing moved.

FR-002 says so since T180. Before it, what bound bytes was `ask:449-phase4-slices`'s paragraph in the spec ("FR-002 binding what is
written (SVG bytes, check verdicts)", a written difference from GEOS a new ask, the `resvg` binary kept if they differ); its geo and
resvg clauses were amended to the GM's rule (`ask:449-engine-order`, recorded in the spec's paragraph in this plan's commit).

## The order, changed so the checks come first

The slices as filed run the generator's parts (S8 labels, S9a model) before the audit (S9b-S10b). Proposed instead:

| step | slice | what | how it is held |
|---|---|---|---|
| 1 | S9b, S10a, S10b (T153-T155) | the audit: `pack_audit`'s leaves, core and registry, `notes_census`, `size_table`, `building_programs` (4,851 lines) | its red fixtures still fail and today's Python-drawn sheets still pass; wired at once (make targets) |
| 2 | S7 (T150) | the sheet's page writer, `page_lit`, `picture_diff`, the image crate (2,912 lines) | the six sheets' pages; pixel reads within the checks' tolerance |
| 3 | S8 + S9a + S11 together, in two landings | labels (shapely onto `geo`), the Mode A model, the top and the six `.gen.py` as one Rust sheet driver with a spec per map (6,130 lines); pytest's last tests as Rust tests | every pool sheet drawn by Rust passes every ported check and every carried claim IN-STEP; side-by-side page |
| 4 | S12 (T157) | the pipeline: gencache, regen, pool_index, render_cache (1,764 lines) | the pool rebuilt from nothing, every sheet passing |
| 5 | S13 (T158) | the claims tools' Python half, codeid, dead_closure, bundle_door, ruff and the requirements (2,443 lines) | both censuses empty; the feature closes |

The new order and the combined, wired landing of S8, S9a and S11 were ruled by the round arbiter (`ask:449-engine-order`, continue,
2026-11-17) on six conditions: the GM reads this plan before step 1; the audit's imports settled before step 1 (below); one wired
implementation, the Python audit code the generators still import held in lockstep with its Rust until step 3 (restated
by T180: a lockstep test may SHOW the two copies agree, but agreement in bytes is not required - what each copy must hold is that the
audit checks pass and still do their job, and the research claims, and a lockstep test whose only failure is a difference that keeps both is changed
to say so, never a reason to hold the Rust to the Python's bytes); every step a
wired landing with its full review; step 3's split named (below); and the spec's paragraph amended in this commit.

**The audit's imports (the ruling's condition 2).** `pack_audit`, `notes_census`, `size_table` and `building_programs` import from
the engine: `buildings.types` (the building types: `BuildingType`, `RequiredItem`, `classification`, `load_types`, `by_tier`,
`tiers`), `compound_model` (`NOTICE_BOARD_MAX_FT`, `TUB_DOOR_MAX_FT`, `TUB_MAX_GAP_FT`, `KINDS`), `compound_parts` (`board_by_a_gate`,
`tub_by_its_door`, `tub_by_its_eaves`), `interactive.sheet` (`element_kinds`, `DEFS`, `Node`, `parse` - the drawn sheet's reading)
and `labels.hand_sheet.start_tags` (observed 2026-11-17, method: each module's imports read). Each comes into step 1 as Rust that
does the audit's job (red fixtures fail, good sheets pass) - the types and constants as data, the three predicates and the sheet's parse as functions - and
the Python copies stay for the generators under the lockstep rule (as restated above) until step 3 deletes them.

**Step 3's two landings (the ruling's condition 5).** The six generators are thin (43 to 105 lines each, observed 2026-11-17, method:
`wc -l`), their logic in the shared compound code, so step 3 splits by building type: 3a the Rust sheet driver, the Mode A model and
the labels drawing the country shrine (`hoshigaoka-shrine`); 3b the five magistracies and pytest's exit. Each passes every ported
check and every carried claim IN-STEP on the sheets it draws and publishes its side-by-side page.

Why the audit first: once its checks are shown to do their job on today's sheets (red fixtures fail, good sheets pass), every later sheet change is judged by checks we
already trust, in Rust, rather than by the code being changed. Why labels, model and generator together: their in-between values
(a label's float position, a part's outline) may differ under the GM's rule, and only the drawn sheet can say whether a
difference matters; porting them one at a time as libraries with no caller would hold in-between values to the Python's, which
the rule does not ask. The work stays in two landings so a review never covers the whole engine at once.

## Where each could fail, and what stops

- **A ported check stops doing its job** (step 1): a red fixture it must refuse passes, or a sheet the Python audit passed fails,
  is a defect of the port, fixed before landing; never ruled away (a check fixed on purpose is the exception, named).
- **A Rust-drawn sheet fails a check or a claim** (step 3): the slice stops and the port is fixed before it lands; under the GM's
  rule a sheet may change only where its checks and claims allow it, so a failure is never accepted.
- **A generator's logic no spec field can express** (Q6): it goes into the driver as a named option, never as code for one map.
- **Claims:** 290 of the 367 `.py` claims sit in the drawing code (compound_example 65, labels 61, interactive 59, compound_parts 58,
  compound 17, compound_model 16, well_gear 11, dwellings 3), the other 77 in `tools/` (steps 1 and 5). Each slice maps its units
  in `dev/claims-ports.json`, and each carried claim gets a fresh check at its landing (T166), run as waves of the claims checker;
  step 3 carries most of them.
- **Tests (FR-008):** every new test under a tenth of a second; drawing a whole sheet is a slice's one end-to-end test.

## The GM's part

1. Read this before step 1 (the audit); anything to change goes into it first.
2. One page per slice with every pool sheet before and after.
3. Every visible change shows on that slice's before-and-after page, where how it looks is the GM's call; a sheet that fails a check
   or a research claim is fixed before its slice lands.

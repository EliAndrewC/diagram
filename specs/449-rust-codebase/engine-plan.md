# Feature 449: the engine slices (S7-S13), a plan for the GM to read before S7

Written 2026-11-17, after S1-S6, T159-T166. What is left is the Mode A building engine and what serves it: the six pool sheets
(`pool/country-shrines/hoshigaoka-shrine`, `pool/magistracies/*`: county-magistracy-example, hayakawa, ochiba, ochiba-roundtrip-test,
ubame) and their pages, labels, audit, generators and pipeline. The five hamlets are already Rust (feature 444) and are not touched.

## What "the same" means for a map (the GM, 2026-11-17)

The GM: "the resulting maps do NOT need to be bitwise identical" (request.md), his standing rule: "it's always okay for maps to
change, so long as the changes don't violate our research findings". So:

- **A check's verdict is bound exactly.** The audit (`pack_audit`), the size table, the notes-type and map-record checks give the
  same verdict on the same sheet. These are judgments, not drawings, so the port of a check is held to its Python's verdicts.
- **A drawn sheet is held to its checks and its research, not its bytes.** A ported sheet must pass every check its Python sheet
  passed (`test_every_mode_a_sheet_passes_its_checks` and its siblings, ported) and every research claim it rests on, carried onto
  the Rust (T166) and checked IN-STEP there. A geometry or rendering difference that keeps both is accepted: shapely against `geo`
  (S8), the `resvg` library against the binary (S11), PIL/numpy against the image crate (S7) stop being new asks.
- **The byte comparison stays as a signal.** Each slice's differential (`make diff-run`) still compares the written SVG, so
  what moved is listed; a difference is shown, not a stop.
- **Shown to the GM every slice:** a page with every pool sheet before and after, side by side, published even when nothing moved.

FR-002 already says so ("maps MAY change where a check or a research claim allows it", the GM 2026-10-18); what binds bytes is
`ask:449-phase4-slices`'s paragraph in the spec ("FR-002 binding what is written (SVG bytes, check verdicts)", a written difference
from GEOS a new ask, the `resvg` binary kept if they differ). Its geo and resvg clauses are amended to the GM's rule before S7.

## The order, changed so the checks come first

The slices as filed run the generator's parts (S8 labels, S9a model) before the audit (S9b-S10b). Proposed instead:

| step | slice | what | how it is held |
|---|---|---|---|
| 1 | S9b, S10a, S10b (T153-T155) | the audit: `pack_audit`'s leaves, core and registry, `notes_census`, `size_table`, `building_programs` (4,851 lines) | its verdicts on today's Python-drawn sheets, exactly; wired at once (make targets) |
| 2 | S7 (T150) | the sheet's page writer, `page_lit`, `picture_diff`, the image crate (2,912 lines) | the six sheets' pages; pixel reads within the checks' tolerance |
| 3 | S8 + S9a + S11 together, in two landings | labels (shapely onto `geo`), the Mode A model, the top and the six `.gen.py` as one Rust sheet driver with a spec per map (6,130 lines); pytest's last tests as Rust tests | every pool sheet drawn by Rust passes every ported check and every carried claim IN-STEP; side-by-side page |
| 4 | S12 (T157) | the pipeline: gencache, regen, pool_index, render_cache (1,764 lines) | the pool rebuilt from nothing, every sheet passing |
| 5 | S13 (T158) | the claims tools' Python half, codeid, dead_closure, bundle_door, ruff and the requirements (2,443 lines) | both censuses empty; the feature closes |

The new order, and landing S8, S9a and S11 together and wired, change the order and the no-caller rule the round arbiter set in
`ask:449-phase4-slices`, so both go to the arbiter (`make arbiter-ask`) before S7.

Why the audit first: once its verdicts are proven identical on today's sheets, every later sheet change is judged by checks we
already trust, in Rust, rather than by the code being changed. Why labels, model and generator together: their in-between values
(a label's float position, a part's outline) may differ under the GM's rule, and only the drawn sheet can say whether a
difference matters; porting them one at a time as libraries with no caller would hold in-between values to the Python's, which
the rule does not ask. The work stays in two landings so a review never covers the whole engine at once.

## Where each could fail, and what stops

- **Audit verdicts differ** (step 1): a check is a judgment, so a different verdict on the same sheet is a defect of the port,
  fixed before landing; never ruled away.
- **A Rust-drawn sheet fails a check or a claim** (step 3): the slice stops and the port is fixed before it lands; under the GM's
  rule a sheet may change only where its checks and claims allow it, so a failure is never accepted.
- **A generator's logic no spec field can express** (Q6): it goes into the driver as a named option, never as code for one map.
- **Claims:** 290 of the 367 `.py` claims sit in the drawing code (compound_example 65, labels 61, interactive 59, compound_parts 58,
  compound 17, compound_model 16, well_gear 11, dwellings 3), the other 77 in `tools/` (steps 1 and 5). Each slice maps its units
  in `dev/claims-ports.json`, and each carried claim gets a fresh check at its landing (T166), run as waves of the claims checker;
  step 3 carries most of them.
- **Tests (FR-008):** every new test under a tenth of a second; drawing a whole sheet is a slice's one end-to-end test.

## The GM's part

1. Read this before S7; anything to change goes into it first.
2. One page per slice with every pool sheet before and after.
3. Every visible change shows on that slice's before-and-after page, where how it looks is the GM's call; a sheet that fails a check
   or a research claim is fixed before its slice lands.

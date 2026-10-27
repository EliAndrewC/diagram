# Implementation Plan: the magistracy residences brought to the research (feature 433)

**Spec**: `spec.md` | **Request**: `request.md` | **Research**: `research.md`

## Summary

Hayakawa's house is redrawn within research 0091's range (D1), from about 145 tsubo (R1); the inner court is laid out again
around it, and its north wall moves south, the envelope a knob (D3), so the compound stays inside 0116's coverage band (R2). Ochiba's and
Ubame's large houses are recorded as deviations with the GM's reason. The procedure for a new sheet sizes the house by the
research and no longer copies Ochiba's.

## Measured before planning (2026-10-26)

- **Coverage with the house alone resized** (observed 2026-10-26, method: the sheet copied to the scratchpad, the two blocks
  cut to 108 and 82 px wide by 76 px deep and their verandas with them, `pack_audit.coverage` on both): 32.8% today, 26.3%
  with the house resized and nothing else changed - about 13,840 sq ft built on 52,592 sq ft walled.
- **What 30.5% needs** (observed 2026-10-26, method: arithmetic on the measure above): about 45,400 sq ft walled, a cut of
  about 7,200 sq ft, about 29 ft off the depth of the 247 ft wide inner court.
- **The karo's house** (observed 2026-10-26, method: its rect, 115 x 74 px): about 38 x 25 ft, 946 sq ft, inside 0118's
  junior houses of 700-1,000 sq ft, and not resized.

## Constitution Check

A hand-drawn Mode A sheet (`pool/magistracies/hayakawa-magistracy/`), its notes, `docs/` and one drawing page of the record
(0116). No engine code; the sheet's png and page are re-rendered by its gen. Every changed number cites its page; every
guess is labeled. Occasion: building-review (a sheet revised).

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->

## T05 - the claims carry: the placer example's office-hall door seat claimed (385 FR-013)

### T05 Approach (checklist part A)

1. **The goal, in the world.** Every decision the placer example makes about the office hall's doors names its research or
   its GUESS.
2. **The constraints.** No code changes: the claim describes the code as it is.
3. **Where each comes from.** O: impl-drift's UNCLAIMED finding of 2026-10-26 on `compound_example.py::county_magistracy_program`,
   carried into this feature by the claims gate.
4. **Do they describe the world here?** Yes: the door seat is drawn and no claim named it.
5. **The order.** After T01-T04.
6. **The exits.** Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** 15 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** impl-drift IN-STEP on the office hall doors claim.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- **D7** The office hall's door seat, 0.8 of its end face (0.7 its second seat), is claimed as a GUESS in the existing
  `office hall doors` claim: no page places an office hall's doors. Rendering: none.

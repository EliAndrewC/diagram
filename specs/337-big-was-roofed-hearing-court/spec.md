# Feature 337: How big was a roofed hearing court?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: In progress - spec under review

**Affects**: magistracy, research record

**Input**: `request.md` (the entry as filed, and the GM's word to take it up, 2026-10-10)

## Why

The hearing court (shirasu) is roofed on every sheet now (research 0099), but at the old open court's size - larger than
the office hall it fronts. No measured roofed court was found. The entry asks for the answer, or an absence note on 0099 so
`make open-questions` can list it.

**The research pass** (2026-10-10, an agent, read-only; `research.md` R1): no measured roofed court is recorded in anything readable. The only measured Edo figures are the South Town Magistracy's
veranda (3 shaku) and stair (1 ken wide) in the 1810 plan; Takayama's pages size only the great hall (49 mats) and an alcove
(4.5 m).

## Requirements

- **FR-001 - The absence recorded.** `research/questions/0099-the-hearing-court-shirasu.html` carries an absence note on
  the roofed court's size, naming what was searched (the record, the archive, Takayama's official and city pages, Japanese
  Wikipedia, imidas, kotobank, and coverage of the Edo, Sado and Suibara magistracies), so `make open-questions` lists it.
- **FR-090 - Its checks.** The record checks the change owes (`make record-owed`) are run and answered.
- **FR-091 - The implementation check** (feature 378): `make impl-check F=337` reports nothing missing at close.
  A claim that the new finding contradicts is recorded DRIFTED and shown in `make claims-report`; the code and the sheets
  are not changed by this feature (the GM, 2026-10-10: research features annotate, they do not fix, unless the spec asks).

## Success Criteria

- **SC-001** (FR-001): `make open-questions` lists 0099's court size.
- **SC-090** (FR-090): `make record-owed` is answered.
- **SC-091** (FR-091): `make impl-check F=337` reports nothing missing; no file under `pool/` changes.

## Decisions Recorded

- **D1 - No map change.** Nothing measured replaces the drawn size; it stays a disclosed guess.

## The entry, as filed

- **How big was a roofed hearing court?** The court is roofed on every sheet now (research buildings 450), but at
  the old open court's size - larger than the office hall it fronts. No measured roofed court was found (Takayama's
  two courts are described, not measured). The size each sheet draws is a guess, disclosed in the modal; research 0099
  carries no absence note for it, so `make open-questions` cannot list it - add one or answer it.

### The context the entry gave every piece (Questions the research opened (each needs a pass))

Feature 267 took up everything this section held when the GM released it (*"take on whatever future work research
we've been putting off"*, 2026-09-27): 53 questions, each answered ACCURATE, KNOB, SILENT or CONTRADICTION-RESOLVED
(`specs/267-compound-research-owed/outcomes.md`), the kinds rewritten from the answers and the three sheets redrawn
(`forms.md` there holds which form each sheet takes). What is left is below - each a research QUESTION with what the
record holds today, or a silence the maps fill with a labeled guess. The page shows each to its reader: a guess leads
with "This is a guess", and a thin part is disclosed in its kind's caveat (`l7r/diagram/interactive/compound_kinds/`).

### Sources to read when a pass comes back

Closer sources named but not read (each check report's "Open" line, gathered in `outcomes.md`): Ueno 1985 (Rekihaku
bulletin vol. 6) on tablet veneration; the NILIM page on samurai-house ranks; the holding archive of the 1841 Edo
magistracy plan; Takehashi yohitsu for the Nakano dog figures; Ji Cheng's Yuanye (1631) on a study's garden siting;
the Fuchu Joge pamphlet's drawing labels, which sit only in its PDF's images and want a rendering reader.

**Implementation check** (feature 378): owed at its close - each question whose findings this feature changes is cited by a checked `Research:` claim of the code that decides it, or recorded in `implementation-check.md` as implemented nowhere; `make impl-check F=337` says what is owed. The code is fixed only where this spec asks.


## Review history

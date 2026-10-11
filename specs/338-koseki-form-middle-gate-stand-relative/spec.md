# Feature 338: Where did the Koseki form's middle gate stand relative to the offices?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: Done 2026-10-11 - 0104 records the Koseki middle gate and that no source places one against an office hall; the divider gate's place a labeled guess; the 1994 repair report on the download list (item 308); make impl-check F=338 reports nothing missing; report.md

**Affects**: magistracy, research record

**Input**: `request.md` (the entry as filed, and the GM's word to take it up, 2026-10-10)

## Why

The record's roji approach (Hayakawa, Ubame) runs a guest of rank behind the office hall to the divider gate; the entry asks
whether the middle gate of the "Koseki form" opened off the forecourt instead, which would make the divider gate's place a
per-sheet form.

**The research pass** (2026-10-10, an agent, read-only; `research.md` R1): no source places a middle gate relative to an office hall. The record's Koseki form is the old Koseki house at Shiroishi (旧小関家, a middle-rank retainer's
house of 1730), a residence with NO office hall: its middle gate is a gate in the roji wall (塀中門), from the gate court
through the walled roji straight to the principal room's veranda. No source read places a middle gate relative to an
office hall, in a jin'ya or elsewhere.

## Requirements

- **FR-001 - The finding recorded.** `research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html`
  states what the Koseki house shows of its middle gate (a gate in the roji wall, from the gate court to the principal
  room's veranda; a house with no offices) and that no source places a middle gate relative to an office hall (an absence
  note naming what was searched).
- **FR-002 - The divider gate's place labeled.** `0104`'s drawing page says the divider gate behind the office hall is a
  GUESS no source places, so no per-sheet form is owed.
- **FR-090 - Its checks.** The record checks the change owes (`make record-owed`) are run and answered.
- **FR-091 - The implementation check** (feature 378): `make impl-check F=338` reports nothing missing at close.
  A claim that the new finding contradicts is recorded DRIFTED and shown in `make claims-report`; the code and the sheets
  are not changed by this feature (the GM, 2026-10-10: research features annotate, they do not fix, unless the spec asks).

## Success Criteria

- **SC-001** (FR-001, FR-002): 0104 carries the Koseki finding and the absence note; its drawing page labels the
  divider gate's place a guess.
- **SC-090** (FR-090): `make record-owed` is answered.
- **SC-091** (FR-091): `make impl-check F=338` reports nothing missing; no file under `pool/` changes.

## Decisions Recorded

- **D1 - No knob.** The research supports no second form (the record's rule: a knob only where the research supports more
  than one form); the place stays a labeled guess.

## The entry, as filed

- **Where did the Koseki form's middle gate stand relative to the offices?** The roji approach (Hayakawa, Ubame)
  runs a guest of rank behind the office hall to the divider gate; if the middle gate opened off the forecourt, the
  divider gate's place becomes a per-sheet form.

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

**Implementation check** (feature 378): owed at its close - each question whose findings this feature changes is cited by a checked `Research:` claim of the code that decides it, or recorded in `implementation-check.md` as implemented nowhere; `make impl-check F=338` says what is owed. The code is fixed only where this spec asks.


## Review history
- spec-fidelity, Mode 2, round 1 (2026-10-10): **FAITHFUL**, with notes for the implementation (R1 search list; the Why wording).

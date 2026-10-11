# Feature 336: Did Takayama's guest route from the office genkan to the residence run indoors?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: Done 2026-10-11 - 0104 carries the Takayama sources with their limits; the 1830 drawing on the download list (item 307); _roji_parts' claims checked (the roji's trigger DRIFTED: no knob chooses genkan or roji); Ochiba's hand-drawn route recorded in implementation-check.md; make impl-check F=336 reports nothing missing; report.md

**Affects**: magistracy, research record

**Input**: `request.md` (the entry as filed, and the GM's word to take it up, 2026-10-10)

## Why

The record (0104) places the genkan on the office and says the visitors' route runs through the office to the residence; the
Ochiba sheet draws it out of doors (the office's rear door, the middle gate and the garden path to the reception's veranda
stone). Whether the way ran under roof is not recorded; the entry asks for it.

**The research pass** (2026-10-10, an agent, read-only; `research.md` R1): probably indoors, but no source states the Edo-period route. The record's own source (shirobito-1717-takayama) describes
the MODERN visitors' route over the restored compound: it "goes round the rooms of the goyakusho ... and continues on to the
residence". The Gifu prefecture's facility table of the Takayama Jin'ya lists a covered corridor, 渡廊下 12.78 m², beside the
office (1816) and the residence (restored 1996 from an 1830 drawing), without its ends. Nothing puts the route out of doors. The Takayama Jin'ya's own illustration of the compound (R2) shows the office running
straight back under joined roofs into the residence's wings, with no open ground between: the way is under roof, on the
compound as restored.

## Requirements

- **FR-001 - The finding recorded.** `research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html`
  states what the Takayama sources show, each with its limit (the restored compound, not an Edo plan):
  - the visitors' route through the office rooms to the residence;
  - a covered corridor among the restored buildings;
  - the official illustration showing office and residence joined under roof with no open ground between.

  It says the Edo-period plan itself (the 1830 drawing the restoration followed) has not been read, and that drawing goes
  to the GM's download list (`make download-add`).
- **FR-002 - Ochiba's outdoor route is recorded as a mismatch, not a guess.** The evidence speaks for an indoor way, so the
  sheet's outdoor route (the office's rear door, the middle gate, the garden path) departs from it. The code that decides
  that route carries a `Research:` claim citing 0104's findings, recorded DRIFTED by its `impl-drift` check and shown in
  `make claims-report` (FR-091). A check that finds otherwise contradicts this requirement's premise and is reported to
  the GM, not passed. The sheet is not redrawn.
- **FR-090 - Its checks.** The record checks the change owes (`make record-owed`) are run and answered.
- **FR-091 - The implementation check** (feature 378): `make impl-check F=336` reports nothing missing at close.
  A claim that the new finding contradicts is recorded DRIFTED and shown in `make claims-report`; the code and the sheets
  are not changed by this feature (the GM, 2026-10-10: research features annotate, they do not fix, unless the spec asks).

## Success Criteria

- **SC-001** (FR-001, FR-002): 0104 carries the Takayama evidence with its limits; the 1830 drawing is on the download
  list; the claim on the route's code is recorded DRIFTED in `make claims-report`.
- **SC-090** (FR-090): `make record-owed` is answered.
- **SC-091** (FR-091): `make impl-check F=336` reports nothing missing; no file under `pool/` changes.

## Decisions Recorded

- **D1 - No map change.** The evidence is the compound as restored, and the Edo-period plan (the 1830 drawing) is unread;
  the GM's rule for research features is to annotate, and the implementation check records the claim it contradicts.

## The entry, as filed

- **Did Takayama's guest route from the office genkan to the residence run indoors?** Research buildings 370 places
  the genkan on the office and says the visitors' route runs through the office to the residence; Ochiba draws it as
  the office's rear door, the middle gate and the garden path to the reception's veranda stone. Whether that way ran
  under roof (a corridor, the office's own rooms) is not recorded; a Takayama Jin'ya plan with its watari-rōka would
  answer it. A lead is already in the record: 0104.drawing.notes quotes shirobito-1717-takayama, "The route goes round
  the rooms of the goyakusho ... and continues on to the residence" - read it first.

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

**Implementation check** (feature 378): owed at its close - each question whose findings this feature changes is cited by a checked `Research:` claim of the code that decides it, or recorded in `implementation-check.md` as implemented nowhere; `make impl-check F=336` says what is owed. The code is fixed only where this spec asks.


## Review history
- spec-fidelity, Mode 2, round 1 (2026-10-10): CHANGES REQUIRED. Applied: the plan the entry named was sought and read (the
  official compound illustration, R2: office and residence joined under roof), the 1830 drawing goes to the download list,
  and the outdoor route is recorded as a mismatch through a checked claim (FR-091), not labeled a guess.
- spec-fidelity-verify, round 2 (2026-10-10): CHANGES REQUIRED. Applied: FR-002 and SC-001 record the claim DRIFTED with no
  hedge (another verdict is reported to the GM); D1's reason is the restored compound and the unread 1830 drawing.

- spec-fidelity-verify, round 3 (2026-10-10): **FAITHFUL**. Both round 2 items resolved.

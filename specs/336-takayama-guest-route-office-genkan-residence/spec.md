# Feature 336: Did Takayama's guest route from the office genkan to the residence run indoors?

**Feature Branch**: none (main, in a session clone)
**Created**: 2026-10-08 (filed); specified 2026-10-10
**Status**: In progress - spec under review

**Affects**: magistracy, research record

**Input**: `request.md` (the entry as filed, and the GM's word to take it up, 2026-10-10)

## Why

The record (0104) places the genkan on the office and says the visitors' route runs through the office to the residence; the
Ochiba sheet draws it out of doors (the office's rear door, the middle gate and the garden path to the reception's veranda
stone). Whether the way ran under roof is not recorded; the entry asks for it.

**The research pass** (2026-10-10, an agent, read-only; `research.md` R1): probably indoors, but no source states the Edo-period route. The record's own source (shirobito-1717-takayama) describes
the MODERN visitors' route over the restored compound: it "goes round the rooms of the goyakusho ... and continues on to the
residence". The Gifu prefecture's facility table of the Takayama Jin'ya lists a covered corridor, 渡廊下 12.78 m², beside the
office (1816) and the residence (restored 1996 from an 1830 drawing), without its ends. Nothing puts the route out of doors.

## Requirements

- **FR-001 - The finding recorded.** `research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html`
  states what the Takayama sources show - the visitors' route through the office rooms to the residence, and a covered
  corridor among the restored buildings - each with its limit (a modern route over a restored compound; the corridor's
  ends unstated), and that the Edo-period route is not recorded (an absence note naming what was searched).
- **FR-002 - The drawing page labels Ochiba's outdoor route.** `0104`'s drawing page says the outdoor way (rear door,
  middle gate, garden path) is a GUESS against the Takayama evidence for an indoor one.
- **FR-090 - Its checks.** The record checks the change owes (`make record-owed`) are run and answered.
- **FR-091 - The implementation check** (feature 378): `make impl-check F=336` reports nothing missing at close.
  A claim that the new finding contradicts is recorded DRIFTED and shown in `make claims-report`; the code and the sheets
  are not changed by this feature (the GM, 2026-10-10: research features annotate, they do not fix, unless the spec asks).

## Success Criteria

- **SC-001** (FR-001, FR-002): 0104 carries the Takayama evidence with its limits and the absence note; its drawing page
  labels the outdoor route a guess.
- **SC-090** (FR-090): `make record-owed` is answered.
- **SC-091** (FR-091): `make impl-check F=336` reports nothing missing; no file under `pool/` changes.

## Decisions Recorded

- **D1 - No map change.** The finding is weak (a modern route; a corridor whose ends are unstated); the GM's rule for
  research features is to annotate, and the implementation check records any claim it contradicts.

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

# Feature 400: campaign costs III - fruit, salt, hemp cloth and amulets, skilled day wages (issue #5)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future."

gm-assistant filed #5 for the GM's money skill (a money research request), so it is approved by his asking.

**Input**: `request.md` (EliAndrewC/diagram#5 and its comments, verbatim)

## Why

The last of the GM's twelve campaign questions: the skill prices fruit, salt, hemp bags, shrine paper and skilled labor
from guesses. Four search passes ran on 2026-10-19 (`passes/`).

## User Scenarios & Testing

### User Story 1 - The skill can grade each estimate (Priority: P1)

**Acceptance Scenarios** (each figure ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT):

1. **Fruit.**
   - **Japan:** ATTESTED ONLY FOR a fresh persimmon at 6 mon in rural Kanto in the early 1800s, from a teaching sheet
     that names no source document. Edo, castle towns, pears, native apples and dried persimmons: SILENT.
   - **China:** ATTESTED for the Qing court's purchase prices in Beijing (persimmon, pears, apple, crabapple; dried
     persimmon by the jin), labeled as court purchase prices, not the market, with the reading of their unit (by the piece)
     stated as the record's; the Shengjing tax-offset valuations; the Ming valuation of stolen goods in paper money.
2. **Salt.**
   - **Japan:** ATTESTED ONLY FOR two villages: inland Kashimo (Mino) 1763-74, by the hundred mon, beside the same
     household's unskilled day wage (60 mon, 1774); Otsukawa (Owari) 1842, retail by the sho and wholesale by the bale. The
     year of each Kashimo entry is settled from the booklet before it is cited. Edo retail, Ako salt and the Edo
     wholesalers' bale price: SILENT. The inland price ladder is ATTESTED ONLY FOR a secondary, hearsay account, labeled so.
   - **Qing monopoly markup:** ATTESTED for the field price (1-2 cash a jin, Lianghuai about 1830), the official Changlu
     price (1688, 1728) and Beijing's 1736 official price beside its wages; a markup computed from them is the project's
     arithmetic. Where a source states the markup, it is given with its verdict and its label: Lianghuai, a yin costing
     over 10 taels in the selling district against 0.64 at the field (a modern paper on Tao Shu's reform); a few cash at the
     field against 30-70 to the consumer (a secondary paper, quoted from OCR); Sichuan retail 12-15 times the cost of
     making it (King, 1909, late Qing); and Songjiang's local retail of official salt, 1651-88 (Ye Mengzhu).
3. **Hemp cloth and amulets.**
   - **Hemp in Japan:** ATTESTED ONLY FOR one early-1600s lot of Etchu hemp cloth by the roll, the roll's length unknown.
     A price by the tan, and a cotton price beside it: SILENT.
   - **Hemp in China:** ATTESTED: Beijing 1736 hemp and ramie beside cotton on the same list, with its wages; the 1615
     Ming list beside it, with no wage.
   - **An amulet's donation:** ATTESTED ONLY FOR one Ise oshi's gross takings over 2,162 households in 1813 (talisman and
     gifts together, given in proportion, not a price). A price per amulet or talisman: SILENT, in Japan and China.
4. **Skilled day wages.**
   - **Osaka:** ATTESTED ONLY FOR the building trades: the magistrate's day-labor wage (1785), the site helpers' guild rate,
     the 1801 carpenter estimate, and Morisada's carpenter-and-helper pair (different metals, carpenter without meals). Any
     ratio is the project's arithmetic. Where it conflicts with Saito's 4.7 times (0250), the question says so and does not
     resolve it beyond what the sources say.
   - **Edo and castle towns:** a same-place, same-period skilled and unskilled pair is SILENT. The record's figures that
     each give one side only (0250, 0255, 0256, 0262) are gathered with their places, years and gaps; any Edo ratio built
     from them is the project's arithmetic across places and decades. Saito's 2.6 times village pair (0250) is the only one
     from a single place, and it is a village.
   - **Qing:** ATTESTED for the Zhili 1769 official norms (craftsmen against laborers by county) and the 1813 Board of Works
     norm, labeled as government reimbursement rates; Allen et al.'s regression premium labeled as an estimate.
   - **Tailors:** Japan SILENT; Qing ATTESTED ONLY FOR the 1769 Zhili norm at Jinzhou and Gaocheng, where tailors share a
     grouped craftsmen's rate (0.08 tael against a laborer's 0.06), a government reimbursement rate that does not price
     tailors on their own. Tailors' piece rates: SILENT.
   - **Smiths:** Japan SILENT; China ATTESTED ONLY FOR a Ming military manual's forge smiths (0.03 tael a day, no place or
     year, no unskilled wage beside it), pointed at in 0263.
   - **Fletchers:** SILENT, in Japan and China; 0263 found no fletcher's wage or day's output, and the question points at
     it.

Each price sits beside the craftsman's and the unskilled laborer's day wage of the same place and period where a source
gives them; where none does, the question says that wage is SILENT and names the nearest, with its class, its place, its
unit and its gap in years. A figure the project computed is labeled as the project's arithmetic. No price is converted
between coins unless its source converts it.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#5 names each question's fragment FILE, a verdict per figure, and what is still open.

## Requirements

### Functional Requirements

- **FR-001**: Four questions MUST be written in the money section, tagged `money` first, with no drawing page: fruit,
  salt, hemp cloth and amulets, skilled day wages. Where an existing question already holds a figure (0250's wages, 0261's
  cotton), the new question points at it rather than repeating it.
- **FR-002**: Each MUST pass the record's checks: source-reader, quote-check, translation-check, record-format,
  intro-check, and source-applicability on each new source.
- **FR-003**: The feature MUST close `make impl-check` with a "no code implements it" line per question.
- **FR-004**: The answer on EliAndrewC/diagram#5 MUST follow `research/money-requests.md`.
- **FR-005**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The four questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004, FR-005): The issue's answer names all four fragment files, a verdict for every figure, and what is
  still open.

## Assumptions

- Four questions fit one write session.
- The verdicts above are the search passes'. The write may narrow them; it may not widen them without a source.
- Canon (`setting/l7r.md`, the Imperial salt monopoly) is the asker's to apply; the record gives the historical figures.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 5 items.** Fletchers added (SILENT, pointing at 0263); smiths
  ATTESTED ONLY FOR the Ming manual's forge smiths in 0263; tailors' day wage from the Zhili 1769 grouped norm, piece
  rates SILENT apart; the Edo pair stated as SILENT, the one-sided figures gathered as arithmetic; the stated salt markups
  given with their verdicts and labels.

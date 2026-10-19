# Feature 401: kitchen knives, and the copper-to-silver rate (issue #8)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future."

gm-assistant filed #8 for the GM's money skill (a money research request), so it is approved by his asking.

**Input**: `request.md` (EliAndrewC/diagram#8 and its comments, verbatim)

## Why

The skill prices kitchen knives from guesses (E0156-E0158), and the record's mon prices (0259-0266) stand beside silver
wages unconverted because no copper-to-silver rate is written. Three search passes ran on 2026-10-18 and 2026-10-19
(`passes/`).

## User Scenarios & Testing

### User Story 1 - The skill can price a knife and convert mon (Priority: P1)

**Acceptance Scenarios** (each figure ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT):

1. **Kitchen knives.**
   - **Edo prices, ordinary and fine:** ATTESTED ONLY FOR the 1851 wholesale price-cut list of Edo's tool and blade
     wholesalers, per ten blades in silver monme, by kind (usuba cooking knife, sashimi, deba, vegetable, tobacco) and
     grade. Reading the unit as per ten is the record's reading of the page layout, and is said so. A price a knife is the
     project's arithmetic.
   - **A castle town:** ATTESTED ONLY FOR the Tsuyama 1665 ceiling on sword smiths' work: a kitchen knife 8 monme.
   - **A noted maker (Sakai, Seki, Takefu, Tosa):** the price by maker is SILENT, each of the four named. What the record finds of each trade
     (Sakai's guild, its 1730 stamp and its levy, Takefu's smithies and its sickle-and-knife sales) is given with its
     verdict.
   - **A smith's output a day:** ATTESTED ONLY FOR Sakai's tobacco-knife guild rule of 1761 (21, 27 or 30 a day by size,
     for night work). Kitchen knives are SILENT. A rate per smith derived from Takefu's totals is not shown as attested.
   - **The split between smith, sharpener and handle-maker:** ATTESTED ONLY FOR Sakai (smiths, polishers and handle-makers
     about 1757, at second hand; polishers bargaining over pay in 1855). A separate handle-maker of kitchen knives is
     SILENT.
   - **A Ming or Qing cleaver:** ATTESTED: 0.1 tael for a 1-jin cleaver on Beijing's official lists (1736; the Qianlong
     statute book), and about 0.05 for a Wanli-era knife at second hand.
2. **The copper-to-silver rate.**
   - **The official rate:** 1 ryo = 60 monme = 4,000 mon from 1700, and the 1842 Edo change to 6,500 mon: ATTESTED, as law,
     not as the market.
   - **The Osaka market rate, 1787-1850s:** copper in silver monme per kanmon, and gold in silver monme per ryo, from the
     Osaka exchange-office diary (Kobe RIEB / Mitsui): ATTESTED ONLY FOR Osaka. Decade means of mon per monme and of mon
     per ryo MUST be given, beside the source's own units (monme per kanmon, monme per ryo), labeled as the project's
     arithmetic from the daily series, with the method stated: which days, which value of each day, the years missing.
     Year means may be added. 1844-49 is shown as an administered floor, never as a market rate.
   - **The Edo rate:** ATTESTED only where a source prints a figure. A figure read off a chart is labeled the project's
     reading of the chart; where no printed figure exists the question says SILENT and names the nearest printed one, with
     its place and its gap in years.
   - **The 1780s before 1787:** whatever source gives the rate, with its verdict, read as above.
   - **The anchor years** the record already uses are given: about 1802-04 (0250) and 1842 (0262).

Each knife price sits beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them; where none does, the question says that wage is SILENT and names the nearest wage, with its class, its
place, its unit and its gap in years. Every conversion (mon per monme, mon per ryo, a price a knife) is labeled as the
project's arithmetic. The rate question gives rates, not converted prices, and says which record question each anchor year
serves.

### User Story 2 - The asker gets its answer on the issue (Priority: P1)

The answer on EliAndrewC/diagram#8 names each question's fragment FILE, a verdict per figure, and what is still open. It
says whether the checked rate supports gm-assistant's laborer-day conversion (Kazusa 1842, a man's day 132 mon, 0262),
without adopting that conversion as the record's.

## Requirements

### Functional Requirements

- **FR-001**: Two questions MUST be written in the money section, tagged `money` first, with no drawing page: kitchen
  knives, and the copper-to-silver rate.
- **FR-002**: Each MUST pass the record's checks: source-reader, quote-check, translation-check, record-format,
  intro-check, and source-applicability on each new source.
- **FR-003**: The rate series' data file and every cited page MUST be archived before it is cited, and the arithmetic
  MUST be reproducible from the archived file by a script the notes name.
- **FR-004**: The feature MUST close `make impl-check` with a "no code implements it" line per question.
- **FR-005**: The answer on EliAndrewC/diagram#8 MUST follow `research/money-requests.md`.
- **FR-006**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-003): Both questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-004): `make impl-check` reports nothing missing.
- **SC-003** (FR-005, FR-006): The issue's answer names both fragment files, a verdict for every figure, and what is still
  open.

## Assumptions

- Two questions fit one write session.
- The verdicts above are the search passes'. The write may narrow them; it may not widen them without a source.
- The Qing cash-to-silver rate is not asked for and is out of scope; a Qing price stays in silver beside a copper wage,
  unconverted, unless the source itself converts it.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 2 items.** Decade means of mon per monme and mon per ryo made
  required beside the source's units; the cross-check names the request's conversion (Kazusa 1842, 132 mon, 0262), not a
  132-200 range. The aside (name Seki and Tosa under SILENT) taken.
- **spec-fidelity round 2 (2026-10-19, verify): FAITHFUL.** Both items resolved; no contradiction introduced.

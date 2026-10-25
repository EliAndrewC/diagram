# Feature 418: the Hoei and Shotoku market rates (1706-1718) and Canton's own cash rate in the 1830s (diagram#13)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files on this repository to be worked (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future"). The two questions were asked on #13 after the GM approved
splitting gm-assistant's `osaka-1700` era by coinage.

**Input**: `request.md` (the two questions, verbatim).

## Why

gm-assistant's conversion table cannot build an era for 1712-1718, the span its rice price overstates most (2.75 times
Kyoho's), without that span's market rates: monme of silver to the ryo of gold, and mon of copper to the monme (or kanmon to the
ryo). The record's coin page (0287) leaves 1706-1721 "mixed coins, not converted", because several silver coinages of different
fineness passed at once. And `canton-1835` borrows its cash rate from rural Beijing because the record has no Canton figure.

## User Scenarios & Testing

1. gm-assistant reads, for each year 1706-1718 (or as a mean of the Hoei years and the Yotsuho/Shotoku years), the market rate
   of silver to gold and of copper to silver, each named by the silver coinage it is quoted in, and builds `osaka-1712` and
   replaces `osaka-1695`'s borrowed 1706-1711 rates.
2. gm-assistant reads Canton's own cash-per-tael rate for the 1830s from a readable source, or a SILENT with its search.

**Acceptance**:
1. Each rate is quoted from a readable page, with the silver coinage it is quoted in (Keicho, Genroku, Hoei Futatsuho,
   Eiji, Mitsuho, Yotsuho, the new Shotoku silver); a year whose rate is given in several coinages gives each.
2. Where gm-assistant needs one rate per year and the source gives several, the record says which coinage passed most in Osaka
   that year if a source says so, and otherwise gives them all and says no source picks one.
3. Canton's rate is ATTESTED with its year, source and whether it is copper cash per tael of silver at Canton itself; a rate
   from elsewhere in Guangdong is ATTESTED ONLY FOR its place.

## Requirements

- **FR-001**: The findings are written into the record under the citation rules, checked by the record checks `make record-owed`
  names: the 1706-1718 rates in 0287 (how much silver was a monme, a ryo and a bu, coinage by coinage) and, if copper's own rows
  belong there, 0277 (what copper coin was worth in silver); Canton's cash rate in 0289 (what a tael, a string of cash and a
  Chinese dollar were worth in silver). No new question unless a finding fits none of these.
- **FR-002**: Every rate the reply gives carries its fragment file, its verdict and its coinage; the reply is posted on #13.
- **FR-003**: The feature closes with `make impl-check F=418` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing; `make
  impl-check F=418` reports nothing missing.
- **SC-002** (FR-002): a reply on #13 gives each year's rates (or the two means) with their coinage, and Canton's rate or its
  SILENT.

## Assumptions

- The coin-walk chronology already archived for 0287 (`coin-walk-edo-kahei-nenpyo`, https://coin-walk.site/J063.htm) quotes
  yearly rates in several silver coinages for 1706-1718 (seen 2026-10-24); its own sources, and any other readable rate table,
  are searched before it is relied on alone.
- One write session and one check session (under four questions, under ten new keys).

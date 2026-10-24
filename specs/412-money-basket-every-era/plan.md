# Implementation Plan: the standard basket's prices, wages and coin rates in every era the record draws on (feature 412, diagram#13)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-24

## Summary

A research-record feature: question 1's figures into 0273 (salt), 0279 (fuel) and 0265 (rent); the Japanese wages of question
3 into 0250; four new money questions - A the basket in Japan era by era, B the basket and day wage in China era by era, C
Japanese coins in silver, D Chinese money in silver - written from the five passes (`passes/`), each passage read on its page
before it is cited; three write page sessions and one check-and-apply session; then the era marks of feature 413 and the
reply on #13. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-write.md briefs/s3-write.md briefs/s4-check.md"`.
- **The GPIH spreadsheets** (Japan_1710-1871.xls, Japanese Wages.xlsx, Osaka_1600-1650.xls, Japan_rice_P_1620-1867.xls,
  China_1730-1933_Allen_et_al.xls, Beijing_prices_1900-1924.xls, China_wages_1807-1925.xls): read with xlrd/openpyxl, each cell
  cited by sheet and row; a row dump goes to source-reader and quote-check. Downloads from the passes are in the session's
  scratchpad (`/tmp/claude-1000/-diagram/9b9d9dec-de8d-4c07-9afd-3bc1cbbaa84b/scratchpad/gpih-xls-raw/`, `gpihjp/`); a write
  session archives each cited file (`make source-outcome OUTCOME=cited:<key>`).
- **Arithmetic** (decade means, per-kg and per-BTU figures, grams of silver) is computed by a script under `measure/` and
  labeled as this project's arithmetic where it is cited.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the
  record tests stay green. XVI: built as the spec's FRs.

## D1 - question 1 and the Japanese wages (FR-001, FR-002)

0273 gains "What did salt cost in Kyoto in 1745-1754?" from Mitsui's Kyoto sheet (塩, per koku), with a per-kg figure as this
project's arithmetic from a stated weight assumption, and "How much salt did a person eat a year?" (Huang Guoxin 2021 for the
Qing; Japan SILENT with the search). 0279 gains Kyoto firewood by weight (薪, per 10 kan) and Mitsui's Edo and Osaka charcoal
(炭), the Osaka 1818-23 anomaly checked against the sheet before it is cited; the per-million-BTU figure is this project's
arithmetic, its energy figure labeled assumed. 0265 gains the Kyoto/Osaka silence and names Edo 1804-30 as the nearest. 0250
gains Mitsui's unskilled day wage by decade for Kyoto and Edo, the Edo book rate said so, the 1780s and 1872-79 SILENT. Question
1's nearest figures are ATTESTED ONLY FOR their place and years (the issue: "or the nearest dates found").

## D2 - question A, the basket in Japan era by era (FR-002)

New, tagged as the money section's price questions are. One table per era of the spec's list (`osaka-1620`, `osaka-1700`,
`kyoto-1745`, `osaka-1780`, `kyoto-1790`, `kyoto-1800`, `edo-1818`, `edo-1830`, `edo-1850`, `edo-1860`): each basket good found, in the era's own unit and money, with
its source; goods not found named; the day wage beside each era (0250, named). Sources: Mitsui (GPIH), Kumon, Kimura,
Iwahashi; Bassino and Ma for 1745-54 (0249, named). The cautions (Kyoto salt from 1791, Bassino and Ma's cloth against Kumon's)
said where the figure stands.

## D3 - question C, Japanese coins in silver (FR-002)

New. Chogin fineness and pure silver a monme by recoinage; the koban's gold; a ryo and a bu in silver by the market rate (0277's
Osaka series named; the pre-1787 chronology labeled secondary); the nanryo and ichibu-gin's own silver; Bassino and Ma's 3.11 g
stated with its basis SILENT and Bassino's GPIH note. The copper rates stay in 0277 (named, not repeated).

## D4 - questions B and D, China (FR-002)

B: per era of the spec's list (`beijing-1500`, `beijing-1615`, `songjiang-1680`, `beijing-1736`, `suzhou-1750`, `beijing-1820`, `canton-1835`, `beijing-1900`),
each good found in its own money, official prices ATTESTED ONLY FOR official prices, Allen et al.'s Beijing database ATTESTED
ONLY FOR a modern reconstruction, with the era's day wage; Song's rice by decade, its row's id proposed on #13 once written. D: the tael's weight, the dollar, strings and
jingqian, cash a tael by point rates; a decade series SILENT, its unread sources listed open.

## D5 - the era marks (FR-003)

Once gm-assistant confirms the ids (#13), each era goes into `research/assets/money-eras-awaiting.json` with its place and
years; amounts in the record's fragments within 25 years of an era are marked with it (`make money-candidates` lists them,
feature 413's procedure), and `specs/413-money-tooltip-on-the-record/backfill.md`'s lines for them are removed as they are
marked; the Takamiya-Toriimoto fares of 1665 (0260 and its notes), marked against `kyoto-1745` at gm-assistant's request
(#13, issuecomment-6386826304), are re-marked to `osaka-1620`. When gm-assistant's table carries an era, `make money-conversions` refreshes the copy and the era leaves the awaiting
list.

## D6 - the implementation check (FR-004)

`implementation-check.md` holds each touched question's line (no code implements a price).

## D7 - the replies (FR-001, FR-005, FR-006)

A comment on #13 at each landing: every census group mapped to its row or to none with its reason, the Nakasendo post stations
by name (FR-006); per figure the issue asks, the fragment FILE, the verdict and what is still open, and a
per-era table laid out for gm-assistant's era files (place, years, coins in grams of silver, goods with unit and source, wage).

## T - the order

1. The page sessions (s1, s2, s3 write; s4 check). 2. The implementation check. 3. The reply and landing. 4. The era marks once
the ids are confirmed, and a second landing.

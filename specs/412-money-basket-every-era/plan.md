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
stated with its basis SILENT and Bassino's GPIH note. Mon and kanmon in grams of silver for EVERY Japanese era of D2: where
0277 holds the market rate (Osaka 1787-1859, Edo 1781-1842, Osaka 1766, Kyoto 1867) it is named and its decade converted at the
era's chogin; outside it - osaka-1620, osaka-1700, kyoto-1745 before 1766, osaka-1780 before 1787, edo-1860 - question C gives
the legal rate (the 1609 rate of 50 monme and 4 kanmon a ryo, the 1700 rate of 60 and 4) and the market rate where a source
read gives one, or SILENT with the search named. osaka-1700's row note names the recoinages of 1695-1714 inside it.

## D4 - questions B and D, China (FR-002)

B: per era of the spec's list (`beijing-1500`, `beijing-1615`, `songjiang-1680`, `beijing-1736`, `suzhou-1750`, `beijing-1820`, `canton-1835`, `beijing-1900`),
each good found in its own money, official prices ATTESTED ONLY FOR official prices, Allen et al.'s Beijing database ATTESTED
ONLY FOR a modern reconstruction, with the era's day wage; Song's rice by decade, its row's id proposed on #13 once written. D: the tael's weight, the dollar, strings and
jingqian, cash a tael by point rates; a decade series SILENT, its unread sources listed open.

## D5 - the era marks (FR-003)

Once gm-assistant confirms the ids (#13), each era goes into `research/assets/money-eras-awaiting.json` with its place and
years; amounts in the record's fragments are marked with it where their author judges it close enough (`make money-candidates` lists them,
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

## T01 - question 1 and the Japanese wages (D1)

### T01 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant's money skill converts a Kyoto/Osaka 1745-1754 amount with salt, fuel and rent
   priced, and a reader of 0250 sees an unskilled day wage for every confirmed Japanese era - the Osaka, Kyoto and Edo rows
   alike, by the source's own place where the era's city has none (Osaka 1620-1628 by pointer to 0257, 1690-1739 by Kyoto 1713
   and Edo 1710-1716) - or a silence written with its search (the 1780s).
2. **The constraints.** The record's citation rules (research/CLAUDE.md: a verbatim passage on a readable page, or an absence
   note); the 20,000-byte question cap; `make record-owed` clean; the issue's "or the nearest dates found".
3. **Where each comes from.** O: the issue (`request.md`, question 1 and question 3); G: research/CLAUDE.md, feature 195 and
   250 D14 - each read in their files this session.
4. **Do they describe the world here?** Yes: a figure from outside the asked place and years is labeled ATTESTED ONLY FOR its
   case, so the rule never forces a borrowed figure.
5. **The order.** Write (s1), then check and apply (s4); no figure cited before its passage is read.
6. **The exits.** A silence written as a silence with its search (0265's rent, the 1780s wages) instead of a borrowed figure.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0250, 0265, 0273, 0279; 0250 names a wage or a
   silence for each of `osaka-1620`, `osaka-1700`, `kyoto-1745`, `osaka-1780`, `kyoto-1790`, `kyoto-1800` and the four Edo rows.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** As the section "D1 - question 1 and the Japanese wages" states. Rendering: none.

## T02 - questions A and C, Japan (D2, D3)

### T02 Approach (checklist part A)

1. **The goal, in the world.** Each Japanese era gm-assistant prices has its basket goods in the era's own money (0286) and its
   coins in grams of silver (0287).
2. **The constraints.** As T01's, plus the era list of the spec (FR-002) and the ids confirmed on #13.
3. **Where each comes from.** O: the issue's question 2 and 4 and the ids gm-assistant confirmed on #13; G: as T01.
4. **Do they describe the world here?** Yes; where a source covers a city other than the era's, the figure says whose it is.
5. **The order.** Write (s2), check and apply (s4).
6. **The exits.** A good not found is named as not found per era, not filled from another era.
7. **The search smell.** None.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` clean for 0286 and 0287.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D2** As the section "D2 - question A, the basket in Japan era by era" states. Rendering: none.
- **D3** As the section "D3 - question C, Japanese coins in silver" states. Rendering: none.

## T03 - questions B and D, China (D4)

### T03 Approach (checklist part A)

1. **The goal, in the world.** Each Chinese era has its goods and day wage in its own money (0288) and its money in grams of
   silver (0289).
2. **The constraints.** As T02's; official prices ATTESTED ONLY FOR official prices; the round arbiter's ruling on
   ask:412-record-round5 (round 5 the last, its EDITs through `make apply-edits` only).
3. **Where each comes from.** O: the issue and #13; G: as T01; the arbiter's ruling in `arbiter.jsonl`.
4. **Do they describe the world here?** Yes.
5. **The order.** Write (s3), check and apply (s4), rounds 3-5 on 0288/0289 in this session.
6. **The exits.** The 0.75 against 0.71 tael a dollar both stated, the choice left to the GM's review.
7. **The search smell.** Reviewer rounds on one page; capped by the arbiter at round 5.
8. **The budget.** One write session, the check session and three further check rounds.
9. **Done, measured.** `make record-owed` clean for 0288 and 0289.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D4** As the section "D4 - questions B and D, China" states. Rendering: none.

## T04 - the implementation check (D6)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The GM can see that no code decides a price, so no claim is owed.
2. **The constraints.** research/CLAUDE.md, feature 378: each touched question's line in `implementation-check.md`.
3. **Where each comes from.** G: research/CLAUDE.md's section on findings checked against the code.
4. **Do they describe the world here?** Yes: the engine draws no price.
5. **The order.** After T01-T03 settle their questions.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=412` reports nothing missing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D6** As the section "D6 - the implementation check" states. Rendering: none.

## T05 - the reply on #13 (D7)

### T05 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant builds its era files from one comment: every census group, every figure asked, its
   verdict and fragment file.
2. **The constraints.** FR-001, FR-005, FR-006 (the Nakasendo stations by name).
3. **Where each comes from.** O: the issue and the spec's FRs.
4. **Do they describe the world here?** Yes.
5. **The order.** After the record settles (T01-T03) and the marks (T06), before the landing's report.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** Half an hour.
9. **Done, measured.** The comment's URL.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- **D7** As the section "D7 - the replies" states. Rendering: none.

## T06 - the era marks (D5)

### T06 Approach (checklist part A)

1. **The goal, in the world.** A reader hovering an amount dated inside a new era sees it converted at that era's prices.
2. **The constraints.** Feature 413's mark and its refusals (`make record CHECK=1`); markup only, no visible word; the ids and
   years confirmed on #13; 0288/0289 untouched.
3. **Where each comes from.** O: #13 (the ids; the borrowed osaka-1620 for the Takamiya fares, Kyoto 1652-1656 and 0185's
   1611 and 1658 fees); G: 413's
   `money.py` docstring.
4. **Do they describe the world here?** Yes: an amount outside every era's years is passed over with its reason, never given a
   borrowed era gm-assistant did not ask for. 0288/0289 are untouched by s5 only because T03's rounds hold those files. Their
   amounts, and every other Chinese amount, are in taels, cash and dollars, coins no era of gm-assistant's table yet carries
   and `make money-candidates` does not list (its coins are Japanese). So T05 asks on #13 for the Chinese eras' coin keys;
   until the table carries them, `backfill.md` passes each Chinese question over in one line with that reason, and once it
   does, the amounts are marked as the Japanese ones were.
5. **The order.** After the ids are confirmed; a session of its own (s5) in its own clone.
6. **The exits.** Passing an amount over with its reason in `backfill.md`.
7. **The search smell.** None.
8. **The budget.** One session.
9. **Done, measured.** `make money-candidates CHECK=1` exits 0; `make record-owed` names nothing the marks caused.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D5** As the section "D5 - the era marks" states. Rendering: none.

## T07 - close: report and land

### T07 Approach (checklist part A)

1. **The goal, in the world.** The record's new questions and marks are on main and the GM has the feature report.
2. **The constraints.** `make land`'s refusals; the feature report (`make feature-report F=412 WRITE=1`).
3. **Where each comes from.** G: the root CLAUDE.md's development workflow.
4. **Do they describe the world here?** Yes.
5. **The order.** Last.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** Half an hour.
9. **Done, measured.** Landed on main.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- **D8** Land once T01-T06 are ticked; the GM-review row lands open. Rendering: none.

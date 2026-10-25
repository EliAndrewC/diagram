# Implementation Plan: how stable prices were, over what spans and for which goods, and when a borrowed price needs a note (feature 414, diagram#15)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-24

## Summary

A research-record feature: five new money questions - A how steady prices were at each time scale, good by good (Japan and
China); B how far prices differed from place to place; C how each good's price moved from period to period and why (salt first);
D when a borrowed price needs a note and when it should not be borrowed (the closeness rule); E (Comparative money) the modern
fiat-era yardstick - written from the four passes and this project's arithmetic (`measure/`), each passage read on its page
before it is cited; three write page sessions and one check-and-apply session, run in a sibling clone after feature 412's; then
the reply on #15. No code, map or canon change.

## Technical Context

- **The record.** `make page-session` in a sibling clone (`/diagram/.clones/diagram-money-pages`, named after it), briefs
  `briefs/s1-write.md` to `s4-check.md`, after 412's queue there has ended and been pulled back.
- **Arithmetic.** `measure/mitsui_stability.py` (the SD of log changes at half a year to 50 years, drift, seasonality, city
  spreads, from the GPIH Mitsui file); `measure/osaka_daily.py` for day to day, a week, a month, three and six months and a year from
  the RIEB daily Osaka rice series (archived; its output committed beside it); `measure/qing_stability.py` for the same lags from Allen et al.'s annual Qing city
  series (GPIH `China_1730-1933_Allen_et_al.xls`; Beijing's prices there a reconstruction, said so) and, where its years allow, the
  GPIH Chinese rice series; `measure/closeness.py` for D4's thresholds. Each script's output is committed beside it and
  cited as this project's arithmetic.
- **Comparative sources.** E's sources carry the kind `comparative` and E is tagged `subject=comparative,money`; the Bank of
  England and Clark series are not written unless the GM approves them (spec acceptance 3).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - question A, how steady prices were (FR-001, FR-002 A)

Per scale the request names - within a day, day to day, week to week, month to month, year to year, decade to decade, century
to century - a verdict: the sources' measured statements (Shinbo, Miyamoto, Saito; Shiue, Shiue and Keller, Keller-Shiue-Wang,
Lu and Peng, 全漢昇, Qian Yong) and this project's arithmetic (Mitsui by city and good, each figure with its city and pairs;
day to day, week to week and month to month from the RIEB daily series), the drift beside each swing, the shocks dated. Per good of acceptance 5 a verdict,
SILENT with the search where none. Copper against silver drift kept apart (China). Set against question 1's canon (an era as one
price level): the measured within-era spread said plainly, escalated if it contradicts the table's treatment (FR-006).

## D2 - question B, places (FR-001, FR-002 B)

The literature's co-movement figures (Takatsuki, Shinbo, Bassino and van der Eng, Shiue and Keller); level spreads as this
project's arithmetic from Mitsui (1818-1858, by good, Kyoto's salt break named and left out); 0280-0283 named for distance and
carriage; Iwahashi's rice in 14 places (GPIH `Japan_rice_P_1620-1867.xls`) for the spread across Japan, castle towns among
them; town against country from Saito's village and Kyoto wages and the record's village prices (0273's Kashimo against
Kyoto), SILENT where no source sets them side by side; China's level spreads from Allen et al.'s Beijing, Canton and Suzhou
wage and basket levels. Set against question 3's canon (one place per era).

## D3 - question C, across periods, salt first (FR-001, FR-002 C)

Salt in days of an unskilled wage per local unit, period by period (Song, Ming, Qing; Edo per sho from 0273, named), each
period's own figures and the drivers the sources name (monopoly reach, license costs, smuggling, the ticket reforms, the
domain monopolies of Kanazawa, Sendai and Ako); Japan and China side by side, not converted. Other goods across periods (高壽仙's
1615 and 1736 Beijing lists; 閱世編's cotton and cloth; Peng's silver purchasing power; Mitsui's goods across the Edo
sub-periods, with the drivers the sources name - harvests, recoinage, the 1859 opening). Set against question 2's canon (the
basket and the day wage).

## D4 - question D, the closeness rule (FR-001, FR-002 D, FR-003)

Derived, and labeled as this project's derivation (no source states one). Japan, by good class and city, from Mitsui and the
daily Osaka series:
- **The era's own spread**: an era row converts any year inside its span at one price level, so the SD of log change at half the
  era's span (5 years for a ten-year era) is the uncertainty the table already accepts.
- **No note**: a borrowed era whose gap in years has an SD of log change no larger than that within-era spread (measured).
- **Do not convert - the measured breaks**: across a structural break whatever the gap - the 1859 opening (the series' own
  break), a recoinage that changed the money's silver, a change of money system (mon to yen, cash to dollars).
- **Between them, a note**; a further numeric limit is NOT set by this project: the measured swing-by-gap curve goes to the GM
  through `escalation-check` (FR-003) for his choice of where a noted conversion stops being made (the request: an amount of
  time "only ... if that amount of time is based on something").
- **China**: the same no-note bound, from `measure/qing_stability.py`'s lags on Allen et al.'s annual city series (Suzhou and
  Canton rice; Beijing's reconstruction named as one) beside the literature's half-year and year figures (Shiue; Keller-Shiue-Wang;
  Lu and Peng's drift in silver); where the series cannot reach a lag, the measured reason (its years, its gaps) is stated; the
  copper-silver rate's moves (1807-1880) are a break for an amount in cash.
- **Place**: the no-note bound read from the city spreads (B) - a city whose spread to the era's city is within the within-era
  spread needs no note; the structural breaks are place's do-not-convert bound too (another money system, a domain's own notes);
  any further limit by distance goes to the GM with the measured city spreads beside the time curve.
- **Size of the amount**: the measurements give no basis to vary the bounds by size unless a source shows small and large
  amounts moving differently; the rule says which.
Each bound gives its years and the pairs it rests on (`measure/closeness.py`), set against question 4's canon (413's marking);
offered to 413's marking and to gm-assistant's tooltip, and whether it becomes a record check put to the GM through
`escalation-check` (FR-003).

## D5 - question E, the modern yardstick (FR-001, FR-002 E)

Comparative: the US and Japanese CPIs since 1971 (drift; monthly, 12-month and annual SD), a staple's modern monthly and
12-month SD (BLS), Rolnick and Weber's commodity against fiat inflation; the scales below a month SILENT for the modern series
read unless one daily staple series is read (a staple's daily futures settlement, the counterpart of Dojima - e.g. rough rice
  or wheat), its search recorded and SILENT the result if none is readable; set beside A in the reply.

## D6 - the implementation check (FR-004)

`implementation-check.md` holds each new question's line (no code implements a price).

## D7 - the reply (FR-001, FR-003, FR-005, FR-006)

A comment on #15: per figure the issue and its addition ask, the fragment FILE, the verdict and what is still open; the rule
with its derivation; its offer to 413 and gm-assistant; per question, how the answer stands against its canon and any
escalation.

## T - the order

1. The measure scripts (osaka_daily, closeness). 2. The page sessions (s1-s3 write; s4 check). 3. The implementation check. 4.
The reply and the landing.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
## T06 - the reply on #15 (D7)

### T06 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify every figure of #15 and its addition from the reply alone, and close it.
2. **The constraints.** FR-001 (per figure: fragment file, verdict, what is open), FR-003 (the rule offered to 413 and
   gm-assistant), FR-006 (each answer against its canon), SC-001-SC-004; GM items through `escalation-check` first.
3. **Where each comes from.** O: the spec's FRs from the issue; G: CLAUDE.md (escalation-check before the GM).
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages and the implementation check; escalation-check on the GM items before posting.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** One reply.
9. **Done, measured.** The comment's URL.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D7** As the section "D7 - the reply" states. Rendering: none.

## T07 - close: report and land

### T07 Approach (checklist part A)

1. **The goal, in the world.** The feature's findings on main, its report written.
2. **The constraints.** `make land`'s refusals; `make feature-report F=414 WRITE=1`.
3. **Where each comes from.** G: CLAUDE.md, Development workflow.
4. **Do they describe the world here?** Yes.
5. **The order.** After the reply.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Landed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- none beyond D1-D7. Rendering: none.

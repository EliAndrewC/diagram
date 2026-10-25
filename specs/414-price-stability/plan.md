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

## T01 - the measure scripts (D1, D4)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Every figure the pages cite as this project's arithmetic can be reproduced: the scripts under
   `measure/` (mitsui_stability, osaka_daily, qing_stability, closeness, plus iwahashi_spread, qing_levels, mitsui_periods and
   modern_yardstick, which sessions 2-4 added for D2, D3 and D5) print exactly their committed `*.out.md` from the archived
   files their docstrings name.
2. **The constraints.** research/CLAUDE.md (a computed figure is labeled this project's arithmetic and names its inputs); the
   inputs archived in the private source archive; `python3 -I`.
3. **Where each comes from.** G: research/CLAUDE.md and constitution XII; O: the script layout (one script per measure, output
   beside it) is ours.
4. **Do they describe the world here?** Yes; Beijing's Allen et al. prices are a reconstruction and the scripts and pages say so.
5. **The order.** Scripts before the pages that cite them (s1-s3 ran each before writing).
6. **The exits.** A lag a series cannot reach is reported with its measured reason (years, gaps), not filled.
7. **The search smell.** None.
8. **The budget.** Part of each write session.
9. **Done, measured.** All eight scripts rerun 2026-10-24 against the archived spreadsheets (GPIH Mitsui, Iwahashi, Allen et
   al., Chinese rice; RIEB served.xlsx; the DBnomics capture) and the session copy of the Yahoo rough-rice JSON: every output
   identical to its committed file. The archive's own capture of the Yahoo URL is a 429 page (outcome partial, twice); the
   rough-rice figures rest on the session copy until a capture succeeds.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** As the section "D1 - question A, how steady prices were" states, for its arithmetic. Rendering: none.
- **D4** As the section "D4 - question D, the closeness rule" states, for `closeness.py`, with one change from the plan's
  place test: a city passes only if both the SD of its gap to the era's city AND the average gap are within the within-era
  spread (the SD alone passed Edo miso at 29% below Kyoto); the reason is in closeness.py's docstring and on 0294. Rendering:
  none.

## T02 - questions A and E (D1, D5)

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant and the GM can read, per time scale from within a day to century to century, how
   far Edo and Qing prices moved, good by good, with the drift beside each swing (0290), and the modern paper-money yardstick
   beside it (0291).
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or an absence note); the
   20,000-byte question cap; `make record-owed` clean; E's sources tagged `comparative`; England's premodern series not written
   without the GM's approval (spec acceptance 3).
3. **Where each comes from.** O: the issue (`request.md`, A and E); G: research/CLAUDE.md; G: the England exclusion is the
   spec's acceptance 3 and research/CLAUDE.md's rule that a comparative source is not sought unless the GM asks for or approves
   it; it goes to him through escalation-check.
4. **Do they describe the world here?** Yes; Japan and China figures are kept in their own money, not converted.
5. **The order.** Write (s1), check and apply (s4), round 3 closed by the arbiter (ask:414-round3, accept).
6. **The exits.** SILENT with its search where a scale or good has no source (the modern scales below a month beyond the one
   futures series read).
7. **The search smell.** None.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0290 and 0291.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D1** As the section "D1 - question A, how steady prices were" states. Rendering: none.
- **D5** As the section "D5 - question E, the modern yardstick" states; England's series named as found and waiting on the GM,
  not written. Rendering: none.

## T03 - questions B and C (D2, D3)

### T03 Approach (checklist part A)

1. **The goal, in the world.** The reader sees how far prices stood apart from city to city and town to country (0292) and how
   a good's price moved from dynasty to dynasty and era to era, salt first in days of a laborer's wage, with the drivers the
   sources name (0293).
2. **The constraints.** As T02's; Japan and China side by side, not converted (no sho-to-weight figure found).
3. **Where each comes from.** O: the issue (B, C and the GM's addition to question 2); G: research/CLAUDE.md.
4. **Do they describe the world here?** Yes; a second-hand or rural wage is labeled ATTESTED ONLY FOR its case.
5. **The order.** Write (s2), check and apply (s4).
6. **The exits.** Absence notes for what no source sets side by side (a good's village and city prices; the monopolies' price
   effect; why Edo salt doubled after 1830).
7. **The search smell.** None.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0292 and 0293.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D2** As the section "D2 - question B, places" states. Rendering: none.
- **D3** As the section "D3 - question C, across periods, salt first" states. Rendering: none.

## T04 - question D, the closeness rule (D4)

### T04 Approach (checklist part A)

1. **The goal, in the world.** An author marking a borrowed price, and gm-assistant's tooltip, know when a borrowed era needs a
   note, when it should not be converted at all, and why (0294).
2. **The constraints.** The rule is this project's derivation (no source states one: SILENT, absence note); the further numeric
   limit is NOT set here but goes to the GM through `escalation-check` (FR-003; the request: a time limit "only ... if that
   amount of time is based on something").
3. **Where each comes from.** O: the derivation (within-era spread at half the era's span, plus twice its standard error); G:
   FR-003 from the request's words; R: the breaks from Shinbo (1859), Saito 2003 (recoinage), the 1871 act and Lu and Peng.
4. **Do they describe the world here?** Yes for the Mitsui cities to 1858; the Qing goods other than the baskets give no bound
   (Beijing's are flour times a fixed figure; Kishimoto's rice too sparse), said so.
5. **The order.** Write (s3), check and apply (s4).
6. **The exits.** The place test changed from the plan (T01 D4) rather than pass Edo miso at 29% below Kyoto; the size of the
   amount left SILENT (no series priced by lot size).
7. **The search smell.** None.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0294; the curve (`measure/closeness.out.md`) in the
   reply for the GM, through escalation-check.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D4** As the section "D4 - question D, the closeness rule" states, with the place test of T01 D4. Rendering: none.

## T05 - the implementation check (D6)

### T05 Approach (checklist part A)

1. **The goal, in the world.** The GM can see that no code decides a price or a borrowing distance, so no claim is owed.
2. **The constraints.** research/CLAUDE.md (feature 378): each touched question's line in `implementation-check.md`.
3. **Where each comes from.** G: research/CLAUDE.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=414`: nothing missing (2026-10-24).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- **D6** As the section "D6 - the implementation check" states. Rendering: none.

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

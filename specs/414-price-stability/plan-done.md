# 414-price-stability - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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


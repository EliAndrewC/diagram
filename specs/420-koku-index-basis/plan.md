# Implementation Plan: the goods-dollar koku on a sound index basis (feature 420, diagram#17)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

A research-record feature answering gm-assistant's six questions from search passes already run (`passes/q1-what-was-bought.md`,
`q3-rent.md`, `q4-japan.md` with `q4-japan-table.md`, `q4-china.md`, `q5-method.md`, and the modern pass `q2-q6-modern.md`).
Five write sessions, each followed by a check-and-apply session (`make page-session`), in two sibling clones so that two queues
run side by side: `/diagram/.clones/diagram-money-marks` (S1 Q1 and the historical rent; S2 Q4 Japan; S3 Q4 China) and
`/diagram/.clones/diagram-money-pages` (S5 the method; S4 the modern goods). Then the reply on #17 (through `escalation-check`
for what bears on the canon). No code, map or canon change.

## Technical Context

- **The passes** are leads, not citations: each write session reads every passage on its page before citing it.
- **The record.** `make page-session` with briefs `briefs/s1-*.md` to `s5-*.md` and their check briefs `c1-*.md` to `c5-*.md`.
- **Two clones.** The queues touch different questions; shared files (the registry, `source-tags.json`, `contents.json`, the
  glossary) merge as they did for 414 and 416.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - what was bought (Q1; FR-001; acceptance 1, 2, 6)

In 0249, a section per basket good: its form and quality as Bassino and Ma's Table 3 note states it (rice white; soybeans whole
dry beans "of above average quality" standing for miso, shoyu, tofu and natto; barley, wheat, buckwheat and millets as
unprocessed grain priced by Meiji farm-gate ratios; fish as salmon and cod by a wholesale ratio of 1882-86; oil rapeseed for
both lamp and table; cloth plain cotton by the tan); and the market level of each price: the Mitsui Kyoto books' "retail"
(an editor's label on a merchant house's purchases, ATTESTED ONLY FOR that), the soybean benchmark an Osaka 相場 table of 1757
(wholesale), the grains and fish constructs at no market level. The Mitsui Kyoto miso and soy sauce prices for 1745-54, held in
the same GPIH sheet and unused by the paper, are given as the observed alternatives to the soybean proxy. Markups: SILENT for
Kyoto and Osaka about 1745; ATTESTED ONLY FOR Mitsui's Edo cotton store (2-12%, Shimomukai) and a village salt seller in Owari,
1842 (this project's arithmetic). What urban commoners ate of fish: SILENT for Kyoto and Osaka; the Edo 1860 diary as
ATTESTED ONLY FOR one low-stipend samurai. Each sibling page where a good has one (0261 cloth, 0273 salt, 0279 charcoal and
fuel) carries its own good's form and market-level finding, not only a pointer (spec FR-001). For the other eras, where a
good's form or market level differs from 1745, the per-era tables of D3 and D4 say so (or SILENT with the search).

## D2 - the historical rent (Q3; FR-001; acceptance 1, 6)

In 0265: Mitsui's Osaka rental houses, 0.7 monme a mat a month for a back house and 0.9 for a front, 1814 and 1846 (Tani 1989),
the 『所以者何』 average beside it (about 1801-32), Edo's back-lot rents of the Kansei years and 1840 (Washizaki 2012), and the
1848 carpenter's rent named as the Bunsei figure 0265 already holds. A 九尺二間 room at the Osaka rate is this project's
arithmetic, labeled so, with its assumption (the whole floor billed by the mat). Kyoto: SILENT with the search. c. 1745: SILENT;
Fujimoto 1978 (Osaka 1764-72) and the Mitsui and Kyoto leads named as not read; McClain and Wakita to the download list if not
there.

## D3 - the eras beyond rice, Japan (Q4; FR-001; acceptance 1, 4)

A new question beside 0286: per Japanese era, a table of every good the era prices - rice, barley and wheat, buckwheat
and millets, soybeans, other beans, fish, edible and lamp oil, cloth, salt, fuel and housing - each cell observed (its
source and city), reconstructed, borrowed (the era or source borrowed from, gm-assistant's addendum: kyoto-1745's beans, grains
and fish from early Meiji ratios; its soybeans set equal to rice; Kumon's soybeans Osaka's, chained to other cities), held in
the record but unused, or absent; new prices in 0286's format. The Kyoto salt unit: from 1791 the Mitsui Kyoto books price salt
by the bale (Kusano 1996), so 0286's "Kyoto's salt from 1791 is doubtful" is revised to the unit change, the bale size labeled
as Kusano's own assumption. Fish: SILENT for every Edo-period era, with the search. Each cell also says, where it differs from
1745's (D1), the good's form and the price's market level (Q1's "and where it differs, the other eras"): wholesale 相場
quotations against purchase books, salt and charcoal by the bale from 1791, LTES retail for 1882; SILENT with the search where
no source says.

## D4 - the eras beyond rice, China (Q4; FR-001; acceptance 1, 4)

A new question beside 0288, in the same shape: Timkovski's Peking prices of 1821 for beijing-1820 (salt, fish, fuel, cloth by
the piece, a rent), the Changzhou cloth recollection for suzhou-1750 (ATTESTED ONLY FOR a neighboring prefecture's rounded
memory), the Beijing fish of the 1590s-1602 only as secondary reports; official and market prices kept apart; each cell's form and market level where it
differs from the Japanese 1745 basket's (Q1's "other eras"), or SILENT with the search; beijing-1500
SILENT; prices already in the record but unused by an era named as such.

## D5 - the method (Q5, with the poverty-line housing allowance; FR-002a; acceptance 5, 6)

A new money question in "Money and prices": what baskets compute in the papers (welfare ratios and poverty lines, a ratio or a
headcount, never what a coin is worth today); index choice where consumption patterns differ (Laspeyres and Paasche resolved
by a Fisher mean, the spread read as the uncertainty; Deaton and Heston); one figure or several (MeasuringWorth's measures side
by side; the Bank of Japan's 1 ryo by rice against by wage); which papers put a basket into modern money (Allen 2017's draft,
which does so to show the problem; Moatsos via Our World in Data) and the rest SILENT with the search; rice as numeraire,
accepted as a convenience (NDL) with its weaknesses named (harvest swings, rice's own relative drift across Kyoho, grain wages'
wrong rankings). Any rule drawn for gm-assistant is labeled this project's derivation. The housing allowance of Allen's and
Moatsos's basic-needs lines from the modern pass.

## D6 - the modern goods (Q2, Q3's modern US candidates, Q6; FR-002; acceptance 3, 6)

A new question (or two, by size) in "Comparative money: other societies": per basket good, the modern US like-for-like product
at retail under the snapshot rule and at wholesale where the historical price is wholesale, each a dated observation with its
link; the housing candidates per m² a year, each with what it measures (Q3); a US adult's yearly quantity of each good. Each page says it never sets a Rokugani
price; a finding that would change a snapshot price is reported for a new snapshot, never edited into it.

## D7 - the implementation check (FR-005)

`implementation-check.md` holds each touched question's line.

## D8 - the reply (FR-004)

A comment on #17, per question, each figure with its fragment file and verdict, what is open, and how to verify; findings that
bear on the canon (the snapshot, the eleven-good table, the Kyoto salt unit) through `escalation-check` first.

## T01 - Q1, what was bought, in 0249 (D1)

### T01 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can price each basket good's modern match as the same form at the same market level.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-6.
3. **Where each comes from.** O: the six questions (`request.md`, with gm-assistant's Q4 addendum); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; the Mitsui 'retail' label is reported as the editor's label it is, and a construct is never called an observation.
5. **The order.** S1 write, C1 check (marks clone).
6. **The exits.** A form or markup no source states is SILENT with its search.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0249 and its siblings (0261, 0273, 0279), each
   carrying its good's own finding.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** As the section "D1 - what was bought" states. Rendering: none.
## T02 - Q3, the historical rent, in 0265 (D2)

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can replace the borrowed Edo room with an observed Osaka rent, or knows none exists for c. 1745.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-6.
3. **Where each comes from.** O: the six questions (`request.md`, with gm-assistant's Q4 addendum); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; Osaka 1814-1846 is ATTESTED ONLY FOR its city and years.
5. **The order.** With T01 in S1 and C1.
6. **The exits.** c. 1745 and Kyoto SILENT with the search.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0265.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D2** As the section "D2 - the historical rent" states. Rendering: none.
## T03 - Q4, the Japanese eras beyond rice (D3)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can average each good across the Japanese eras without counting one observation twice.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-6.
3. **Where each comes from.** O: the six questions (`request.md`, with gm-assistant's Q4 addendum); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; each cell says observed, reconstructed, borrowed (from where), held or absent.
5. **The order.** S2 write, C2 check (marks clone).
6. **The exits.** Fish SILENT for every Edo-period era with the search; a bale size no source fixes stays labeled as Kusano's.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the new question and 0286.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D3** As the section "D3 - the eras beyond rice, Japan" states. Rendering: none.
## T04 - Q4, the Chinese eras beyond rice (D4)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The same for the Chinese eras.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-6.
3. **Where each comes from.** O: the six questions (`request.md`, with gm-assistant's Q4 addendum); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; official and market prices kept apart.
5. **The order.** S3 write, C3 check (marks clone).
6. **The exits.** beijing-1500 SILENT; a secondary report ATTESTED ONLY FOR what it is.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the new question and 0288.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D4** As the section "D4 - the eras beyond rice, China" states. Rendering: none.
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
## T07 - the implementation check and the reply (D7, D8)

### T07 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify each answer and close #17.
2. **The constraints.** `make impl-check F=420`; `escalation-check` on what bears on the canon.
3. **Where each comes from.** G: root CLAUDE.md; O: `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01-T06 land.
6. **The exits.** None.
7. **The search smell.** None: research, not a fit.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=420` reports nothing missing; the reply posted; `make feature-report F=420 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- **D7-D8** As the sections "D7" and "D8" state. Rendering: none.

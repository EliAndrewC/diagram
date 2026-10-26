# Implementation Plan: working days a year by kind of worker, and how often players performed (feature 428, diagram#20)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-26

## Summary

A research-record feature answering the GM's three questions from search passes (`passes/q1-working-days.md`,
`q2-engagement.md`, `q3-performances.md`). Two write sessions, each followed by a check-and-apply session, in two clones side by
side: this clone, `/diagram/.clones/diagram-money-research` (S1: Q1 working days and Q2 terms of engagement - the labor
questions, which share 0250, 0115, 0260 and 0307), and `/diagram/.clones/diagram-money-research-2` (S2: Q3 performances, Japan
and China, and England as its own comparative question). Then the reply on #20. No code, map or canon change.

## Technical Context

- **The passes** are leads, not citations: each write session reads every passage on its page before citing it. Pages the passes
  read through local copies (Kumon 2020 and the postal-museum PDFs by pdftotext, research_09_02 by OCR, the 2013 chinanews page
  decoded from GBK) go through `make source-pages` or the archive; an image-only page goes to the checks with `IMAGES=`.
- **Secondary summaries** (the three summaries of 古川貞雄『村の遊び日』, the popular chinanews article, Chambers reading
  Henslowe) are cited as what they are, each write-up saying whose evidence it relays; the primary works go on the leads list.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - working days (Q1; FR-001)

A new money question, its title asking how many days a year a worker worked. Built on 0250 (no count), 0115 (degawari) and 0260
(fares), with a pointer from each. Japan: live-in term farm servants' contract rest days (Kumon 2020: 2-4 a month, 310-330
working days, Harima, Kai and Kanto, 1780-1840; whether the ~11 national holidays came on top unclear, said); village rest days
(asobi-bi) from the summaries of 古川, about 20 a year around 1700 rising to 30-60 and in places 50-80 after 1800, not added to
Kumon's (the sources do not say a servant got both); yabuiri, 1/16 and 7/16, ATTESTED ONLY FOR those two days, "not limited to
these" said, no yearly total; porters SILENT on a count, the Meguro sukego evidence (official traffic peaked in the farming
season; travel time unpaid) and Oiso's 10-day office turns given as what they are; carpenters and day laborers SILENT on a count,
weather idling attested. China: the 250 days of Allen et al., Bassino and Ma, and Liu 2022 is an ASSUMPTION, quoted as one;
Qing accounts' notional 360 days a bookkeeping convention; Li and Pomeranz's 200 spinning days an estimate. Any days-worked
figure from rest days a month is this project's arithmetic, labeled. Against the canon: a weekly county market day, no working
calendar - the record names no weekly rest day for any worker (the rest days are monthly, festival and seasonal).

## D2 - terms of engagement (Q2; FR-001)

In 0307 (it holds the clerks and the Beijing agencies) or a sibling by size (0307's prose cap). Guards: China's escort-masters
kept on by the agency (board, lodging, about 4-5 taels a month undated and popular, a year-end share), 3-4 trips a year of about
three months (Chircop-Reyes 2018), hired out as house guards between trips, clients contracting the agency by trip, season or
year; Japan: cash went with the courier house's own convoy leader, who wore his own short sword; no armed escort hired for one
trip found (SILENT with the search); the by-the-job pattern ATTESTED ONLY FOR unarmed couriers with other trades (a rice-cake
maker, a tinker; 64 mon a run, 1852), the village courier on a yearly stipend. Scribes: China paid by the document (100-300
cash a plaint by official rate, 1796-1900; copying against composing); Japan kept on (the ward clerk from 1721, the village
courier), petition-writing by the case at the litigants' inns (fee SILENT); a scribe hired by the day SILENT. Against the canon:
scribes among the heimen.

## D3 - how often players performed (Q3 a-c; FR-001)

A new money question, its title asking how often players performed, with pointers from 0308, 0214 and 0187. (a) The city
playhouses: one program a day by daylight, no night playing before gas light (1878); the theatrical year of five or six named
programs from the kaomise (11th month, about 10 days) to the autumn farewell (9th month); a new program every month only after
1912; the 6th and 7th months idle by rule, later cheap summer plays; no play in rain; actors toured when fire shut the house;
narimono choji ATTESTED, its length SILENT; the puppet theaters' calendar SILENT; a castle town's permanent playhouse SILENT
unless the session finds one. (b) Shrine-ground licenses for 100 fair-weather days, granted each time, sometimes renewed back to
back; a provincial town's licenses a year SILENT (Kotohira's ~3 a year from 0214 the nearest). (c) Country troupes: festival
engagements of one to fifteen days (0308's Shima runs and Buhler's 1728 nine fair days and 15 shows by name, not repeated);
Hamanoichi's 15 runs in about 45 years; a troupe's engagements a year SILENT. China beside it: Beijing's theaters by day, no
night plays (c. 1800), troupes rotating among theaters every four days before 1900; village and temple-fair hires of about three
days, fairs of 1-15 days clustered in the 3rd-5th months; imperial mourning stopped plays. Against the canon: the county troupe
working market day and touring the villages the rest of the week is NOT ATTESTED - every rural source shows episodic festival
hires - and goes to the GM through `escalation-check` (D5).

## D4 - England, the GM's comparison (Q3 d; FR-001)

A new question in the "Comparative money" section, `subject=comparative,money`, its source kind `comparative` (Chambers 1923,
reading Henslowe's diary and the primary documents): one performance a day at 2 or 3 p.m., six days a week, no Sundays; 23 plays
in 18 weeks in 1592, the same play rarely twice a week; a new play about every fortnight (1594-97); 728 performances in three
years (about 243 a year, this project's arithmetic); Lent (about 37 days), summer breaks spent touring, plague inhibitions (play
allowed once deaths fell to 30 a week, c. 1604); the Blackfriars as the King's men's winter house from 1608. Marked as another
society's evidence under `research/CLAUDE.md` "Comparative money sources": never a Rokugani figure.

## D5 - the implementation check and the reply (FR-003, FR-004)

`implementation-check.md` holds each touched question's line; the reply on #20 gives each figure with its fragment file and
verdict, what is still open (the leads: 古川 1986 itself, Saito and Abe 1998, Li Bozhong 2008, Liu Jiansheng 2014, Hirai's
*Government by Mourning*, 『義太夫年表』, Greg's Henslowe), and the 250-day convention's standing (an assumption in every source
that uses it; the one count is farm servants' 310-330). The canon finding (D3) and anything else for the GM go through
`escalation-check` first.

## T01 - Q1 working days and Q2 terms of engagement (D1, D2)

### T01 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant knows how many days a year each kind of worker worked or was paid for, and how guards and scribes were engaged, and where the record is silent - so its 250-day convention can be kept, labeled, or replaced.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-3 (an assumed working year never reported as a count).
3. **Where each comes from.** O: the questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; each figure ATTESTED ONLY FOR its place, time and kind of worker.
5. **The order.** S1 write, C1 check (this clone), after the Q1 and Q2 passes.
6. **The exits.** A figure no source gives is SILENT with its search; 古川's figures cited only as the summaries that relay them.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the touched questions.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1, D2** As the sections "D1" and "D2" state. Rendering: none.

## T02 - Q3 performances and England (D3, D4)

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant knows how often each kind of troupe played - a day, a week, a year - with its idle months and closures, beside London's players, and how that stands against the canon's county troupe.
2. **The constraints.** The record's citation rules; the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the comparative-source rules for England; the spec's acceptance 1-3.
3. **Where each comes from.** O: the questions (`request.md`); G: research/CLAUDE.md ("Comparative money sources"), research/money-requests.md.
4. **Do they describe the world here?** Japan and China yes, each ATTESTED ONLY FOR its city, time and kind of troupe; England is another society's evidence, marked comparative, never a Rokugani figure.
5. **The order.** S2 write, C2 check (the -2 clone), after the Q3 pass.
6. **The exits.** A figure no source gives is SILENT with its search; a canon contradiction is reported, never softened, and goes to the GM through `escalation-check`.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the touched questions.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3, D4** As the sections "D3" and "D4" state. Rendering: none.

## T03 - the implementation check and the reply (D5)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify each answer, revisit its 250-day convention and close #20; the GM rules on the canon's county troupe.
2. **The constraints.** `make impl-check F=428`; `escalation-check` on what is for the GM.
3. **Where each comes from.** O: the questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 and T02 land.
6. **The exits.** None.
7. **The search smell.** None: research, not a fit.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=428` nothing missing; the reply posted; `make feature-report F=428 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** As the section "D5" states. Rendering: none.

# Feature 428: working days a year by kind of worker, and how often players performed (diagram#20)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-26, "the GM Assistant repo will have some money research tasks for you soon, so please watch GitHub for any new or updated issues"

The GM asked these questions in his own words (in full in `request.md`: "Do we have any indication of how many days per year
different types of laborers worked?"), and in this session sent this session to work them (quoted above); he asked for what gm-assistant files here
to be worked (2026-10-24: "anything that gets filed, go ahead and work it"), and a money research request gm-assistant opens for
him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (the issue body, verbatim).

## Why

gm-assistant's money skill turns a day's wage into a year's with a 250-day convention that 0250 found NOT ATTESTED (a laborer's
year = 1.89 kg of rice a day x 250 days / 151.5 kg = 3.12 koku). Wage dollars, laborer-days on every price sheet and any yearly
income built from a day rate (a guard's, a porter's, a troupe's) rest on it. The record holds no count of working days for any kind
of worker, no terms of engagement for a guard or a day-hired scribe, and no performance calendar for any kind of troupe.

## User Scenarios & Testing

1. **Q1, working days.** gm-assistant reads, for Tokugawa Japan with Ming and Qing China beside it, how many days a year each kind
   of worker actually worked or was paid for, and the regular days off: an unskilled day laborer (hiyatoi); a live-in servant
   (hokonin), and whether servants had fixed holidays (the yabuiri home-leave days, festival days); a post-station porter or
   packhorse driver, and whether stations kept them busy or idle between travelers, by season; a construction worker or carpenter
   (rain days, winter); a farm laborer by season. Each figure with its place and date.
2. **Q2, by the job or by the year.** It reads whether these were hired by the job or kept on all year, and what they did between
   jobs: an armed escort of goods or cash (and whether China's escort agencies' guards were salaried staff or hired per trip); a
   literate scribe or clerk (whether one could be hired for a day or two of writing - letter-writers, copyists, a temple's or
   village's hired hand). The terms of engagement (day, trip, season, year), and trips or jobs a year where recorded.
3. **Q3, how often players performed.** It reads performances a day, days a week and months a year, with seasons and closures, for
   (a) an Edo, Kyoto or Osaka kabuki or puppet theater with its own roofed playhouse (daytime or night, program length, the
   theatrical year and its seasons); (b) a troupe playing on shrine or temple ground in a provincial city (miyaji shibai), licensed
   for how many days; (c) a country troupe touring villages and a county town (engagements a year, days each); (d) for comparison,
   Shakespeare's company at the Globe (time of day, days a week, how often the bill changed, closures for Lent and plague).
   Japan first, China beside it, England as the GM's comparison.

**Acceptance**:
1. Every figure each question names gets a verdict - ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT -
   SILENT with its search; any arithmetic (a year's days from a count of holidays, a yearly total) is labeled this project's
   arithmetic. No source's assumed working year is reported as a count: where a study ASSUMES a number of days (as the wage
   comparisons behind 0250's 250 do), the answer says it is an assumption.
2. Each figure is given per kind of worker or troupe, with its place and date, in the unit the question names (days worked or
   paid a year, holidays a year, trips or jobs a year, performances a day, days a run, idle months).
3. Each answer says how it stands against the canon the request names (`l7r.md`'s weekly county market day and no working
   calendar; "Entertainers": the county troupe of about 5-10 making most of its money on market day and touring the village
   districts the rest of the week; provincial cities' competing troupes; a domain capital's entertainers tied to one
   establishment); a contradiction goes to the GM through `escalation-check`, and nothing edits the canon.

## Requirements

- **FR-001**: The findings are written in the "Money and prices" section under the citation rules: Q1 in a new question with a
  pointer from 0250; Q2 in 0307 or a sibling by size; Q3 (a)-(c) in a new question with pointers from 0308, 0214 and 0187 where
  they bear. Q3 (d), England, is a COMPARATIVE source (the GM asked for it): its own question in the "Comparative money" section,
  tagged `subject=comparative,money`, its source kind `comparative`, under `research/CLAUDE.md` "Comparative money sources".
- **FR-002**: The work runs in page sessions of at most four questions and ten new registry keys a write, each followed by a check
  session; search passes run first.
- **FR-003**: The reply on #20 gives each figure with its fragment file and verdict, what is still open, and how to verify; findings
  for the GM go through `escalation-check` first.
- **FR-004**: The feature closes with `make impl-check F=428` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-004): `make record CHECK=1` passes, `make record-owed` shows nothing unanswered for the touched
  questions and keys at landing, and `make impl-check F=428` reports nothing missing.
- **SC-002** (FR-003, Acceptance 1-3): a reply on #20 answers each of Q1-Q3 with every figure it names, or that figure's SILENT.

## Out of scope

- Editing the canon or gm-assistant's toolkit (the 250-day convention is theirs to change).

# Feature 428: working days a year by kind of worker, and how often players performed (diagram#20)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-26, "the GM Assistant repo will have some money research tasks for you soon, so please watch GitHub for any new or updated issues"

The GM asked these questions in his own words (in full in `request.md`: "Do we have any indication of how many days per year
different types of laborers worked?"); in this session he sent this session to watch for and work gm-assistant's money tasks
(quoted above - the approval guard admits only words the GM wrote in this session, so his question cannot stand on that line).
He asked for what gm-assistant files here to be worked (2026-10-24: "anything that gets filed, go ahead and work it"), and a money research request gm-assistant opens for
him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (the issue body, verbatim).

## Why

gm-assistant's money skill turns a day's wage into a year's with a 250-day convention that 0250 found NOT ATTESTED (a laborer's
year = 1.89 kg of rice a day x 250 days / 151.5 kg = 3.12 koku). Wage dollars, laborer-days on every price sheet and any yearly
income built from a day rate (a guard's, a porter's, a troupe's) rest on it.

What the record already holds, and what it lacks: 0250 has no count of a laborer's working days; 0115 has servants changing
households on two fixed days a year (degawari) and nothing on time off; 0260 has porter and horse fares per stage and nothing on
how steadily porters worked; 0307 has live-in merchant clerks on yearly wages and Beijing escort agencies paid yearly, but no day
pay for a hired scribe and no guard's terms in Japan; 0308 has city kabuki stars on yearly contracts from the 11th month and Shima
villages hiring puppet companies for three-day festival runs twice a year; 0214 has Kotohira raising a temporary playhouse about
three times a year before 1835; 0187 has plays on shrine and temple ground at festivals. Missing: any count of days worked or of
days off, the terms of engagement beyond those, and any performance calendar beyond those village festival runs - performances a day,
days a run for a city or shrine-ground troupe, idle months.

## User Scenarios & Testing

1. **Q1, working days.** gm-assistant reads, for Tokugawa Japan with Ming and Qing China beside it, how many days a year each kind
   of worker actually worked or was paid for, and the regular days off: an unskilled day laborer (hiyatoi); a live-in servant
   (hokonin), and whether servants had fixed holidays (the yabuiri home-leave days, festival days); porters, both post-station
   porters and packhorse drivers and porters hired by the job in towns, ports and markets, and whether they were kept busy or idle
   between jobs (by season); a construction worker or carpenter
   (rain days, winter); a farm laborer by season. Each figure with its place and date.
2. **Q2, by the job or by the year.** It reads whether these were hired by the job or kept on all year, and what they did between
   jobs: an armed escort of goods or cash (and whether China's escort agencies' guards were salaried staff or hired per trip); a
   literate scribe or clerk (whether one could be hired for a day or two of writing - letter-writers, copyists, a temple's or
   village's hired hand). The terms of engagement (day, trip, season, year), and trips or jobs a year where recorded.
3. **Q3, how often players performed.** It reads performances a day, days a week and months a year, with seasons and closures, for
   (a) a successful troupe with its own roofed (indoor) playhouse - the licensed kabuki and puppet theaters of Edo, Kyoto and
   Osaka first, and a castle town's permanent playhouse where one stood (daytime or night, program length, the
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

- **FR-001**: The findings are written in the "Money and prices" section under the citation rules: Q1 in a new question built on 0250,
  0115 (servants) and 0260 (porters), with pointers from each; Q2 building on 0307's clerk and escort-agency findings, in it or a
  sibling by size; Q3 (a)-(c) in a new question with pointers from 0308, 0214 and 0187 where
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

## Review history

- spec-fidelity round 1 (2026-10-26): CHANGES REQUIRED - (1) the Approved line quotes the watch instruction, not the question: NOT
  applied, because `feature-approval-hooks.sh` refuses any quote the GM did not write in this session (it refused his question from
  `request.md`, and `CLAUDE.md`'s 10-18 standing quote, by the 10-25 lint); the prose under the line now says so and quotes his
  question; (2) porters widened to all porters, Q3(a) named as a troupe with its own roofed playhouse, castle towns included:
  applied; (3) Why now says what 0115, 0260, 0307, 0308, 0214 and 0187 hold; FR-001 builds on 0115, 0260 and 0307: applied.
- round 2 (verify, 2026-10-26): CHANGES REQUIRED - item 1 accepted as not blocking (the guard admits no other quote); items 2 and 3
  resolved; one new item: Why's "Missing" sentence denied the village runs 0308 holds - applied ("beyond those village festival
  runs").

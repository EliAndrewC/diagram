# Feature 423: books, skilled wages, a smith's income, and entertainers' incomes and gear (diagram#19)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-25, "Do we know what books cost? To buy? To transcribe?"

The GM asked these questions in his own words (quoted above and in full in `request.md`); he asked for what gm-assistant files here
to be worked (2026-10-24: "anything that gets filed, go ahead and work it"), and a money research request gm-assistant opens for
him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (the issue body, verbatim).

## Why

gm-assistant's money skill prices books, skilled and trusted labor, a maker's yearly income and entertainers on guesses (its
estimates E0169-E0193, logged before this research so they can be graded against it). The record holds the unskilled day (0250),
skilled against unskilled (0275), the kitchen knife (0276) and plays (0266), but none of these four.

## User Scenarios & Testing

1. **Q1, books.** gm-assistant reads, for Tokugawa Japan with Ming and Qing China beside it, the price of a cheap popular booklet
   and of one bound volume of an ordinary classic, primer or reference work (with its leaf count); a lending library's charge a
   loan; a copyist's charge to copy by hand (per leaf, per volume, or a day's pay) and how many leaves a day one wrote.
2. **Q2, skilled and trusted labor.** It reads the wages of (a) a literate clerk - a merchant house's live-in clerk (tedai, banto)
   by seniority, and a scribe hired by the day; (b) an armed guard of goods or cash on the road - Japanese escorts, China's escort
   agencies (biaoju) - per day or per trip; (c) skilled servants - a household cook, a lord's noted cook, a lady's personal maid
   (a samurai house's jochu or koshimoto) - each with what came in kind (board, clothing).
3. **Q3, a maker's income.** It reads, for a Tokugawa (or Qing) blacksmith, ideally a village or town smith of farm tools: a common
   tool's price (a sickle, a hoe) against the iron and charcoal in it; how many tools or repairs a year; his gross takings and net
   income; how many apprentices or journeymen worked with him; and any other craft's yearly accounts (a carpenter-master, a
   cooper, a tailor) as a second case.
4. **Q4, entertainers.** It reads a traveling country troupe's takings per performance and per year and how they were shared; a
   street performer's daily take; a city star actor's yearly pay; a traveling or rural troupe's size (beside the city companies of
   about 43 and 26 in 0266); and the price of a stage costume (ordinary and fine), a shamisen, a bamboo flute and a hand drum
   (tsuzumi). Japan first - kabuki, rural troupes and Morisada's 『守貞謾稿』 - with China beside it.

**Acceptance**:
1. Every figure each question names gets a verdict - ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT -
   SILENT with its search; Japan first, China beside it; any arithmetic (a per-year total from a per-day wage, a unit or coin
   conversion) is labeled this project's arithmetic.
2. Each figure is given in the unit the question names (per booklet, volume, loan, leaf, day, trip, year, item) in silver or copper
   as the source states it, with the in-kind part of a wage named where the source names it.
3. Each answer says how it stands against the canon the request names (scribes among the heimen; stipend = rank squared for samurai
   clerks; servants and cooks hinin laborers; the ledger's unverified Kanazawa lead for servants and stewards - 0.7-1 koku a year, a
   young steward 3 - which the Q2 answer confirms, narrows or contradicts, its source traced and cited from the work it came from,
   never the ledger; smiths heimen craftsmen; the county troupe of about 5-10 entertainers earning most
   on market day; entertainers hinin), and gives figures gm-assistant's estimates E0169-E0193 can be graded against; a
   contradiction goes to the GM through `escalation-check`.

## Requirements

- **FR-001**: The findings are written in the "Money and prices" section under the citation rules: Q1 in a new question; Q2 in 0275
  or a sibling by size; Q3 in a new question beside 0276; Q4 beside 0266 or in it by size. Comparative sources (another society's
  money) only under the comparative rules, and only where the GM's question asks for them (it does not).
- **FR-002**: The work runs in page sessions of at most four questions and ten new registry keys a write, each followed by a check
  session; search passes run first.
- **FR-003**: The reply on #19 gives each figure with its fragment file and verdict, what is still open, and how to verify; findings
  for the GM go through `escalation-check` first.
- **FR-004**: The feature closes with `make impl-check F=423` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-004): `make record CHECK=1` passes, `make record-owed` shows nothing unanswered for the touched
  questions and keys at landing, and `make impl-check F=423` reports nothing missing.
- **SC-002** (FR-003, Acceptance 1-3): a reply on #19 answers each of Q1-Q4 with every figure it names, or that figure's SILENT.

## Out of scope

- Editing the canon or gm-assistant's estimates.

## Review history

- spec-fidelity round 1 (2026-10-25): CHANGES REQUIRED - Acceptance 3 left out the ledger's unverified Kanazawa lead; Scenario 4
  dropped Q4's named sources (kabuki, rural troupes, Morisada). Both applied.

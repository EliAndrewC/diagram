# Feature 431: the work a household did that was never paid, who did it, and how long it took (diagram#21)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future"

The GM asked these questions in his own words (in full in `request.md`), and gm-assistant filed them here for him: a money
research request gm-assistant opens for the GM is approved by his asking (the standing words quoted above).

**Input**: `request.md` (the issue body, verbatim).

## Why

gm-assistant's money toolkit prices a koku by what it buys and by the paid working days it stands for (0250's 250-day
convention, which 0311 found an assumption). Neither sees work that was never sold: a homemade robe cost a farm household no
coin but weeks of someone's time, and a tenement laborer bought what a farm wife made. The GM wants a Money page on that work,
and asked for an explicit note that women's household work was almost never written down at the time - itself a historical
fact about what we can know of premodern societies, and the reason some figures will be missing.

What the record already holds: 0311 (farm servants' 310-330 paid days, village rest days, Li and Pomeranz's estimate of at most
200 spinning days a year for a Chinese woman; no household time budget); 0004 (household size, who lives under one roof); 0209
(dyers and weavers as a trade); 0183 (side trades in towns and villages, as paid work); 0306 (a smith's pay, spinning in
passing). Missing: any time budget of unpaid work, a list of household tasks, hours to make cloth or a garment, what city
households bought instead, and the historiography of why the record is thin.

## User Scenarios & Testing

1. **Q1, a farm household's year by member.** gm-assistant reads, for a Tokugawa farm household with a Ming or Qing one beside
   it, how each member's days or hours (husband, wife, grown children, children, elders, any servant) split between fieldwork,
   side trades for sale and unpaid work for the household, and how that changed by season (slack winter, rain days,
   transplanting and harvest); failing figures, the off-season and night tasks (yonabe) a source names.
2. **Q2, the household tasks with their relative cost in time.** As near an exhaustive list as the sources allow - fiber, food,
   fuel and water, straw, house and tools, care, and whatever the sources add - with who did each and hours or days per task a
   year or per unit; and the GM's hypothesis tested in both halves: clothing the largest single claim on its maker's time
   (larger than fieldwork for any one worker), fieldwork larger in total.
3. **Q3, the fiber chain in hours.** Hours per stage (growing, preparing, spinning, weaving, dyeing, sewing) for a robe or a
   bolt (tan) in hemp, cotton and silk; a household's robes or bolts a year and how much cloth it bought. A measured modern craft
   or experimental rate is a COMPARATIVE source where no period figure exists.
4. **Q4, city households.** The GM's main question: home-work days or hours a year (or a share of the year) for a single
   laborer in a back tenement (nagaya), against a laborer or artisan with a family, or an extended family, in a house of their
   own - each with its verdict or SILENT with its search - and who in that household did the unpaid work (from 0004's
   household composition); what each bought that a farm household made (used clothing, cooked food, washing, mending, firewood,
   water), the trades that sold it and their prices.
5. **Q5, other workers' days off.** What a live-in servant, a merchant house's clerk, a guard or a porter did on days not
   worked for pay: rest, their own household's work, or a side trade; and their home-work days or hours where any account
   gives them.
6. **Q6, the proverb.** Whether a Chinese (or Japanese) proverb says that no one who rises before dawn 360 days a year will fail
   to make the family rich; its original text, or SILENT. If found, whose saying it was (the kind of source and its audience:
   farm households, merchants, scholars), which tests the GM's guess that it is a farming proverb; if not found, that question
   stays open.
7. **Q7, why the record is thin.** What historians say about why women's unpaid household work in Tokugawa Japan and Ming/Qing
   China was rarely recorded, with author, and which kinds of source they use to reconstruct it.

**Acceptance**:
1. Every figure each question names gets a verdict - ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT -
   SILENT with its search; any arithmetic (a year's hours from a rate, a robe's days from a bolt's) is labeled this project's
   arithmetic; a study's assumption or estimate is reported as one, never as a count.
2. Each figure is given per member, task or stage with its place and date, Japan first and China beside it.
3. The record says explicitly, where figures are missing for women's household work, that such work was rarely written down at
   the time and that this is why (the GM's addendum), citing Q7's historians where they say it.
4. Each answer says how it stands against the canon (`l7r.md`); a contradiction goes to the GM through `escalation-check`, and
   nothing edits the canon.

## Requirements

- **FR-001**: The findings are written in the "Money and prices" section under the citation rules, in new questions as the
  material divides (expected: the household's year and its tasks; the fiber chain; city households; why the record is thin),
  Q5 extending 0311 and Q6 where it fits, with pointers from 0311, 0004, 0209, 0183 and 0306 where they bear. A Europe or
  modern-experiment figure is a COMPARATIVE source in the "Comparative money" section, tagged `subject=comparative,money`, under
  `research/CLAUDE.md` "Comparative money sources".
- **FR-002**: The work runs in page sessions of at most four questions and ten new registry keys a write, each followed by a
  check session; search passes run first.
- **FR-003**: The reply on #21 gives each figure with its fragment file and verdict, what is still open, and how to verify;
  findings for the GM go through `escalation-check` first.
- **FR-004**: The feature closes with `make impl-check F=431` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-004): `make record CHECK=1` passes, `make record-owed` shows nothing unanswered for the touched
  questions and keys at landing, and `make impl-check F=431` reports nothing missing.
- **SC-002** (FR-003, Acceptance 1-4): a reply on #21 answers each of Q1-Q7 with every figure it names, or that figure's SILENT.

## Out of scope

- Editing the canon, and building the Money page (gm-assistant's).

## Review history

- spec-fidelity round 1 (2026-10-26): CHANGES REQUIRED - (1) Q4 names home-work days or hours a year for both city households,
  Q5 the same where any account exists; (2) Q6 reports whose saying the proverb was, testing the GM's farming guess; (3) Q4
  says "a family, or an extended family" and who in it did the unpaid work: all applied.

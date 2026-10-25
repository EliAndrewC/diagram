# 412-money-basket-every-era - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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

<!-- plan-archive: archived 2026-10-24 -->
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
   and `make money-candidates` does not list (its coins are Japanese). The coin keys are gm-assistant's to name: asked on #13
   (issuecomment-6390793368, proposing `tael`, `cash`, `dollar`) before this task closes. With keys confirmed, the Chinese
   amounts are marked against the awaiting Chinese eras as the Japanese ones were, and `make money-candidates` is extended to
   list them; with a deferral gm-assistant confirms on #13, each Chinese question is passed over in `backfill.md` with that
   reason and the comment's URL.
5. **The order.** After the ids are confirmed; a session of its own (s5) in its own clone.
6. **The exits.** Passing an amount over with its reason in `backfill.md`.
7. **The search smell.** None.
8. **The budget.** One session.
9. **Done, measured.** `make money-candidates CHECK=1` exits 0; `make record-owed` names nothing the marks caused; the
   Chinese amounts marked under the keys gm-assistant confirmed, or a deferral it confirmed on #13 cited in `backfill.md`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D5** As the section "D5 - the era marks" states. Rendering: none.


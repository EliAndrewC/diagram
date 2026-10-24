# Feature 412: the standard basket's prices, wages and coin rates in every era the record draws on (diagram#13)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files on this repository to be worked (his words, quoted above); a money research request
gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as
automatic approval, and therefore you should not ask in the future").

**Input**: `request.md` (issue #13, verbatim), `passes/` (the census of the record's priced eras and the search passes,
2026-10-24)

## Why

gm-assistant converts every historical amount on the research site into goods dollars, wage dollars and Rokugani coin (feature
413 shows it). That needs one standard basket priced in each era and place the record cites, an unskilled day wage there, and
the era's coins in grams of pure silver. Two eras are built (Kyoto 1745-54, Tokyo 1882-86); salt, fuel and housing in the
reference era are guesses. The issue asks four questions to fill the rest.

## User Scenarios & Testing

### User Story 1 - each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue's four questions - (1) salt, fuel and a room in Kyoto or Osaka 1745-54, and salt
per person per year; (2) the basket's goods in every era and place the record cites; (3) an unskilled day wage in each; (4)
each era's coins in grams of pure silver - the fragment file, the verdict and what is still open.

**Acceptance scenarios**:

1. Each verdict is one of the four of `research/money-requests.md`. Question 1 asks for "the nearest dates found": a figure
   from outside 1745-54 or from another city is ATTESTED ONLY FOR <its place and years>, the gap stated - unlike feature 411,
   whose issue asked for each figure's own place and period (its FR-005).
2. The eras of question 2 are the record's own: a census of every price, wage and coin rate the money questions state, by
   place and years (`passes/census.md`), names them; each era gets an id in gm-assistant's `<place>-<first year>` form.
3. An era priced from an official schedule (the Qing 物料價值則例) says so: its prices are ATTESTED ONLY FOR official rates.
4. Figures are laid out per era so gm-assistant can type them into its era files: place, years, coins in grams of pure
   silver, each good's price in the era's money with its unit and source, the day wage.

### Edge cases

- A price per bundle of firewood is converted to a price per million BTU only with the bundle's weight from a source; where the
  weight is this project's assumption, the per-BTU figure is labeled as its arithmetic.
- Japan's monme was a weight of chogin whose fineness changed at each recoinage: grams of pure silver per monme are given per
  recoinage, not computed from the copper rates of 0277.
- Nothing here moves the rice anchor (1.49 g a kg) or rules on the koku's weight; a source that bears on either is listed
  under what is still open.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #13, its fragment file, its verdict and what is still open.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names; question 1's figures in 0273 (salt), 0279 (fuel) and 0265 (rent), question 3's in 0250,
  question 4's in 0277 or a companion question, question 2's in a new money question that tables the basket per era.
- **FR-003**: Every amount in the record's fragments (not only the money questions) whose era this feature defines is marked
  for feature 413's tooltip with that era id; each era defined is added to `research/assets/money-eras-awaiting.json` (413
  FR-008) until gm-assistant's table carries its row.
- **FR-004**: The feature closes with `make impl-check F=412` (money questions: no code implements them).
- **FR-005**: Replies are posted on #13 at each landed batch; gm-assistant verifies and closes it.

## Success Criteria

- **SC-001** (FR-001, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open in a reply
  on #13.
- **SC-002** (FR-002, FR-004): `make record-owed` shows no unanswered unit for the touched questions at each landing, and
  `make impl-check F=412` reports nothing missing.

## Assumptions

- Japan first for prices and wages, China beside it (the issue's order).
- The session count is set once the passes are counted against the ten-new-key cap of a write session.

## The findings, figure by figure

(filled from the passes)

## Review history

# Feature 422: miso and soy sauce in the basket, and which goods the opening changed in Edo 1860-67 and Beijing 1900-19 (diagram#18)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-25, "yes go with your recommendations for the Meiji, and yes let's switch the basket to the recorded prices"

The GM's words, relayed by gm-assistant in `request.md`, ask for this work; he asked for what gm-assistant files here to be worked
(2026-10-24: "anything that gets filed, go ahead and work it"), and a money research request gm-assistant opens for him is
approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (the issue body, verbatim).

## Why

The GM ruled that the standard basket's 52 kg of soybeans a year (Bassino and Ma's basket A, which 0249 says stand for miso,
soy sauce, tofu and natto) switch to the miso and soy sauce prices the Mitsui Kyoto books record for 1745-54 (feature 420,
0249). That needs quantities, which gm-assistant will not guess, and prices in more eras than Kyoto 1745-54. The GM also ruled
that a good foreign trade visibly changed is excluded from Rokugan's cross-era mean (applied to Tokyo 1882's kerosene and linen);
the same rule is to apply to Edo 1860-67 and Beijing 1900-19 on evidence.

## User Scenarios & Testing

1. **Q1.** gm-assistant reads how much miso (kg) and soy sauce (liters) an ordinary adult of a laborer's household in Kyoto or
   Osaka used in a year in the mid-1700s, or the nearest time and place with a figure; if no consumption figure exists, how much
   soybean goes into a kg of miso and a liter of soy sauce in Edo-period practice, and what share of a household's soybeans went
   to miso, soy sauce, tofu and natto; and the source of Bassino and Ma's 52 kg.
2. **Q2.** It reads whether the Mitsui books (Edo and Osaka from 1818, Kyoto from 1791) or any other series price miso or soy sauce
   in any era it holds, and whether the Chinese eras price soy sauce or bean paste (jiang 醬), each as grams of silver a kg or a
   liter per era in 0286's and 0302's format.
3. **Q3.** It reads the cheapest plain household pack at a national US retailer of miso (white or red, by the kg) and of naturally
   brewed soy sauce (by the liter), in the snapshot rule's sense, each with its link and the date seen.
4. **Q4.** It reads, per era and good, whether foreign trade after the opening visibly changed the price - Edo 1860-67: rice, salt,
   lamp oil, firewood, soybeans, barley and wheat, cooking oil; Beijing 1900-19: rice and millet - with the evidence, or not
   changed, or SILENT; and why Tokyo 1882's soybeans stand at 0.65 times rice, below every Tokugawa era's 0.89-1.43 (the opening,
   a grade difference, or something else).

**Acceptance**:
1. Every figure each question names gets a verdict - ATTESTED, ATTESTED ONLY FOR <the narrower case>, NOT ATTESTED or SILENT -
   SILENT with its search; a quantity no source gives is never estimated by this project, and any arithmetic from a source's
   figures (a per-adult share of a household's figure, a unit conversion) is labeled this project's arithmetic.
2. Q2's prices are in 0286's format (grams of pure silver a unit at the era's coin, label, source); a price already in the record
   is pointed to, not copied.
3. Q3's prices are dated observations with their links, archived, under the comparative rules.
4. Q4's verdict for each good is "changed" only where a source shows foreign trade moving that good's price (an export pull, an
   import's competition, a trade-driven price series), never inferred from the timing alone; a price that moved for another
   stated cause (the recoinage, a harvest) is said so.
5. Each answer says how it stands against the canon the request names: the GM's two rulings (the basket switch; keep the food,
   exclude a good trade visibly changed).

## Requirements

- **FR-001**: The findings are written in the "Money and prices" section under the citation rules: Q1 in a new question beside 0249
  (or in 0249 if it fits the size cap), Q2 in 0301 and 0302 (or a sibling, by size), Q4 in a new money question; Q3 in 0299,
  comparative, never a Rokugani price.
- **FR-002**: The work runs in page sessions of at most four questions and ten new registry keys a write, each followed by a check
  session; search passes run first.
- **FR-003**: The reply on #18 gives each figure with its fragment file and verdict, what is still open, and how to verify;
  findings for the GM go through `escalation-check` first.
- **FR-004**: The feature closes with `make impl-check F=422` (money questions: no code implements them).

## Success Criteria

- **SC-001** (FR-001, FR-002, FR-004): `make record CHECK=1` passes, `make record-owed` shows nothing unanswered for the touched
  questions and keys at landing, and `make impl-check F=422` reports nothing missing.
- **SC-002** (FR-003, Acceptance 1-5): a reply on #18 answers each of Q1-Q4 with every figure it names, or that figure's SILENT.

## Out of scope

- Changing the basket or the conversion table: gm-assistant's.
- Estimating a quantity no source gives.

## Review history

- spec-fidelity round 1 (2026-10-25): FAITHFUL. Carried forward: Q1's tofu-and-natto remainder of the 52 kg is owed in the
  answer whether or not consumption figures are found (Acceptance 1, the request's "Figure needed").

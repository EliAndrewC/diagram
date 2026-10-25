# Feature 419: England's premodern prices as a comparative yardstick (diagram#15)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files here to be worked (his words, quoted above), and his answer on #15, "yes" (relayed by gm-assistant, `request.md`), approves what feature 414's acceptance 3 held back: England's
premodern series are "not sought out unless the GM asks for it or approves it" (research/CLAUDE.md, "Comparative money
sources"). A money research request gm-assistant opens for him is approved by his asking (GM 2026-10-18: "you should treat
features that I have asked to be filed as automatic approval, and therefore you should not ask in the future").

**Input**: `request.md` (the GM's answer, verbatim).

## Why

Feature 414 measured both English series (`specs/414-price-stability/passes/modern-yardstick.md`, section 2) and wrote only
the modern fiat-era yardstick (0291), because a premodern European series needed the GM's approval. With it given, the
record can set the Edo and Qing figures (0290) beside a third commodity-money society that players know from novels: little
drift over centuries, a big swing from year to year.

## User Scenarios & Testing

1. gm-assistant, or a player, reads in the "Comparative money: other societies" section how steady English prices were under
   commodity money: the long-run drift (per year over each period, and by century) and the year-to-year swing of the whole
   price level, from the Bank of England's millennium dataset, and of single goods (grain, salt, fuel, cloth, a building
   laborer's wage) from Clark's English prices and wages.
2. The same reader finds each figure set beside its Edo and Qing counterpart (0290) and the modern one (0291) in the measure
   those pages use, and reads that none of it prices anything in Rokugan.

**Acceptance**:
1. Both sources are in the registry with the kind `comparative`, archived, and cited only by questions of the Comparative
   money section (`make record` enforces it); `source-applicability` judges them on England's own terms.
2. Every figure computed from a series is labeled this project's arithmetic, names the series, the place and the measure (the
   standard deviation of annual log changes; the drift as the mean log change a year), the years and how many year pairs it
   rests on, and is reproducible from a script in `specs/419-england-price-yardstick/measure/` with its output beside it.
3. Each source's stated limits are carried: the Bank of England column's own source note (and that its years before 1661 are
   Clark's index rescaled, labeled as this project's check); Clark's file's own caveat, that his series are subject to
   revision; Lindert's note that he interpolated the silver price of the pound for 1699, 1702-1709 and 1711-1717 (carried only
   if a figure uses that series); and the years each goods series is missing, which Acceptance 2's count of year pairs shows.
4. The page says, in its own words, that these are yardsticks for players and never the basis of a Rokugani price (the GM's
   words, `request.md`).

## Requirements

- **FR-001**: The findings are written into the record under the citation rules, as ONE new question in the "Comparative
  money: other societies" section (tagged `subject=comparative,money`), because 0291's title is about paper money and these
  series are commodity money; 0291's "Beside the premodern figures" and its source comment point to it. Checked by the
  record checks `make record-owed` names.
- **FR-002**: Every figure carries its arithmetic label and script (Acceptance 2); the reply on #15 gives the drift and swing
  with their fragment file and says how to verify the landing.
- **FR-003**: The feature closes with `make impl-check F=419` (a money question: no code implements it).

## Success Criteria

- **SC-001** (FR-001, FR-003): `make record CHECK=1` passes and `make record-owed` shows no unanswered unit for the touched
  questions and sources at landing; `make impl-check F=419` reports nothing missing.
- **SC-002** (FR-002): each script in `measure/` reproduces its committed output; a reply on #15 says where the figures are
  and how to verify them.

## Out of scope

- English wage or price LEVELS converted for players (what a laborer's day was worth in shillings): the GM's answer asks for
  the yardstick of stability, not a conversion; a later request may ask for one.
- Any other European series (Munro, Rolnick and Weber, Jacks et al., Albers et al.): the GM named two sources. Rolnick and
  Weber are already in 0291.

## Assumptions

- The data files measured on 2026-10-24 (the Bank of England xlsx, sheet A47; the GPIH Clark xls) are re-fetched and
  archived; if either has changed, the figures are re-measured from the archived copy.
- One write session and one check session (one question, two new keys).

## Review history

- spec-fidelity round 1 (2026-10-25): CHANGES REQUIRED - Acceptance 3 named an interpolation caveat the Clark file does not
  state; replaced with the file's own caveat, Lindert's silver-price note and the missing years. Applied.
- round 2 (verify): FAITHFUL.

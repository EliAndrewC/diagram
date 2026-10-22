# Feature 410: charcoal, ordinary and fine white (diagram#11)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-22

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-22, "Thanks. After that lands, please take a look at GitHub issue number 11."

The GM asked for issue #11 to be worked (his words, quoted above); a money research request gm-assistant opens for him is
approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (issue #11 verbatim), `passes/` (two search passes, 2026-10-22: Japan; Ming/Qing China)

## Why

gm-assistant's money skill prices charcoal by its own guess (a ~15 kg bale of black 13-32 sen retail, white 3-4x; an
ox-cart of ~33 bales delivered). The record holds bale weights only for Iburi, Hokkaido, undated and by grade (0197 and 0199: the best 4 kan, the next 10,
a lower 8), no Edo-period bale weight, and the kilns (0079), but no price.

## User Scenarios & Testing

### User Story 1 - Each figure the issue asks for has a verdict and a fragment (Priority: P1)

gm-assistant reads, per figure of the issue - black and white charcoal by the bale (with its weight), retail and
wholesale; retail by small measure in a city; the white-to-black ratio; burner-days per bale and the yield of charcoal from wood; what carriage added; a Ming/Qing comparison - the fragment
file, the verdict and what is still open. Every figure the findings below answer is in that list: retail by small measure in
a city, the yield of charcoal from wood, and burner-days per bale included.

**Acceptance Scenarios**:

1. Each figure is written into a money question beside the craftsman's and the unskilled laborer's day wage of the same
   place and period, or, where no source gives one, that wage is SILENT with the nearest in the record named.
2. What the record already holds (0197's and 0199's Iburi bale weights) is named by file, not repeated.
3. Each verdict is one of the four of `research/money-requests.md` (ATTESTED, ATTESTED ONLY FOR, NOT ATTESTED, SILENT). A
   figure for which only a nearest exists (another fuel, place or century) is SILENT, the nearest named under "what is still
   open" with the leads not tried, and the search in the absence note; a combined price says what it covers.

### Edge Cases

- A source that gives a price per weight (kan, jin) and not per bale: the price stays per weight; a bale equivalent, where
  given, is the project's arithmetic at a named weight (e.g. 4 kan, 0197's Iburi best grade, undated, Hokkaido), labeled.
- No price is converted to koku; between coins only by a rate the source gives or 0277's, labeled.

## The findings, figure by figure (the passes, 2026-10-22; leads until read on the page)

All go into a new money question, 0279 "What did charcoal cost?" (Japan first, then the Qing comparison).

- **Charcoal by the bale (Japan)**: ATTESTED ONLY FOR an ordered price per bale in Edo, 1842, by grade names that do not
  say black or white - Ōishi 1966's table of the price-cut order reported by the ward headmen: 上炭 500 -> 466 mon, 中炭 448
  -> 422, 下炭 364 -> 342, 佐倉炭 144 -> 135 (its 中/下 132/120 -> 124/112); no bale weight printed. Open: whether it is
  retail or wholesale, and whether black, unless the page says so. Beside it, the nearest wages in 0275 (Edo 1830s-50s,
  carpenter 5-5.5 monme, tobi 300 mon), named as the nearest.
- **The bale's weight**: the record holds no Edo-period bale weight - 0197 and 0199 give Iburi (Hokkaido), undated, by
  grade: 4, 10 and 8 kan. The Itsukaichi bulletin gives Tama bales of 4, 5 or 6.5 kan, undated, and a Meiji 20s (1887-96)
  record of 5 kan; 0279 states these and names 0197 and 0199.
- **Retail by small measure in a city**: SILENT in the passes. Open: Morisada's 炭売 (the 生業 sections, pid 991466) and
  『商人職人懐日記』.
- **White charcoal, and white against black**: ATTESTED ONLY FOR white against white - 1716, through Mitamura Engyo
  (Itsukaichi bulletin): Kumano (binchotan) 400-500 mon a bale, 8-9 bales a ryo, against Hachiōji (Tama, all white) about
  20 bales a ryo. Japan's black-against-white ratio SILENT. Qing comparison: Beijing 1736's official list, 白炭 1.1 against
  黑炭 0.5/0.6 tael per 100 jin (about 2:1, arithmetic), with the same list's craftsman 154 and laborer 75 cash a day.
- **Wholesale at the kiln, by boat or cartload**: SILENT; open: the 飯能 1822 charcoal brokers' agreement; the brokers' levy of 8 (later 12) mon per
  8-bale horse-load is a tax, not a price; 809,710 bales came to Edo by ship in 1726 (second hand).
- **Labor per bale, yield**: SILENT on burner-days and wood-to-charcoal yield; an undated modern statement gives 20-30
  bales an earth kiln of black in 3-4 days against 2-3 bales a stone kiln of white - ATTESTED ONLY FOR that general
  statement.
- **Carriage to the city**: SILENT on the fee (open: the same 飯能 agreement); carriers and horse-loads (6-8 bales) described, no amount.
- **Ming/Qing comparison**: ATTESTED ONLY FOR official assessed prices - Beijing 1615 and 1736 (Gao 2022), Zhili 1769 by
  district (Bochum, 木炭 0.0018-0.008 tael a jin beside each district's 匠 and 夫 wages), 武編's Ming smithing costs.
- **Nearest only**: Akita 1600, 181 kanmon for 120 bales of smith's charcoal (pre-Edo) - named, not an answer.

## Requirements

- **FR-001**: Every figure of the issue gets, in the reply on #11, its fragment file, its verdict and what is still open.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names, in a new money question (or questions) tagged as the money section's are.
- **FR-003**: The feature closes with `make impl-check F=410` (money questions: no code implements them).
- **FR-004**: The reply is posted on #11; gm-assistant verifies and closes it.
- **FR-005**: A nearest figure is not an answer: each verdict is one of the four of `research/money-requests.md`; a figure
  the record holds only a nearest for is SILENT, the nearest and the leads not tried named under "what is still open".

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every figure of the issue carries a fragment file, a verdict and what is still open
  in the reply on #11.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make
  impl-check F=410` reports nothing missing.

## Assumptions

- Japan first; Ming/Qing China as comparison (the issue's region order).

## Review history

- spec-fidelity round 1 (2026-10-22): CHANGES REQUIRED - 0197's bale weight misstated (Iburi, by grade, undated; with 0199);
  retail by small measure missing; OPEN is no verdict (the four of money-requests.md, nearest under "still open"); the
  1842 table filed as black retail without the source saying so. All four applied, and in plan D1 and the write brief.
- spec-fidelity round 2 (2026-10-22): FAITHFUL - all four round-1 items fixed in the spec, plan D1 and the write brief.

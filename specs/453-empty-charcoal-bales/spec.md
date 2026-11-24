# Feature 453: what an empty charcoal bale cost, who wove it and how long it took (diagram#23)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-24

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future"

The GM asked this session to work the research requests filed as issues (2026-11-24: "Please take a look at our GitHub issues because there are a number of research requests which I would like for you to handle."); a money research request
gm-assistant opens for him is approved by his asking.

**Input**: `request.md` (issue #23 verbatim), `passes/a-bales.md` (one search pass, 2026-11-24)

## Why

gm-assistant's money skill prices a bale of charcoal (0279: 15-21 sen for a black-charcoal bale of about 4 kan) and has nothing on the bale
itself: the woven bag, its end caps and ropes, bought empty. The record holds what charcoal cost (0279), the straw work a farm household
did unpaid (0312) and what became of straw after the harvest (0332), but no price for an empty bale, no account of who wove charcoal bales
and no time to weave one.

This feature records only the history. What an empty bale costs in Rokugan stays with the money skill and the GM.

## User Scenarios & Testing

### User Story 1 - Each part of the issue's question and each figure it needs has a verdict and a fragment (Priority: P1)

gm-assistant reads, for each part of the issue's one question and each figure it needs, the fragment file, the verdict and what is still
open: the price of an empty charcoal bale bought on its own; who made them (the burners themselves, or village straw-workers in winter as
by-employment); how long one took to weave; whether they were traded as a separate good, by the hundred, to charcoal makers or dealers; the
neighbors the issue names where charcoal bales are silent (rice bales, and other straw goods: straw mats, sandals, rope); China's
equivalent, the basket or matting charcoal was packed in, and its price; and the three figures - sen, mon or laborer-days per empty bale,
laborer-hours to make one, and what share of a full bale's price the bale was.

**Acceptance Scenarios**:

1. Each part and each figure carries one of the four verdicts of `research/money-requests.md` (ATTESTED, ATTESTED ONLY FOR, NOT ATTESTED,
   SILENT). A figure for a neighboring good, place or century is not an answer to the figure asked: that figure is SILENT, the nearest named.
2. Each price stands beside the same place and period's day wage where a source or the record gives one, and says where the wage comes from;
   a wage of another place or decade is named as that.
3. What the record already holds (0279, read first as the issue asks; 0199 and 0197 on the charcoal bale itself; 0312, 0332, 0283), from
   `grep -lIiE '俵|tawara|charcoal bale|straw bale|炭俵|明俵' research/questions/*.html`, is named by file, not repeated.
4. Japan comes first, then Ming and Qing China as comparison, as the issue orders.

### Edge Cases

- An empty bale whose kind the source does not state (明俵) is recorded as that, never as a charcoal bale.
- A text read only through machine reading of a handwritten manuscript is cited only where the passage was read on the page image.
- A 20th-century figure (an oral account, a ministry survey, a 1935 standard) is given with its date and does not carry an Edo-period verdict.
- Any division of one source's figure by another's is this project's arithmetic and is labeled so, with the two dates and places.

## The findings, figure by figure (the pass, 2026-11-24; leads until read on the page)

- **Price of an empty charcoal bale bought on its own, Edo period**: SILENT. The nearest: empty bales of unstated kind (明俵) bought by Edo's
  wards for flood dikes and relief sheds - 6 mon a bale in 1802 beside a laborer's 124 mon a day; 8-12.5 mon in 1806 beside 2.5 monme of
  silver a day; 10-11 mon in 1808 - ATTESTED ONLY FOR empty bales of unstated kind in Edo in those years. One monme a bale at Hamura beside a
  2-monme day, dated by the pass's inference to 1868-69, outside the window. The kiln cost account read (the Washizawa official charcoal,
  1796-1868) carries carriage and no bale or rope line.
- **Who made them**: ATTESTED ONLY FOR Nippara village in the Tama hills, 1814 (the women wove the bales from the village's kaya grass while
  the men burned, a gazetteer quoted in a local-history article). Village straw-workers weaving charcoal bales in winter as by-employment, for
  sale: an undated 20th-century memoir from Tosayama only, so SILENT for the Edo period. Men twisting rope and weaving mats between farm work
  is in a Musashi village account the record already cites. The Nippara passage bears on 0197's GUESS that charcoal was baled at the kiln,
  and the new question says so.
- **Material**: kaya grass for the body in 1814, ATTESTED ONLY FOR that village; straw-rope ties, brushwood end caps and a 2.5 kg tare in a
  1935 Tokyo standard, modern. Straw bodies: the record holds 0199's straw bale and Iburi's charcoal rolled in straw mats (undated), named by
  file. Reed bodies: SILENT in the pass.
- **How long one took**: SILENT for the Edo period. The nearest are 20th-century: 14-15 woven pieces (not finished bales) in a short winter
  day in Okutama folklore, and under an hour a bale at Tosayama. Laborer-hours per bale is therefore SILENT, those two named.
- **Traded as a separate good**: SILENT for charcoal bales in the Edo period (the Tosayama memoir, 20th century, the nearest). The nearest Edo
  figures: empty bales of unstated kind bought by the hundreds and thousands 1802-1808; 5,000 empty rice bales to be bought from the city's
  rice dealers in 1859; the Kodenmacho jail selling its empty bran bales in the 1840s-60s, ATTESTED ONLY FOR those kinds.
- **Share of a full bale's price**: SILENT for the Edo period. The nearest: packing at 4.6-6.5% of the white-charcoal price, Japan, 1914-26,
  and 10-13% of production cost in 1933 (ministry surveys, the first a division by this project); the Beijing basket below.
- **Neighbors**: straw mats 25 mon each in a Mino village in 1765 beside a farm laborer's 60 mon a day, about 29-30 mon in Edo in 1806 and
  0.3-0.6 monme in 1840-42, used mats at 83-92% of new; komo matting 16-37 mon a sheet (Edo 1842); rope about 3 mon a bundle (Hanno 1763) and
  67-70 mon a larger bundle (Edo 1806); earth bags 0.041 monme each beside a 1.2-monme day (Osaka castle works, 1628). ATTESTED. Sandals,
  kamasu sacks and rice bales woven in a day: SILENT. An empty rice bale's price as such: SILENT (the 1859 order names no price).
- **China**: ATTESTED ONLY FOR Beijing, 1736 - a basket holding 60 jin of black charcoal at 0.0195 tael and one holding 10 jin at 0.0066, a
  large cattail-matting bag at 0.01, beside a laborer's 75 cash a day at 800 cash to the tael; by this project's division the basket is
  5.4-6.5% of its charcoal. Ming charcoal packing: SILENT.

## Requirements

- **FR-001**: Every part of the issue's question and every figure it needs gets, in the reply on #23, its fragment file, its verdict and what
  is still open.
- **FR-002**: The findings are written into the record under the citation rules (`research/CLAUDE.md`), checked by the record checks `make
  record-owed` names, in a new money question tagged as the money section's are, with `subject=money` first, pointed at from 0279.
- **FR-003**: The feature closes with `make impl-check F=453`. No engine code decides a bale's price (`grep -rnIi -E 'sumidawara|tawara|charcoal
  bale|empty bale' l7r pool rust`, run in the write session and recorded in `implementation-check.md`).
- **FR-004**: The reply is posted on #23; gm-assistant verifies and closes it.
- **FR-005**: A nearest figure is not an answer: each verdict is one of the four; a figure the record holds only a nearest for is SILENT, the
  nearest and the leads not tried named under "what is still open".
- **FR-006**: Findings state the history as found. No fragment says what a bale costs in Rokugan.
- **FR-007**: Each price stands beside the same place and period's day wage where one is found, the wage's source said; two sources that
  disagree are both given; a figure from one source only says so.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every part and figure of the issue carries a fragment file, a verdict and what is still open in the
  reply on #23.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make impl-check F=453`
  reports nothing missing.
- **SC-003** (FR-006, FR-007): no fragment states a Rokugani price, and every price that has a wage beside it names where the wage comes from,
  as the check rounds read them.

## Review history

- spec-fidelity round 1 (2026-11-24, MODE 2): CHANGES REQUIRED - 0199 and 0197 missing from what the record holds, and the list's search unnamed; the separate-trade verdict taken from a neighboring good. Both applied.
- spec-fidelity round 2 (2026-11-24, verify): FAITHFUL - both round-1 items resolved.

## Assumptions

- One new question holds it (the pass's material is well under the 20,000-byte cap); if the write session finds it does not, it splits along
  Japan and China.
- The leads the pass names and did not read (地方凡例録 vol. 9's standard allowances, 牧民金鑑, 守貞謾稿 and the 御仕置例類集 cases on the
  empty-bale buying trade, the farm manuals' work rates) are tried once in the write session; one still unreadable is named as open.

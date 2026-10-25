# Implementation Plan: gold, silver and copper as separate monies (feature 416, diagram#16)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-24

## Summary

A research-record feature: two new money questions - A gold, silver and copper as monies in Edo Japan, B silver and copper as
monies in Ming and Qing China - each answering the issue's four questions, written from the two passes (`passes/japan.md`,
`passes/china.md`), each passage read on its page before it is cited; two write page sessions and one check-and-apply session,
run in the sibling clone after features 412 and 414's; then the reply on #16. No code, map or canon change.

## Technical Context

- **The record.** `make page-session` in `/diagram/.clones/diagram-money-pages`, briefs `briefs/s1-write.md` (A), `s2-write.md`
  (B), `s3-check.md`.
- **PDFs the reader could not read** (Oishi 1966 - the archive holds only HTTP 406 stubs, re-archive it; Iwahashi 2010; Kano;
  Kobayashi 2017; Morse 1908 on archive.org): downloaded with curl into an empty directory, read with pdftotext, quoted as the text
  layer gives it with garbled characters bracketed; page images (`IMAGES=`) to the checks where the text layer is garbled.
- **Named, not repeated**: 0277 (Japan's legal rates of 1700 and 1842, the Osaka and Edo market series, the 1843 floor); 412's coin
  questions (chogin fineness, koban gold, nanryo and ichibu-gin silver against face; cash a tael by era); 414's (copper wages
  against the rate); 0265 (rents, both ways).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - question A, Japan (FR-001, FR-002, FR-003)

The four questions in order. (1) The legal rates of 1609, 1700 and 1842 and who set them, enforcement as the orders print it
(Oishi's 1842 order, the 1813 order, the 1796 purchases and 1829 sales, Ooka's summons of 1736), a prosecution SILENT; the market's
straying by period; the fixed-by-count ladder (ryo = 4 bu = 16 shu; the five-monme piece, the nanryo, the ichibu-gin) and what it
did to weighed silver; the changers' resistance to the nanryo. (2) The pattern by transaction kind and region - wholesale against
retail, gold in the east against silver in the west, wages, rents (0265, both ways), taxes (in koku, rice and money in shares;
the Kanto's ei), samurai stipends (rice through the fudasashi), shop purchases (copper) - and the fees attested (the 1859 recall,
the nanryo allowances, the fudasashi), the uncited "1-2%" said to be uncited. (3) Edo 1842's copper-only cuts; Tsugaru's coin and
note prices; Edo 1854-1868's different values for one face; the Tenpo coin at about 80; premia for old full-weight coin;
Sengoku's discounted bad coin; a premium for paying in gold searched (金払い 打歩, 小判 増歩, 金建て 値引), SILENT with the search
if none; how fast copper prices followed the rate outside 1842 SILENT (the Japan pass searched; feature 414's series cannot
answer it, Mitsui's prices being in silver). (4) The four groups the issue names - wage earners in copper, taxpayers, merchants,
samurai on stipends - in the episodes the issue names and those the sources measure: the Meiwa iron and brass coins (copper from
about 4,000 to 6,000 mon a ryo, 1769-1778; Oishi tying the fall to the Tanuma-period risings), the Tenpo recoinage and copper's
fall of the 1830s-1840s (Edo craftsmen's copper wages not falling with rice after 1836; the 1842 orders; the Tenpo coin's slide),
the Bunsei, Tenpo and Man'en recoinage gains, the 1860s silver-west real wage (Saito 1993); for each, the real-wage and
tax-burden effect where a source gives one, SILENT with the search where none (a Meiwa-An'ei real wage in copper; a Japanese tax
burden measured in any episode); and what people did. Against each question's canon (FR-003): question 1, Rokugan's fixed
decimal coinage (`l7r.md` "Money"); question 2, the money skill's "Coins and who uses them"; question 3, the conversion table,
which converts each coin through its era's rate into silver and then by the basket - and the request's consequence, that if
copper prices were sticky a mon amount should be measured against copper prices instead, said where the findings bear on it;
question 4, none yet, as the request says. Stated as material for the GM to decide what to import, escalated through
`escalation-check`.

## D2 - question B, China (FR-001, FR-002, FR-003)

The four questions, Qing first and Ming where found. (1) The 1645 and 1653 rates, the 1684 ban, the 1702 discount for old coin,
the 1737 brokers and treasury releases, the drift to about 2,000 by 1837; the Xianfeng notes and big cash, their legal rates and
collapse; Ming paper's legal rate (1375, gold 1:4 against silver), its fall, the bans and their lifting. (2) Silver for tax, salt
levies, official pay and long-distance trade; copper for retail, household salt, labor and materials; the 1436 commutation and the
Single Whip; the weight and fineness standards against the treasury tael and the banks' spreads (Morse, late Qing - dated as
such); rents both ways (0265); a retail cash shop's fee SILENT. (3) Sticky copper prices (salt 1728, rice about 1850, wages from
414) and 朱嶟's dissent; payment-dependent prices in Xianfeng Beijing; light coin at 70%; paying in gold - the Ming bans and rate,
the Qing case searched (金價 折算 交易, 黃金 兌換 銀 清代, 赤金 市價), SILENT if none. (4) Taxpayers (Zeng Guofan's doubling; the
Henan conversion of 1905), officials, the state's arrears, soldiers; merchants and wage earners - 414's inference only, said so.
Against each question's canon as D1, question 3's conversion table included (Qing copper prices sticky while the silver rate
doubled is the case the request names).

## D3 - the implementation check (FR-004)

`implementation-check.md` holds each new question's line (no code implements a price).

## D4 - the reply (FR-001, FR-003, FR-005)

A comment on #16: per figure the issue asks, the fragment FILE, the verdict and what is still open; per question, how the answer
stands against its canon, and any escalation.

## T - the order

1. The page sessions (s1, s2 write; s3 check). 2. The implementation check. 3. The reply and the landing.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->

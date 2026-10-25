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

## T01 - question A, Japan's three monies (D1)

### T01 Approach (checklist part A)

1. **The goal, in the world.** The GM can read how gold, silver and copper worked as separate monies in Edo Japan - the legal
   rates and how far the market strayed, which metal paid for what and where, whether prices depended on the coin, and who gained
   and lost when the rates moved - to decide how much of it Rokugan's fixed decimal coinage imports (0295).
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or an absence note); the 20,000-byte
   question cap; `make record-owed` clean; the four questions of #16 in order; each set against its canon (FR-003); the canon
   not edited.
3. **Where each comes from.** O: the issue (`request.md`); G: research/CLAUDE.md, research/money-requests.md; G: the canon
   (`l7r.md` "Money") read, not changed.
4. **Do they describe the world here?** Yes; a fee computed from a rate is labeled this project's arithmetic, and a reading one
   source gives (Kano's fee, Iwahashi's premium) is set beside the other.
5. **The order.** Write (s1), check and apply (s3), the round-3 tail closed by the arbiter (ask:416-round4, accept), then the
   marks (s4).
6. **The exits.** SILENT with the search where no source answers (a premium for paying in gold; a prosecution; a Meiwa-An'ei real
   wage in copper; a measured tax burden), not a borrowed figure.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0295; `make money-candidates CHECK=1` exits 0.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** As the section "D1 - question A, Japan" states. Rendering: none.

## T02 - question B, China's silver and copper (D2)

### T02 Approach (checklist part A)

1. **The goal, in the world.** The same four answers for Ming and Qing China (0296): the legal cash rates and their enforcement,
   the Xianfeng notes and big cash, Ming paper; silver for tax and long-distance trade against copper for retail and wages; sticky
   copper prices while the silver rate doubled; taxpayers, officials, soldiers and wage earners in the silver crisis.
2. **The constraints.** As T01's.
3. **Where each comes from.** As T01's.
4. **Do they describe the world here?** Yes; a late-Qing standard (Morse) is dated as such, and a second-hand report is labeled
   ATTESTED ONLY FOR one.
5. **The order.** Write (s2), check and apply (s3), marks (s4).
6. **The exits.** SILENT with the search (paying in gold under the Qing; a retail cash shop's fee; a measured real wage); the wage
   earners' case is feature 414's inference, said so.
7. **The search smell.** None.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0296; `make money-candidates CHECK=1` exits 0.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D2** As the section "D2 - question B, China" states. Rendering: none.

## T03 - the implementation check (D3)

### T03 Approach (checklist part A)

1. **The goal, in the world.** The GM can see no code decides a coin's worth, so no claim is owed.
2. **The constraints.** research/CLAUDE.md (feature 378): each new question's line in `implementation-check.md`.
3. **Where each comes from.** G: research/CLAUDE.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=416`: nothing missing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D3** As the section "D3 - the implementation check" states. Rendering: none.

## T04 - the reply on #16 (D4)

### T04 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant and the GM can take every figure of #16 from the reply alone.
2. **The constraints.** FR-001 (per figure: fragment file, verdict, what is open), FR-003 (each answer against its canon), FR-005;
   GM items through `escalation-check` first.
3. **Where each comes from.** O: the spec's FRs from the issue; G: CLAUDE.md (escalation-check before the GM).
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages, the marks and the implementation check.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** One reply.
9. **Done, measured.** The comment's URL.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D4** As the section "D4 - the reply" states. Rendering: none.

## T05 - close: report and land

### T05 Approach (checklist part A)

1. **The goal, in the world.** The findings on main, the report written.
2. **The constraints.** `make land`'s refusals; `make feature-report F=416 WRITE=1`.
3. **Where each comes from.** G: CLAUDE.md, Development workflow.
4. **Do they describe the world here?** Yes.
5. **The order.** After the reply.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Landed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- none beyond D1-D4. Rendering: none.

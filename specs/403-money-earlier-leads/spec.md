# Feature 403: the earlier money answers' open leads, written in (0250, 0259, 0260, 0262, 0265, 0270)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-19, "I'm going to sleep now and would like you to finish all of the outstanding research tasks relating to the new money skill overnight, so please keep working at that."

The GM asked for every outstanding money research task to be finished; feature 402's request.md lists these leads (the
answers on #3, #6 and #7) as outstanding under the same instruction and not covered by 402, so this feature is approved by
his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and therefore
you should not ask in the future").

**Input**: `request.md` (the GM's words and the open leads), `passes/` (two search passes, 2026-10-19)

## Why

The answers on #3, #6 and #7 left leads unfollowed. Two passes followed them: Morisada (public in NDL's viewer) prices
inns, soba and sake and describes Edo rent; Gamble's Beijing day wages (1807-1902) and the Zhili freight rates are
public. The rest were searched and are not publicly readable or give nothing.

## User Scenarios & Testing

### User Story 1 - The record's money questions carry the found figures (Priority: P1)

**Acceptance Scenarios** (each figure ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT):

1. **0259, a night at an inn:** Morisada (類聚近世風俗志 上, koma 79-80): Kyoto and Osaka first-class inns 3 monme 5 bu
   of silver with two meals, low-grade about 200 mon; Edo about 248 mon with two meals; Osaka's beggars' lodging 36 mon,
   no bedding; the Tokaido 200 mon and Nakasendo 148 before Ansei, 700-800 by Keio. ATTESTED, each with its city and date
   as Morisada gives it; his date for each is 1837-53 unless the text says otherwise.
2. **0262, sake and soba:** Morisada (上 koma 74-76, 137; 下 koma 229): the best sake a sho, Osaka 164 mon and Edo 200-248
   in his childhood (he was born in 1810), 350-400 from about Tenpo; Edo good morohaku about 250 "thirty years ago", now
   350-400; one go 40 mon on an Edo soba board; a bowl of soba 16 mon in Edo and Kyoto-Osaka, raised in Keio to 20 then 24
   in Edo; the price boards' other dishes; 3,763 Edo soba shops in 1860. Cursive item names on the price boards are the
   record's reading, said so.
3. **0265, rent:** Morisada (上 koma 57): Edo rent paid monthly to the yanushi; the move-in fee (tarudai) 2 shu to 10 ryo,
   against Kyoto-Osaka's chit for 1-2 sho of sake; festival payments; a Tenpo order banning both. ATTESTED ONLY FOR the
   system; a monthly amount stays SILENT in Morisada.
4. **0250, an unskilled laborer:** Gamble's rural Beijing day wages, 1807-1902, as reprinted in LSE working paper 123
   (archived), ATTESTED ONLY FOR one fuel store's hands, food extra, with the change in cash units around 1860 stated.
5. **0260, a horse or a porter:** the Zhili 1769-era official freight rates (Bochum chapters 1 and 13), ATTESTED ONLY FOR
   official building work, only after the per-li / per-100-li label is settled on the scanned original; otherwise left out
   and named in the absence note.
6. **0270, a shrine's metal furnishings:** 『高岡史料』 (NDL pids 899934, 899935, public) read at its 関野神社 section for
   the 1833 mirrors' cost; a sum found is cited, otherwise SILENT naming it.
7. **Closed as not publicly readable** (named in the absence notes where the question touches them): the 宿村大概帳 print
   edition (NDL-only), Koyaizu's 『近世賃金物価史史料』 (NDL-only), the Mitsui and Miyamoto Osaka price books (login or
   NDL-only; the series "from 1757" is soybeans, not cotton), Gamble 1943 and Ting Hsien (paywalled, restricted), the
   Okamoto papers (the mirror donor's letters). Sewing, used clothing, a hand mirror, paper and ink: SILENT in Morisada.

Each new figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them; where none does, the question says that wage is SILENT and names the nearest. A figure the project
computed is labeled as the project's arithmetic. No price is converted between coins unless its source converts it or
0277's rates are applied and labeled.

### User Story 2 - The asker learns of the change (Priority: P2)

A note on GitHub names the changed fragment FILES, each changed verdict, the leads closed as not readable, and what is
still open.

## Requirements

### Functional Requirements


- **FR-001**: 0250, 0259, 0260, 0262, 0265 and 0270 MUST carry the figures and verdicts of User Story 1, each from a
  passage read on its page.
- **FR-002**: Each changed question MUST pass the record's checks on what changed.
- **FR-003**: `make impl-check` closes with a "no code implements it" line per changed question.
- **FR-004**: The asker is told on GitHub (on EliAndrewC/diagram#9, opened for 402 and 403): the changed fragment FILES, each changed verdict, the leads closed as not publicly readable, and what is still open.
- **FR-005**: Nothing changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The questions build and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004): The note names the changed files, each changed verdict, the closed leads and what is still open.
- **SC-004** (FR-005): The feature's diff touches no file under `l7r/`, `pool/` or the GM's canon.

## Assumptions

- Six questions, few new keys: one write session, continuation if the key cap is passed.
- Koyaizu's nail prices (Hirayama 2019) answer nothing asked and are not written in; noted as found.

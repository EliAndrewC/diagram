# Feature 404: the Hunan edition's porter and boat rates, written into 0260

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-19, "I'm going to sleep now and would like you to finish all of the outstanding research tasks relating to the new money skill overnight, so please keep working at that."

The GM asked for every outstanding money research task to be finished; 0260's Qing porter rate is one feature 403 left
open (named on EliAndrewC/diagram#9), so this feature is approved by his asking (GM 2026-10-18: "you should treat features
that I have asked to be filed as automatic approval, and therefore you should not ask in the future").

**Input**: `request.md`, `passes/zhili-ch13.md`

## User Scenarios & Testing

### User Story 1 - 0260 carries a Qing official porter rate whose unit is read on the original (Priority: P1)

**Acceptance Scenarios**:

1. **The Hunan rows:** 0260 gives the Hunan edition's porter rate (80 jin, per li, 0.003 tael) and boat rate (100 jin,
   per 10 li, 0.002 tael) for 長沙/善化, read on the scan's page images (PDF pp. 38-39 of 卷一) and quoted verbatim with
   the rows' note; ATTESTED ONLY FOR official building-work reimbursement in Hunan, dated as the edition states it
   (Qianlong; 1769 only if read on its pages).
2. **Wages beside them:** the same edition's craftsman's and laborer's day wage for 長沙/善化 if its scan gives them (read
   and quoted); otherwise SILENT naming the search, and the nearest named with its class, place, unit and gap in years. A
   porter's 100 li in days is the project's arithmetic.
3. **The Zhili rows:** stay out. The rewritten absence note says no public scan of the Zhili original was found
   (Tsinghua's copy is the one cited; searched in NLC, Internet Archive, Commons and the National Archives of Japan),
   quotes the Bochum chapter 13 rows its claim rests on - at least 青縣 28b (車運, 船運 labeled 里) against 29a (夫運,
   馬騾驢馱運 labeled 百里), the same figures - and says the Hunan original writes its unit row by row (per li for the
   porter, per 10 li for the boat), so a single unit column cannot be assumed; it chooses no unit for Zhili.
4. **The pack animal:** stays without an official rate: Hunan 卷一's 長沙/善化 運價 rows (pp. 38-39) are two items only (its
   note: 以上貳欵), and Zhili's are left out; said so in the note.
5. **Reads retried:** Moll-Murata, Song and Vogel (eds.) 2005 (Google Books) and the HathiTrust search, which failed on
   2026-10-19 (quota; Cloudflare challenge), are retried; read, what they give is used (they settle Zhili's unit only if
   they reproduce the original's rows); still failing, they are named with the failure and both dates. Leads still open
   named: the Jiangsu edition (National Archives of Japan), the Hunan scans 卷2-8.

### User Story 2 - The asker learns of the change (Priority: P2)

A note on EliAndrewC/diagram#9 names 0260, the changed verdict, and what is still open.

## Requirements

### Functional Requirements

- **FR-001**: 0260 MUST carry User Story 1's figures and verdicts, each read on its page image.
- **FR-002**: 0260 MUST pass the record's checks on what changed, and source-applicability on the new source.
- **FR-003**: `make impl-check` closes with a "no code implements it" line for 0260.
- **FR-004**: The asker is told on EliAndrewC/diagram#9.
- **FR-005**: Nothing changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): 0260 builds and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004): The note names 0260, the changed verdict and what is still open.
- **SC-004** (FR-005): The feature's diff touches no file under `l7r/`, `pool/` or the GM's canon.

## Assumptions

- One question, one or two new keys: one write session and one check session.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 3 items.** The pack animal's verdict stated; the Bochum ch.13
  rows quoted in the rewritten note (403's owed item); Moll-Murata and HathiTrust retried or named with the failure and
  dates, and "not public" narrowed to "no public scan found" with the places searched.

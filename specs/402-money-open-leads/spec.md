# Feature 402: the money answers' open leads, written in (0273, 0275, 0276, 0277)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-19

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-19, "I'm going to sleep now and would like you to finish all of the outstanding research tasks relating to the new money skill overnight, so please keep working at that."

The GM asked for every outstanding money research task to be finished; these are the leads the answers on #5 and #8 left
open, so the feature is approved by his asking (as a requested feature, GM 2026-10-18: "you should treat features that I
have asked to be filed as automatic approval, and therefore you should not ask in the future"). 402 covers the open leads
of the #5 and #8 answers only; the other answers' unfollowed leads (#3, #6, #7) are outstanding under the same instruction
and are listed in `request.md` for a further feature, so landing 402 does not finish the instruction.

**Input**: `request.md` (the GM's words and the open leads), `passes/` (four search passes, 2026-10-19)

## Why

The money skill was told three things were SILENT that public sources in fact give: a seventeenth-century day wage, the
Edo copper rate year by year to 1842, and an Edo price of Ako salt. The record should hold them, and say plainly which
leads were searched and found nothing.

## User Scenarios & Testing

### User Story 1 - The record's money questions carry the found figures (Priority: P1)

**Acceptance Scenarios** (each figure ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED or SILENT):

1. **0276, a kitchen knife:**
   - **The wage beside Mimasaka 1665:** the "SILENT; nearest 1741/1749" becomes ATTESTED ONLY FOR other places of the same
     silver coinage: a Kyoto carpenter at 1.8 monme with rice (1653, Myoshinji's account via Hirai 2007; reading it as a
     day's rate is the record's reading, the page having no 一日), the 1656 bath account's carpenters and day laborers (a
     per-day rate from its totals is the project's arithmetic), and Osaka's day laborers of the 1620s (Kitano). A wage of
     Mimasaka or Okayama stays SILENT. The knife beside them in days is the project's arithmetic.
   - **A sharpener's fee:** stays SILENT for a kitchen knife or razor, now with Morisada's 磨師 entry cited for the trade
     (it sharpened kitchen knives; no fee) and Uwajima's 1662 sword-polishing tariff given as ATTESTED ONLY FOR swords.
   - **A wage of Mimasaka or Okayama:** SILENT only after 『藩法集1 岡山藩』's 賃銀雑事 chapter is read, if public; if it
     cannot be read, the verdict names it as an unread lead.
   - **Inui's papers** (Takefu 1980, Sakai 1972): not publicly readable, said so in the absence notes; Kawashima's one line
     on Inui stands.
2. **0275, a skilled craftsman against a laborer:**
   - **An Edo pair:** "SILENT" stands only after 類聚近世風俗志 is searched for an Edo carpenter's and an Edo day laborer's
     wage (the #5 answer named 朝倉編『守貞謾稿』 pp. 159-161 as the lead), by the routes of the salt search in scenario 4 (0273); a
     pair found there is written into 0275 with its verdict, any ratio the project's arithmetic. If 下 cannot be searched,
     the verdict names it as an unread lead, not SILENT.
3. **0277, copper coin in silver:**
   - **The Edo market rate:** "SILENT" becomes ATTESTED ONLY FOR 1781-1842, Oishi's printed yearly table (low and high mon
     per ryo, from Mitsui's table "centered on Edo"); that it is Edo's rate is the record's reading of his method, said so.
     Decade summaries from it are the project's arithmetic. 1842-1852 is blank in the source (the official 6,500 only),
     and the 1850s stay SILENT.
   - **The series past 1842:** 新稿両替年代記関鍵 and 校註両替年代記 are NDL-restricted and 新保 1978 is not online; the
     absence note names them as the sources for a market series past 1852.
4. **0273, salt:**
   - **Edo, Ako salt:** "SILENT" becomes ATTESTED ONLY FOR the Edo brokers' (下り塩仲買) selling price of 1791, 9 to 9.5
     bales per ryo, a bale of 35 sho nominal and about 32 actual as the page reads (3斗5升, 3斗2升); per sho is the
     project's arithmetic. The bale's actual measure (3斗2升) is given only if read on the page image.
   - **Edo retail by the sho, and an Edo salt price of 1800-1850s:** SILENT only after 類聚近世風俗志 is searched for them:
     上 (pid 991466) and the 1934 one-volume edition (pid 1444386) by NDL's full-text search, which worked for them; 下
     (pid 991467), whose full-text routes refused, page by page in NDL's viewer, or by 1444386 once its NDL record or a
     read of its contents shows it holds the whole text. A figure found is cited with its verdict; if 下 cannot be
     searched, the verdict names it as an unread lead, not SILENT. The wholesalers'
     commission (3 monme a ryo, of which 1 to the brokers) may be given if read on the page image.

Each new figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and period where a
source gives them; where none does, the question says that wage is SILENT and names the nearest, with its class, place,
unit and gap in years. A figure the project computed is labeled as the project's arithmetic. No price is converted between
coins unless its source converts it or the record's own rate question (0277) is applied and labeled.

### User Story 2 - The asker learns of the change (Priority: P2)

gm-assistant's money skill took 0273, 0275, 0276 and 0277 in when #5 and #8 closed. A note on a new EliAndrewC/diagram issue
(or on #8, reopened only if the asker prefers) names the changed fragment FILES, each changed verdict, the leads closed as not
readable and what is still open, so the skill can move its rows.

## Requirements

### Functional Requirements

- **FR-001**: 0273, 0275, 0276 and 0277 MUST carry the figures and verdicts of User Story 1, each from a passage read on its page.
- **FR-002**: Each changed question MUST pass the record's checks on what changed: source-reader, quote-check,
  translation-check, record-format, intro-check, and source-applicability on each new source.
- **FR-003**: The feature MUST close `make impl-check` with a "no code implements it" line per changed question.
- **FR-004**: The asker MUST be told on GitHub: the changed fragment FILES, each changed verdict, the leads closed as not
  publicly readable, and what is still open after this feature (`research/money-requests.md`).
- **FR-005**: Nothing in this feature changes engine code, a map, or the GM's canon.

## Success Criteria

- **SC-001** (FR-001, FR-002): The four questions build, and `make record-owed` names no unanswered check.
- **SC-002** (FR-003): `make impl-check` reports nothing missing.
- **SC-003** (FR-004): The note names the changed fragment files, each changed verdict, the closed leads and what is
  still open.

## Assumptions

- The edits fit one write session (four questions, a few new keys).
- The verdicts above are the search passes'. The write may narrow them; it may not widen them without a source.
- The 磨師 entry is in 類聚近世風俗志 上 (NDL pid 991466), public online, so the sharpener needs no scan. The salt and wage
  searches cover 下 as well, by the routes in User Story 1.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 4 items.** The closed leads (Inui, 新保 1978, the 両替年代記
  books) written in; Morisada searched for Edo salt retail and an Edo wage pair (0275 added) before SILENT, and the Okayama
  藩法集 read or named; the note names the closed leads and what is still open; request.md and the approval paragraph say
  402 covers #5 and #8 only, the other answers' leads listed as outstanding. Aside taken: 3斗2升 only if read on the image.
- **spec-fidelity round 2 (2026-10-19, verify): CHANGES REQUIRED, 1 item.** 下's full-text routes refused in the salt
  pass, so the Morisada clauses name the route for 下 (viewer page by page, or 1444386 once shown whole) and fall back to
  "unread lead"; the Assumptions bullet matched and the unlabeled scan size dropped.
- **spec-fidelity round 3 (2026-10-19, verify): CHANGES REQUIRED, 3 items + 1 lesser, all wording.** The write brief's
  Morisada paragraph and the plan no longer call 991467 full-text searchable; the 0275 clause points at scenario 4; the
  request's summary line matches the passes.

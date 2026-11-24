# Implementation Plan: what distance did to the price of traded goods (feature 454, diagram#24)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-11-24

## Summary

A research-record feature answering the issue's questions from the search passes in `passes/` (`passes/a-ratios-japan.md`, `b-ratios-china.md`,
`c-margins.md`, `d-sea-freight.md`, `e-ships.md`). Five write sessions (and their continuations under the key cap), each followed by a
check-and-apply session, one after another in this clone (`/diagram/.clones/diagram-research`), in the issue's priority order: question 1
(Japan, then China), question 3, then questions 2 and 4. One queue, because the sources overlap between parts (Kibe on Hagi's rice ships,
Matsuura on the sand junks, Gutzlaff, the Amoy customs survey) and sequential sessions reuse a registry key without naming it twice. Each
pair is landed on its own. Then the reply on #24. No code, map or canon change.

## Technical Context

- **The passes are leads, not citations**: each write session reads every passage on its page before citing it, through `make archive-find`
  and `make source-pages`.
- **PDFs and scans**: the passes read many PDFs by downloading them and extracting their text, because `make source-pages` logged them
  NOT-CHECKED; several tables (Ball 1848, Fortune 1852, Timkowski, Gutzlaff, the Satsuma law collection, the 1842 Edo price lists, Kibe's and
  Kudo's tables) were read from scrambled machine text. The session that cites one reads it on the page image and gives it to the checks
  with `IMAGES=` or an archive copy.
- **Ledger rows to supersede**: pass A recorded pages that bear on the question as nothing-found or rejected (Seijo jpn-039-04, Kito
  fe.sophia 53-03, Shimane 38042/4947, Yamagata 75_moriya, iwt_11 and Graduation_Thesis); the write session that cites one records
  `cited:<key>` over it.
- **The question count and the write cap**: nine new questions (D1 2, D2 1, D3 2, D4 2, D5 2), each under 20,000 bytes of prose. Each write
  session takes at most four questions and ten new registry keys; `make reserve`'s eleventh key sends the rest to a continuation write
  session, and no finding is dropped for the cap.
- **Conversions**: a coin's silver from 0287 (Japan) and 0289 (China), a koku of burthen as the source converts it, a distance from the
  source or, failing one, measured and labeled as this project's.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` stays green. XVI: built as
  the spec's FRs.

## D1 - both ends' prices in Japan (issue question 1; FR-001, FR-002, FR-005, FR-006, FR-007)

Two new money questions. One on raw silk and iron: Kyoto against Maebashi and the Fukushima district, with Shinshu's silence; the Harima
ironworks' cost against Osaka, labeled a cost estimate, with Izumo and Iwami's producer-end figures and their silence as a pair. One on
sugar and tea: Satsuma's black sugar in the rice-exchange terms and the two silver figures that disagree; Ryukyu, Sanuki and Awa's silence;
tea's silence, with Uji's fixed price and Edo's retail prices as what they are, and the three tea leads tried once. The neighbors (safflower,
rice; spices, incense woods and medicinal roots SILENT) go with the question whose route they share. Each good: source units, the ratio, the
distance and how it traveled, grams of silver per kg as labeled arithmetic, and what the source says made up the gap. Point at 0282 and 0283.

## D2 - both ends' prices in China (issue question 1; FR-001, FR-002, FR-005, FR-006, FR-007)

One new money question: tea from the hills to Canton and to Shanghai with the gap itemized, and Beijing's silence as a pair; raw silk's
silence with the far-end prices named; sugar from Taiwan with its freight share and no Suzhou price, and the Takow-Yokohama account as a
Japanese port; Guangdong sugar's silence; spices, incense woods and medicinal roots as one-end prices only. Points at D1 and at 0283's
Bohea tea, which it does not repeat.

## D3 - what a trader kept (issue question 3; FR-001, FR-002, FR-005, FR-006, FR-007)

Two new money questions. One on the wholesaler: commissions by good, the buying house's markup, the fish wholesalers' net share, the net
margin's silence, China's brokerage silence and the Hong merchants' margin on tea. One on the shipowner trading on their own account: the
return per voyage in ryo and its silence as a percent of cargo, against carrying for hire; voyages a year; the split with captain and crew;
loss to wreck; the single Chinese cargoes; and the interest on cargo money beside the canon's rates.

## D4 - sea freight (issue question 2; FR-001, FR-002, FR-005, FR-006, FR-007)

Two new money questions, Japan and China: each route's rate in source units and voyage days; the Osaka-Edo rate's silence beyond 0280's
sake figure; the request's freight figure (silver by weight and distance) as labeled arithmetic where a distance can be stated; the comparison with 0280's river and
pack-horse rates. A pointer from 0280.

## D5 - coastal ships (issue question 4; FR-001, FR-002, FR-005, FR-006, FR-007)

Two new money questions, Japan and China: burthen by class and period, crew by size, crew pay, build cost, working life, and charter's
silence with how hire was paid; the essay's disputed author and the two unreconciled state rates both given.

## D6 - the implementation check, the reply and the report (FR-001, FR-003, FR-004, FR-008)

`implementation-check.md` holds each new question's line (`no code implements it`, with the search). The reply on #24 gives, question by
question and figure by figure in the issue's priority order, the fragment file and the verdict, what is still open, and the issue's canon
quotations beside the history. Anything for the GM goes through `escalation-check` first, and nothing here edits the canon.

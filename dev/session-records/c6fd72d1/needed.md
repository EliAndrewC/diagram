# Was each pop-up's before-version wrong? 449 record bundles, 2026-11-23 (read-only)

**Method.** The 30 listed edits are B1 = 085f4598c3 (10 pop-ups) plus 0108968f8c (day-office), and B2 = cce80ca436 (19). They cover 26 pop-ups.
- Each pop-up went to its own blind opus judge, four at a time. A judge saw only each edit's BEFORE, AFTER and diff, plus the HEAD text of every cited `.html` and `.drawing.html`. It saw no commit, message or reason.
- I checked every quoted contradiction against the page at the landing commit, not at HEAD, and overrode two verdicts (marked OVR).
- The judges were blind, but I saw the list's short edit-label column. Reading the listed day-office edit as 0108968f8c is (inferred).
- Bundles are in `tmp/needed-bundles/`, verdicts in `tmp/needed-verdicts/`, and the rule test is `tmp/rule-echo.py` with its output in `.out`.

## Tally
Precedence for an edit's or pop-up's class is CORRECTION > WORSE > COMPLETION > WORDING. Metadata lines (Sources, Entry) are left out.

| unit | CORRECTION | WORSE | COMPLETION | WORDING | total |
|---|---|---|---|---|---|
| passages | 30 (23 firm, 7 minor or borderline) | 1 | 29 | 9 | 69 |
| edits (the 30) | 20 | 1 | 6 | 3 | 30 |
| pop-ups (26) | 18 | 0 (garden-pond also has the WORSE) | 5 | 3 | 26 |

Each listed edit and its class:
- **COMPLETION:** compound-shrine, inner-court B1, main-gate, notice-board, garden and cell.
- **WORDING:** sacred-tree, servants--quarters and clerks--room. For clerks--room (OVR), the judge's weak CORRECTION is overturned: 0113 makes the "permanent memory" reading only for Chinese clerks, but canon `/host-l7r-repo/setting/budgets.md:652` says "as the office's permanent staff they provide continuity across successive magistrates".
- **WORSE:** garden-pond B2.
- **CORRECTION:** the other 20.

Outside the list, the 085 day-office edit came out WORDING 4 and COMPLETION 2. armory, writing-rooms, official-study B1 and the later T375 edits were not judged.

## The CORRECTIONs and the page edit behind each
I traced these myself without the list's 24/6 labels, so the caller can intersect the two. 16 are page-traced and 4 were wrong before the landing.

**(a) A page sentence reversed: 0090 in cce, 7 edits.** "the residence stood beside the office, on the lot to the west" and "a deliberate simplification" became "at the back of the office" and "follows Takayama, ... One case is all it rests on". The edits are court-divider, family-quarters, inner-court B2, nakamon, office-hall (Depiction only; its "beside ... lot to the west" was judged WORDING), outer-court and residence (2 of its 3 passages).

**(b) A page claim narrowed: 4 edits.**
- karo B1: 0106.drawing in 085 changed "Every plan labels" to "The hand-drawn plans label ... program-drawn ... without the gloss".
- karo B2: 0106 in cce changed "its staff lived inside the compound's walls" to "junior officials, the tetsuki and tedai", and "head of that staff" to "head of its tedai". The new page 0331 (Omori) adds to it.
- weir_form--frame and hamlet/weir: 0059 in cce changed "the joints" to "some joints".

**(c) A new block falsified an absence or only-case claim: 5 edits.**
- kitchen B2 and door (2 passages, borderline): 0107 in cce added the jaanus blocks: the kitchen door "often stood at the back", the tradesmen's entry, and "led onto the doma". Residence's roof passage comes from the same blocks, but residence is counted under (a).
- barracks and retainers--quarters: 0097 in cce added the Sakai doshin "one to a man", which falsifies "the one case found".
- official-study: 0113 in cce added "the intendant ordinarily worked ... in the residence", which is absent at cce^. Its second CORRECTION, "away from the armory", rests on the post-landing T392 note, so I counted it WORDING (OVR).

**(d) Wrong before the landing: 4 edits (inferred).**
- genkan: 0104.drawing already called the porch's block "the genkan's door" at cce^. cce rewrote that block.
- garden-pond B1: 0103 already said Okutono is "a restoration".
- day-office 0108: 0113's "kakiyaku-beya, was where the documents ... were drawn up" was already there at 085^.
- kitchen B1 (mixed): 0118's katte has predated it since 01375a8ee0, and 085 also added "a kitchen yard" to 0091.
- karo B2's family sentence (a borderline passage) also predates the landing: its 0106 sentence did not change.

## Live defect (found, not fixed)
garden-pond, from cce through HEAD, says in its Guesses: "the pond is taken as the office's form, since both government offices ... kept one". This contradicts 0103.drawing, which makes the form a knob "rolled from its seed" and says "The two offices read that had a pond were far grander than a county post". It also contradicts the pop-up's own Depiction: "Each plan takes one of the two forms". The before-text was correct. No current pop-up still carries the reversed or narrowed claims I grepped for ("beside the office", "rather than behind", "staff lived inside", "the joints tied", "every plan labels").

## The narrowest rule
**ECHO rule.** A pop-up is owed a check only when a page it cites, in the same landing, removed or rewrote a sentence, and the pop-up shares a word trigram with that sentence that covers a changed word. Changed words are found with difflib against the nearest new sentence. The test is deterministic and ran over all 121 pop-up x landing pairs that cite a changed page:
- It fires on all 17 page-touched CORRECTION edits (the 16 plus genkan) and on 38 of the 102 other pairs. Those 38 include 3 of the 9 edited non-CORRECTIONs: notice-board, compound-shrine and servants.
- It misses kitchen B1 and garden-pond B1, which were wrong before the landing. day-office 0108 cites no changed page, so it is not among the pairs.
- For 14 of the 17, the matched sentence is the one behind the corrected passage. For hamlet/weir, barracks and retainers, the hit is incidental to a heavy rewrite of the page. 0097's absence sentence gained words and lost none, so arm (c) as 0097 shows it needs its own test: a new `<li><strong>` block on a cited page, plus an absence or only-case marker in the pop-up ("not recorded", "no source", "the one case", "every plan"). Over the 30 edits that test caught 10 CORRECTIONs and fired once on a COMPLETION (inner-court B1).
- Adding a polarity filter (the changed span holds every / all / only / one / no / not / some / beside / behind / back / simplification / guess / recorded / found / staff / each / any) keeps 17 of 17 and cuts the others to 12 of 102. That filter was fitted on these two landings (inferred, in-sample).
- No rule based on page changes can reach the 3 edits that were wrong before the landing; only a full check of the pop-up can.

# Which page edits could have needed the pop-up cascade - 449 record bundles, 2026-11-23

**Answer:** yes. 24 of the 30 pop-up edits trace to a page edit that changed a claim (0090's Takayama reversal alone
accounts for 7). None trace to a wording, citation, footnote or label adjustment; the other 6 fixed problems that were
already there. A claim-bearing edit changes what the page says is so; an adjustment changes only how it is said or cited.

Bundle 1 = the T358-T370 record half of 085f4598c3 (pages 0082 0091 0093 0101 0106 0113 0190 0218), plus its landing fix
0108968f8c. Bundle 2 = cce80ca436, landed by efcf9c44b7 (0009 0059 0090 0096 0097 0099 0103 0104 0106 0107 0113 0123, new 0331).
Evidence: the commits' diffs, `.git/check-replies` (the clone's and /diagram's), the t358*/t371* briefs and handoffs, and the
ledger rows dated 11-23. Left out: the T351-T357 sheet bundle's pop-up edits (armory, official-study, writing-rooms, day-office).

## 1. Page edits by class (an edit repeated across a page's files counts once)
| bundle | SUBSTANTIVE | ADJUSTMENT | where the SUBSTANTIVE ones sit |
|---|---|---|---|
| 1 | 14 (2 minor) | 27 | 8 on drawing pages, 5 in findings bodies, 1 in a drawing-notes absence note (0190) |
| 2 | 48 (7 minor, 2 relocations 0097 -> 0331) | 47 | findings bodies and drawing-page bullets |
| **total** | **62** | **74** | none in `.originals`, none in the Evidence/Grounds comments |
SUBSTANTIVE, for example: 0090 "beside the office rather than behind it" -> "at the back of the office"; 0097 Sakai "one to a
man, ~12 by 18 ft"; 0107 "roofed as the house was"; 0103 "Set stones and shores curved to copy a coastline"; 0218 the tree "[a
guess]"; 0093 "A grievance drum ... is not drawn"; 0059 "the joints tied" -> "some joints". ADJUSTMENT, for example: 0009
"Barley is weak to damp" (a duplicate clause cut); `)「As` -> `); 「As`; 0059 "a weir mostly closed only half the river" (the same
claim); 戦国未 -> 末; 0113 "irigawa" -> "irikawa"; 0103 "(Britannica);"; Evidence comments relabeled; originals added behind new
footnotes. 0009 and 0101 were all ADJUSTMENT except one minor reading ("often" -> "not seldom").

## 2. The pop-up checks and what they led to
(inferred: counted by hand from the replies) Bundle 1 ran about 47 units (one pop-up under one check) and about 19 found
something. Bundle 2 ran about 101 units (19 form, 55 research, 27 depiction; dep-b2's reply was not found), and about 41
found something. Bundle 2's modal-triage also ran 7+ times on overlapping sets and sent most units on (t371h 79 of 114).
Each pop-up edited, and what its edit traces to (S = SUBSTANTIVE):
| pop-up | the edit | traces to |
|---|---|---|
| B1 compound-shrine | Guesses: the tree beside the shrine | S: 0218 drawing, attested -> GUESS |
| B1 inner-court, kitchen | Kanazawa's four garden kinds, the kitchen yard | S: 0091's new grounds finding |
| B1 karo-s-house / main-gate / notice-board | "some plans add the gloss" / the drum / the bounty board | S: 0106 / 0093 / 0190 drawing |
| B1 sacred-tree, garden, garden-pond, clerks--room, day-office | roped absence, black pine, "restored", clerks, drafting | neither |
| B2 court-divider, family-quarters, inner-court, nakamon, office-hall, outer-court, residence | Takayama "beside" -> "at the back" | S: 0090 reversal |
| B2 office-hall, residence, official-study | the intendant worked in the residence; the study's seat | S: 0113 finding, seat GUESS |
| B2 barracks, retainers--quarters, karo-s-house | Sakai, Omori, Sano, Sayama; tetsuki/tedai | S: 0331, 0097, 0106 |
| B2 cell / genkan / outer-court | the join a GUESS / the porch's size and fill / the koshikake | S: 0096 / 0104 drawing / 0099 |
| B2 kitchen, door, residence / garden-pond | roof, louvre, walls, tradesmen's entry / the banks, drawn edge | S: 0107 / 0103 |
| B2 weir_form--frame, hamlet/weir | "the joints" -> "some joints" | S (minor): 0059 |
| B2 servants--quarters | "walls" -> "grounds" | neither |
The builder edited garden-pond, kitchen, the barracks and retainers Entry lines, genkan's Guesses and outer-court by hand from
the new pages before any check ran (T371 handoffs). T376 and T381 wrote 0103 and 0107 to answer bundle 1's form FIX M5/M6,
so for those pages the pop-up edit was the goal of the work, not a side effect of the cascade.

## 3. Tally
- Pop-ups edited: 11 (bundle 1) + 19 (bundle 2) = 30. **24 trace to a SUBSTANTIVE page edit, 0 to an ADJUSTMENT** and 6 to
  neither. Another 6 findings that trace to neither rode along inside S-traced pop-ups: the dropped years (barracks,
  retainers, form M16), karo's 0115 layout and M19 "their", cell's 0168, and garden-pond's guess bullet.
- The SUBSTANTIVE edits that required a change: 0090 Takayama (7 pop-ups); 0331/0097/0106 staff lodging (3); 0113 the intendant's
  workplace and the study's seat (3); 0107 kitchen (3); 0091 grounds (2); 0059 "some joints" (2); 0103 banks; 0104 porch; 0099
  koshikake; 0096 cell join; 0218 tree; 0093 drum; 0190 bounty board; 0106 gloss.
- (inferred) About 20 SUBSTANTIVE edits needed none (0082 cart gate, 0113 corridors, 0123 granary, 0190 edicts: clean).
- ADJUSTMENT-only moves found nothing: 0009's paddy and winter_crop--none clean; 0059's 30 units clean bar "some joints".

## 4. The rule
**A pop-up can need a re-check only when the visible prose of `<q>.html` or `<q>.drawing.html` (or a `.notes` absence note)
changes what it claims.** A tool could apply it in four steps:
1. Clear `.originals.html` changes outright, and Evidence/Grounds/measured comments, tags, links, glossary marks and `[^key]`
   markers. **This step is evidenced:** none of the 30 edits traced to such a change.
2. Run `.notes.html` through step 3, not outright: 0190's widened absence note was claim-bearing, but it came with a drawing change.
3. Pair each old block with its new one and word-diff them after step 1. Send the pair on if the diff adds or removes any of:
   a digit or a unit; a label (GUESS, attested, convention, deviation, simplification, knob); an absence or negation (not
   recorded, no page, none, not); a quantifier or hedge (every, all, some, only, most, often, one case, thought to); a
   placement word (beside, behind, back, end, join, inside, the compass points); or a name. A block new or removed outright is
   always sent on.
   **Untested:** as worded it still sends on 0009's trims ("1975-76", "Wakayama", "544", "often") and 0059's ("1902",
   "Sengoku"); (inferred) it saves real work only if a removed token the page still states elsewhere is ignored.
4. Everything sent on goes to modal-triage, as now.

**What modal-triage does now, and why it let these through** (`.claude/agents/modal-triage.md`):
- It reads the MANIFEST's changed and removed blocks and each pop-up's About and Depiction cut at 400 characters, and is told
  "When unsure, name it".
- The MANIFEST never pairs a block with its old self. In t371-triage-1, 0009's 734-character paddy block sits in one list and
  its 738-character old version in the other, and the only difference is a footnote. So the agent has to diff long paragraphs
  by eye.
- With About cut short it cannot see whether the pop-up rests on the moved sentence, so unsure becomes TOUCHES. (inferred)
  Paired blocks with a word diff, after steps 1-3, would leave it only the claim-bearing changes.

# The A/B/C rule against the 449 record bundles (2026-11-23), read-only

Scope. B1 = 085f4598c3 (parent 253f81afa7); B2 = cce80ca436 (parent 02465be2f7). `git log` confirms these are the only
two commits between them that touch `research/questions/`. An edit is one changed paragraph or note (a `<li>` line or a
comment), paired old against new by its note/orig key, its question heading, or text similarity of 0.6 or more. Pop-ups
were read as they stood at the parent commit, and "citing" means the modal names `questions/NNNN-`. The judges were seven
blind opus readers given parent-time pop-ups only. Their calls were frozen in `tmp/rc/calls-frozen.tsv` (the pair table,
with evidence from both sides) before step 3. The edits are in `tmp/rc/edits.json`.

## Counts
Edits **460** (B1 98, B2 362) | MATTERS **54** | CANNOT-MATTER **406** (161 mechanical: originals-only additions; 245
judged) | misses **6** of 24 at pop-up level (5 by design) | false flags **2** edits (E132, E088), 9 pairs. Edit-level
false flags are scored at page level: an edit is credited if any traced pop-up on its page was flagged (inferred; the key
traces no finer). The 44 edits on 0331 (a new page) had no citers at the parent. They were judged against the 3 pop-ups
that cite it afterwards, and all were CANNOT-MATTER. The staff lodging was caught through 0097 and 0106 instead.

## Step 3: the 24 traced pop-up edits
Caught, 18: B1 compound-shrine (0218, B), kitchen (0091, A) and karo-s-house (0106, A). B2 court-divider,
family-quarters, inner-court, nakamon, office-hall, outer-court and residence (0090, A+B); official-study (0113, A+B);
barracks and retainers--quarters (0097: A on the Sakai dwellings, C on the paragraphs moved to 0331); karo-s-house
(0106, A+B); kitchen and door (0107, B); weir_form--frame and hamlet/weir (0059, "some joints", A).
Misses at pop-up level, 6:
- **B1 inner-court <- 0091 E015** (Kanazawa's four garden kinds, Kochi's walled garden). The pop-up said only "nor what
  the wall ... was built of": N.
- **B1 main-gate <- 0093 E030-E033** (a grievance drum under the gate). The pop-up is silent on a drum: N.
- **B1 notice-board <- 0190 E079-E086** (the bounty board). The pop-up is silent on bounties: N. Its only MATTERS edit,
  E088 (edicts), changed nothing in it.
- **B2 cell <- 0096 E156** ("a county cell joined to the junior rowhouse, a GUESS"). The pop-up said "may stand on any side": N.
- **B2 garden-pond <- 0103 E271-E291** (pond banks, set stones, tataki). The pop-up said "a small pond": N, on 16 pairs.
- **B2 genkan <- 0104 E325/E326** (porches as drawn: 12 x 9 ft, and Ochiba's 10 x 6 ft a GUESS). The pop-up stated "about
  10 to 11 ft across and 4 to 6 ft deep". This is an A the judge tagged N (inferred): the rule misapplied, not the rule.
Misses at pair level, where the pop-up was caught through another page: office-hall <- 0113 E401 (the intendant
"ordinarily worked ... in the residence", N), and residence <- 0107 E341/E344 (roofs, against "walls and roof ... not
recorded", N). Unreachable: residence <- 0113, since residence cites 0113 only from this commit on.
False flags: E132 (0059, the Edo diversion weirs no longer scoped as large-river works) -> weir_form--crib, which was not
edited. E088 (0190, the walls carried "most of the emperor's edicts ...") -> notice-board, which was edited for the
bounty only. Pair level, 9: sacred-tree x3 (E091-E093; edited, but the key traces that edit to neither), gatehouse x2
and granary (0097, C), writing-rooms x2 (0113, not edited in B2), weir_form--crib.
**B, the label changes:** 12 of the 18 caught were caught on a pair that carried a B tag, and 3 were B alone
(compound-shrine, kitchen B2, door). Two misses, cell and genkan, were new Guesses bullets (inferred from the pop-up
diffs), which makes 14 of the 24 at most.

## Verdict
- **Not safe.** The rule misses 6 of 24 pop-up edits. Five are by design: each added new material on a topic the pop-up
  was silent on.
- **Cut.** The unit is a distinct citing pop-up per bundle, not a pop-up x check unit; the key counts about 148 of those.
  The rule sent on 24 of the 123 re-owed pop-ups (B1 5 of 47, B2 19 of 76), so 99 checks (80%) would not have run.
- **Made safe.** Counting N as well (wording 1) sends on 37 of 123 (B1 13, B2 24), measured from the frozen pairs. That
  covers all 24 and cuts 86 (70%).
- **Judges disagree.** A second blind run on G7 (59 edits) flipped E011/E012 to MATTERS for inner-court B1, reading the
  bare-earth court as newly labeled a guess. The pop-up already listed it as a guess, so this is a false hit that happens
  to land on a missed pop-up (inferred). That run also added garden and guest-quarters pairs.

## Wording changes these say to make
1. Add **(D) "adds an attested fact, or a new guess, on something the pop-up's subject is drawn or described with, where
   the pop-up is silent."** All 5 by-design misses are D; "anything else can't" is false for new findings.
2. Rule that **an absence the pop-up states ("not recorded", "no source names") is a fact under A**. My brief told the
   judges to tag an answer to a "not recorded" as N, so the N on residence <- 0107 is the brief's doing. Kitchen B1 was
   judged A on the same shape of change.
3. Rule that **a size or count in a Guesses bullet is a stated fact** (the genkan miss).
4. Narrow (B) to **a change of label**: restating a label the pop-up already carries is not B (the run-2 E012 hit).
5. Make (C) match **the exact key** in `Sources:`. Gatehouse cites `takayama-jinya-jawiki`; the key removed was `-3`.
6. In (C), **a passage moved to another page is not a removal unless the pop-up rests on it there**. Granary's Takayama
   rowhouse moved from 0097 to 0331 and its fact still stands, so it was a false flag. Barracks and retainers were real
   hits on the same move.

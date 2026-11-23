# Handoff - feature 451 T184 (0009, 0059), session 1: write

- SECTION=0009 0059 0332 0333

- K1 DONE - 0009: all eight trimmed wordings restored into the current text. cce80ca436's footnotes stay
  (`qimin-yaoshu-enwiki` after 544, `horikawa-2011-nakaboshi-6`, the Qimin Yaoshu link). In item 6 the footnote keeps
  its pre-trim place after "varying by region,".
- K2 DONE - 0059: items 1-6 restored on 0059 and item 7 on its two blocks, which moved to 0333 under K3. The absence note
  `...-seki-6` is restored in 0059.notes.html. 449 T371's corrections stay: "advisable", "some joints", "a natural
  intake, one with no weir", the 1974 dam, "1902", the 戦国未 note and the Ueno passage.
- K3 DONE - both pages split along their topics:
  - 0332 `after-the-rice-harvest-the-straw-ricks-and-the-winter-crop`. Its lead is 0009's old second lead paragraph,
    followed by the sections "Once the rice was reaped and threshed ..." through "Did rape ever stand beside growing
    rice?". 0009's second lead paragraph is now a one-sentence pointer to 0332.
    0332's lead ends with a pointer back to 0009.
  - 0333 `how-a-village-weir-was-built-stakes-cribs-frames-and-gabions`. Its lead is the two sentences from 0059's
    second lead paragraph on the first weirs (stakes woven with brushwood or bamboo; timber frames packed with stone),
    with their four footnotes, and it ends with a pointer back to 0059. After the lead comes the section "A weir on
    small water was built of what lay to hand." through "How thick was a village weir?". 0059 keeps everything else
    above that section, including the one-bank intake and offtake-siting blocks the engine claims cite. Where the
    section stood, 0059 now has a one-sentence pointer to 0333.
  - **A departure from the brief:** it said 0059 keeps everything above the moved section, but those two lead sentences
    moved too. My reason: they sum up the moved section, and its notes would otherwise sit in two files. The brief
    says no note is in two places, although `research/CLAUDE.md` (feature 301) allows it. To overrule, put the two
    sentences back in 0059's lead and copy their four notes and originals into 0059's files.
  - **Tags:** 0332 is tagged `subject=fields,farming` and drops 0009's `water`, because it covers straw and crops, not
    the paddy's water. 0333 keeps 0059's tags.
  - Every note and its originals moved with the sentence citing it: 15 notes and 22 originals to 0332, 22 notes and 28
    originals to 0333. No key was renamed, and no note is in two places. The counts add up to the old files' totals
    (42/62 and 65/65), and every `data-orig` placeholder resolves in its own originals file. The Evidence comments
    are divided between source and new page, and each page carries an HTML comment noting the split.
  - The drawing pages are untouched: they cite only their own `.drawing.notes.html`, and none of those notes moved.
  - `make record CHECK=1` builds cleanly (4356 pages). `make record`, `make glossary` (no glossary file changed) and
    `make question-sizes` (0 over) all ran clean.

## Prose sizes (bytes of the question file)

| page | at HEAD (trimmed) | pre-trim (cce80ca436^) | now |
|---|---|---|---|
| 0009 | 19,853 | 20,044 | 13,766 |
| 0059 | 19,830 | 20,065 | 12,664 |
| 0332 | - | - | 7,761 |
| 0333 | - | - | 8,682 |

## Files

- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.notes.html
- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.originals.html
- research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html
- research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.notes.html
- research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.originals.html
- research/questions/0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.html (new)
- research/questions/0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.notes.html (new)
- research/questions/0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.originals.html (new)
- research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.html (new)
- research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.notes.html (new)
- research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.originals.html (new)
- the claims sheet, via `make research-claim Q="0332 0333" FEATURE=451`
- specs/451-time-retro-and-efficiency/briefs/t184-handoff.md (this file)

## Open

- **Pop-ups not edited (another builder's).** Each one below names 0009 or 0059, and part of what it says now lives on
  a new page. 27 of them name 0009 or 0059 on an `Entry:` line. Five name a 0009 page only elsewhere in the file:
  choice/fan_middle--wild, --cleared and hamlet/millet, buckwheat, soy.
  - On 0333 (weir forms, stakes, cribs, gabions, thickness): choice/weir_form--fence, --frame, --crib, --gabion;
    choice/intake--weir; hamlet/weir. A lighter touch (stakes, brushwood or cribs in passing): choice/water_source_position--*
    (8 files), choice/intake_place--shoulder, --center, hamlet/irrigation-ditch (Yayoi, crib), hamlet/sluice-gate.
  - On 0332 (ricks, rice-and-barley year, rape): choice/winter_crop--none, --barley; hamlet/paddy; hamlet/barley;
    choice/town_nearness--near, --far; choice/fan_middle--wild, --cleared. Barley in passing: hamlet/millet,
    hamlet/buckwheat, hamlet/soy.
- **Engine `Research:` claims.** I grepped `rust/` (read-only). Only two claims cite 0059's findings page:
  `rust/phases/src/field/brook.rs:95` (the one-bank intake) and `:101` (the intake's siting). Both blocks stayed on
  0059. No claim cites 0009's findings page; every other claim cites a `.drawing.html`, and the drawing pages are
  unchanged. No claim was edited.
- **Archive records.** `research/archive/*.json` records still name the 0009 and 0059 notes files for notes that now
  live in the 0332 and 0333 notes files. They were not edited, and `make record` did not refuse them.
- **The reserved stubs.** Given the full heading as KEY, `make reserve` wrote stub files named with the raw heading. I
  did not re-run it: I deleted those two stubs and wrote the files under the heading-id slug, keeping the reserved
  numbers 0332 and 0333.
- **Size-edit refusal.** Another builder's uncommitted `question_size.rs` work adds a refusal for a page that shrinks and
  drops claim-bearing words. 0009 and 0059 each shrank by about 6,000 to 7,000 bytes because of the split, so expect it
  may flag them unless it recognizes that the words moved to 0332 and 0333.
- **`research/size-limits.json`.** It is untracked and not mine: it appeared at 14:35, between my `make` runs, and
  belongs to that size-limit work.
- **Other builders' edits.** Rust edits were uncommitted in the tree (`question_size.rs` size-edit work and
  `apply_edits/settled.rs`). Mid-session one of them briefly broke the gate build. Nothing of theirs was touched.
- **Record checks.** None were run, per the brief; the next session runs them.
## Session 2: checks (t184-checks)
CHECKED quote-check 0009 (10 notes) - 9 SUPPORTS, 1 absence, 0 EDITs - nothing
CHECKED record-format 0009 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED quote-check 0059 (11 notes) - 8 SUPPORTS, 1 PARTIAL (tabayashi-1987-6), 1 CLAIM-FROM-UNREAD (absence note -6) - applied: the -6 EDIT verbatim; the tabayashi sentence by hand, merged with record-format's fix on the same sentence
CHECKED record-format 0059 r1 - 1 VOCABULARY (diversion works) - applied by hand in the merged sentence (enters a main canal, is tapped by secondary canals at division works on it, and passes on into lesser canals); r2 - 0/0/0 - nothing
CHECKED quote-check 0332 r1 - 4 SUPPORTS, 1 PARTIAL - applied both EDITs (nimosaku-jawiki on the manuring clause; a wet one could not carry the barley); r2 - 5 SUPPORTS, 1 absence - nothing
CHECKED record-format 0332 r1 - 1 VOCABULARY (true leaves), 1 contradiction (no page we read -> cite) - applied both (glossary term true leaf added); r2 - 0/0/0 - nothing
CHECKED quote-check 0333 r1 - 8 SUPPORTS, 3 PARTIAL, 1 JOINED-WRONG, 1 unfootnoted (These are large-river works) - applied all 5 EDITs; the unfootnoted claim fixed by hand: the page gives no river size, so the Edo li now says these weirs were built to work in flood, not to take the ordinary water, on a new note hrr-agagawa-dento-3 quoting the same lecture; r2 - 13 SUPPORTS, 1 gloss EDIT on ushi - applied; r3 - 4 SUPPORTS - nothing
CHECKED source-reader 0333 hrr-agagawa-dento, hrr-agagawa-dento-3 - 3 READ, 1 EDIT (the dropped など, and the like) - applied; its scope point (some Edo flood weirs were stone, Hyakken and Ogure) applied by hand: the lead now reads Some flood-dividing weirs ... and the prose list ends and the like
CHECKED record-format 0333 r1 - 2 VOCABULARY (ushi; Seki) - ushi met by a gloss in the note, not a glossary variant (a bare ushi variant would also match kometori-ushi on 0048); Seki needed nothing (its definition carries the weir sense); r2 - 0/0/0; r3 - 1 VOCABULARY (the gloss lost its noun) - met by hand with is a kind of groyne (not its timber frame EDIT: quote-check r2 had found the source never says what an ushi is made of), quote-check answered FIXED_BY; r4 - 0/0/0 - nothing
CHECKED translation-check 0333 hrr-agagawa-dento-3, hrr-agagawa-dento - FAITHFUL 1, then FAITHFUL 2, FAITHFUL 2 - nothing
CHECKED intro-check 0332 0333 - NO-INTRO-NEEDED 2 - nothing
CHECKED modal-triage (81 units, 27 pop-ups) - 25 TOUCHES, 2 cleared (hamlet/stream, hamlet/sluice-gate; cleared again by the tool after 0059 moved)
CHANGED research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html
CHANGED research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.notes.html
CHANGED research/questions/0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.html
CHANGED research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.html
CHANGED research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.notes.html
CHANGED research/questions/0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.originals.html (make record moved hrr-agagawa-dento-3's original)
CHANGED l7r/diagram/interactive/assets/glossary/28530-true leaf.json (new; apply-edits named it with a space)
CHANGED l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt (rebuilt by make glossary / make record)
CHANGED the record-checked ledgers (the answers above, by make record-checked)
OPEN K2 undone twice: the two 0059 findings (tabayashi-1987-6 secondary and lesser canals; the -6 absence note's Chinese articles clause) repeat round 1 and 4 fixes that cce80ca436 carried along with its trim; restoring the pre-trim wording brought the defects back. Both are fixed again here. A check fix, not a size edit.
OPEN pop-ups (not edited here: pop-ups are not this session's): 19 still owed after 0059 moved again, all TOUCHES in the first triage, owing modal-accuracy, modal-gaps and modal-references: choice/intake--open, --weir; choice/intake_place--center, --shoulder; choice/intake_siting--bend, --straight; choice/water_source_position--edge_E/N/S/W, --head_center/left/right; choice/weir_form--crib, --fence, --frame, --gabion; hamlet/irrigation-ditch; hamlet/weir. Also TOUCHES on 0009 (the after-harvest blocks now on 0332): choice/winter_crop--none, --barley; choice/town_nearness--near, --far; hamlet/barley; hamlet/paddy
OPEN 0009's title still ends and after the harvest, which is now at 0332 (record-format 0009's observation). A renamed heading owes its Entry: links, so it is left to the orchestrator.
OPEN OUTSIDE THE CHANGE (filed by record-checked REPLY=): 0009 maff-suitou-mizu, maff-suitou-mizu-4 character check against the archived suitou-2.pdf is still owed (www.maff.go.jp 403); 0009 the 1975-76 transplanting survey is introduced twice (paragraph and bullet), a style matter
OPEN 0333 tabayashi-1987-5: the scan may set pp. 80-261 with an en dash; it has no text layer, so the GM reads it
OPEN 0059 fn-40 zhwiki-zhengguoqu: quote-verbatim says NOT-ON-PAGE for its original. Not owed here (it predates the write session).
OPEN record-style on the split: record-owed named none, so none was run
OPEN source-reader's lead for 0333 (not acted on): at the Chikugo River stone weir the villagers laid the stones together in the off-season (hrr lecture line 66)
CHECKED modal-triage, second pass (57 units, after 0059 moved again) - 15 TOUCHES, 4 cleared (choice/intake_place--center, --shoulder; choice/intake_siting--bend, --straight)
OPEN pop-ups, final list (this supersedes the pop-up OPEN line above): 21 pop-ups owe modal-accuracy, modal-gaps and modal-references. On 0059/0333: choice/intake--open, --weir; choice/water_source_position--edge_E/N/S/W, --head_center/left/right; choice/weir_form--crib, --fence, --frame, --gabion; hamlet/irrigation-ditch; hamlet/weir. On 0009/0332: choice/winter_crop--none, --barley; choice/town_nearness--near, --far; hamlet/barley; hamlet/paddy. The weir_form pop-ups should note that 0333's Edo item changed its claim, from the weirs of large rivers to some flood-dividing weirs.
OPEN registry entry hrr-agagawa-dento still says DIVERSION weirs on large rivers. The source-reader found the page gives no river size (large rivers is our own description), so the entry should be restated. It is not this session's unit, so it was not edited.
OPEN source-reader points not acted on: the Hamura intake weir (Tama River) was built of ushi and waku (line 67), so frame building was not limited to diversion weirs; and the page links of this kind to diversion weirs only by nearness, which the gloss on note hrr-agagawa-dento states as fact
OPEN process: rounds 3 and 4 on 0333 ran as ordinary narrow later-round checks, not through the round-arbiter as the brief says, because make arbiter-bundle BATCH=1 named no owed trigger and no dispatch was refused. Quote-check never read the final gloss (is a kind of groyne); it was answered FIXED_BY record-format.
OPEN the glossary term true leaf: record-format drafted it from general botany, not from the record's text (the record rule asks for a definition from the record's own text)
CHANGED specs/451-time-retro-and-efficiency/found.jsonl (OUTSIDE THE CHANGE rows filed by record-checked REPLY=) and research/source-attempts.jsonl (source-outcome cited:hrr-agagawa-dento)
NOT MINE docs/building-programs.md, l7r/diagram/interactive/assets/modals/sheet/garden.md, garden-pond.md and the rust/ files changed during this session: no target of mine writes them (another builder)
P1 DONE - the two split pointers (0009 -> 0332, 0059 -> 0333) are now <a class="moved" href="...">, href and link text unchanged; make record CHECK=1, make record, make question-sizes clean (0 over 20,000 bytes); make record-owed names no unanswered check on 0009/0059/0332/0333 blocks
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
CHANGED research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html
OPEN after the marked pointers make record-owed still names 28 pop-up units modal-accuracy "a page its Entry names moved" (0059+0333: choice/intake*, intake_place*, intake_siting*, water_source_position*, weir_form*, hamlet/irrigation-ditch, sluice-gate, stream, weir; 0009+0332: choice/town_nearness*, winter_crop*, hamlet/barley, paddy) - T185 says the moved pointer should clear them; either the owed logic does not yet read class="moved" or these Entries need re-pointing. Out of this brief (no pop-up, rust or claims edits); not triaged
F1 DONE - hrr-agagawa-dento limits restated from the archived page: no river size; the frame sentence follows the diversion-weir account but the Hamura intake weir (Tama River) is named as built of ushi and waku, so frames were not limited to diversion weirs; the 9 m x 5 m daiseigyu is the one frame dimension; What it is now credits the figure sources accurately (source-applicability EDITs)
F2 DONE - glossary true leaf def restated to what aburana-jawiki in 0332 and 0009.drawing supports: a seedling's leaf counted to tell when it is ready to set out (rapeseed set out at five or six); file name kept; no seed-leaf botany
CHANGED research/sources/010-works-cited/10550-hrr-agagawa-dento.html
CHANGED l7r/diagram/interactive/assets/glossary/28530-true leaf.json (untracked before this session; rebuilt by make glossary)
CHECKED source-applicability:hrr-agagawa-dento - 1 APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT, 2 EDITs applied and settled (make apply-edits); the glossary edit owed no check
OPEN none for F1/F2; record-owed still lists other sessions' units (modal triage on 0059/0333/0009/0332 pop-ups, sheet/compound-shrine), not this brief's

# Handoff - feature 449 T284 / T283, session 1: write

- SECTION=0048
- SECTION=0028

- T284.6 DONE - 0048's findings bullet "How big was an ordinary smallholder's byre?" now gives the encyclopedia's figure (a farm stable narrow in Kinki, about 3 m (~10 ft) square, wide where winters are long, as in Tohoku), cited by a new note on 0048, `kotobank-umaya-2` (the same Kotobank 厩 passage 0108's `kotobank-umaya-3` quotes, its original added to 0048's originals file), says the passage names no period, and says how big an Edo-period smallholder's byre was stays unrecorded (the two measured Edo stables stand on registered farmsteads; the existing absence note keeps its place). The evidence comment's silence now reads "an Edo-period smallholder's byre's size".
- T283.7 DONE - 0028 is under its 20,000-byte cap (`make question-sizes` no longer lists it): two redundant words cut from its own prose, "laid out so that the warm air" -> "laid out so the warm air" (the magariya bullet) and "roofed building that stood apart from the main house" -> "roofed building standing apart from the main house" (the Tagawa survey bullet). No fact, footnote or quotation changed.

`make record CHECK=1`, `make record` and `make glossary` all pass.

## Files

- research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.html
- research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.notes.html
- research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.originals.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html
- specs/449-rust-codebase/briefs/t284-handoff.md

## Open

- The record checks for these edits were not run (the next session's job): 0048 owes source-reader / quote-check on the new note `kotobank-umaya-2` (and translation-check on its original, which is copied verbatim from 0108's `kotobank-umaya-3#1`), and record-format on the changed bullet; 0028's two-word cut may owe record-format.
- 0028 sits only a few bytes under the cap; the next addition to it will need a split or a larger cut.
CHECKED quote-check 0028 (magariya-jawiki-4, sugiura-1973-fuzoku; 12 notes in the bundle) - 12 READABLE, 12 VERBATIM, 12 SUPPORTS, 0 PARTIAL, 0 DOES-NOT-SUPPORT, 0 unfootnoted - nothing to apply
CHECKED quote-check 0048 (kotobank-umaya-2, draft-oxen-and-horses-and-their-byres-umaya) - 1 VERBATIM, 1 SUPPORTS, 1 absence note, 0 flags, 0 unfootnoted - nothing to apply
CHECKED record-format 0028 - 29 of 29 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing to apply
CHECKED record-format 0048 - 56 of 56 words ruled; 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing to apply
CHECKED source-reader 0048#kotobank-umaya-2 - 1 claim, 1 READ (the passage names no period, confirmed) - nothing to apply
CHECKED modal-triage (the whole bundle, 65 units, including pop-ups owed by other builders' pages 0091/0093/0097/0116/0123) - 14 units TOUCHES, the rest answered triage: untouched - nothing to apply
CHANGED none (no finding needed an edit; the rebuilt research/site/ and glossary output came from make record and make glossary)
OPEN pop-ups the triage sent on from 0048's new byre-size bullet: choice/byre_form--courtyard, choice/byre_form--detached_commons, hamlet/farmhouse (modal-accuracy, modal-gaps, modal-references each) - the orchestrator's, since pop-ups are not edited here
OPEN other builders' triage hits from 0093 (not my units): sheet/gatehouse, sheet/main-gate
OPEN outside the change, quote-check 0028: sugiura-1973-fuzoku-5 lacks the '; ' join after passage #2; its passage #2 (4.38/4.57 averages) supports no block - drop it with original sugiura-1973-fuzoku-5#2; the all-houses row gives 11 figures for 12 columns and its gloss should name the blank column (read off the scan)
OPEN outside the change, source-reader: kotobank-umaya's registry write-up (9860-kotobank-umaya.html) says the Kinki 3 m 'comes from modern studies of surviving farmhouses' - the page does not say where the figure comes from; only 'no date given' holds
OPEN optional lead (quote-check, source-reader): the same Kotobank page's Nipponica entry says 3 m square is usual for one animal, horse-breeding districts with a dozen or more build nearly house-sized - could strengthen 0048's smallholder-byre bullet
OPEN 0028 still sits a few bytes under its 20,000-byte cap

# T305 handoff - session 1 (write)

- SECTION=0220
- SECTION=0028
- SECTION=0217
- SECTION=0229

## Items

- T305.1 DONE - 0220's "How many arches did a village shrine have?" now ends "the share of shrines with one arch is a GUESS"; the clause "and that one with none was rare" is gone. The Evidence comment had no separate label for it, so it is unchanged.
- T305.2 DONE - registry `jawiki-yashikigami` "Used for" now reads "a small stone or wooden hokora at the plot's corner, often the NW or NE" (the archived page: 「屋敷の北西・北東に祀られることが多い」, the NE demon-gate reading a later Onmyodo overlay).
- T305.3 DONE - registry `nakasendoway-dosojin` now calls the horse-headed Kannon "found near rough stretches of the highway to protect the baggage horses" (the archived page: "for the protection of the baggage carrying horses").
- T305.4 DONE - 0028: (a) the ranking of the pre-1944 houses now takes in Table 5's p. 151 half: bath shed 0.39, storage shed and well house 0.32 (with the livestock shed), garage 0.18, bran shed and bird shed 0.03. Note `sugiura-1973-fuzoku-4` now quotes p. 151's header (new original `sugiura-1973-fuzoku-4#4`), its B_I row and Table 2's key to those symbols (new original `sugiura-1973-fuzoku-4#5`), with the column reading in the gloss. To stay under the cap, the sentence's opening is now "For the houses built by 1944, the survey's oldest". (b) `sugiura-1973-fuzoku-5`'s passage #2 (4.38 / 4.57) is gone, with its link and its original `sugiura-1973-fuzoku-5#2`, and the `; ` join now stands before "Table 5, all-houses row". (c) Read by eye off the archived scan (p. 151, rendered at 300 dpi): the all-houses row's blank column is `kyo` (detached living quarters). The gloss now says so and gives bran 0.01, bird 0.02, shrine 0.01, charcoal 0.01. The prose is 19,997 bytes, the same as before.
- T305.5 DONE - registry `kotobank-umaya`'s limits now end "The Kinki farm stable's 3 m is given with no date." (the page: 「約3m四方ほどである」, no period named).
- T305.6 DONE - 0217: (a) The `jizo-bosatsu-jawiki` passages were NOT-ON-PAGE because the live ja.wikipedia article has been rewritten since the archive's capture (2026-10-02, revision 111026026). The live page no longer carries either quoted sentence; that revision carries both, word for word (checked by source-pages fetch of the oldid URL). Both notes (`jizo-bosatsu-jawiki` in the notes, `jizo-bosatsu-jawiki-2` in the notes and drawing notes) now link the revision's permalink. The registry citation line now names revision 111026026 and its oldid URL, the reason in its READ comment. Its limits paragraph gains one sentence saying the live article has since been rewritten without the quoted passages. No other question cites the key. quote-verbatim now reads both VERBATIM. Ledger: the live URL is `rejected` (rewritten), the oldid URL `cited:jizo-bosatsu-jawiki` (archived). (b) The page's own notes copy of `matsumoto-dosojin-2` now carries "(of Kemi, in Azusagawa)" like the drawing notes. The source's own heading supports it: 「花見の道祖神（梓川地区）」, with けみ as furigana.
- T305.7 DONE - 0229: `homemate-shichido-garan` put on the download list as entry 333 (`make download-add`). The citation `homemate-shichido-garan-5` is kept, read from the archived copy of 2026-10-02.

## Also fixed (found in the work)

- 0028's `Grounds:` session comment named `hamletgen/homesteads.py::farmstead_fixtures` and `settlement/farm_fixtures.py`, Python files deleted with the engine's Python. Both pointers are dropped (comment only, no visible text). That also bought the bytes for T305.4(a). The names kept in the comment (`farm_sheds`, `farm_fixtures_attached`, `farm_fixtures_as_declared`) still appear in `rust/mode_a/src/`.

## Files

- research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.notes.html
- research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.originals.html
- research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.notes.html
- research/questions/0217-wayside-shrines-and-stone-figures-dosojin-jizo.drawing.notes.html
- research/sources/010-works-cited/4960-jawiki-yashikigami.html
- research/sources/010-works-cited/7370-nakasendoway-dosojin.html
- research/sources/010-works-cited/9860-kotobank-umaya.html
- research/sources/010-works-cited/13540-jizo-bosatsu-jawiki.html
- research/to-download.md (entry 333)
- research/archive/2e/2e1e2ccaa0d5.json (the oldid page archived by `make source-outcome OUTCOME=cited:`)
- research/source-attempts.jsonl (this session's ledger lines appended among other builders')
- Not mine, though modified in the tree: `0028-...drawing.notes.html` (another builder's ido-jawiki note), `research/assets/glossary-variants.txt`, `0019-...`, `0072-...`, `research/archive/d0/d0cb58393b46.json`.
- specs/449-rust-codebase/briefs/t305-handoff.md

## Left open

- None of the record checks has run, as the brief says; the next session runs them. They are owed for the four questions' notes (0028 fuzoku-4 and fuzoku-5, 0217's three jizo and matsumoto notes) and for four registry write-ups: the three named plus jizo-bosatsu-jawiki's citation line.
- 0217's two `fukuyama-tsujido-jawiki` passages read DIFFERS only by the page's reference markers ([1][5]). That was so before this work and was left alone.
## Check session (t305-checks)
- CHECKED quote-check 0028 - 13 READABLE, 13 SUPPORTS, 0 PARTIAL (Table 2/5 cells NOT-CHECKED, images) - nothing
- CHECKED quote-check 0217 - 7 READABLE, 7 VERBATIM, 7 SUPPORTS - nothing
- CHECKED quote-check 0220 - 1 READABLE, 1 VERBATIM, 1 SUPPORTS - nothing
- CHECKED record-format 0028 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY (two rounds) - nothing
- CHECKED record-format 0217 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
- CHECKED record-format 0220 - 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
- CHECKED translation-check 0028 - 4 FAITHFUL - nothing
- CHECKED source-reader 0028 sugiura-1973-fuzoku-4/-5 - 4 READ, 0 CONTRADICTED - applied 1 EDIT: the all-houses block now says fewer than half the households (the all-houses row includes the 10 non-farm households); record-format round 2 passed it
- CHECKED source-applicability jawiki-yashikigami - APPLICABLE-WITH-LIMITS (What it is INACCURATE, limits MISSING one) - applied 2 EDITs (Naoe's three patterns; the 1803 picture, the hokora and every-household shrine as late forms, absent in Jodo Shinshu areas, worship in woods)
- CHECKED source-applicability jizo-bosatsu-jawiki - APPLICABLE-WITH-LIMITS (limits MISSING one), then round 2 HONEST - applied 2 EDITs (statues per block a floor not a count, Kyoto pamphlet; read September and again from the archive in November) and by hand dropped 'which is the town's count', which the new sentence contradicted
- CHECKED source-applicability kotobank-umaya - APPLICABLE-WITH-LIMITS, limits HONEST - nothing
- CHECKED source-applicability nakasendoway-dosojin - APPLICABLE-WITH-LIMITS (limits MISSING one) - applied 1 EDIT (the page speaks only from the highway; not-in-a-farmyard is our reading; no date)
- CHECKED modal-triage (57 units) - 8 TOUCHES, 20 units sent on, the rest untouched - recorded with make modal-triaged
- CHANGED research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html
- CHANGED research/sources/010-works-cited/4960-jawiki-yashikigami.html
- CHANGED research/sources/010-works-cited/13540-jizo-bosatsu-jawiki.html
- CHANGED research/sources/010-works-cited/7370-nakasendoway-dosojin.html
- OPEN pop-ups owed because 0028 moved, named TOUCHES by the triage, not checked here per the brief: choice/row_water--own, choice/row_water--shared, choice/well_siting--cluster, hamlet/hen-coop, hamlet/storage-shed, sheet/well (modal-accuracy/gaps/references)
- OPEN pop-ups owed because 0220 moved, which record-owed routes straight to modal-bundle (not into the triage bundle), not checked here: hamlet/household-shrine, sheet/approach, sheet/compound-shrine (the last two also name other builders' 0222/0116)
- OPEN (triage, not mine) sheet/gatehouse and sheet/main-gate TOUCHES by 0093.drawing - another builder's page
- OPEN outside the change (quote-check 0220): the hokora-jawiki note's comment in 0220's drawing notes says the Edo-onward reach is on no page read; fushimi-inari-senbon-2 now quotes it - a stale session comment
- OPEN outside the change (source-applicability nakasendoway-dosojin): a lead, not read - the JTA multilingual pages mlit.go.jp tagengo-db R1-02298 and R1-02300 may state the village-boundary placement outright
- OPEN not my units: record-owed still names other builders' 0091, 0093, 0113, 0123 checks and the sayama-jinya-uematsu, jiandao-zdic, jta-aoyagi-kakunodate write-ups

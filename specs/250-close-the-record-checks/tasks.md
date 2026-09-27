# Tasks - feature 250, close the record checks

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5). American spellings, hyphens only.

## Phase 0 - the baseline and the meter

- [x] T01 The regression baseline: the four record tests and `make record CHECK=1`, `make citations
      CHECK=1`, `make glossary CHECK=1` on the unmodified clone; every later failure is checked against it
      research: rendering
      measure: the runs' own output
      verify: DONE. Baseline on the unmodified clone: record, citations and glossary CHECK in sync; the four record tests 257 passed.
- [x] T02 `measure/tokens.py`: one session cut into a window per task, reporting the main session, each
      named agent and each ad-hoc agent, with what each agent read, largest first (D3)
      research: rendering
      measure: its report over this session's own planning window
      verify: DONE. measure/tokens.py: windows from marks, main session plus each agent per window, first-turn floor, what each agent read, and the main session's largest tool results. Output in measure/tokens-slice.json.

## Phase 1 - the measured slice (D3). STOP for the GM after T10

- [x] T03 FR-001, reading: `make source-pages` for the candidate pointers, then one `source-reader`
      pass over the five bare items of `cities/sizing`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. make source-pages saved the Edo and Jokamachi pages; one source-reader pass over the five items: 1 READ, 1 CONTRADICTED, 3 NOT-FOUND with partials. Boxes: the pass is this task; the reader returned a verdict per item; T04 records and cites; T06 quote-check; T05 source-applicability.
- [x] T04 FR-001, writing: each of the five items carries a citation, an absence note or a grounds note
      in its entry's fragment and `.notes.html`; the registry write-ups for any new key; `make record`,
      `make citations`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. Five items carry a citation or an absence note in the two sizing fragments; the contradicted sentence now says what Chang says; the edo-enwiki and jokamachi-wiki write-ups carry the new use. Fixed where found: make record did not write the citations page. Boxes as T03.
- [x] T05 FR-001, `source-applicability` over each new registry key, one file per key (D2); none
      dispatched if T04 added no key, and the task says so
      research: rendering
      verify: DONE. No new key, two changed write-ups: source-applicability one agent per key, both APPLICABLE-WITH-LIMITS; the missing limit (the Edo article's two maintenance banners) and the stale What-it-is sentence applied.
- [x] T06 FR-001, `quote-check` per changed entry of `cities/sizing`, after `make quote-verbatim` (D2);
      findings applied
      research: rendering
      verify: DONE. quote-check one agent per entry after make quote-verbatim (3 VERBATIM by script, Chang image-only): 2 SUPPORTS, 4 PARTIAL, 0 DOES-NOT-SUPPORT; marks re-aimed, the p. 94 passage quoted, one unfootnoted assertion rewritten as the map's own decision.
- [x] T07 FR-001, `record-format` per changed entry of `cities/sizing`, after `make record-prepass`
      (D2); findings applied; SC-001 judged with `worklist.py cities/sizing.html`
      research: rendering
      verify: DONE. record-format one agent per entry; findings applied. SC-001: worklist reports FOOTNOTED 4, LOCATED 1, NOT-LOCATED 1 - both confirmed by hand as rewritten sentences carrying chang-2 and chang-3 to 5. Fixed where found: record-prepass SECTION=010 matched nothing, silently.
- [x] T08 FR-003 for ONE entry: the vocabulary terms the reports named in it each get a glossary term
      file or a rewritten sentence; `make glossary`
      research: rendering
      verify: DONE. ways 010: girder, the term the 242 report named, defined; the sizing entries' terms defined from today's reports. make glossary green, 735 terms.
- [x] T09 FR-003, the `record-format` re-check of T08's entry: every candidate ruled on
      research: rendering
      verify: DONE. record-format over ways 010 with the candidate list: 33 of 33 ruled on; eight terms defined, three left with the reason (bearing seat is not a phrase the page uses, carried deck and sine need the record's own wording).
- [x] T10 **The measurement the GM asked for**: `measure/tokens.py report` over T01 to T09, recorded in
      `research.md` R1 with the per-window table, what each agent read, what it implies for phases
      2 to 4, and BY NAME every agent the slice did not measure (D3), so the figures are not read as
      complete
      research: rendering
      measure: `python3 specs/250-close-the-record-checks/measure/tokens.py report`
      verify: DONE. research.md R1: main session 87 percent of input over 92 turns, 13 named runs 13 percent, no ad-hoc; a check reads 2,400 to 10,600 tokens of the record and carries 28,400 of nested CLAUDE.md; experiment X1 cut a record-format run's peak from 47,700 to 14,500; the agents not measured are named.

## Phase 1b - the token work (GM 2026-09-26; plan D6 to D10)

- [x] T11 `make quote-verbatim ... SECTION=` checks only that question's notes (the rule dropped the
      argument), and an unmatched SECTION exits 2
      research: rendering
      verify: DONE. DONE. The Makefile rule now passes SECTION; make quote-verbatim PAGE=cities/sizing SECTION=010 checks 4 notes where it checked 11; SECTION=nonesuch exits 2. quote-verbatim tests green.
- [x] T12 `make check-bundle` (`KIND=` for entry-drift) and the five contracts that read a bundle and write `REPORT.md` (D6, D8);
      tests in `tests/tooling/test_check_bundle.py`
      research: rendering
      verify: DONE. DONE. scripts/_check_bundle.py and make check-bundle (PAGE+SECTION, KEY, KIND, EXTRA, NO_QUOTES); tests/tooling/test_check_bundle.py 9 passed, including the exact-key lookup (edo-enwiki is not fires-in-edo-enwiki). The five contracts read the bundle, carry Write, and reply in one line.
- [x] T13 `check-bundle-hooks.sh`, its suite, its settings entry and its row in the root CLAUDE.md;
      proven to go red with its refusal removed
      research: rendering
      verify: DONE. DONE. check-bundle-hooks.sh refuses a dispatch of the five checks into the repository with the make check-bundle command; test-check-bundle-hooks.sh 22 passed, 6 red with the refusal removed; settings.json entry; root CLAUDE.md row.
- [x] T14 `make page-session` and `measure/brief.py` (D7); `research/CLAUDE.md` says how a check and a
      page are now run
      research: rendering
      verify: DONE. DONE. make page-session (scripts/page-session.sh: headless, named like the clone, session id chosen in advance, detached) and measure/brief.py (items derived from assertions.py and worklist.py); a probe session routed to this clone by name. research/CLAUDE.md and the root CLAUDE.md say how a check and a page are run now.
- [x] T15 The seeded-fault runs, three a leg for each of the five agents (D6), recorded as R2's first half;
      an agent whose bundle leg loses a finding keeps reading the tree
      research: rendering
      verify: DONE. DONE. 30 seeded runs, three a leg, five agents (measure/seeded-results.json): every run of both legs named every planted fault (rf 4/4, qc 2/2, sa 1/1, ed 1/1, sr 2/2). Bundle leg: 0 nested CLAUDE.md, peak 28,000-45,000 against 54,000-82,000 in the tree; all 30 wrote REPORT.md and replied in one line. No agent keeps reading the tree.
- [x] T16 **The comparison the GM asked for** (D9): T18 worked in a page session, measured against R1,
      recorded as R2 with the next recommendations
      research: rendering
      measure: `python3 specs/250-close-the-record-checks/measure/tokens.py report --session <child transcript> --marks <its marks>`
      verify: DONE. research.md R2: homesteads (8 items) in one page session, 12.5 million tokens against the slice's 8.0 million for 5 - 1.56 against 1.60 million an item; checks attached no CLAUDE.md (0 of 10); seeded runs 30 of 30 findings kept; the report file refused by the harness and replaced by a compact reply (D8, priced in d8-pricing.txt); five next recommendations.

## Phase 1c - the second round (GM 2026-09-26; plan D11)

- [x] T26 One file per bundle: the MANIFEST holds every copy inline; the five contracts read it once
      research: rendering
      verify: DONE. DONE. make check-bundle writes every copy inline in MANIFEST.md under its origin (the variant index and saved pages stay grep targets); the five contracts read it once; test_check_bundle.py 12 passed.
- [x] T27 Two sessions per page: `brief.py` writes a write brief and a check brief joined by a handoff;
      `make page-session` runs several briefs in order (`_page_session_runner.py`)
      research: rendering
      verify: DONE. DONE. brief.py writes <page>-1.md (locate, read, write, hand off) and <page>-2.md (check, apply, re-check, close); page-session.sh runs several briefs in order through _page_session_runner.py; test_page_session.py passed.
- [x] T28 The engine's dev loop moves to `l7r/diagram/CLAUDE.md`; `pool/` and `tests/` import it; the skill's
      `CLAUDE.md` is a short index; every link resolves
      research: rendering
      verify: DONE. DONE. The dev loop is l7r/diagram/CLAUDE.md (every link rewritten and resolving; the doctrine unchanged but for a header comment, as the plan review confirmed); pool/ and tests/ import it; the skill CLAUDE.md is an index of 1,155 bytes, down from 30,073; a nested @import was proven to attach on a probe.
- [x] T29 `make notes PAGE= SECTION= KEYS=`
      research: rendering
      verify: DONE. DONE. make notes PAGE= SECTION= KEYS= prints the named notes and the blocks carrying them - 2,044 bytes for two notes of sizing 020; tested.
- [x] T30 `make check-bundle ... NOTES=<key,key>` - a re-check of the named notes only
      research: rendering
      verify: DONE. DONE. make check-bundle ... NOTES=<keys> cuts the notes, the fragment and the quote-verbatim report to the named notes; tested on sizing 020.
- [x] T31 The one-file seeded leg, three runs per agent on the planted inputs; recorded in R3
      research: rendering
      verify: DONE. DONE. One-file leg, 15 runs, every run named every planted fault. Mean input per check against the multi-file bundle: rf 166K->112K, qc 110K->53K, sa 152K->107K, ed 104K->57K, sr 102K->74K; turns 4-6 -> 2-4 (seeded-results.json).
- [x] T32 FR-002 and FR-006 for `vegetation`, in two page sessions (D11)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. vegetation checked and applied: 5 questions (020 060 090 110 150) quote-checked and record-formatted, meadow-enwiki source-applicability APPLICABLE-WITH-LIMITS (write-up corrected); ~35 findings applied (claims narrowed to their quotes or labeled as the record's reasoning, scythe-swath framing dropped, 3 translations fixed, 1 new citation each in 020 and 150, stale history and session notes removed), 14 glossary terms + 10 variants; 5 note-scoped re-checks, remaining PARTIALs closed; 5 entry-drift DRIFTED modals rewritten; FR-006 19/19 footnoted; open: Coggins, Aomori and forests-2020 PDF quotes unverifiable here (no PDF text tool)
- [x] T33 **The comparison the GM asked for** (D11): T32 measured against R1 and R2, recorded as R3 with the
      next recommendations
      research: rendering
      verify: DONE. research.md R3: vegetation (6 items) in two page sessions - 15.5 million, 2.58 million an item against 1.60 (slice) and 1.56 (homesteads); a main turn 37% cheaper than the slice and an agent run 48% cheaper, but 18 main turns an item (more work applied, one call a turn, a 40,000 floor); one-file bundle leg 15 of 15; five next recommendations.

## Phase 1d - the third round (GM 2026-09-26; plan D12)

- [x] T34 The session floor: the runner's launch flags (tools, no MCP servers, no skills, the mirror's CLAUDE.md
      excluded in a clone); tested
      research: rendering
      verify: DONE. DONE. _page_session_runner.floor_flags: research's tools, --strict-mcp-config, --disable-slash-commands, and in a clone claudeMdExcludes for the mirror's CLAUDE.md; probes 2026-09-26: first turn 40,280 -> 28,590 -> 21,267 tokens; tested.
- [x] T35 Check sessions of two questions each, planned from the handoff by a `then:` step; tested
      research: rendering
      verify: DONE. DONE. brief.py checks turns the handoff into check briefs of two questions (keys to the first, the last closes); the runner's then: step queues them when the write session ends; a dry run on vegetation's handoff made three; tested.
- [x] T36 The check brief applies a report's findings in one turn
      research: rendering
      verify: DONE. DONE. The check brief's step 6: every finding of one report in ONE message, the record commands and tests once for all of it.
- [x] T37 `research/CLAUDE.md` holds the rules; the full text is `docs/research-record-rules.md`
      research: rendering
      verify: DONE. DONE. research/CLAUDE.md 45,051 -> 13,290 characters, every rule kept (two review rounds compared the files section by section); the full text verbatim in docs/research-record-rules.md, links resolving; 144 record tests green.
- [x] T38 `entry-drift` in each check group's brief, on the modals of its own questions
      research: rendering
      verify: DONE. DONE. Each check group's brief runs _entry_owed.py and checks the modals written from its own questions with KIND= bundles, re-checking a rewritten modal.
- [x] T39 The raster-mode browser check waits for its state; three runs green
      research: rendering
      verify: DONE. DONE. The raster-mode check reads each opacity through the driver's bounded settles; three runs of the browser file green (19 passed each); the expected values unchanged.
- [x] T40 FR-002 and FR-006 for `cities/defenses`, in a write session and check sessions of two (D12)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/defenses 040 and 060 checked and applied (group 2 of 2): quote-check x3 rounds on 060, x2 on 040, record-format x1 each; 040 - one-character DIFFERS fixed (and in the xian-wall-zhwiki registry), the mamian gloss cited (ditai-zhwiki-3), gatepost figure labeled GUESS; 060 - xian-wall-zhwiki-5 DIFFERS fixed, jah-2 retranslated, first sentence reworded onto xian-wall-zhwiki-7, gate and water-gate stretches cited (panmen-zhwiki, a second absence note), tower-count tie labeled GUESS, one HISTORY sentence commented, the stale Pingyao clause cut; 5 glossary terms added, 2 mamian variants; no modal owed; FR-006 worklist 17 bare items: 15 FOOTNOTED, 1 LOCATED (010), 1 NOT-LOCATED (040, now an HTML comment); open: the two jah-song-military-cities quotes are unverified in-container (the PDF has no readable text layer here)
- [x] T41 **The comparison the GM asked for** (D12): T40 measured against R1 to R3, recorded as R4 with the next
      recommendations
      research: rendering
      verify: DONE. research.md R4: cities/defenses (6 items) in three fresh sessions - 6.56 million tokens, 1.09 million an item against 2.58 (vegetation), 1.56 (homesteads) and 1.60 (slice); mean main turn 60,000; first turn 21,400; .39; four next recommendations.

## Phase 1e - the fourth round (GM 2026-09-26; plan D13)

- [x] T42 One re-check round per question in the check brief
      research: rendering
      verify: DONE. DONE. The check brief's step 7 allows one note-scoped re-check per question; a PARTIAL left after it is labeled honestly in its note.
- [x] T43 One-sentence agent descriptions, the full text kept in each contract
      research: rendering
      verify: DONE. DONE. Twelve agent descriptions one sentence each, 8,448 -> 2,122 characters; each full text moved verbatim under 'When to dispatch this agent' (the plan review compared all twelve); tier test green.
- [x] T44 Every clone's local settings exclude the mirror's CLAUDE.md (`_clone_local_settings.py`, the prompt hook)
      research: rendering
      verify: DONE. DONE. _clone_local_settings.py from the clone-sync prompt hook writes claudeMdExcludes for the mirror's CLAUDE.md into the clone's untracked local settings; 3 unit tests, the clone-sync suite green; a probe with the file alone loaded only the clone's CLAUDE.md and started at 19,413 tokens.
- [x] T45 FR-002 and FR-006 for `religion-and-death`, worked as `cities/defenses` was (D13)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. religion-and-death closed: 010/020 (2a) and 190/200 (2b) quote-checked, record-formatted and applied with one re-check round each; 13 glossary terms added in 2b+2a's 10; FR-006 worklist 33 bare items - FOOTNOTED 31, LOCATED 1, NOT-LOCATED 1 (item 14, confirmed in session 1 as an absence note); 4 PDF notes UNFETCHABLE in-container (tama-100, tanigawa, sinoss), l7r-castes canon citation left as session 1 placed it
- [x] T46 **The comparison the GM asked for** (D13): T45 against R1 to R4, recorded as R5 with the table over all
      five rounds
      research: rendering
      verify: DONE. research.md R5: religion-and-death (5 items) 7.42 million, 1.48 million an item; first turn 19,300, largest context 92,000, mean main turn 58,000; one re-check round held; the table over all five rounds.

## Phase 1f - the fifth round (GM 2026-09-26; plan D14)

- [x] T47 A bundle per check (`FOR=`), and the check briefs dispatch each agent with its own
      research: rendering
      verify: DONE. built in a10cb973; verified in the recovery session: the government check sessions dispatched FOR= bundles, check-question-size clean over the record's touched questions (18 untouched over the cap), the four split sessions reviewed (ids kept, every note moved unchanged to one part, joins point and do not restate)
- [x] T48 The question-size cap: `scripts/check-question-size.py` in `make quick`, `make question-sizes`, the rule in
      both research docs
      research: rendering
      verify: DONE. built in a10cb973; verified in the recovery session: the government check sessions dispatched FOR= bundles, check-question-size clean over the record's touched questions (18 untouched over the cap), the four split sessions reviewed (ids kept, every note moved unchanged to one part, joins point and do not restate)
- [x] T49 The splits this feature owes: `cities/government` 080 by hand; homesteads 040 and 210, vegetation 150,
      religion-and-death 200 by split sessions; each judged for lost context
      research: rendering
      verify: DONE. built in a10cb973; verified in the recovery session: the government check sessions dispatched FOR= bundles, check-question-size clean over the record's touched questions (18 untouched over the cap), the four split sessions reviewed (ids kept, every note moved unchanged to one part, joins point and do not restate); the six modals written from homesteads 210/040 re-pointed to the parts holding their text (entry-drift answers stay with T23); the clone guard now lets a page session through as its dispatcher's child (L7R_DISPATCHER, 1fee77a3)
- [x] T50 FR-002 for `cities/government`, worked as the last two pages were (D14)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/government closed: 020/070 (2a) and 080/081 (2b) quote-checked, record-formatted and applied with one re-check round each; 4 source-applicability (2a); 3 FR-002 items cited (session 1, 080 split to 081); FR-006 worklist 13 bare items - FOOTNOTED 10, NOT-LOCATED 3 (the three sentences session 1 and 2a rewrote to what their quotes carry); 5 glossary terms in 2b + 5 in 2a; 2b's step 7-8 run by the recovery session after the crash; quote-verbatim fixed to find a passage through Wikipedia reference markers
- [x] T51 **The comparison the GM asked for** (D14): T50 against R1 to R5, recorded as R6 with the table over all six
      rounds
      research: rendering
      verify: DONE. research.md R6: government 6.38 M measured (about 7.0 M with the dead 2b session's estimated tail) over 4 questions checked - 1.59 M a question against 1.67 (defenses) and 1.90 (religion); quote-check read 19,400 chars against 34,800, record-format 15,000 against 31,300; mean agent run 60,000 against 89,000; main session now 83% of the spend, the apply step its largest part; four recommendations for the GM

## Phase 1g - the sixth round (GM 2026-09-26; plan D15)

- [x] T52 EDIT blocks in `quote-check` and `record-format`, and `make apply-edits` (D15.1)
      research: rendering
      verify: DONE. built in 519865d6; verified: tests/tooling/test_apply_edits.py, test_source_pages.py and the brief/summary run by hand (government summary reproduces R6's rows; the fabric brief names 140 over the cap); make quick clean; plan review CLEAR
- [x] T53 The write brief: the page's over-cap questions split in the write session, reads in one message, the
      registry shape named; `source-pages` adds to its directory (D15.2, D15.3)
      research: rendering
      verify: DONE. built in 519865d6; verified: tests/tooling/test_apply_edits.py, test_source_pages.py and the brief/summary run by hand (government summary reproduces R6's rows; the fabric brief names 140 over the cap); make quick clean; plan review CLEAR
- [x] T54 `tokens.py summary`, per question checked (D15.4)
      research: rendering
      verify: DONE. built in 519865d6; verified: tests/tooling/test_apply_edits.py, test_source_pages.py and the brief/summary run by hand (government summary reproduces R6's rows; the fabric brief names 140 over the cap); make quick clean; plan review CLEAR
- [x] T55 FR-002 for `cities/fabric`, worked as the last three pages were (D15.5)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/fabric closed over sessions 2a-2c: 040, 050, 140, 143 and 146 checked by quote-check and record-format and applied, one re-check round each; 146's fn-82 PARTIAL narrowed and re-checked to SUPPORTS; zongjia, pu and fang glossed and the 2b kidoban term given its bare variant; FR-006 worklist 14 of 14 FOOTNOTED; the four record tests 257 passed; no modal owed on the page
- [x] T56 **The comparison the GM asked for** (D15): T55 against R4 to R6, recorded as R7
      research: rendering
      verify: DONE. research.md R7: cities/fabric 10.81 M over 5 questions checked (2.16 M a question) against 1.56-1.90 M on R4-R6; agents cheaper again (quote-check read 14,300 chars, mean run 54,000); growth all main-session: write session 3.62 M (canon greps, the 140 split carried), a third check session, four first-use tool defects (fixed); four recommendations for the GM

## Phase 1h - the seventh round (GM 2026-09-27; plan D16)

- [x] T57 `make canon` and `canon-read-hooks.sh` with its suite, registered (D16.1)
      research: rendering
      verify: DONE. built and verified: see D16 (live proof in a headless session in the clone, 00:13:14Z; suites green; plan review CLEAR)
- [x] T58 The split before the write, and the write brief refused while an item's question is over the cap (D16.2)
      research: rendering
      verify: DONE. built and verified: see D16 (live proof in a headless session in the clone, 00:13:14Z; suites green; plan review CLEAR)
- [x] T59 Check groups packed by bytes (D16.3)
      research: rendering
      verify: DONE. built and verified: see D16 (live proof in a headless session in the clone, 00:13:14Z; suites green; plan review CLEAR)
- [x] T60 The Mode A sheet regenerated when stale (D16.5)
      research: rendering
      verify: DONE. built and verified: see D16 (live proof in a headless session in the clone, 00:13:14Z; suites green; plan review CLEAR)
- [x] T61 FR-002 and FR-006 for `fields`, worked as the last pages were (D16.4)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. fields closed for 070, 110, 160 (session 2a): quote-check, record-format x3, source-applicability x4 (all APPLICABLE-WITH-LIMITS, limits added), entry-drift x7 (all DRIFTED, rewritten; 6 IN-STEP on re-check, IrrigationDitch fixed after); 26 edits applied by make apply-edits, 2 refused and done by hand; FR-006 worklist 37 bare items: 31 FOOTNOTED, 1 LOCATED, 4 NOT-LOCATED, 1 TOO-SHORT; open: the 160 contrary reading of ja.wikipedia 散村 is stated without a quote (needs a sanson-jawiki entry), Tabayashi 1987 PDF quotes unverifiable here (no text layer)
- [x] T62 **The comparison the GM asked for** (D16): T61 against R4 to R7, recorded as R8
      research: rendering
      verify: DONE. research.md R8: fields 10.26 M over 3 questions (3.42 M a question) but 14 things checked (0.73 M each); the canon guard used, 0 refusals; the split first worked (write session never loaded 020; split 1.35 M); groups-by-bytes put 3 questions + 7 owed modals + 4 sources in one session (peak 171,000) - a regression; modal rewrites were 13 hand edits; three recommendations

## Phase 1i - the eighth round (GM 2026-09-27; plan D17)

- [x] T63 `entry-drift` EDIT blocks, and `apply-edits` on a modal's class file (D17.1)
      research: rendering
      verify: DONE. built and verified (tests/tooling/test_apply_edits.py; brief.py replayed on the fields handoff 61551e06: 3 groups, 7 modals each in one group; tokens.py summary per_thing reproduces R8's 0.73 M); plan review CLEAR
- [x] T64 Check groups packed by load - questions, owed modals, registry keys (D17.2)
      research: rendering
      verify: DONE. built and verified (tests/tooling/test_apply_edits.py; brief.py replayed on the fields handoff 61551e06: 3 groups, 7 modals each in one group; tokens.py summary per_thing reproduces R8's 0.73 M); plan review CLEAR
- [x] T65 `tokens.py summary` per thing checked (D17.3)
      research: rendering
      verify: DONE. built and verified (tests/tooling/test_apply_edits.py; brief.py replayed on the fields handoff 61551e06: 3 groups, 7 modals each in one group; tokens.py summary per_thing reproduces R8's 0.73 M); plan review CLEAR
- [x] T66 FR-002 and FR-006 for `archetypes`, worked as the last pages were (D17.4)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. archetypes session 2c: question 170 checked and applied - quote-check 33 notes (24 SUPPORTS, 5 PARTIAL, 1 DOES-NOT-SUPPORT, all acted on; the gazetteer succession and abandoned-rice passages read and cited, Fei 1936/Lake Tai/yu cited, OCR restored), record-format 6 VOCABULARY + 1 SESSION NOTE + 2 HISTORY applied (6 glossary terms), 8 modals DRIFTED and rewritten, re-check: 12 notes VERBATIM/SUPPORTS, 6 modals IN-STEP, 2 edited once more; FR-006 26 bare items, FOOTNOTED 24, NOT-LOCATED 2
- [x] T67 **The comparison the GM asked for** (D17): T66 against R4 to R8, recorded as R9
      research: rendering
      verify: DONE. research.md R9: archetypes 6.39 M over 6 things (1.07 M each), peak 102,000, mean turn 56,000; the 170 group (a parser defect, owed work) 7.04 M over 9 things; modal rewrites by command (0 hand edits on 8 modals); groups by load held every session under 124,000; the parser now derives questions from commits

## Phase 1j - the ninth round (GM 2026-09-27; plan D18)

- [x] T68 `source-applicability` EDIT blocks (D18.1)
      research: rendering
      verify: DONE. built and verified (see D18; plan review CLEAR, start-up re-derived by the reviewer within 0.06%)
- [x] T69 The start-up measured and the budget decided (D18.2)
      research: rendering
      verify: DONE. built and verified (see D18; plan review CLEAR, start-up re-derived by the reviewer within 0.06%)
- [x] T70 A page's round takes the modals still owed from its other questions (D18.3)
      research: rendering
      verify: DONE. built and verified (see D18; plan review CLEAR, start-up re-derived by the reviewer within 0.06%)
- [x] T71 FR-002 for `cities/hinterland`, worked as the last pages were (D18.4)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. cities/hinterland closed: 010 and 050 checked and applied in two groups; 050 by quote-check (8 notes, 2 DIFFERS fixed, 2 PARTIAL fixed, 2 unfootnoted closed - one footnoted, one labeled a guess with an absence note), record-format (6 vocabulary findings, 2 glossary terms, 2 wording fixes) and one re-check (3 PARTIAL applied); no modals owed; FR-006 6 of 6 footnoted, 0 bare
- [x] T72 **The comparison the GM asked for** (D18): T71 against R6 to R9, recorded as R10
      research: rendering
      verify: DONE. research.md R10: cities/hinterland 8.80 M over 6 things (1.47 M each); one book-length source (cdlib-local-elites, 1.38 MB saved) cost 0.73 M in one source-applicability check - 8.07 M / 1.35 M a thing without it; source write-ups partly by command; no session over 115,000; owed-modal folding built, not exercised

## Phase 1k - the tenth round (GM 2026-09-27; plan D19)

- [x] T73 A long saved page in parts, and a key bundle's long page as an excerpt around its quoted passages (D19.1)
      research: rendering
      verify: DONE. built and verified (see D19: the book's source-applicability page 1.37M chars -> 22,857 bytes, 5 of 5 passages; WHOLE=1 for source-reader via the brief, the guard and the rules doc; suites green; plan review CLEAR)
- [x] T74 The two GM decisions recorded as future work (D19.2)
      research: rendering
      verify: DONE. built and verified (see D19: the book's source-applicability page 1.37M chars -> 22,857 bytes, 5 of 5 passages; WHOLE=1 for source-reader via the brief, the guard and the rules doc; suites green; plan review CLEAR)
- [x] T75 FR-002 and FR-006 for `water`, worked as the last pages were (D19.3)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. water closed: group 2c entry-drift on DrainageDitch (260) and Weir (250) - both DRIFTED, 5 edits applied by apply-edits (0 refused), the DrainageDitch Caveat rewritten by hand as a verbatim slice of its Note; re-check: DrainageDitch IN-STEP, Weir one further sentence (the slant's reason ranked as the source ranks it) applied; FR-006 worklist 42 bare items, FOOTNOTED 34, NOT-LOCATED 3, TOO-SHORT 5; four record tests + test_classes 505 passed
- [x] T76 **The comparison the GM asked for** (D19): T75 against R6 to R10, recorded as R11
      research: rendering
      verify: DONE. research.md R11: water 10.55 M over 10 things (1.06 M each); parts cut source-reader's read to 17,780 chars; folded owed modals checked in their own group, all fixes by command; no further process change recommended - the remaining research moves to a new feature

## Phase 2 - FR-002 and FR-006, one page per session (D7)

- [ ] T17 `measure/assertions.py` derives FR-002's list from the six quote-check reports (D4)
      research: rendering
- [x] T18 FR-002 and FR-006 for `homesteads` - the page of the comparison (D9)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. homesteads: FR-002 5 items - 3 now CITATION (kyuhi-jawiki; tonami-yashikirin-haichi for the Tonami grove sides and winds; the 040 height band on kashima-kainyo-1987 + minami-2022), 2 stay ABSENCE re-searched 2026-09-26 (060 in-house well, 080 interconnected-lanes quotation) plus the 030 6-7 m ridge ABSENCE confirmed; the Tonami model-homestead remainder re-dated ABSENCE; 0 GROUNDS. FR-006 3 of 3 confirmed by grep (22 -> the-gardens-sun...-4 citation, 23 -> kikanchiiki-igune citation + -3 absence, 24 -> yashikirin-jawiki-5 citation); worklist: 45 items, 40 FOOTNOTED, 2 LOCATED (080 items 11-12, outside this brief), 3 NOT-LOCATED (22-24). New keys kyuhi-jawiki, tonami-yashikirin-haichi, kikanchiiki-igune. Agents: 1 source-reader, 3 source-applicability, 4 quote-check (2 rounds), 2 record-format; all findings applied bar the scanned PDFs (6 added to TO-DOWNLOAD 233-238) and the Kameyama NW roll (for the GM); 8 glossary terms, 6 variants.
## Phase 3 - the cosmetic sweeps

MOVED to feature 265 (GM 2026-09-27; plan D20): T20, T21, T22 - and from Phase 2, T19; from Phase 4, T24.

## Phase 4 - the close

- [ ] T23 FR-007, the checks owed by what this feature changed; every `_entry_owed.py` pair answered before the push (D20)
      research: rendering
- [ ] T25 FR-009, the closing report; `make page-check`; the push
      research: rendering

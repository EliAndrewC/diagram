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

## Phase 2 - FR-002 and FR-006, one page per session (D7)

- [ ] T17 `measure/assertions.py` derives FR-002's list from the six quote-check reports (D4)
      research: rendering
- [x] T18 FR-002 and FR-006 for `homesteads` - the page of the comparison (D9)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. homesteads: FR-002 5 items - 3 now CITATION (kyuhi-jawiki; tonami-yashikirin-haichi for the Tonami grove sides and winds; the 040 height band on kashima-kainyo-1987 + minami-2022), 2 stay ABSENCE re-searched 2026-09-26 (060 in-house well, 080 interconnected-lanes quotation) plus the 030 6-7 m ridge ABSENCE confirmed; the Tonami model-homestead remainder re-dated ABSENCE; 0 GROUNDS. FR-006 3 of 3 confirmed by grep (22 -> the-gardens-sun...-4 citation, 23 -> kikanchiiki-igune citation + -3 absence, 24 -> yashikirin-jawiki-5 citation); worklist: 45 items, 40 FOOTNOTED, 2 LOCATED (080 items 11-12, outside this brief), 3 NOT-LOCATED (22-24). New keys kyuhi-jawiki, tonami-yashikirin-haichi, kikanchiiki-igune. Agents: 1 source-reader, 3 source-applicability, 4 quote-check (2 rounds), 2 record-format; all findings applied bar the scanned PDFs (6 added to TO-DOWNLOAD 233-238) and the Kameyama NW roll (for the GM); 8 glossary terms, 6 variants.
- [ ] T19 FR-002 and FR-006 for every other page `assertions.py` names (not `homesteads`, `vegetation`,
      `cities/defenses` or `religion-and-death`), one task per page, cut when T46's figures are read
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] recorded and cited  - [ ] quote-check confirmed  - [ ] source-applicability confirmed

## Phase 3 - the cosmetic sweeps

- [ ] T20 FR-003, the rest of the vocabulary findings and the two variants (`ochiba`, `fire-gap`)
      research: rendering
- [ ] T21 FR-004, the history passages into comments
      research: rendering
- [ ] T22 FR-005, the registry's citation lines carry English titles, one mechanical sweep
      research: rendering

## Phase 4 - the close

- [ ] T23 FR-007, the checks owed by what phases 2 and 3 changed; every `_entry_owed.py` pair answered
      research: rendering
- [ ] T24 FR-008, the download list grown at its end
      research: rendering
- [ ] T25 FR-009, the closing report; `make page-check`; the push
      research: rendering

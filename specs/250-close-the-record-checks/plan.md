# Implementation Plan: close the record checks

Spec: [`spec.md`](spec.md) (accepted, FAITHFUL at round 3). Request: [`request.md`](request.md).
Inputs: `specs/242-cite-the-unfootnoted-assertions/HANDOFF.md` sections 4 to 8, its thirteen reports,
its `research.md` R12.

## Summary

The spec was accepted on 2026-09-14. Since then the record was split into per-entry fragments (feature
258), the glossary into per-term files (259), the checks were tiered and given script pre-passes (251,
255, 260) and the defined agents stopped loading the project's instruction files (256). None of that
changes WHAT this feature owes; all of it changes WHERE an edit lands and HOW a check is dispatched.
This plan maps the spec's requirements onto the record as it now stands, and takes the work in two
steps: a measured slice first, then the rest.

## Technical Context

- No engine Python. Edits land in `research/<page>/NNN-*.html`, the `.notes.html` beside each,
  `research/sources/010-works-cited/NNNN-<key>.html`, and the glossary's per-term files; `make record`,
  `make citations` and `make glossary` assemble. Route: DIRECT (spec D2).
- Measurement scripts live in `specs/250-close-the-record-checks/measure/`.
- The four record tests (`tests/interactive/test_footnotes.py`, `test_citations.py`, `test_sources.py`,
  `test_record_format.py`) after each page; `make page-check` at the close (SC-010).

## Performance bookends

None owed: no engine code, no map moves.

## Constitution Check

- XII (research): every FR-001 and FR-002 task is `research: physical` and carries the five boxes.
- XIII (no regressions): T01 records the baseline of the four record tests before any edit.
- XVI (the literal thing): D1 and D3 below are the two places this plan could be read as departing
  from the request; both go to `spec-fidelity` with the GM's words before a task is ticked.

## The design

### D1 - The spec's paths are read through the split; the spec's text stays as it is

The spec names `cities/sizing.html`, `SOURCES.html` and `glossary.json` as edit targets. Each is now an
ASSEMBLED file that is never hand-edited (features 258, 259). The requirement on each is unchanged and
is met on the assembled file; the EDIT lands in the fragment that assembles into it. The spec is not
amended for this: a spec records what was decided when (feature 260 D4 took the same position), and an
amendment would reset an accepted review over a change of address.

242's `measure/apply_notes.py` places notes by LINE into a whole page and writes footnote numbers; both
are gone. Notes are hand-placed per the per-entry rule: `<sup class="fn" data-note="<key>"></sup>` in
the fragment, `<li data-note="<key>">` in its `.notes.html`. 242's `measure/worklist.py` reads the
assembled page and still runs (measured 2026-09-21: `cities/sizing.html`, 6 items, FOOTNOTED 1,
LOCATED 5), so SC-001 and SC-006 are judged with it unchanged.

### D2 - A check is dispatched per ENTRY, with its pre-pass, never per page

FR-007 asks for `quote-check` and `record-format` "scoped to the changed notes and sections". After the
split that scope is a file: one agent per changed entry, handed `make quote-verbatim PAGE= SECTION=` or
`make record-prepass PAGE= SECTION=` output and the fragment paths. `source-applicability` is handed
the one registry file of each new key. `source-reader` is handed pages saved by `make source-pages`.
242 measured 340,000 to 720,000 tokens per check when each read two to four whole pages and the
registry (HANDOFF section 7); this is the change that measurement asked for.

### D3 - A measured slice first, then the GM reads the figures (GM 2026-09-21)

The GM, starting this feature: *"begin feature 250, but then only perform a few of its tasks, and then
measure the token usage for the different aspects of each task. For example, how many tokens are eaten
up by the main session, how many by each named subagent, how many by the ad hoc subagents, etc. by
measuring this, we can then check whether we need to make any more structural changes before we proceed
with the rest of the feature."*

So Phase 1 is a slice chosen to run as many of the agents the full feature will run as the smallest
real work allows, and Phase 2 onward waits for the GM. It cannot run all of them: `entry-drift` is owed
only at the close (FR-007), and `source-applicability` runs only if the slice adds or changes a registry
write-up. T10 names every agent the slice did NOT measure, so the figures are not read as complete. `measure/tokens.py` cuts the session into one
window per task (`mark`) and reports the main session, each named agent and each ad-hoc agent per
window, with what each agent read, largest first. The slice:

- **FR-001 whole** - `cities/sizing`: two entries, five bare items. Runs `source-reader`, the note
  writing, `source-applicability` on any new key, `quote-check` and `record-format` per entry.
- **FR-003 for one entry** - the vocabulary findings of one entry, with a `record-format` re-check. No
  reader; the contrast case (edits and one check).

The slice is real work and stays. It is not pushed: a feature with an open task lands nothing but its
`specs/` claim, so the record edits wait in the clone for the feature's close.

### D4 - FR-002's count is derived by a script over the reports

`measure/assertions.py` lists, per report, page and section, the bullets under each "assertions with no
footnote" listing. The listing has no one shape (the plan review measured it, 2026-09-21): five of the
six reports open it with a markdown heading, worded differently each time, and
`qc-fields-religion-archetypes.md` opens it three times mid-document with a plain bold line
(`Unfootnoted real-world assertions, by section:`, once per page) and no heading at all. The script is
written and was run on the six reports (2026-09-21), and this decision states what it does, which its
docstring carries beside the code:

- **The opener** is a LINE, heading or not, wherever it falls, carrying "assertion" and "footnote"
  (which "unfootnoted" contains), case-blind, that is NOT itself a bullet or a table row - a listing's
  own bullet (`hw-quotecheck.md` line 123) and the summary tables' count rows carry both words and
  would otherwise open a block.
- **The block ends** at the next horizontal rule or the next heading at the opener's level or above -
  never at a blank line, because `hw-quotecheck.md` puts one between every item.
- **An item** is a top-level bullet in the block, except one beginning "Skipped", "Nothing else" or
  "Other sections" - the reports' notes of what they passed over.
- **The page** comes from a deeper heading inside the block naming `<page>.html` (the fabric and
  river-cities reports), else the nearest bold line (`hw-quotecheck.md`), else the opener
  (`qc-buildings-vegetation.md`), else the nearest heading above it (`qc-fields-...`); the one report
  about a single page names it nowhere and is mapped by file name. **The section** comes from the
  nearest bold-only line above the item inside the block, else the item's own leading italic prefix,
  else a trailing `("...")`.
- **Two guards.** A report with no opener FAILS the run. Where a report's summary table states its own
  count the script compares and fails on a mismatch (one report states a bare total, measured equal;
  `qc-buildings-vegetation.md` states "7 (buildings) + 5 (vegetation)", which the script does not parse
  and which was compared by hand: equal).

Measured: every item the script returns carries both a page and a section - 0 without, over six
reports and fifteen pages, 72 items (the script's own last line prints all three). The task list names
no count; the closing report prints the script's.

### D5 - FR-006's items are found by their own words, grepped over the page's fragments

`worklist.py` prints a section label beside each item, and the label is NOT the record section the
sentence lives in: `section_of` returns the last `###` heading of the inventory REPORT above the item.
Measured by the plan review, 2026-09-21: on `cities/sizing` three of the six items carry a heading from
another page or the other entry, and on `fields` a NOT-LOCATED item carries an empty label and three
carry a heading no fragment of `research/fields/` has. So the label is a hint and nothing more. Each
NOT-LOCATED, TOO-SHORT or AMBIGUOUS item is found by grepping its distinctive words - a figure, a proper
noun, a term - over `research/<page>/*.html`, and the fragment the grep names is the one opened. An item
whose words no fragment carries is recorded as such, with the words tried, and is then searched by its
subject; it is never confirmed against a fragment the grep did not name.

### D6 - A record check reads a BUNDLE outside the repository (GM 2026-09-26)

The GM, on the measurement of D3 (research R1) and its three recommendations: *"Do not move tooling fixes
to another clone or make them a standalone fix. Just go ahead and make them as part of your work here. And
yes, I agree that all of those recommendations should be implemented. So please keep going and implement all
of them. And then after they are all implemented, we can move forward with testing them by resuming some of
the research itself to compare the token usage of the next subset of research tasks with the token usage
from the previous set of research tasks."*

R1 finding 2: an agent that reads a file under the repository is handed every `CLAUDE.md` above it, about
28,400 tokens under `research/`, which `omitClaudeMd` does not stop. So `make check-bundle PAGE= SECTION=`
(or `KEY=`) copies what one check reads - the fragment, its notes, the prepass, the quote-verbatim report,
the registry entries its notes cite, the variant index - to `/tmp/l7r-check/`, with a `MANIFEST.md` naming
each copy's origin. The contracts of `quote-check`, `record-format`, `source-applicability` and
`source-reader` read the bundle and nothing under `/diagram`; so does `entry-drift` (plan review of
2026-09-26: it is a check agent this feature runs at FR-007, and it reads the same fragments), whose bundle adds
`kind.txt`, the docstring of the one modal class it compares (`KIND=<class>`), rather than the whole classes
module. `check-bundle-hooks.sh` refuses a dispatch of any of the five that points into the repository and prints
the command.

**Does a check still find what it found?** A check that loses the CLAUDE.md files loses nothing its contract
does not carry (feature 256's position), but that is a claim, and the tier rule measures it: seeded-fault runs,
THREE a leg, for every one of the five agents the bundle moves. Each case is one input with known findings,
read three times in the tree (under `research/_seeded250/`, where the CLAUDE.md files attach) and three times
from its bundle - the same bytes in two places - and each run is judged on whether its report names every known
finding: `record-format` on ways 010 with a visible Grounds field, a history sentence, a note to a session and an
undefined term planted; `quote-check` on sizing 020 with a mark moved to a sentence its quote does not support and
an unfootnoted figure added; `source-applicability` on the slice's recorded case (`edo-enwiki` before its limit was
added); `entry-drift` on the `WetPaddy` modal against its section with the section's two thirds made a tenth;
`source-reader` on three claims against the saved Edo page, one of them contradicted by it. Recorded as R2. A leg that loses a finding the other
catches is a regression, and the bundle is not adopted for that agent.

### D7 - One page per session, started fresh from a brief (GM 2026-09-26)

R1 finding 3: the main session was 87% of the input. `make page-session BRIEF=<file>` starts a headless
`claude -p` in this clone - named like it, so the hooks route it here; with the project's appended system
prompt; with a session id chosen in advance, so its transcript is known - detached, and returns at once. The
brief carries the page's items (derived: `measure/brief.py` reads `assertions.py` and `worklist.py`) and the
procedure (D2, D5, D6, D8), so the session does not read the spec and plan to orient. It commits and does not
push; the parent session does not edit the clone while it runs.

### D8 - A check's report is compact: counts first, then only what to act on

R1 finding 3: thirteen whole reports sat in the main session's context and were re-read on every later turn.
**The form first built FAILED, and is recorded here so it is not re-tried:** the contracts gained `Write` and
wrote the report to `REPORT.md` in the bundle with a one-line reply. Headless, as the seeded runs were, that
worked (30 of 30); as SUBAGENTS in the first page session every one was refused by the harness itself -
*"Subagents should return findings as text, not write report files"* - and spent a turn on the attempt. That
is a deliberate harness rule, not a bug, so it is not worked around. What replaced it: the reply IS the
report, and the contracts of the five checks say its first line is the counts, then only the findings the
session must act on, a pass in one line - never the quotation again or the reasoning that it passed. `Write`
is off their tool lists again. The alternative priced and not taken: run each check as a headless process
whose output a launcher writes to a file. Measured (observed 2026-09-26; method: `measure/d8-pricing.txt` - the first turn of the 15 seeded bundle runs against the 10 subagent checks of the page session, and each report's length times the main-session turns after it): a headless check's first turn holds 22,300 tokens
against a subagent's 7,200 (3.1 times), so over a check's 5.8 turns it costs about 87,000 tokens more; an
inline report averaged 1,600 tokens and was re-read on a mean of 30 later turns, about 51,000. The file route
would cost the GM's own measure more than it saves, so the narrowing serves the recommendation's purpose -
keeping the reports' cost out of the session - by the cheaper road. It is raised with the GM with the result.

### D9 - The comparison (research R2)

The next subset is FR-002 and FR-006 for `homesteads`: five FR-002 items (the slice had five) and three FR-006
items, worked in one page session (D7) with bundled checks (D6, D8). Measured with `measure/tokens.py` over the
child session's transcript, and set against the slice (R1) three ways: the whole; per item closed; and per check
run, split into the floor an agent carries before it reads and what it read. The FR-006 items are their own
window, so the like-for-like figure can be taken without them. The seeded-fault runs (D6) are measured as their
own line and are not part of either side.

### D10 - The route is GATED, not DIRECT

Spec D2 expected no engine Python. The slice fixed `tools/record_asset.py` (constitution XIV), so the delta
carries engine code and the push takes the gated route on a green `make done`. The spec is not amended for
it: D2 recorded an expectation, and the route is chosen from the delta by `sync-with-main.sh`, never by a spec.

### D11 - The second round: R2's five recommendations, then another measured page (GM 2026-09-26)

The GM, on R2: *"Yes, I agree with your suggestion. So please do all five things, then do another measured page,
the same as this round, and then let's see if that helps."* The five, each the smallest form that does what R2
measured:

1. **One file per bundle.** `make check-bundle` writes every copy INLINE in its `MANIFEST.md` under its origin;
   the variant index and saved pages stay files beside it, as grep targets. The five contracts say to read it
   once. Proven the way D6 was: a one-file leg of three seeded runs per agent on the same planted inputs,
   judged on the same findings, beside the tree and multi-file legs already recorded (R2).
2. **Two sessions per page.** `measure/brief.py` writes two briefs - locate, read and write; then check, apply
   and close - joined by a handoff file that names the changed questions and keys; `make page-session` runs
   several briefs one after another, each a fresh session (`scripts/_page_session_runner.py`).
3. **The engine's dev loop moves under the engine.** The skill's `CLAUDE.md` body moves to
   `l7r/diagram/CLAUDE.md` with every link rewritten for its depth; `pool/CLAUDE.md` and `tests/CLAUDE.md` import it
   (`@../l7r/diagram/CLAUDE.md` - a nested import was proven to attach on a probe, 2026-09-26); the skill's
   `CLAUDE.md` becomes a short index. Nothing in the doctrine changes, only where it auto-loads.
4. **`make notes PAGE= SECTION= KEYS=`** prints the named notes of one question and only the blocks of its
   fragment that carry them. The briefs tell a session to use it, and never to dump a notes file.
5. **Re-check only what moved.** `make check-bundle ... NOTES=<key,key>` cuts the notes file and the fragment to
   the named notes and the blocks carrying them, and the quote-verbatim report to their footnotes; the check
   brief's re-check step uses it.

The page is `vegetation` - five FR-002 items (as both earlier pages had) and one FR-006 - worked in two sessions
and measured with `measure/tokens.py` over both transcripts, against R1 and R2. Recorded as R3.

### D12 - The third round: R3's five recommendations, the flaky browser check, and another measured page (GM 2026-09-26)

The GM, on R3: *"Yes, I like those recommendations. So my decision is that you should do all five and then measure
again the same way as this round. Thanks. You should also fix the flaky timing check if you didn't already fix
that."* Each built in its smallest form:

1. **The session floor.** `_page_session_runner.py` starts a page session with only research's tools, no MCP
   servers, no skill listing, and - in a clone - `claudeMdExcludes` naming the MIRROR's root `CLAUDE.md`, which
   sits above every clone and otherwise loads beside the clone's own copy (found while pricing this; measured on
   probes 2026-09-26: a first turn of 40,280 tokens as launched, 28,590 with the tool and service cuts, 21,267
   with the duplicate excluded).
2. **One or two questions per check session.** The write session's handoff is turned into check briefs of TWO
   questions each (`brief.py checks`), by a `then:` step the runner executes when the write session ends; each
   group is a fresh session, and the last one closes the page. The registry keys go to the first group.
3. **A report's findings in one turn.** The check brief's apply step says: every finding of one report in ONE
   message, the record commands and tests once for all of it.
4. **`research/CLAUDE.md` holds the rules only.** Its 45,051 characters move VERBATIM to
   `docs/research-record-rules.md` (links rewritten), and the file keeps every rule, compactly, at 13,290 (both
   observed 2026-09-26; method: `len` of the file's text at 37c20e57 and after this change) -
   under the same headings, so the full reasoning is one lookup away. The plan review of 2026-09-26 compared the two
   files section by section and found about twenty short rules the first cut had dropped (among them the
   `Not cited` marker, the translator in a translation note, the pixel figure in a spec's comment); each is back
   under its heading, and a second comparison of the whole old file found the rest (the citation link's full-text
   and original-language page, the checker's anchor, the roster's parenthetical, and others); the GROUNDS sentence
   keeps its own words, "on an existing note". The two tests that read the file are green.
5. **`entry-drift` belongs to the check session, budgeted.** Each group's brief runs `_entry_owed.py` and checks
   the modals written from its own questions, with the question they were written from.

**The flaky check.** `test_in_raster_mode_the_lit_paddy_is_washed_and_the_lit_beads_are_not` read a computed
opacity in the same tick as the highlight; under a loaded gate the style had not been recomputed (one FULL run:
`('1', '1')` against `('0.45', '1')`; green alone twice). It now waits for the state with the driver's bounded
`settles`, the pattern its sibling tests use (feature 145) - exactly as strict: a value that never arrives fails.

The page is `cities/defenses` - five FR-002 items and one FR-006, the size of the last - measured over every
session the runner starts (listed in `.git/page-sessions/index.txt`) against R1 to R3. Recorded as R4.

### D13 - The fourth round: R4's recommendations 2 to 4, then an equivalent page before the rest (GM 2026-09-26)

The GM, on R4: *"Go ahead and implement recommendations two, three, and four. then kick off another round of
equivalent work to the others so that we can do an apples to apples comparison before we proceed with all
remaining pages. Because I really want to get this right before we burn through too many tokens again."* So R4's
recommendation 1 (go) waits for this round's figures, and:

2. **One re-check round.** The check brief's step 7 allows a single note-scoped re-check per question; a PARTIAL
   left after it is labeled honestly in its note - what the quote carries and what it does not, or the assertion
   narrowed to the quote - and not re-checked again.
3. **One-sentence agent descriptions.** Each of the twelve defined agents' `description` is one sentence (8,448
   characters to 2,122 in all, observed 2026-09-26; method: `len` of the twelve fields before and after); the full
   statement moves verbatim into the contract body under "When to dispatch this agent". The built-in agent types'
   descriptions, the rest of the listing, are the harness's and are not ours to shorten.
4. **Every clone without the mirror's CLAUDE.md.** `scripts/_clone_local_settings.py`, run by the clone-sync
   prompt hook, writes `claudeMdExcludes` naming the mirror's root CLAUDE.md into the clone's untracked
   `.claude/settings.local.json`, keeping every other key; the mirror is never touched. Measured on a probe with the
   local file alone (no launch flag): only the clone's own CLAUDE.md loaded, and with the shorter descriptions a
   page session's first turn fell from 21,267 to 19,413 tokens (observed 2026-09-26; method: first-turn usage of two
   headless probes in this clone).

The page is `religion-and-death` - four FR-002 items and one FR-006, the nearest in size to the last two - worked
exactly as `cities/defenses` was (a write session, then check sessions of two questions) and measured the same way.
Recorded as R5, with the updated table over all five rounds.

### D14 - The fifth round: per-check bundles, a size for a question, and another measured page (GM 2026-09-26)

The GM, asked whether "the page's content" in R5 meant the web or our record: it meant OUR files - a check on that
page read 82,000 tokens of the question files and their notes against 4,000 of web pages. The GM: *"I think we
should do both of them, but I do not have a clear sense on what the maximum size a question should grow to is ...
perhaps you would be able to pick something sensible, and then we can try that out ... if we end up splitting up
some of our existing questions, then you should look and see whether you think there is important context being
lost or if those questions linking to each other is good enough for a human without depriving necessary context from
a future reviewer who is doing the subagent checks ... after you've made the tooling change, go ahead and do one
more round on one more page, and then do another set of measurements."*

1. **A bundle per check.** `make check-bundle ... FOR=quote-check|record-format|entry-drift` keeps only the parts
   that check reads - the question and its notes always, then the quote report for `quote-check`, the word list and
   the variant index for `record-format`, the modal's docstring for `entry-drift`; the registry entries only in
   `FOR=all`. The check briefs dispatch each agent with its own.
2. **A question has a size: 20,000 bytes, question plus notes.** The record's 90th percentile when set (288
   questions, median 6,750; observed 2026-09-26, method: `scripts/check-question-size.py --report`), about 5,000
   tokens. Checked on what a change TOUCHES (`make quick` fails on one over it); 18 questions no change touched are over it
   (observed 2026-09-26 after the four splits below; method: `check-question-size.py --report`) and are split when
   their pages are worked. The rule and how to split without losing context are in
   `research/CLAUDE.md` and `docs/research-record-rules.md`, "A question has a size".
3. **The splits this feature owes.** `cities/government` 080 (38,500 bytes) was split by hand into three - the Japanese
   finding with its decision and departure (19,800), China checked second (7,000), and where the foot soldiers lived
   (13,400; bytes with notes, observed 2026-09-26, method: `wc -c` of each part and its notes file; session 1 of
   the page then moved 080's hiring finding into 081, leaving 080 at 15,587) - and the review of it found two bridging sentences that restated the other parts' evidence, a claim
   without a footnote to a check reading one part alone; both now only point. The four other questions this feature
   touched and left over the cap (homesteads 040 and 210, vegetation 150, religion-and-death 200) are split by fresh
   sessions from a split brief, each reporting what every part relies on from the others, and the session that
   dispatched them judges each split for lost context before it lands.
4. **The measured page** is `cities/government` - three FR-002 items, one of them in 080 - worked as the last two
   pages were, measured the same way and set against R1 to R5 as R6. It is the smallest page measured, so its per-item
   figure is the noisiest; R6 says so.

### D15 - The sixth round: R6's four recommendations, then another measured page (GM 2026-09-26)

The GM, on R6: *"Implement all of your recommendations and then do another measured page for comparison."*

1. **A report is applied with one command** (R6 recommendation 1). `quote-check` and `record-format` end every
   finding with an `EDIT` block - the origin file, the exact old text, the new text - or `EDIT: none - <why>` where
   the fix needs what the bundle cannot settle; `record-format` writes each glossary term as one `GLOSSARY` line.
   `make apply-edits FROM=<the agent's output_file>` (`scripts/_apply_edits.py`) applies a block only where its old
   text occurs exactly once in a file under `research/`, refuses the rest with the reason, and takes `SKIP=` for a
   block the session disagrees with. The agents still never edit: the block is a proposal the session reads and
   applies, and the check brief's step 6 does the refused, skipped and `EDIT: none` findings by hand in one message.
   The bundle's copies are the origin files' own lines (`_check_bundle.py` copies or excerpts, never assembles), so
   old text copied from a bundle matches its origin.
2. **A split happens in the write session** (recommendation 2). The write brief names the page's questions over the
   cap (`brief.py over_cap`), and step 3b splits one an item falls in there, while the session has it read, each part
   its own `SECTION=` line in the handoff. The standalone split brief stays for a question no page's items touch.
3. **The write session's read step** (recommendation 3), measured first as R6 asked: the government write session's
   19 read-and-write turns went to a `make source-pages` batch that overwrote the first (numbered from 01 again), five
   files read one a turn so `Edit` would accept them, turns studying the registry's shape, and a stray one-word agent
   call (observed 2026-09-26; method: the tool calls of transcript `d93e4c76`, in order). So: `source-pages` ADDS to
   an existing directory (a saved page is kept, a failed one retried, numbering continues past every old file); the
   brief says to read every file to be edited in ONE message of parallel reads, and names the newest registry entry
   as the shape to copy.
4. **Per question checked** (recommendation 4). `tokens.py summary --files ... --questions N --items N` gives a
   page's row, per question checked as the headline and per item beside it.
5. **The measured page is `cities/fabric`**: three FR-002 items and no FR-006, as `cities/government` had, and one
   item falls in question 140 (36,858 bytes with its notes; observed 2026-09-26, method: `wc -c` of 140 and its notes,
   as `brief.py over_cap` prints it), so the page exercises the in-session split. Worked as the last three
   were - a write session, then check sessions of two questions - and compared in R7 with R4 to R6, computed the same
   way.

### D16 - The seventh round: R7's four recommendations, mechanically enforced, then another measured page (GM 2026-09-27)

The GM, on R7: *"Please implement all of your recommendations and then do another round of tests ... However, make
sure that what you are doing is mechanically enforced, especially on recommendation number one, because simply saying
that we should do a certain thing is probably not enough to make it happen. That is why we use hooks and such."* And,
separately, the small fix R7's report raised: the Mode A sheet tests read a generated sheet without checking it was
current.

1. **The canon, searched in one call - by guard** (recommendation 1). `make canon TERMS="a|b|c"` (`scripts/_canon.py`)
   searches every canon file under `/host-l7r-repo/setting` and `/host-l7r-repo/gm-assistant/setting` for every term
   at once and names each hit's heading. `canon-read-hooks.sh` (PreToolUse on Bash, Read and Grep; the decision in
   `scripts/_hm_canon.py`) makes it the only way in: a direct read of a canon file - a Read or Grep on it, or a shell
   read verb naming it, absolutely or after a `cd` into the host repository - is refused with the command, and a
   `make canon` within three tool calls of another is refused unless it names every earlier term (the fold; the same
   rule lets the retry after a refusal pass). A mention is not a read. Escape `CANON_OK="<reason>"` for a read the
   search cannot give (a whole section in order). Its companion suite drives the real hook; it is registered in
   `.claude/settings.json` and in the root CLAUDE.md's guard table.
   **It runs where the measured round runs** (plan review, item 1): hooks run the MIRROR's copy of a guard, and a
   guard added in a feature is not in the mirror until the feature lands - so `check-bundle-hooks.sh` (D8) had never
   run (zero guard-log entries) and this one would not have either. Both are now registered in a fallback form that
   runs the mirror's copy when it exists and the session's own clone copy until then, and
   `tests/tooling/test_hooks_resolve.py` fails on any hook registered by a mirror path the mirror does not have (proved
   red on the bare form). Proved LIVE: a headless session in this clone told to Read `budgets.md` was refused with
   the `make canon` message and the guard log recorded `canon-read blocked direct` (2026-09-27T00:13:14Z). A third
   `make canon` in the window is refused however it is worded (item 2: `a`, `a|b`, `a|b|c` had passed), a refused
   call does not count toward the window, and a recursive grep over the host repository or a read of any `setting/`
   under it (the webapp's copy too) is a canon read. The write brief names the canon files and the command (item 3).
2. **The split, its own session, before the write - by construction** (recommendation 2). `brief.py <page> <task>`
   maps each FR-002 item to its question (the heading the report names, else the question containing the item's
   quoted text) and each FR-006 item by its quoted text or its report sub-heading; an item it cannot place is named
   loudly, never skipped and, for each such question over the cap,
   queues a split session first. The write brief is made by a `then:` step after the splits, and `brief.py write`
   REFUSES while any item's question is still over the cap - so the write session never loads an unsplit question.
   `brief.py` prints the one `make page-session` line to run.
3. **Check groups by bytes - by construction** (recommendation 3). `check_groups` packs the handoff's questions first
   fit, largest first, into sessions of at most 40,000 bytes (two questions at the cap, the most the old two-question
   groups ever held), each question sized with its notes as the write session left it.
4. **One more page** (recommendation 4): `fields` - three FR-002 items, as the last two pages had, plus four FR-006
   items, as the homesteads and religion rounds had some. Its FR-002 items fall in 070, 110 and 160, all under the
   cap; three of its FR-006 items fall in 020, at 56,248 bytes the largest question in the record (observed
   2026-09-27, method: `brief.py questions` and `fr006_questions`), so the page exercises recommendation 2 - a split
   session on 020 runs before the write. The FR-006 mapping is part of D16.2: the first version mapped FR-002 items
   only and would have handed the write session 020 whole. Compared in R8 with R4 to R7 by `tokens.py summary`, per
   question checked, with the split session reported beside the page, as R6 reported its splits. R8 says which recommendations the page
   exercised and how many times the canon guard fired (item 4): none of the three FR-002 items is a canon claim, so
   recommendation 1 is measured only if the session reaches the canon.
5. **The Mode A sheet is current before a test reads it.** `tests/_sheets.py`: a declared generated exception's svg
   is regenerated when missing OR older than its generator or any engine module, under a lock so two workers never
   read one the other is writing; both readers (`test_mode_a_sheets.py`, `tools/test_registry.py`) go through it.

### D17 - The eighth round: R8's three recommendations, then another measured page (GM 2026-09-27)

The GM, on R8: *"Go ahead and implement those suggestions and then do another research pass of a similar size as the
others to see how that affects our token usage and such. Basically just, you know, the same type of testing we've
done for each of our other iterations."*

1. **A drifted modal is applied by command** (recommendation 1). `entry-drift` ends each DRIFTED finding with an
   `EDIT` block on the modal's class file - old text copied from `kind.txt` and kept within one docstring line, the
   new text one line in the modal's own register, data tags never touched - or `EDIT: none - <why>` when the fix is
   not a rewording. `apply-edits` accepts `.claude/skills/diagram/l7r/diagram/interactive/classes/` as a second root
   under the same exactly-once rule (tested: a class file applied, a file elsewhere in the engine refused). The check
   brief's step 6 names `entry-drift` among the reports it applies.
2. **A check group is sized by everything it checks** (recommendation 2). `check_groups` packs LOAD, first fit,
   largest first: a question's bytes with its notes, plus, for each modal `_entry_owed.py` names as owed from it, the
   modal's prose and `MODAL_WORK` = 2,000 bytes for its report and rewrite - each modal credited to the first of the
   questions it is owed from that a check group takes, the group that runs its `entry-drift` (the first version
   credited the first on the PAGE and lost `paddy`, owed from 110 but listed first under 020; plan review) (a GUESS, labeled at the constant, which
   this round measures); the registry keys are one more item whose load is their entries' bytes, and the group that
   takes it checks them. The budget, `GROUP_BYTES` = 28,000, is FITTED: over the six measured check sessions of R6 to
   R8, peak context = 40,881 + 2.08 x load, so a load of about 28,000 keeps a session near the 100,000 the earlier
   two-question groups peaked at (observed 2026-09-27; method: each session's questions, owed modals at the median
   modal prose of 1,225 bytes, and registry entries, against its recorded peak, least squares; loose - fabric's 2a
   peaked at 7.5x its load while fixing tool defects). The fields session's load under this rule packs into three
   sessions, not one: 070 (26,826 bytes of load) alone, 110 (13,990) alone, 160 (16,213) with the four registry keys
   (3,878) (observed 2026-09-27; method: HEAD's `brief.py loads` and `check_groups` run on the fields handoff commit
   61551e06 in a detached worktree, where `_entry_owed.py` names the seven modals R8 counts).
3. **Per thing checked** (recommendation 3). `tokens.py summary --modals N --keys N` adds `per_thing` - the total over
   questions + owed modals + registry keys - with per question beside it.
4. **The measured page is `archetypes`**: two FR-002 items (questions 100 and 140) and one FR-006 item, no question
   over the cap - the nearest in size of the pages left (`cities/hinterland` has two items and no FR-006). Worked as
   the others were and compared in R9 with R4 to R8, per thing checked, saying which of the three changes the page
   exercised (whether any modal was owed, how the groups packed).

### D18 - The ninth round: R9's three recommendations, then another measured page (GM 2026-09-27)

The GM, on R9: *"Yes, please implement those recommendations and then do another round of testing and measurements
when researching the next page."*

1. **`source-applicability` ends each write-up fix with an EDIT block** (recommendation 1) on the registry entry -
   the old text copied from the bundle's copy, occurring once; `EDIT: none - <why>` for a source judged
   NOT-APPLICABLE or a fix that is not a rewording. `apply-edits` already writes under `research/`, where the registry
   lives. The check brief's step 6 names it among the reports it applies.
2. **Measure a session's start-up, then decide the budget** (recommendation 2). MEASURED: a check session spends a
   median 117,693 tokens (mean 129,268; 3 to 10 turns) before its first check dispatch, over the nine check sessions
   of R6 to R9 (observed 2026-09-27; method: each session's main-thread usage summed up to and including the message
   that first calls `Agent`). That is about 5% of a typical session, so merging small groups would save little, while
   a larger budget raises every later turn's context. The fit, refitted over the same nine sessions, is peak =
   52,184 + 1.41 x load (a load of 28,000 predicts 91,639; a load of 33,934 predicts 100,000). DECISION: the budget
   stays at 28,000 - the start-up it would save is small, and the refit leaves headroom under 100,000.
3. **A page's round also takes the modals still owed from its other questions** (recommendation 3). `homes` credits
   an owed modal to the first of its questions the round changed, else to its own first question on the page; such a
   question enters the packing as an item whose load is its modals alone (its own findings are not re-checked), and
   its group's brief names the modals with `Your questions: none - this group checks only the modals and keys named
   below` when that is all it holds. Replayed at the archetypes write session's commit (7f0d8e4c): the round would
   have taken 100 and 140 plus every owed modal on the page - four folded into 100's group, eight dike-pond modals in a
   modal-only group - each checked once (observed 2026-09-27; method: `brief.py checks` in a detached worktree).
   None of the pages left has an owed modal today (`_entry_owed.py`: homesteads 24, archetypes 7, fields 6,
   vegetation 1 - all pages already worked), so the next page will not exercise this; those four stay with T23.
4. **The measured page is `cities/hinterland`**: two FR-002 items (questions 010 and 050), no FR-006 item, nothing
   over the cap - the nearest in size of the pages left. Compared in R10 with R6 to R9, per thing checked, saying
   which changes it exercised.

### D19 - The tenth round: a check reads the part of a long source it needs, then one more measured page (GM 2026-09-27)

The GM, on R10: *"Mark those two things as future work so we don't forget about it, but for now I want to focus on
getting the research process right. Go ahead and implement the 1 fix and then do 1 more round instead of proceeding
with the rest. If our guess is correct then after the 1 recommendation you've made will be the final adjustment ...
But if we do turn up anything else then we can keep iterating."*

1. **A long source is read in part** (R10's recommendation 1). `scripts/_source_pages.py` saves a page over 20,000
   characters as PARTS of at most 20,000 (`parts`), so a grep hit leads to one bounded read - for `source-reader`'s
   saved pages and every other caller; and, given the passages the record quotes from a source (`--quotes`), saves a
   page over 30,000 characters as an EXCERPT (`excerpt`): its first 6,000 characters (the front matter a source is
   judged by) and 1,500 either side of each quoted passage found in it, with a header saying how much of the page it
   is and how many of the passages were found, and a marker at every cut. `make check-bundle KEY=` hands it the key's
   quoted passages (`_check_bundle.quoted_passages`: every note of the key across the record, the ORIGIN of a
   translated quote, a link's href and a gloss under 20 characters left out). Measured on R10's book
   (`cdlib-local-elites`, a 1,372,518-character page): its bundle is now 22,857 characters, with all five passages the
   record quotes from it found (observed 2026-09-27; method: `make check-bundle KEY=cdlib-local-elites`). Tested
   (`tests/tooling/test_source_pages.py`, `test_check_bundle.py`).
2. **The two GM decisions R9 raised are future work** - `future-work/farming-communities.md`, the mulberry density
   and the modern dike forms, each with its evidence and a sketch, per the GM's instruction.
3. **The measured page is `water`**: two FR-002 items, as the last two pages had, and eight FR-006 items to confirm
   (as `fields` had four), nothing over the cap. Compared in R11 with R6 to R10, per thing checked, saying whether the
   excerpt acted (whether any source was long) and what else, if anything, the round turns up.

## Phases

0. Baseline and the meter (T01, T02).
1. **The measured slice** (T03 to T09), ending in the measurement report (T10). STOP for the GM - who ruled
   on 2026-09-26 (D6).
1b. **The token work** (T11 to T16), its second round (T26 to T33, D11) its third (T34 to T41, D12) its fourth (T42 to T46, D13) and its fifth (T47 to T51, D14): the fixes, the bundle and the guard (D6, D8), the page session (D7), the
   seeded-fault runs (D6), and the comparison (D9) - which is phase 2's first page.
2. FR-002 page by page, one page per session; FR-006 beside it, since both open the same fragments.
3. FR-003, FR-004, FR-005 (the cosmetic sweeps).
4. FR-007's owed checks over what phases 2 and 3 changed; FR-008; FR-009; the close.

## Complexity Tracking

Measurement scripts under `measure/`; one operation (`check-bundle`), one launcher (`page-session`) and one guard (`check-bundle-hooks.sh`), each the smallest form of a recommendation the GM adopted (D6-D8).

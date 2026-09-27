# Brief - feature 272 (temples and shrines researched), group S: the country shrine's open questions (second search), session 1: research and write

You are a FRESH session for one part of feature 272. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-shrines-1`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md`
above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** religion-and-death 130-206 and new 270-300 (feature 269's
burial group R1, in `/diagram/.clones/diagram-supplemental`); religion-and-death 220-260 (feature 267); every page
other than religion-and-death. Where a finding OWES one of those a correction, say exactly what in the handoff; the
orchestrator sends it to the owner. Other groups of THIS feature run beside you in sibling clones: stay inside your
own sections and range.
**FR-007 - the drawn country shrine.** For EVERY finding, say in the handoff whether it contradicts the Hoshigaoka
country-shrine sheet or its village map: the sheet (`pool/country-shrines/hoshigaoka-shrine/`) draws an open grove
with no fence or wall round the precinct, torii 12 ft apart on the approach, a 66 by 32 ft one-roof building (the
villagers' hall with the country monk's kitchen and dwelling at its ends), a stone basin and a sacred tree by the
approach; the village (`legacy-hand-authored-pool/villages/hoshigaoka/`) carries that shrine and no temple of its own.
A line per contradicting finding, `FR-007: <finding> - contradicts <what is drawn>`, or `FR-007: none`. Do NOT edit
the sheet or the map; the orchestrating session applies what contradicts them.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.

## Your items (group S)

- FR-001 **Every absence note and labeled guess in 090-128** (listed in `readers/272-shrine-absences.md`): a
  second search has run (`readers/272-reader-S.md`, by item label - GREP it by label, it is 100 KB; never read it
  whole). For each: ANSWERED -> cite it (through source-reader); HUMAN-FETCHABLE -> a TO-DOWNLOAD entry; STILL
  SILENT -> the absence note gains the second search (what, where, 2026-09-27) beside the first.
- D50 **A small kuri's size** (120): silent after the reader's second search unless the curl retry of its blocked
  sources answers - the note says which.
- D51 **A village shrine-temple's bell tower** (120): as D50.
- A133 A135 D49 D52-D56 (100-128, COVERED by 268): confirm only; change nothing that the second search leaves as it is.


## What was already read

A reader searched for these items on 2026-09-27; its report is `272-reader-S.md` and `272-shrine-absences.md` in `specs/272-temples-and-shrines-researched/readers/`. Its quotes are
leads, NOT citations: nothing is written from them until `source-reader` returns it READ (step 3). Its list of
blocked sources is where your TO-DOWNLOAD entries start - first try each once more with `curl` (a PDF through
`pdftotext`; a Shift_JIS page decoded as such), because the reader's fetch tool could not open a PDF.

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Save the pages.** Save every source you will cite with `make source-pages OUT=/tmp/l7r-check/272-s-pages
   URLS="<u1> <u2> ..."` (one directory for the group; a second call adds to it) and grep them yourself - a page over
   20,000 characters is saved in PARTS. Search further where the reader left an item thin. A source already in the
   registry reaches `source-reader` as `make check-bundle KEY=<key> WHOLE=1`.
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited), SILENT (nothing readable says it - an ABSENCE note with what was searched
   and when, both searches where there were two; the claim stays a labeled guess), or CONTRADICTION-RESOLVED (an
   existing section was wrong - say which and what corrects it). The GM's canon governs the setting: report the
   history against it, never override it.
5. **Write** on the existing sections religion-and-death 090, 100, 110, 120, 122, 124, 126, 128 (edits only; no new question). A new question is a fragment `research/religion-and-death/NNN-<heading id>.html` at a free
   prefix in your range, opening with `<h2 id="...">` whose text is the question a reader would ask from the map; a
   `<p><strong>Sources:</strong> ...</p>` roster; the finding; and where it drives what a map draws, the decision in
   plain words, labeled (accurate, deviation, convention, guess). Footnotes: `<sup class="fn" data-note="<key>"></sup>`
   in the prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted,
   translated and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by the record's rules. A
   new key gets its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is. A source only
   the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format (a heading, the
   believed link, a Google-search link, what rests on it, what blocked the fetch) - read its last entry first for the
   shape; never run git there. First `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` -
   never script an edit. Then in `.claude/skills/diagram`: `make record && make citations && make test-file
   FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py
   tests/interactive/test_record_format.py"`, and `python3 scripts/check-question-size.py` from the clone root (a
   question and its notes stay under 20,000 bytes - split one along its topics).
6. **Hand off.** Write `specs/272-temples-and-shrines-researched/briefs/s-handoff.md`: one line per new or changed question as
   `- SECTION=religion-and-death/<NNN>`, one per new registry key as `- KEY=<key>`, and one line per item:
   `<id> <OUTCOME> - <one sentence of what the record now says> - <what it means for the maps: what a generator or a
   sheet should draw differently, if anything>`. Then one line per TO-DOWNLOAD entry you appended, and anything left
   open and why. Commit (a message beginning `272 S:`). Do NOT run the record checks, do NOT push - the check
   sessions do that in fresh contexts. Your last message is one paragraph saying what you wrote.

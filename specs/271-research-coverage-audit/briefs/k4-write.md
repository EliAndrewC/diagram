# Brief - feature 271 (the research coverage backfill), group K4: cities/defenses: town walls, crossings and barbicans, session 1: research and write

You are a FRESH session for one part of feature 271. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-research-6`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 267: buildings 240-640, vegetation 170-200,
religion-and-death 220-260, fields 220-240 (magistracy and compound buildings); feature 268: religion-and-death 080-126;
feature 270: the country/village shrine hall's size; feature 269: every section its inventory
(`/diagram/.clones/diagram-supplemental/specs/269-research-backfill/inventory.md`) names, and its new ranges (fields
250-360, homesteads 250-360, water 290-360, vegetation 210-290, archetypes 200-270, religion-and-death 270-330,
cities/defenses 100-140, cities/government 100-140, cities/fabric 160-190, cities/hinterland 060-090, cities/sizing
030-050, settlements 030 and 090-110). Where a finding OWES one of those a correction, say exactly what in the handoff;
the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.
**Claims first (FR-002).** Before any research, read `/diagram/.clones/RESEARCH-CLAIMS.md`. Skip any item of yours
that another session has claimed since, and name it in the handoff. Then set 271's line there to say group K4 is
in progress; edit only that line.

## Your items (from `specs/271-research-coverage-audit/inventory.md`, group K4)

Each is a research QUESTION the record owes: never researched, labeled a guess, or thinly sourced. The kinds named are
the map features whose write-ups will be rewritten from what you find (by the orchestrating session, NOT by you).

- B07 C03 **Rampart in section**: how high and thick is a county town's and a provincial city's rampart, rammed earth,
  stone- or brick-faced or a Japanese earthwork (dorui, sōgamae), with what parapet, how many gates, and what of it
  shows from above? (towns/100; cities/capitals/150, 155; cities/defenses/060, 269 B38's - cite it). M. P1.
  > COORDINATION (C03): new question; cite 269's cities/defenses 020-090 (B38) for the city figures
- B08 **Town gate**: a gatehouse or a tower over the opening, its footprint and opening width, at a walled county town?
  (cities/defenses/030, 040 are the city's, 269 B38's). M. P1.
  > COORDINATION (B08): take the TOWN side; cite 269's cities/defenses 020/040/050/080/090 (B38) for the city figures
- C09 **Barbican**: did a provincial gate have a barbican (wengcheng) or a Japanese masugata, how large, and how
  common? (cities/defenses/050, names it). M. P1.
  > COORDINATION (C09): new question; cite 269's cities/defenses 020 (B38)
- C17 **Moat crossing**: fixed timber bridge, earthen causeway, stone bridge, drawbridge - how does a road cross the
  moat at a city gate, and how wide and long? (cities/capitals/240 is the castle's gates only). M. P1.
  > COORDINATION (C17): new question; cite 269's cities/defenses 040 (moat depth, B38)
- B09 **Town moat**: did a walled county town carry a moat or ditch, and how wide? (water/110, 120 are city moats).
  S. P3.
  > COORDINATION (B09): town side only; cite 269's cities/defenses 020/040/050/080/090 (B38) for the city
- B77 **Town inspection post**: did a town on a road keep a barrier or inspection post, and what did it look like?
  (urban-features/140; the city's is 269 B38's). S. P3.
  > COORDINATION (B77): town side only; cite 269's cities/defenses 050 (B38) for the city

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Find and save the pages.** Search (Japanese sources first for Edo villages and castle towns - jawiki, kotobank,
   a prefecture's or city's page, J-STAGE open papers, a museum's page; Chinese for Chinese practice). Save every
   candidate with `make source-pages OUT=/tmp/l7r-check/271-k4-pages URLS="<u1> <u2> ..."` (one directory for the
   group; a second call adds to it) and grep them yourself - a page over 20,000 characters is saved in PARTS, so a
   grep hit leads to one bounded read. A source already in the registry reaches `source-reader` as
   `make check-bundle KEY=<key> WHOLE=1` (the plain `KEY=` bundle is an excerpt for `source-applicability` only).
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited; the map rolls among them per settlement), SILENT (nothing readable says it -
   an ABSENCE note with what was searched and when; the claim stays a labeled guess), or CONTRADICTION-RESOLVED (an
   existing section was wrong - say which and what corrects it). A search that finds nothing is an outcome, not a
   failure: record it and move on. A degree along a continuum is calibrated liberty; distinct forms are a knob.
5. **Write** on cities/defenses 200-250, and the existing sections the items name. A new question is a fragment `research/<page>/NNN-<heading id>.html` at a free prefix in
   your range, opening with `<h2 id="...">` whose text is the question a reader would ask from the map; a
   `<p><strong>Sources:</strong> ...</p>` roster; the finding; and where it drives what a map draws, the decision in
   plain words. A THIN-SECTION item is answered in the section that makes the claim: every real-world assertion there
   ends cited, with an absence note, or labeled a guess. Footnotes: `<sup class="fn" data-note="<key>"></sup>` in the
   prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted, translated
   and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by the record's rules. A new key gets
   its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is (both write-ups). A source
   only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format. First
   `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` - never script an edit. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and
   `python3 scripts/check-question-size.py` from the clone root (a question and its notes stay under 20,000 bytes -
   split one along its topics).
6. **Hand off.** Write `specs/271-research-coverage-audit/briefs/k4-handoff.md`: one line per new or changed question as
   `- SECTION=<page>/<NNN>` (e.g. `- SECTION=homesteads/250`), one per new registry key as `- KEY=<key>`, and one line
   per item: `<id> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and maps
   named: what the generator should draw differently, if anything>`. Then anything left open and why. Commit (a
   message beginning `271 K4:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh
   contexts. Your last message is one paragraph saying what you wrote.

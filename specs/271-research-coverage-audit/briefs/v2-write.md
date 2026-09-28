# Brief - feature 271 (the research coverage backfill), group V2: homesteads: the yard and its animals, session 1: research and write

You are a FRESH session for one part of feature 271. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-research-1`); the project's CLAUDE.md files apply to you, the research record's
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
that another session has claimed since, and name it in the handoff. Then set 271's line there to say group V2 is
in progress; edit only that line.

## Your items (from `specs/271-research-coverage-audit/inventory.md`, group V2)

Each is a research QUESTION the record owes: never researched, labeled a guess, or thinly sourced. The kinds named are
the map features whose write-ups will be rewritten from what you find (by the orchestrating session, NOT by you).

- A82 **Draft animals**: ox or horse, by region, and what share of households kept one? (homesteads/070,
  homesteads/145). M. P1.
  > COORDINATION (A82): read 269 B16 (homesteads 300, in diagram-supplemental) first; if it answers the share of households, cite it and keep only ox against horse by region
- A83 **Pigs and poultry in a paddy hamlet**: did an ordinary south-China paddy hamlet keep pigs, poultry and ducks, and
  where (the sty is drawn only on dike-pond hamlets)? (archetypes/171). M. P1.
  > COORDINATION (A83): narrow to pigs and ducks on a PLAIN paddy hamlet; chickens are answered by 269 B13 (homesteads 250/218, Buck: 82% of farms) and dike-pond sties and pens by 269 B32 (archetypes, group A1) - cite both, read them in /diagram/.clones/diagram-supplemental
- A95 **Farmstead boundary**: a hedge (ikegaki), a stone wall, an earth bank or nothing, and how does it show?
  (homesteads/145). M. P1.
  > COORDINATION (A95): 269's vegetation 270 windbreak grove is the boundary planting on many farmsteads - cite it; the hedge, wall and bank question is ours
- A148 **Communal threshing floor**: did a south-China village thresh and dry on a shared floor (a stone roller, the
  drying ground before the hall) rather than each dooryard, and how big? (homesteads/020). M. P1.
  > COORDINATION (A148): 269 B05 (fields 290-310) covers the straw rick - cite it; the threshing floor is ours
- A17 **Drying racks (hasa)**: where were rice-drying racks put up - along bunds, by the lane, in the yard - how long,
  and how many per household? (homesteads/145). M. P2.
  > COORDINATION (A17): 269 B05 (fields 290-310, in diagram-supplemental) covers nimosaku and the straw rick - cite it for the rick; the racks are ours

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Find and save the pages.** Search (Japanese sources first for Edo villages and castle towns - jawiki, kotobank,
   a prefecture's or city's page, J-STAGE open papers, a museum's page; Chinese for Chinese practice). Save every
   candidate with `make source-pages OUT=/tmp/l7r-check/271-v2-pages URLS="<u1> <u2> ..."` (one directory for the
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
5. **Write** on homesteads 460-510, and the existing sections the items name. A new question is a fragment `research/<page>/NNN-<heading id>.html` at a free prefix in
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
6. **Hand off.** Write `specs/271-research-coverage-audit/briefs/v2-handoff.md`: one line per new or changed question as
   `- SECTION=<page>/<NNN>` (e.g. `- SECTION=homesteads/250`), one per new registry key as `- KEY=<key>`, and one line
   per item: `<id> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and maps
   named: what the generator should draw differently, if anything>`. Then anything left open and why. Commit (a
   message beginning `271 V2:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh
   contexts. Your last message is one paragraph saying what you wrote.

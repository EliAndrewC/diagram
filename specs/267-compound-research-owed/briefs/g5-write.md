# Brief - feature 267 (the compound research owed), group G5: the shrine, session 1: research and write

You are a FRESH session for one part of feature 267. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-buildings`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections** - feature 265, in another session, is working them: buildings 010, 070, 150, 170, 210;
cities/river-cities 010, 020, 030, 040; urban-features 010, 020, 030, 050, 060, 070, 080, 160; ways 020; towns 040,
080, 090, 100, 130; cities/capitals 040. Write the finding in a question of your own; where it OWES one of those
sections a correction, say exactly what in the handoff (the orchestrator makes it once 265 is done with the page).

## Your items (from `specs/267-compound-research-owed/inventory.md`, group G5)

Each is a research QUESTION the record owes. The kinds named are the map features whose write-ups will be rewritten
from what you find (by the orchestrating session, NOT by you); O, H, U are the Ochiba, Hayakawa and Ubame sheets.

- R36 **several kami in one hall** - one altar each, or sharing one. `shrine altar`, `compound shrine`. O H.
- R37 **the torii's distance** before a compound hall (the record's ~20 ft is a village shrine's; Ubame's ~5 ft). `torii`. H U.
- R38 **one torii for two shrines**. `torii`. H.
- R39 **salt wards (morijio)** at a compound's doors. `salt wards`. H.

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Find and save the pages.** Search (Japanese sources first for Edo buildings - jawiki, kotobank, a prefecture's
   or city's page on a surviving jin'ya, bukeyashiki or honjin; Chinese for yamen). Save every candidate with
   `make source-pages OUT=/tmp/l7r-check/g5-pages URLS="<u1> <u2> ..."` (one directory for the group; a second
   call adds to it) and grep them yourself - a page over 20,000 characters is saved in PARTS, so a grep hit leads to
   one bounded read. A source already in the registry reaches `source-reader` as `make check-bundle KEY=<key> WHOLE=1`
   (the whole page, in parts; the plain `KEY=` bundle is an excerpt for `source-applicability` only - 250 D19).
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited), SILENT (nothing readable says it - an ABSENCE note with what was
   searched and when), or CONTRADICTION-RESOLVED (an existing section was wrong). A CONTRADICTION-RESOLVED is not
   done until the wrong section is CORRECTED, cited, in this session - on any page, whatever its prefix - unless it is
   on the do-not-edit list above, in which case the handoff says exactly what the correction is. A search that finds
   nothing is an outcome, not a failure: record it and move on.
5. **Write.** Each item (or a few closely joined ones) is a question on religion-and-death 220-260: a new fragment
   `research/<page>/NNN-<heading id>.html` at a free prefix in your range, opening with `<h2 id="...">` whose text is
   the question a reader would ask from the map; a `<p><strong>Sources:</strong> ...</p>` roster; the finding; and
   where it drives what a plan draws, the decision in plain words. Footnotes: `<sup class="fn" data-note="<key>"></sup>`
   in the prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted,
   translated from Japanese or Chinese and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by
   the record's rules. A new key gets its registry entry in `research/sources/010-works-cited/NNNN-<key>.html`, shaped
   as `9340-bungotakada-tagoshi.html` is (both write-ups). First `Read` every file you will change ALL IN ONE MESSAGE,
   then `Edit`/`Write` - never script an edit. Then in `.claude/skills/diagram`: `make record && make citations &&
   make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py
   tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and `python3 scripts/check-question-size.py`
   from the clone root (a question and its notes stay under 20,000 bytes - split one along its topics).
6. **Hand off.** Write `specs/267-compound-research-owed/briefs/g5-handoff.md`: one line per new or changed question - a corrected
   existing section included, so the checks read it - as `- SECTION=<page>/<NNN>` (e.g. `- SECTION=buildings/240`), one per new registry key as `- KEY=<key>`, and one line
   per item: `R<nn> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and sheets
   named>`. Then anything left open and why. Commit (a message naming the group). Do NOT run the record checks, do NOT
   push - the check sessions do that in fresh contexts. Your last message is one paragraph saying what you wrote.

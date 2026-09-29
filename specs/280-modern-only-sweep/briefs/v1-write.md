# Brief - feature 280 (the modern-only sweep), group V1: vegetation: the belts and groves' extent, session 1: research and write

You are a FRESH session for one part of feature 280. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`/diagram/.clones/diagram-supplemental-2`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**What the feature is for.** The GM, 2026-09-28: *"We should eliminate anything which is only modern"* and *"We should
avoid anything that appears only on modern lists."* Each item below is a form a map draws (or a figure it uses) that an
audit found MAY be attested only in the modern period. Your job is to find out, searching for a PREMODERN attestation
FIRST, and to record what you find. You do not change the engine or the maps: the eliminations are a later phase.

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**A held section is researched, never edited, and never skipped.** A section is HELD when the claims file names it
in progress for another feature (religion-and-death 124-129 are feature 279's while its line is open), or when
feature 269 rewrote it and has not landed - whatever 269's claim line says, "done, committed in clone" included: any
output from `git -C /diagram/.clones/diagram-supplemental log origin/main..HEAD --oneline -- .claude/skills/diagram/research/<page>/<NNN>-*`
means unlanded. For an item on a held section, do the research all the same, but do not edit the section: put the
outcome in the handoff as usual, with `OWED-TO <feature>` and the exact text the section owes (the finding and its
footnotes), so the orchestrator applies it once the hold clears. No item leaves your session without an outcome.
**Coordination files are read by line, never whole** (feature 274): `make lines FILE=<f> KEY=<regex>` and
`make append FILE=<f> LINE="<text>"`. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md
KEY="<each page your items name>"` (a held section is handled as above, never skipped); then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram supplemental (diagram-supplemental-2) | 280 |
group V1 in progress (<the sections>) | <date>"`. Read only your own lines of a handoff (`make lines
FILE=<handoff> KEY="SECTION=<yours>|KEY=<yours>"`), and add to a checks report with `make append`.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`), never "the highest + 10" by eye; a write session's eleventh registry key is refused - then
follow its message (write the unreached items to `$L7R_CONTINUE` as a brief of this same shape, commit, stop).

## Your items (from `specs/280-modern-only-sweep/inventory.md`, group V1)

Each names the section that makes the claim, the drawn form, why the audit thinks it modern-only, and the maps it
touches. The kinds and maps named will be changed from your outcome by the orchestrating session, NOT by you.

- M40 **Fengshui-forest scale**: a back belt of about 1-2 ha and about 3,400 stems/ha, with a hundred to three hundred canopy crowns. Every size is measured on groves surviving today: afcd-hkbio-8, hu-2011-fengshui-patches (2011), zhongshan-fsw-2016 and forests-2020. The institution is premodern; whether today's extent reflects modern conservation is open (vegetation/010) - kinds: Windbreak, Copse; maps: the scripted hamlets' belts, and legacy hoshigaoka. L.
- M41 **The afternoon-sun lane**: no belt clump within 50 ft west or southwest of a yard or garden. The principle's only source is umca-windbreak-manual, "a present-day agroforestry training manual"; the 50 ft is the page's own. The sun lane of M14 depends on it (vegetation/020) - kinds: Windbreak; `hamletgen/consts.py`, `hinterland/belt.py`; maps: all scripted hamlets. M.
- M42 **A lane through the belt**: how a lane crosses the belt, and the rule that a bare run wider than about 30 ft is a hole and is filled. The section says "the angled crossing is a modern extension service's design rule, borrowed here because nothing read says how a Chinese or Japanese planter cut an access through a belt" (umca-windbreak-manual). The gap rule is from umca alone. Confirm whether any angle or end offset reaches the engine; the auditor's grep found none (vegetation/030) - kinds: Windbreak; maps: the scripted hamlets. S.
- M43 **The water-mouth grove**: a cluster of about 0.1-0.5 ha. It is a GUESS bracketed by modern surveys of surviving Korean groves (park-2013-maeulsup, kweon-youn-2021), with no Chinese measurement (vegetation/290) - kinds: Windbreak, Copse (the water-mouth cluster); maps: mizuguchi, and legacy hoshigaoka. L.

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Search for a PREMODERN attestation first.** For each item, search for the form before modernity: in Japan before
   the Meiji Restoration (1868), in China before the end of the Qing (1912). Look for Edo farm manuals (nosho, e.g.
   農業全書, 百姓伝記), period illustrations (名所図会, 農業図絵, 耕作図), village records (村明細帳), archaeology, a
   museum's or prefecture's page, J-STAGE open papers, kotobank and jawiki for Japan; 天工開物, 農政全書, gazetteers
   (地方志) and the Chinese Text Project for China; and modern historians who DATE the form. Search in Japanese or
   Chinese as well as English. Save every candidate page with `make source-pages OUT=/tmp/l7r-check/280-v1-pages
   URLS="<u1> <u2> ..."` (one directory for the group; a second call adds to it) and grep them yourself - a page over
   20,000 characters is saved in PARTS. A source already in the registry reaches `source-reader` as
   `make check-bundle KEY=<key> WHOLE=1`. Keep a list of every search you ran (terms, language, where) - a MODERN-ONLY
   outcome must state it.
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read - exactly one of:
   - **PREMODERN-ATTESTED**: a readable source places the form in Japan before 1868 or in China before 1912, whatever
     the source's own date (a modern historian who dates it counts). Cite it.
   - **MODERN-ONLY**: every attestation found is modern practice, or a 20th-century record that gives no date. Record
     the search that found nothing earlier: the terms, languages and places searched, and the date. Where the only
     attestation is an undated modern record of custom ("in the old days", remembered practice), the outcome is
     MODERN-ONLY with the tag `undated-custom` (spec D1: an undated record could mean the Meiji era; the GM may re-sort
     that set).
   - **MIXED**: some forms (or some values of a figure) are attested premodern and some only modern. Name each form,
     cite the attested ones, give the search for the rest. For a degree (a size, density, count), give the premodern
     figure the map should be calibrated to, as the GM ruled for mulberry spacing.
   A search that finds nothing is an outcome, not a failure: record it and move on.
5. **Write** on vegetation/010, vegetation/020, vegetation/030, vegetation/290, and vegetation 600-690 for a new question - a held section excepted (the held rule above: its text goes in the handoff). The finding is written in the section that makes the claim: the premodern attestation cited,
   or the modern-only finding with its search and date, and the decision in plain words ("the maps do not draw it").
   Write it as the finding a casual reader needs, never as what the section used to say. A new question, where one is
   needed, is a fragment `research/<page>/NNN-<heading id>.html` at a free prefix in your range, opening with
   `<h2 id="...">` whose text is the question a reader would ask from the map, and a
   `<p><strong>Sources:</strong> ...</p>` roster. Footnotes: `<sup class="fn" data-note="<key>"></sup>` in the prose,
   `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted, translated and
   marked as such, the original after), an ABSENCE note (what was searched, where, when), or a GROUNDS note. A new
   key gets its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is (both write-ups). A
   source only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format.
   First `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` - never script an edit. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and
   `python3 scripts/check-question-size.py` from the clone root (a question and its notes stay under 20,000 bytes -
   split one along its topics).
6. **Hand off.** Write `specs/280-modern-only-sweep/briefs/v1-handoff.md`: one line per new or changed question as
   `- SECTION=<page>/<NNN>` (e.g. `- SECTION=homesteads/250`), one per new registry key as `- KEY=<key>`, and one line
   per item: `M<nn> <OUTCOME>[ undated-custom] - <one sentence of what the record now says> - <what it means for the
   kinds and maps named: what the generator should stop drawing, or draw instead, if anything> - <searched: terms,
   languages, where, date> (for MODERN-ONLY and MIXED)`. Say also, per item, whether the GM ruled the form in (the
   record or the kind says so) and whether knowingly. Then anything left open and why. Commit (a message beginning
   `280 V1:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh contexts. Your
   last message is one paragraph saying what you wrote.

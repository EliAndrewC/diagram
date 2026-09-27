# Brief - feature 250, page `cities/river-cities` (T03), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research-3`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=cities/river-cities SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "cities/river-cities <step>" --marks specs/250-close-the-record-checks/measure/marks-cities-river-cities.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **Most provincial cities sit on a river** - "tapping the river upstream and returning downstream so the current flushes it" - no footnote of its own; fn-40, which closes the sentence, quotes only siting and moat width.  _(from `qc-river-cities-defenses-towns.md`)_
- **Most provincial cities sit on a river** - spec 1: "the river IS the stronger defense on that flank" - a comparative claim about defense, footnoted nowhere on the page.  _(from `qc-river-cities-defenses-towns.md`)_
- **Most provincial cities sit on a river** - spec 1: "the dead cross the river: the moat's water set-back leaves no dry landward fringe to put them on, so the funerary ground sits on the far bank, downstream of the city and clear of the bridge road" - siting of graves relative to water; no footnote and no cross-reference.  _(from `qc-river-cities-defenses-towns.md`)_
- **Most provincial cities sit on a river** - spec 2: "a burial or cremation ground sits beside the farmland, never on a paddy body or on its ditches" - same class; presumably grounded on another page, but not pointed at from here.  _(from `qc-river-cities-defenses-towns.md`)_
- **Which way does an offtake leave a river, and why?** - "what the engineering literature appears to hold, on no page that could be read, is that a diversion draws its LEAST sediment at an intermediate angle rather than at the square, and that the often-quoted 90 to 120 degree rule for a headworks is measured from the WEIR's axis rather than from the river's own line" - two claims about engineering practice, disclosed in prose but carrying neither a footnote nor an absence note.  _(from `qc-river-cities-defenses-towns.md`)_
- **Does a city's canal open its own mouth on the river?** - "the moat's downstream river junction is then the single navigation entrance" - the exclusivity is in neither fn-4 nor fn-7 (the entry it refers back to), and no footnote is attached here.  _(from `qc-river-cities-defenses-towns.md`)_
- **The wharf's working face** - "The Chinese matou (碼頭) is, in one of its two forms, a stepped landing … set into a faced bank" - carries no footnote of its own; the note that would support it (fn-31) is attached to a later clause.  _(from `qc-river-cities-defenses-towns.md`)_
- **The wharf's working face** - "a port that also handles timber and stone wants at least one [pier]" - a claim about port practice, unfootnoted.  _(from `qc-river-cities-defenses-towns.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/cities/river-cities/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- none

**Over the size cap on this page:** none

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/cities/river-cities/`; note the fragment and
   sentence. An item that is a claim about the SETTING is checked against the GM's canon - `budgets.md` and `l7r.md`
   in `/host-l7r-repo/setting/`, and `/host-l7r-repo/gm-assistant/setting/*.md` - with ONE call naming every term of
   every such item: `make canon TERMS="<term>|<term>|<term>"` (in `.claude/skills/diagram`). A direct read of a canon
   file is refused, and so is a second call that does not fold the first's terms (`canon-read-hooks.sh`; R7: fifteen
   sequential greps on the last page).
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/cities-river-cities-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). Keep ONE directory for the page: a second `make source-pages` into it ADDS pages, it never
   overwrites the first batch. A source already in the registry: `make check-bundle KEY=<key> WHOLE=1` (the whole page, in parts) and name its MANIFEST.md.
3. **Write the notes.** First `Read` every fragment and notes file you will change, ALL IN ONE MESSAGE (parallel
   `Read` calls): `Edit` needs the read, and a file a turn re-reads your whole context each time (feature 250 R6:
   the write step took 19 turns for three items). In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its
   `.notes.html` `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new registry entry:
   `make reserve KIND=registry KEY=<key>` (in `.claude/skills/diagram`) reserves its prefix under a host-wide lock and
   writes the empty file - fill it, shaped as `.claude/skills/diagram/research/sources/010-works-cited/9400-suzhou-enwiki.html` is (copy its shape rather than studying others). A new file
   there written any other way is refused (`new-file-hooks.sh`: queues run in parallel, and a hand-taken prefix
   collides). `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
3b. **Keep every question you touched under the size cap** - 20,000 bytes, question plus notes
   (`python3 scripts/check-question-size.py` from the clone root names any over it; `make quick` fails on one). A
   question over it is SPLIT along its topics: a finding stays with the decision it drove; each part becomes its own
   question - a free prefix, an `<h2 id>` that is the question a reader would ask, its own `Sources:` line naming the
   keys its notes quote, and the notes that its sentences cite moved into its own `.notes.html`; and the sentences that
   join the parts POINT at each other (a link and what the other question is about) rather than restating its
   evidence, so a check reading one part alone meets no claim without its footnote. If a split would separate a
   finding from what it needs to be understood, say so in the handoff instead of splitting. A question named
   above as over the cap that one of your items falls in is split HERE, in this session, while you have it read
   (feature 250 R6: a split in a session of its own cost about 0.8 million, most of it re-reading the question);
   every part goes in the handoff as its own `SECTION=` line, and in one line say what each part relies on from
   the others.
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/cities-river-cities-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

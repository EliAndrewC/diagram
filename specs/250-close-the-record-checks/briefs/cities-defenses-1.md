# Brief - feature 250, page `cities/defenses` (T40), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=cities/defenses SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "cities/defenses <step>" --marks specs/250-close-the-record-checks/measure/marks-cities-defenses.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **Does the city wall close a full ring - and why so few gates?** - "weng is an urn and the name is the urn's" - a philological claim with no footnote (fn-19 beside it gives the square plan, not the etymology).  _(from `qc-river-cities-defenses-towns.md`)_
- **Does the city wall close a full ring - and why so few gates?** - "Setting the three of them against the European sally port as its nearest equivalents is this record's own comparison; no source makes it." - honestly labeled in prose, but it is a bare sentence with no absence note.  _(from `qc-river-cities-defenses-towns.md`)_
- **What keeps the moat full?** - "A wet ditch has to be fed, and a trickle cannot hold one full against seepage and evaporation: the channel that supplies a moat carries something like what the moat itself holds." - a physical claim; the Sources line says it "rests on this project's own reasoning about flow", but the sentence carries no footnote or absence note.  _(from `qc-river-cities-defenses-towns.md`)_
- **Wall towers - the mamian system and bowshot ranges** - spec 2: "a tower counts as reaching 36 ft past its recorded center, because an archer shoots from the bastion's parapet SPAN and not from a point" - the archery premise is unfootnoted.  _(from `qc-river-cities-defenses-towns.md`)_
- **Wall towers - the mamian system and bowshot ranges** - spec 2: "within 186 ft of a ward gate where a neighborhood fence meets the rampart, which is a manned chokepoint" - "manned" is unfootnoted.  _(from `qc-river-cities-defenses-towns.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/cities/defenses/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- 7. [HIGH] L0 NOT-LOCATED | 4. Gate structures - real footprints | (reserve the 120-130 ft towers for a capital)

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/cities/defenses/`; note the fragment and
   sentence.
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/cities-defenses-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). A source already in the registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its `.notes.html`
   `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/cities-defenses-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

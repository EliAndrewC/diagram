# Brief - feature 250, page `towns` (T04), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research-2`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=towns SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "towns <step>" --marks specs/250-close-the-record-checks/measure/marks-towns.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **The market-day flophouse** - spec: "It is deliberately large, plain and barn-like - no awning, a long row of plain doorways - … it beds dozens on market eve." - the form and the capacity are claims about the building; no footnote.  _(from `qc-river-cities-defenses-towns.md`)_
- **The market-day flophouse** - spec: "since the gate shuts at dusk and a peasant arriving late cannot get in at all" - the dusk closing has no footnote here (and where it is footnoted, fn-38, the source is about ward gates).  _(from `qc-river-cities-defenses-towns.md`)_
- **The gate market exists for TRAFFIC, not taxes** - "the market-day chokepoint where the rural catchment trades" - the middle of the three named drivers, and the only one with no footnote (the first has fn-20, the third fn-38).  _(from `qc-river-cities-defenses-towns.md`)_
- **A street is access infrastructure for the buildings it serves** - "it is paved or worn into the ground by the foot traffic to and from them" - unfootnoted.  _(from `qc-river-cities-defenses-towns.md`)_
- **A street is access infrastructure for the buildings it serves** - "and a desire path forms only between real destinations" - unfootnoted (the record holds desire-path sources elsewhere; none is pointed at here).  _(from `qc-river-cities-defenses-towns.md`)_
- **A street is access infrastructure for the buildings it serves** - Observation rather than a missing footnote: the hutong sentence sets *"emerged as access routes lined by contiguous courtyard residences"* in quotation marks, and fn-14's own comment says those are not the page's words - my fetch confirms the page reads 「hutongs are alleys formed by lines of siheyuan…」 and 「Many neighbourhoods were formed by joining one siheyuan to another to form a hutong」. A quoted span that is a paraphrase.  _(from `qc-river-cities-defenses-towns.md`)_
- **A rampart's cost scales with its LENGTH** - "its cost scales with its length" - disclosed in prose as "this page's reasoning; no page read prices a wall" (my fetch confirms it), but the clause carries no footnote or absence note.  _(from `qc-river-cities-defenses-towns.md`)_
- **A rampart's cost scales with its LENGTH** - spec: "since a wall climbs or skirts a hill rather than leveling it" - unfootnoted.  _(from `qc-river-cities-defenses-towns.md`)_
- **A rampart's cost scales with its LENGTH** - Observation: the spec-adjacent 「no empty ground」 in the finding uses the source-quotation brackets around this project's own phrase, which no source said.  _(from `qc-river-cities-defenses-towns.md`)_
- **How is a town farmstead laid out?** - "because a farmer builds close to the ground they work (this page's reasoning)" - disclosed, no footnote or absence note.  _(from `qc-river-cities-defenses-towns.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/towns/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- none

**Over the size cap on this page:** none

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/towns/`; note the fragment and
   sentence. An item that is a claim about the SETTING is checked against the GM's canon - `budgets.md` and `l7r.md`
   in `/host-l7r-repo/setting/`, and `/host-l7r-repo/gm-assistant/setting/*.md` - with ONE call naming every term of
   every such item: `make canon TERMS="<term>|<term>|<term>"` (in `.claude/skills/diagram`). A direct read of a canon
   file is refused, and so is a second call that does not fold the first's terms (`canon-read-hooks.sh`; R7: fifteen
   sequential greps on the last page).
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/towns-pages URLS="<u1>
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
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/towns-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

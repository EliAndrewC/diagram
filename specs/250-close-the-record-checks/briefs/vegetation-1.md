# Brief - feature 250, page `vegetation` (T32), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=vegetation SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "vegetation <step>" --marks specs/250-close-the-record-checks/measure/marks-vegetation.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **with occasional wider emergents** - *"with occasional wider emergents"* ("Forest density and crown size") — a claim about a real stand; fn-100 covers only the 5-8 m crown.  _(from `qc-buildings-vegetation.md`)_
- **Constant cutting is why woody scrub could not establish within about a scythe's swath (~1-2 m) of a field edge** - *"Constant cutting is why woody scrub could not establish within about a scythe's swath (~1-2 m) of a field edge"* ("The crop margin") — the causal claim and the swath figure carry nothing; fn-103 sits on the next clause.  _(from `qc-buildings-vegetation.md`)_
- **6 ft = one scythe swath** - *"6 ft = one scythe swath"* ("The cut bank") — no footnote.  _(from `qc-buildings-vegetation.md`)_
- **A working belt about 10 m tall** - *"A working belt about 10 m tall"* ("What are the village's three groves") — the belt height is the input to fn-121's trigonometry and is itself uncited.  _(from `qc-buildings-vegetation.md`)_
- **the take-yabu (bamboo thicket) as its own stand at the village edge, harvested like a coppice** - *"the take-yabu (bamboo thicket) as its own stand at the village edge, harvested like a coppice"* ("Bamboo") — no footnote.  _(from `qc-buildings-vegetation.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/vegetation/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- 19. [LOW] L0 TOO-SHORT |  | ...

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/vegetation/`; note the fragment and
   sentence.
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/vegetation-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). A source already in the registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its `.notes.html`
   `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/vegetation-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

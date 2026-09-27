# Brief - feature 250, page `cities/government` (T50), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=cities/government SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "cities/government <step>" --marks specs/250-close-the-record-checks/measure/marks-cities-government.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **What stands between the temples in a temple neighborhood** - *"What stands between the temples in a temple neighborhood"* — **"The vermilion shed is an Inari form"**. A claim about a real shrine type, no note; the sentence's fn-38 is an absence note about the temple-quarter placement, not about the Inari attribution.  _(from `qc-fabric-government-hinterland-ways.md`)_
- **Martial training is an URBAN institution** - *"Martial training is an URBAN institution"* — **"nearly every one of the ~260 domains had one"**: fn-4 gives 255 schools and 「ほぼ全藩」, but the ~260-domain denominator is in no quote.  _(from `qc-fabric-government-hinterland-ways.md`)_
- **Servant housing in the samurai ward** - *"Servant housing in the samurai ward"* — **"hired out of the merchant quarter through labor brokers"**: fn-10 and fn-56 both concede the merchant-quarter half is on no page read, and no absence note stands beside it.  _(from `qc-fabric-government-hinterland-ways.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/cities/government/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- none

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/cities/government/`; note the fragment and
   sentence.
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/cities-government-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). A source already in the registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its `.notes.html`
   `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
3b. **Keep every question you touched under the size cap** - 20,000 bytes, question plus notes
   (`python3 scripts/check-question-size.py` from the clone root names any over it; `make quick` fails on one). A
   question over it is SPLIT along its topics: a finding stays with the decision it drove; each part becomes its own
   question - a free prefix, an `<h2 id>` that is the question a reader would ask, its own `Sources:` line naming the
   keys its notes quote, and the notes that its sentences cite moved into its own `.notes.html`; and the sentences that
   join the parts POINT at each other (a link and what the other question is about) rather than restating its
   evidence, so a check reading one part alone meets no claim without its footnote. If a split would separate a
   finding from what it needs to be understood, say so in the handoff instead of splitting.
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/cities-government-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

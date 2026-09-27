# Brief - feature 250, page `religion-and-death` (T45), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=religion-and-death SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "religion-and-death <step>" --marks specs/250-close-the-record-checks/measure/marks-religion-and-death.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **Many modest temples per walled city is the historical norm** - *Many modest temples per walled city is the historical norm*: "**Sakai ~60 and ~50 in its two wards**" and "**Akita 43 in 1663**" carry no footnote marker; their note (`fn-138`) is attached two clauses later. This is the same finding as B above, stated from the other side.  _(from `qc-fields-religion-archetypes.md`)_
- **City temple size - the deliberate L7R liberty** - *City temple size - the deliberate L7R liberty*: "small hereditary Chinese temples held a handful of monks" — the sentence's `fn-136` quotes the Ming one-monastery/two-monk limit, which is adjacent but is not this claim.  _(from `qc-fields-religion-archetypes.md`)_
- **Where do the crematory, the ossuary and the clan mausoleum stand?** - *Where do the crematory, the ossuary and the clan mausoleum stand?*: "Monks officiate with *burakumin* assistants, a religious order standing outside the caste system, so handling the dead does not pollute its caste." — no footnote; setting canon, which the record elsewhere cites by key to the GM's notes.  _(from `qc-fields-religion-archetypes.md`)_
- **How large are the gates, walls and funerary features drawn?** - *How large are the gates, walls and funerary features drawn?*: "Cremated bone takes almost no volume" — no footnote (a candidate for a grounds note on physical necessity rather than a citation).  _(from `qc-fields-religion-archetypes.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/religion-and-death/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- 14. [HIGH] L0 NOT-LOCATED |  | A **provincial city** (~3,000 inhabitants) has **~15-30 monks per complex** (a serious Ming urban monastery's scale); a **domain capital** (

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/religion-and-death/`; note the fragment and
   sentence.
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/religion-and-death-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). A source already in the registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its `.notes.html`
   `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/religion-and-death-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

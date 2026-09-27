# Brief - feature 250, page `urban-features` (T05), session 1 of 2: locate, read and write

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`/diagram/.clones/diagram-research-1`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE=urban-features SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "urban-features <step>" --marks specs/250-close-the-record-checks/measure/marks-urban-features.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **The notice board (kosatsuba)** - *"...ban edicts - and its siting was a TRAFFIC decision"* - every other item in that list of what a board carried has its own mark; "ban edicts" has none.  _(from `urban-quotecheck.md`)_
- **The notice board (kosatsuba)** - *"the board is also the state's standing presence in a place that may see a magistrate's deputy **twice a year**."* - a frequency of official visitation, no mark.  _(from `urban-quotecheck.md`)_
- **The notice board (kosatsuba)** - *"**Every** attested site is ON the way - a verge, a gate front, a bridge foot - **never** a plot of open ground beside it."* - an exhaustive claim over the attested corpus, no mark of its own.  _(from `urban-quotecheck.md`)_
- **The justice works** - *"The bamboo (笞 / 杖) was a COURT act administered inside the yamen courtyard before the magistrate's bench"* - how the beating was administered; fn-145 beside it covers the cangue only.  _(from `urban-quotecheck.md`)_
- **Trade works** - *"A provincial city adds the daimyo's stable (**several hundred horses per domain**)"* - a stock figure for a domain, no mark. (Under "Tanning yards", but it is a trade-works claim.)  _(from `urban-quotecheck.md`)_
- **The bell-and-drum tower** - *"...the City God temple ranked down to the county **from 1369**"* - a dated administrative fact named as attested, no mark.  _(from `urban-quotecheck.md`)_
- **The bell-and-drum tower** - *"Beijing's single drum tower timed the watches for an inner city **~6.5 x 5.3 km**"* - a dimension of a real city, no mark.  _(from `urban-quotecheck.md`)_
- **Stable yards** - *"the Chinese hitching post 拴马桩"* named as **WELL-ATTESTED** in the same sentence - no mark anywhere on it.  _(from `urban-quotecheck.md`)_
- **Stable yards** - *"cattle drink **~1-2 gal/min**, so a working ox's 5-8 gal session is over in ~5 minutes"* - a physiological rate, no mark.  _(from `urban-quotecheck.md`)_
- **Stable yards** - *"That fits how a stage stop worked: **animals were unyoked and rested for HOURS**"* - a practice, no mark.  _(from `urban-quotecheck.md`)_
- **Tanning yards** - *"real castle towns kept **designated carcass routes** off the main streets for precisely that reason"* (in the kegare-direction bullet) - no mark. The same claim two paragraphs later **does** carry fn-161, which is the absence note saying no page read records such a rule; the first statement of it stands bare.  _(from `urban-quotecheck.md`)_
- **Refining forges / clan border** - *"agreed between the two domains in 1642 **after more than fifty years of dispute**, and **growing smaller and more closely spaced over time** as the zonal frontier became a line"* - fn-65 carries the 1642 re-confirmation and the 130 km line, but neither the fifty years nor the changing spacing.  _(from `urban-quotecheck.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/urban-features/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

- 36. [HIGH] L228 AMBIGUOUS(2) |  | which is exactly why caravanserais centralized on one courtyard well/cistern instead of multiplying basins, and why coaching-inn yards typic
- 58. [HIGH] L0 NOT-LOCATED |  | ... because salted and dried raw hides keep for months and that storage is how the entire pre-modern hide trade worked ...
- 59. [HIGH] L0 TOO-SHORT |  | the
- 60. [HIGH] L0 NOT-LOCATED |  | Wealthy samurai kept walled country **estates outside the walls** and commuted in, for roomier houses than cramped city lots allowed.
- 86. [MEDIUM] L0 NOT-LOCATED |  | **Potters are not hinin.**
- 87. [MEDIUM] L0 NOT-LOCATED |  | The caste's own name for itself was *kawaramono*,

**Over the size cap on this page:** none

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/urban-features/`; note the fragment and
   sentence. An item that is a claim about the SETTING is checked against the GM's canon - `budgets.md` and `l7r.md`
   in `/host-l7r-repo/setting/`, and `/host-l7r-repo/gm-assistant/setting/*.md` - with ONE call naming every term of
   every such item: `make canon TERMS="<term>|<term>|<term>"` (in `.claude/skills/diagram`). A direct read of a canon
   file is refused, and so is a second call that does not fold the first's terms (`canon-read-hooks.sh`; R7: fifteen
   sequential greps on the last page).
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/urban-features-pages URLS="<u1>
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
4. **Hand off.** Write `specs/250-close-the-record-checks/briefs/urban-features-handoff.md`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.

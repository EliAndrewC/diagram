# Brief - feature 250, page `homesteads` (T18)

You are a FRESH session for one page of feature 250 (close the record checks). This brief is the whole of
what you need; do not read the feature's spec, plan or research files to orient - they cost you tokens on
every later turn, and everything they would tell you about this page is here. Work in this clone
(`/diagram/.clones/diagram-research`); the project's CLAUDE.md files still apply to you.

## Measure as you go

Before each numbered step below, open a window on the token meter:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "<page> <step>" --marks specs/250-close-the-record-checks/measure/marks-homesteads.json

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

- **May a byre stand beside a wellhead?** - *"And the well (ido), where a house had one, sat "in the rear corner of the earthen-floored doma or in a rear projection room" - i.e. inside the same building."* — a **quotation in the visible prose with no footnote and no key**. The nearest mark, `fn-138`, sits on the following sentence and is an absence note about farmhouse plan dimensions, not about the in-house well.  _(from `hw-quotecheck.md`)_
- **Is every farmhouse reached by a lane, and in what FORM?** - *""every house in the nucleated village is accessible via the INTERCONNECTED system of narrow lanes and alleys""* (in the GM's-question paragraph) — a quotation with no footnote. `fn-132` earlier in the section is an absence note saying the two passages this page paraphrases are on no page fetched; the quotation is repeated here unmarked.  _(from `hw-quotecheck.md`)_
- **The garden's sun, and how far the windbreak shades** - *"house faces E, away from the SW wind; the front (E) yard is the work yard, "securing adequate open space" with only fruit trees and a persimmon in the yard center; S and W carry 2-3 rows of sugi; the N/W bamboo strip is "shady ... always damp""* — three quoted fragments from the Tonami model homestead, with an inline `no publicly readable source, searched 2026-09-06` in the prose but **no footnote** on any of them.  _(from `hw-quotecheck.md`)_
- **The threshing yard's sun** - *"which agrees with surviving farmhouses (~6-7 m)"* — a measurement of real buildings, no footnote. (The section's Sources line discloses the figure is unsourced; the assertion itself carries nothing.)  _(from `hw-quotecheck.md`)_
- **The farmstead's fixtures** - *"Stable litter and grass composted into stable manure (kyuhi, 厩肥)"* — carries an inline "(no readable page supports it)" but **no footnote**.  _(from `hw-quotecheck.md`)_

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words (a figure, a name, a term) over `research/homesteads/*.html` - the section label beside it is
the REPORT's heading, not the record's, and is only a hint. Then either confirm the sentence carries its note
(say which note) or work it as an FR-002 item. Never confirm against a fragment the grep did not name.

- 22. [HIGH] L0 NOT-LOCATED | The garden's sun, and how far the windbreak shades | Tohoku sources put a mature skeleton at 20 m+
- 23. [HIGH] L0 NOT-LOCATED | The garden's sun, and how far the windbreak shades | Kainyo/igune are limb-pruned (edauchi), never height-capped.
- 24. [HIGH] L0 NOT-LOCATED | The garden's sun, and how far the windbreak shades | Tohoku: the S-facing open ground in front is the drying yard.

## The procedure

1. **Locate.** For every item, grep its words over `.claude/skills/diagram/research/homesteads/` and note the
   fragment and sentence. Read only the fragments that hold items.
2. **Read the sources.** Save the candidate pages with `make source-pages OUT=<dir> URLS="<u1> <u2>"` (in
   `.claude/skills/diagram`; `<dir>` under `/tmp/l7r-check/`), grep them yourself for the passages, then
   dispatch ONE `source-reader` over every item at once. Hand it the saved-pages directory and each claim's
   text written into the prompt - never a path under `/diagram` (a reader that opens one is handed ~28,000
   tokens of CLAUDE.md files; `check-bundle-hooks.sh` refuses the dispatch). A source already in the
   registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment, `<sup class="fn" data-note="<key>"></sup>` at the sentence; in its
   `.notes.html`, `<li data-note="<key>">...</li>` (no numbers anywhere). A new registry key needs both
   write-ups in a new `research/sources/010-works-cited/NNNN-<key>.html` (a free prefix; copy a neighbor's
   shape). Use `Edit`, not a script, on a file you have read. Then in `.claude/skills/diagram`:
   `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. **Check, one agent per changed entry or key, all in one message, in the background.** For each changed
   question: `make check-bundle PAGE=homesteads SECTION=<NNN>`, then `quote-check` and `record-format`, each
   naming the MANIFEST.md it printed and nothing else. For each new or changed registry key:
   `make check-bundle KEY=<key>` and `source-applicability`. Each replies with ONE line of counts and writes
   its report to `REPORT.md` in its bundle.
5. **Apply.** Open a REPORT.md only when its line reports something to apply; apply every finding (a new
   glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then `make glossary`); re-run
   step 3's commands.
6. **Close.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py homesteads.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T=T18 BOXES=1 NOTE="<what closed, with the counts>"`.
   Do NOT run `scripts/sync-with-main.sh done` - the feature has other open tasks.
7. **Report.** Your last message is one paragraph: items closed per form (citation / absence / grounds),
   FR-006 items confirmed or worked, the agents run, and anything left open and why.

If a finding needs the GM (a claim the record contradicts, a rule that would change), do not decide it: write
it into your last paragraph and leave the text as it is.

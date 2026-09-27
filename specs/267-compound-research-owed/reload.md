# The research procedure, reloaded from main (FR-009; the GM, 2026-09-27: "reload whatever files talk about how to do research")

Read in this clone after `sync-in` at main `51515eb6` (2026-09-27), which carries feature 250's landing, and found by
search rather than memory (`grep -rln "page-session\|check-bundle\|quote-check\|research pass" CLAUDE.md docs
.claude/skills/diagram/research/CLAUDE.md .claude/agents scripts specs/250-*`). Every hit that states a research
procedure is below; the rest state none of their own - the guards and scripts that enforce these (their messages name
the same commands), 250's history and measurement files (its request, spec, tasks, research and review, settled by
its plan), the review ledger, the generated list of make targets, and `escalation-check` asking whether a pass ran.

| file | what it sets |
|---|---|
| `CLAUDE.md` "Research" | the six rules; checks read BUNDLES (`make check-bundle`), replies compact; a page worked in two fresh sessions from briefs (`make page-session`); `make notes`, `make canon` |
| `.claude/skills/diagram/research/CLAUDE.md` | where a question, its notes and a source live (feature 258); editing and `make record`/`citations`/`glossary`; checking on bundles (feature 250), `apply-edits` in one turn; the 20,000-byte question cap; the reader; four labels; every reference a link; quote what you cite; citation / absence / grounds; written for the reader; citations pages and the two write-ups; `source-applicability` before a source's numbers are used |
| `docs/research-doctrine.md` | the GM's rulings: read what you cite, quote it, translate a foreign passage and mark it, the download list's format, research before a ruling, a guess last, two forms a knob |
| `docs/research-record-rules.md` | the why of each rule, above all the size cap and how to split (D14) |
| `scripts/page-session.sh`, `scripts/_page_session_runner.py` | fresh headless sessions from briefs, one after another, detached; `then:` steps queue briefs; the sessions commit and do not push; do not edit the clone while they run |
| `specs/250-close-the-record-checks/briefs/*` and `measure/brief.py` | the brief shape this feature's `briefs/gen.py` follows: the write session (canon once, `source-pages`, ONE `source-reader`, read every file in one message, write, test, the cap, a handoff) and the check sessions (bundles, `apply-edits`, one re-check, a report) |
| `specs/250-close-the-record-checks/plan.md` D6-D20 | a check reads a BUNDLE outside the repository (D6); a page in fresh sessions from briefs, write then check groups packed by load (D7, D17); compact reports and `apply-edits` in one turn (D15); canon through `make canon` (D16); a long source read in PARTS, and a registered source reaches `source-reader` as `make check-bundle KEY=<key> WHOLE=1` - the plain `KEY=` excerpt is for `source-applicability` only (D19). The briefs said the plain form until this reading; corrected |
| `docs/efficiency-tooling.md` | `make source-pages` runs BEFORE `source-reader`, which greps the saved pages; the batching line (send the reads you know you need in one message) |
| `docs/spec-kit-and-reviews.md` | a physical task carries the five research boxes, ticked before the task (`tasks.md` T01-T09, T16, T17) |
| `.claude/agents/{source-reader,quote-check,record-format,source-applicability,entry-drift}.md` | the check contracts the sessions dispatch; each reads only its bundle's MANIFEST (`check-bundle-hooks.sh`), and each says how a long page reaches it |

What changed against what this session remembered from before 250 landed: the checks read bundles outside the
repository; the research runs in page sessions, not in the orchestrating session; canon is read only through
`make canon`; a question is capped at 20,000 bytes; report edits are applied by `make apply-edits`.

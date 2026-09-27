# The research procedure, reloaded from main (FR-009; the GM, 2026-09-27: "reload whatever files talk about how to do research")

Read in this clone after `sync-in` at main `51515eb6` (2026-09-27), which carries feature 250's landing, and found by
search rather than memory (`grep -rln "page-session\|check-bundle\|quote-check\|research pass" CLAUDE.md docs
.claude/skills/diagram/research/CLAUDE.md scripts specs/250-*`):

| file | what it sets |
|---|---|
| `CLAUDE.md` "Research" | the six rules; checks read BUNDLES (`make check-bundle`), replies compact; a page worked in two fresh sessions from briefs (`make page-session`); `make notes`, `make canon` |
| `.claude/skills/diagram/research/CLAUDE.md` | where a question, its notes and a source live (feature 258); editing and `make record`/`citations`/`glossary`; checking on bundles (feature 250), `apply-edits` in one turn; the 20,000-byte question cap; the reader; four labels; every reference a link; quote what you cite; citation / absence / grounds; written for the reader; citations pages and the two write-ups; `source-applicability` before a source's numbers are used |
| `docs/research-doctrine.md` | the GM's rulings: read what you cite, quote it, translate a foreign passage and mark it, the download list's format, research before a ruling, a guess last, two forms a knob |
| `docs/research-record-rules.md` | the why of each rule, above all the size cap and how to split (D14) |
| `scripts/page-session.sh`, `scripts/_page_session_runner.py` | fresh headless sessions from briefs, one after another, detached; `then:` steps queue briefs; the sessions commit and do not push; do not edit the clone while they run |
| `specs/250-close-the-record-checks/briefs/*` and `measure/brief.py` | the brief shape this feature's `briefs/gen.py` follows: the write session (canon once, `source-pages`, ONE `source-reader`, read every file in one message, write, test, the cap, a handoff) and the check sessions (bundles, `apply-edits`, one re-check, a report) |
| `.claude/agents/{source-reader,quote-check,record-format,source-applicability,entry-drift}.md` | the check contracts the sessions dispatch; each reads only its bundle's MANIFEST (`check-bundle-hooks.sh`) |

What changed against what this session remembered from before 250 landed: the checks read bundles outside the
repository; the research runs in page sessions, not in the orchestrating session; canon is read only through
`make canon`; a question is capped at 20,000 bytes; report edits are applied by `make apply-edits`.

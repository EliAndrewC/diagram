# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0113, 0106), session 1: write (cleanup 3)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message. Touch no question but the ones your items name.

**Claims.** The orchestrator claimed this bundle's questions, 0106 among them, for this clone (feature 449); nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited. Look in the archive before the web (`make archive-find`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page,
its archived copy or the PDF's text (`pdftotext`; `make source-pages` does not parse a PDF - record its outcome with
`make source-outcome`), never from a pass's report. Each new source takes its registry key (`make reserve KIND=registry
KEY=<k> TAGS="..."`, at most ten new keys this session; a source the record already cites keeps its key). A defect is a
wrong outcome: restate rather than invent.
**Size**: the findings pages are 17,633 bytes of prose (0113) and 4,479 (0106) - the cap is 20,000.

## Your items

The last checks (2026-11-23) reported these. Fix each; for one you find is not a wrong outcome once you have read it, leave
it and say why in one line.

- **I1 `0106`** (`0106-the-chief-retainers-house-karo-yashiki.html`, its opening paragraph): "An office of the shogunate's
  intendants was run differently: its staff lived inside the compound's walls, in small houses and long-houses", cited to
  `jinya-kotobank`, goes past what that source and the record say (modal-research 2026-11-23 on the barracks and
  retainers' quarters pop-ups): the question on where an office's staff lived (research/questions/0331-where-an-offices-staff-lived.html) cites the same source only for
  the junior officials' quarters being among the office's parts, says "No page we read counts who lived inside one, or
  says whether all its staff did", and gives Omori's mid-ranking official living in a house of his own in the town. Narrow
  0106's sentence to what `jinya-kotobank` says, read on its archived copy, and point to 0331 for the rest (a link, not a
  restatement).
- **I2 `0113`**: the note `mapple-takayama-jinya-2` (both notes files) joins two passages with " and, of the goyakusho,"
  where quote-check (OUTSIDE THE CHANGE, JOINED-WRONG) asks for the record's join mark: read the source and join them as
  the record's rules want, or, if the text is one continuous passage, say so in the handoff with the line that shows it.
- **I3 two registry entries** (`research/sources/010-works-cited/`):
  - `9731-mapple-takayama-jinya.html`: its limits say "reconstruction finished in 1996 from an 1830 plan" and "1777
    gundai's office", which source-reader did not find on the mapple page: find them on that page (cite the line) or
    restate the limits to what the page carries.
  - `0660-shimane-toshuko-lecture.html`: "on every kind of river from torrent to gentle" drops the lecture's 原則 (as the
    rule) on gentle rivers; source-reader's wording is "on torrent and steep rivers, and as the rule on gentle ones" - read
    the lecture's line and restate it.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (neither listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371i-handoff.md`: `- SECTION=0106 0113`, one line per item
   `I1|I2|I3 <DONE|NARROWED|LEFT> - <what changed, or why left>`, every file you changed under `## Files`, and anything
   left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph
   saying what you wrote.

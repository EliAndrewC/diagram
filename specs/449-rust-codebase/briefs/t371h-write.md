# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0009, 0103, 0107), session 1: write (cleanup 2)

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

**Claims.** The orchestrator claimed this bundle's questions for this clone (feature 449); nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited. Look in the archive before the web (`make archive-find`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page,
its archived copy or the PDF's text (`pdftotext`; `make source-pages` does not parse a PDF - record its outcome with
`make source-outcome`), never from a pass's report. Each new source takes its registry key (`make reserve KIND=registry
KEY=<k> TAGS="..."`, at most ten new keys this session; a source the record already cites keeps its key). A defect is a
wrong outcome: restate rather than invent.
**Size**: the findings pages are 19,793 bytes of prose (0009), 13,061 (0103) and 14,195 (0107) - the cap is 20,000; 0009
must stay under it (a footnote mark is about 55 bytes: take bytes back from a repeated phrase if it would pass 19,950,
never a finding, footnote, figure or label).

## Your items

The last check session (2026-11-23) reported these OUTSIDE THE CHANGE on this bundle's pages. Fix each; for one you find
is not a wrong outcome once you have read it, leave it and say why in one line.

- **H1 `0009`** (`0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html`): the
  block "Was the drain also confined to well-watered places" cites `horikawa-2011-nakaboshi` for the prewar confinement,
  which only `horikawa-2011-nakaboshi-6` quotes (quote-check PARTIAL): cite `-6` on that clause.
- **H2 `0103`**: the note `kotobank-ishidoro` (both notes files) joins its two passages with " and " where the source's text
  is not continuous (quote-check JOINED-WRONG): mark the join as the record's rules want.
- **H3 `0107`** (`0107-kitchens-daidokoro.drawing.html` and its notes):
  - "Where the kamado stands is a knob between two forms." - "knob" is the engine's word: say it as the reader's sentence
    (our plans set the kamado in one of two places, chosen per map).
  - the absence `kitchen-walls-absence`'s comment calls the Kakunodate report "Unreadable" for an HTTP 429: a page that
    refuses us goes on the GM's download list (`make download-add`) and the comment says so, not "unreadable".
- **H4 registry `37320-mlit-kaga-ashigaru`** (`research/sources/010-works-cited/37320-mlit-kaga-ashigaru.html`): it says
  "one domain's lowest warrior rank", but the source never ranks the ashigaru: say "one domain's foot soldiers" (or the
  source's own words).

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (none of the three listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371h-handoff.md`: `- SECTION=0009 0103 0107`, one line per item
   `H1|H2|H3|H4 <DONE|NARROWED|LEFT> - <what changed, or why left>`, every file you changed under `## Files`, the bytes of
   the three findings pages after, and anything left open and why. Do NOT run the record checks - the next session does,
   fresh. Your last message is one paragraph saying what you wrote.

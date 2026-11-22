# Brief - feature 449 T284 (0048's byre-size silence against 0108's figure) and T283 (0028 over its size cap), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file or any
pop-up - the orchestrator does those. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
`make notes Q=<n> KEYS=<k,k>`, read by line range; send the lookups you know you need in one message.

First: `make research-claim Q="0048 0028" FEATURE=449` (release with `STATUS=done` at the end).

## Your items

- B1 `0048` (`research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.html`, its `.notes.html`):

  - **T284.6 - the smallholder's byre size.** 0048's findings bullet "How big was an ordinary smallholder's byre?" says
    "No page we read gives it", and the page's evidence comment lists "an ordinary smallholder's byre's size" as a silence.
    But 0108 (`research/questions/0108-stables-umaya.notes.html`, note `kotobank-umaya-3`; the same encyclopedia entry is
    0188's `umaya-kotobank-4`) quotes an encyclopedia: farm stables wide where winters are long (Tohoku) and narrow in
    Kinki, about 3 m square. 0188's drawing page (`...0188-...-umaya-toiyaba.drawing.html`, the bullet "The maps do not size
    a stall from an undated farmhouse stable of about 10 ft square") rules that figure names no period. Reconcile 0048
    with both: the bullet gives the encyclopedia's figure (cite the note on 0108 the record's way - a cross-page note, or a
    new note on 0048 quoting the same passage verbatim from the archived page, `make archive-find`), says it names no
    period, so how big an Edo-period smallholder's byre was stays unrecorded; the evidence comment's silence restated to
    match ("an Edo-period smallholder's byre's size"). Nothing else on the page changes.

- B2 `0028` (`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html`):

  - **T283.7 - the size cap.** `make question-sizes` (and `make quick`) report the page at 20,004 bytes of prose, over
    the 20,000 cap. Bring it under by cutting redundant words in its own prose (a repeated clause, a "that", a doubled
    gloss) - never a fact, a footnote or a quotation - or, if no such cut exists, split it as
    docs/research-record-rules.md 'A question has a size' says. Prefer the smallest honest cut.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. No history in the text; a session note is an
   HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes` (0028 must be
   under its cap).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t284-handoff.md`: `- SECTION=0048`, `- SECTION=0028`, one line
   per item `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and
   anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.

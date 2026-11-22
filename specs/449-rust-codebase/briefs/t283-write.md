# Brief - feature 449 T283 (0028's and 0229's quote-check findings), session 1: write

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

First: `make research-claim Q="0028 0229" FEATURE=449` (release with `STATUS=done` at the end).

## Your items (quote-check findings outside 449 T254's change, 2026-11-22; restate each to its source)

- B1 `0028` (`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html`, its `.notes.html`, its
  `.drawing.html` and `.drawing.notes.html`; the originals in the `.originals.html` files):

  - **T283.1 - `sugiura-1973-fuzoku-7`'s original** likely ends in the paper's full-width period (．), not the ideographic
    one (。): check the archived copy (`make archive-find KEY=sugiura-1973-fuzoku`) and make the original match the paper.
  - **T283.2 - the 'snowy district' heading** rests on Sabusawa's snow figures where the paper's own sentence (p. 146)
    should be quoted: find Sugiura 1973's own sentence on the snowy district on p. 146 of the archived copy and quote it
    for the heading (a new note key from `make reserve` if needed), or restate the heading to what the cited figures
    support.
  - **T283.3 - `matsumoto-dosojin-2`** reads 花見 as Hanami where the place is Kemi: fix the romanization in the
    translation (and any glossary or prose that repeats it).
  - **T283.4 - joined passages without '; '**: `ido-jawiki` (in BOTH notes files), `sugiura-1973-fuzoku-4` and
    `nakasendoway-dosojin` join two passages of their source without the record's '; ' separator (or an ellipsis where
    the record's rule asks for one - follow the record's CLAUDE.md). Separate them as the rule says, the quoted words
    unchanged.

- B2 `0229` (`research/questions/0229-village-temples-tera.html`, `.drawing.html`):

  - **T283.5 - the opening's "with a small house for its monk"** (line 7) generalizes `onga-choshi-jiin-4`'s one temple
    (quote-check PARTIAL): restate it to that one temple ("..., and one such temple kept a small house for its monk" or
    similar), so the sentence claims only what the note shows.
  - **T283.6 - the drawing item 'The village's shrine is its parish temple.'** (drawing page line 9) - the heading lacks
    its closing period inside the `<strong>` as the record's bullet form has it, or the period sits outside: make it the
    record's standard bullet-heading form.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. No history in the text; a session note is an
   HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t283-handoff.md`: `- SECTION=0028`, `- SECTION=0229`, one line
   per item `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and
   anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.

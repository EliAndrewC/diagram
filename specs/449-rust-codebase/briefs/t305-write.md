# Brief - feature 449 bundle T302 (the record's leftover findings), session 1: write (0220, 0028, 0217, 0229)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0220 0028 0217 0229" FEATURE=449` (release with `STATUS=done` at the end).

## Your items (four questions, three registry write-ups) - each restated to its source, nothing new researched

- **T305.1 - 0220** (`research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html`): the findings' bullet
  "How many arches did a village shrine have?" labels "and that one with none was rare" a GUESS, though that claim was cut from the
  page: drop the clause (and any label for it in the Evidence comment).
- **T305.4 - 0028** (`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html` and its notes): (a) note
  `sugiura-1973-fuzoku-4`'s ranking leaves out the p. 151 half of Table 5's B1 row (bath 0.39, storage and well sheds 0.32): add that
  half with its own quotation off the p. 151 scan, or narrow the ranking's words to the half quoted; (b) `sugiura-1973-fuzoku-5`
  lacks the record's `; ` join before "Table 5, all-houses row", and its passage #2 (the 4.38 / 4.57 a household averages) supports
  nothing: drop passage #2 with its original `sugiura-1973-fuzoku-5#2`, and add the `; `; (c) that all-houses row gives 11 figures
  for 12 columns - name the blank column in the gloss, read off the scan (the Table 2/5 cells are images: read them by eye; if the scan
  cannot be read, say so in a session comment and narrow the gloss). 0028 sits a few bytes under its 20,000-byte cap: keep it under.
- **T305.6 - 0217** (`research/questions/0217-*.html`; `ls research/questions/0217-*`): (a) its `jizo-bosatsu-jawiki` passage (the
  article's opening paragraph) is NOT-READABLE by the verbatim script: re-quote it verbatim from the archived page
  (`make archive-find KEY=jizo-bosatsu-jawiki`), or, if the passage cannot be found, replace it with an absence note per the record's
  rules; (b) the drawing notes' copy of `matsumoto-dosojin-2` has "(of Kemi, in Azusagawa)", which the page's own notes copy lacks -
  make the two copies agree with the source.
- **T305.7 - 0229** (`research/questions/0229-*.html`): `homemate-shichido-garan-5`'s host returns 503 (its archived copy reads
  VERBATIM): put the page on the download list with `make download-add` (see its `--help`/usage), keeping the citation, which the
  archive supports.

## Three registry write-ups (not questions; their rows in `research/sources/`, each restated to its page)

- (T305.2) registry `research/sources/*/4960-jawiki-yashikigami.html`: its "Used for" says "especially the NE 鬼門"; the page gives
  NW and NE together and calls the NE-as-demon-gate reading a later overlay. Restate to the page (e.g. "often the NW or NE").
- (T305.3) registry `research/sources/*/7370-nakasendoway-dosojin.html`: calls the horse-headed Kannon "the guardian of horses and
  travelers"; the page says only baggage horses. Restate to the page.
- (T305.5) registry `research/sources/*/9860-kotobank-umaya.html`: says the Kinki 3 m "comes from modern studies of surviving
  farmhouses"; the page says only that no date is given. Restate to the page.

Keep each change to the words its finding needs.

## The procedure (session 1: write)

1. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>` for every key you re-read.
2. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and labels by the record's rules; no history in
   the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
3. **Hand off.** Write `specs/449-rust-codebase/briefs/t305-handoff.md`: `- SECTION=0220`, `- SECTION=0028`, `- SECTION=0217`,
   `- SECTION=0229`, one line per item `<item> <DONE|NARROWED|LEFT> - <what the record now says>`, every file you changed under
   `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.

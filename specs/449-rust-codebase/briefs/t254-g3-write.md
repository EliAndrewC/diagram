# Brief - feature 449 task T266 (bundle T254), group G3 (city temples' kuri quotation), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your item needs, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push. Do not edit `docs/building-programs.md`, any
`Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up. Do not run `make claims-*`. Read narrowly.

First: `make research-claim Q="0227" FEATURE=449` (release with `STATUS=done` at the end).

## Your items

- G3.1 **0227's `kuri-jawiki` notes** (`research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.html`'s
  notes, fn-3, and its drawing notes, fn-2, with their `.originals.html`): the Japanese Wikipedia article 庫裏 was
  reworded since they were quoted. `make quote-verbatim Q=0227 NOTES=kuri-jawiki` reports 「寺院の僧侶の居住する場所、また寺内の時食を調える、つまり台所も兼ねる場合がある。」
  NOT-ON-PAGE and 「庫裏は大規模寺院では独立した建物であるが、一般寺院では寺の事務を扱う寺務所と兼用となっていることが多い。」
  DIFFERS (the page now has 「大規模な寺院では独立した建物であるが、一般の寺院では寺の事務を扱う寺務所と兼用されていることが多く、...」).
  The same restatement was just made on 0221's notes (`research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.notes.html`
  and `.originals.html`; read them first, and the live page through `make source-pages OUT=/tmp/l7r-check/t254-g3-pages
  URL=<the kuri-jawiki url> QUESTION=0227 SOUGHT="the kuri definition and the large-temple sentence"`). Restate each
  original to the page's current text, the English translation to match, and the sentence each supports if its meaning
  moved. Also check the registry entry `research/sources/010-works-cited/7630-kuri-jawiki.html` for a quotation of the
  old wording and restate it the same way. `make quote-verbatim Q=0227 NOTES=kuri-jawiki` must then show no DIFFERS or
  NOT-ON-PAGE but reference-marker-only ones. 0227 is over the 20,000-byte prose cap already (`make question-sizes`):
  do not let your edit grow it.

## The procedure

1. Archive first: `make archive-find KEY=kuri-jawiki`; the live page through `make source-pages` and its outcome
   through `make source-outcome`.
2. `Read` every file you will change in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`.
3. Hand off: write `specs/449-rust-codebase/briefs/t254-g3-handoff.md`: `- SECTION=0227`, `- KEY=kuri-jawiki` if its
   entry changed, `G3.1 <DONE|NARROWED|LEFT> - <what>`, every file under `## Files`, anything open. Do NOT run the record
   checks; the next session does. Your last message is one paragraph saying what you wrote.

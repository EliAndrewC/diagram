# Brief - feature 449 T260 (0091's servants' range against 0115), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file or any
pop-up - the orchestrator does those. Do not run `make claims-*`. Read narrowly.

First: `make research-claim Q="0091 0115" FEATURE=449`. If it is REFUSED (another session - the magistracy bundle,
449 T289-T300 - holds 0091 or 0115), write the handoff `LEFT - claimed by <holder>` and stop without editing.

## Your items

- B1 `0091` **T260.1 - one household's servants on two sides of the house.** 0091's findings
  (`research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html`, line 54, the bullet "Where in the
  grounds did a house keep its well, its family privy and its servants' rooms?") guesses "that the family privy and any
  servants' range stood in the shady rear, with the storehouses: a GUESS, which the Miwa house's servants' hut outside
  its back door fits." 0115 (`research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.html`
  and its drawing page, lines 5-10) records the menservants and the gatekeeper lodged in the range along a residence's
  street front, the nagayamon (`kotobank-nagayamon`, `matsue-bukeyashiki`), and the building plans draw them there;
  no plan draws a servants' range behind the house. Reconcile: restate 0091's guess so the shady rear holds the family
  privy and the storehouses, and the servants are where the record puts them - a large household's menservants in its
  street-front range (link 0115's findings page), the Miwa house's chugen hut outside its back door by the kitchen
  being one house's form (keep its footnote). If the record shows the two as two forms of one question, say so in the
  sentence and leave which a plan draws to 0115's drawing page (link it). Check 0091's drawing page (line 38) says the
  same thing after the edit; restate it the same way if it implies a rear servants' range. No code changes.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges in ONE message, then `Edit`. No history in the text; a session note is an HTML
   comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t260-handoff.md`: `- SECTION=0091`, `- SECTION=0115` (only if
   changed), one line `T260.1 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under
   `## Files`. Do NOT run the record checks. Your last message is one paragraph saying what you wrote.

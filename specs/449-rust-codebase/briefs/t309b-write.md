# Brief - feature 449 bundle T302 (the record's leftover findings), session 7: write (0123, the T309 follow-up)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0123" FEATURE=449` (release with `STATUS=done` at the end).

## Your items (one question)

- **T309 follow-up - 0123** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.drawing.html`,
  the bullet "On the manor's own map the granary stands in the office court, in a flanking column beside the office hall - a guess."):
  it says the county seat's map draws "a store about 50 by 27 ft against the east wall". The county example now draws its granary
  50 x 36 ft (feature 449 T309: the staff long-houses were shortened to stand below the residence, and the granary was deepened to
  keep the plan inside the jin'ya coverage band). 0098's drawing page, the bullet "How big is a county office's granary on our
  maps?", now guesses one storehouse of about 43 to 50 by 25 to 36 ft. Restate "about 50 by 27 ft" to "about 50 by 36 ft". Change
  only those words; keep the footnotes, the comment and every other block. A session note, if any, is an HTML comment.

## The procedure (session 7: write)


1. **Write.** `Read` the file, then `Edit`. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t309b-handoff.md`: `- SECTION=0123`, one line `T309b <DONE|NARROWED|LEFT> - <what
   the record now says>`, every file you changed under `## Files`. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.

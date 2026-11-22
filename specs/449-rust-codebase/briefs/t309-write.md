# Brief - feature 449 bundle T302 (the record's leftover findings), session 5: write (0098)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0098" FEATURE=449` (release with `STATUS=done` at the end).

## Your items (one question)

- **T309 - 0098** (`research/questions/0098-storehouses-for-the-tax-rice.drawing.html`, the bullet "How big is a county office's
  granary on our maps?"): it says one storehouse of about 43 to 50 by 25 to 27 ft, some 1,100 to 1,350 sq ft, a GUESS, "at about a
  tenth of the 11,222 sq ft of the Takayama intendancy's rice store". The county example's plan now draws its granary 50 x 36 ft
  (1,800 sq ft): its two staff long-houses were shortened to stand below the residence (0116's order), and the ground they gave back
  left the plan under the jin'ya coverage band's 30% (0116), so the granary - the one building 0116 lets be the largest - was
  deepened, inside the type's 30-60 by 14-36 ft band. Restate the bullet to what the maps draw: about 43 to 50 by 25 to 36 ft, some
  1,100 to 1,800 sq ft, still a GUESS, at about a tenth to a sixth of the Takayama rice store (1,800 / 11,222 is 16%; say the
  arithmetic is this project's). Keep the footnotes; change no other block. A session note, if any, is an HTML comment.

## The procedure (session 5: write)

1. **Write.** `Read` the file, then `Edit`. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t309-handoff.md`: `- SECTION=0098`, one line `T309 <DONE|NARROWED|LEFT> - <what
   the record now says>`, every file you changed under `## Files`. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.

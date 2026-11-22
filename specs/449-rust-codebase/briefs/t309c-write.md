# Brief - feature 449 bundle T302 (the record's leftover findings), session 9: write (0123, a T303 check finding)

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

- **T303 check follow-up - 0123** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html`,
  and the same words on its drawing page if they appear there): the sentence "At Hamamashike, a guard post of the Shonai domain in
  Ezo whose main buildings were finished in 1860" calls Hamamashike a "guard post". Both source-applicability verdicts on its sources
  (`hamamashike-jinya-site-bunka`, `ishikari-hamamashike-jinya-file`) found it an administrative seat with a garrison (a jin'ya).
  Restate "a guard post of the Shonai domain in Ezo" to say it was the Shonai domain's administrative seat in Ezo, with a garrison.
  Keep the footnotes and change no other block. Read the two registry write-ups first (`make notes Q=0123 KEYS=hamamashike-jinya-site-bunka`)
  so the words match what they say. A session note, if any, is an HTML comment.

## The procedure (session 9: write)



1. **Write.** `Read` the file, then `Edit`. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t309c-handoff.md`: `- SECTION=0123`, one line `T303c <DONE|NARROWED|LEFT> - <what
   the record now says>`, every file you changed under `## Files`. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.

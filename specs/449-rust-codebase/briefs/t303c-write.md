# Brief - feature 449 T303 (0093's drawing page: the store's seat withdrawn), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your item needs, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`.
Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you need in one message.

The orchestrator already claimed 0093 for this clone (`make research-claims Q=0093`); keep the claim for the check session.

## Your items

- `research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html`

**T303.4 - drop the store's outer-court seat.** The block "The store of arms is drawn in one of three places, one chosen
for each plan from its seed." and the `<!-- Evidence: ... -->` comment (line 4) say a store of its own is drawn in the outer
court, on the main gate's side of the court divider, a GUESS. That rule is withdrawn (feature 449 T303's plan review,
2026-11-22: no source places a separate store, and a seat rule would forbid a placement the round arbiter's three-way
ruling allows). Restate both to say instead that no page we read places a store of its own (Nirayama's and Hamamashike's
are unplaced; Jiexiu's account lists its armory inside the side gates but leaves open whether it stood there, and whether
it was a building or a room), so a plan draws its store where it has room - drop the outer-court sentence and the
Evidence comment's "a store of its own seated in the outer court on the main gate's side of the divider". Keep everything
else in the block as it stands. No new footnote; keep the block's voice; no history in the text.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t303c-handoff.md`: `- SECTION=0093`, one line
   `T303.4 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph saying
   what you wrote.

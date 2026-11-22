# Brief - feature 449 T303 (0093's drawing page: the armory's three sites), session 1: write

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

**T303.3 - the armory's sites, reconciled with the round arbiter's three-way roll.** The drawing page's block (line 13,
"Where the main gate is drawn as a gate range, the store of arms may be one of its rooms, a knob chosen for each plan.")
and its `<!-- Evidence: ... -->` comment (line 4, "the armory's seat in a room of the gate range or an end bay of the
office hall, a knob between attested seats") name two sites. The engine now rolls ONE choice from the map's seed among
the sites a plan offers (the round arbiter's ruling `ask:armory-store-ubame`, route (a), 2026-11-22; the audit check
`armory_site`, feature 449 T303): a room of the gate range (only where the main gate is drawn as a range, Kaibara's gun
store), an end bay of the office hall (Pingyao's armory), or a store of its own (a building, as the weapons store at
Nirayama was, 5.4 by 3.7 m; question 0123's page (the magistrate's manor in a town)
records it, with Hamamashike's store and Jiexiu's armory listed inside its side gates, building or room unsaid). A plan
with a one-bay gate rolls between the hall's bay and a store. A store of its own is seated in the outer court, on the
main gate's side of the divider - a GUESS (no page places Nirayama's or Hamamashike's store; Jiexiu's account lists its
armory inside the side gates, before the middle gate, but leaves open whether it stood there). Its size on a plan is a
range about Nirayama's (11-18 by 11-24 ft, 120-430 sq ft), a GUESS. Ubame's plan still takes the gate range (its west
room, about 13 by 12 ft) and no pool plan draws a store today.

Restate the block and its Evidence comment to say this: the three sites, which a plan is offered, the one roll, the
store's outer-court seat and its size as GUESSES, Ubame's roll as it stands. Cite 0123's findings by a link to the
question (no new footnote is needed unless you quote; if you quote, quote only what you re-read verbatim on the public
page, and the archive comes first: `make archive-find`). Keep the block's form (a bold one-sentence heading, then the
account) and the drawing page's casual voice; no history in the text (a session note is an HTML comment).

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t303b-handoff.md`: `- SECTION=0093`, one line
   `T303.3 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph saying
   what you wrote.

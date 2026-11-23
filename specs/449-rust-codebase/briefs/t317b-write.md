# Brief - feature 449 T318 and T327 (0220, 0088), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your item needs, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push, and never write or push the archive's real remote.
Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file or any
pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the
lookups you know you need in one message.

The orchestrator already claimed 0220 and 0088 for this clone; keep the claims for the check session.

## Your items

- B1 `0220`: T318, in `research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.notes.html`
- B2 `0088`: T327, in `research/questions/0088-highways-and-what-lines-them-kaido.drawing.html` and its `.drawing.notes.html`

**T318 - a stale session comment.** In 0220's drawing notes, the `hokora-jawiki` note (line 5) carries an HTML comment
saying "the ~90%+ mode, hokora vastly outnumbering shrines, three as a ceiling and the row's Edo-onward reach are on no
page read". The note `fushimi-inari-senbon-2` now quotes the row's Edo-onward reach (found by a quote-check,
2026-11-22). Restate the comment so it names only what is still on no page read (check each of the other three items
against the page's notes before keeping it), or drop it if nothing remains. A session comment only; no visible text
changes.

**T327 - what the road's bands stand for.** The building plans draw the road a compound stands on as two stacked strokes
of the road's width: a translucent tan, and over it a darker tan dashed along the road's length, so the road shows light
and dark bands across its width every 4 to 5 ft. No drawing page records what the banding stands for. A research pass
of 2026-11-22 found (its saved pages under `/tmp/l7r-pass/t327-*`; the ledger has every page's outcome):
- no source gives a level Japanese road, a post-town street or a jin'ya frontage any feature across its bed: roads were
  trodden earth, gravel on main roads (ja.wikipedia 砂利道), sand built up crowned under the 1648 standard
  (ja.wikipedia 五街道), and Hakone's stone paving stopped inside the post towns (Shizuoka prefecture's Hakone pages);
- period plans give a road a flat color or leave the paper bare - red on provincial and boundary-dispute maps
  (hist-geo.jp 209_001.pdf), yellow on Edo kiriezu - and the one period cross-line on a road found marks a steep slope
  (Yamaguchi tourism, the Hagi road map of 1742).
Add one block beside "The road at a compound's front gate is the road the compound stands on, at that road's width." (line
27 of 0088's drawing page) saying that the bands across the road are a map drawing convention - texture marking the
ground as road, standing for no real surface feature (no ruts, paving or steps), since the road itself is earth - and
that period plans drew a road in a flat color. Label it a map drawing convention in the block and in the page's
`<!-- Evidence: ... -->` comment. Support it with a footnote: cite the pages that say it, verbatim, if you can read
them (`make archive-find URL=<u>` first; new registry keys through `make reserve`, at most ten), or an absence note
saying only what the search found and when. No history in the text.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t317b-handoff.md`: `- SECTION=0220 0088`, one line per item
   `T318|T327 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph saying
   what you wrote.

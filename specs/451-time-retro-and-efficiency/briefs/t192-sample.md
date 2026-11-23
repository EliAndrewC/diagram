# Brief - feature 451 T192 (0090 0196 0036 0026), session 1: tag the items (labels are data)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 451's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for every
git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md` is in
your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish". Other builders
have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your files by name. Never run
`scripts/sync-with-main.sh`, never push, never push the archive by hand. Do not edit any `rust/` file, any `docs/` file, any `Research:`
claim, `dev/claims-index.json`, any `pool/` file or the `Makefile`. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short
context, read by line range. Touch only the four drawing pages below and the pop-ups (`l7r/diagram/interactive/assets/modals/`)
already changed in this clone for them (`git -C /diagram/.clones/diagram-backlog diff --stat -- l7r/ research/`).

**Why this work.** The GM (2026-11-23): *"Yes please tag the rest of the record before resuming our port"*. A finding of a drawing page
carries a TAG naming the item and its label once, so a relabel is one edit and what reads the label follows:

`<span class="item" data-item="<id>" data-label="<ATTESTED|GUESS|CONVENTION|DEVIATION>" data-guess="<the Guesses bullet>"></span>`

The tag is EMPTY and sits INSIDE its `<li>` block, at the end, just before `</li>` (never an attribute of the `<li>`). `data-item` is a
lowercase slug unique across the question's pages. A GUESS tag carries `data-guess`, the bullet a pop-up shows, in the form
`<what is guessed>: <why no page says>`, written as the pop-ups' Guesses bullets are (`&`, `<`, `"` escaped as `&amp;`, `&lt;`,
`&quot;`). The block's own words must already carry the label the tag names: GUESS as `GUESS`, a convention or deviation by that word,
an ATTESTED block with no `GUESS` in it. A pop-up's Guesses bullet may be a reference, `- {NNNN#<id>}` (a `[knob=value]` condition
kept before it), filled at build from the tag's `data-guess`.

**What is already done.** A script (`.git/t192/tag.py`) placed a tag where a pop-up's Guesses bullet matched a GUESS block of a page
the pop-up cites, with `data-guess` the bullet's text VERBATIM, and turned that bullet into a reference; it also tagged blocks stating
a convention in a fixed form. Its list, and the blocks it left, are `.git/t192/batch-0090.md`. A tag and a verbatim reference owe no
check (`make record-owed` names nothing today): keep it so.

## Your items

- **G100 Tag 0090** (`research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html`).
- **G106 Tag 0196** (`research/questions/0196-communal-wells-ido.drawing.html`).
- **G46 Tag 0036** (`research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html`).
- **G36 Tag 0026** (`research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html`).

## What to do on each

1. **Confirm each placed tag** (the list's first part). Read its block and the bullet: does the block state the guess the bullet names?
   If the tag sits in the wrong block, MOVE the tag (span) to the block that states it on the same question's pages; never change
   its `data-guess` text, its `data-item` or the pop-up's reference (a changed text owes the pop-up its checks). Where two tags in one
   block carry two pop-ups' wordings of the same guess, leave both. A tag whose bullet matches no block of the question: remove the tag
   and restore the pop-up's bullet exactly as `git -C /diagram/.clones/diagram-backlog diff` shows it was.
2. **Tag the blocks the script left** (the list's second part): a GUESS block gets a GUESS tag with an id and a `data-guess` written
   from the block's OWN words (no new claim, nothing the block does not say); a block holding two guesses gets two tags; a
   CONVENTION or DEVIATION block its tag; a block whose label word is only a mention (a GUESS another block makes, "no deviation")
   gets none - say which in the handoff. Then scan each page's other `<li>` blocks for a label the list missed.
3. **Change no visible word** of any page or pop-up. If a block's label is wrong or unclear, do not fix it: write it in the handoff.
4. **Check**: `make rust-test CRATE=rust/gate/crates/registry` (its real-tree test reads every tag and every reference: each failure
   names its fix) and `make record-owed` (it must name nothing; if it names a unit, undo what owed it unless it is a label fault you
   report). Both in one message, in the foreground.

**Handoff.** Write `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T192-sample-session.md`: the time you started and ended
(`date -Is`), each tag you confirmed, moved, removed or added (page, id, label), each block you left untagged and why, every file you
changed, and the two checks' last lines.

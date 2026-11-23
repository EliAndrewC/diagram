# Brief - feature 451 T184 (0332, 0333), session 4: two findings the checks session left open

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need. Work only in this clone,
`/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command). `scripts/container/page-session-rules.md`
is in your system prompt; the research record's `CLAUDE.md` loads when you touch `research/`.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; touch
only the files your items need and list them in the handoff. Never push, and never push the archive by hand. Do not edit
any `Research:` claim, `dev/claims-index.json`, `pool/`, `docs/`, `rust/` or any pop-up. Do not run `make claims-*`.
A citation quotes its passage verbatim from the page you read; read the archived copy first (`make archive-find`).

## Your items

- **F1 The registry entry `hrr-agagawa-dento`** (`research/sources/010-works-cited/10550-hrr-agagawa-dento.html`) says
  "Its weir passage is about DIVERSION weirs on large rivers built to work in flood". The source-reader of 2026-11-23
  found the page gives no river size: "large rivers" is our description. It also found that the page names the Hamura
  intake weir on the Tama River as built of ushi and waku (its line 67), so frame building was not limited to diversion
  weirs. Read the archived page and restate the entry's limits paragraph to what the page says, with no river size it
  does not state.
- **F2 The glossary term `true leaf`** (`l7r/diagram/interactive/assets/glossary/28530-true leaf.json`) was drafted from
  general botany. The record's rule is that a definition comes from the record's own text. Read the passages in
  `research/questions/0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.notes.html` and
  `research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.notes.html`
  that use the term (`grep -n "true lea"`), and restate `def` to what they support. Keep the file's name.

## What to do

1. Edit, then `make record CHECK=1`, `make record`, `make glossary`, `make record-owed`. Run any check it names for your
   two units as the rules file says (bundle, foreground dispatch, `make record-checked`); apply its findings.
2. Append to the handoff with `make append FILE=specs/451-time-retro-and-efficiency/briefs/t184-handoff.md LINE="..."`:
   `F1 DONE|LEFT - ...`, `F2 DONE|LEFT - ...`, `CHANGED <path>`, `CHECKED ...`, `OPEN ...`. Your last message is one line.

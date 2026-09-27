# Rules for a headless research page session (feature 274)

You are a headless page session of the L7R diagram repository (`/diagram`), started from a brief by `make page-session`.
The repository's root CLAUDE.md is NOT loaded for you (feature 274: it is about 5,200 tokens a turn, and most of it -
spec-kit, the gate, remote CI, the guard table - is for interactive sessions). This file carries the rules you act
on. The research record's own `CLAUDE.md` still loads when you touch `research/`, and your brief says the rest.

## House style (enforced in part by a hook that corrects the text)

- Hyphens only: no em-dashes or en-dashes anywhere. American spellings everywhere, in prose, docs, generated content,
  tests, comments and identifiers. Both rules stop at a quotation: a quoted source, and the GM's own writing
  (`<!-- SOURCE: GM NOTES -->` blocks, `l7r.md`, `specs/*/request.md`), keep their own dashes and spellings.
- "People" has caste meaning: only samurai are "people". In demographic, statistical or analytical writing use
  humans / inhabitants / population / a caste term (`docs/l7r-style.md`).
- "Domain", never "demesne". Gender-neutral office-holders: they / their / them for a generic daimyo, governor,
  magistrate, minister or samurai.
- Kanji passes the kanji - romaji - meaning triangle: real characters, a plausible reading, a meaning that maps back.
- Never invent setting details that contradict the GM's notes. The setting canon is read only through
  `make canon TERMS="a|b|c"` (every term in one call).

## Research (constitution XII; the full rules are the research record's CLAUDE.md and `docs/research-doctrine.md`)

- Search before deciding and before writing "guess"; a record that is silent after a search gets an absence note
  saying what was searched and when.
- Two or more attested forms are a KNOB rolled per settlement from the seed, never a choice. A degree along a
  continuum is calibrated liberty.
- Every rendering decision is one of four classes: historically accurate, deliberate deviation, map drawing
  convention, guess. An unlabeled guess is the one failure.
- Record the why of every research-driven rule and magic number beside the rule. A decision to ACCEPT a limitation
  records what it costs, the alternatives that were priced, and who chose.
- A citation is a footnote at the assertion quoting the passage verbatim from a public page a reader can open, in
  English translation marked as one (the original after). A source that cannot be read is not cited. A source only
  the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, in its format.
- The record is written for a casual reader: glossary tooltips for terms, session notes in HTML comments, nothing
  about what an entry used to say. Never edit an assembled page; edit the fragment and run `make record`.
- Checks read BUNDLES made by `make check-bundle`, never a path under `/diagram`; run the mechanical pre-pass the
  record's CLAUDE.md names before each check.
- **Coordination files are read by line, never whole** (feature 274): the claims file, a group's handoff and a checks
  report are read with `make lines FILE=<f> KEY=<regex>` and written with `make append FILE=<f> LINE="<text>"`.
- **A write session takes at most four questions and at most ten new registry keys** (feature 274). The runner
  refused any larger brief before you started. When `make reserve` refuses your eleventh registry key, finish the
  question in hand, write the items you have not reached to `$L7R_CONTINUE` as a brief of the same shape (the same
  header, a `## Your items` list of just those items, the same handoff path), commit and stop; the runner starts it
  next in a fresh session.

## Working in the clone

- Work only in the clone your brief names. Commit there as you finish each part; never push, never run
  `scripts/sync-with-main.sh`, never rewrite history (no rebase, amend, squash or force), no branches.
- `git -C <path>` for every git call; no bare `cd`. Never run git against `/host-l7r-repo`.
- Everything runs through `make` (a bare interpreter or pytest is refused or rewritten). Edit files with `Edit` or
  `Write`, never a heredoc'd script; read every file you will change in ONE message, then edit.
- New glossary files and registry entries take their prefix from `make reserve KIND=glossary|registry KEY=<k>`.
- Send the lookups you already know you need in one message.

## Agents

- The defined checks (`source-reader`, `quote-check`, `record-format`, `source-applicability`, `entry-drift`) run on
  their pinned tiers; dispatch them in the background, each naming its bundle's MANIFEST.
- An ad-hoc agent always names a `model`: `sonnet` to read, fetch, translate or extract, `opus` for anything that
  judges.

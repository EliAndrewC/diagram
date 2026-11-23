# Brief - feature 449 T342, T343, T344, T349 (0093, 0116, registries 5220 and 14050), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(including this bundle's own earlier, checked edits in 0093 and 0116: keep them); the orchestrating session commits
your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short
context, read by line range; send the lookups you know you need in one message.

**Claims.** The orchestrator claimed 0093 and 0116 for this clone (feature 449). Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources say rather than invent.
These are the same-subject follow-ups the bundle's earlier checks found outside their change.

## Your items

- **C1 `0093` findings page: the one-bay gate's width.** The findings bullet "How wide was a one-bay gate (yakuimon)?"
  and the paragraph above it say "about 6 to 9 ft" and give the widest registered example as "2.6 m (~9 ft)", while
  the drawing page (edited and checked today) gives "about 6 to 8.5 ft" for the same three examples; 2.6 m is 8.5 ft
  (quote-check 2026-11-22). Restate the findings page's figures to "about 6 to 8.5 ft" and "2.6 m (~8.5 ft)" wherever
  they appear (grep `6 to 9 ft` and `~9 ft` in 0093's files); change no quoted passage.
- **C2 `0116` drawing notes: the absence note `how-our-maps-size-a-compound-and-its-buildings-2`** (the footnote of the
  kura fire-gap bullet; quote-check 2026-11-22: CLAIM-FROM-UNREAD and unlinked names). Its visible sentence says what
  the Japanese Wikipedia articles on the earthen storehouse (土蔵), on jin'ya (陣屋) and on the town fire brigades (町火消)
  give, without quoting them and without links. Read the three articles (the archive first: `make archive-find
  URL=<the ja.wikipedia URL>`; then the live page). Restate the sentence to what you read: link each article at its
  first mention; where it says what an article gives (the storehouse's wall thickness, how it survived fires), either
  quote the passage (its own note, translated and marked) or narrow the sentence to what an absence note may say -
  that the article was searched and gives no spacing between buildings. Keep its "no publicly readable source" form if
  it stays an absence note.
- **C3 registry `5220` takayama-jinya-jawiki** (`research/sources/010-works-cited/5220-takayama-jinya-jawiki.html`;
  source-reader 2026-11-22). (a) "What it is" and "Used for" say the article records "the 1816 rebuild of the office
  block as one range"; the article's sentence (quoted in 0116's note `takayama-jinya-jawiki-6` and 0099's
  `takayama-jinya-jawiki-5`) says 部分 (parts): restate both to what it says, for instance "the 1816 rebuild of the
  office's parts - 玄関・吟味所・御役所・大広間". (b) "Used for" still lists "the numbered storehouse rows (一～四番蔵・
  九～十二番蔵・書物蔵)", and this bundle dropped that passage from `takayama-jinya-jawiki-6`. Grep every note keyed
  `takayama-jinya-jawiki*` in `research/questions/*.notes.html` for 番蔵 or 書物蔵: if none still quotes the storehouse
  rows, drop them from "Used for" (keep "What it is"'s description of the article if the article does list them); if
  one does, keep them.
- **C4 registry `14050` fuchu-joge-jinya** (`research/sources/010-works-cited/14050-fuchu-joge-jinya.html`, the same
  pamphlet PDF as registry 9971; the T344 write session). Its "Why it applies" says the branch office was "run by three
  officials sent from the intendant's seat"; the pamphlet says only that three officials 「来ていた」 ("had come"), and
  registry 9971 (edited today) now sources the post's tie to the Iwami Ōmori intendant's office to Fuchū city's page
  `fuchu-joge-daikansho-ato`. Restate it to what the pamphlet says ("staffed in 1867 by three officials who had come
  there", as 9971 words it), and grep 14050's other lines for "1717", "Ōmori" or "Omori" and treat them as 9971's
  were (sourced to `fuchu-joge-daikansho-ato` or cut).

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t342c-handoff.md`: `- SECTION=0093 0116` (and the registry keys
   5220, 14050), one line per item `C1|...|C4 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed
   under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.

# Brief - feature 449 bundle T278, T279 (Ochiba's granary on 0116's drawing page; the office hall's size on 0090's), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up - the
orchestrator does the claims. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
`make notes Q=<n> KEYS=<k,k>`, read by line range; send the lookups you know you need in one message.

First: `make research-claim Q="0090 0116" FEATURE=449` (release with `STATUS=done` at the end).

## Your items (both measured 2026-11-22 from the sheets' own rects at 3 px = 1 ft; no new source is needed)

- **T278.1 - 0116's drawing page** (`research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html`,
  line 24, "Ochiba's jail cell and barracks are one guard building."). Its sentence "It stands in the compound's
  southeast corner beside the granary, with a 16 ft loading apron beside it" reads as if the granary stood in the
  corner. On Ochiba's sheet (`pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg`) the granary stands at the
  head of the office court's east column, beside the office hall's east end (granary 820-970 x 490-568 px, the hall
  420-780 x 478-562, the divider at y 450), and the guard building is below it in the south-east corner (894-966 x
  616-716 px), the 16 ft apron (48 px) between them. Restate the sentence so it says that: the guard building in the
  south-east corner, below the granary at the head of the east column, the 16 ft loading apron between them. Keep the
  bullet's heading and label.
- **T279.1 - 0090's drawing page** (`research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html`,
  lines 25-26: "At that scale the office hall runs 113 ft long." and "A smaller or larger scale would not fit.").
  The 113 x 38 ft hall and 80 x 26 ft hearing court are the GENERATED county example's (`pool/magistracies/county-magistracy-example/`),
  whose hall is now 127 x 38 ft (113 ft before the armory bay added at its west end, feature 449 T265); the hand
  sheets' halls are 28 ft deep (Hayakawa 113 x 28, Ochiba 120 x 28, Ubame 110 x 28 ft). Restate line 25 so it names
  which plan: e.g. heading "At that scale an office hall runs about 110 to 127 ft long." and text "The generated county
  example's is 127 by 38 ft, its hearing court 80 by 26 ft; the hand-drawn sheets' halls are 28 ft deep (Hayakawa's
  113 by 28 ft). ..." keeping the cell and wall sentence and updating the HTML comment's measurement (the county
  example's office hall 127 x 38, 2026-11-22). Line 26's "the office hall 85 ft long instead of 113" is Hayakawa's
  hall (its sheet is the comment's 741 x 600 px): make that explicit ("Hayakawa's office hall 85 ft long instead of
  113"). Measured statements of our own maps carry no footnote; keep the HTML comments as the measurement record.

## The procedure (session 1: write)

1. **Write.** `Read` both line ranges in ONE message, then `Edit`. No history in the text; a session note is an HTML
   comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t278-handoff.md`: `- SECTION=0116`, `- SECTION=0090`, one line
   per item `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and
   anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.

# Brief - feature 449 T342, T343, T344, T349 (0113, registry 9971), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(including earlier, finished edits in 0113 and registry 9971: keep them; edit around them); the orchestrating session
commits your files by name. Touch only the files your items need, and list every file you changed in the handoff.
Never run `scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive
step does what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/`
file, any `docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a
short context, read by line range; send the lookups you know you need in one message.

**Claims.** The orchestrator claimed 0113 for this clone (feature 449). Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources say rather than invent.

## Your items

- **B1 (T344) registry `9971` fuchu-joge-pamphlet: two facts neither page of the pamphlet carries.**
  (`research/sources/010-works-cited/9971-fuchu-joge-pamphlet.html`; source-reader and source-applicability.) Its
  "What it is" says the post was "an outpost of the Iwami Ōmori intendant's office from 1717 to the end of the Edo
  period", and its "Why it applies" says "a branch office (出張陣屋) of the Ōmori intendant's office". Read the
  pamphlet (https://www.city.fuchu.hiroshima.jp/material/files/group/23/daikanpanfu2.pdf; `make archive-find
  URL=<that url>` names the archived copy; its labels are in the image, so read the rendered pages, not only the text
  layer). For each of "from 1717" and "Iwami Ōmori" / "Ōmori": if the pamphlet says it, keep it (and say in the READ
  comment where it does); if it does not, look for a readable public page that does (the archive first: `make
  archive-find TERMS="上下 陣屋 大森"`; then the web, e.g. Fuchū city's or Hiroshima prefecture's pages on the Jōge
  jin'ya) and, if found, add that source as the registry entry's own stated source for the fact (key it with `make
  reserve`, which archives it) - otherwise cut the fact, writing what the pamphlet does say (for instance "an outpost
  (出張陣屋) of an intendant's office" if that is all it gives). Check any question note that repeats the cut fact
  (`grep -rn "1717\|Ōmori\|Omori" research/questions/*fuchu* research/questions/0090* research/questions/0104*
  research/questions/0113*` and the notes citing `fuchu-joge-pamphlet`) and restate it the same way. Record the
  outcome with `make source-outcome`.
- **B2 (T344) `0113` drawing page: the 1842 South Town Magistracy plan.** The drawing page's clerks'-room bullet cites
  only the 1841 North plan (via `edo-ashigaru-bugyosho`, the archived edo.ashigaru.net/?eid=23); the 1842 South plan
  (http://edo.ashigaru.net/?eid=20, the image https://www.ashigaru.net/archives/edo/minami_te1302_m25x.jpg) is named
  only in comments, unarchived and unkeyed. The research pass that read it is `.git/l7r-handoffs/T337-pass-behind-the-dais.md`
  (34 lines, read it whole; its item 2): reading of the image, 白洲 -> veranda -> 裁許所 (入側 beside) -> 調之間 ->
  廊下 -> 用達詰所. The page is http-only: fetch it with `curl -sL http://edo.ashigaru.net/?eid=20` (WebFetch forces
  https). If it is readable, key it with `make reserve` (a registry entry, which archives the page), quote its own text
  verbatim for what the page says (translated, marked), and cite it beside the 1841 plan in the bullet's room-order
  sentence ("the plans of the North Town Magistracy of 1841 and the South of 1842 show ..."), saying "the plan shows"
  for the room order read off the image, as the bullet does for the 1841 plan; update the note's session comment and
  the Evidence comment that say "not archived". If the page or its image cannot be read, leave the bullet as it is and
  report it LEFT with what failed.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t342b-handoff.md`: `- SECTION=0113` (and the registry key 9971),
   one line per item `B1|B2 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`,
   and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.

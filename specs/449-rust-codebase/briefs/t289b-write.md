# Brief - feature 449 bundle T289 (armories, the main gate, the record's leftovers), session 3: research and write (0090, 0109, 0118)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0090 0109 0118" FEATURE=449` (release with `STATUS=done` at the end).

## What a research pass found (2026-11-22)

- **The ground by a samurai house's kitchen.** archiscape blog (Kurasawa Satoru, 2020) summarizing Shimamura Noboru, 『金沢の家並』
  (archived 98/98c50e19571b, key `archiscape-kanazawa-sedo`, https://kurarc.exblog.jp/30027032, uncited): 「武家住宅の庭は大きく4つのタイプに
  分類される　１：玄関前の前庭　２：台所前の勝手（小背戸）　３：座敷に面する観賞用の庭園　４：宅地背後に広がる背戸（果樹、野菜の栽培用）」
  ("The gardens of samurai houses fall broadly into four types: 1, the front court before the entrance; 2, the katte (ko-sedo, little
  back yard) before the kitchen; 3, the viewing garden facing the reception room; 4, the sedo spreading behind the lot (for fruit trees
  and vegetables)", translated). Kanazawa, Edo practice, at second hand with no pages given; says nothing of what the katte held.

## Your items (three questions)

- **T295.6 - 0090** (`research/questions/0090-magistrates-compounds-jinya-and-yamen.html` and `.drawing.html`): the engine word "the
  divider" in the page's prose - say it in the reader's words (the wall between the outer and inner courts); and the
  `fuchu-joge-pamphlet-6` footnote's "Meiji 2 drawing" lacks its year - give it as Meiji 2 (1869).
- **0109's drawing page** (`research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.drawing.html`): the block "On the three
  hand-drawn magistracy plans, the bed stands south" is stale for Hayakawa, whose plan since its 2026-10-26 redraw seats the bed WEST of
  the house (`pool/magistracies/hayakawa-magistracy/hayakawa-magistracy.notes.md`, the 2026-10-26 entry: "the vegetable garden west of
  the house (the seat knob's 'west of the residence')"; read it, do not edit it). Restate the block to what the three plans draw (Ochiba
  and Ubame south, in the inner court's garden, their west and rear shaded; Hayakawa west of its house).
- **0118** (`research/questions/0118-samurai-house-lots-and-houses-by-rank-bukeyashiki.html`; find its drawing page with `ls`): it says no
  page names a separate kitchen yard. Add, briefly, that at Kanazawa a samurai house's grounds were classed in four kinds, among them the
  katte or ko-sedo before the kitchen, apart from the sedo behind the lot (the source above, secondhand, its limits stated), and what it
  leaves unsaid (what the katte held, its size). Footnote to the key, original then a marked translation.

Keep each addition to a sentence or two.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="divider|Joge|vegetable|kitchen yard|back yard"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>`. Register each new source with its write-ups
   (`make reserve` for keys).
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and labels by the record's rules; no history in
   the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t289b-handoff.md`: `- SECTION=0090`, `- SECTION=0109`, `- SECTION=0118`, one line per item `<item> <DONE|NARROWED|LEFT> - <what the record now says>`, the new keys and notes, every file
   you changed under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.

# Brief - feature 449 T303 (a seat's armory as a store of its own), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your items need, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file, any drawing page or any pop-up - the orchestrator does those.
Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by
line range; send the lookups you know you need in one message.

The orchestrator already claimed 0123 for this clone (`make research-claims Q=0123`); keep the claim for the check session.

## What is already recorded (do not redo)

0123's findings already carry Jiexiu (the bullet "Jiexiu kept its gunpowder and weapons in the great hall's end bays,
and later in an armory of its own.", notes `gujin-tushu-jicheng-juan338-zhwikisource-2` and `-3`). The research pass of
2026-11-22 adds one limit to it: the 1677 account lists the 武庫 inside the east side gate of the ceremonial gate, beside
the jail, across from the gatekeepers' rooms, and does not say whether it was a building or a room. If the bullet's
heading "an armory of its own" says more than that, restate it to what the passage says.

## The research pass behind the new items (2026-11-22; quote only what you re-read verbatim from the public page)

- Nirayama (the Egawa intendant's office, Izu) 武器庫: late Edo, 5.4 x 3.7 m, gabled, entered at the gable end under
  a pent roof, pantile; where it stood in the compound is SILENT. Cultural Heritage Online,
  https://bunka.nii.ac.jp/heritages/detail/122177 . Nirayama was a shogunal intendant's office (daikansho) from 1692,
  not a small lord's seat (the registry's `31710-touken-world-jinya` says so).
- Hamamashike (Ezo guard post, 1859) 武器蔵: named only, in the Ishikari city PDF the pass read; its powder store 火薬庫
  on the hill behind (designation text https://online.bunka.go.jp/db/heritages/detail/189992 ).
- How common a separate store was: SILENT (2 of 31 職方典 entries name a weapons store at all).
- Archive first (`make archive-inbox`, `make archive-find`); a page that cannot be archived or read is not cited, and
  the block says the record is silent.

## Your items (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html` and its `.notes.html`)

- **T303.1 - the Japanese stores.** The bullet "No page we read puts a seat's arms in its barracks, or says what doors
  an armory had." says the one Japanese gun store read of is Kaibara's, a room of the gate range. Restate it: Kaibara's
  is a room of the gate range; Nirayama's 武器庫 is a building of its own, 5.4 by 3.7 m, its place in the compound
  unsaid; Hamamashike's 武器蔵 is named, and its powder store stood on the hill behind. Footnote each (new registry keys
  with `make reserve KIND=registry KEY=<key>`), with its date of evidence and its limits (an intendant's office; a
  frontier guard post), so the source-applicability check can rule on them. The doors clause stays if still true
  (Nirayama's gable-end entry may now answer it in part: say so if the page you read states it).
- **T303.2 - Jiexiu's limit**, as above, only if the heading overstates.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. No history in the text; a session note is an
   HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t303-handoff.md`: `- SECTION=0123`, one line per item
   `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every new registry key, every file you changed under
   `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.

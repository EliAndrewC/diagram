# Brief - feature 449 T292 (a polder seat's belt takes the windward side its polder leaves dry), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/, research/ pages 0028 0048 0090 0091 0093 0097 0109 0116 0123); the
orchestrating session commits your files by name. Touch only the files your items need, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim,
`dev/claims-index.json`, any `pool/` file, any `docs/` file or any pop-up - the orchestrator does those. Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0072 0019" FEATURE=449` (release with `STATUS=done` at the end).

## What the engine now does (the orchestrator's change, for your words to match)

A polder's village backs onto its landward shore (0019's drawing page), not onto the wind. Its shelter belt still
stands to windward of its houses (0072: the wind decides the belt's side), but only on the windward side its polder
leaves dry: on Kuwabata (the polder to the west, the landward shore east, the northwest wind) the belt takes the
houses' north end, and none stands between the houses and the dike, which the village stays a few steps off. This is a
GUESS: the record is silent on a belt between the houses and a dike.

## The research pass behind it (2026-11-22; quote only what you re-read verbatim from the public page)

- Otsubo and Ono 2019, a field study of the groves of 11 waju (ring-dike polders) on the Nobi plain (98 groves; aerial
  photos 1949-2009 and a 2018 survey), J-STAGE PDF
  https://www.jstage.jst.go.jp/article/ceispapers/ceis33/0/ceis33_13/_pdf/-char/ja - the pass read these passages (re-fetch and confirm them verbatim; the
  pass fetched the PDF with curl and pdftotext, outside the source ledger - archive it the record's way first, `make
  archive-inbox`, `make archive-find`; if it cannot be archived or read, it is not cited, and the block says the record is
  silent and the side is a GUESS from 0072 alone):
  - 「当該地域は，冬に北西側の伊吹山地からの颪が吹き荒れるため，屋敷林の多くは北西側に設けられ」 ("most homestead groves are set
    on the northwest side", the winter wind off the Ibuki mountains)
  - 「4か所の屋敷林は輪中提の付近の列状集落で確認できる」 and 「列状集落全体を通して一体的な屋敷林の一部であることが確認できる」 (four groves in
    row villages near the ring dike, each part of one continuous grove along the whole row village)
  - 「列状の集落では『一面型』の屋敷林が形成される」 (in row villages a one-sided grove forms)
  - corner-type groves in 1961, 18 of 20 at 「集落の北~西方向の端部」 (the north-to-west edge of the cluster)
  - the evidence is modern photographs of inherited groves, not a premodern record: say so (date of evidence 1949-2018).
- What the pass found SILENT: whether such a belt stood between the houses and the dike, its depth there, or houses set
  back from a dike to give it room. NOT ATTESTED: a dike's own trees standing in for the village's grove (0027 already
  says the farmhouses keep their own groves besides).

## Your items

- B1 `0019` (`research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html`, its
  `.drawing.notes.html`; 13 KB, room enough):
  - **T292.1 - the polder village's belt.** Under "The rule the map follows, for where the polder and its village sit",
    after the block "A village is drawn hard against its own polder.", add one block: a polder's village keeps its
    shelter belt on the windward side its polder leaves dry - on the pool's polders, with the polder to the west and the
    northwest wind, the houses' north end - and none between the houses and the dike; labeled a GUESS (the record is
    silent on a belt between houses and a dike), resting on 0072's rule that the wind decides the belt's side and a belt
    stands on one or two windward sides (link 0072's drawing page the record's way), and on Otsubo and Ono's Nobi plain
    groves (north to west of the homestead, one continuous one-sided grove along a row village by the ring dike, which
    side unsaid) as a footnoted note with a new registry key (`make reserve KIND=registry KEY=<key>`).
- B2 `0072` (`research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html`; it stands at
  19,992 bytes of its 20,000 cap - TRIM FIRST):
  - **T292.2 - the northwest-wind block.** The block "Every map takes the northwest wind unless it declares a local one."
    ends "...and a settlement is laid out with its back to that wind, except where its map declares that the ground slopes
    down toward the wind." It names only the declared fall as an exception to the back to the wind; a polder's village
    backs onto its landward shore instead (0019's drawing page). Restate the sentence to name both exceptions, and say the
    belt still stands to windward on both - on a polder, on the side its fields leave dry (link 0019's drawing page). First
    cut redundant words in the page's own prose (a repeated clause, a doubled gloss - never a fact, a footnote or a
    quotation) so the page stays under its cap after the edit; `make question-sizes` must pass.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. No history in the text; a session note is an
   HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes` (0072 under its cap).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t292-handoff.md`: `- SECTION=0019`, `- SECTION=0072`, one line
   per item `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, and
   anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one
   paragraph saying what you wrote.

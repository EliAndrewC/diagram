# Brief - feature 449 bundle T282, T286, T284.5, T285.1 (0220, 0222, 0236), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file or any
pop-up (`l7r/diagram/interactive/assets/modals/`) - the orchestrator does those. Do not run `make claims-*`. Read
narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range; send the lookups you
know you need in one message.

First: `make research-claim Q="0220 0222 0236" FEATURE=449` (release with `STATUS=done` at the end).

## Your items

- **T282.1 - 0220's findings carry the arch-count canon.** The approach pop-up says "In Rokugan any shrine's approach
  may pass under one arch or a row of three or seven, numbers that carry power in the setting, seven most of all", and
  today that rests only on 0220's DRAWING page (`research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html`,
  the bullet "The counts of one, three and seven are a deliberate deviation", whose comment holds the GM's words of
  2026-07-21: counts are numerological - 1, 3 or 7 only, 7 even more potent in Rokugan than in the real world; and
  line 7's comment, the GM 2026-09-29 on arches at ordinary shrines). Add ONE sentence of the setting's rule to the
  FINDINGS page (`research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html`), where it
  reads naturally (the opening or the bullet on rows of arches), stating it as the setting's, e.g. "In Rokugan, the
  setting our maps are drawn for, a shrine's approach may pass under one arch or a row of three or seven, numbers that
  carry power there, seven most of all." - with an HTML comment quoting the GM's words verbatim and their date (copy
  them from the drawing page's comments; search `make canon TERMS="seven|numerolog|potent"` once and quote any
  l7r.md line that bears, with its heading). The model is the village-temples page's acolytes sentence (449 T262):
  a plain sentence and a comment `<!-- the GM's campaign notes, the canon (make canon, <date>; ...): l7r.md
  "<heading>": "<quote>" -->`. No footnote: canon is cited by
  the comment, as there.
- **T282.2 - 0222's findings carry the Fortune canon.** The sanctuary pop-up says "In Rokugan the deity a village
  shrine houses is a Fortune", resting only on drawing pages. Add one sentence to 0222's FINDINGS page
  (`research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.html`),
  where the sanctuary is described, e.g. "In Rokugan the kami a village shrine houses in its sanctuary is a Fortune,
  most often Inari, the Fortune of rice." - only what the canon supports. Leads: `make canon TERMS="Fortune of rice|
  Country monks serve|Seven Fortunes|Inari"` (l7r.md "Temple Organization": "Country monks serve in village shrines";
  l7r.md 7304 "The Fox Clan's economy": "Inari is the Fortune of rice and of foxes"); `docs/building-programs.md`
  knob 3 (read only: the default dedication Inari, the rice Fortune, "the ordinary rural dedication", GM 2026-09-20).
  Quote each in an HTML comment as above. Do not claim "most often Inari" unless a GM sentence says so; the GM's
  default-dedication ruling may be quoted as the project's choice (on the drawing page if it is not already there).
- **T286.1 - 0222's drawing page, the wealth-knob bullet's two bare sentences.** On
  `research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html`
  the wealth-knob bullet says "They are gifts a parish gave its shrine as it grew richer" and "The strength stones
  stand beside the approach" with no footnote or link. Find what each rests on (the findings page's "Most of what else
  stood in a precinct was given to it, piece by piece" may be the first's ground: link the findings page there, or
  footnote the note that page cites; the second: footnote the source that places strength stones, or, if none places
  them beside the approach, label the placement a GUESS in the sentence). quote-check found these OUTSIDE 449 T254's
  change; fix both.
- **T286.2 - glossary terms in `0222`'s notes.** The `nara-byakugoji-hondo-2` note's translated passage has "formal tile
  roof, single-piece S-curved tiles" (hongawarabuki 本瓦葺, sangawara 桟瓦) with no glossary term. Add the glossary
  tooltips the record's CLAUDE.md prescribes (`make glossary`; a new glossary file takes its prefix from
  `make reserve KIND=glossary KEY=<k>`; kanji passes the kanji - romaji - meaning triangle). Gloss both, in the
  translation's words, without changing the quoted passage.
- **T284.5 - `0222`'s drawing page records the shrine-altar emblem marks, a convention no drawing page records.** The shrine-altar pop-up's Depiction
  says "The plan draws each altar as a small mark standing for the kami it serves - a rice-straw figure, a fox's torii,
  a flame, a wave - not as the altar at its size". Record that as a MAP DRAWING CONVENTION on 0222's drawing page, in
  its compound-shrine section (the paragraph "A magistrate's compound keeps a shrine of its own ..." and the bullets
  after it, about line 33-37): one bullet or sentence, labeled a map drawing convention, saying why (no source shows what
  an altar inside a hall looked like or its size - the findings page says so - so the mark names its kami rather than
  drawing an altar). Session note in an HTML comment: the sheets that draw them (`pool/magistracies/*/*.svg`,
  `data-kind="shrine altar"`).
- **T285.1 - 0236's drawing page, which grounds count as "on a hill".** The bullet "Our maps never put a village's
  graves at a shrine on a hill." (`research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.drawing.html`
  line 16) says a village whose shrine stands on a hill always takes a ground apart. The building plan of a country
  shrine (Mode A) classes its hall's ground four ways (`docs/building-programs.md` knob 8, read only): at the foot of its
  slope; at the top of its slope, the approach climbing to it; on a rise or on flat paddy ground; midway on an even
  slope. Add one sentence to the bullet saying which count as a shrine on a hill on the building plans - a hall at the
  top of its slope or on a rise (not flat paddy ground, not the foot of a slope or midway on one) - labeled a GUESS
  (the record says "on a hill" and no source splits the grounds), so a plan on no map whose hall stands so draws its
  burial ground apart. Keep the bullet's heading.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. No history in the text; a session note is an
   HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t282-handoff.md`: `- SECTION=0220`, `- SECTION=0222`,
   `- SECTION=0236`, one line per item `<item> <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed
   under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your
   last message is one paragraph saying what you wrote.

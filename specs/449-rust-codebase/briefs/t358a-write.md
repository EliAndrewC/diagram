# Brief - feature 449 T358, T360, T361, T362, T369, T370 (0106, 0101, 0218, 0190), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*`.
Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you need in one
message. Do not touch 0082, 0091, 0093 or 0113 (the next brief's).

**Claims.** The orchestrator claimed 0082 0091 0093 0101 0106 0113 0190 0218 for this clone (feature 449);
`make research-claims Q="0101 0106 0190 0218"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources and the sheets say rather
than invent. Where the record is silent, the line says it is this project's GUESS or a map drawing convention, with an
absence note listing what was searched (and when). Look in the archive before the web (`make archive-find`,
`make research-search`); every page read goes on the ledger (`make source-pages`, `make source-outcome`).

## Your items

- **A1 (T360) `0106` drawing page: the county plan's long-house as drawn today.** Line 7's bullet says the long-house
  is "24 by 82 ft" with the karō's quarters "its north 14 ft"; line 3's Grounds comment says "24 x 82 ft" and "24 x 14
  ft". Measured 2026-11-23 (the orchestrator read `pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json`
  and its `.svg`; you may re-read them, read-only): the "senior retainers' quarters" is 22 ft wide by 60 ft long on the
  outer court's west wall (`w 22, h 60, wall W`; the SVG rect 66 by 180 px at 3 px = 1 ft), partitioned at 24 and 42 ft
  into three dwellings (`bays [24, 42]`), each with its own door on the court (three door marks on its east face); the
  karō's quarters is its north bay, 22 by 24 ft (room `x 0, y 0, w 22, h 24`, captioned "karo's quarters"). Restate the
  bullet and the Grounds comment to 22 by 60 ft and the north 24 ft (keep "The sizes are a GUESS"; the Grounds comment
  may name the file instead of `compound_example.py`, which no longer draws it). Then line 9's bullet "Every plan labels
  the karō's quarters with the gloss 'the house elder'": measured 2026-11-23 (grep of the five sheets' SVG text), the
  hand-drawn plans (Ochiba, Hayakawa, Ubame) print "(the house elder)" under "karo's house"; the program-drawn plans
  (the county example's "karo's / quarters", the Ochiba round-trip test plan's "karo's house") print no gloss. Restate
  it to the hand-drawn plans' gloss, a map drawing convention, and say the program-drawn plans caption the karō's
  quarters without it; the Evidence comment (line 4) to match.
- **A2 (T362) `0101`: the Kôka Shunjû in the note `tajima-2007-night-soil`.** The note's quoted passage (0101's notes
  file, line ~5) names "Kôka Shunjû" with no explanation. Give the work a glossary term (`make reserve KIND=glossary
  KEY=...`; read how a term is written in `research/editing-the-record.md` or an existing term file) or, if the term
  machinery cannot reach a quoted passage, a short gloss in the note's own words outside the quotation. Its title in
  Japanese (耕稼春秋), what it is, its author and its date come from a page you READ (archive first: `make archive-find
  TERMS="耕稼春秋|Kōka shunjū|Koka shunju"`; then, e.g., the Japanese Wikipedia article or a Kotobank entry), never from
  memory, cited as the record cites. Do not alter the quoted passage itself.
- **A3 (T369) `0218` drawing page: the tree beside the shrine.** Line 5 says every compound has its shrine "in a corner
  of its grounds beside a tree"; line 11's bullet "Why does the shrine stand in a corner, beside a tree?" says a
  household's god was kept in a corner of its lot "in a small shrine or at an old tree or a stone taken as the god's
  seat" (`kotobank-yashikigami`) and that our maps "give it the tree as well"; the Evidence comment (line 4) lists "the
  shrine in a corner of its ground and a tree beside it" as accurate. The source gives the god a shrine OR a tree or a
  stone as its seat; it does not give a shrine with a tree beside it. Before labeling, search once: `make research-search
  Q="Did a household or office shrine (yashikigami, a jin'ya's shrine) stand beside a tree?" Q_JA="屋敷神の祠の傍らに木"
  TERMS="屋敷神|祠 木|神木 屋敷;yashikigami tree" KEY=t369-shrine-tree`, and read what bears. If a readable page shows a
  household's or an office's shrine with a tree beside it, cite it and keep the pairing as that page gives it; otherwise
  restate: the corner follows the record; the tree beside the shrine is our maps' GUESS (the record giving the god's seat
  as a small shrine, or an old tree or a stone, not the two together), with an absence note naming the searches. Move
  the pairing in the Evidence comment to guess. Keep the bullet's other sentences.
- **A4 (T370) `0190` drawing page: Ubame's second board.** Lines 32-34: "One board stands apart from a settlement's own:
  the one at a magistrate's gate", and the bullet "Would a magistrate's office have had a notice board at its gate?"
  ends "a freestanding board ... at the office's own gate ... - a GUESS". Ubame's plan draws two boards at its gate,
  "notice board" and "bounty board" (`pool/magistracies/ubame-magistracy/ubame-magistracy.svg`, two `data-kind="notice
  board"` marks; read-only), the second for the GM's canon's bounty on the hermit Shoda (`make canon TERMS="Shoda|bounty"`;
  `/host-l7r-repo/setting/l7r.md` "Shoda the hermit"). Add, in that section, that where a seat has a bounty out, as
  Ubame's on the hermit Shoda, our maps draw a second freestanding board beside the gate's notice board for it - a board
  of its own that no page we read records, our maps' GUESS - citing the canon as the record cites the GM's canon
  elsewhere (find an existing `l7r-...` canon note key and its form), and the page's absence note (the existing
  `bench-board-absence`, extended to say so, or a new one; say what was searched). The Chinese county office's wanted
  notices were posted on the walls flanking its gate among its other notices (`gmw-tianxia-yamen`), not on a board of
  their own; keep that. Update the Evidence comment's guess list (and the Grounds comment, if it names the bench's
  board, with the bounty board).

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t358a-handoff.md`: `- SECTION=0106 0101 0218 0190`, one line per
   item `A1|...|A4 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, the
   searches you ran (KEY and what they found), and anything left open and why. Do NOT run the record checks - the next
   session does, fresh. Your last message is one paragraph saying what you wrote.

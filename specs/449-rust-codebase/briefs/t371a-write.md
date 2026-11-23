# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0104, 0123, 0090, 0009), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message. Do not touch 0113, 0099, 0097, 0096, 0103, 0107 or 0059 (the other briefs').

**Claims.** The orchestrator claimed 0009 0059 0090 0096 0097 0099 0103 0104 0107 0113 0123 for this clone (feature 449);
`make research-claims Q="0104 0123 0090 0009"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources and the sheets say rather
than invent. A figure measured on our own maps carries its date and method in the page's HTML comment, as the pages
already do. Where the record is silent, the line says it is this project's GUESS or a map drawing convention.

**What the plans draw** (measured 2026-11-23 by the orchestrator, method: each sheet's SVG rects by `data-kind`, the
first rect of a `<g data-kind=...>` group on a hand sheet, at the sheets' scale bar of 3 px to the foot; you may re-read
`pool/magistracies/<map>/<map>.svg` and `.compound.json` read-only to confirm):
- The genkan porch (`data-kind="genkan"`): the county example (`county-magistracy-example`, generated) a porch 36 x 27 px
  = 12 x 9 ft in `#DDB87A`, the office hall's own fill, its door block 18 x 4 px = 6 x about 1.3 ft; Ochiba's hand sheet
  (`ochiba-magistracy`) a porch 30 x 18 px = 10 x 6 ft in `#C9A57A`, darker than its hall's `#DDB87A`, its door block
  16 x 4 px = about 5.3 x 1.3 ft; Hayakawa, Ubame and the Ochiba round-trip test plan (`ochiba-roundtrip-test`) draw no
  genkan mark at all (check each plan's notes or compound.json for its `formal entrance form` before saying which form
  it takes).
- The office halls: the county example 355.5 x 114 px = 118.5 x 38 ft (shortened by 449 T336); Ochiba 336 x 84 px =
  112 x 28 ft; Hayakawa 340 x 84 px = about 113 x 28 ft; Ubame 330 x 84 px = 110 x 28 ft; the round-trip test 336 x 84
  px = 112 x 28 ft. The county's hearing court 240 x 78 px = 80 x 26 ft. The cells: the three hand sheets 36 x 30 px =
  12 x 10 ft; the county example's 10 x 12 ft (`w 10, h 12` in its compound.json, joined to the junior retainers'
  quarters since 449 T356); the round-trip test's 18 x 15 ft.
- The county seat's granary: 150 x 78 px = 50 x 26 ft (since 449 T364; it was 50 x 36).

## Your items

- **A1 (T371) `0104` drawing page: the porch as each plan draws it.** Line 10's bullet says "The porch is drawn in its
  hall's own fill, about 12 by 9 ft, the one shikidai found measured; the small dark block on its outer edge, 6 ft wide
  and about 1.3 ft deep, is the genkan's door". That is true of the county example only. Restate it to what each plan
  draws (above): the county example's porch 12 by 9 ft in the hall's fill (keep its link to the one shikidai found
  measured, as the page has it); Ochiba's hand sheet a smaller porch, about 10 by 6 ft, in a darker fill, its door block
  about 5 ft wide - that size and fill our GUESS / a map drawing convention as the page's own labels allow (say which);
  and the plans that draw no genkan. Keep the door-glyph convention sentence and its note. Update the Evidence comment
  (line 4) and, if it names the porch's size, the Grounds comment (line 3), with the measurement's date and method.
- **A2 (T373) `0123` drawing page: the county seat's granary.** Line 16 says the county seat's store is "about 50 by 36
  ft"; it is drawn 50 by 26 ft since 449 T364. Restate the size, and the measured-on-our-maps comment beside it if it
  carries the old figure, with the date and method.
- **A3 (T373) `0090` drawing page: the halls' sizes.** Line 25's bullet "At that scale an office hall runs about 110 to
  127 ft long" gives the county example's hall as 127 by 38 ft and Ochiba's as 120 by 28 ft; they are drawn 118.5 by 38
  and 112 by 28 (above). Restate the bullet's lead and body to the plans as drawn (all five halls, the court, and the
  cell sentence, which the county's 10 by 12 and the round-trip's 18 by 15 make untrue as "A cell is 12 by 10 ft" -
  restate it to what each draws, keeping the link to 0096's drawing page), and its HTML comment with the date and
  method. Grep the rest of 0090's files for `127` and `120 by 28` and restate any other line that states those sizes as
  drawn.
- **A4 (T385) `0009`: under the 20,000-byte cap.** `research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html`
  is 20,044 bytes of prose (measured 2026-11-23, `make question-sizes`; the cap counts the question file alone, a money
  mark counted as its words; notes are not counted). Bring it to 19,800 bytes or below by cutting words, not findings:
  tighten repeated phrasing, cut a sentence that restates another, move a long HTML comment's working notes into the
  drawing page's comment only if it is a drawing note. Do not drop a finding, a footnote, a figure, a label (GUESS,
  convention) or the why of a rule; if no cut of that kind reaches the target, split along a topic instead (a part its own
  question with its own heading, made with `make reserve KIND=question`, the joins pointing, not restating). Say in the
  handoff what you cut, and the bytes before and after.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (0009 must not be listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371a-handoff.md`: `- SECTION=0104 0123 0090 0009`, one line per
   item `A1|...|A4 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, the
   searches you ran (if any), and anything left open and why. Do NOT run the record checks - the next session does,
   fresh. Your last message is one paragraph saying what you wrote.

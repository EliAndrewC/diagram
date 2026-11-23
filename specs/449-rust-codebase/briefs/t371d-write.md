# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0103, 0107), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/` - the
orchestrator edits the garden-pond and kitchen pop-ups from your pages). Do not run `make claims-*`. Read narrowly: grep
with `-o` and a short context, read by line range; send the lookups you know you need in one message. Do not touch
0104, 0123, 0090, 0009, 0097, 0096, 0113, 0099 or 0059 (the other briefs').

**Claims.** The orchestrator claimed 0103 and 0107 (with the bundle's other questions) for this clone (feature 449);
`make research-claims Q="0103 0107"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). Look in the archive before the web (`make archive-find`, `make research-search`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page or
its archived copy, never from a pass's report. Each new source takes its registry key (`make reserve KIND=registry
KEY=<k> TAGS="..."`, at most ten new keys this session; a source the record already cites keeps its key). A defect is a
wrong outcome: restate rather than invent. Where the record is silent, the line says so plainly ("is not recorded"),
with an absence note listing what was searched and when. The date of the evidence decides what a finding attests: a
modern survey of an undated surviving garden or a reproduction is said to be one.

**The two passes these items record** (research-pass, 2026-11-23; full reports with each source's URL, archived copy,
verbatim passage and translation - read them first, by line):
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t376-pond-banks.md` (KEY t376-pond-banks) - ATTESTED ONLY
  FOR the great gardens and a few surviving samurai-house gardens: the classic pond garden's set-stone revetments (護岸石組)
  and pebble-beach shores (州浜), and its clay-puddled bed under gravel, thinning from the Heian period; from the
  mid-17th century fewer set stones, after about 1716 smaller ponds and smaller stones (a dictionary history, high-status
  gardens); at Nagoya Castle's Ninomaru garden (drawing of 1818-30) an excavated revetment of tataki with feature stones,
  the bank's own date unfixed; at Obata, a jin'ya town, the surviving viewing ponds ringed by large stones or planting and
  the utility ponds walled by dry-laid stone, and at Matsushiro small-stone walling along the channels (modern surveys of
  undated survivals). No source dates the bank of a jin'ya's, an intendant's office's or a small samurai house's pond: what
  a small residence's or office's pond bank was is not recorded.
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t376-kitchen-fabric.md` (KEY t376-kitchen-fabric) - WALLS
  SILENT for a samurai or office kitchen (only general late Edo to Meiji walls at Boso-no-mura and a farmhouse's clay walls);
  ROOF ATTESTED: the kitchen a room of the main house or a wing of it under its roof (the Yokota house at Matsushiro, 1794,
  thatched; the Kuchiba house at Hagi, c.1800, a pantiled wing; Matsue, tiled; Kaga's foot soldiers' houses, shingled;
  Kaminoyama, thatched), the great mansions' kitchen a building of its own with a smoke louvre; smoke rising through a
  gapped ceiling or open rafters, no kemuridashi named for an ordinary samurai house; DOOR ATTESTED ONLY FOR the doorway
  and its place (a kitchen door at the rear onto the doma, Matsue, Kaminoyama, JAANUS), its leaf and its barring at night
  not recorded for a samurai house - only Morse's storm shutters with a wicket (houses in general, after 1868) and a
  farmhouse's big doma door shut at night and barred (Miyoshi).

## Your items

- **D1 (T376) `0103`: a pond's banks.** Put on 0103's findings (`0103-ornamental-gardens-ponds-and-stone-lanterns-teien.html`,
  beside "How large was a residence garden's pond?"), cited: what the great gardens' banks were, and the surviving
  samurai-house ponds at Obata (and Matsushiro's channels) as modern surveys of undated survivals; then that no page we read
  says what the bank of a small residence's or an office's pond was - an absence note naming the searches (KEY
  t376-pond-banks, 2026-11-23). Then the drawing page (`.drawing.html`): if it says how our plans draw a pond's edge, say
  whether that edge depicts a bank or is a map drawing convention for the water's outline; if it says nothing, a short
  bullet saying the drawn edge is the water's outline, the bank not drawn, the bank itself not recorded.
- **D2 (T376) `0107`: a kitchen's walls, roof and door.** Put on 0107's findings (`0107-kitchens-daidokoro.html`), cited: the
  kitchen under the house's own roof as a room or a wing of it at the named houses (thatched or tiled as the house was),
  the great mansions' separate kitchen with its smoke louvre, the smoke's way out through a gapped ceiling or the open
  rafters; the kitchen door's place at the rear onto the doma, as the page already has it, and that its leaf and whether it
  was barred at night are not recorded for a samurai house (Morse's storm shutters and the farmhouse's barred doma door said
  as the narrower cases they are, if you cite them); and that the walls are not recorded - an absence note naming the
  searches (KEY t376-kitchen-fabric, 2026-11-23). Then the drawing page, if it says what the kitchen's roof or walls are on
  our plans: match it. Keep each page under the cap.

## The procedure (session 1: write)

1. **Write.** Read the two reports and the line ranges you need, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371d-handoff.md`: `- SECTION=0103 0107`, one line per item
   `D1|D2 <DONE|NARROWED|LEFT> - <what the page now says, in a sentence a pop-up could follow>`, the note and absence-note
   ids a pop-up would rest on, every file you changed under `## Files`, the registry keys you reserved, the searches you
   ran, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.

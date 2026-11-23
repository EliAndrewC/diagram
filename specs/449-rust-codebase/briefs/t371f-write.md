# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0059, 0099, 0113), session 1: write (cleanup)

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
need in one message. Touch no question but the ones your items name.

**Claims.** The orchestrator claimed this bundle's questions for this clone (feature 449); nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited. Look in the archive before the web (`make archive-find`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page,
its archived copy or the PDF's text (`pdftotext`; `make source-pages` does not parse a PDF - record its outcome with
`make source-outcome`), never from a pass's report. Each new source takes its registry key (`make reserve KIND=registry
KEY=<k> TAGS="..."`, at most ten new keys this session; a source the record already cites keeps its key). A defect is a
wrong outcome: restate rather than invent.
**Size**: the findings pages are 19,778 bytes of prose (0059), 14,018 (0099) and 17,633 (0113) - the cap is 20,000; 0059
must end at 19,800 or below (take any bytes back from a repeated phrase, never a finding, footnote, figure or label).

## Your items

The last check session (2026-11-23) reported these OUTSIDE THE CHANGE on this bundle's pages. Fix each that makes a reader
told something untrue, shown a wrong tooltip, or sent to a citation that does not carry the claim; for one you find is
not a wrong outcome (the text is true and its citation carries it), leave it and say why in one line.

- **F1 `0059`** (`0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.*`):
  - the drawing page's "so its form is a knob" is engine wording shown to the reader: say it as the reader's sentence
    (each map draws one of the attested forms, chosen per map).
  - "seki" shows the glossary term Seki (the seki-juku, barrier-station sense), not the weir: give the weir sense its own
    term or variant from the record's words, so a weir's "seki" tooltips as a weir (`l7r/diagram/interactive/assets/glossary/`,
    then `make glossary`).
  - "the joints tied with wisteria vine" overstates `suido-ishizue-iseki-3`'s "Some joints": match the passage.
  - the absence note ending `-6` (the one the checker named "the -6 absence note") claims what the Chinese articles say:
    restate it to what was searched and not found, or cite the article that says it.
  - `maff-toshuko-history-5` and `-6`: their dates rest on the gloss, not the quoted passage: quote the passage that dates
    them, or move the date into the gloss's own words as the page's reading, with what it rests on.
  - `tabayashi-1987-5`: "pp. 80 - 261" - a page range takes a plain hyphen with no spaces (house style); check the range
    against the source.
  - `shimane-toshuko-lecture#1` stores 戦国末 where the PDF's text layer reads 戦国未: read the printed page (its image,
    `pdftoppm`) and store what is printed.
  - the ICID Diversion Weirs glossary page (HTTP 403 to us): `make download-add` it for the GM.
- **F2 `0099`** (`0099-the-hearing-court-shirasu.*`):
  - "At Edo, the shogun's capital, the town magistracy's court was a stepped hall..." has no footnote: cite the note that
    carries it, or say so in the handoff if none does.
  - the drawing page's ruling "every source ties it to the shogunate's courts in the capital": `koshikake-jawiki`'s
    bibliography lists an Osaka book (薮田貫『武士の町大坂』), and the North plan of 1841 has more than one 腰掛 (a second by
    the 与力番所, a 非人腰掛): narrow the ruling to "every source we read", name the Osaka book as an unread lead in its
    comment, and say the pairing of the court quarter's koshikake with the gate bay is the page's reading.
- **F3 `0113`** (`0113-the-office-hall-and-its-clerks-goyakusho.*`):
  - `mapple-takayama-jinya-2` and `-3` join two passages with "and": if the source's text is not continuous there, mark the
    gap ("...") as the record's rules want.
  - `edo-ashigaru-minami-plan-2` leaves out 祐筆所 and 中番部屋, which share the office room's court-side wall: if the
    page's sentence depends on what stood on that wall, quote them; otherwise leave it and say why.
  - `takayama-jinya-viewing-guide-4` would place the living room in the residence more plainly by quoting item 12 (where
    the 役宅 begins), and `edo-ashigaru-bugyosho-3` by quoting line 5 (用部屋を中心に...北には勝手向きの内玄関): take the
    plainer passages if the page's sentence rests on them.
- **F4 registry entries** (`research/sources/010-works-cited/`):
  - `37140-takayama-jinya-viewing-guide`: its Used for and What it is miss its new use on 0113 (the intendant's living
    room): add it.
  - `4280-banfang-zhwiki`: it calls a disambiguation page "a short encyclopedia article": say what the page is.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (none of the three listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371f-handoff.md`: `- SECTION=0059 0099 0113`, one line per item
   `F1|F2|F3|F4 <DONE|NARROWED|LEFT> - <what changed, or why left>`, every file you changed under `## Files`, the registry
   keys you reserved (if any), the bytes of the three findings pages after, and anything left open and why. Do NOT run the
   record checks - the next session does, fresh. Your last message is one paragraph saying what you wrote.

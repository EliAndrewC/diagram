# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0090, 0113), session 1: write (cleanup 4)

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your item needs, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message. Touch no question but the two your item names.

**Claims.** The orchestrator claimed this bundle's questions, 0090 and 0113 among them, for this clone (feature 449);
nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited. Look in the archive before the web (`make archive-find`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). Every passage you cite you READ yourself from the page,
its archived copy or the PDF's text, never from a check's report. A new source takes its registry key (`make reserve
KIND=registry KEY=<k> TAGS="..."`, at most ten new keys this session; a source the record already cites keeps its key).
A defect is a wrong outcome: restate rather than invent.

## Your items

- **J1 Takayama's official residence (`0090`, `0113`).** modal-research (2026-11-23, on the office-hall pop-up) found
  the record contradicting itself:
  - `research/questions/0090-magistrates-compounds-jinya-and-yamen.html`, the block "Did Japanese offices put the office
    in front and the residence behind?": "No page we read says so. At Takayama the intendant's official residence stood
    on the lot immediately to the west, beside the office rather than behind it." Its note, `takayama-jinya-city`,
    says only that the detention branch on the lot immediately to the west (西隣) stood where the 役宅 had been.
  - `research/questions/0113-the-office-hall-and-its-clerks-goyakusho.html`, the block "Where did the magistrate's office
    stand against the residence?", quotes `takayama-jinya-viewing-guide`: 「代官・郡代は、普段は御役所の奥にある役宅で執務していました。」
    ("ordinarily did their work in the residence at the back of the office", translated).
  - Both name the same word, 役宅. So 0090's "No page we read says so" is now contradicted by a page the record cites,
    and "beside the office rather than behind it" is a reading its own source does not state (the west lot is behind the
    office if the office faces east).

  Read both sources on their archived copies, and any page the record already cites on the Takayama Jin'ya's layout
  (`make archive-find` for takayama), for which way the office faces and where the 役宅 and the intendant's living rooms
  stood. Then restate 0090's block (its question line and its body) to what the sources carry, with the date of the
  evidence, and keep 0113's block consistent with it; if the two sources name different buildings (the rooms behind the
  office in the surviving main building, and a residence on the west lot), say so on both pages. Then
  `research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html`'s sentence "Drawing the residence behind
  the office in a Japanese compound is a deliberate simplification: at the intendant's office at Takayama the residence
  stood beside the office, on the lot to the west." follows the findings: if the record now places Takayama's official
  residence behind the office, the plans' order is not a deviation there - say what it is (attested at Takayama, one
  case) with its label. If no readable source settles the facing, say only what each source says and drop the reading
  neither states.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (neither listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371j-handoff.md`: `- SECTION=0090 0113`, one line
   `J1 <DONE|NARROWED|LEFT> - <what changed, or why left>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph
   saying what you wrote.

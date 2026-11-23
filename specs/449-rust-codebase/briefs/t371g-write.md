# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0097, 0096), session 1: write (cleanup)

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
**Size**: the findings pages are 19,271 bytes of prose (0097) and 14,403 (0096) - the cap is 20,000; 0097 must end at
19,800 or below (if a citation pushes it over, take bytes back from a repeated phrase, never a finding, footnote, figure or
label).

## Your items

The last check session (2026-11-23) filed these on this bundle's pages, outside its change (`specs/449-rust-codebase/found.jsonl`,
status open). Fix each that tells a reader something untrue or uncited; for one you find is not a wrong outcome, leave it
and say why in one line.

- **G1 `0097`** (`0097-staff-rowhouses-and-barracks-nagaya.*`):
  - the absence note `staff-rowhouses-and-barracks-nagaya` (quote-check: CLAIM-FROM-UNREAD) says "The pages count each
    dwelling of a row as a household", a claim about what named pages say that the note does not show was read: restate
    it to what was searched and found or not found, or cite the page that says it.
  - the findings sentence "Inside, a warriors' rowhouse was divided... servants below the foot soldiers shared large rooms"
    has no footnote: cite the note whose passage carries it (read it), or cut what no note carries.
  - the sentence "China shows the other form... a Beijing courtyard house lodged its servants" has no footnote: the same.
  - `make quote-verbatim Q=0097` lists four lines "not found verbatim in the archived text of 2026-10-02" on notes no
    check was owed: read each against its archived copy; correct a passage that differs from its source, or say in the
    handoff why it stands (a page edited since its archive, for instance).
- **G2 `0096`** (`0096-holding-cells-agariya-and-roya.*`) and its registry entry:
  - the note `boso-jinya-chiba-kiyo`'s gloss spells "Yuki domain" where the body block spells "Yūki domain": make them one.
  - the registry write-up of `boso-jinya-chiba-kiyo` (`research/sources/010-works-cited/37350-boso-jinya-chiba-kiyo.html`):
    add its limit for the Iwaito jin'ya (it stood only about 1853-1861), from the source's own words.

## The procedure (session 1: write)

1. **Write.** Read the lines you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (neither listed). If `make record` refuses only on another question's
   registry key having no archived copy (0107's `mlit-kaga-ashigaru`, another session's), say so in the handoff; do not
   fix it here.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371g-handoff.md`: `- SECTION=0097 0096`, one line per item
   `G1|G2 <DONE|NARROWED|LEFT> - <what changed, or why left>`, every file you changed under `## Files`, the registry keys
   you reserved (if any), the bytes of the two findings pages after, and anything left open and why. Do NOT run the record
   checks - the next session does, fresh. Your last message is one paragraph saying what you wrote.

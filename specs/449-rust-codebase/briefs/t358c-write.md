# Brief - feature 449 T358, T360, T361, T362, T369, T370 (0190, 0082, registry 4950, glossary), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone (including this bundle's own earlier, checked edits in 0082, 0091,
0093, 0101, 0106, 0113, 0190 and 0218: keep them); the orchestrating session commits your files by name. Touch only the
files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`, never
push, and never push the archive by hand. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/`
file, any `docs/` file, any `rust/` file or any pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a
short context, read by line range.

**Claims.** The orchestrator claimed 0190 (and the bundle's other pages) for this clone (feature 449). Nothing to
claim. Registry entries are not claimed.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); restate a line to what its source says rather than invent.

## Your items

Two findings the first brief's checks (2026-11-23) met OUTSIDE their change, on the same notes and sources:

- **C1 `0190`: the note `gmw-tianxia-yamen` joins its passages wrongly.** quote-check (JOINED-WRONG): its five quoted
  passages are joined with " and " where the record joins separate passages with "; " (or each in its own 「」, as the
  record's other multi-passage notes are written: read one, e.g. `grep -n -o 'data-note="[^"]*"' ` on a notes file
  with a multi-passage note, and match its form). Fix the join in every notes file the note appears in
  (`grep -l 'data-note="gmw-tianxia-yamen"' research/questions/0190-*`: the findings notes and the drawing notes), and
  its originals file if `make record` keeps one. Change nothing quoted.
- **C2 registry `4950-tokushima-yashikigami`** (`research/sources/010-works-cited/4950-tokushima-yashikigami.html`):
  source-reader found it drops the source's 位 ("about") in "20 m east", twice. Read the archived page (`make archive-find
  KEY=tokushima-yashikigami`) and restate both to "about 20 m east" (or the source's own wording).

Two more the second brief's checks (2026-11-23, `t358b-handoff.md` OPEN lines 85-86) met OUTSIDE their change:

- **C5 `0082` drawing page**: "The Edo hand cart's bed was 8 shaku long and 2 shaku 5 sun wide" - the note's kotobank
  quote (registry `9958-kotobank-daihachiguruma`) does not say Edo. Read the archived page; restate the line to the
  period the source gives, or to "the hand cart" with no period if it gives none. (`docs/buildings.md` repeats "the Edo
  hand cart's bed": a docs file, not yours - say in the handoff whether its wording still holds.)
- **C6 glossary, from `0082`**: `sun` (a tenth of a `shaku`) has no glossary term, and `beka-guruma` is not a variant
  of the term `25040-beka cart`. Add the variant (`research/assets/glossary-variants.txt` or the term file's own
  variants, as the record does it), and a `sun` term in the form of `5120-shaku.json` whose definition a public page
  you read states (kotobank's 寸, say), cited as the other unit terms are; if none reads, LEFT with why.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t358c-handoff.md`: `- SECTION=0190 0082 registry-4950 glossary`, one line per
   item `C1|C2|C5|C6 <DONE|NARROWED|LEFT> - <what it now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph.

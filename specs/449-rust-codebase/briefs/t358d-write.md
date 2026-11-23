# Brief - feature 449 T358, T360, T361, T362, T369, T370 (0093, registries 20550, 31150), session 1: write

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

Three findings the second brief's checks (2026-11-23, `t358b-handoff.md` OPEN lines 84 and 87) met OUTSIDE their change:

- **C3 registry `20550-morse-1886-homes`**: its `Used for:` lacks the use 0091's findings now make of it (a
  better-class Tokyo house's grounds, by 1885). Add that use, in the entry's own form.
- **C4 registry `31150-archiscape-kanazawa-sedo`**: its write-up says "Meiji and Taisho novels" and "the honey peach
  came to Japan only in 1875", neither on the blog page (source-reader). Read the archived page (`make archive-find
  KEY=archiscape-kanazawa-sedo`) and cut or restate each to what the page says.
- **C7 `0093`: the note `netease-pingyao-yamen`'s original ids run #5, #6, #3, #4 in the findings notes and #3, #4, #5,
  #6 in the drawing copy.** Read both notes files' pairs (and their originals files) by line, and make each English
  passage pair with the same original in both; change nothing quoted.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t358d-handoff.md`: `- SECTION=0093 registry-20550 registry-31150`, one line per
   item `C3|C4|C7 <DONE|NARROWED|LEFT> - <what it now says>`, every file you changed under `## Files`, and anything left
   open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph.

# Brief - feature 451 T184 (0009, 0059), session 3: the split pointers in T185's marked form

<!-- page-load: kind=check -->

You are a FRESH headless page session. This brief is the whole of what you need. Work only in this clone,
`/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command). `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; touch
only the two lines this brief names. Never push. Do not edit any `Research:` claim, `dev/claims-index.json`, `pool/`,
`docs/`, `rust/` or any pop-up. Do not run `make claims-*`.

## Your item

- **P1.** A split's pointer on its source page is one marked form (451 T185): `<a class="moved" href="NNNN-<slug>.html">`.
  With it, the pop-ups citing the source page follow the pointer and the split re-owes nothing. Two pointers left by
  T184's split are plain links. Change each `<a href="...">` to `<a class="moved" href="...">`, the href and the link
  text unchanged:
  - `research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html`:
    the sentence "What became of the paddy after the harvest - its straw ricks and its winter crops - is at <a
    href="0332-after-the-rice-harvest-the-straw-ricks-and-the-winter-crop.html">...".
  - `research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html`: the sentence
    "What a village weir was built of, and how thick it stood, is at <a
    href="0333-how-a-village-weir-was-built-stakes-cribs-frames-and-gabions.html">...".
  Leave the back-pointers on 0332 and 0333 as they are (they point from a new page, not from a split's source).

## What to do

1. Read the two lines (`grep -n 'href="033[23]-' <file>`), then `Edit` each.
2. `make record CHECK=1`, `make record`, `make question-sizes`, then `make record-owed`. The change is markup only (no
   visible word moved), so it should owe no check; if a check is named for these two blocks, run it as
   `scripts/container/page-session-rules.md` says (bundle, foreground dispatch, `make record-checked`).
3. Append to the handoff with `make append FILE=specs/451-time-retro-and-efficiency/briefs/t184-handoff.md LINE="..."`:
   `P1 DONE - <what changed>`, `CHANGED <path>` for each file, and any `CHECKED` or `OPEN` lines. Your last message is
   one line.

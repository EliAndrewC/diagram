# Brief - feature 449 T322 and T323 (0098, 0113, 0164, 0170, glossary term 10850), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your item needs, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push, and never write or push the archive's real remote.
Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file or any
pop-up. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the
lookups you know you need in one message.

The orchestrator already claimed 0098, 0113, 0164 and 0170 for this clone (`make research-claims Q="0098 0113 0164 0170"`);
keep the claims for the check session.

## Your items

- B1 `0098`: T322.1 and T323 (its notes files)
- B2 `0113`: T323 (its notes files)
- B3 `0164`: T322.2
- B4 `0170`: T322.2, with T322.3's two glossary files (`10850-hongawara.json`, `28280-archery strip.json` under
  `l7r/diagram/interactive/assets/glossary/`), which belong to no question

**T322.1 - tojo-gura.** 0098's notes (both notes files, note `kawashiri-komegura-kunishitei`) say "tojo-gura"
unexplained in a translated passage (record-format, 2026-11-22). Gloss it for a casual reader - a glossary term if the
word is a kind of storehouse the reader meets, or a bracketed gloss in the translation - from what the cited page says
(read it through `make archive-find KEY=kawashiri-komegura-kunishitei`); if the page does not say what it is, say only
that it is one of the named stores. Never guess a meaning.

**T322.2 - arrow lane.** 0164 and 0170 say "arrow lane(s)" (箭道) undefined, as 0123 did before; 0123 now uses the
archery strip glossary term (`28280-archery strip.json`, which already takes "jiandao"). Link these uses to that term -
by a variant ("arrow lane", "arrow lanes") or by using the term's word - and widen the term's definition if a
use falls outside "In a Chinese county office" (0170's is a city garrison's). Keep translated quotations' own words
where they are a quotation; the tooltip may sit on them.

**T322.3 - hongawara.** The hongawara term (`10850-hongawara.json`) lacks "full tile" and "full-tile" as variants
(record-format on 0093). Add them, if `research/assets/glossary-variants.txt` shows no other term owns them.

**T323 - two absence notes that may describe pages they did not read** (quote-check CLAIM-FROM-UNREAD, 2026-11-22).
0098's note `how-our-maps-draw-storehouses-for-the-tax-rice` (drawing.notes) says "the one dictionary entry that gives
Takayama's store in ken is behind a login" - a statement of what an unread page contains. 0113's absence note on the
office hall (`how-our-maps-draw-the-office-hall-and-its-clerks-goyakusho` in drawing.notes and
`the-office-hall-and-its-clerks-goyakusho` in notes) says what named pages contain (the Takayama pages' floor area, the
Kaibara page's rooms, the Fuchu pamphlet's tsubo).
For each page a note describes, look it up (`make source-pages URL=<u> QUESTION=<NNNN>`, `make sources-consulted
URL=<u>`, `make archive-find`). Where it was read and is readable, cite it with its passage, or keep the description
if a cited note of the same page already carries the passage (fuchu-joge-jinya-2 is cited in 0113). Where it was not
read, say only what the search found ("a dictionary entry turned up in search behind a login was not read"), never what
the page holds. If the login-walled dictionary entry can be identified, add it to the GM's list with
`make download-add FILE=<draft>` (an entry headed `### NEW. <the work>`; read the top of `research/to-download.md` by
line for the shape); otherwise leave it.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t317a-handoff.md`: `- SECTION=0098 0113 0164 0170`, one line per
   item `T322.1|T322.2|T322.3|T323 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under
   `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.

# Brief - feature 449 task T197, group G1 (households and the retirement house), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, Makefile, docs/ and Python deletions); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit `docs/building-programs.md`, any `Research:` claim, `dev/claims-index.json` or any `pool/` file -
the orchestrator does the claims. Read narrowly: grep with `-o` and a short context, `make notes Q=<NNNN> KEYS=<k,k>`,
read by line range; send the lookups you know you need in one message.

First: `make research-claim Q="0004 0030" FEATURE=449` (they are unclaimed; release with `STATUS=done` at the end).

## Your items

Each is a correction T187's checks found: a citation that does not support its sentence, or a term a reader cannot place.

- G1.1 **0004's main page, `0004`** (`research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html` and its `.notes.html`):
  (a) the paragraph opening "A household did not always keep to one roof" cites `kotobank-inkyo` for "In much of the
  country" and for "once they had handed the farm to their heir, moved out to a retirement house of their own on the
  family's house plot"; the note's quotation (retirement houses within the house plot, a separate entrance, their own New
  Year pine) says neither how widespread nor the handing-over nor the leaving of the heir's roof. Narrow the sentence to
  what the quotation says, or cite a passage that does say it (the same kotobank entry's other sections, already
  registered as `kotobank-inkyo-2`/`-3`/`-4`, are the first place to look: `-2` gives separate-residence retirement, the
  retired couple moving to a separate building; `-3` gives the regions).
  (b) `okada-bitchu-2004` (https://appsv.main.teikyo-u.ac.jp/tosho/aokada17.pdf): its notes did not match verbatim in the
  2026-10-02 archived text and its PDF is uncached (checked by hand). Archive first: `make archive-find KEY=okada-bitchu-2004`;
  then `make source-pages ... QUESTION=0004 SOUGHT="..."` if no readable copy; `make quote-verbatim Q=0004 NOTES=<the
  okada keys>`. Correct each quotation to the text as it reads. If the PDF cannot be read at all, the source is not
  citable: add it with `make download-add FILE=<draft>` and narrow or drop each sentence resting on it, honestly labeled.
  (c) "Echizen" has no glossary term, where Bitchu and Nihonmatsu do: add one, written from the record's own text
  (`make reserve KIND=glossary KEY=<term>`; grep `research/assets/glossary-variants.txt` first).
  (d) "divided-residence retirement" in the `kotobank-inkyo-3` quotation is unglossed: give the reader the term
  (a glossary term or variant, written from what `kotobank-inkyo-2`'s entry says of the forms of retirement).
- G1.2 **0004's drawing page** (`...0004-....drawing.html`): "the furniture inside a gate" is a phrase a reader cannot
  place - say plainly what is meant (read the sentence and its neighbors first).
- G1.3 **`l7r-median-domain`'s citation line** (`research/sources/010-works-cited/7180-l7r-median-domain.html`) and **`0030`'s
  two notes** (`research/questions/0030-the-headmans-house-and-the-rich-farmers-homestead-shoya-gono.notes.html` and
  `.drawing.notes.html`, note `l7r-median-domain`): the quoted sentence "Each county is divided into Village Districts,
  overseen by a peasant Village Headsman who lives in the main village." stands under the heading "### Hierarchies"
  (`/host-l7r-repo/setting/l7r.md` line 141; the sentence is line 151), not under "The Median Domain" (line 155). So the
  registry's citation line gains "Hierarchies" with its heading URL (https://github.com/EliAndrewC/l7r/blob/master/setting/l7r.md#hierarchies,
  GitHub's anchor rule), its "What it is" names the section, and both 0030 notes' parenthetical says `in "Hierarchies"`.
  Verify the line numbers with one grep before editing; never edit `/host-l7r-repo`.
- G1.4 **The retirement house's two pop-ups**: `l7r/diagram/interactive/assets/modals/hamlet/retirement-house.md` and
  `l7r/diagram/interactive/assets/modals/choice/family_form--retirement_house.md` say the retirement house's size is not
  recorded, where research 0028's drawing page (`research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html`)
  gives Kakimochi's eight retirement houses at 3 to 15 tsubo and one of 1820 at 7.7 by 4.6 m - a pop-up telling the
  reader wrong (modal-depiction, 2026-11-19). Rewrite each pop-up's size statement from that page (its pointer list
  naming the question it now rests on), by the modal guidelines in `dev/modals.md`. Do not change any drawn size.

## The procedure (session 1: research and write)

1. **Canon once** where an item is the setting's: `make canon TERMS="Hierarchies|Village Headsman|retirement"`.
2. **Archive before the web** (feature 309): `make archive-inbox`, then `make archive-find KEY=<k> | URL=<u> | TERMS="a|b"`
   for every source before any fetch. Every page read goes through `make source-pages OUT=/tmp/l7r-check/t197-g1-pages
   URL=<u> QUESTION=<NNNN> SOUGHT="<what>"`, and its outcome through `make source-outcome`.
3. **Read through `source-reader`** only where a NEW passage is to be cited: one dispatch, in the FOREGROUND, on a bundle
   (`make check-bundle ... NEW="<claim>"`), never a path under `/diagram`. Write only what it returns READ with a quote.
4. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes, glossary and the four labels by
   the record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make
   record`, `make glossary`, and `make question-sizes` (a question's prose stays under 20,000 bytes).
5. **Hand off.** Write `specs/449-rust-codebase/briefs/t197-g1-handoff.md`: one line per changed question as
   `- SECTION=<NNNN>`, one per changed registry key as `- KEY=<key>`, one per changed pop-up as `- MODAL=<kind>/<name>`,
   one line per item `G1.<n> <DONE|NARROWED|LEFT> - <what the record now says>`, every file you changed under
   `## Files`, and anything left open and why (a `make download-add` named as such). Do NOT run the record checks - the
   next session does, fresh. Your last message is one paragraph saying what you wrote.

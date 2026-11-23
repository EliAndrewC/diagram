# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0103, 0009, 0107), session 1: write (cleanup)

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
wrong outcome: restate rather than invent. The date of the evidence decides what a finding attests: an excavation of a
named garden attests that garden, said as one case, never as the rule for a small residence's or an office's pond.
**Size**: the findings pages are about 11,500 bytes of prose (0103), 19,770 (0009) and 13,870 (0107) - the cap is 20,000; 0009 must
end at 19,800 or below (the two fixes add a footnote and a few words; take any bytes back from a repeated phrase).

## Your items

- **E1 (T376) `0103`: two excavated banks the page lacks.** The pass
  `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t376-pond-banks.md` (research-pass 2026-11-23, KEY
  t376-pond-banks; read its entries 1 and 4 and its "Reading", lines 7-58 and 134-150) found two cases 0103 does not carry:
  - **Shunjuen**, the stroll garden of the Chimura family's lower residence (a hatamoto family) at Kukuri, Kani (Gifu), made
    1756-65 and enlarged c. 1804-28: its 2001-03 excavation found laid-stone pond edges - a near-vertical stone wall about
    60 cm high at the south pond, a neatly laid revetment on the Johari pond's shore with facing stones on the slope above,
    edging stones round the central pond, and a lined earthen bed in the south pond. Source: Kani City Board of Education,
    市名勝春秋園 遺跡保存のための発掘調査報告書 (2004),
    https://sitereports.nabunken.go.jp/files/attach/65/65477/40733_1_%E5%B8%82%E5%90%8D%E5%8B%9D%E6%98%A5%E7%A7%8B%E5%9C%92.pdf
    (OCR text layer; it spells the pond both 浄破璃池 and 浄披璃池).
  - **Nagoya Castle's Ninomaru garden** (the Owari domain's daimyo garden, matched to a drawing of 1818-30): the North pond's
    revetment of tataki (rammed earth and lime) with feature stones, a tataki floor; the tataki's date could not be fixed.
    Source: https://www.nagoyajo.city.nagoya.jp/plan_expert/uploads/b7316da1d745be0a2b7e08930b1a74b8_1.pdf
  Download each PDF into its own new, empty directory under `/tmp/t371e/`, read it with `pdftotext`, and quote from it.
  Put both on 0103's findings beside the bank lines the last session wrote (notes `kotobank-teien-banks`,
  `kotobank-teien-edo-banks`, `ohno-2014-obata-ponds`, `kaken-matsushiro-sensui`, absence `pond-bank-absence`), each said
  as the one garden it is - Shunjuen a hatamoto's lower-residence stroll garden of several ponds, Nagoya a daimyo garden -
  and keep the line that what the bank of a small residence's or an office's pond was is not recorded. Update the
  absence note `pond-bank-absence` (findings and drawing notes) so its searched list names these two excavations as read
  and its conclusion stays what it is; it also still says "A Japanese dictionary's history of the garden" where the page
  now says encyclopedia (the passages are Heibonsha and Nipponica entries hosted on Kotobank) - match the page. If a PDF
  cannot be read, do not cite it: say so in the handoff.
  Two more of 0103's, left OPEN by the last checks: the registry entry `ohno-2014-obata-ponds`
  (`research/sources/010-works-cited/37360-ohno-2014-obata-ponds.html`) speaks in its Used for and limits of the banks
  only, while 0103 also takes the 40-60 cm pond depth from it (a 2010s measurement of an undated survival) - say both;
  and the lantern kinds Kasuga, Enshu and Oribe have no glossary entry, so "Kasuga" shows the shrine-building term's
  tooltip - give the lantern its own term or variant from the record's own words (`l7r/diagram/interactive/assets/glossary/`,
  then `make glossary`), or, if the record says nothing a definition can rest on, say so in the handoff.
- **E2 (T385 follow-up) `0009`: two small fixes a check flagged outside the last change.**
  - The drawing notes' `obata-1977-taue-2` (`0009-...drawing.notes.html`, line 1) says "the mountain zone of Kichu and
    Kinan" without the gloss "central and southern Wakayama" its twin on `0009-...notes.html` (line 31) now carries; give
    it the same gloss (source-reader confirmed the source supports it).
  - The findings page's opening block (`0009-...html`, near "a Chinese farm manual of 544") cites only
    `qimin-yaoshu-juan2`, which does not give the date; add the note that does, `qimin-yaoshu-enwiki` (already on
    `0009-...notes.html`), as the date's footnote.
- **E3 (T376 follow-up) `0107`: three lines the last checks left OPEN, now untrue beside the notes cited since.**
  - The drawing notes' absence `kitchen-two-doors-absence` (`0107-kitchens-daidokoro.drawing.notes.html`, line 9) says no
    page places a kitchen's outside door on its doma, but `jaanus-shimodaidokoro-door` (now cited on the findings page)
    places it on the service kitchen's doma in the great mansions: narrow the absence to a small house's doma, and add
    that search to its searched list.
  - The findings' "Who came in by the kitchen door?" (`0107-kitchens-daidokoro.html`, line 37) opens "Only modern pages
    say", but `jaanus-shimodaidokoro-door` calls the mansion kitchen door the tradesmen's entry: restate it (the great
    mansions' service kitchen door from that note; the modern pages for a small house), and match the drawing page's
    "Our plans draw the kitchen door but do not say who came in by it" if it repeats the same claim.
  - The bullet "A samurai house's kitchen was a room of the main house or a wing of it, roofed as the house was." (line 25)
    counts the Kaga foot soldiers' (ashigaru) houses among its samurai houses, where the source calls them only foot
    soldiers: say them as foot soldiers' houses, in the heading or the body, so no reader takes them for samurai houses.
  - Optional, only if the PDF reads: the registry entry `mlit-kaga-ashigaru`
    (`research/sources/010-works-cited/37320-mlit-kaga-ashigaru.html`) links a .docx that `make quote-verbatim` cannot
    decode; the same text is a PDF at https://www.mlit.go.jp/tagengo-db/common/001559629.pdf - link the PDF if its text
    carries the quoted passages verbatim.

## The procedure (session 1: write)

1. **Write.** Read the report's line ranges and the page lines you need in ONE message, then `Edit`. Then
   `make record CHECK=1`, `make record`, `make glossary`, and `make question-sizes` (neither page listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371e-handoff.md`: `- SECTION=0103 0009 0107`, one line per item
   `E1|E2|E3 <DONE|NARROWED|LEFT> - <what the page now says, in a sentence a pop-up could follow>`, the note ids a pop-up
   would rest on, every file you changed under `## Files`, the registry keys you reserved, the searches you ran, the bytes
   of 0103, 0009 and 0107 after, and anything left open and why. Do NOT run the record checks - the next session does, fresh.
   Your last message is one paragraph saying what you wrote.

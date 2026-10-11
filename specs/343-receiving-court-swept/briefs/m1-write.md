# Brief - features 336, 337, 338 and 343 (the magistracy's research owed), group M1. Session 1: write

You are a FRESH session for the record edits of four features. This brief is the whole of what you need; do not read the
features' specs or plans. Work in this clone (`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What the GM asked** (2026-10-10): take up four filed research features about the magistracy compound, and record what
the research found. Research features annotate the record; they change no map and no code.

## Your items (two questions; no new registry key expected unless a source below has none)

- **0104** (`research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html`, with its `.notes.html`; and,
  for item C only, its `.drawing.html`), three changes, EACH COMMITTED ON ITS OWN in this order:
  - **A - feature 343, commit `343: ...`.** The record is silent on the ground before a formal entrance being swept,
    raked, graveled, sanded or bare earth before modern times. Add an absence note saying what was searched:
    - the record (0104, 0110, 0224, 0099, 0090);
    - Japanese web searches on 武家屋敷 前庭 砂利 掃き清める, 玄関 式台 駕籠寄せ 砂利, 門前 掃除 辻番 門番, 高山陣屋
      玄関前 and 大名屋敷 発掘 玄関前 砂利敷;
    - Morse's Japanese Homes and Their Surroundings (1886), searched in full.

    Say, as 0224 reads, that a precinct's swept surface is a guess there and that grave and shrine cleaning are recorded
    only as modern custom. Name Morse's Sakai drawing, his Fig. 283 from the Chikusan teizoden, as Morse dates it
    ("nearly two hundred years ago" from 1886): a stone path through a second gateway to the "genka" inside a garden with
    lanterns. It is a garden approach, only loosely dated, not a court's surface. The sentence that "the one drawing" of
    that ground (Joge's) shows it open becomes true of the two drawings now known. Read Morse at
    https://www.gutenberg.org/cache/epub/52868/pg52868.txt (the archive holds it: `make archive-find TERMS="genka"`).
  - **B - feature 336, commit `336: ...`.** Whether Takayama's guest route from the office to the residence ran indoors.
    Record the three sources, each with its limit:
    - the visitors' route "goes round the rooms of the goyakusho ... and continues on to the residence"
      (`shirobito-1717-takayama`, a modern route over the restored compound);
    - the Gifu prefecture facility table's 渡廊下 12.78 m², listed beside the office (1816) and the residence restored in
      1996, its ends unstated (https://www.pref.gifu.lg.jp/uploaded/attachment/39687.pdf, archived);
    - the Takayama Jin'ya's own illustration of the compound (https://jinya.gifu.jp/en/architecture/), which shows the
      office running straight back under joined roofs into the residence's wings with no open ground between - the
      compound as restored, from an 1830 drawing that has not been read.

    Write that the Edo-period plan itself is unread. Quote the Japanese with an English translation marked as yours.
  - **C - feature 338, commit `338: ...`.** What the Koseki house (`shiroishi-koseki`,
    https://www.shiro-f.jp/shiroishijo/residence) shows of its middle gate:
    「式台付き玄関はないが、塀中門から露地を経て直接に正座敷の縁側に通ずる。」 - a gate in the roji wall, from the gate court
    straight to the principal room's veranda. The house is a middle-rank retainer's residence with no offices. Add an
    absence note: no source read places a middle gate relative to an office hall, in a jin'ya or elsewhere. On 0104's
    DRAWING page, say that the divider gate drawn behind the office hall is a GUESS that no source places.
- **0099** (`research/questions/0099-the-hearing-court-shirasu.html` and `.notes.html`), commit **`337: ...`**: an absence
  note on the size of a ROOFED hearing court, in the form `make open-questions` lists. It names only what was searched:
  - the record;
  - the archive;
  - the Takayama Jin'ya's official and city pages;
  - Japanese Wikipedia's お白洲 (which gives the 1810 South Town plan's 3-shaku veranda and 1-ken stair, not the court);
  - coverage of the Edo, Sado and Suibara magistracies.

  BEFORE writing it, ask the archive one term at a time - `make archive-find TERMS="白洲"` (23 texts hold it),
  then `お白洲`, `吟味所`, `shirasu` - and read the texts it names for any size of a ROOFED court. A size found there is
  recorded and cited, and the absence note is then not written. Check that `make open-questions` lists the note.

Keep each question under the 20,000-byte cap. Change nothing else, and edit no modal, sheet or code.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0104 0099"`. If another session holds either, stop and say so in your handoff. Else
   `make research-claim Q="0104 0099" FEATURE=343`.
2. Read each page and its notes; for each source, `make archive-find URL=<u>` first (the archive before the web), then
   `make source-pages`, then the `source-reader` agent from a bundle on every passage you will quote.
3. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit A, B, C and the 0099 note separately, each message opening with its feature's number.
4. Write `specs/343-receiving-court-swept/briefs/m1-handoff.md`: one `- SECTION=0104/<id>` or `- SECTION=0099/<id>` line
   per changed question and one `- KEY=<key>` per new registry key, then a sentence. Release the claim
   (`make research-claim Q="0104 0099" FEATURE=343 STATUS=done`). Do not push. Your last message is one paragraph.

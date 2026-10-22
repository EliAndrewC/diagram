# Brief - feature 405, page session 4: write (0246, a lane that serves nothing; 0014 split at the size cap)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The research record's
`CLAUDE.md` applies to you above all. Research only: edit no engine code, modal, sheet or canon. Commit each change with a
message opening `405: `. Do not push. Sessions 1-3 edited 0246 before you (see `specs/405-engine-findings-from-385/briefs/p-handoff.md`).

**What is asked (405 T15).** The engine sometimes keeps a lane that serves nothing (leads to no house, field, well, shrine,
ford or other way) whole and sometimes drops it; 0246 is silent, and three claims checks returned NEEDS-RESEARCH. A search
pass has run (2026-10-22); its leads, to be read on their pages before citing (a lead that does not read as said is written
as the page reads, or left out):

- Mencius 《孟子·尽心下》14.21: 「山径之蹊间，介然用之而成路；为间不用，则茅塞之矣。」 - read at
  https://chinakongzi.org/eBook/worksmencius/four/files/basic-html/page207.html (Legge's English on the same page: a hill
  footpath becomes a road by use, and the wild grass fills it when it is not used). ctext.org refused automated reading.
- The Tang Code 《唐律疏議》卷二十六 雜律, article 404 「侵巷街阡陌」, read at
  https://zh.wikisource.org/wiki/唐律疏議/卷第二十六 : lanes, streets and field paths encroached on, planted and tilled
  over, protected only as "places where the public passes" (公行之所); planting that obstructs nothing is no offense.
- Japan: SILENT (the archive's 道普請, 袋小路, 廃道 hits and three web searches found nothing on a disused village path).

## Your items

- **`0246`** (`research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html`, and its notes page if a
  passage goes there by the record's rules):
  1. Record the rule: a lane, or the part of a lane, that serves nothing is not drawn - labeled a GUESS resting on the two
     sources above (a path lasts only while it is walked; lanes and field paths were in fact planted over, protected only
     for the passage they carried); applying them to a hamlet's lanes is the project's reading. Say it extends the page's
     own pull-back of a lane end "to the last house it serves". Add the registry keys the citations need (two at most).
  2. Name the Japanese search as SILENT in an absence note.

- **`0014`** (`research/questions/0014-bunds-between-the-paddies-aze.drawing.html`):
  3. The drawing page is 20,633 bytes against the 20,000-byte question-size cap (whole file, comments counted): 385 T33 took it
     to 20,112 and session 2's dry-hem sentence (T92) added 521, so `make quick` and the push refuse. Split it along its
     topics into a new drawing question (`make reserve` for its number, tagged as 0014 is, with an intro), moving whole
     sections, never trimming; leave each side well under the cap, and repoint every link the move breaks
     (`make record` names them). The engine's claims that cite a moved paragraph will be repointed by the orchestrating
     session: list each moved paragraph and its new home in the handoff.

## When you are done

Run `make record` and the record tests (`make test-file FILE=tests/research`) once, fix what fails, and commit. Append one
line per item to `specs/405-engine-findings-from-385/briefs/p-handoff.md` with `make append`, then a last line `STILL OWED:`
naming anything left. Your last message is one paragraph.

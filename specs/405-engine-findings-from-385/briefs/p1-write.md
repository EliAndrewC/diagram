# Brief - feature 405, page session 1: write (0246, 0081)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The research record's
`CLAUDE.md` applies to you above all. Research only: edit no engine code, modal, sheet or canon. Commit each change with a
message opening `405: `. Do not push.

**What is asked.** The engine's claims checks (impl-drift) found places where two DRAWING pages - how our maps draw a thing,
not the history - are silent, ambiguous or out of step with what the code deliberately does. Each item says what to record.
Every statement you add is labeled as the drawing pages label (historically accurate, deliberate deviation, map drawing
convention, guess). Where an item says the code departs from the page, record the departure as a DEVIATION with its reason;
do not change the page's own rule to match the code. Where an item needs a fact the record does not hold, run a search pass
(the `research-pass` agent) first; where it stays silent, write it as a GUESS and say what was searched. Keep the edits small:
change only the paragraphs an item touches.

## Your items

- **`0246` (`research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html`)**
  1. (405 T78) The page gives 100 ft as the back-lane laying rule (§10) and does not say whether it is the general test of a
     house being served. Say so: a lane END serves a house by §6's test (within 60 ft of the house or 12 ft of the steading's
     built ground, the page's GUESS); the 100 ft is the back-lane laying rule AND the map's check that every farmhouse has a
     way within 100 ft of it (the engine's `WEB_REACH_FT`, which cites this page as its GUESS: "within 100 ft, how close
     counts as serving a house; but the few reached across a neighbor's land") - label it a GUESS.
  2. (405 T88) The page sizes a lane's room on "a 4 ft tread between" the fences (§32) while its gap paragraph (§45) and the
     code's unwidthed default read a 3 ft footpath (0081's footpath). Say which the drawn footpath is - the code draws 3 ft -
     and where the 4 ft applies (a lane's room, if that is what §32 means), or correct §32 if the 4 ft is a slip.
  3. (405 T94) The own-garden exemption is given to "a household's own way". Say that a back lane, a cross lane and the track
     out belong to no household (as the code reads it), and record as the page's GUESS that a join link (a short link joining
     a way end to the network) belongs to no household either.
  4. (405 T114) Two DEVIATIONs of the code from this page, each recorded with its reason:
     (a) the knot exception: where the 7 ft fence gap leaves two households' way ends unjoined (a knot), the engine gathers
     them at one point with the join as close as 3 ft to another household's garden fence - reason: two ways joined at one
     point is what 0081 draws, and where lots abut (`specs/405-engine-findings-from-385/spacing-research.md`: typical
     clustered lots of 90-180 tsubo) the 7 ft cannot always be kept;
     (b) the walled own garden: the run-on to the bund and the homestead fabric keep EVERY garden 7 ft off a way, the way's
     own household's garden included, where the page lets a household's own way run beside its own fence - reason: one
     margin for every garden keeps the run-on's clearance test simple (feature 405 T116, D87); the page's exemption still
     holds for the household's other ways.
- **`0081` (`research/questions/0081-village-lanes.drawing.html`)**
  5. (405 T70) The drawing paragraph "none of them sharp, and never doubling back" stands unqualified beside the bullet "A
     turn the ground forces": qualify it so the two agree.
  6. (405 T70, from T108 D90) The page asks a Z at a joint pulled straight and names no mend when the pull fails. Record the
     code's mend - the joint moved back one vertex (`joints._one_joint`) - as the page's GUESS.
  7. (405 T119) The page lets a straightened lane "come right up to the buildings" within 6 ft of its old line (§33) beside
     keeping a lane's tread 3 ft clear of a farmhouse wall (§34), not saying which wins. Read both in their sources first;
     say which wins, labeled. The engine's lane law today lets a tread come to a house wall (0 ft); do not change that here -
     say what the page holds.
  8. (405 T119) The page sizes the 3 ft tread gap for a farmhouse wall only, while the engine (`joints.tread_gap`) keeps the
     same 3 ft off every building a pull touches (sheds, byres, retirement houses). Search for the other buildings' gap; if
     silent, record the engine's 3 ft for them as the page's GUESS.

## When you are done

Run `make record` and the record tests (`make test-file FILE=tests/research`) once, fix what fails, and commit. Append one
line per item to `specs/405-engine-findings-from-385/briefs/p-handoff.md` with `make append` (what you wrote and where, its
label), then a last line `STILL OWED:` naming anything left. Your last message is one paragraph.

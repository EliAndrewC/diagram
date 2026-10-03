# Brief - feature 317 (reached across a yard), group R2: what the maps draw. Session 1: write

You are a FRESH session for one part of feature 317. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-performance`); the project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What the GM asked** (2026-10-02): whether the record truly shows that a network of village lanes reached every house, or whether
some households crossed a neighbor's yard or land - *"if that is what the research bears out, then we should go with it."*

**What the record now says** (feature 317 R1, checked): `research/questions/0081-village-lanes.html`, the bullet "Was every house
in a clustered village reached by a lane?", answers "Not always": no page states a lane to every house as a rule; Wigmore 1892
records customary passage over a neighbor's land for land with no way of its own to the highway, province by province, once as a
chain (Echigo: C over both B's plot and A's); Morse's Enoshima has alleys to the houses in the rear.

**What the engine now draws** (feature 317, built and measured; the values and their classes - state each in its class, the
record's four classes):

- A nucleated settlement rolls, from its seed, the share of its households that may be reached by passage: between 0 and 25%,
  floored to whole households - a GUESS (the record attests the custom, not how common it was, and a clustered village whose rear
  households all walked through their neighbors' yards is not what its entries describe: alleys to the rear houses, Morse; blind
  alleys to the houses, the Manchu survey already cited on the page).
- While that share has room, the cluster's growth also offers seats against a standing neighbor's land, with no path's room left
  between the two homesteads. A household there is seated ONLY where it has no way of its own to the lanes (the custom's own
  condition, Wigmore - historically accurate) and a walk from its dooryard to the neighbor's threshing yard stays on the two
  households' land and crosses no house, garden bed, shed or fixture of either.
- Its own land must ADJOIN the neighbor's: no farther apart than the parting the growth leaves (2 px, i.e. 2 ft at the hamlet's
  1 ft a pixel) and a foot more - a GUESS; the custom's condition is land against land, never a walk across open ground.
- A chain is allowed as far as Echigo's: a household may be reached across a neighbor who is itself reached across another, and
  no farther - a GUESS citing the Echigo entry, the longest chain the record reads.
- The walk is NOT DRAWN as a lane: a dooryard and a yard are open, trodden ground, and the walk across them is the custom, not a
  way (this record's reading, a GUESS). So such a household shows no lane of its own on the map; the reader sees it standing
  against its neighbor. Measured on the reference spec at 15 households, seeds 1-16: such households appeared on 9 of the 13
  settlements whose share allowed one, never more than the share (`specs/317-reached-across-a-yard/research.md`).
- Every other household is reached by a lane of its own, as before; its path is now routed round its own garden beds and fixtures
  where a straight one would cross them (a map drawing convention: the path is how a seat's way is FOUND, the lane law draws it).

## Your items (one question; no new registry key unless a footnote below needs one)

- 0081's drawing page (`research/questions/0081-village-lanes.drawing.html`): rewrite the bullet "Every farmhouse is served by a
  lane." and its text ("that is a way the maps do not draw, so on our maps every farmhouse has a lane...") to the rule above, each
  value in its class, citing the question page for the custom. Bring the page's other sentences that say the lanes "reach every
  farmhouse" (its opening paragraph and the clustered-settlement lead) into line, and the `Evidence:` comment at its head (the
  classes). Keep the GM's comment where it stands.
- Two items the R1 check left (its log, `specs/317-reached-across-a-yard/briefs/r1-checks.md`, and its last message): (a) on
  0081's question page, the sentence "In neither country was an ordinary village lane a wide, two-lane road" carries no footnote -
  footnote it from a page already in the record that says so, or write an absence note saying what was searched; (b) the registry
  entry of the road ministry's page (the source cited for the 1605 highway widths, 4-7 m in the mountains and 2 ken at passes such
  as Hakone) does not list those widths among the uses its write-up names - add them.

Keep each question under the 20,000-byte cap. Change nothing else.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0081"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram performance (diagram-performance) | 317 | R2 in progress (0081 drawing page: what the maps draw) | 2026-10-03"`.
2. Read the fragments and their notes; for any source you will quote anew, `make archive-find` first (the archive before the web),
   then `make source-pages`, then the source-reader agent from a bundle.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/317-reached-across-a-yard/briefs/r2-handoff.md` (one `- SECTION=0081/<id>` line per section touched and a
   sentence), commit only your files (message beginning `317 R2:`), do not push. Your last message is one paragraph.

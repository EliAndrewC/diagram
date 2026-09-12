# Feature 232 - closing report

*What the pass changed, what it could not close, and every claim a readable source contradicts.*

## What this feature was asked to do

The GM, 2026-09-12: *"I would like to now run down all of the [absence] notes. Like, do however much
research you need to do in order to find sources and citations for those things in the normal way. Normal
rules apply for this, and as always, if you find resources that you believe are likely to be available
online for a human, such as myself who is not a bot and will therefore not have their browsing blocked as
you are sometimes blocked when you try to download papers from certain websites, then let me know and give
me a list."*

162 absence notes were in the record when the pass began. Every one of them was read, searched and given a
verdict; the per-note table is [`research.md`](research.md) R1.

## The numbers

| | |
|---|---|
| notes worked | 162 |
| now CITED | 94 |
| now a GROUNDS note (feature 235) | 1 |
| still an open absence | 67 |
| claims a readable source CONTRADICTS | 14 |
| documents listed for the GM to fetch | 12, plus 5 from the second pass |

The still-absent 67 are not the same 67 the first pass left: a second pass of three batches closed most of
the notes the first pass had called findable, and every remaining note carries its own dated queries and
what they returned.

## THE CONTRADICTIONS - what the record said, and what a readable source says

**SC-007.** Each row's divergence is also stated on its own page, in the sentence a reader meets.

| note | what the record said | what a readable source says | what happened to it |
|---|---|---|---|
| `fields.html` fn-89 | contour ridging belongs to a STEEP slope | its advantages are greater the LESS steep the terrain; steep ground gets terraces and bunds | corrected on the page |
| `cities/river-cities.html` fn-16 | classical headworks kept the offtake near square | a canal leaving a RIVER at 90 degrees is "the most objectionable orientation"; 30-45 degrees is recommended | split by junction type: 30-45 degrees off a river, near-square off a parent canal |
| `cities/hinterland.html` fn-12 | walling ground is expensive, so farmland is the first thing left outside | important Chinese city walls "often enclosed an area much larger than existing urban areas ... to secure resources such as timber and farmland in times of war" | reversed - the sentence now opens "Often, and on purpose" |
| `fields.html` fn-51 | two paddies under the straw raincoat | the preservation council's own site says ONE | corrected |
| `vegetation.html` fn-87 | a windbreak belt stands on one or two windward sides | the Izumo *tsuijimatsu* enclosed the whole perimeter BEFORE Meiji and became a two-sided hook afterwards | corrected - the two-sided form is the wrong end of the change for a pre-Meiji setting |
| `towns.html` fn-22 | a two-story caravan inn | the closest attested analogue, the Chinese *dachedian*, is 平房 - single-story | **left for the GM to rule on** (below) |
| `ways.html` fn-1 | a bearing seat justifies 5-15 ft of bridge landing | bearing length is 10 to 24 inches | corrected; the landing is the project's own and is labeled so |
| `vegetation.html` fn-22 | a FLUCTUATING water table is what resists alder | large fluctuation is where alder EXPANDS; permanent inundation resists it | corrected - the causal direction was reversed |
| `fields.html` fn-82 | a village transplants together BECAUSE labor is exchanged | the survey finds the agreed schedule in both zones, a 7-10 day window where the PRECEDING CROP sets the calendar and communal work is little, and *yui* working BECAUSE dates differ | the observable claim kept and sourced; the causal clause dropped |
| `water.html` fn-73 | a crew re-digs a bend rather than a corner | nobody writes that; the design maxim is 「大弯就势，小弯取直」, follow the large bends and straighten the small | replaced by two sourced statements |
| `urban-features.html` fn-62 | the *chao* hearth and Song Yingxing's basin elaborated as one process | Wagner separates them: an insulated pit with charcoal and forced blast, against an open basin with neither, "a very different process" | separated; *wuchaoni* corrected from a mineral additive to "filthy wet loam" |
| `cities/fabric.html` fn-17 | a merchant's wall marks a standing wealth cannot buy | late-Edo domains "issued the qualification indiscriminately ... in exchange for monetary contributions" | relabeled a **deviation** this project takes, not a finding |
| `cities/fabric.html` fn-20 | the *roji* at 12 ft | 0.9 to 1.8 m | written as both a plain error and a declared **map drawing convention**, since an alley at true width vanishes on the sheet |
| `cities/defenses.html` fn-16 | a gate tunnel about 23 ft | Nanjing's four Zhonghua Gate tunnels measure 4.80-5.35 m, 16-18 ft; Xi'an's is 6 m | the band corrected, Xi'an kept as the wide end |

Two more claims were **withdrawn** rather than corrected, because nothing supports them at all:
`cities/fabric.html` fn-25's town-inn against city contrast, and `cities/hinterland.html` fn-11's 55 ft
"bed", which the *Qimin yaoshu* shows is a parcel of many beds - the hand-worked bed is two paces by one.

## The shape the corrections share, and what it says about the record

Nine of the fourteen are the same failure: **a real finding attached to the wrong case.** Contour ridging
is real and belongs to gentle ground. The near-square offtake is real and belongs to a distributary off a
canal. The two-sided windbreak is real and belongs to the period after ours. The 1 m bank top is real and
belongs to a provincial guideline rather than the national standard the record credited.

None of them came from inventing a number. They came from a source being read once, summarized, and then
applied a step further than it reached - and every one of them was caught by the same thing: putting the
quotation next to the assertion, so the scope of what the source says travels with the claim.

## The maps were still saying the old thing - twelve modals brought back into step

Correcting the record does not correct what a player reads when they click a feature. The modal's prose is
written FROM a research section and does not move when the section does, and nothing about the corrected
page makes that visible.

`scripts/_entry_owed.py` named seventeen class/section pairs this pass had disturbed, and an independent
reader judged each. **Twelve had drifted**, several of them into saying the opposite of the record: the
byre's shared-and-courtyard pairing was inverted, the fruit dike was given as the delta's older form when
the gazetteer puts mulberry first, the sugarcane dike asserted a loop the pass had specifically failed to
find, the pig sty's wording read as "Japan had no pigs" against a record that now names four excavated
sites, and the field ditch's note credited a standard the record records as readable nowhere. All twelve
are rewritten; the table is `research.md` R26.

Two defects in the pages themselves came out of the same reading and are fixed: `archetypes.html` gave the
drawn water ratio as two different numbers three paragraphs apart (measured off the manifest: 80.4% of the
parcel ground is water, median parcel 77.6%), and its dike-crop bullet still called a shipped roll a
candidate for the GM's decision.

## What the pass learned about its own tools, which is the other finding

A large share of the notes reading "no publicly readable source" turned out to be findings about this
container's default request headers rather than about the public web. Three distinct mechanisms, all
measured (`research.md` R5, R22):

- a host that refuses the fetcher's default user agent and serves a browser one normally;
- an article that is **open access by its own license** and still answers 403 or a JavaScript challenge;
- an unfollowed redirect reported as a failure.

The practical consequences are written up where a future pass will meet them: a 403 is evidence about the
fetcher, `curl` under a browser user agent recovers many hosts, Unpaywall / OpenAlex / DOAJ / Semantic
Scholar / Crossref answer reliably, and the MediaWiki, J-STAGE, CiNii, NDL and ctext APIs work when the
general search engines are exhausted or throttled. The web-search budget is SESSION-WIDE across every
agent, which is a real constraint on a pass this size and is what ended the first one.

## The two things reserved for the GM

Neither is a document to fetch. Each is a ruling.

1. **The caravan inn's second story** (`towns.html` fn-22). The one attested analogue is single-story.
   Keep the two-story form as a deliberate deviation, or bring the drawing down.
2. **The Xuxiebian site name** (`urban-features.html` fn-62). A named excavated Sichuan smelting site is
   asserted, and the authority on Han iron names it in neither of the two works of his that are readable
   in full, searched character by character. Either the GM knows where it came from, or it should go; the
   Han claim stands without it.

The documents a person could fetch and this session could not are in [`for-the-gm.md`](for-the-gm.md),
seventeen in all across the two passes, each named to the volume and page and each with the route that
failed.

## What is left open, honestly

- **67 open absence notes.** Each carries its dated queries. They are the backlog, and feature 235 is what
  makes that number mean only that.
- **`SOURCES.html`'s section headings have drifted**: every entry appended for weeks lands under the last
  `<h2>`, `Setting canon`. Nothing derived is affected, since keys are addressed by id, but the headings no
  longer describe what follows them.
- **`ryobosei-jawiki` carries no `Used for:` line.** Pre-existing; both feature-211 write-ups are there, so
  nothing fails.

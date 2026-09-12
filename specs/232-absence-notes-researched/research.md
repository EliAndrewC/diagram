# Feature 232 - research notes

## R1 - the 162 notes and their verdicts

*Filled in per batch as each reader returns; the machine inventory is [`inventory.json`](inventory.json)
and the reader evidence is under [`reader-reports/`](reader-reports/). SC-001 is satisfied when every one
of the 162 has a row here, and SC-005 when every STILL ABSENT row carries its queries, its candidate
pointers and a verdict or a written dismissal for each.*

| batch | notes | CITED | STILL ABSENT | NOT SEARCHED | FOR THE GM | CONTRADICTED |
|---|---|---|---|---|---|---|
| vegetation, roads and the rest | 14 | 8 | 3 | - | 2 | 1 |
| funerary and temple | 29 | 17 | 11 | - | 1 | 0 |
| water A - canals, ditches, sizing | 37 | 21 | 14 | 8 of the 14 | 1 | 1 |
| buildings and houses | 20 | 11 | 5 | - | 4 | 0 |
| fields and crops | 27 | 12 | 7 | 5 | 2 | 2 |
| water B - moats, ponds, wetland, flow | 19 | 11 | 6 | - | 2 | 3 |
| trades, defense and government | 16 | 10 | 2 | - | 0 | 3 |
| **ALL SEVEN BATCHES** | **162** | **90** | **48** | **13+** | **12** | **10** |

*A row does not always sum to its batch: some notes carry a PARTIAL citation (the source supports half
the claim) and some carry a half-verdict (searched for one part, budget-blocked for another). The
authority is the per-note section in each reader report, not this table; the table is for sizing.*

**Nine of the funerary batch's seventeen citations are PARTIAL in a way that changes the SENTENCE, not
only its footnote** - the source carries half of what the record claims and not the other half (planks
but no gravel; the water mouth but not the earth god; grain drying but not the market or the opera; the
sweet-seller on the highway rather than at the gate). Those are FR-004 corrections, not conversions, and
each is written up with the limit named.

## R2 - the Grokipedia question, asked and answered (2026-09-12)

The vegetation reader reported that the ONLY text it could find matching `cities/government.html`
fn-35's claim - that in a planned seat the government compound sits where the main streets cross, with
the bureau offices lining the avenues around it - was on Grokipedia, which constitution XII forbids as a
source (machine-rewritten, no editorial community, no provenance a reader can follow). It did not fetch
it, correctly, and it asked where the claim entered the record from.

**Checked, and the record is clean.** Three things were asked:

1. **Where the sentence entered.** `git log -S` puts it in `59811dcc`, feature 229's migration - it came
   off a retired rule file as part of the sweep, phrased from general reading. It was never sourced to
   anything.
2. **What the sentence claims for itself.** It already reads *"(this rests on general reading; no source
   is cited)"*, and its footnote is an absence note saying the claim entered with no source named. That
   is the honest form, not a citation to a forbidden work.
3. **Whether Grokipedia is cited anywhere in the record.** Three files mention it and all three are
   records of it being REFUSED: `SOURCES.html` states the rule; `cities/government.html` notes that the
   Grokipedia half of a key was dropped and the other half kept; `citations/urban-features.html` records
   two Wikipedia articles that REPLACED Grokipedia pages.

So the resemblance runs the other way: Grokipedia is machine-rewritten from the same widely-repeated
description this record's sentence was written from. The claim stays, labeled as it already is, and this
check is written down so the question is not reopened from the same evidence.

## R3 - a constraint on the reading, found in the first batch

A reader can exhaust its **web-search budget** (200 searches) before finishing its batch. The vegetation
reader did, and `cities/hinterland.html` fn-11 got no searches of its own as a result - its STILL ABSENT
is a gap in that report rather than a finding about the record, and the reader said so, which is the
behavior wanted. Notes in that state are re-read rather than counted, and R1's verdict for fn-11 is
withheld until they are.

The other lesson from batch one: **curl with a browser user agent recovered three sources the default
fetcher lost** - one host refused the connection outright, one PDF came back as binary, one was never
tried. That is the same finding as the blocked-source census, arriving independently.


## R4 - two cautions the funerary reader raised, and what is owed on them

1. **An OCR layer can be wrong in a way that survives into a quotation.** The Chinese journal PDF behind
   two of that batch's quotes renders 租賃 as 租質. The reader transcribed both passages from page
   IMAGES instead and said so. Before either lands, the passage is re-checked the same way, and the
   footnote records that the quotation is read from the page image rather than from the text layer.
2. **Several of these sources need `source-applicability` badly, and one is named already**: the
   crematorium ground areas are Meiji-to-Showa MUNICIPAL facilities being offered as a scale anchor for a
   premodern setting. That is exactly the judgment the agent exists to make (feature 211: a source is
   judged BEFORE its numbers reach a page), and no figure from that batch stands in a page until it has.

## R5 - what the fetcher was costing us, measured twice

The blocked-source census found that only one of nineteen documents was genuinely closed to a person.
The funerary batch then hit the same thing from the other direction: `patheos.com`, recorded in the
record as "403 Forbidden (refused)", returns HTTP 200 and its whole article to `curl` with a browser user
agent, and carries the exact sentence the claim needed. Three PDFs the default fetcher could not use came
down cleanly with `curl` and `pdftotext`.

So a share of the record's 162 absence notes were never findings about what the public can read. They
were findings about one tool's default headers. The honest form of that lesson is not "the notes were
wrong" - each recorded what was actually tried, which is what an absence note is for - but that **what
was tried was too narrow**, and the three checks (a browser user agent, the open-access APIs, a
repository copy) are now part of what a pass owes before it writes one.


## R6 - the standard we could not open, reached by another road

Five notes rested on **GB 50288**, the Chinese national standard for irrigation and drainage engineering
design, and the copies found were an antpedia page that refuses even a browser user agent and a mirror
that is a scan with no text layer. Nothing quotable, and a national standard is not the kind of document
a search finds a substitute for by luck.

The water reader found one anyway: **`T/JSSLKX 002-2021`**, the Jiangsu Society for Water Resources
guideline for the planning and design of small farmland water-conservancy works, an openly readable PDF
whose own clause 9.1.6 declares it subordinate to GB 50288. It carries the numbers, and it closes EIGHT
notes across three pages at once - the 1 m bank top, the 0.3 m bottom width stated explicitly as
maintenance access, canals of every grade running on the high ground of their own command area with the
mains along the contours and the laterals crossing them, and irrigation and drainage as two coordinated
systems rather than one.

**What this does NOT license.** A subordinate guideline is evidence of what the standard requires, not
the standard's own text, so a footnote cites T/JSSLKX and says so. `water.html` fn-49 currently
attributes its 1 m figure to GB 50288 DIRECTLY, which nobody in this project has read; that attribution
is corrected to the guideline, or marked second-hand.

## R7 - the search budget is a real constraint, and the notes it touched are named

TWO of the first three readers exhausted the 200-search budget before finishing their batch. Both said
so plainly and neither dressed an unsearched note as searched-and-empty, which is the behavior the floor
in FR-002 exists to produce.

But a note whose searches were refused has NOT had its pass, and SC-005 cannot be satisfied by a row
that says "no search could be run". So those notes are tracked here and re-read in a second, smaller
wave rather than counted:

| note | why |
|---|---|
| `cities/hinterland.html` fn-11 | the vegetation reader's budget ran out before it reached it |
| eight notes in the water A batch | the reader lists the eight composed queries verbatim with the notes each affects |

The lesson for the remaining batches: a reader that is going to run out does so around two thirds of the
way through, so the batches still out are within reach, and the wave that follows is small.


## R8 - the search budget is SESSION-WIDE, and it is spent

R7 recorded two readers running out of searches. The fourth reader established the shape of it: the
200-search budget is **shared across every agent this session runs**, not per agent, and it was already
spent when that reader made its fourth call. So the batches still out have no general search engine, and
neither will anything else this session dispatches.

**What this does to the feature.** A STILL ABSENT verdict from a reader that could not search is not the
verdict FR-002 defines - it is a note that has not had its pass - so the three readers still out were
told to use a fifth verdict, **NOT SEARCHED - budget exhausted**, and to list the queries they would have
run verbatim. A row that says so is honest and is re-runnable; a row that says STILL ABSENT would be
neither. SC-005 is not satisfiable for those notes in this session, and the spec is not bent to pretend
otherwise: they carry forward.

**What still works without search, and is not nothing.** Direct fetches; `curl` with a browser user
agent; and the APIs, which are not the search tool and kept answering - Crossref, OpenAlex, Unpaywall,
DOAJ, Semantic Scholar, and the MediaWiki API, whose `list=search` is a per-site search that the budget
does not touch. The buildings reader closed 11 of its 20 notes with a spent budget, largely through the
MediaWiki API and Japanese and Chinese Wikipedia reached by title.

**What does NOT work as a substitute**, measured rather than assumed: DuckDuckGo on both endpoints and
Mojeek return zero organic results to `curl`, and Bing drops CJK queries entirely.

## R9 - a guess label on a finding is the same failure as an unlabeled guess

`homesteads.html` fn-36 carries a sentence labeled *"A GUESS - no readable page supports it"*. The
buildings reader found it supported VERBATIM, in the open repository copy of the very article whose
publisher page had returned 403 - pedestrians *"have angular preferences of fewest turns or least angle
changes"*.

Constitution XII names one failure: the reader must never be told a guess is a finding. This is its
mirror, and it costs the record the same way - a reader is told the project guessed at something it can
in fact demonstrate, so the record understates itself and the next session re-researches a closed
question. It is a correction of the same weight as a contradiction, and it goes in the closing report
beside them.


## R10 - the GM's list shrank again, and one entry on it was never needed

The blocked-source census put the *Education About Asia* article behind three `water.html` notes on the
list of documents only a person could fetch. The fields reader closed all three itself: `asianstudies.org`
REDIRECTS to `educationaboutasia.org` and serves the full text to a browser user agent. **A redirect the
default fetcher does not follow looks exactly like a refusal**, which is a third distinct way this
project has mistaken its own tooling for the state of the public web.

`sizes.com` likewise reads at 200 - and reading it produced a correction rather than a citation: the koku
page says nothing whatever about charcoal, so the pointer this record hangs on it is wrong independently
of whether it could be fetched. A source that cannot be read cannot be checked, and an unreadable
pointer had been sitting on a claim it does not support.

**And a search engine still works.** With the budget spent, `search.yahoo.co.jp` fetched through `curl`
with a browser user agent returns real organic results, in English and in CJK, and produced the two best
leads of that reader's pass. DuckDuckGo answers with a challenge, Mojeek and Bing are unusable. It was
relayed to the readers still out.

## R11 - the four contradictions so far, and one of them was predicted

| note | what the record says | what a readable source says |
|---|---|---|
| `fields.html` fn-89 | contour ridging belongs to a STEEP slope | its advantages are greater the LESS steep the terrain; terraces and bunds are what steep ground gets |
| `cities/river-cities.html` fn-16 | classical headworks kept the offtake near square | a canal leaving a river at 90 degrees is "the most objectionable orientation"; 30-45 degrees is recommended. The near-square rule belongs to a distributary leaving a parent CANAL |
| `cities/hinterland.html` fn-12 | walling ground is expensive, so farmland is the first thing left outside | important Chinese city walls "often enclosed an area much larger than existing urban areas ... to secure resources such as timber and farmland in times of war" |
| `fields.html` fn-51 | two paddies under the straw raincoat | the preservation council's own site says ONE |

The hinterland one was PREDICTED and written down before this feature existed. Feature 229's quote-check
pass added that absence note and flagged, in its own comment, that a source already cited on a sibling
page said the opposite of half the claim. The prediction was correct, which is an argument for taking
those comments seriously as a work list rather than as commentary.


## R12 - a fifth correction, and the shape they all share

The fields reader's closing caution: `vegetation.html` fn-87 is headed *"a belt stands on one or two
windward sides"*, and the Izumo *tsuijimatsu* it rests on **enclosed the entire perimeter of the house**
before Meiji, becoming a two-sided hook only afterwards. That is the wrong end of the change for a
setting modeled on pre-Meiji Japan.

Five corrections have come out of five batches, and four of the five share one shape: **the record took a
real finding and attached it to the wrong case.** The contour-ridging rule is real and belongs to gentle
ground rather than steep. The near-square offtake is real and belongs to a distributary leaving a canal
rather than a river. The two-sided windbreak is real and belongs to the period AFTER the one we draw. The
1 m bank top is real and belongs to a provincial guideline rather than to the national standard the
record credits. Only the raincoat anecdote is a plain miscount.

That is worth naming because it says where the next pass should look. These did not come from inventing
numbers; they came from a source being read once, summarized, and then applied a step further than it
reached. The defense against it is the one this project already has - quote the passage at the assertion,
so the scope of what the source actually says travels with the claim - and every one of these five was
caught by putting a quotation next to a sentence that had never carried one.


## R13 - the bridge landing, which is the one likely to reach a map

`ways.html` fn-1 carries a GUESS: a modest timber bridge lands roughly **5 to 15 real feet** of deck past
the water on each side, and the maps draw 10 ft. The reasoning given is that scour undercuts the bank, the
footing must sit back from it, and *"the seat itself needs a length of timber to bear on"*.

The water B reader found and read the engineering manual - Ritter's *Timber Bridges*, 944 pages, hosted
openly by LTRC (the identifier search engines return points at a different publication, which is why
earlier passes failed). **Bearing length is 10 to 24 INCHES on 94-foot highway spans.** So the third leg
of the record's reasoning does not carry the figure at all: a bearing seat is measured in inches, and
cannot justify feet.

This is the correction most likely to imply a change to what a generator DRAWS, which under FR-004 this
feature does not make. What it does: correct the reasoning on the page, state the divergence between the
record and the drawing in the reader's own words, and put it in the closing report with what the source
says and what the map does. Whether 10 ft of landing is right for other reasons - scour, the bank's own
slope, a hand-laid abutment rather than a highway one - is a question for the GM with a generator change
behind it, not a question this pass may answer by moving a number.

## R14 - two more claims the record called unsourced, that are sourced

R9 recorded one sentence labeled a guess that a readable page supports verbatim. The water B batch found
another: `archetypes.html` fn-82's dike erosion, which the record calls unsourced, is in a CC-BY paper
almost word for word - *"arable dikes, which used to be 20 meters wide, were eroded to less than 4
meters"* - the exact magnitude the note says nothing carries.

Both were open-access articles whose PUBLISHER page refused our fetcher while a repository or a direct
PDF host served the same text at 200. The pattern is now established well enough to state plainly: a
meaningful share of this record's "no readable source" notes were written about pages that are readable.

## R15 - three corrections from the water B batch

| note | what the record says | what a readable source says |
|---|---|---|
| `towns.html` fn-22 | a two-story inn | the closest attested analogue, the Chinese *dachedian*, is described as 平房 - single-story |
| `ways.html` fn-1 | a bearing seat justifies 5-15 ft of landing | bearing length is 10 to 24 inches (R13) |
| `vegetation.html` fn-22 | a FLUCTUATING water table is what resists alder | large fluctuation is where alder EXPANDS; permanent inundation is what resists it |

The alder one is the fourth of the "right finding, wrong case" family in R12, and the sharpest: the
record has the causal direction reversed, not merely the scope.


## R16 - the reading is finished: what 162 notes came to

Every note has a verdict. **90 of 162 found a readable source** - well over half of what the record had
recorded as unsupported was supportable, and most of the difference was not new scholarship but a
browser user agent, a redirect followed, an open-access repository, or a search engine that answers.

**10 claims are contradicted by a source we can now read.** That is the feature's real yield. A footnote
that merely gains a citation changes nothing a reader sees; a contradicted claim was wrong on the page.

The last batch added three, including the two largest errors of the whole pass:

| note | what the record says | what a readable source says |
|---|---|---|
| `fields.html` fn-36 | a market area of 300-500 sq km | Skinner's own open text: *"marketing areas are just over 50 square kilometers"*, *"eighteen or so villages distributed over fifty square kilometers"* - out by a factor of six to ten. The map argument survives at the corrected number |
| `cities/defenses.html` fn-17 | a round tower is a European medieval signature, and the European and Chinese rationales are inverted | the Song *dituan* corner tower is arc-shaped ON PURPOSE, *"to increase the difficulty of the enemy's attack and to reduce the area exposed to attack"* - which IS the European reason. The inversion is wrong and so is the signature; what survives is the rectilinear *mamian* at bowshot spacing |
| `cities/fabric.html` fn-36 | a fire tower per machi | one per TEN machi, with a ladder-and-bell on the watch hut between. Correcting it makes this page agree with `cities/capitals.html`, which it currently contradicts |

That last one is worth its own line: **the record contradicted ITSELF on two pages, and no check caught
it.** Nothing in this project compares one research page's number against another's. The source pass
found it by accident, in the course of sourcing one of the two.

## R17 - what this says about the absence notes as a class

The honest summary for the GM is not "the notes were wrong". Each recorded what was actually tried, which
is what an absence note is for, and 48 of them survive a much harder pass unchanged. Three things were
wrong, and they are different from each other:

1. **What was tried was too narrow.** One fetcher, one set of headers, no redirect following, no
   open-access lookup. That accounts for most of the 90.
2. **A source read once was applied a step beyond its scope** - five times, the R12 family.
3. **A claim was labeled a guess that a readable page supports** - twice (R9, R14), which understates the
   record in the same way an unlabeled guess overstates it.

None of the three is an argument against the absence-note rule. All three are arguments for it: every one
of these was found because feature 195 forced the claim to say what stood behind it, which made a list of
exactly the sentences worth re-reading.

# Feature 238 - research notes

## R1 - the census of unfootnoted paragraphs (2026-09-12)

Feature 232's closing report estimated *"roughly 180 sentences across the thirteen pages"*. That figure
came from six `quote-check` agents reporting as they went, and no list of the sentences survived - the
agents' findings were applied and their reports were not kept. So the population has to be rebuilt, and
the first question is how big the reading is.

**Method.** Every `<p>` inside `<main>` on every research page except `SOURCES.html`, counted, and
counted again for those carrying no `<sup class="fn">`. This is an upper bound on the work, not the work:
a paragraph with no footnote is very often not an assertion about the world at all - it frames a section,
states a drawing convention, or records a decision, none of which owes a source. The third column counts
the inline markers (`unsourced`, `no source is cited`, `rests on general reading`, `not cited`) that
feature 232 named as honest but invisible to the classifier.

| page | paragraphs | no footnote | inline markers |
|---|---:|---:|---:|
| `archetypes.html` | 67 | 31 | 26 |
| `buildings.html` | 51 | 22 | 38 |
| `fields.html` | 89 | 66 | 15 |
| `homesteads.html` | 131 | 97 | 24 |
| `presentation.html` | 42 | 42 | 0 |
| `religion-and-death.html` | 67 | 43 | 8 |
| `settlements.html` | 38 | 28 | 0 |
| `towns.html` | 42 | 32 | 9 |
| `urban-features.html` | 80 | 56 | 27 |
| `vegetation.html` | 68 | 50 | 28 |
| `water.html` | 122 | 96 | 18 |
| `ways.html` | 26 | 21 | 10 |
| `cities/capitals.html` | 209 | 169 | 21 |
| `cities/defenses.html` | 23 | 12 | 11 |
| `cities/fabric.html` | 56 | 32 | 15 |
| `cities/government.html` | 31 | 21 | 15 |
| `cities/hinterland.html` | 21 | 14 | 7 |
| `cities/river-cities.html` | 18 | 15 | 11 |
| `cities/sizing.html` | 19 | 17 | 2 |
| **total** | **1,200** | **864** | **285** |

**What the numbers say.** Nineteen pages, not thirteen: 232 read the pages that carried absence notes,
and `presentation.html`, `settlements.html` and the six under `cities/` were not all in that set.
`presentation.html` is the clearest case of the upper bound being the wrong number - all 42 of its
paragraphs carry no footnote and none of them owes one, because the page is about how the map is drawn
rather than about the world.

The 285 inline markers are the floor of the real work: each is a sentence a previous session already knew
was unsupported and labeled in prose instead of in a note. They are not 285 distinct sentences (a
paragraph can carry two) and they are not all `CITE` (many will be `GROUNDS` - a decision, a drawing
convention), but every one of them is a sentence somebody has already judged to need something.

So the honest expectation is that the pass is **larger than the 180 the residue estimated** and
**smaller than the 864 the census bounds**, and the inventory FR-001 builds is the only number that will
mean anything.

## R2 - the caravan inn's second story: what the record already says (2026-09-12)

The GM ruled on 2026-09-12:

> The caravan in does not a deliberate deviation. So if the record draws it as two story, then that is
> simply a mistake. If our attested analog reads it as a single story.

Two halves. The first is unconditional: the caravan inn is not a deliberate deviation, so its drawn form
may not be recorded as one. The second is conditional on the attested analogue, and **the record already
answers that condition**, with a citation rather than an absence note. `research/towns.html`:

> The second story is the one part of the drawn inn the record does not bear out: the same account says
> the buildings in the yard were uniformly single-story, mud brick and reed thatch.

The footnote behind it is `towns.html` fn-25, `dachedian-jilin-daily`, quoting 「院里清一色平房，同样是用土坯和苇草盖成。」
- 平房 names a single-story building as against a multi-story one.

**Where the drawing is.** `settlement/civic_grounds/lodging.py`, the `inn()` glyph: a lower eave band
commented `(2-story)` and a row of three `upper-story lattice windows`, with a docstring calling the
footprint "a large 2-story post-road inn". No LIVE map draws it - the two towns that call `s.inn()`,
Hirameki and Ubame, are in `legacy-hand-authored-pool/`, which is frozen and never regenerated. So the
change moves no shipped map; it changes what the next town drawn will get.

**The open question, which does NOT gate the fix.** The engine's own docstring says *post-road inn*,
which is a Japanese institution (旅籠, hatago), while the only analogue read is a twentieth-century
Manchurian cart inn. If two-story post-station inns are attested in Japan, the drawn second story would
have support and the record should carry that citation instead. A `source-reader` was dispatched on that
question on 2026-09-12. **The default action is the fix**: the analogue in the record reads single-story,
which is the condition the GM set, so the second story goes unless a reading actually overturns fn-25.
Recording it the other way round - making the GM's ruling wait on a research question the session
thought of - is re-setting the GM's own trigger, which `spec-fidelity` refused in round 1 of this spec's
review.

### R2a - what the reading found, 2026-09-12

A `source-reader` was asked four questions. The short answer is that the premise the GM's ruling rested
on has moved: there are now **two attested analogues pointing opposite ways**, and the Japanese one - the
setting's first model - is two-story.

**A two-story post-station inn IS attested.** 大旅籠柏屋 (the Ō-hatago Kashibaya), the preserved hatago of
Okabe-juku on the Tōkaidō, built around 1836 and a registered tangible cultural property since 1998, is
described in its own infobox as 「木造2階建、瓦葺」 - "wooden, two stories, tile-roofed" (translated from the
Japanese by this project). Its second floor is 「客間として使用された空間」 - "a space that was used as guest
rooms". Source: Japanese Wikipedia 大旅籠柏屋.

**But "commonly" is not attested.** No page read says hatago were usually two-story. The nearest general
statement cuts the other way: Seki-juku's surviving townhouses are 「二階建・中二階建・平屋建」 - "two-story,
half-second-story and single-story" - "making for a varied townscape". And the encyclopedia entry on the
hatago-ya classes them by SIZE (large, medium, small), not by stories; the 本陣 article lists what a
hatago was forbidden - a front gate, a shikidai entrance, a raised-dais room - and **names no story
restriction**, which is a real if negative finding.

**The inns that actually served drivers say nothing either way.** 馬宿 (umayado), 木賃宿 (kichin-yado) and
問屋場 (toiyaba) are defined on four pages with their clientele and their rates - the 1611 ordinance fixed
the kichin charge at three mon for a person and six for a horse - and not one states a story count. One
passage is worth keeping for a different reason: a dictionary usage example gives 「表は旅人宿で、裏には大きい
厩があって馬宿もする」 - "the front is a travelers' inn, and at the back there is a large stable, so it also
does umayado business" - which is exactly the arrangement our town maps draw, inn in front and stable
behind.

**The Chinese side gained a second account but not a second story reading.** Chinese Wikipedia 大车店
describes the twenty-to-a-kang dormitory and the basket shop-sign and never uses 平房, 二层 or 楼. So
`towns.html` fn-25 - the Jilin Daily's 「院里清一色平房」 - remains the only story reading on the Chinese
side, and it is NOT overturned.

**What this means for the ruling.** The GM's condition was *"if our attested analog reads it as a single
story"*. When they wrote it, the record had one analogue and it read single-story. It now has two, and
they disagree: a Manchurian cart inn that is single-story, and a surviving Japanese highway inn that is
two-story. Two things follow, and only the first is this session's to do.

1. **One sentence on `towns.html` is now false and is corrected under FR-006.** It says "The second story
   is the one part of the drawn inn the record does not bear out". The record does bear it out, from
   Okabe-juku. The page carries that citation instead.
2. **The form itself is a question the session may not settle alone.** Constitution Principle XII's own
   ladder says two supportable answers become a KNOB rolled per settlement, never a choice - which would
   mean the story count varies by town. But the GM has already ruled on this specific drawing, and
   reaching for the knob doctrine to keep a form they called a mistake is exactly the shape Principle XVI
   forbids a session to approve for itself. So it goes to an independent adjudication first, and to the
   GM with the evidence either way.

**One caution on the reading.** The agent's own WebSearch budget was exhausted at its first query, so
every page it reached was a guessed URL. It names three cultural-property listings that would probably
settle the "commonly" question - Narai's 中村邸, Toyokawa's 大橋屋, Kameyama's 玉屋 - and one host that
refused it, `www.aichi-c.ed.jp`, which was Wikipedia's cited source on 大橋屋 and may carry that
building's story count. Those are in the GM's download list.

### R2b - what `source-applicability` caught in this feature's own first citation (2026-09-13)

APPLICABLE-WITH-LIMITS on `okabe-hatago-jawiki`, `What it is:` accurate, **limits MISSING three** - and the
serious one is worth recording because it is precisely the failure this whole feature exists to correct,
committed by the session while correcting it elsewhere.

**The write-up asserted that a lodging house of this kind "took travelers on foot and by palanquin".**
That is on no page read. 駕籠 and 徒歩 appear nowhere in the article, nor on the Okabe-juku page, and the
encyclopedia entry on the hatago names its guests as samurai, common people and itinerant merchants -
which is nearer the map's clientele, not further. It was the session's own inference, written flat as a
fact, and it was **load-bearing**: it is the premise the disqualifying conclusion was drawn from. Worse,
the record's own other sources cut against it - a Tokaido post station is organized around large numbers
of horses, and this very inn's proprietors served as the officer who ran the relay of men and horses.

The negative half was an argument from silence stated as fact. "It has no cart yard, no long stable, no
feeding trough and no grooms' lean-to" asserts more than silence can carry: the article describes the
surviving building's rooms and does not describe the plot as it stood. The conclusion survives; the
invented fact does not. All three places now read that **nothing read describes** those fittings at a
lodging house of that kind - the registry write-up, `towns.html`, and the footnote's comment.

Two more, both applied. A parenthetical claiming "one post station's surviving frontages are recorded as
a mixture of two-story, half-second-story and single-story" sat inside this key's write-up, where a
reader would take it for something this article says; it is from a different page, carried no key, and is
dropped - the clause it qualified, that nothing read says inns of this kind were usually two stories, is
true and stands alone. And the limits paragraph now carries the two the reader needs: the building is
**selected by its own survival** (大旅籠 is the great hatago of its town, its proprietors ran a pawnshop
and held post-station office - the leading house of the street, not the ordinary one on it), and its date
of about 1836 is the very end of the period this setting draws on. That second one matters for symmetry:
the counterweight source is disclaimed in its own write-up for being a twentieth-century survival, so
both sides of the open question now state their dates.

Two wording slips also fixed: the building is a 再建, a rebuilding, and its date is inferred from an 1835
cost record rather than documented; and it is a REGISTERED tangible cultural property, which the verb
already said and the noun now does too.

**The lesson is the feature's own.** An inference written flat, inside a limits paragraph, in a citation
added by the pass whose subject is inferences written flat. The check that caught it is the fifth research
box, and it earned its place here on the first source this feature registered.

## R3 - the inventory (2026-09-13)

Four `quote-check` readers, one per batch, each asked for the one thing this feature needs: per section,
every sentence that asserts something about how a place was built, farmed, planted, governed, traded in,
worshipped in or lived in, and that carries no footnote. Their reports are kept verbatim under
`reader-reports/`. **The reports are the evidence; the dispositions are this session's.**

| batch | pages | sections read | items | with an inline marker |
|---|---|---:|---:|---:|
| A | religion-and-death, vegetation, urban-features | 53 | 171 | 34 |
| B | the four `cities/` pages (capitals, fabric, government, defenses) | 72 | 203 | 59 inline + 12 roster-only |
| C | water, fields, cities/river-cities, cities/hinterland, cities/sizing | 57 | 153 | 51 |
| D | homesteads, buildings, archetypes, settlements, towns, ways, presentation | 100 | 168 | 67 |
| **all** | **19 of 19 pages** | **282** | **695** | **223** |

**The residue's estimate of "roughly 180 sentences" was low by about a factor of four.** R1 bounded the
work at 864 unfootnoted paragraphs and floored it at 285 inline markers; 695 sits between them, which is
what the bound and the floor were for. The estimate was not careless - it came from six agents reporting
in passing while doing a different job, and a count made in passing is a count of what was noticed.

### Four shapes the readers found, which matter more than any single item

**1. The marker is narrower than the sentence it sits in.** `buildings.html`'s poverty-texture sentence
carries "(both specifics unsourced)" while making three assertions; `homesteads.html`'s village-variation
paragraph closes with a marker naming "the field-system and market groundings" while also asserting a
siting rule, four site-to-form mappings and a water claim. **A reader counting markers undercounts**, and
so did R1's floor of 285.

**2. Roster-level disclosure hides from the reader.** In more than thirty places across the four reports
the section's `Sources:` line admits a figure was never read while the sentence carrying it stands bare
in the body - the Honcho-dori street width, the length of Edo's buried mains, the Toribeno distance,
the south-facing-by-divination gate rule, the sluice's board-in-grooves mechanism, the eleven-figure
Sugiura table, `fields.html`'s whole per-archetype in-field siting matrix, the samurai quarter's absent
public wells, the one-well-per-10-to-20-households rate. The record's own rule is a footnote AT the
assertion; an admission elsewhere on the page is honesty the reader never meets. **These are the items
most likely to be mistaken for findings on a skim**, and they are the highest-value work in this feature.

**3. Unfootnoted quotations.** A quotation with no source is a sharper failure than a paraphrase with no
source, because quotation marks assert that someone specific said this. Eight across the four reports,
including 「larger compounds separated by walls and gates」 and 「six rooms and three shifts」 on
`capitals.html`; Injo-ji 「at the entrance of Rendaino」, with "explicitly described as" attributing it to
nothing; Shen Kuo's 矢石相及 on `defenses.html`; and 「had to do with rainfall or natural underground
sources」 on `urban-features.html`, whose own note says the phrase is not on the page it cites.

**4. Two cross-page contradictions, both of the same kind** - one page states as a finding what another
page records as unsupported:

- **The Forbidden City's NW-in / SE-out flush.** `water.html` "A fed closed moat must drain" asserts it
  inside a footnoted bullet; `water.html` "The diverted-stream moat is a historical type" says of the same
  direction "no readable page supports the direction - a GUESS". Same page, two sections.
- **The sealed samurai quarter.** `cities/government.html` states in the historical voice that a seat of
  this size seals its samurai ground with an earthwork and palisade abutting the city wall;
  `cities/capitals.html` records that "This research says the continuous fence is more than history
  supports even there"; and `cities/defenses.html` then builds a second rule on top of the first.

Both are FR-006 corrections. Neither is a reading failure - each is a page written at a different time
from a different source, which is the failure mode a record of this size has by construction.

### R3a - what batch A added, and where the density actually is (2026-09-13)

The three pages feature 232 named as clusters came back at 171 items, and the reader's own headline is
that **232 named the right pages and not the worst sections on them**.

- The torii-count distribution, named in the closing report, is **one** unfootnoted sentence.
- "Forest density and crown size" on `vegetation.html` is a section with **zero footnotes anywhere in it**.
- The tanning yard (19 items) and the bell-and-drum tower (10) are the two densest clusters on the three
  pages, as named. The tower entry is **one paragraph carrying ten unfootnoted real-world claims**,
  including every acoustic and audibility figure it rests on - decibel levels, a night noise floor, a
  fee-radius in kilometers, a threshold past which one tower stops sufficing.
- But `urban-features.html`'s "Trade works" section (16 items) and "Stable yards" (3 items, each a dense
  run of measured figures) **are comparable and were not named**. So is the well research (5), whose base
  rate - one to three communal wells for a village of seventy households - is what this project's whole
  well liberty is measured against.

`urban-features.html` alone carries **103 of the 695**, which is 14.8% of the record's whole exposure
on one page (`m:urban-features-share`). It is the page to work first.

### R3b - the inventory, closed

**695 items over 282 sections and 19 pages**. The four batches agree closely on the shape of what they
found, and the shape is worth stating precisely rather than roundly, because a later feature has to
plan against it: **494 of the 695 carry no marker of any kind, 71.1% - seven in ten rather than the two
thirds a first reading of these reports suggested** (`m:unmarked-share`), and **390 are HIGH, 56.1% of
the whole** (`m:high-share`) - or 59.7% if the 25 items the readers hedged `MEDIUM-HIGH` are counted as
HIGH (`m:high-share-with-hedged`), which is the ambiguity that hedged tier exists to keep visible.

<!-- The harness is measure/inventory_shares.py; it loads feature 242's census by path rather than
     copying its parser, so there is one thing to keep true. -->

Two pages are `NOT AN ASSERTION` in bulk and need no work: `presentation.html` (zero items) and
`settlements.html` (one, restating footnoted canon). That is the census's upper bound doing its job -
84 unfootnoted paragraphs between them, none of which owes a source.

**What the number means for the feature.** A `source-reader` pass on every `CITE` item is several times
feature 232, which took a day of readers for 162 notes. FR-009's page-by-page batching is therefore not a
convenience but the deliverable's shape: pages land finished, and FR-010 names whatever does not. The
order is R3a's - `urban-features` first at 103 items, then `capitals` at 125, then the rest by density.

**And the priority within a page is the second shape from R3, not the count.** An item whose section
roster already admits the figure was never read is a defect the reader meets as a finding; an item nobody
ever claimed a source for is a gap. The defects come first.

## R4 - `urban-features.html`, the first page worked (2026-09-13)

Nine items closed, all of them the second shape from R3: the section's `Sources:` roster already recorded
that a figure had been searched for and not found, while the sentence carrying it stood bare in the body.
No new research was needed for any of them - the search had been done and dated; the label was in a place
the reader never looks. Each is now a note at its own assertion, and each roster line points at the notes
instead of carrying the admission.

| the claim | what it became |
|---|---|
| one well per ten to twenty households, in a commoner quarter | ABSENCE (searched 2026-08-28, 共同井戸 世帯数) |
| the samurai quarter keeps NO public wells, drawing from private ones inside its compounds | ABSENCE (searched 2026-08-28, 武家屋敷 井戸) |
| the same ratio again, in the sibling section, as ten to eighteen | ABSENCE, naming the duplication |
| a walled city keeps a burakumin neighborhood inside, for its labor in a siege | **GROUNDS: this project's decision** |
| a kido ward gate barred at night seals the samurai quarter | ABSENCE (searched 2026-09-13) |
| the Kawagoe bell tower's base dimension | ABSENCE; the figure REMOVED, the height kept |
| the Dingbian and Xingcheng tower plans | ABSENCE; both figures REMOVED |
| an inspection station at every gate, and a caravan facility on the trade route | ABSENCE; the gate tariff and the granary restated as the setting's canon |
| kiln workers living at the kiln | ABSENCE; the three arguments kept as reasoning |

**Two of the nine did not get a note - they lost a number.** The Kawagoe base and the Dingbian and
Xingcheng plans were figures no reader can check supporting a distinction that survives without them: the
type contrast is carried by the Pingyao market tower, which IS quoted. A relabeled figure would have kept
a precision the record cannot back. Where a number does work, it stays and is labeled; where it does not,
it goes.

**One GROUNDS note, written carefully.** The burakumin-quarter rule is a decision this project made for
its own maps, and the siege-labor sentence beside it is the reasoning offered for the decision rather
than a historical finding - which is the one thing that makes the form legitimate here. Feature 235's
prohibition is quoted in the note's own comment, because a grounds note on a caste's siting is exactly
the shape that would let a hard research question be relabelled a decision.

### R4a - a citation that said more than its quote

Not a roster case, and the only one of its kind found on this page. The text read *"Song Kaifeng ran 20+
dedicated wanghuolou fire-lookout towers with a standing brigade"* with a footnote attached. The quoted
passage behind it says something else: 「In every ward, at every three hundred paces, there is a military
patrol post, and on high ground there is a fire-watch tower, with men on top keeping lookout and a
hundred soldiers quartered below」. Per ward, not per city, and no count of towers anywhere in it. The
roster had recorded that a citywide count was "not found in any page read" while the footnote sat on the
sentence making one. The sentence now says what the source says.

### R4b - what the entry-drift check found, which was not drift

`make page-check` named one pair after the section changed - the `well` modal. The agent reported
**IN-STEP**: the modal carries neither of the newly-hedged claims, and its numbers come from the sibling
section, which was untouched. What it found instead was an inconsistency between the two sections - one
newly saying no page gives a households-per-well ratio while the other still asserted one - and it said
plainly that this was a question for the record's own checkers rather than a modal rewrite. It was right,
and closing it is the third row of the table above. **An agent asked one question answered a different
one correctly and stayed inside its brief**, which is worth recording as the behavior to want.

## R5 - the GM's second download, read (2026-09-13)

The GM fetched thirteen of the sixteen documents in Part 1 of `academic-sources/TO-DOWNLOAD.md` and
reported the other three unavailable, which settles those: they stay uncited and their claims keep their
absence notes. Four `source-reader` agents then read the copies against the exact claims resting on them.
**Ten quotations came back verbatim and one load-bearing reading was confirmed. Seven defects came back
with them**, and two of the seven change what an entry argues rather than how it is worded.

### R5a - the two that change an argument

**1. The Wagner workforce figures describe the opposite of what the record built on them.** The entry had
read "200 charcoal producers alongside 200 furnace-tenders and 300 miners" and concluded that "the fuel
workforce as large as the furnace workforce". The source says "more than 200 furnace tenders, 300 miners,
and 200 'water-carriers' and charcoal producers" - one figure covering two occupations, against a furnace
figure that is explicitly "more than" 200. The comparison does not survive. Worse, the record used that
staffing as its picture of ONE concentrated state complex, and the same paragraph of the source rejects
that reading: the authority calls it "a large firm which operated numerous ironworks scattered over a
large area". The figures were leaned on in three places on the page; all three are rewritten.

**2. The two-site arrangement is attested CHINESE practice, not a Japanese override.** The entry's
"THE DISCLOSED DIVERGENCE" said the Chinese arrangement is one site - a fining basin a few feet from the
blast-furnace outlet - and that our maps follow the Japanese two-site pattern instead. Both arrangements
are in the same work. The single site is the seventeenth-century treatise's description; Guangdong's
large-scale sector is the other, with "large firms operating numerous ironworks in the forested mountains
of the province" and the pig iron shipped downriver to Foshan for conversion and casting. That is what
these maps draw. The heading is now "WHY THE TWO SITES ARE NOT A DEPARTURE", and the section gained a
sourced reason for the spacing as well: two charcoal blast furnaces are not normally put close together,
because it doubles the load on the forest for little or no gain.

### R5b - the five smaller defects, all fixed

- **A quotation readable on no page the note points at.** `urban-features` fn-88 quoted "believed to be
  fining hearths" of Han archaeology. That phrase is in neither Wagner document - both searched in full -
  and comes from a third work this project does not hold. It failed the feature-195 condition outright and
  is gone; the note now says the evidence is deferred to a book we have not read.
- **A hearth described as open that the source calls insulated.** The record had fining as "an open fire
  under a forced blast". The working hearth is "a small well-insulated hollow in the ground"; *open* is
  the word the authority reserves for the basin he argues cannot work as described.
- **A truncation with no ellipsis.** `fields` fn-10 began its quotation mid-sentence, dropping the
  source's own reason for the practice - root soundness and the ground bearing capacity that lets a field
  be walked. Restored.
- **A quotation of a damaged text layer.** `cities/river-cities` fn-16 rendered the degree signs as
  apostrophes, which is what a broken extraction produces and not what the page shows. A quotation has to
  be findable by a reader opening the page, so it reads as the page does. (The `rl` for `a` stays: that
  smudge is on the scanned page itself.)
- **An inference presented as a quotation's content.** The same note's "so what enters is the cleaner
  upper water" is in neither quoted sentence. The unit does say it, four pages later, and that passage is
  now quoted instead of inferred.

### R5c - what the reading CONFIRMED, which matters as much

- **The staged paddy depth.** All six MAFF quotations verbatim, and the load-bearing reading confirmed on
  two independent surfaces: 10 cm and 20 cm appear only as a cold contingency at two named growth stages,
  conditioned in the text on 「気温が下がる恐れがある場合は」 and labeled 「低温障害対策」 in the document's own
  chart. The only ordinary depths in ten pages are 3-4 cm and 2-3 cm. A record that had asserted a
  maintained four-to-six-inch depth would have been contradicted by its own source.
- **The offtake angles, and that the record is right to carry two bands.** The document really does
  distinguish the river case (30 to 45 degrees, section 10.4) from the canal case (60 to 80 degrees,
  section 10.6) in two separately headed sections, and it never reconciles them - so the record's line
  that a drawn junction has to say which of the two it is was the only reading available.
- **Xuxiebian is in neither Wagner work**, searched again in full against the downloaded copies, in
  romanization and in characters. The only named Han ironworking site anywhere in either is Guxingzhen at
  Zhengzhou in Henan - a link in a site map rather than a statement in the text, and not in Sichuan. The
  absence note holds and now records the second search.

### R5d - a reader's own quotation was wrong, and checking it is why we know

The desire-paths reader reported the record's quotation as differing from the paper: it gave "the angular
'choice'" where the record has "the angular weighted 'choice'". Extracting the text of the PDF directly
shows the paper reads **"the angular weighted choice"** - the record was right and the agent dropped a
word. This is the second time in two features that a checking agent's own factual claim has needed the
same verification we give our own (feature 232's memory records the first, a date pair that appeared in
no paper). **An agent's finding is a lead, not a verdict**, and the cost of confirming one is a minute
against a wrong correction landing in the record.

What the same reader got right, and it is the more important half: the turn preference the record cites
is Hillier and Iida's 2005 result reported at second hand and hedged - pedestrians "are believed to have"
those preferences - while the paper's own "Go straight!" rule is a **modeling assumption its agents were
given**, not a finding, and its measured "angle" of 90-120 degrees is the agent's field of vision rather
than a turn. The footnote had presented the agent rule as the paper following the same preference; it now
says it is an input the model was built on.

### R5e - the Korean grove figures, the outcast siting, and a source swap that lost a claim

**The Korean grove mean was mis-scoped.** The registry read 10,375 m² as the mean of the 462-grove census.
It is the paper's own 전국 평균 면적, but Table 3 is a table of eight PROVINCIAL means and 10,375 is their
unweighted average - it weights a province with 37 groves equally with one holding 131. The per-grove
mean of the census is the paper's own total over its own count, about 10,223 m². Both figures are now in
the registry, with which is which. Two limits were also missing and are added: the 100 field-surveyed
groves are a purposive selection with fixed provincial quotas rather than a sample of the 462, and their
mean area of 17,253 m² is well above the census's, so they skew large; and **the paper names Japan
nowhere**, in its text or in any of its twenty-five references, so reading a Korean maeulsup across to a
Japanese homestead grove is entirely this project's step and now says so.

**The outcast-quarter siting: what the dissertation gives, and what it does not.** It gives the
separation (a distinct residential cluster inside the parent village's own territory), the attachment
("nearly every kawata village in the Kinai ... attached to a nearby peasant community"), the poor ground,
and a direction with a mechanism behind it - the community settled on the uncultivated land that was
left, which in the case studied was the south end, confirmed by the informal name neighbors used for it.
It gives **no distance in any unit, no watercourse and no wall**. So the record's reading of "across its
stream" out of the name kawaramono is this project's own step, and the page now says so rather than
leaving the etymology to look like a siting source.

**A claim did not survive its own source swap.** The Daoist clergy rule rested on an unsigned portal page
with no author and no references, which the registry itself had flagged for replacement. Three open works
were read to replace it. Two of its three halves came through with better evidence - the married priest
living at home is Lai's own sentence, and the hereditary office is Lagerwey's dated genealogies over
sixteen generations, which demonstrate it rather than assert it. **The third half did not.** That marriage
is REQUIRED to become a priest of the highest rank is supported by none of the three: the first treats
ordination ranks at length and conditions none of them on marriage, the second discusses no clerical
ranks at all, and the third is about the ranks of GODS rather than of priests - which is the trap, since
matching its "rank" to the claim would be the same word meaning a different thing. The claim came from
the portal page and it is deleted rather than re-cited.

That is the honest shape of a source swap: it improves what it can support and it takes away what it
cannot. **Two of three is a good outcome, and the third being gone is the point of doing it.** The portal
page is now cited for nothing and its footnote is removed; Lagerwey's own tables also force a widening
the record carries, since transmission there runs to an adopted son, a son-in-law or a disciple as
readily as to a son.

### R5f - what did NOT turn out to be a defect

Two of the readers' flags did not survive checking, and both are worth recording, because the cost of
checking them was minutes and the cost of acting on them would have been a wrong correction.

- **The desire-paths quotation.** The reader reported the record quoting "the angular weighted 'choice'"
  where the paper says "the angular 'choice'". Extracting the PDF's own text shows the paper reads
  **angular weighted choice**. The record was right; the agent dropped a word.
- **The outcast-village comparison.** A reader returned CONTRADICTED on "a kawata village lived nearer to
  two neighboring villages than to the kawata of their own status" - correctly, because that is not what
  the source says. But it is not what the RECORD says either: the page reads "the peasants of the village
  lived nearer to two neighboring villages than to the kawata of their own", which is the source's
  sentence. The reversed version was in the prompt this session wrote for the reader, not on the page.
  **A badly paraphrased claim in a prompt produces a true finding about a false claim**, and the only
  protection is reading the page before acting on the verdict.

### R5g - `source-applicability` on the two replacement sources (2026-09-13)

Both APPLICABLE-WITH-LIMITS, both `What it is:` accurate, and **the deletion verified**: neither work
conditions any ordination, rank or grade on marriage. The one residence requirement in either runs the
other way - the monastic ordinands had to have lived in a monastery for three years. Nothing true was
removed.

Seven corrections to the write-ups, all applied.

**The premodern half of the Daoism claim is a RELAY, and the limits said the opposite.** The write-up had
hedged that the article "reaches this setting only as the surviving form of an older one". That
understates it in one direction and misses a limit in the other. The author states the premodern married
priesthood directly and in the past tense, so the record is not back-projecting on its own authority -
but the sentence carries his own footnote to Schipper's <em>The Taoist Body</em>, and the state-pressure
sentence beside it a footnote to Goossaert, and this project has read neither. So the historical claim
arrives at one remove, and those two footnotes name exactly where a session should go to put it on its
own feet. What IS the author's own is modern, and no proportion for any earlier century can come from it.

**The article is read on a library mirror, and the record already knew to say so elsewhere.** The link is
a subscription aggregator's old full-text feed left open on a German foundation's library server, not the
publisher's edition - the kind of link that vanishes, at which point the quotation becomes unreadable and
the note fails the feature-195 rule until it is re-pointed. The entry immediately above it on the same
registry page already carries that disclosure for its own mirror; this one now does too, with the DOI
recorded as the fallback.

**Three smaller ones on the genealogies.** One lineage traces over the provincial line to Fujian, not
Guangdong, which the entry had folded into "Chaozhou country". The `fieldwork is of the 1980s` clause
undersold the source in the record's own disfavor: the Qing evidence is documentary - written family
registers and liturgical manuscripts copied in 1908, 1928 and 1932, with masters dated from the middle of
the eighteenth century - which is why it is the right place to hang the hereditary claim rather than a
weaker one. And the author is candid that those registers carry manifest errors and gaps, which touches
who descended from whom rather than whether the offices descended at all. All three are in the limits now,
along with the honest form of what a handful of lineages can support: that the office DID descend in
families, never a rate.

## R6 - the inventory classified (2026-09-13, FR-002)

The four readers named 695 sentences. This section gives every one of them a disposition, so that the
successor works a list rather than re-reading nineteen pages.

**The classification is a rule plus a named exception list, not 695 hand judgments**, and the rule is
sound because of what the readers were asked. Their brief EXCLUDED, by name, anything about how our map
is drawn, anything recording a decision this project made, and any framing or cross-reference. So the
surviving population is already filtered to claims about the world: the default disposition for an item
the readers reported is therefore `CITE`, and the interesting work is the exceptions.

**The rule.**

- An item the readers marked **HIGH** or **MEDIUM** (including MEDIUM-HIGH) is **`CITE`**. It asserts
  something about how a place was built, farmed, governed or lived in, and a source must be sought.
- An item marked **LOW** or **LOW-MEDIUM** is triaged individually, and every one of them is listed below.
- Two pages are **`NOT AN ASSERTION`** in bulk on the readers' own verdicts: `presentation.html` (zero
  items found in six sections; the page is about how the sheet is drawn and nothing else) and
  `settlements.html` (one item, which restates footnoted setting canon from the section above it).

| batch | HIGH | MEDIUM / MEDIUM-HIGH | LOW / LOW-MEDIUM | items |
|---|---:|---:|---:|---:|
| A - religion-and-death, vegetation, urban-features | 112 | 52 | 7 | 171 |
| B - the four `cities/` pages | 118 | 71 | 14 | 203 |
| C - water, fields, river-cities, hinterland, sizing | 62 | 65 | 26 | 153 |
| D - homesteads, buildings, archetypes, towns, ways, settlements, presentation | 103 | 61 | 4 | 168 |
| **total** | **395** | **249** | **51** | **695** |

### The dispositions

| disposition | count | what it means for the successor |
|---|---:|---|
| `CITE` | **631** | a source must be sought - the long tail, and the successor's whole job |
| `GROUNDS` | 27 | no source is owed; a note in feature 235's form and no reading at all |
| `COVERED` | 16 | a footnote elsewhere already supports it; a cross-reference, not a search |
| `NOT AN ASSERTION` | 21 | nothing owed; two whole pages and a handful of stray lines |
| **worked and CLOSED by this feature** | **21** | the nine roster-hidden claims on `urban-features` and the twelve defects the two readings surfaced |

### The exceptions, enumerated

**`GROUNDS` - no source is owed.** Every one of these is a sentence the readers themselves flagged as
resting on this project's own reasoning, its own maps, or on physical necessity, and each is disclosed as
such in the record's visible text already. They need a note in the closed-list form and nothing else.

- *This project's decision*, self-disclosed at the sentence: the dredging half of the berm (`water`), the
  record's own step from a river bend to a dug ditch, the record's own reading of where a windlass stands,
  the record's own inference about a collector's meeting angle, the bund-against-a-crooked-ditch reading,
  the parcel taking its frame from the canal, the splice behind the in-wall garden, the two-reckoning
  arithmetic for a bed's size (`cities/hinterland`), and the record's own reading that a green bund
  disappears into a green field (`fields`).
- *Physical necessity*: a basin has to be watertight on the side facing its ditch or it drains into it.
- *Measured on our own maps*: the metric restatement of our own drawn ditch widths.
- *Follows from the definitions*, or an economics-of-construction argument the record makes in its own
  voice: the marginal cost of one more terrace bench, nobody building a weir for two acres, a rampart's
  cost scaling with its length, a city being the market of the land that feeds it, the road-driven suburb
  forming where the traffic is.
- *A drawing convention*: what makes a castle read as a castle on the sheet.

**`COVERED` - a footnote already carries it.** Each is a sentence whose support exists, elsewhere, and the
work is a cross-reference rather than a search: the interceptor-ditch practice (footnoted on the same page
under a different question), the moat as storm drain (footnoted on `water`), the two open-reserve shares
and the density claim on `cities/sizing` (all three pointed at `cities/fabric`), the field-margin value
(`vegetation`), the shared transplanting schedule (footnoted two sections on), the `settlements` item, and
the restatements in the `capitals` dimensional-audit table of figures footnoted earlier on that page.

**`NOT AN ASSERTION`.** `presentation.html` entire, `settlements.html`'s single item, and a small number
of lines the readers reported for completeness while saying they owe nothing.

### What this leaves, per page, for the successor

`urban-features` 94 of 103 remaining; `cities/capitals` 125; `homesteads` 58; `buildings` 46;
`water` 55; `fields` 47; `archetypes` 38; `religion-and-death` 39; `vegetation` 29; `cities/government` 27;
`cities/defenses` 26; `cities/fabric` 25; `cities/river-cities` 22; `towns` 16; `cities/hinterland` 9;
`ways` 8; `cities/sizing` 3. `presentation` and `settlements` are closed.

**The order the successor should take them in is not the count.** It is the second shape from R3: the
items whose section roster already admits the figure was never read are DEFECTS a reader meets as
findings, and they are cheap because the search is already done and dated. `urban-features` was worked
that way and nine of its items closed without a single new search.

### R6a - where R6's numbers come from, and a hook that altered a count (2026-09-13)

**The confidence table above is the four readers' OWN stated splits**, taken from the summary section each
of them wrote, not from any parse this session made of their prose. That matters because a peer session
reported the same day that feature 236's house-style hook had silently rewritten one of this session's
shell commands: it splits a Bash payload on `|` without respecting quotes, so the alternation inside a
`grep -oE` pattern was cut into fragments, and an em-dash inside the pattern was "corrected" to a hyphen.
The grep then searched for a character the pattern did not contain, and undercounted with no error.

That command was used to inspect what label FORMS the reports use, and its output was never carried into
R6. Checked rather than assumed: an independent parse, run inside a quoted heredoc with no shell pipeline
and no em-dash, recovers 641 of the 695 labels - 366 HIGH, 228 MEDIUM or MEDIUM-HIGH, 47 LOW or
LOW-MEDIUM. Every class is short by about the same proportion, which is label-format variance in prose
written by four different agents rather than a disagreement with their arithmetic. **The readers' own
totals stand as the table's source**, and the individual triage of the LOW items was extracted by a
heredoc'd regex that contained no em-dash and so was never touched.

The general lesson is worth more than the incident: **a guard that edits a command can change what the
command MEASURES**, and it reports that it corrected the text rather than that it changed a result. Any
count taken from a shell pipeline whose pattern carries a dash or a quoted alternation should be
re-derived before it is written down.

## R7 - the closed list: exactly what feature 238 worked (FR-013)

The successor owns every item the four readers named that this list does not. It is a filter over the
reports, not a reconciliation of counts against prose.

**Closed by disposition, on every page.**

1. **Every bare inline unsourced-class marker in body prose - 142 of them**, across `archetypes`,
   `buildings`, `fields`, `homesteads`, `religion-and-death`, `towns`, `urban-features`, `vegetation`,
   `water`, `ways`, and `cities/capitals`, `defenses`, `fabric`, `government`, `hinterland`,
   `river-cities`. Each is now an absence note at its own assertion. **A reader-report item whose entry
   quotes a marker is therefore closed**, and that is the largest single class.
2. **The nine roster-hidden claims on `urban-features`** (R4's table) and **the five on `buildings`** -
   the Joge plan and its shrines, the light-offender sentence, the west-as-death-direction gloss, the
   staged arrival, and the site figure that brackets the Mode A scale.
3. **The six sections that carried a roster disclosure and no footnote at all**: the lotus area share
   (`archetypes`), the yamen predecessor-veneration practice (`buildings`), the no-subsumed-crown rule
   (`vegetation`, a grounds note), and on `cities/capitals` the sluice duty cycle, the sluice mechanism
   and Edo's moats blooming green.
4. **Every defect the two readings surfaced** - R4a, R5a, R5b, R5e, R5g. Twelve corrections, of which
   two changed what an entry argues.
5. **Two whole pages**: `presentation.html` (zero items) and `settlements.html` (one, restating canon).
6. **The caravan inn**, glyph and page (R2, R2a).

**What the successor owns.** Everything else: the `CITE` items, each needing its own `source-reader`
pass. R6's per-page remainder is the cross-check - `cities/capitals` 125, `urban-features` 94,
`homesteads` 58, `buildings` 46, `water` 55, `fields` 47, `archetypes` 38, `religion-and-death` 39,
`vegetation` 29, `cities/government` 27, `cities/defenses` 26, `cities/fabric` 25,
`cities/river-cities` 22, `towns` 16, `cities/hinterland` 9, `ways` 8, `cities/sizing` 3 - **minus**
whichever of them this list closed, since a marker conversion and a `CITE` disposition can name the same
sentence. The reports are the authority on identity; these numbers are only a size.

**One class deferred by VOLUME rather than by cheapness, and named because FR-012 requires it.** Fifty-one
sections still carry a disclosure on their `Sources:` roster that is now redundant, the label having
moved to a note at the assertion. Rewriting those roster lines to point at the notes is cosmetic - the
reader already meets the honest label in the right place - and it is fifty-one edits with no change of
meaning in any of them. It goes to the successor as tidying, not as a defect.

## R8 - what `record-format` found, reading the pages as a reader meets them (2026-09-13)

The check was pointed at the conversion's own risk: whether moving 142 markers out of prose left any
sentence reading as a flat assertion where a reader can no longer see a hedge without hovering. It read
eight pages in full, four in part, and scanned four mechanically - and said so, which is what makes the
rest of it usable.

**The verdict on the risk itself: the conversion is sound, with ONE loss.** In most places the prose kept
its visible hedge and gained a note, so the reader sees it twice - redundant, never a loss. The exception
is `religion-and-death.html`'s very first assertion: two counts, the Edo parish temples and the Shaolin
monks, stood as flat numbers with their disclosure one paragraph earlier in the `Sources:` line. That is
the paragraph a "See references" click lands a reader on. **A hedge a reader has to go looking for is not
a hedge**, and both now carry notes at their own sentences.

**Three truncated passages, and none of them was this feature's doing.** The check found a sentence
ending on a comma, one ending on the word "and", and a paragraph opening lowercase. Checked against
`origin/main` before fixing: all three predate this work - an earlier edit had moved the tail of a
sentence into an HTML comment and left the prose dangling, twice. They are fixed here under Principle
XIV rather than left because they are somebody else's: the tail restored to visible text in both, the
paragraph given back its capital.

**Two duplicated clauses**, the same sentence stated twice in one paragraph - the signature of a
replacement inserted without the original being removed. Both fixed.

**Fourteen glossary terms added and one variant** - barbican, sally port, chaoguan, dituan, Meireki, the
iroha companies, ri, Akiba, tudi miao, ossuary, well-sweep, skimmer wall, shi, qiandao, and `benjo` as a
variant of the `kawaya` already there, since they are the same building. The glossary is 641 terms.

**Three session notes still visible**, each removed: a "yet" addressed to a future session rather than a
reader, a bare hostname doing no work in prose, and an instruction to whoever draws the next capital.

### R8a - and one finding that did not survive checking

The check reported four references on `archetypes.html` carrying no `id="fnref-N"`, and called the back
links broken. They are not. Each of those four is a SECOND reference to a note whose id sits on its first
occurrence, and an id has to be unique in a document - so the markup is correct and the back link
resolves to the right place. **That is the third agent finding in this feature that did not survive being
checked**, against a great many that did, and the ratio is the argument for both halves of the rule: run
the checks, and read the page before acting on what they say.

### R8b - what the check could not cover, stated because it stated it

It read `fields`, `vegetation`, `water` and `buildings` mechanically rather than as a reader - artifact
greps only. Those four came back clean on every mechanical shape, and their visible markers survive
beside their new notes, so no hedge was lost there. But **their vocabulary is unjudged**, and a hedge
dropped from a sentence that never carried a marker would not show in a grep. `water.html` at 1,100 lines
and `fields.html` at 800 are the two the successor should send back through this check.

### R8c - one browser test failed once and would not do it again

The page check that followed the format work came back red on a single assertion - the lit place card read
its own parchment, `rgb(247, 240, 220)`, where the highlight gold `rgb(255, 200, 61)` was expected - in a
run of 776 at ten workers. **It has not happened since**: the whole check green twice, and the suite run
six more times alone, 18 of 18 each time. Nothing in this feature's delta touches that page - the only
interactive file it changed is `assets/glossary.json`, and the glossary paints no fill.

**What the reading rules OUT.** The same test's earlier assertion passed, so the group genuinely carried
the lit class when the fill was read; the class was not missing. There is no CSS transition on the
property, and the driver loads the page with `wait_until="load"`, so neither an animation nor a pending
stylesheet is the obvious cause. The two reads are separate round trips into the renderer, but both are
synchronous evaluations.

**What it is CONSISTENT with, stated as a candidate rather than a finding.** The gold is applied as
`fill: var(--hl)`, and a custom property that fails to resolve makes the declaration invalid at computed-value
time - the fill then INHERITS, and what it inherits from the placard's group is exactly the parchment the
failure reported. So an unresolved `--hl` and a class that never lit produce the same observed value, and
the assertion as written could not tell them apart.

**What was done, and what was not.** No fix: seven runs could not reproduce it, and a speculative
`var(--hl, #FFC83D)` fallback would hide the mechanism rather than establish it. What the test lacked was
the ability to say WHICH of the two happened, so it now reads the resolved `--hl` and puts it in the
failure message. The next occurrence is a diagnosis instead of a second mystery.

## R9 - the house-style guard corrupted a counting command again, and this time it is reproducible

R6a records this hazard's first appearance: a peer session's house-style hook altered a counting grep
under this feature, the peer landed a fix, and this feature's command became its regression case. **It
happened again on 2026-09-13**, to the census that sizes feature 242, and the second instance is
cleaner than the first because it reproduces on demand.

**What happened.** The census splits each reader report into items on a pattern containing the report's
own em-dash. The guard rewrote that dash to a hyphen inside the `re.split()` call, so the pattern
matched nothing in three of the four reports; the run reported 39 items where the true count is 695.
Nothing failed. The only reason it was caught is that three reports returning exactly zero is not a
believable answer.

**The mechanism, confirmed against the CURRENT code in the mirror** (not the copy in this clone, which
is behind): calling `_hm_house.report` with a payload whose command is

    parts = re.split(r'\n(?=\*\*R\d+\*\* <em dash> )', txt)

returns `updatedInput` with the dash replaced, and an `additionalContext` reading *"What the command
only NAMES was left as typed: a search pattern, a path, a code span..."* - which is the exemption this
very payload should have taken. The dash is inside a raw-string regex literal in a heredoc: text the
command MATCHES WITH, never text it writes. The guard's exemptions already cover a searcher's segment,
a regex alternation and a dash in a character class; what they do not cover is a pattern passed to a
regex function in an interpreter heredoc, which is how this project does every census it writes.

**It is fixed here** (`scripts/_hm_house.py`). A first draft of this section deferred it, and every
reason it gave was false, which an independent check established rather than the session: feature 239
is complete with no open task, no clone holds an unlanded edit to that file, `make hookbench` is in
THIS clone at line 998 of the skill Makefile, and the concurrency doctrine allocates feature NUMBERS
under a lock - it says nothing about owning a source file. Principle XIV's only exception is an
overhaul or a giant architectural change, and a one-clause exemption is not that.

**The fix.** A string handed to a regex constructor is a pattern the command MATCHES WITH, never text
it writes, so `_REGEX_LITERAL` holds it as a mention exactly as a searcher's segment is held. The
searcher rules already covered a pattern reaching a regex through `grep` or `sed`; what had nothing was
a pattern reaching one through an INTERPRETER, because an interpreter's heredoc is prose by default.

**What it cost, measured rather than asserted.** `make hookbench GUARD=house-style AGAINST=origin/main`
replays the frozen 560-command window: **one** verdict moves, corrected to silent. That one is the
argument for the fix rather than a cost of it - a peer session's command building
`re.compile(r'\b\w*(cruell|duell|colour|honour|...')` to FIND British spellings, whose search pattern
this guard was rewriting into the American ones. The same defect, in another session, in the wild.
The exemption is proven to fire the way this project requires: removing it from the held-ranges tuple
turns the selftest red.

**The general lesson, which is the part worth keeping**: a guard that silently edits a command can turn
a measurement into a plausible wrong number, and a plausible wrong number is worse than a crash. Every
census this project writes should assert against something it already knows - this one refuses to
report unless it reproduces all four of the reports' own stated totals, which is what would have caught
the corruption on the first run instead of the third.

### R9a - a second non-reproducing gate failure, and what the two have in common

The gate that vouches for the merged tree failed once on
`test_every_shipped_hamlets_lane_ends_reach_something[inashiro.json]` and was green on the next run
with nothing changed between them.

**What rules out a real regression, rather than what merely suggests it.** The baseline on unmodified
`origin/main` in a detached worktree passes; the test passes standalone in this clone; the second full
gate is green. Those three only establish that it does not reproduce. The fourth is the one that
settles what it was: **`git status` showed no pool manifest changed after the failing run.** The test
reads a manifest as static data, so if the gate's pool phase had rolled a different Inashiro the file
would have been dirty against HEAD - it was clean, which means the manifest the test rejected was
byte-identical to the one it accepts now. A deterministic test cannot judge identical bytes two ways,
so the failure was not about the map at all.

**The shared factor with R8c.** Both failed once inside a full ten-worker gate, neither reproduced
alone or on re-run, and in both the failing assertion was reading something another part of the same
run produces - a manifest the pool phase writes, a computed style the page applies. Neither is
diagnosed. On a third, take the cheap distinguishing measurement FIRST rather than re-running until
green: for the lane test that was one `git status`, for the placard the resolved value of the custom
property. That is what separates "the artifact is wrong" from "the reading of it was".

### R9b - this section was claimed by a commit message before it existed

R9a was written into a command that also carried a `git commit -m`, the commit guard refused the whole
command for the two-message form, and only the commit half was re-run. So commit 62459ee3 says
"Recorded beside R8c's browser flake" while changing nothing but two log files, and the record it
describes was absent until now.

**This feature already recorded that exact failure once**, at R3: a guard refusal ate a research
section, the commit half was re-run alone, and later sections landed on top of a section that never
existed. Writing the lesson down did not prevent the repeat, which is the useful part of saying it
twice. The mechanical form of the rule is: **when a guard refuses a command, re-run the WHOLE command,
never the half that was not the reason for the refusal** - and the check that would have caught both is
to grep for the section heading after committing it, which costs nothing and is the only thing that
distinguishes a record from a commit message about a record.

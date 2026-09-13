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

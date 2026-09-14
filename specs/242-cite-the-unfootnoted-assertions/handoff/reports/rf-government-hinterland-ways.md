## Report: three research pages, their citations pages, and the feature‑242 registry entries

Read as the reader meets them (comments and tags stripped). Nothing was edited. Line numbers are from the files as they stand.

Paths read:
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/cities/government.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/cities/hinterland.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/ways.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/cities/government.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/cities/hinterland.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/ways.html`
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/SOURCES.html` (355 entries carrying `<!-- READ 2026-09-14 by a source-reader (feature 242) -->`, lines 411‑2184)
- glossary: `/diagram/.clones/diagram-research/.claude/skills/diagram/l7r/diagram/interactive/assets/glossary.json`

**Standing note on the glossary.** It is now very complete for these pages: `kido`/`ward gate`, `nagaya`, `nagayamon`, `daozuofang`, `banfang`, `gongxiefang`, `yayi`, `houzhaofang`, `komono`, `chugen`, `degawari`, `kumi-yashiki`, `jokamachi`, `buke-chi`, `hanko`, `bugeijo`, `machi-dojo`, `koku`, `ken`, `shaku`, `kan`, `ryo`, `shi`, `mu`, `li`, `ri`, `tsubo`, `hari-ma` (梁間), `hem`, `toe`, `baulk`, `offtake`, `scour`, `sill`, `abutment`, `strip footing`, `riprap`, `gabion`, `glulam`, `itabashi`, `dobashi`, `jetty`, `tread`, `guanxiang`, `yakata`, `flophouse`, `sally gate`, `night soil`, `well-sweep`, `windlass`, `levee`, `natural levee`, `backswamp`, `alternate attendance`, `hatamoto`, `shoin`, `kawata`, `lifang`, `zicheng`, `luocheng`, `yacheng`, `kuru…`-family layout terms (`rinkaku`, `renkaku`, `teikaku`), `mitochigai`, `kurayashiki`, `monzen`, `teramachi`, `sogamae`, `towpath`/`qiandao`, `tulou`, `Qimin Yaoshu` (matching is whole-word and case‑insensitive, so "Qimin yaoshu" still gets its tooltip). What is below is what it does **not** cover.

---

## A. `research/cities/government.html`

### §"Where does a province's government stand in its city?" (l.18)

**VOCABULARY**
- **`stroke`** - l.24: *"the governor's compound, the six ministry offices and a samurai neighborhood all stand in the city's INTERIOR, inside the rampart and clear of the wall's stroke and its moat."* This is the drawn line's width, not anything on the ground. DEFINITION (drafted from this page's own usage and `presentation.html`'s convention language): "The width of the line a map draws a feature with; ground 'clear of the stroke' is ground the drawn line itself does not cover." Alternative: rewrite in the reader's terms ("clear of the wall and its moat").

**SESSION NOTE** - none (Grounds/Evidence are in comments, l.19‑21).
**HISTORY** - none.
**DEFECTS** - none.

### §"What stands between the temples in a temple neighborhood?" (l.25)
VOCABULARY none; SESSION NOTE none; HISTORY none; DEFECTS none.

### §"Where do a city's samurai live, and how many of them are drawn?" (l.32)
VOCABULARY none missing; SESSION NOTE none; HISTORY none; DEFECTS none.

### §"Is the samurai quarter walled, or only gated?" (l.39)
VOCABULARY none missing (`extramural`, `ward gate`, `curtain` are all defined).
**SESSION NOTE** - none. **HISTORY** - none. **DEFECTS** - none.

### §"Which way does a ward gate face?" (l.47)
VOCABULARY none missing. SESSION NOTE none (the second measured city sits in a comment, l.52). HISTORY none. DEFECTS none.

### §"Where does the gate watch stand?" (l.54)
Clean: the three failed approaches and the footprint-judging note are both HTML comments (l.61, l.62), which is exactly right.

### §"Martial training is an URBAN institution" (l.63)

**DEFECT (markup / reader-facing)** - l.66, the `Sources:` roster is broken in half by two sentences of prose and carries footnote marks:
> *"…`genbukan-jawiki` (the disciple count is contested, ~3,000 against 6,000+, and no readable page gives one). The "boom of 1830-1860" range is not on any page read; it is drawn from the three founding dates and late-Edo growth, `kenjutsu-jawiki`, `edo-enwiki`, `wuxue-zhwiki`, `kotobank-machidojo`"*

A reader sees a sentence ending in a period followed by a comma-separated list of keys, so the last four works read as part of that sentence. Two separate things to separate: the honest label about the boom range belongs in the body beside the assertion it qualifies (where footnote 5/6 already sit), and the roster should be keys with their parentheticals only. Also in this roster: `<sup class="fn">1</sup>` and `<sup class="fn">2</sup>` are attached to roster entries rather than to assertions, which is the one place the feature‑194 form does not put a footnote mark.

**VOCABULARY**
- `武芸`, `演武場`, `藩地` (l.66, l.68) - each is glossed in English immediately beside it ("martial arts (武芸)", "the training hall (演武場)", "the domain's own territory (藩地)"): **defined inline**, nothing owed.

**SESSION NOTE** - none owed. (*"There is none."* at l.69 with the GM's question quoted is the decision the record owes its reader; the reconstruction's provenance is already a comment at l.69/70.)
**HISTORY** - none visible; the 2026‑08‑08 correction and the transferable lesson are both comments (l.70, l.76). This section is the model for the rest.

### §"Servant housing in the samurai ward - servants are drawn as WALLS, not as houses" (l.77)

**VOCABULARY**
- **`property 2` / `property 1`** - l.93: *"the setting's own budget notes give a provincial city 120 servant families, of which **72 are attached to samurai households** (30 to wealthy samurai at property 2, 42 indentured to non-wealthy at property 1) against **60 samurai families**"*. A reader has no way to know this is the GM's economic model's wealth tier. DEFINITION (drafted from the sentence itself): "A household's wealth rank in the setting's own economic model: property 2 is a wealthy household, property 1 a household of modest means." Either a glossary term or an inline gloss would do.

**SESSION NOTE**
- l.97: *"drawing the range alone - a long thin building hard on the street line - carries the same read at 3 ft/px without introducing walled compounds into the ward."* `3 ft/px` is the engine's scale notation; the record's own rule for a spec paragraph is real feet visible with the pixel figure in a comment. PROPOSE `comment`: the sentence reads whole as *"…carries the same read at the city map's scale without introducing walled compounds into the ward."* with `<!-- 3 ft/px -->` beside it.

**HISTORY (borderline - keep, with one clause reconsidered)**
- l.93: *"What the GM saw on Minami (2026-08-02) - "more commoner houses in the samurai neighborhood" - was the ARRANGEMENT: a rank of detached servant houses unattached to any samurai household reads as exactly what the fence exists to exclude."* USEFUL and kept: the GM's observation, its date, and the rule it drove. The per-map measurement is already in a comment (l.94), which is right. The one thing to weigh is whether "was the ARRANGEMENT" is describing a map state that no longer exists; if the arrangement has been fixed, the reader-facing half is just the rule.

**DEFECT (a claim standing beside its own refutation)**
- l.88: *"Sendai and Hachinohe placed them at the highway ends (on no page read; Hachinohe's page puts one ashigaru quarter on the east side)."* The sentence asserts a placement and then says no page read supports it and that the page consulted says something else - a CONTRADICTED fetch verdict rendered as prose. As it stands the reader is told a fact and then told it is wrong. PROPOSE: state what the page does say (*"Hachinohe put one ashigaru quarter on the east side"*), and drop or comment the unsupported "highway ends" claim.

### §"Samurai and commoner ground were zoned apart by law" (l.100)

**DEFECT (untranslated foreign text in visible prose)**
- l.103, the Sources roster: *"`jokamachi-jawiki` (侍町 by rank around the castle, 町人地 outside it, 寺町 at the rim)"*. Three Japanese words with no English beside them, in the one line the modal reads. The body sentence at l.105 does it correctly (*"samurai ground (武家地) and townsman ground (町人地)"*). PROPOSE: *"(the samurai town (侍町) ranked by distance from the castle, the townsman ground (町人地) outside it, the temple town (寺町) at the rim)"*.

**Heading form (format, not markup)** - three headings on this page are statements rather than the question a reader would ask from a map: l.63 *"Martial training is an URBAN institution"*, l.77 *"Servant housing in the samurai ward - servants are drawn as WALLS, not as houses"*, l.100 *"Samurai and commoner ground were zoned apart by law"*. The other six are questions. Flagged as an observation for the session; anchors are inbound-linked, so this is not a free rename.

---

## B. `research/cities/hinterland.html`

### §"Gentry estates are DISPERSED, not clustered at the wall" (l.19)

**DEFECTS**
- l.24‑26: the whole finding is wrapped in a one-item `<ul><li>…</li></ul>`, so a reader meets a single lone bullet carrying four bold run-ins and six footnotes. Every other finding on the page is a `<p>`.
- Heading is a statement, not a question (same class as the government page).

VOCABULARY none missing. SESSION NOTE none visible (the `leftover` / `not re-read` note is a comment at l.23 - correct). HISTORY none visible.

### §"Why is a city ringed by farmland on every side?" (l.32)

**SESSION NOTE (two mild ones)**
- l.40: *"Each field is a whole water chain rather than a colored polygon: a tap that sits ON the water and is derived from the watercourse's own line rather than picked by eye, … a declared source and a declared drain…"* - "declared" is the generator's word for a registered feature. PROPOSE `drop` the word: *"…a source and a drain the map states…"*, or leave as is if it reads as plain English to you.
- l.42: *"the map wants about seven farmhouses for every 3,000 ft of that boundary"* - "the map wants" is a check's voice; a reader-facing spec would say *"the map draws about seven farmhouses per 3,000 ft"*.

VOCABULARY none missing. HISTORY none visible - the whole "ringing a single capital took the better part of a working day" narrative and the two performance traps are correctly inside the comment at l.38.

### §"Does the moat feed the fields, or do the fields drain into it?" (l.43)
Clean on all three classes; pixel figures are in comments (l.49‑51).

### §"What stands outside a city gate?" (l.52)

**DEFECT**
- l.56: `<p><strong>Sources:</strong><a href=…>` - no space after the colon, so the reader sees *"Sources:chang-morphology-walled-capitals (what grew outside a gate: …)"*.

**SESSION NOTE**
- l.58: *"no city on the sheet has one today, and a city that declared one would keep its sally gates out of the list the market rule reads."* "the list the market rule reads" is the check's data structure. PROPOSE `comment` the second clause; the sentence reads whole as *"A purely military sally gate … carries no market, no flophouse and no caravan cluster; no city on the sheet has one today."*

HISTORY none. VOCABULARY none missing.

### §"Does a city farm inside its walls?" (l.59)

**DEFECT (broken markup - the clearest one in the three pages)**
- l.67 begins a paragraph with **no opening `<p>`** and closes with `</p>`:
> *"A field's fan has a hand, and both hands were real.<sup>10</sup> The pocket an in-wall field sits in is rarely symmetrical … and the fan fills the ground downhill of it.</p>"*

Rendered, this text joins the tail of the preceding paragraph (l.66) and the stray `</p>` closes nothing a browser opened. Everything else on the page is a well-formed `<p>`.

**VOCABULARY**
- **`metrology`** - l.68: *"Turning a sixth-century pace into feet needs a metrology this record has not read; on the two common reckonings it comes out at roughly 5 by 10 ft…"* DEFINITION (drafted from this sentence and from the hinterland citations page's own limit note on `qimin-yaoshu-zhongkui`): "The study of what a period's own units of measure actually were; a bu or a mu has no single value in feet, so a figure cannot be converted without a source for the units of its own century." (The page's honest label - that it has not read one - is correct and stays.)

**SESSION NOTE** - none. **HISTORY** - none.
- Minor note: l.66 *"Both halves of that are attested and the join between them is this record's own."* uses the Evidence vocabulary ("attested") in prose. It reads as ordinary English here, so no change proposed; recorded only because the word is a field name elsewhere.

---

## C. `research/ways.html`

### §"How far past the bank does a bridge land?" (l.19)

**VOCABULARY**
- **`girder`** - l.24: *"Its girder bears on an abutment sill set back from the channel edge…"* (`abutment`, `sill`, `scour`, `strip footing` are all in the glossary; `girder` is not.) DEFINITION (drafted from this page and `ritter-timber-bridges`'s write-up): "The main beam of a bridge, which carries the deck and rests at each end on the abutment."
- `obliquity` (l.25) - the next clause explains it (*"Where a way crosses a watercourse at an angle…"*): **defined inline**.

**HISTORY**
- l.25: *"…which is how the capital's east deck over the diagonal river came to have 0.0 ft of landing at its worst corner, the deck the GM saw."* USEFUL and kept: the GM's 2026‑08‑09 ruling, the obliquity mechanism, and the rule that the four real corners are what is tested. The past state of one map, and the engine-formatted `0.0 ft`, are the history half. PROPOSE: *"The crossing is solved for that angle exactly, and the test is applied to the deck's four real corners rather than to the ends of its centerline, because a corner is what runs out of bank first."* with the capital's measured corner in a comment beside it.

SESSION NOTE none visible (Grounds/Evidence are comments, l.21‑22). DEFECTS none.

### §"What vehicle used a village lane, and where could the lane run?" (l.28)

**VOCABULARY**
- **`post-horse system`** - l.34: *"on the highways their use was forbidden to the very end of the shogunate - to keep the post-horse system alive, the fear being that more vehicles would mean fewer horses."* DEFINITION (drafted from this sentence and the `shukuba-jawiki` registry entry): "The relay of horses and porters kept at every post station for official traffic, which a highway full of carts would have starved of animals."
- **`litters`** - l.33, inside the quoted passage: *"pedestrians, porters with carrying poles, pushers of wheelbarrows, and men carrying litters."* DEFINITION: "A covered seat or frame slung between poles, carried on men's shoulders - the way a passenger traveled where no vehicle could go." (The wrap adds no characters to the quote.)
- **`footslope`** - l.37: *"the wet toe is only as wide as the ground the fan waters …, leaving dry footslope at both of its lateral ends."* (`toe` is in the glossary; `footslope` is not.) DEFINITION (drafted from `water.html`'s fan sections): "The gentle ground at the foot of a slope, below the hill and above the wet valley floor."
- **`seed`** - l.36: *"it fought the homestead packing on every seed of that map"*. DEFINITION (drafted from the project's own usage): "The number a map is generated from; the same seed always produces the same settlement, and a different seed a different one." Note this word also carries a SESSION-NOTE reading - see below.

**SESSION NOTE**
- l.36: *"The alternative - routing a detour around the foot of the staircase - was drawn and measured, and it fought the homestead packing on every seed of that map, while the hem-edge stop left the known-clean packing untouched."* The declined alternative and its measurement are exactly what the record owes a reader; "the homestead packing", "every seed", "known-clean packing" are the generator's terms. PROPOSE a rewrite that keeps the decision: *"The alternative - routing a detour around the foot of the staircase - was drawn and measured, and it disturbed the farmstead layout on every map it was tried on, while the hem-edge stop left it untouched."* with the engine words in a comment.
- l.35: *"…at the hamlet's scale of one foot to the pixel…"* - borderline. The scale is arguably a fact about the sheet the reader is looking at; recorded for your judgment, no change proposed.

HISTORY - none. DEFECTS - none.

### §"What is a plank bridge, and what is it for?" (l.42)

**HISTORY**
- l.49: *"That last rule came from a census rather than from a single bad plank. Asked about one useless crossing on 2026-07-22, this project counted them across the whole pool and found the defect everywhere: the drainage toes of the water-first maps and the diagonal edge-drains along every field's outer boundary all carried planks stepping straight into swamp or scrub. The rule clears them pool-wide, while every field-to-field, dry-to-wet and settlement-to-field crossing stands. A ditch running along a field's outer margin with nothing on its far side now carries no plank at all…"*
  USEFUL and kept: the GM's question of 2026‑07‑22, the rule (both banks must land on ground worth crossing to), and its consequence for an outer-margin ditch. HISTORY that goes: what the maps used to draw, that the defect was "everywhere", that the rule "clears them pool-wide", and the "now" (the per-map counts are already correctly in the comment). PROPOSE: *"Both banks must land on ground worth crossing to, and the rule was set from a census of every plank on every map rather than from one bad crossing: the drainage toes and the diagonal edge-drains are where a plank has nothing on its far side. A ditch running along a field's outer margin with nothing beyond it carries no plank: nothing to cross to needs no crossing."*

VOCABULARY - none missing. SESSION NOTE - the placer/check-read-the-same-record note is already a comment (l.49), correct. DEFECTS - none.

### §"Where does a village's freight go? Onto the water - but not onto a canal" (l.54)

**VOCABULARY**
- **`waystation`** - l.61: *"tens of thousands of miles of Imperial road with thousands of staffed waystations, maintained by corvee"*. DEFINITION (drafted from the `shukuba-jawiki` and `yizhan-zhwiki` registry entries): "A staffed post on a trunk road where couriers and officials changed horses and travelers found lodging."
- The Great Clan names (`the Lion`, `Crane`, `Dragon`, `Unicorn`, `Scorpion`, l.60) and the two named rivers are setting proper nouns; the glossary defines `Rokugan` only. Optional: a one-line gloss per clan is probably below the bar for a casual L5R reader, so no definition drafted.

SESSION NOTE - none (the two `Evidence: setting-canon` markers are comments, l.60‑61). HISTORY - none. DEFECTS - none.

### §"Is the bridge where the road actually crosses the water?" (l.64)

**HISTORY**
- l.70: *"Why it had happened is worth keeping, because it is the shape of the failure rather than one map's mistake. The ring road was not counted as a way that carries traffic and the cargo canal was not counted as a watercourse, so the automatic pass could not see that crossing at all, and both cities had their deck placed by hand at design coordinates. Hand-placed coordinates then drift: when the first city's ring road was re-derived from its own budget the deck stayed where it had been typed, ending about 51 ft and 39 degrees off its crossing, and the second city's about 45 ft and 24 degrees off."*
  USEFUL and kept: the GM's 2026‑07‑27 quotation (l.69), the mechanism ("a hand-placed deck drifts when the way it belongs to is re-derived"), and the tolerance the two measurements produced. HISTORY that goes: that it *had* happened, on which two cities, and what each was off by - the two offsets are the evidence for the tolerance, so they can stay if they are attached to the tolerance rather than to the incident.
  PROPOSE: *"A deck typed at design coordinates drifts away from its crossing as soon as the way it belongs to is re-derived - by tens of feet and tens of degrees, which is what a reader sees as a road running through the water. So a crossing is solved from the water and the way rather than placed by hand."* with the per-city offsets in a comment beside it (the second city's figures are already half in a comment).
- l.71: *"The tolerance now applied comes from measuring the difference."* - "now applied" implies a previous tolerance. PROPOSE `drop` the word: *"The tolerance comes from measuring the difference."*

SESSION NOTE - none owed; the drawing consequence at l.71 is already a comment. VOCABULARY - none missing. DEFECTS - none.

---

## D. `research/citations/cities/government.html` (227 lines)

The works section here is DERIVED by `make citations` from `SOURCES.html` - every item below in the works half must be fixed in the registry entry, not on this page.

**DEFECTS - duplicated quotations (systemic, from the feature‑202 conversion)**
1. **fn‑13 (l.170)** - the same English passage is printed **twice, back to back**, the second copy with curly quotes and an em-dash: 「The nagaya-mon owes its name to its form … who came and went.」「The nagaya-mon owes its name to its form, which resembled a traditional Japanese nagaya (literally “longhouses”—a term applied to…)…」 The reader reads the note twice.
2. **fn‑20 (l.177)** - the same English sentence quoted twice, joined by *"and (H30-00647)"*. If two pages carry identical text that is worth one clause saying so; as printed it reads as a duplication.
3. **fn‑9 (l.166)** - the translation is given, then a second English rendering of the same material follows, whose `original:` covers only its last sentence. Mismatched pair.
4. **The trailing-paraphrase pattern** - fn‑1, fn‑2, fn‑5, fn‑7, fn‑10, fn‑11, fn‑14, fn‑19, fn‑21, fn‑25 each quote the English translation in 「」 and then repeat the same English in a trailing parenthesis. Example, fn‑2 (l.159): three 「」 translations, then *"(1773 (An'ei 2), Momonoi Naoyoshi (the first Momonoi Shunzo) opened [the Shigakukan] at Nihonbashi Minami-Kayabacho; autumn 1822 …)"*. One class, ten notes.

**DEFECTS - other**
5. **`((English.))`** - double parentheses in fn‑13, fn‑16, fn‑17, fn‑18, fn‑20, fn‑26, fn‑33 (e.g. l.173: *"…either 165 or 230 m². ((English.))"*).
6. **Markdown backticks inside HTML** - fn‑17 (l.174): *"Also `bukeyashiki-wiki`: 「Samurai residences of the senior-retainer class…"* and fn‑19 (l.176): *""By default" (terraced as the norm) is on `jta-ashigaru-kaga`:"*. The backticks render literally, and the key is not a link here while every other key on the page is.
7. **Notes out of order** - fn‑40 (l.196) is printed **before** fn‑39 (l.197) in the ordered list.
8. **Entity-encoded text in the works section** - l.91: `<p>&#32500;&#22522;&#30334;&#31185; &#22235;&#21512;&#38498; (…)</p>` (the `siheyuan-zhwiki` citation line, entity-encoded where every other line is plain text), and l.93 carries `project&#8217;s` / `article&#8217;s` - curly apostrophes in this project's own prose. Source of the defect: the registry entry at `SOURCES.html:3836‑3839` (a 2026‑09‑12 entry, not one of the 09‑14 set).
9. **`m2`, `km2`** written flat where the rest of the page writes "square meters" (fn‑16 l.173 has `m²`, fn‑37 l.194 has `0.94 km2`).

**SESSION NOTES (visible on a page the reader opens from a hover)**
- fn‑1 (l.158): *"NOTE: 演武場 appears on the page only in the per-domain list rows … - there is no prose sentence listing 演武場 as a standard facility."* The finding (the drill hall is not stated as standard; the list rows are the evidence) is the reader's; the `NOTE:` prefix and the "no prose sentence" bookkeeping are the session's. PROPOSE: keep the substance, drop `NOTE:` - *"The page names a drill hall only in its per-domain rows … so a drill hall on every school is a generalization."*
- fn‑7 (l.164): *"NOTE: 下女 (gejo) does not appear on the page; 中間 is described 「…」 with no separate housing sentence."* Same shape; `comment` the "does not appear / no separate housing sentence" bookkeeping or restate it as the limit.
- fn‑11 (l.168): *"NOTE (finding, not contradiction): the family name is 菅沼 = SUGANUMA, not "Suginuma"; and the page's meter conversions are swapped against its own ken figures (28 ken = ~51 m, 32.5 ken = ~59 m) - the file's ~167 x 194 ft follows the ken figures correctly."* Three things at once: a HISTORY item (the record used to romanize it "Suginuma"), a session note (`NOTE (finding, not contradiction)`, "the file's"), and one genuinely useful reader fact (the source page's own metric conversions are swapped, so the feet figure follows the ken). PROPOSE: *"The page's meter conversions are swapped against its own ken figures (28 ken is about 51 m, 32.5 ken about 59 m); the feet figure follows the ken."* - the romanization correction goes to git.
- fn‑6 (l.163): *"the page gives no disciple count; what it does say: … The 3,600 figure is on no page read and matches neither contested synthesis figure (the Sources line already says so)."* The honest label stays; *"(the Sources line already says so)"* is a note to the next editor - PROPOSE `drop`. The `SUMMARY-ONLY` / `NOT FOUND` verdicts are correctly inside the comment.
- fn‑22 (l.179): *"…refuses automated fetches and was not asked a second time…"* - `comment` the fetch-attempt bookkeeping; *"searched 2026-09-12: the Chinese encyclopedia that carries the Pingyao clerks' lodging of 1619 and the Neixiang west line refuses automated fetches, and no other readable page names either building"* reads whole.
- fn‑38 (l.195): *"Two of the four queries were refused by the search host and are recorded as unrun; the likely carrier is a municipal cultural-property survey of a named quarter."* The date and what was tried are the honest label and stay; "recorded as unrun" and the pointer to what would settle it next are instructions to a future session - PROPOSE `comment`.

**HISTORY (visible)**
- fn‑32 (l.189): *"(7.3 m = 24 ft, not 21 ft.)"* - a correction of a figure that no longer appears anywhere a reader can see. PROPOSE: *"(7.3 m is 24 ft.)"*, with the correction in git.
- fn‑33 (l.190) and fn‑34 (l.191) keep their history inside comments - correct, and the model for the two above.

**VOCABULARY** (all inside quoted passages, which still counts; none is in the glossary)
- **`yoriai-seki`** - fn‑11/fn‑31: 「The Suganuma family was of yoriai-seki rank…」 DEFINITION (from the note's own context): "A rank band of a domain's retainers, here a house assessed at 1,000 koku after 1686."
- **`kumi-chi`** - fn‑14: 「ashigaru (foot soldiers) lived in designated residential areas called kumi-chi.」 DEFINITION (from `kumi-yashiki` in the glossary and this quote): "The ground assigned to one unit of foot soldiers, where the men of that unit lived together."
- **`machi-kido`** - the `kotobank-kido` write-up (registry l.483, derived onto other citations pages): *"it gives the machi-kido's hours"*. DEFINITION: "The wooden gate that closed a town block's street at night, as against a gate in a castle's own works."
- The era names used without explanation in the notes: **`An'ei`**, **`Bunsei`**, **`Tenpo`**, **`Kanbun`**, **`Jokyo`** (fn‑2, fn‑11, fn‑31, fn‑41, fn‑44). The glossary already carries Genroku, Keicho, Kyoho, Meireki and Wanli, so these five are the gap. Each definition is one clause: the years and what the reader needs from them (e.g. "Bunsei: the Japanese era 1818‑1830, when the three great Edo dojos were founded").
- **A glossary MISMATCH to watch**: fn‑9 (l.166) says 「the yearly stipend was about 2 ryo 2 bu」. `ryo` is defined, but the glossary's `bu` is *"a unit of land area the size of a tsubo"* - so the reader hovering `bu` in a money phrase gets a land measure. Either widen the `bu` definition to name both senses or leave the money sense unwrapped.

---

## E. `research/citations/cities/hinterland.html` (111 lines)

**DEFECT - a note that prints every quotation twice**
- fn‑3 (l.84): the whole note is doubled. It gives 「The streets outside the city gate and the nearby area.」 and 「The main street outside the city gate.」 with their originals, and then repeats both in straight quotes, then gives 「In antiquity, the lodging-houses (亭舍) near the city walls.」 followed by *- "in antiquity, the lodging-houses near the city wall" -* and the Ming-shi example likewise twice. Four passages, eight printings.

**DEFECT - 「」 used around English that is not a quotation**
- fn‑21 (l.102): *"the 2-15 mile band, 「isolated」, the dispersal and the near-city retreats are this page's"*. The corner brackets are the record's marker for a quoted passage; here they wrap one English word of the record's own.

**SESSION NOTES** - none visible; every fetch verdict and partial-support judgment is inside an HTML comment (fn‑1 l.82, fn‑2 l.83), which is exactly right.
**HISTORY** - none visible.
**VOCABULARY**
- **`Northern Wei`** - the `qimin-yaoshu-zhongkui` write-up (l.57): *"its limits are that it is Northern Wei north China, far earlier than the Ming and Edo anchor"*, and again *"a Northern Wei bu is not a Ming bu"*. DEFINITION (drafted from that write-up): "The dynasty that ruled north China in the fifth and sixth centuries, when the farming treatise this record quotes was written - centuries earlier than the Ming and Edo the maps are drawn from."
- `natural levee`, `backswamp`, `guanxiang` all defined; nothing else owed. (Note this write-up also carries the one useful reader warning on units - *"converting with a later metrology would be positively wrong rather than merely unsupported"* - which pairs with the `metrology` term proposed above.)

---

## F. `research/citations/ways.html` (123 lines)

**DEFECT - broken sentence in the works section (fix in the registry)**
- l.29, the `toyama-1988-road-undevelopment` write-up: *"It is the direct evidence for the countryside our lanes are drawn for - no horse-drawn carriage at all before Meiji, inhabitants on foot or on horseback, goods on a horse's back - It is also precise where the general account is loose:"* - a dash followed by a capitalized new sentence with no closing punctuation. This text is derived from `SOURCES.html`; the edit belongs to that entry.

**DEFECT - duplicated quotation**
- fn‑22 (l.115): the chuma passage 「In chuma one man ordinarily led three or four horses, and carried around 100 kan of goods at one time.」 is printed twice with the same original, once as the quote and once inside the trailing gloss.

**DEFECT - 「」 around the record's own English**
- fn‑26 (l.119): *"the one 「one horse wide」 figure read is an English packhorse bridge under 6 ft"*.

**SESSION NOTES** - none visible; the three feature‑238 conversion notes at fn‑19/20/21 (l.112‑114) are inside comments, correct. The absence notes themselves (*"searched 2026-09-13: the sentence rests on general reading and no source was cited for it when it was written"*) are the honest label and stay.
**HISTORY** - none visible.
**VOCABULARY** - all quoted technical terms are covered (`riprap`, `gabion`, `glulam`, `strip footing`, `scour`, `kan`, `ken`, `shaku`). Two uncovered, both inside quoted passages:
- **`stringers`** - fn‑12 (l.105): 「…various simple structural systems including rail cars, steel I-beams, and timber stringers.」 DEFINITION: "The lengthwise beams of a bridge that carry its decking."
- **`nawate`** - fn‑23 (l.116): 「Those that also serve as a path for going round the paddy fields are called azemichi, or nawate.」 `azemichi` is defined; `nawate` is the same thing under another name - PROPOSE adding it as a **variant of `azemichi`** rather than a new term.

---

## G. `research/SOURCES.html` - the 355 entries marked `READ 2026-09-14 (feature 242)`

Scope note: by the GM's own carve-out (spec 209 D6) the registry is **not** under the session-note and no-history rules - its `READ` markers are read by the link classifier and its entries are the record of the search. It *does* load the glossary, and since feature 211 both write-ups are DERIVED onto the top of every citations page that cites the work, so a reader meets them. I therefore report vocabulary and defects, and only note the two session-shaped sentences a reader would trip over.

**DEFECTS**
1. **l.922 (`manzello-2019-firebrand`)** - garbled sentence, visible: *"A peer-experimental studyed open-access review in Frontiers in Mechanical Engineering of how firebrands are generated…"* Reads as a failed substitution over "peer-reviewed". (The same entry's citation line at l.921 names Hedayati et al. under a key called `manzello-…`; keys are opaque, so that is a note rather than a defect.)
2. **l.947 (`japanknowledge-jishibai`)** - two problems in one sentence: a missing relative pronoun (*"The article on provincial and village kabuki in the kabuki encyclopedia JapanKnowledge serves openly (…)"* wants "that JapanKnowledge serves openly"), and a parenthetical addressed to a session rather than a reader: *"(the page was read in full on 2026-09-14 while the site around it is subscription-gated; a reader who meets a paywall should say so)"*. The second clause is an instruction to whoever reads next.
3. **l.1923 (`fengshuilin-zhwiki`)** - untranslated Chinese in visible prose with no English beside it: *"the back-hill 龍座林 planted against wind and wash"*. Everywhere else in the marked set a foreign term is glossed.
4. **l.1632/1634 (`genge-jawiki`)** - the entry names the plant **genge** in "What it is" and **renge** in "Used for" (*"renge as the paddy's winter green manure"*), with nothing saying they are the same plant.
5. **l.531 (`jining-museum-qiandao`)** - mangled dash run in the title: *"浙东运河古纤道 -  - 秋水长堤 通古鉴今"*.
6. **l.1608 (`mu-land-enwiki`)** - flat exponents and a mixed fraction in visible text: *"the 1915 mu of 614.4 m2 and the 1930 metric mu of 666 2/3 m2 (0.1647 acre)"*, where neighboring entries write "square meters".
7. **Foreign titles are handled inconsistently.** Most marked citation lines give the work's title in its own script only (l.511 *"第46回【構造】お城の塀や石垣はどうして折れ曲がっているの？"*, l.601, l.606, l.646, l.661, l.666…), while a few give a translation beside it (l.441, l.471, and `subai-ancient-city-sites` on the citations page marks its title as translated). A title is a name rather than a quoted passage, so this is a consistency call for the session, not a rule breach - but a reader meets 300-odd of them on the derived works lists.

**HISTORY (visible; the registry is exempt, flagged because the derived works list puts these in front of a reader)**
- l.1893 (`crown-shyness-enwiki`): *"It states that stocked crowns do not touch, **which corrects this page's earlier claim that neighboring canopies interlace**."*
- l.1863 (`estate-map-enwiki`): *"**It corrects this page's attribution**: estate maps seldom showed relief, drawing buildings and trees pictorially instead."*
- l.2148 (`kotobank-degawari`): *"…**which corrects this page's date**."*
  In each case the useful half is what the source says; "corrects this page's earlier claim / attribution / date" is the history of the research page.

**VOCABULARY** (terms in the marked write-ups that the glossary does not define and the write-up does not gloss)
| term | where | drafted definition |
|---|---|---|
| `paling` | l.477, l.479, l.428 - *"the palings set across street and lane mouths from a Ming edict of 1488"* | A fence or barrier of upright stakes; a paling across a lane mouth closed the lane at night. |
| `wicket` | l.627 - *"the wicket by which those with business passed after inspection"* | A small door set in a larger gate, opened for one person while the gate stays shut. |
| `machi-kido` | l.483 | The wooden gate that closed a town block's street at night. |
| `junks` | l.544 - *"the nine- to tenfold cost advantage of junks over land carriage"* | The flat-bottomed Chinese cargo sailing ship, the carrier of bulk goods on river and canal. |
| `raku` | l.672 - *"the unglazed and raku pottery fired at Imado"* | Low-fired hand-formed ware, taken from the kiln hot and glazed simply. |
| `dead ground` | l.497 - *"the vulnerability of a square tower's corners to mining and to the dead ground they create"* | Ground a defender on the wall cannot see or shoot into. |
| `kera` | l.1232‑1234 - *"how the kera lump was broken and sorted"* | The mass of iron and steel taken from a tatara furnace after a smelt, broken up and sorted into grades. |
| `murabarai`, `tokorobarai` | l.1084 - *"the village's own banishment, murabarai and tokorobarai"* | Expulsion from the village, and expulsion from the district, the heaviest punishments a village could impose on its own authority. |
| `Wubei Zhi` | l.1997 - *"with the Wubei Zhi's dictum on it"* | The great Ming military treatise of 1621, quoted for what a wall's bastions were for. |
| `Northern Wei` | (hinterland citations l.57, derived from `qimin-yaoshu-zhongkui`) | see §E above. |

---

## Summary tables

### Per file

| file | sections read | VOCABULARY | SESSION NOTES | HISTORY | DEFECTS |
|---|---|---|---|---|---|
| `research/cities/government.html` | 9 (`h2`) | 2 (`stroke` l.24; `property 1/2` l.93) + 3 defined inline | 1 (`3 ft/px` l.97) | 1 borderline (l.93 Minami arrangement) | 3 (Sources roster broken + footnote marks in it, l.66; contradicted claim l.88; untranslated 侍町/町人地/寺町 l.103) + heading form x3 |
| `research/cities/hinterland.html` | 5 (`h2`) | 1 (`metrology` l.68) | 2 mild (`declared` l.40; "the map wants" l.42; plus "the list the market rule reads" l.58) | none | 3 (missing `<p>` l.67; `Sources:` no space l.56; one-item `<ul>` l.24) + heading form x1 |
| `research/ways.html` | 5 (`h2`) | 5 (`girder`, `post-horse system`, `litters`, `footslope`, `seed`) | 1 (engine words l.36) | 3 (l.25 capital's deck; l.49 pool-wide plank sweep; l.70‑71 hand-placed decks and "now applied") | none |
| `research/citations/cities/government.html` | works (36) + 66 notes | 3 + 5 era names + 1 glossary mismatch (`bu`) | 6 (`NOTE:` x3, fn‑6, fn‑22, fn‑38) | 1 (fn‑32 "not 21 ft"); fn‑11 mixes history with a real finding | 9 (doubled quote fn‑13, fn‑20, fn‑9, the trailing-paraphrase class over 10 notes, `((English.))` x7, backtick spans x2, fn‑39/40 order, entity-encoded l.91/93, flat `km2`) |
| `research/citations/cities/hinterland.html` | works (13) + 26 notes | 1 (`Northern Wei`) | none | none | 2 (fn‑3 every quote twice; 「」 around English fn‑21) |
| `research/citations/ways.html` | works (18) + 26 notes | 2 (`stringers`; `nawate` as a variant) | none | none | 3 (broken sentence in the derived write-up l.29; doubled quote fn‑22; 「」 around English fn‑26) |
| `research/SOURCES.html` (355 marked entries) | 355 entries | 10 | 1 reported (l.947) - rules 2/3 exempt by spec 209 D6 | 3 reported (l.1893, l.1863, l.2148) - exempt, flagged because derived | 7 (garbled l.922; garbled + instruction l.947; untranslated 龍座林 l.1923; genge/renge l.1634; dash run l.531; flat `m2` l.1608; title-translation inconsistency across the set) |

### Glossary terms to add (paste-ready shape for `assets/glossary.json`)

| term | variants | draft definition |
|---|---|---|
| girder | girder, girders | The main beam of a bridge, which carries the deck and rests at each end on the abutment. |
| footslope | footslope, footslopes | The gentle ground at the foot of a slope, below the hill and above the wet valley floor. |
| post-horse system | post-horse system, post-horse | The relay of horses and porters kept at every post station for official traffic, which a highway full of carts would have starved of animals. |
| waystation | waystation, waystations | A staffed post on a trunk road where couriers and officials changed horses and travelers found lodging. |
| litter | litter, litters, litter-bearers | A covered seat or frame slung between poles and carried on men's shoulders - how a passenger traveled where no vehicle could go. |
| seed | seed | The number a map is generated from; the same seed always produces the same settlement, a different seed a different one. |
| metrology | metrology | The study of what a period's own units of measure actually were; a bu or a mu has no single value in feet, so a figure cannot be converted without a source for the units of its own century. |
| stroke | stroke | The width of the line a map draws a feature with; ground "clear of the stroke" is ground the drawn line itself does not cover. |
| paling | paling, palings | A fence of upright stakes; a paling set across a lane mouth closed the lane at night. |
| wicket | wicket | A small door set in a larger gate, opened for one person while the gate stays shut. |
| machi-kido | machi-kido | The wooden gate that closed a town block's street at night. |
| junk | junk, junks | The flat-bottomed Chinese cargo sailing ship, the carrier of bulk goods on river and canal. |
| raku | raku | Low-fired hand-formed pottery, taken from the kiln hot and simply glazed. |
| dead ground | dead ground | Ground a defender on the wall can neither see nor shoot into. |
| kera | kera | The mass of iron and steel drawn from a tatara furnace after a smelt, broken up and sorted into grades. |
| murabarai | murabarai, tokorobarai | Expulsion from the village, and from the district - the heaviest punishments a village could impose on its own authority. |
| stringer | stringer, stringers | The lengthwise beams of a bridge that carry its decking. |
| Wubei Zhi | Wubei Zhi | The great Ming military treatise of 1621, quoted for what a city wall's bastions were for. |
| Northern Wei | Northern Wei | The dynasty that ruled north China in the fifth and sixth centuries, when the farming treatise this record quotes was written - far earlier than the Ming and Edo the maps are drawn from. |
| yoriai-seki | yoriai-seki | A rank band among a domain's retainers; the Fukui house cited here held it at 1,000 koku. |
| kumi-chi | kumi-chi | The ground assigned to one unit of foot soldiers, where the men of that unit lived together. |
| property (setting) | at property 1, at property 2 | A household's wealth rank in the setting's own economic model: property 2 a wealthy household, property 1 a household of modest means. |
| An'ei / Bunsei / Tenpo / Kanbun / Jokyo | one entry each | The Japanese eras the notes date events to (An'ei 1772-1781, Bunsei 1818-1830, Tenpo 1830-1844, Kanbun 1661-1673, Jokyo 1684-1688) - the glossary already carries Genroku, Keicho, Kyoho, Meireki and Wanli, and these five are the gap. |
| nawate | (add as a VARIANT of the existing `azemichi` entry) | - |
| bu | (existing entry) | Consider widening: the notes also use `bu` as a unit of MONEY (*"2 ryo 2 bu"*), where today's land-area definition misleads. |
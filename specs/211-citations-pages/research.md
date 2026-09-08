# Research - 211 citations pages

## R1 - what the footnotes weigh (measured 2026-09-07, main at 44de5c69)

The bytes from `<section class="footnotes">` to the end of each research page, against the page - the part the
split moves. 795 notes, 319 distinct registry keys cited.

| page | bytes | footnotes | share |
|---|---|---|---|
| archetypes.html | 113,855 | 55,103 | 48% |
| buildings.html | 106,619 | 50,664 | 48% |
| fields.html | 126,430 | 52,650 | 42% |
| homesteads.html | 157,538 | 58,932 | 37% |
| religion-and-death.html | 38,395 | 17,025 | 44% |
| towns.html | 25,861 | 16,986 | 66% |
| urban-features.html | 149,561 | 46,271 | 31% |
| vegetation.html | 103,831 | 41,755 | 40% |
| water.html | 140,171 | 56,544 | 40% |
| cities/capitals.html | 190,884 | 64,906 | 34% |
| cities/defenses.html | 16,202 | 8,625 | 53% |
| cities/fabric.html | 23,187 | 12,798 | 55% |
| cities/government.html | 48,288 | 30,785 | 64% |
| cities/hinterland.html | 7,756 | 3,843 | 50% |
| cities/river-cities.html | 15,962 | 6,500 | 41% |

Registry entries for the cited keys run 162 to 2,002 bytes (median 369); `SOURCES.html` is 205,875 bytes with 374
entries before the write-ups.

## R2 - the drafting rulebook

The write-ups were drafted by twenty Opus agents, one per batch of sixteen keys, under one rulebook. The rulebook,
verbatim as the agents read it, is [`writeup-rules.md`](writeup-rules.md); the batch files were the cited keys' registry
entries copied out with a `cited by` comment naming the pages and footnotes that cite each. Checked afterwards by
different agents (R3).

## R3 - the source-applicability verdicts (2026-09-07)

Twenty checks, one per batch, by Opus agents other than the drafters, each following
`.claude/agents/source-applicability.md` (the agent file was written in this feature, so the agents were dispatched
as general-purpose Opus agents told to read and follow it - the harness does not route a new `.claude/agents/*.md`
type to agents launched by type mid-session). Fifteen of the twenty were cut off by an Opus session rate limit
(*"You've hit your session limit, resets 1:10am (UTC)"*); twelve of those had already written their report to the
scratchpad before the final reply failed, so seventeen reports were usable. Batches 09, 11 and 12 (48 keys) were
relaunched after the reset and reported: batch 09 one APPLICABLE, fourteen with limits, one NOT-APPLICABLE for its stated use (`kameyama-yashikigami` - the page carries six cases and no tally, so the corner weights the record attached to it are a guess, now labeled); batch 11 fifteen with limits and one canon key, with two partial not-applicable uses (`kuniezu-enwiki` for boundaries, `maff-drain-shape` for channel sections); batch 12 sixteen with limits, three write-ups mis-describing the work (an author's name, a simulation called a measurement, a museum called a general site) and two disclaiming a full text that is in fact public (`minami-2022-igune`, whose full text names the west and north sides - the footnote now quotes it; `mlit-senjochi-kurashi`, upgraded to read). The `record-format` agent then read every write-up and three citations pages: its items were the registry's own citation lines, now shown to the reader on every citations page, carrying the session's fetch notes and reading routes - 40-odd of them moved into HTML comments - and about forty terms the glossary did not define, added (`tertiary source` alone appears in more than forty write-ups).

The verdict pattern over the seventeen reports: **no source in the record is NOT-APPLICABLE as a whole**; nearly
every one is APPLICABLE-WITH-LIMITS, and a handful are APPLICABLE outright (the primary fieldwork and the
period-record studies: `kikoba-kenchi`, `tabayashi-1986`, `kaifeng-pmc7048742`, `tetsu-to-hagane-91`,
`saitama-minuma-tsusenbori`). What the checks found instead, across about 150 of the 271 keys they judged, was
that a write-up - or the registry's own `Used for:` line it inherited - claimed something the LINKED PAGE does not
carry. The GM's hypothetical (*"twenty first century forestry numbers"*) did not occur; the recurring shapes were:

- **a NOT-APPLICABLE COMPONENT inside an applicable key** (14 keys): the source supports one of its stated uses and
  not another - `plos-2016-pine` (a marsh-grass study cited for pine), `nishikori-tsunaba` (a gazetteer extract
  carrying the site and none of the four figures), `shaoxing-towpath` (no 815 CE, no 40 km, no Marco Polo),
  `qing-zhalan` (the fence, not the curfew hours or the lashes), `pingjiang-tu` (neither stated use),
  `jta-nagayamon`, `kagawa-tameike`, `jokamachi-zoning`, `neixiang-yamen`, `edo-machi-kido`, `aze-standard`,
  `asakusa-kuramae`, `adachi-kosatsu`, `hirosaki-castle`. Each `Used for:` line was cut to what the page carries
  and the research sentence resting on the rest was relabeled (R4).
- **a limit the write-up omitted** (about 100 keys): the encyclopedia article that carries a maintenance banner
  or no citation on the sentence we quote; the modern survey of a surviving form; the region standing in; the
  frozen machine-translation corpus; the figure derived by us and presented as read.
- **a "What it is" that misdescribed the work** (about 30 keys): a self-media account called an archive; a
  newspaper column called a library's writing; a Meiji land register called a survey of standing houses; a key
  bundling four works behind one link.
- **three keys whose NAME misleads**, left for the GM because renaming touches every citing page:
  `plos-2016-pine` (no pine in it), `tabayashi-1986` (the paper is 1987), `sphere-unicef` (the Sphere Project's
  handbook, not UNICEF's). Each carries an HTML comment in its entry saying so.

The seventeen reports are in the session scratchpad (`checks/batch-NN.md`); their substance is in the write-ups
and the corrected `Used for:` lines, which is where a reader meets it.

## R4 - research sentences relabeled under the checks (constitution XIV: a defect found is fixed)

Where a check found a research page asserting something its cited page does not carry, the sentence was labeled
in place rather than the source re-found (a re-sourcing is a research pass of its own, spec D5):

- `cities/capitals.html`: Hirosaki's ~50 ha (the article gives 612 by 947 m; the hectare figures are the park's,
  a GUESS); Nanjing's 35 km circuit (on no page read); the kurayashiki count of 110+ (not in the quoted passage).
- `cities/government.html`: the nagaya-mon's rooms (the Kanazawa page names servants' quarters and a stable; the
  gatekeeper's room, the chugen room, the storeroom and the guard box are a GUESS).
- `urban-features.html`: Edo's fire season (January to April, March worst, per the cited article - not "winter");
  the Qingming gate yard (tethering, no fence, no lawn are our reading of the picture); the Ming ironworks'
  workforce (Wagner's caution that the source describes a firm running several works).
- `archetypes.html`: Shunde's 4.6% (our arithmetic over a denominator on no readable page); fn 69's comment on
  the Hayami page corrected (the "trend toward smaller households" sentence IS on the page).
- `fields.html`: "many run about 1 m2" (our reading; the page gives the average and the smallest).
- `research/SOURCES.html`: `dongjing-menghualu-rujia`'s citation line (the quoted words are Yuan Jiong's
  recollection, which the article quotes; 東京夢華錄 it paraphrases); `nagoya-castle`'s line (the AI-generated
  encyclopedia struck - the linked page is Wikipedia's); `ide-japanese-experience`'s `Used for:` (a quoted phrase
  not on the page, already flagged on the research page).

## R5 - for the GM (spec D5: recorded, not silently acted on)

- **Three key names** that misdescribed their work (R3) - RENAMED on 2026-09-08 at the GM's ruling (*"If something is misdescribed then we should fix it rather than leave it misdescribed"*): `plos-2016-pine` -> `lou-2016-floodplain-zones`, `tabayashi-1986` -> `tabayashi-1987`, `sphere-unicef` -> `sphere-2004-water`, across every research and citations page, one class docstring and its snapshot fixture; the guard corpus (`scripts/fixtures/`) keeps the old name as recorded history.
- **`sugiura-1973-fuzoku`** - SETTLED 2026-09-08 by reading the paper (a `source-reader` pass over the J-Stage scan; the GM, asked to rule, rightly said it was not theirs to know): Table 5 is 「主屋類型による各機能別1戸当り付属建物棟数の変化」, the MEAN NUMBER of buildings per household by function, computed by totaling buildings and dividing by the type's household count; a building serving two functions counts under each, and the non-farm row's 1.40 storage sheds per household shows a household can hold two of a kind - so every figure is an upper bound on the share of households owning one. The record's eleven numbers are the pre-1944 row (38 households), and its "shrine 0.03" was a neighboring shed column: the shrine column reads 0.01 over all houses and is empty in that row. The entry, its footnote gloss, the fixtures comment and the class note now say so. The engine's fixture bands (`FIXTURE_BANDS`: privy 0.85-0.95, woodpile 0.75-0.95, bath 0.20-0.45, shrine 0.03-0.08) are unchanged - they were set as bands around these figures and now sit at or above the honest ceiling; whether to lower them is a knob change, an engine feature, and the GM's call.
- **Closer sources one click away** (the write-ups say so): `geography-hub-satoyama` (unsigned, undated, no
  sources; Takeuchi 2010 in *Ecological Research* and the 2019 *Sustainability* review carry the same three claims),
  `guernica-night-soil` (Kayo Tajima's 2007 study of the Edo night-soil trade is openly readable),
  `ridgelineimages-gsi` (the GSI legend itself is public and linked from the blog), `cropfarming-soybeans` (an
  extension growth-stage guide), `edago-ja` (Kotobank's 枝郷 entry, linked from the unsourced stub),
  `kojodan-dobei` (a conservation report on a surviving compound wall). Each is a research pass under the
  five-box procedure.
- **The registry's size**: `SOURCES.html` went from 195,671 to 537,047 bytes - the write-ups run longer than the
  two short paragraphs D2 priced (median about 1,050 bytes for the pair). The GM accepted the growth on 2026-09-08 (*"The growth of the registry's size is fine and I accept it"*).
- **What the map should call an assertion resting on a source of limited applicability** (D5): none arose as a
  whole-source NOT-APPLICABLE; the component cases above were labeled GUESS or "our reading" in place.

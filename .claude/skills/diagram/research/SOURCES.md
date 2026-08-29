# Sources

*The registry of sources the research entries actually cite. It records what was consulted and written down - **it is not a verified bibliography**, and nothing may be added here that has not genuinely been consulted. Where an entry names no source it says so, rather than borrowing one.*

## Citing

Cite by key in an entry's `**Sources:**` line. Add a key here the first time a source is used, with what it was used FOR - that second field is what makes a stale or over-stretched citation visible later.

**Required, not optional** (GM 2026-08-27, constitution v2.10.0): every research finding cites its sources here. **What counts as a source**, in order: primary and scholarly work; a serious reference - museum, ministry, university, standards body, an established encyclopedia such as Wikipedia (and its underlying references over the article itself). **Never an AI-generated encyclopedia or summary** (Grokipedia included): machine-rewritten from other sources, no editorial community, no provenance a reader can follow - citing it hands the interactive map's reader a dead end. A web-search result summary is a pointer to sources, never a source.

**A source carries its link** (GM 2026-08-28, constitution v2.13.0): every entry below records the URL at which the source can be read, in parentheses in the citation line - the DOI or J-STAGE landing page for a paper, the article URL for an encyclopedia, the institution's own page - or an explicit `URL: none - <why>`. The interactive map's references modal links each source to it (`interactive/sources.py` reads the URLs from this file); `tests/interactive/test_page.py` fails on an entry with neither.

**Read what you cite** (GM 2026-08-27, constitution v2.11.0): a key is added here only after the session has read the source itself - fetched and read, not summarized by a search engine or paraphrased by another page - and the finding recorded is what that text says in context. A source that cannot be fetched may still be cited, and its claim asserted, labeled SUMMARY-ONLY with what was seen (the GM, 2026-08-27: acceptable "as long as we document ... that we were relying on a search summary of a paywall paper rather than the paper itself"); citing a summary as if read is the one thing forbidden. The reading is the `source-reader` agent's job (`.claude/agents/source-reader.md`): hand it the claims and pointers, write the entry from its quotes, and label each source READ or SUMMARY-ONLY as it reports.

## Re-sourcing queue

Findings recorded before the rule, or on a source the rule now excludes. Each is re-sourced when its entry is next revisited - not rewritten wholesale - and struck from this list then. **Feature 143 (2026-08-28) worked the whole queue and every `not recorded` entry**; what remains is what a page could not be read for, each labeled in its entry.

- `zhengyi-householder-priests` - the Grokipedia half DROPPED (2026-08-28); the Patheos half stands.
- Economy of the Song dynasty (Grokipedia) - RESOLVED 2026-08-28: `economy-song-enwiki` (Hartwell's figure, read).
- History of agriculture in China (Grokipedia) - RESOLVED 2026-08-28: `loess-plateau-enwiki` (the summer concentration read; the mm range dropped as unsourced).
- Nagoya Castle (Grokipedia; site documentation) - the site-documentation half stands; the Grokipedia half is to be replaced by ja.wikipedia 名古屋城 (feature 143 leftover).
- Jokamachi surveys - RESOLVED 2026-08-28: `jokamachi-jawiki` read; the Grokipedia half dropped from the key.
- Village lane WIDTH (T50, 2026-08-27): no numeric source found for an ordinary hamlet lane or farm path in Japan or China; the drawn 3 / 5 / 6 ft stand as drawing conventions inside read bounds (Wikipedia "Stone routes" 2.7 m cart road; ja.wikipedia "大八車"; MLIT road history; Low-Tech Magazine on the wheelbarrow). A measured survey of a surviving village lane would settle it.
- The coppiced-mulberry density and crown height (research/archetypes.md 'The 6:4 water-to-dike ratio, and coppiced mulberry'): not re-found in the feature-139 pass (2026-08-28); the ratio itself was re-sourced
- Still summary-only after the `source-reader` run of 2026-08-27 (T45), each labeled in its entry: the bund-width convention (IRRI, unreachable; FAO read and larger); the Shirakawa farmstead bamboo grove (Kids Web Japan, 403 with no corroboration); the turn-minimization sentence (Ma et al. 2024 full text - the abstract's angle finding IS read); EUNIS E5.2 (404). Resolved by that run: madake hardiness (read, three growers), the forest-edge three layers (German Wikipedia "Waldrand"), the Okinawa windbreak (PMC 7898781), the GSI bamboo symbol (ridgelineimages.com).

- Still summary-only after the `source-reader` run of 2026-08-27 (T45), each labeled in its entry: the bund-width convention (IRRI, unreachable; FAO read and larger); the Shirakawa farmstead bamboo grove (Kids Web Japan, 403 with no corroboration); the turn-minimization sentence (Ma et al. 2024 full text - the abstract's angle finding IS read); EUNIS E5.2 (404).
- Summary-only or not found after feature 143's passes (2026-08-28), each labeled in its entry and listed by file in `specs/143-research-citations/ledger.md` section F2: the Jōge daikansho plan; the daikan-debt figure; the jin'ya coverage ratio; the Song monk census year; the Shunde 1581 percentages; the dike-pond board sluice (Ruddle & Zhong 1988); the lotus area share; the tameike m3/ha ratio; the forest stems/ha band; the Kaifeng tower count; the communal-well ratio; the Sado fire count.

## Works cited

### `kitamoto-mushiro-niwa`

北本市史 民俗編, the farm yard measured in straw mats (https://kdas.jp/test2/detail_display.php?t_cd=1&acc_cd=3&aclc_cd=0&chap=6&hp_page=74&bc_cd=1; READ 2026-08-28, feature 134 T49)

*Used for:* the one directly-stated work-yard size - 「普通四〇〜六〇枚、中には百枚を越す家もあった。ちなみに、ムシロ二枚が一坪にあたる」 = 20-30 tsubo (66-99 sq m) ordinarily, past 50 tsubo for a few; and that the yard tracks the household's cropped acreage (a barley district)

### `kodaira-niwa`

小平市史, the 回田新田 farmstead's measured yard (https://adeac.jp/kodaira-lib/text-list/d100010/ht002170; READ 2026-08-28)

*Used for:* the one directly measured yard - 約七十坪 (231 sq m) of swept working ground inside a 700-tsubo homestead: the upper end of the range, a large Musashino dry-field holding

### `yonekura-mushiro`

Yonekura district museum note, Okayama, on the straw mats a farm kept (https://townweb.e-okayamacity.jp/yonegura/minna/hakubutukan/hakubutu012.htm; READ 2026-08-28)

*Used for:* ~50 mats per farm - the independent second line that agrees with Kitamoto's count

### `tobunken-mushiro`

今石みぎわ, むしろ織り, Tokyo National Research Institute for Cultural Properties (https://tobunken.repo.nii.ac.jp/record/3166/files/06_55_Imaishi.pdf; READ 2026-08-28)

*Used for:* the mat's measured size - 幅3尺 x 長6尺 (90 x 180 cm, 1.62 sq m) - which converts a mat count into an area

### `kamikanai-1771-houses`

上金井村 (Meiwa 8, 1771) main-house and holding histograms, 日本建築学会論文報告集 418 (https://www.jstage.jst.go.jp/article/aijax/418/0/418_KJ00004075360/_pdf; READ 2026-08-28)

*Used for:* the SHAPE of the distribution - 31 commoner main houses fitting a lognormal of median 22.5 tsubo, sigma_ln 0.46, the headman detached at 3.1x; and the ADDITIVE coupling to holding size (5 koku more buys about 10 tsubo more)

### `kikoba-kenchi`

木古庭村 (Miura, Sagami) Bunroku 1594 and Genroku 1699 検地帳, 日本建築学会計画系論文集 222 (https://www.jstage.jst.go.jp/article/aijsaxx/222/0/222_KJ00003747888/_pdf; READ 2026-08-28)

*Used for:* homestead-lot areas 15-100 bu about a mode of 30, great holders at 2x the ordinary class - the right-skew corroboration; and that by Genroku every peasant held a homestead, so the small end is occupied rather than empty

### `santome-shinden-allotment`

三富新田 (Genroku 9, 1696) founding allotment, 日本建築学会論文報告集 436 (https://www.jstage.jst.go.jp/article/aijax/436/0/436_KJ00004077200/_pdf; READ 2026-08-28)

*Used for:* the counter-form - a planned shinden colony issued every settler an identical homestead, 屋敷の規模はまったくの均等配分: the uniform `yard_sizes="allotted"` knob

### `ndl-kokumori`

National Diet Library reference on 石盛 (the assessed yield per tan) (https://crd.ndl.go.jp/reference/entry/index.php?id=1000296656&page=ref_view; READ 2026-08-28)

*Used for:* 1.3 koku/tan for 中田 - the first input of the crop-derived yard area

### `irri-drying-floor`

IRRI Rice Knowledge Bank, sun drying and drying-floor area (https://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm; READ 2026-08-28)

*Used for:* the spread depth ("thin layers of ideally 2-4 cm") and the only direct area statement ("500 square meters of drying floor can handle 6 tons of paddy") - MODERN practice, flagged as such, used only to convert a crop volume into a floor area

### `sugiura-1973-fuzoku`

Sugiura Tadashi, 「農村集落における農家の付属建物について - 宮城県宮崎町の例」, *Tōhoku Chiri* 25(3): 145-152, 1973 (JStage tga1948/25/3/25_3_145; READ 2026-08-27, all eight pages) (https://www.jstage.jst.go.jp/article/tga1948/25/3/25_3_145/_article/-char/ja)

*Used for:* the per-household inventory of farmstead outbuildings by function (Table 5) and what stood inside the old main house (Table 6) - privy 0.87, firewood shed 0.76, straw shed 0.68, barn 0.58, work shed 0.55, livestock shed 0.55, kura 0.24, manure shed 0.24, bath 0.29, coop 0.16-0.28, household shrine 0.03; scope 1972 Tōhoku, stated wherever quoted

### `tabayashi-1986`

Tabayashi 1986, *Geographical Review of Japan* 60(1) (jstage grj1984b/60/1) (https://www.jstage.jst.go.jp/article/grj1984b/60/1/60_1_41/_article/-char/en/)

*Used for:* tameike siting above its fields; one outlet; canals taper as they are tapped; supply/drain separation at system level

### `kagawa-tameike`

Kagawa prefecture *tameike* structure pages (https://www.pref.kagawa.lg.jp/tochikai/about_tameike/repair/structure.html)

*Used for:* inclined intake (shahi) + bottom conduit (sokohi); spillway as flood-safety; parent/child pond linkage

### `mbalib-canal-layout`

MBA智库百科, 灌溉渠道系统 (https://wiki.mbalib.com/wiki/灌溉渠道系统)

*Used for:* the command-area placement law - mains on the district's high ground for gravity command of the largest area; every canal tier on the high ground of its own control area; mains/branches along contours and ridges, field channels across them

### `saitama-minuma-tsusenbori`

Saitama City, 見沼通船堀のしくみ (https://www.city.saitama.lg.jp/004/005/006/008/p077111.html)

*Used for:* Minuma-dai dividing its head into east-edge/west-edge canals (東縁/西縁) along the plateau rims, with the Shiba River draining the central lowland

### `jsidre-minumadai`

JSIDRE, on Minuma-dai (1728) (https://www.jsidre.or.jp/tabata5-a/)

*Used for:* the Edo Kishu-school comb layout - supply on the elevated margins, drainage on the lowest line

### `maff-water-history`

MAFF agricultural-water history PDF (https://www.maff.go.jp/j/nousin/mizu/kurasi_agwater/k_agri/pdf/detail_jp.pdf)

*Used for:* Japanese irrigation history background

### `nies-shiroyone`

Shiroyone terraced paddies (NIES) (https://ap-plat.nies.go.jp/inas/goodpractices/tradition/3.html)

*Used for:* terrace form

### `japanese-wiki-corpus`

Japanese Wiki Corpus + Tsukuba field-trace surveys (https://www.japanesewiki.com/history/Jori%20sei%20(system%20of%20land%20subdivision%20in%20ancient%20Japan).html)

*Used for:* jori-sei grid

### `beitang-studies`

Nature Communications 2023; Jiang-Huai pond irrigation (PMC6695888) (https://www.nature.com/articles/s41467-023-39454-w; unfetched 2026-08-28)

*Used for:* Chinese *beitang* pond systems as the dominant village-scale irrigation mode in rice China

### `buck-survey`

Buck, pre-mechanization farm survey of China, 1929-33 (https://archive.org/details/landutilizationi0000buck)

*Used for:* mean dry parcel near 1 mu; mid-Qing Jiangnan holdings scattered over several parcels

### `senmaida`

Shiroyone Senmaida (Wajima, Ishikawa) - the Japanese government's *Highlighting Japan* feature (gov-online.go.jp, June 2025), the Wajima city cultural-property listing (wajima.hiddenheritage.jp), and JNTO's site page (japan.travel); cross-read against the Obasute and Maruyama Senmaida listings (https://www.gov-online.go.jp/hlj/en/june_2025/june_2025-01.html; unfetched 2026-08-28)

*Used for:* the SMALL end of a real worked paddy - 1,004 basins on ~4 ha, average ~18-20 m2, many near 1 m2, the smallest about half a meter square, and the straw-raincoat anecdote. Establishes that no ABSOLUTE minimum paddy area exists, which is why the size floor is a ratio to the fan's own design cell instead

### `bench-terrace-riser`

FAO STI-portal and ICIMOD pages on traditional irrigated / rainfed paddy rice terraces, plus general bench-terracing references (https://sti-portal.fao.org/innovations/traditional-irrigated-rice-terraces)

*Used for:* the terrace riser as a structural retaining face (0.8-1.5 m, stone-faced where available, slope 80-160%) with water held by a separate 10-15 cm lip on the platform edge - the physical difference that makes micro-basins a terrace phenomenon and not a valley-floor one

### `li-bozhong-jiangnan`

Li Bozhong, "The Practice of 'Ten Mu per Farmer' and the Scale of the Traditional Peasant Economy" (*Zhongguo Nongshi*, 1996) and *Agricultural Development in Jiangnan, 1620-1850* - consulted at secondhand via LSE economic-history working papers and the EH.net review (https://eh.net/book_reviews/agricultural-development-in-jiangnan-1620-1850/)

*Used for:* mid-Qing Jiangnan farms averaged ~10 *mu* (~1.5 ac at the Ming-Qing *mu* of ~614 m2) per farm household

### `skinner-marketing`

G. William Skinner, *Marketing and Social Structure in Rural China* (1964-65) - consulted at secondhand via retrospectives and reviews (https://doi.org/10.2307/2050412)

*Used for:* the standard marketing community - a market town centered on ~18 villages across ~300-500 km2 of farmed hinterland

### `aric-land-history`

ARIC, "History of Agricultural Land Development in Japan" (aric.or.jp) (https://www.aric.or.jp/kiseki/en/tsuchi/index.html)

*Used for:* the Edo average farm household holding of ~1 *cho* (~2.45 ac), paddy plus dry

### `mdpi-kunisaki`

"Sustainable Irrigation Management in Paddy Rice Agriculture: A Comparative Case Study of Karangasem Indonesia and Kunisaki Japan" (*Sustainability* 12(3):1180, 2020) (https://www.mdpi.com/2071-1050/12/3/1180; unfetched 2026-08-28)

*Used for:* small *tameike* command areas - Tsunai ward's 5 systems / 50 ha / 11 farmers; traditional tanks typically commanding well under 200 ha

### `fortune-1843`

Robert Fortune, eyewitness account, 1843 (https://www.gutenberg.org/ebooks/54720)

*Used for:* tea on the lower and most fertile hillsides, never the low lands or the barren upper slope

### `willow-palisade`

Qing Willow Palisade statute (border embankment) (https://baike.baidu.com/en/item/Willow%20Palisade/1480401)

*Used for:* willow whips every 5 chi (~1.67 m) in rows on an embankment. **ANALOG only** - no polder-dike-specific statute was found

### `shen-kuo`

Shen Kuo, *Illustrated Records of Wanchun Polder* (Northern Song) (https://zh.wikipedia.org/wiki/%E4%B8%87%E6%98%A5%E5%9C%A9)

*Used for:* full dike enclosure as the defining feature of a weitian

### `fei-xiaotong`

Fei Xiaotong, Kaixiangong / the Xichang polder layout (https://archive.org/details/PeasantLifeInChina)

*Used for:* houses inside the polder along its interior streams (the deep-water settlement case)

### `qingming-shanghe-tu`

*Qingming Shanghe Tu* 清明上河図, gate scene (https://en.wikipedia.org/wiki/Along_the_River_During_the_Qingming_Festival)

*Used for:* the city-gate cart yard: clustered carts and pack animals, hitching posts, no fence, no lawn

### `forests-2020`

"Village Fengshui Forests as Cultural and Ecological Heritage", *Forests* (2020) (https://doi.org/10.3390/f11121286; unfetched 2026-08-28)

*Used for:* southern-China village fengshui grove field-survey areas

### `sphere-unicef`

Sphere / UNICEF water-supply standards (https://ec.europa.eu/echo/files/evaluation/watsan2005/annex_files/Sphere/SPHERE2%20-%20chapter%202%20-%20Min%20standards%20in%20water,%20sanitation%20and%20hygiene%20prom.pdf)

*Used for:* one open well serves ~400 people - capacity is never the binding constraint on well count

### `aas-rice-technology`

AAS, "Rice, Technology, and History" (https://www.asianstudies.org/publications/eaa/archives/rice-technology-and-history-the-case-of-china/; unfetched 2026-08-28)

*Used for:* rice domesticated in naturally marshy areas; paddy as reclaimed marsh

### `lacey-regime`

Lacey's regime theory for unlined alluvial canals - the wetted-perimeter equation `P = 4.75 * sqrt(Q)`, and the regime power-law exponents (width 0.5, depth 0.33, velocity 0.17 against discharge). Consulted via canal-design references and the *Journal of Hydrology* review "The width of a bankfull channel; Lacey's formula explained" (2003) (https://doi.org/10.1016/S0022-1694(03)00069-6)

*Used for:* the taper LAW - a channel's width goes as the square root of the discharge it carries, so `taper_w` interpolates the width SQUARED; and the absolute-width sanity check that found the drawn comb net ~5-6x its true hydraulic size

### `fao-paddy-duty`

FAO irrigation training manuals - "Scheme Irrigation Water Need and Supply" (u5835e) and "Determination of the Irrigation Schedule for Paddy Rice" (t7202e) (https://www.fao.org/4/u5835e/u5835e00.htm)

*Used for:* the paddy irrigation duty used to size a real channel against a real command area - a net need near 1 L/s/ha (~8.6 mm/day) continuous, plus ~200 mm for puddling, which is the peak that sets a supply canal's section

### `nougyoudoboku-suikou`

のうぎょうとぼく (Japanese agricultural-engineering design notes), 水田内の「水口・水じり（落水口）」に関する設計について (https://nougyoudoboku.com/water-entrance-exit/)

*Used for:* the *mizuguchi* as the plot's intake from the terminal channel - one per plot (two if the spacing exceeds 50 m), **width within 50 cm**, sill 0-10 cm above the field surface, ~0.4 m/s allowable velocity; and the outlet (*shirimito* / 落水口) as an overflow set 5-10 cm below the field surface

### `nougyoudoboku-matsutan`

のうぎょうとぼく, 水田圃場内の「末端用水路・小用水路」 and 「末端排水路・小排水路」 (https://nougyoudoboku.com/terminal-irrigation-canal/)

*Used for:* the three-tier supply hierarchy 幹線 -> 支線 -> 末端用水路 and its drainage mirror 末端 -> 支線 -> 幹線排水路; branch spacing 300-600 m; the terminal channel's bed set -5 to +10 cm against the paddy surface; a terminal drain 50-60 cm below the field surface, its section sized from the accumulating 集水面積

### `gb50288`

GB50288-2018 灌溉与排水工程设计标准, sections 6.4 and 17.7; plus the Chinese five-tier canal vocabulary 干渠 / 支渠 / 斗渠 / 农渠 / 毛渠 (https://www.antpedia.com/standard/7931413-1.html; unfetched 2026-08-28)

*Used for:* the FIVE fixed canal tiers with the *maoqu* (毛渠) as the finest, the tier below anything we draw; 斗渠 1,000-3,000 m at 400-800 m spacing and 农渠 400-800 m at 100-200 m spacing; paddy plot (格田) 25-30 m x ~100 m on the plain; 斗/农 bank tops not under 1 m

### `toro-site`

Toro site (登呂遺跡), Shizuoka - Shizuoka City Toro Museum and the Japanese Wikipedia entry (https://www.city.shizuoka.lg.jp/s6725/s005190.html; unfetched 2026-08-28)

*Used for:* the attested pre-modern paddy net - ~40 plots of 1,000-2,000 m2 over ~8 ha, a single central canal with the paddies ranked either side, 大畦畔 dividing large compartments with small ones inside, and canal + bund revetted with *yaita* sheet boards 2 m x 30-40 cm x 5 cm

### `aze-standard`

Japanese land-improvement standard designs for 畦畔 (paddy bunds) - Aomori prefecture ほ場整備 standard drawing set and 大和川流域水田貯留技術基準 (https://www.pref.aomori.lg.jp/soshiki/nourin/noson/files/H2904_nnzusyu_H2911syuusei.pdf)

*Used for:* the standard outer bund as a trapezoid of **30 cm top width, 30 cm high, 1:1 side slopes** (so ~90 cm at the base), enlarged to ~50 cm x 40 cm in cold regions for deep-water irrigation and frost heave

## Attested instances (anchors, not works)

Named real-world cases the rules are calibrated against. They are evidence, but they are measurements rather than publications, so they are listed separately and cited inline by name.

| Anchor | What it anchors |
|---|---|
| Suzugamori | 74 x 16.2 m (~243 x 53 ft), serving Edo for 220 years - the execution-ground size anchor |
| Pingyao | Market Tower attested at 133.4 m2 plan (~38 ft square); ~60 m mamian tower spacing - the wealthy-county-seat anchor |
| Xi'an | mamian bastions ~20 m wide projecting ~12 m; ~120 m tower spacing (the `peaceful` tier) |
| Himeji | moats averaging ~20 m (max 34.5 m) - the provincial-city moat tier |
| Osaka | outer moat ~70-90 m - the grand-city moat tier, deliberately ABOVE our range |
| Fushimi Inari | *Senbon Torii*: ~800 gates over ~400 m - the donation-row regime |
| Kasuga Taisha / Meiji Jingu / Nagao | ranked ichi/ni/san-no-torii 200 m-1.3 km apart - the other regime |
| Northampton | largest excavated urban tannery at 36-37 pits - far past anything in this pool |
| Longsheng | largest terrace 0.62 mu (~0.10 acre); 15,862 terraces in one village |
| Edo Kokucho time bell | billed ~400-410 blocks 'within earshot' - the bell-audibility anchor |
| Shunde county | ~4.6% dike-pond in 1581 while containing townships already over 50% - the scatter was normal |

### `kanazawa-teramachi`

VISIT KANAZAWA official travel guide, Teramachi Temple Area (https://visitkanazawa.jp/en/spot/detail_10182.html)

*Used for:* ~70 temples clustered in one castle-town temple district

### `takada-teramachi`

Takada Teramachi tourism site / Joetsu Stories (https://joetsu-stories.jp/2025/02/03/takada-teramachi-part-1/)

*Used for:* ~25 temples relocated to Takada in the 1614 wave

### `takayama-teramachi`

Japan Travel, "Takayama's historic 'Temple Town'" (https://en.japantravel.com/gifu/takayama-s-teramachi-gifu/13893)

*Used for:* "over 10 temples and shrines" in a SMALL castle town - the size-matched anchor for the city tier

### `jokamachi-wiki`

Japanese Wiki Corpus, *Jokamachi* (https://www.japanesewiki.com/history/Jokamachi.html)

*Used for:* the teramachi sited at the jokamachi's outer rim, its precincts forming part of the city defenses

### `pingyao-chenghuangmiao`

Wikipedia, City God Temple of Pingyao (https://en.wikipedia.org/wiki/City_God_Temple_of_Pingyao)

*Used for:* the City God temple as a complex of three distinct temples on one county-seat site

### `chinaknowledge-tang-econ`

chinaknowledge.de, Tang-period economy (http://www.chinaknowledge.de/History/Tang/tang-econ.html; unfetched 2026-08-28)

*Used for:* monastic land and dependents funding mills, oil presses and other enterprises

### `inexhaustible-treasuries`

*Studies in Chinese Religions* 5(2), "Giving while keeping: inexhaustible treasuries and inalienable wealth in medieval China" (https://doi.org/10.1080/23729988.2019.1639463; unfetched 2026-08-28)

*Used for:* the wu-jin-zang interest-earning endowment; Xuanzong's 713 liquidation

### `tontine-monastery-lending`

The Tontine Coffee-House, "Buddhist Monastery Lending" (https://tontinecoffeehouse.com/2024/02/26/buddhist-monastery-lending/)

*Used for:* monasteries as pawnbrokers; the 1202 Song lay-partnership pawnshop *ju*

### `pawnbroking-history`

Wikipedia, History of pawnbroking (https://en.wikipedia.org/wiki/History_of_pawnbroking)

*Used for:* pawnbroking limited to Buddhist monasteries prior to the Tang

### `zhengyi-householder-priests`

Grokipedia, *Zhengyi Dao*; Patheos, Taoism leadership and clergy (https://grokipedia.com/page/Zhengyi_Dao; unfetched 2026-08-28)

*Used for:* married priests residing in households, hereditary ordination within families

### `kannushi-wiki`

Wikipedia, Shinto priest / Kannushi (https://en.wikipedia.org/wiki/Kannushi)

*Used for:* hereditary shrine office, up to 100 generations; abolished 1871, persists by local preference

### `jodo-shinshu-marriage`

Seattle Betsuin, "Jodo Shinshu and Marriage" (https://seattlebetsuin.org/jodo-shinshu-and-marriage/)

*Used for:* the Tokugawa exemption permitting a married temple head to keep priestly status

### `tricycle-temple-wives`

Tricycle, "Temple Wives of Japan" (https://tricycle.org/magazine/japan-temple-wives/)

*Used for:* the bomori institution and eldest-son succession

### `nishikori-tsunaba`

Kotobank, Nishikori tsunaba site entry; Yaotsu town history pages (yaotsu-mall.com) (https://kotobank.jp/word/%E9%8C%A6%E7%B9%94%E7%B6%B1%E5%A0%B4%E8%B7%A1-3061429)

*Used for:* the full-river rope catch at the gorge mouth; ~300,000 logs/yr; the autumn-to-spring season; the 138-official timber magistracy; 1340s origin

### `kiso-unzaihou`

Rinya-cho (Japan Forestry Agency), Kiso-style felling and transport method pages (https://www.rinya.maff.go.jp/chubu/kiso/morigatari/unzaihou.html)

*Used for:* the kanagashi loose-log drive handing off to rafts at the tsunaba; three-man raft crews; onward transport to the Nagoya and bay-port storage yards

### `susquehanna-boom`

Wikipedia, Susquehanna Boom; PA Conservation Heritage; Lumber Heritage Region (https://en.wikipedia.org/wiki/Susquehanna_Boom)

*Used for:* seven miles of boom ALONG one side of the river; ~350-400 stone-filled cribs 22 ft high; 300 million board feet held at once; ~40 million logs lifetime

### `stcroix-boom-nps`

NPS, "The St. Croix Boom" (https://www.nps.gov/articles/000/stcroixboom.htm)

*Used for:* lengthwise division into log channels and holding pens beside a maintained navigation channel; the hinged sheer boom; navigation lawsuits and negligence rulings

### `hudson-big-boom`

New York Almanack, "The Big Boom: Old Hudson River Chain Recalls Logging History" (https://www.newyorkalmanack.com/2016/10/the-big-boom-old-hudson-river-chain-recalls-logging-history/)

*Used for:* boom construction - hewn timbers bolted raftwise, chained end to end over friction rollers to bank abutments; the 1859 break that scattered logs 40 miles

### `kiba-koto`

the tokyo files, "the kiba of Koto-ku"; Hiroshige print notes (Adachi / Brooklyn Museum) (https://thetokyofiles.com/2023/03/20/the-floating-world-of-floating-logs-the-kiba-of-koto-ku/)

*Used for:* Edo's off-river timber district of canals and storage ponds; floating storage preserving timber; rafts poled in canals

### `shangxinhe-gazetteer`

Jiangsu provincial gazetteer site on Shangxinhe; Wikipedia/Baidu, Shangxinhe (https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%96%B0%E6%B2%B3%E9%95%87)

*Used for:* Nanjing's ~9 km side-channel timber market; rafts moored in mass along the banks; the Qing-peak "constantly sufficient through all seasons" trade

### `timber-rafting-wiki`

Wikipedia, Timber rafting (https://en.wikipedia.org/wiki/Timber_rafting)

*Used for:* rafting vs driving as distinct systems; raft dimensions across traditions (Rhine rafts to hundreds of meters, thousands of logs)

## Setting canon

`l7r.md` and `budgets.md` (the GM's own notes) are cited inline by filename rather than keyed here - they are canon rather than research, and an entry resting on them carries the `setting-canon` evidence class.

### `jta-nagayamon`

Japan Tourism Agency multilingual commentary database, Nagaya-mon (H30-00651) (https://www.mlit.go.jp/tagengo-db/en/H30-00651.html)

*Used for:* the nagayamon as a perimeter retainer range with a gate cut through it; its contents (gatekeeper's room, chugen room, stable, storeroom); lookout windows

### `jta-ashigaru-kaga`

Japan Tourism Agency multilingual commentary database, Ashigaru Residences / Samurai Ranks in the Kaga Domain (H30-00660, H30-00647) (https://www.mlit.go.jp/tagengo-db/en/H30-00660.html)

*Used for:* ashigaru kumi-yashiki on the town fringe; 165/230 m2 hedged plots with gardens, flagged as unusual for Japan; enclosure by rank (wall / fence / hedge)

### `fukui-bushi-jutaku`

Fukui Prefectural Archives exhibit, the housing of Fukui-domain samurai (Matsudaira Bunko) (https://www.library-archives.pref.fukui.lg.jp/bunsho/category/tenji/32442.html)

*Used for:* the plot-size ladder by stipend (1,000-1,700 tsubo karo down to 66-96 tsubo clerks); the Suginuma 1839 plan whose street-facing buildings are named as the servants' nagaya

### `matsue-bukeyashiki`

Matsue Buke Yashiki (Shiomi Nawate), museum building documentation (https://www.matsue-bukeyashiki.jp/about/equipment.html)

*Used for:* a middle-rank residence with its nagayamon on the street; room program including servants' service rooms

### `hikone-ashigaru`

Hikone ashigaru kumi-yashiki documentation (hikone-bunkaisan.net) (https://hikone-bunkaisan.net/ashigaru/)

*Used for:* ashigaru housing as the town's outermost defensive ring; 5 x 10 ken plots; kumi living together along numbered stretches of one street

### `shibata-ashigaru-nagaya`

Shibata ashigaru-nagaya (1842, Important Cultural Property), Hoppou Bunka museum documentation (https://online.bunka.go.jp/heritages/detail/144338)

*Used for:* the default TERRACED form of low-retainer housing - 8 households under one roof, 24 x 3.5 ken, 9 tsubo per household

### `bukeyashiki-wiki`

Japanese Wikipedia, 武家屋敷 (https://ja.wikipedia.org/wiki/%E6%AD%A6%E5%AE%B6%E5%B1%8B%E6%95%B7)

*Used for:* the buke-yashiki plot program and the perimeter nagaya; setback and enclosure conventions

### `buke-hokonin-wiki`

Japanese Wikipedia, 武家奉公人 (https://ja.wikipedia.org/wiki/%E6%AD%A6%E5%AE%B6%E5%A5%89%E5%85%AC%E4%BA%BA)

*Used for:* live-in domestic service on annual contracts (degawari), hiring out of the merchant quarter through brokers; chugen as shared-room staff on call

### `neixiang-yamen`

Neixiang county yamen (内乡县衙), Henan - site documentation and plan descriptions (https://cn.chinadaily.com.cn/a/202103/12/WS604b0287a3101e7ce9743b4c.html)

*Used for:* the three-axis yamen plan; the clerks' lodging (吏舍) on the west line; the runners' duty courtyard; banfang as improvised sheds against the wall

### `pingyao-yamen`

Pingyao county yamen (平遥县衙), Shanxi - site documentation (https://baike.baidu.com/item/%E5%B9%B3%E9%81%A5%E5%8E%BF%E8%A1%99/2409876; unfetched 2026-08-28)

*Used for:* the 1619 gongxiefang clerk lodging built behind the west office range; yamen footprint (~200 x 100 m)

### `daozuofang`

倒座房 / 北京四合院 (Chinese Wikipedia and vernacular-architecture summaries) (https://zh.wikipedia.org/wiki/%E5%80%92%E5%BA%A7%E6%88%BF)

*Used for:* servants' quarters in the street-fronting south row whose blank back wall is the compound's street face; rear service row; wings house family, not servants

### `pingjiang-tu`

Pingjiang tu (平江图), the 1229 stone-carved plan of Suzhou, and its scholarship (https://zh.wikipedia.org/wiki/%E5%B9%B3%E6%B1%9F%E5%9B%BE)

*Used for:* post-Song wards as name plaques rather than enclosures; plot DEPTH as the class marker in an elite quarter

### `jokamachi-wiki-corpus`

Japanese Wiki Corpus, *Jokamachi* (translation of the ja.wikipedia article) (https://www.japanesewiki.com/history/Jokamachi.html)

*Used for:* the castle at the town's center; concentric rank-graded zoning (Sange / Kamiyashiki-cho for samurai, Ban-cho / Teppo-cho for ashigaru); occupational machi (Gofuku-machi, Kaji-machi); teramachi at the outer rim as part of the city defenses; main roads routed past the castle's front "to indicate the glory of the ruler"; sogamae total enclosure (Odawara, Osaka)

### `hirosaki-castle`

Hirosaki Castle (Wikipedia; Hirosaki Park official site) (https://en.wikipedia.org/wiki/Hirosaki_Castle)

*Used for:* castle enceinte ~50 ha / 123 acres including moats, at a 47,000-koku daimyo; the tenshu itself ~0.6 ha - the anchor for the median capital's `castle_px2` and for "the keep is not the castle"

### `himeji-castle`

Himeji Castle (Wikipedia) (https://en.wikipedia.org/wiki/Himeji_Castle)

*Used for:* the grand end of the castle band - 233 ha / 576 acres total enceinte, 4,200 m circumference, 107 ha inside the middle moat; moat dimensions (avg 20 m, max 34.5 m, depth ~2.7 m)

### `hikone-castle-town`

Nakasendo Way, *The Story of Hikone Castle Town* (https://www.nakasendoway.com/the-story-of-hikone-castle-town/)

*Used for:* the 1695 census figure of 15,371 townspeople in 53 wards at a 300,000-koku domain - the population anchor showing a Rokugani capital is a Hikone-scale market town carrying far fewer samurai

### `okayama-castle`

Okayama Castle site and visitor documentation (https://okayama-castle.jp/learn-history-en/)

*Used for:* Ukita Hideie diverting a branch of the Asahi River as the moat on the castle's northeastern flank - an attested edge castle

### `kitsuki-castle`

Kitsuki castle town coverage (Japan Today; JNTO) (https://japantoday.com/category/features/travel/kitsuki-castle-town-on-the-sea; unfetched 2026-08-28)

*Used for:* the castle on a promontory between the Yasaka and Takayama river mouths at Morie Bay, samurai quarters and temples on the surrounding hills - the second attested edge castle

### `beijing-imperial-city`

Imperial City, Beijing (Wikipedia) (https://en.wikipedia.org/wiki/Imperial_City,_Beijing)

*Used for:* the Six Ministries' offices flanking the Corridor of a Thousand Steps outside Chengtianmen - the bureaucracy on the ceremonial avenue OUTSIDE the palace walls

### `liufang-yamen`

Qing local-government scholarship on the 六房三班 organization; Pingyao county yamen documentation (https://zhuanlan.zhihu.com/p/660442182; unfetched 2026-08-28)

*Used for:* the six fang as ROOMS (side halls flanking the yamen courtyards) rather than separate buildings at county scale; ~300 rooms across Pingyao's courts

### `nagoya-castle`

Nagoya Castle (Grokipedia; site documentation) (https://en.wikipedia.org/wiki/Nagoya_Castle)

*Used for:* the Sannomaru Oyakata mansions in the third bailey; the goten as the administrative and residential center as distinct from the defensive tenshu

### `matsumoto-goten`

Matsumoto Castle official site, Honmaru/Ninomaru Goten pages (https://www.matsumoto-castle.jp/eng/about/palace)

*Used for:* the county office and town office being moved OUT of the castle into Rokku town when the ninomaru proved too small, and the daimyo/headman conference hall to Agetsuchi town

### `edo-machi-kido`

Edopedia (edoflourishing), *machi - towns and villages*; Edo nagaya/roji coverage (https://edoflourishing.blogspot.com/2013/10/machi-towns-and-villages.html)

*Used for:* the machi-level kido barring each town block (open ~4 am to ~10 pm); the finer roji-kido / nagaya-kido on each tenement lane (locked ~6 pm to ~6 am, keys with the nagaya owner or trusted neighbors); block-level collective responsibility for the gate

### `qing-zhalan`

Qing Beijing street-fence coverage (Dashilan street history; Beijing city fortifications; imperial-curfew reporting) (https://www.atlantis-press.com/proceedings/ssha-23/125988752)

*Used for:* zhalan (栅栏) palings closing each street at night, and Dashilan named for its gate; the curfew that backs them - dusk drum at 8 pm, dawn bell at 4 am, 40 lashes for being abroad 9 pm to 3 am (50 in the capital), barricaded sentry points on the thoroughfares each evening

### `jokamachi-zoning`

Jokamachi surveys (Nakasendo Way, *Castle Towns*; the Grokipedia half dropped 2026-08-28, feature 143 - the zoning claims now also rest on `jokamachi-jawiki`, READ) (https://www.nakasendoway.com/castle-towns-2/)

*Used for:* chonin wards forming narrow strips that SEPARATE different groups of samurai, sited along the major thoroughfares; separation within the buke-chi being per-compound ("larger compounds separated by walls and gates") rather than a district palisade; chonin plots smaller per family and tightly aligned along the streets

### `edo-josui`

Tokyo Waterworks Historical Museum; Tokyo Metropolitan Waterworks, Tamagawa Josui pages; Tamagawa Aqueduct (Wikipedia); IHCSA Cafe, *Tamagawa Josui: Edo's Precious Waterworks* (https://ihcsacafe-en.ihcsa.or.jp/news/josui/)

*Used for:* the two-part josui - ~43 km of OPEN cut "excavated without timbering" from Hamura to the Yotsuya gate, then ~67 km of BURIED stone (sekihi) and wooden (mokuhi) pipe inside the city feeding 3,600+ draw-wells and cisterns; ship's carpenters as the trade that laid the wooden pipe

### `kanda-kakehi`

Tokyo Metropolitan Library, *Ochanomizu Aqueduct, Kanda Service Water Supply Flume*; Nippon.com on Suidobashi; Tokyo Waterworks Historical Museum (Kanda Aqueduct stone pipe) (https://www.library.metro.tokyo.lg.jp/portals/0/edo/tokyo_library/modal/index.html?d=5655)

*Used for:* the kakehi (懸樋) carrying the Kanda Josui over the Kanda River at Ochanomizu as an open flume on a bridge; Suidobashi ("aqueduct bridge") named for it; Hiroshige's depiction - the attested above-ground crossing

### `osaka-kurayashiki`

Dojima Rice Exchange (JPX/ODEX); Japanese Wiki Corpus, *Daimyogashi*; rice-broker surveys (https://www.jpx.co.jp/dojima/en/index.html; unfetched 2026-08-28)

*Used for:* kurayashiki as the daimyo's warehouse-residence AT THE MARKET (Osaka, Nakanoshima, 110+ at the early-1800s peak) where tax rice was auctioned against rice bills - i.e. the SELLING end, not the domain capital

### `asakusa-kuramae`

Asakusa / Kuramae district histories; *Rice broker* (Wikipedia) (https://en.wikipedia.org/wiki/Rice_broker)

*Used for:* the shogunate's own riverside rice granaries on the Sumida; Kuramae (蔵前) "before the storehouses" as the brokers' district; fudasashi warehousing, converting and lending against stipend rice, and their wealth seeding the neighboring entertainment district

### `kuramai`

Britannica, *kuramai*; koku-system surveys (https://www.britannica.com/topic/kuramai; unfetched 2026-08-28)

*Used for:* peasants paying tax rice up to the DOMAIN granary, from which samurai stipends were paid - the collecting-and-disbursing role of a castle town as distinct from the market

### `shaoxing-towpath`

Shaoxing ancient towpath coverage (CGTN; Shanghai Daily); Grand Canal surveys (https://news.cgtn.com/news/3d3d674d7755444d33457a6333566d54/index.html)

*Used for:* the qiandao (纤道) towpath as the real riverside way - Shaoxing's dating to 815 CE and running 40+ km on the Eastern Zhejiang Canal, barges hauled by horse teams (Marco Polo), and its two forms: bank-side, and slab stones on stone piers standing ~0.5 m above the water parallel to the bank

### `edo-river-transport`

IDE "Japanese Experience" archive on Edo distribution; Nakasendo Way, *River and Sea Transport*; Oi-kawa crossing histories (https://www.nakasendoway.com/river-and-sea-transport/)

*Used for:* river transport carrying the tribute rice with a cargo role equivalent to the roads' military/administrative one; Japan's short fast rivers preventing an extensive inland waterway network; and roads NOT following rivers - bridges and ferries prohibited at the Oi-kawa on the Tokaido so the river served as a checkpoint

### `kotobank-benjo`

日本大百科全書(ニッポニカ) 「便所」, via kotobank.jp/word/便所-131200 (READ 2026-08-27, source-reader) (https://kotobank.jp/word/便所-131200)

*Used for:* the farm privy as ONE independent outbuilding holding the urinal and the privy, "普通" (T53).

### `sinyoken-madori`

sinyoken.sakura.ne.jp, 「間取りからみたトイレの位置の変遷」 (camadori.htm) and cayomo016.htm (READ 2026-08-27, source-reader) (https://sinyoken.sakura.ne.jp/caffee/camadori.htm)

*Used for:* where the farm privy stood - by the naya, at the back door, toward the 背戸口, the 戸口便所 (T53).

### `artic-pigsty-latrine`

Art Institute of Chicago, "Model of a Pigsty and Latrines", Eastern Han, object 37716 - catalog text read through api.artic.edu (the page itself 403s) (READ 2026-08-27, source-reader) (https://www.artic.edu/artworks/37716; unfetched 2026-08-28)

*Used for:* the Han pigsty-privy as one customary structure - the muck clusters with the privy (T55).

### `boso-no-mura-kigoya`

Chiba Prefectural Museum, Boso-no-Mura, the reconstructed farmstead's 木小屋 page (READ 2026-08-27, source-reader; a second page returned mojibake) (https://www.chiba-muse.or.jp/MURA/facility/page-1521181891660/page-1521294570333/)

*Used for:* a firewood/charcoal shed on the farmstead (T54). Its PLACEMENT is not on the page.

### `jawiki-koedame`

ja.wikipedia 肥溜め and 下肥 (READ 2026-08-27, source-reader) (https://ja.wikipedia.org/wiki/肥溜め)

*Used for:* night soil fermented in buried jars/plastered pits, 1-1.5 m across, 1-4 weeks (T55). Location not stated.

### `mizumaki-goemonburo`

Mizumaki town historical museum, 五右衛門風呂 (READ 2026-08-27, source-reader) (https://www.town.mizumaki.lg.jp/museum/040/020/050/550/1258.html)

*Used for:* the goemon-buro "used widely in self-sufficient farm villages" (T56).

### `cambridge-animals-china`

*Animals through Chinese History*, Cambridge, chapter "Where did the animals go" (READ 2026-08-27, source-reader; the chapter leans on 1930s survey data by its own account) (https://www.cambridge.org/core/books/animals-through-chinese-history/where-did-the-animals-go/E281204414087F0A9ACCDDCEF5358C08)

*Used for:* "farmers in most regions of China managed to keep a pig and some chickens in their yard" (T59).

### `qimin-yaoshu-yangji`

齊民要術 卷六 養雞第五十九, wikisource (四庫全書本) (READ 2026-08-27, source-reader) (https://zh.wikisource.org/wiki/齊民要術_(四庫全書本)/卷06)

*Used for:* the chicken roost as a ground-level enclosure with a perch, preferred to the trees (T59).

### `pitt-zhengzhou-coop`

University of Pittsburgh HAA news, "Tao and colleagues publish on a 400-year-old Chinese chicken coop" (READ 2026-08-27, source-reader) (https://www.haa.pitt.edu/news/tao-and-colleagues-publish-400-year-old-chinese-chicken-coop)

*Used for:* a late-Ming square coop with six niche openings and eggshell (T59). No size given.

### `zhwiki-liuchu`

zh.wikipedia 六畜 (READ 2026-08-27, source-reader; en.wikipedia 403s) (https://zh.wikipedia.org/wiki/六畜)

*Used for:* the chicken as one of the six livestock (T59).

### `tokushima-yashikigami`

徳島県立図書館 紀要 50, pp. 131-133, 屋敷神 (PDF READ 2026-08-27, source-reader) (https://library.bunmori.tokushima.jp/digital/webkiyou/50/131-133.pdf)

*Used for:* the two patterns (every house / old families only), the SW corner as the local norm, one 40 cm stone hokora, one persimmon 20 m east of a homestead (T58, T57).

### `jawiki-yashikigami`

ja.wikipedia 屋敷神; minka-en.com 屋敷神; satologue.com 屋敷神様 (READ 2026-08-27, source-reader) (https://ja.wikipedia.org/wiki/屋敷神)

*Used for:* the two patterns; a small stone or wooden hokora at the plot's corner, especially the NE 鬼門 (T58).

### `kameyama-yashikigami`

亀山市史 民俗編, 屋敷神 (kameyamarekihaku.jp) - SUMMARY-ONLY: the page would not render on three fetches; a search summary carries 17 of 37 at the NW corner, 11 at the NE (2026-08-27) (https://kameyamarekihaku.jp/sisi/MinzokuHP/jirei/bunrui3/data3-4/index3_4_1.htm; unfetched 2026-08-28)

*Used for:* the NW/NE corner weights (T58), labeled SUMMARY-ONLY.

### `toyoko-kaki`

「農家の庭先にはなぜ柿の木が植えられているのか？」, ameblo.jp/toyoko-housing (READ 2026-08-27, source-reader) (https://ameblo.jp/toyoko-housing/entry-11418946119.html)

*Used for:* a persimmon in every dooryard; Miyazaki Yasusada's encouragement; summer shade for the house (T57).

### `uekipedia-kaki`

植木ペディア カキ (READ 2026-08-27, source-reader) (https://www.uekipedia.jp/落葉広葉樹-カ行/カキ/)

*Used for:* persimmon height 3-20 m (T57). No crown width.

### `326woods-stack`

326-woods.com, 薪の保管方法 (READ 2026-08-27, source-reader) - MODERN stacking practice (https://326-woods.com/2021/02/09/keepwoods/)

*Used for:* a stack to ~1.5 m high (T54), labeled modern.

### `fei-1939`

Fei Hsiao-tung, *Peasant Life in China: A Field Study of Country Life in the Yangtze Valley* (Routledge, 1939) - https://archive.org/details/in.ernet.dli.2015.76327, full text READ 2026-08-28 (the djvu text, grepped)

READ by the session from the downloaded djvu text (671 KB), each quote located by grep. The `source-reader` run of 2026-08-28 could confirm only the boat/village-plan sentences: its fetch truncates the book inside chapter III, so its NOT-FOUND on the silkworm-tray, manure-pit and yu-margin quotes is a tool limit, not an absence; and its CONTRADICTED on the boats is two sentences that both exist - II-4 "Nearly every household possesses at least one boat" and XIV-3 "Nearly every household possesses one or more boats except those who are not engaged in agricultural or fishing work." Average holding "about 8.5 mow" (XI), 3,065 mow over 450 adult men

*Used for:* silkworms reared inside the dwelling on tray stands (five stands of eight 1.5 x 1 m trays per house; every room but the kitchen at the peak); home reeling; nearly every household owning one or more boats and the village laid out along its streams; the village agent boat; manure kept in half-buried earthenware pits behind the house and along the road; mulberry on the 10-30 m raised margin that is also the dyke, houses on it, vegetables beneath it; sheep huts as a 1920s innovation; rice threshed in the open space before the house or the front room

### `fao-ac264e`

FAO/NACA, *Integrated Fish Farming in China*, ch. 7 "Introduction of Chinese integrated fish farming and some major models" (https://www.fao.org/4/ac264e/ac264e09.htm) - READ 2026-08-28

*Used for:* the pig shed "constructed on the pond dyke or over the water surface" (ponds under 8 mu), 1-5 pigs per mu; fish-cum-duck ponds with a fenced dry run on the dike and a wet run in a corner of the water. Modern practice (1980s), cited as the FORM, not as premodern prevalence

### `fao-ac241e`

FAO/NACA, *The Integration of Mulberry Cultivation, Sericulture and Fish Farming* (https://www.fao.org/4/ac241e/ac241e00.htm) - READ 2026-08-28

*Used for:* the dike:water ratio - "each mu of mulberry plants can yield worm dregs, pupae and waste water to provide feeds and fertilizers sufficient for 1 mu of fish ponds. Hence, the ratio of areas of dike and water surface is 1:1", and "the water/dike ratio is 6:4" where other feed is added; pond depth 3.5 m falling to 2.5 m in summer with a 1.5 m slope to the dike top

### `fao-x6708e`

FAO Training Series, *Simple methods for aquaculture: Pond construction*, ch. 10 "Pond outlet structures" (https://www.fao.org/fishery/docs/CDrom/FAO_Training/FAO_Training/General/x6708e/x6708e10.htm) - READ 2026-08-28

*Used for:* the sluice gate, verbatim: "a protected opening in the pond dike that can be easily closed with wooden boards to regulate water level and can be screened to avoid fish losses" (inside width up to 0.8 m); the monk outlet as the older draining structure

### `gd-gazetteer-sangji`

Guangdong Provincial Gazetteer Office (广东省人民政府地方志办公室), 【粤故事】中国第一个机器缫丝厂与桑基鱼塘有何渊源, 2023-08-16 (https://dfz.gd.gov.cn/index/dqyj/content/post_4237091.html) - READ 2026-08-28

*Used for:* the water-to-dike ratio stated as 水基比 "三七至四六开" (3:7 to 4:6); dikes planted 桑、蔗、蕉; Chen Qiyuan's 1873 filature as the point where household reeling met the factory

### `gmrb-2024-sangji`

Guangming Daily, 【这些文化遗存现今的模样87】二千多岁的桑基鱼塘仍未老 (赵玙, 侯楠楠), 2024-03-19 (https://epaper.gmw.cn/gmrb/html/2024-03/19/nw.D110000gmrb_20240319_7-01.htm) - READ 2026-08-28

*Used for:* the form in one line - 将地势低洼处深挖为鱼塘，塘泥堆在鱼塘四周形成塘基; dredging in the seventh and eighth months to rebuild the dikes (七八月清淤，培固塘基); the Huzhou dating (Spring and Autumn origin, Ming-Qing peak)

### `dili360-2005-sangji`

邓芬, "桑基鱼塘 最常见的美景风光不再", 中国国家地理 2005(02) (https://www.dili360.com/cng/article/p5350c3d7e437f08.htm) - READ 2026-08-28

*Used for:* the lost traditional landscape's elements - 塘里养鱼，基上种桑树、种果树; 蕉林蔗海; the 河涌 creek net. No dimensions

### `cssn-sangyuanwei`

中国社会科学网, 水乡农谚见证桑园围发展, 2022-09-23 (https://www.cssn.cn/ztzl/jzz/rwln/wh/lnfw/202209/t20220923_5541513.shtml) - READ 2026-08-27 by the feature-139 search agent (its transcript carries the quotes; the page was not re-fetched by the session)

*Used for:* the Sangyuanwei proverbs - 男贩鱼花，妇女喂爱蚕 (men trade fish fry, women feed the worms), 一船蚕丝出，一船白银归 (a boat of silk out, a boat of silver back), 又以塘泥肥桑; the polder's 窦 sluice named in a place-name saying

### `isis-dykepond`

Mae-Wan Ho, "The Circular Economy of the Dyke-Pond System", ISIS, 2006-10-09 (https://www.i-sis.org.uk/DykePondSystem.php) - READ 2026-08-28; a secondary summary of Ruddle & Zhong 1988, Zhong et al. 1997 and Deng 1987/1993

*Used for:* the numbers it carries from Ruddle & Zhong - "most ponds are rectangular, 0.4 to 0.6 ha in area and 2 to 3 m deep. The dykes are usually 6 to 10 m wide"; the late-1980s land use (fishponds 35%, mulberry 12%, sugar cane 18%); "pigs, chickens and ducks are reared on the dykes"; "ponds are drained two or three times a year, and the mud at the bottom is dredged up to put on the dykes"; dike construction from the mid-fourteenth century

### `ruddle-zhong-1988`

Kenneth Ruddle and Gongfu Zhong, *Integrated Agriculture-Aquaculture in South China: The Dike-Pond System of the Zhujiang Delta* (Cambridge University Press, 1988; URL: none - a print monograph. Cambridge's own subject page title-matches in search but 403s to a fetch, and no catalog record could be confirmed by reading it; a link nobody verified is worse here than an admitted gap, because the interactive map renders it) - SUMMARY-ONLY: the monograph, its Cambridge Core review (Leeds-Harrison 1989) and the Ruddle et al. 1983 *Agricultural Systems* paper all returned 403; the numbers are taken through `isis-dykepond` and the search summaries, labeled so wherever quoted

*Used for:* pond size/depth, dike width, the dike livestock, the dredging cycle (as above)

### `miles-2003`

Steven B. Miles, "From Small Fry to Big Fish: Representing the Rise of Jiujiang Township, Nanhai County, 1395-1657", *Ming Studies* 48 (2003) (https://doi.org/10.1179/014703703788762953) - SUMMARY-ONLY (paywalled; the search summary gives the subject: the township's rise on the fish-fry trade in Ming Nanhai)

*Used for:* fish fry as a Ming-era Pearl-delta trade with its own center

### `mdpi-3860`

*Sustainability* 10(11):3860 (2018) (https://www.mdpi.com/2071-1050/10/11/3860), on the Pearl-delta dike-pond landscape - SUMMARY-ONLY: 403 on both hosts in the feature-139 pass; the "mosaic-like constructed ponds with meandering natural river systems" description in 'Grid vs mosaic' was read in the 2026-07 session that wrote that entry and could not be re-verified

*Used for:* the historical mosaic form versus the modern consolidated grid; ~20 m dikes eroded to under 4 m
### `tenmacho-jawiki`

ja.wikipedia 伝馬町牢屋敷 (READ 2026-08-28, feature 143) (https://ja.wikipedia.org/wiki/伝馬町牢屋敷)

*Used for:* the Edo remand jail's size (2,677坪 ≈ 8,850 m2), its neribei wall and outer moat; that it held 未決囚 pending judgment AND, exceptionally, 永牢・過怠牢 prison-as-sentence cases

### `chuo-royashiki`

Chuo City, 伝馬町牢屋敷跡 (https://www.city.chuo.lg.jp/a0052/bunkakankou/rekishi/tokyobunkazai/royashiki.html; READ 2026-08-28)

*Used for:* corroborating figure "2,600坪（8,595㎡）以上", moat and embankment on three sides, 300-400 inmates at a time, execution ground in the SE corner

### `takayama-jinya-city`

Takayama City, 高山陣屋跡 (https://www.city.takayama.lg.jp/kurashi/1000021/1000119/1000847/1000954/1000956.html; READ 2026-08-28)

*Used for:* the 吟味所 standing with the 白州 ("吟味所、白州はグリ石敷で屋根のあることが特徴的である"); the 御蔵 moved from the castle's third bailey in 1695; the designated site figure "員数 11,219.05平方メートル" (the label reads oddly - recheck against the 史跡 register before relying on it)

### `takayama-jinya-jawiki`

ja.wikipedia 高山陣屋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/高山陣屋)

*Used for:* the 1816 rebuild of the office block as one range - 玄関・吟味所・御役所・大広間; the numbered storehouse rows (一～四番蔵・九～十二番蔵・書物蔵); 25 daikan/gundai over 177 years

### `neixiang-yamen-zhwiki`

zh.wikipedia 内乡县衙 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/内乡县衙)

*Used for:* "前衙后邸" as an instance of the 前朝后寝 system; the jail in the yamen's southwest ("坐北朝南的监狱位于内乡县衙的西南部"); the jail-god shrine to 皋陶 inside the jail (READ); the 衙神庙 and 土地祠 on the east line (SUMMARY-ONLY - seen in a search synthesis of the same page, not quoted)

### `henan-neixiang`

Henan provincial government, "China's best-preserved county-level magistrate office in Neixiang" (https://english.henan.gov.cn/2023/11-23/2853070.html; READ 2026-08-28)

*Used for:* the prison southwest of the Major Court, "usually called South Prison"

### `hatakata-men-jawiki`

ja.wikipedia 畑方免 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/畑方免)

*Used for:* dry-field tax commonly paid in coin, the 関東畑永法 as the type case ("金納で納税が行われることが多かった" - coin, not specifically copper); the rate fixed and not reduced in bad years

### `tfd-hongou-fire-history`

Tokyo Fire Department, 防火対策の歴史 (Hongo station; https://www.tfd.metro.tokyo.lg.jp/fs/hongou/page_00029.html; READ 2026-08-28)

*Used for:* commoners keeping fire-water routinely at the doorway and on the roof ("用水桶、天水桶、鎮火水と名称はいろいろあるが、庶民は平素から水を用意して、玄関先や、屋根上に設置した")

### `gujianchina-taipinggang`

古建中国, 古代故宫的防火器材 - "太平缸" (https://www.gujianchina.cn/news/show-5949.html; READ 2026-08-28)

*Used for:* 308 vats in the Forbidden City; vats placed on the axis and before buildings far from the Inner Golden Water River and wells

### `thepaper-taipinggang`

澎湃新闻, 这口大缸能防火？！ (https://www.thepaper.cn/newsDetail_forward_23268207; READ 2026-08-28)

*Used for:* 308 originally, 231 surviving; Qing regulation fixing which vat type and how many per courtyard

### `guernica-night-soil`

Guernica, "Raising a Stink" (https://www.guernicamag.com/raising-a-stink/; READ 2026-08-28; the Howell OSU paper it draws on could not be parsed)

*Used for:* farmers supplying daimyo estates with firewood and seedlings for the privilege of emptying their privies; the tsuke-tsubo annual contract paid in rice

### `hatchobori-jawiki`

ja.wikipedia 八丁堀 (東京都中央区) (READ 2026-08-28) (https://ja.wikipedia.org/wiki/八丁堀_(東京都中央区))

*Used for:* the yoriki/doshin 組屋敷 district of the Edo town magistracy standing apart from the office after the 1635 temple relocation

### `jinya-jawiki`

ja.wikipedia 陣屋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/陣屋)

*Used for:* a small DOMAIN's jin'ya program - residence, office, retainers' houses, storehouses and a 調練場 drill ground ("小藩の陣屋では…居館・役所・家臣の役宅や土蔵、調練場などを配置する構成がみられる"); scope: a domain seat, not a bakufu daikansho

### `hanko-jawiki`

ja.wikipedia 藩校 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/藩校)

*Used for:* 255 domain schools at the peak, in nearly every domain; martial arts encouraged and 演武場 among their facilities

### `edo-three-dojos-jawiki`

ja.wikipedia 幕末江戸三大道場 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/幕末江戸三大道場)

*Used for:* the three great late-Edo fencing halls and their metropolitan addresses (Nihonbashi, Kanda Otamagaike, Kudan); no date range for the "boom" is given there

### `hei-jokaku-jawiki`

ja.wikipedia 塀 (城郭) (READ 2026-08-28) (https://ja.wikipedia.org/wiki/塀_(城郭))

*Used for:* plastered castle-class earthen walls "壁の厚さは1尺（約300ミリメートル）以上ある", with medieval walls as thin as 3-7 sun

### `kojodan-dobei`

攻城団, お城の基礎講座 40. 土塀の種類 (https://blog.kojodan.jp/entry/2020/08/26/180000; READ 2026-08-28)

*Used for:* frameless neribei "築地塀に比べて…30cm程度"; tsuijibei up to about 1 m thick

### `sado-bugyosho-fires`

Sado magistracy fire history - SUMMARY-ONLY (2026-08-28): search snippets across Sado tourism pages state the 奉行所, built 1603, "焼失と再建を5回繰り返しました"; the three pages fetched (ja.wikipedia 佐渡奉行, visitsado.com, city.sado.niigata.jp museum) describe only the 2000 reconstruction and say nothing about fires (https://www.asoview.com/spot/15224af2172090002/)

*Used for:* administrative halls as ordinary wooden buildings that burned and were rebuilt repeatedly

### `fuchu-kosatsuba`

Tokyo Jinjacho, 府中高札場 (http://www.tokyo-jinjacho.or.jp/goshahou/fuchukousatsuba/; READ 2026-08-26, feature 133 T13)

*Used for:* kosatsuba set "at points of heavy passage: barriers and ports, the foot of large bridges, and the entrances and centers of towns and villages"

### `ogose-kosatsuba`

Ogose town, cultural property H26-04 高札場 (https://www.town.ogose.saitama.jp/kamei/shogaigakushu/bunkazai/kaisetsu/explanation_cultural/H26_04.html; READ 2026-08-26, T13)

*Used for:* village kosatsuba at the village center, the shrine precinct or the assembly place; before the village officials' houses

### `kosatsu-jawiki`

ja.wikipedia 高札 (READ 2026-08-26, T13) (https://ja.wikipedia.org/wiki/高札)

*Used for:* the edict board institution - standing law, rate tables, ban edicts; Nihonbashi as Edo's principal board

### `adachi-kosatsu`

Adachi City museum, 高札 (https://www.city.adachi.tokyo.jp/hakubutsukan/chiikibunka/hakubutsukan/shiryo-kosatsu.html; READ 2026-08-26, T13)

*Used for:* the board read aloud by officials; the headman relaying circulars

### `caishikou-enwiki`

en.wikipedia Caishikou Execution Grounds (READ 2026-08-28, feature 143) (https://en.wikipedia.org/wiki/Caishikou_Execution_Grounds)

*Used for:* the Qing execution ground at the crossroads of Xuanwumen Outer Street and Luomashi Street, "Vegetable Market Execution Ground"; the term 棄市 is not on the page

### `qiushen-zhwiki`

zh.wikipedia 秋审 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/秋审)

*Used for:* the Qing autumn review of death sentences through 刑部, 大理寺, 都察院 and the emperor - the capital case climbs and the confirmed sentence comes back down

### `suzugamori-jawiki`

ja.wikipedia 鈴ヶ森刑場 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/鈴ヶ森刑場)

*Used for:* Suzugamori at Edo's southern entrance on the Tokaido, paired with Kozukappara at the northern entrance on the Nikko kaido ("江戸の北の入口（日光街道）沿いに設置されていた小塚原刑場とともに、南の入口（東海道）沿いに設置されていた刑場であった")

### `kozukappara-jawiki`

ja.wikipedia 小塚原刑場 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/小塚原刑場)

*Used for:* the two as Edo's 二大刑場 - the page names two major grounds, not three

### `shiniuba-jawiki`

ja.wikipedia 死牛馬取得権 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%AD%BB%E7%89%9B%E9%A6%AC%E5%8F%96%E5%BE%97%E6%A8%A9)

*Used for:* the kawata's right to fallen cattle and horses over a defined territory ("死牛馬を集める特定の地域を「草場」ないしは「旦那場」といった"), abolished 1871

### `himeji-shironameshi-jawiki`

ja.wikipedia 姫路白なめし革細工 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%A7%AB%E8%B7%AF%E7%99%BD%E3%81%AA%E3%82%81%E3%81%97%E9%9D%A9%E7%B4%B0%E5%B7%A5)

*Used for:* the white-tawing process - salted hides soaked in the river "数日間" (several days) to loosen the hair, then salt and rapeseed oil under the sun; NOT the "one week summer, two weeks winter" figure the entry carried

### `northampton-tannery-1996`

Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Green, Northampton", Post-Medieval Archaeology 30(1), 1996 (https://www.tandfonline.com/doi/abs/10.1179/pma.1996.002; SUMMARY-ONLY 2026-08-28 - abstract page 403; the 36-37 pit figure seen in search snippets of the abstract)

*Used for:* the largest excavated urban tannery (the Western Tannery, 36-37 pits) as an upper comparison

### `pingyao-shilou-zhwiki`

zh.wikipedia 平遥市楼 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E5%B9%B3%E9%81%A5%E5%B8%82%E6%A5%BC)

*Used for:* "底层面阔、进深各三间，占地133.4平方米，平面呈方形", 18.5 m high, rebuilt 1688

### `dongjing-menghualu-rujia`

吴钩, 大宋消防队 (儒家网, https://www.rujiazg.com/article/11577; READ 2026-08-28), quoting 東京夢華錄

*Used for:* "每坊三百步有军巡铺，又于高处有望火楼，上有人探望，下屯军百人及水桶、洒帚、钩锯、斧权、梯索之类" - the Song fire-watch tower as a separate institution; no citywide tower count

### `kyomachiya-jawiki`

ja.wikipedia 京町家 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E4%BA%AC%E7%94%BA%E5%AE%B6)

*Used for:* the narrow-front deep-lot machiya, and its own rebuttal of the frontage-tax story ("江戸時代の京都の税制は、間口幅に関係なく、まず町に対し総額が賦課され")

### `kyototuu-unagi`

京都通百科事典, 鰻の寝床 (https://www.kyototuu.jp/Life/ProverbUnaginoNedoko.html; READ 2026-08-28)

*Used for:* "間口２間（約３.６m）前後、奥行１０〜１２間（約１８〜２２m）"; carries the popular frontage-tax explanation that `kyomachiya-jawiki` disputes

### `nagaya-jawiki`

ja.wikipedia 長屋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E9%95%B7%E5%B1%8B)

*Used for:* the nagaya as one building divided into units sharing walls ("1棟の建物を水平方向に区分し、それぞれ独立した住戸とした物")

### `hiyokechi-jawiki`

ja.wikipedia 火除地 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E7%81%AB%E9%99%A4%E5%9C%B0)

*Used for:* firebreak lots cut through Edo after the 1657 Meireki fire - breaks at block scale, not between houses

### `song-architecture-enwiki`

en.wikipedia Architecture of the Song dynasty (READ 2026-08-28) (https://en.wikipedia.org/wiki/Architecture_of_the_Song_dynasty)

*Used for:* Tang cities "strictly divided into distinct residential and commercial wards divided by city walls"; under the Song "shops could now line streets in residential areas and did not have to be situated behind precinct walls"

### `guanxiang-zdic`

漢典 zdic.net, 关厢 (READ 2026-08-28) (https://zdic.net/hans/%E5%85%B3%E5%8E%A2)

*Used for:* the bare definition - "城门外的街道及附近区域"; that commerce clustered there is SUMMARY-ONLY (Baidu Baike, 403)

### `jokamachi-jawiki`

ja.wikipedia 城下町 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%9F%8E%E4%B8%8B%E7%94%BA)

*Used for:* samurai quarters ranked by distance from the castle, merchant and artisan quarters outside them, the temple district on the perimeter as part of the defense, and streets kinked and dead-ended to lengthen the approach ("道を鍵形に曲げたり袋小路を設けるなどすることで、城への到達距離を延長した")

### `kichinyado-jawiki`

ja.wikipedia 木賃宿 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%9C%A8%E8%B3%83%E5%AE%BF)

*Used for:* the firewood-fee inn - a common room, bedding at the guest's own expense, guests pooling rice and paying the firewood cost to have it cooked

### `kichinyado-kotobank`

コトバンク 木賃宿 (https://kotobank.jp/word/木賃宿-51029; READ 2026-08-28)

*Used for:* prices - 3 mon a person (1611 ordinance), 6 mon firewood fee (1658), 24 mon roof fee plus 16-24 mon for a futon (1843)

### `hutong-enwiki`

en.wikipedia Hutong (READ 2026-08-28) (https://en.wikipedia.org/wiki/Hutong)

*Used for:* alleys "formed by lines of siheyuan", neighborhoods "formed by joining one siheyuan to another to form a hutong" - the entry's "access routes lined by contiguous courtyard residences" is a paraphrase of this

### `chinese-city-wall-enwiki`

en.wikipedia Chinese city wall (READ 2026-08-28) (https://en.wikipedia.org/wiki/Chinese_city_wall)

*Used for:* "In areas of rugged relief, however, a square form was usually replaced by one of irregular shape, determined in many cases by topographic conditions"

### `thepaper-city-walls`

澎湃新闻, on the plan forms of Chinese city walls (https://m.thepaper.cn/newsDetail_forward_1270378; READ 2026-08-28)

*Used for:* hill cities taking the surrounding high points inside the wall and so producing irregular outlines (荆州's oval, 北京's 凸 plan)

### `xian-wall-zhwiki`

zh.wikipedia 西安城墙 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89%E5%9F%8E%E5%A2%99)

*Used for:* "城垣高12米，底宽15-18米，顶宽12-14米"; "城墙的外壁筑98座敌台，延伸出墙12米，宽20米，高与城齐"

### `hakone-seki-jawiki`

ja.wikipedia 箱根関 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E7%AE%B1%E6%A0%B9%E9%96%A2)

*Used for:* the facility list - 面番所 (上御番所・番士詰所・休息所・風呂場) and 向番所 (所詰半番・休息所・牢屋), stables, 辻番, 高札場, all inside a fence; that the two stations face each other across the road is SUMMARY-ONLY (search synthesis of hakonesekisyo.jp)

### `wengcheng-zhwiki`

zh.wikipedia 瓮城 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E7%93%AE%E5%9F%8E)

*Used for:* the barbican definition - a half-round or square outwork before a gate (Nanjing's 中华门 the inside-the-gate exception)

### `genbukan-jawiki`

ja.wikipedia 玄武館 (READ 2026-08-28 - the page gives no aggregate disciple count; search syntheses split between ~3,000 from 清河八郎's roster and "over 6,000") (https://ja.wikipedia.org/wiki/%E7%8E%84%E6%AD%A6%E9%A4%A8)

*Used for:* the Genbukan as a metropolitan commercial dojo (1822, Nihonbashi then Kanda); the disciple count is SUMMARY-ONLY and contested

### `cdlib-local-elites`

Esherick & Rankin (eds.), *Chinese Local Elites and Patterns of Dominance*, introduction (UC Press e-book, https://publishing.cdlib.org/ucpressebooks/public/book/chinese-local-elites-and-patterns-of-dominance.html; READ 2026-08-28)

*Used for:* "By Qing times, the substantially urbanized gentry were living the leisured life of absentee landlords in administrative centers or the many small towns that lined the canals"; absentee landlords acting through agents and rent bursaries

### `kaifeng-flood-1642-enwiki`

en.wikipedia 1642 Yellow River flood (READ 2026-08-28) (https://en.wikipedia.org/wiki/1642_Yellow_River_flood)

*Used for:* "300,000 of the 378,000 residents were killed by the flood and ensuing peripheral disasters"; the levee breached by the Ming governor during the siege

### `kaifeng-pmc7048742`

Storozum et al., "Geoarchaeological evidence of the AD 1642 Yellow River flood that destroyed Kaifeng", Scientific Reports 2020 (PMC 7048742; READ 2026-08-28) (https://doi.org/10.1038/s41598-020-60169-1)

*Used for:* the Yellow River flooding Kaifeng "around 40 times over the past 3000 years" - the entry's "seven times" is found nowhere

### `pan-gate-enwiki`

en.wikipedia Pan Gate (READ 2026-08-28) (https://en.wikipedia.org/wiki/Pan_Gate)

*Used for:* "two separate gates, one opening to a road ... and another opening to a canal", Suzhou's Land and Water Gate; the sluiced arch is SUMMARY-ONLY (chinahighlights)

### `tetsu-to-hagane-91`

History of Iron and Steel Making Technology in Japan, Tetsu-to-Hagané 91(1), JStage (READ at the 2026-08 pass, feature 107; not re-read 2026-08-28) (https://doi.org/10.2355/tetsutohagane1955.91.1_2)

*Used for:* the two-stage refining of tatara iron

### `ohitayama-tatara-enwiki`

en.wikipedia Ohitayama Tatara Iron Works (READ 2026-08) (https://en.wikipedia.org/wiki/Ohitayama_Tatara_Iron_Works)

*Used for:* dōba, ōkajiba, wari-tetsu; the Chugoku mountains' 80% share

### `wagner-ming-iron`

Donald Wagner, *Iron production in three Ming texts* (https://donwagner.dk/MingFe/MingFe.html; READ 2026-08)

*Used for:* the chao fining hearth as Song Yingxing describes it; the 200 charcoal producers / 200 furnace tenders / 300 miners

### `wagner-fining-puddling`

Donald Wagner, *Traditional Chinese fining and puddling* (http://donwagner.dk/arch-iron/eu/fining-puddling-china-eu.html; READ 2026-08)

*Used for:* fining as stir-frying pig iron under blast

### `xuxiebian-han-fining`

*Cast Iron Smelting and Fining: an Eastern Han site at Xuxiebian, Sichuan* (Project MUSE 725769; READ 2026-08) (https://muse.jhu.edu/article/725769; unfetched 2026-08-28)

*Used for:* the practice running back to the Eastern Han

### `fao-charcoal-safety`

FAO, *Simple technologies for charcoal making*, ch. 5 safety precautions (https://www.fao.org/4/X5555E/x5555e06.htm; READ 2026-08)

*Used for:* self-heating of fresh charcoal, fines as the worst case, the 24-hour open-air rule and the 8-day threshold

### `tonya-enwiki`

en.wikipedia Ton'ya (READ 2026-08) (https://en.wikipedia.org/wiki/Ton%27ya)

*Used for:* the wholesaler-warehouseman of the Edo economy

### `fires-in-edo-enwiki`

en.wikipedia Fires in Edo (READ 2026-08) (https://en.wikipedia.org/wiki/Fires_in_Edo)

*Used for:* the winter clustering of serious fires

### `sizes-koku`

Sizes.com, "What is the unit called a koku?" (https://www.sizes.com/units/koku.htm; READ 2026-08)

*Used for:* the charcoal hyō as a bale of indeterminate size

### `nanbu-date-mounds-enwiki`

en.wikipedia Nanbu-Date border mounds (READ 2026-08) (https://en.wikipedia.org/wiki/Nanbu-Date_border_mounds)

*Used for:* the earth-mound boundary between Morioka and Sendai, reconfirmed 1642

### `kuniezu-enwiki`

en.wikipedia Kuniezu (READ 2026-08) (https://en.wikipedia.org/wiki/Kuniezu)

*Used for:* the shogunate's provincial maps with boundaries drawn

### `mukoyama-linear-borders`

Mukoyama, "Linear borders in early modern Japan", European Journal of International Relations (https://journals.sagepub.com/doi/full/10.1177/13540661221133206; READ 2026-08)

*Used for:* domains building a territorial order of agreed boundaries and mutual exclusion

### `irripro-jiegao-lulu`

History of Irrigation - irrigation tools (http://www.irripro.net/en/nd.jsp?id=113; READ 2026-08) with Baidu Baike *Lulu* (a weaker reference)

*Used for:* the shadoof and the windlass; the Ming-Qing upgrade to animal power and deeper wells

### `ide-japanese-experience`

IDE, *Passing on "The Japanese Experience"*, rural society (https://d-arch.ide.go.jp/je_archive/english/society/wp_je_unu4.html; READ 2026-08)

*Used for:* hatake vs suiden; small farmers on "rainfall or natural underground sources"; the defeated late-Tokugawa hata irrigation schemes

### `harie-kabata`

Harie Shozu no Sato, the kabata wells (https://ihcsacafe-en.ihcsa.or.jp/news/harie/; READ 2026-08)

*Used for:* the domestic and social character of the village well

### `kabu-ido-commons`

Groundwater commons and the kabu-ido rules, *Water History* (https://link.springer.com/article/10.1007/s12685-022-00302-1; READ 2026-08 - abstract)

*Used for:* villages regulating the NUMBER of wells

### `kochi-seiri-jawiki`

ja.wikipedia 耕地整理 (READ 2026-08-28, feature 143) (https://ja.wikipedia.org/wiki/%E8%80%95%E5%9C%B0%E6%95%B4%E7%90%86)

*Used for:* rectangular plot consolidation as a Meiji institution - the Shizuoka method of 1872, the 耕地整理法 of 1899/1900, "区画の整形化と正方位化"

### `nougyoudoboku-keihan`

のうぎょうとぼく, 水田圃場における畦畔について (https://nougyoudoboku.com/a-ridge-between-rice-fields/; READ 2026-08-28)

*Used for:* the standard bund - "法面勾配1:1・高さ30cm・上幅30cmの台形が標準" (so ~3 ft at the base), cold regions ~50 cm top / ~40 cm high

### `seijoue-kotobank`

コトバンク 正条植 (https://kotobank.jp/word/正条植-85971; READ 2026-08-28)

*Used for:* straight-row planting rare before Meiji, promoted nationally in the 1890s-1900s together with the hand-pushed inter-row weeder (田打車), planting ropes and rulers

### `seijoue-seika`

精華町 せいか舎, 正条植え (https://seikasya.town.seika.kyoto.jp/essays/seijoue; READ 2026-08-28)

*Used for:* seijoue spreading in Meiji and bringing weeder-based weeding and mid-season cultivation with it

### `kubota-transplanting`

Kubota, 稲作の歴史 - 田植え (https://www.kubota.co.jp/kubotatanbo/history/tools/transplanting.html; READ 2026-08-28)

*Used for:* the 1890s adoption, ropes and rolled frames marking the lines

### `kokudaka-jawiki`

ja.wikipedia 石高 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E7%9F%B3%E9%AB%98)

*Used for:* one koku as an adult's annual rice ("一石は大人一人が一年に食べる米の量に相当する"), with the page's own hedge that real stipends ran ~1.8 koku of brown rice

### `gokogomin-kotobank`

コトバンク 五公五民 (https://kotobank.jp/word/五公五民-64520; READ 2026-08-28)

*Used for:* the tax rate - 四公六民 in early Edo, 五公五民 after the Kyōhō era (1716-36)

### `satoyama-enwiki`

en.wikipedia Satoyama (READ 2026-08-27 T34/T42 and 2026-08-28) (https://en.wikipedia.org/wiki/Satoyama)

*Used for:* the border zone between foothills and arable flat land; the mosaic of forest, paddy, dry field, grassland and ponds; Edo-era leaf gathering for paddy fertilizer; cutting every 15-20 years

### `louzeyuan-zhwiki`

zh.wikipedia 漏澤園 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E6%BC%8F%E6%BE%A4%E5%9C%92)

*Used for:* Cai Jing's 1104 proposal; siting "高曠不毛之地，四周建有圍欄"; plots numbered by the 千字文 with name, origin and dates; continued through Yuan and Ming

### `toribeno-jawiki`

ja.wikipedia 鳥辺野 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E9%B3%A5%E8%BE%BA%E9%87%8E)

*Used for:* the great Kyoto burial ground with "範囲について、明確な定義はない" - an unbounded hillside field

### `fushimi-inari-senbon`

伏見稲荷大社, 千本鳥居 (https://inari.jp/sp/map/spot_07/; READ 2026-08-28)

*Used for:* "稲荷山全体で約1万基、そのうち千本鳥居は約800基"; donated by worshippers from the Edo through Meiji periods

### `meiji-jingu-jawiki`

ja.wikipedia 明治神宮 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%98%8E%E6%B2%BB%E7%A5%9E%E5%AE%AE)

*Used for:* the shrine's torii - the page counts 8, not 3; no spacing figures

### `religion-song-enwiki`

en.wikipedia Religion in the Song dynasty (READ 2026-08-28) (https://en.wikipedia.org/wiki/Religion_in_the_Song_dynasty)

*Used for:* "In 1221, records counted the existence of 400,000 monks and 61,000 nuns in the dynasty" - the one census figure actually read

### `chang-jiang-jawiki`

ja.wikipedia 長江 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E9%95%B7%E6%B1%9F)

*Used for:* the reach names - 沱沱河 -> 通天河 -> 金沙江 -> 川江 (宜賓-宜昌) -> 荊江 -> 揚子江 (from the 揚子津 ferry)

### `shinano-gawa-jawiki`

ja.wikipedia 信濃川 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E4%BF%A1%E6%BF%83%E5%B7%9D)

*Used for:* "信濃川と呼ばれているのは新潟県域で、長野県に遡ると「千曲川」と呼称が変わる"

### `sumida-gawa-jawiki`

ja.wikipedia 隅田川 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E9%9A%85%E7%94%B0%E5%B7%9D)

*Used for:* 大川, 浅草川, 宮戸川 as names of the same river; 両国川 not confirmed there

### `yato-jawiki`

ja.wikipedia 谷戸 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E8%B0%B7%E6%88%B8)

*Used for:* yatsu as easily-worked paddy land given drainage; iriai rights over the adjacent woods (firewood - the reed-bed application is the entry's extension)

### `shitsuden-kotobank`

コトバンク 湿田 (https://kotobank.jp/word/湿田-74168; READ 2026-08-28)

*Used for:* the poorly drained paddy that never dries; wet-to-dry conversion beginning in late Yayoi western Japan

### `hibiya-irie-jawiki`

ja.wikipedia 日比谷入江 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%97%A5%E6%AF%94%E8%B0%B7%E5%85%A5%E6%B1%9F)

*Used for:* infill from 1592 with the spoil of the Nishinomaru works, in earnest from 1603, complete in early Edo

### `sotobori-jawiki`

ja.wikipedia 外濠 (東京都) (READ 2026-08-28) (https://ja.wikipedia.org/wiki/外濠_(東京都))

*Used for:* "外濠川は、日比谷入江へ注ぐ平川の流路を移設した開削で作られた" - the Hirakawa turned into the moat

### `bitchu-takamatsu-jawiki`

ja.wikipedia 備中高松城 and 備中高松城の戦い (READ 2026-08-28) (https://ja.wikipedia.org/wiki/高松城_(備中国))

*Used for:* "低湿地にある沼城", "低湿地帯でこれらが天然の堀を形成していた"; the 1582 water siege raising a 200 ha lake

### `kagawa-tameike-structure`

香川県, ため池の構造 (https://www.pref.kagawa.lg.jp/tochikai/about_tameike/repair/structure.html; READ 2026-08-28 - the page behind the older `kagawa-tameike` key)

*Used for:* the intake as one facility - 斜樋/堅樋 into the 底樋 discharging to the canal, plus a sediment drain

### `offtake-angle-studies`

Diversion-angle hydraulics (SUMMARY-ONLY 2026-08-28: search syntheses of several ResearchGate / ScienceDirect papers - "maximum water discharge and minimum sediment discharge when its diversion angle was 30° or 45° among 90°, 75°, 60°, 45°, and 30°"; a 30° angle cutting sediment entry by up to 64%; no paper read) (https://www.sciencedirect.com/science/article/abs/pii/S1001627920300706; unfetched 2026-08-28)

*Used for:* the acute downstream-pointing offtake, 30-45° over 90°

### `fao-pond-water`

FAO, *Water for animals* ch. 6 surface reservoirs (https://www.fao.org/4/r7488e/r7488e06.htm; READ 2026-08-28)

*Used for:* evaporation (up to 2 m/yr) and seepage as the losses of a standing reservoir; the page states the losses in prose, not as the balance equation

### `desire-path-enwiki`

en.wikipedia Desire path (READ 2026-08-27, feature 133 T32; cites Hampton and Cole 1988 for the fifteen-passage figure) (https://en.wikipedia.org/wiki/Desire_path)

*Used for:* "as few as 15 passages over a site can be enough to create a distinct trail"; a desire path "usually represents the shortest or the most easily navigated route", sidestepping slopes and obstacles

### `ninety-nine-pi-desire`

99% Invisible on desire paths (READ 2026-08-27, T32) (https://99percentinvisible.org/article/least-resistance-desire-paths-can-lead-better-design/)

*Used for:* corroborating the desire-line reading

### `ma-2024-desire-paths`

Ma, Brandt, Seipel and Ma (2024), *Environment and Planning B* - agent-based desire paths (SUMMARY-ONLY: paywalled/403; abstract READ via ideas.repec.org, T45, and found to be about a field-of-view angle, NOT turn minimization) (https://doi.org/10.1177/23998083231184884; unfetched 2026-08-28)

*Used for:* nothing load-bearing - recorded as the case where a search summary recast a parameter as a finding

### `pmc7538448-levee`

"Earthworm species and density in semi-natural grasslands on rice paddy levees in Japanese satoyama", PMC 7538448 (READ 2026-08-27, T41) (https://pmc.ncbi.nlm.nih.gov/articles/PMC7538448/)

*Used for:* levees "constructed and maintained to retain water in the paddies and to allow the passage of people and transportation of tools"; "farmers generally maintain levee grasslands by periodic mowing"

### `paddy-field-enwiki`

en.wikipedia Paddy field (READ 2026-08-27, T41) (https://en.wikipedia.org/wiki/Paddy_field)

*Used for:* plots "separated by bunds approximately 10 cm in height" (a Korean example)

### `irri-bund-summary`

IRRI Rice Knowledge Bank on bund height (SUMMARY-ONLY 2026-08-27, T45 - unreachable; the "15-150 cm" range seen nowhere) (http://www.knowledgebank.irri.org/step-by-step-production/pre-planting/land-preparation/how-to-construct-bunds; unfetched 2026-08-28)

*Used for:* bunds built ~20 cm to avoid overflow - summary only

### `visit-toyama-sankyoson`

Visit Toyama, the Tonami dispersed settlement (https://visit-toyama-japan.com/en/travel-inspiration/sankyoson; READ 2026-08-24)

*Used for:* farmers building "in the middle of their cultivated rice fields so that they could easily manage the water for their own rice fields"; ~7,000 farmsteads over ~220 km2 with their kainyo groves

### `mdpi-sho-fan-groundwater`

Sho River alluvial-fan groundwater study, *Geosciences* 11(8):352 (https://www.mdpi.com/2076-3263/11/8/352; READ 2026-08-24)

*Used for:* shallow groundwater on the fan as a mix of river water and paddy recharge - a well anywhere on the fan finds water

### `geography-hub-satoyama`

The Geography Hub, "Japan's Satoyama Landscapes" (READ 2026-08-27, T34) (https://thegeographyhub.com/japans-satoyama-landscapes/)

*Used for:* leaf litter to fertilizer, oak and chestnut cut cyclically, sunlight reaching the floor

### `uehara-2009-agris`

Uehara et al. 2009, on Rhododendron in the abandoned satoyama coppice forest (AGRIS record; READ 2026-08-27, T34) (https://agris.fao.org/search/fr/records/64724aabe17b74d2224f9430)

*Used for:* a managed coppice floor under a cut canopy

### `waldrand-dewiki`

de.wikipedia Waldrand (READ 2026-08-27, T45 - found when the English "Woodland edge" page did not carry the terms) (https://de.wikipedia.org/wiki/Waldrand)

*Used for:* the three-layer edge: herb fringe, shrub belt, forest mantle

### `pmc7898781-fukugi`

"Distribution and utilization of homestead windbreak Fukugi trees", PMC 7898781 (READ 2026-08-27, T45) (https://pmc.ncbi.nlm.nih.gov/articles/PMC7898781/)

*Used for:* Okinawan homestead windbreaks planted around 300 years ago

### `ijc-yamaguni`

International Journal of the Commons, "External impacts on traditional commons ..." - the Yamaguni district study (READ 2026-08-27, T36) (https://thecommonsjournal.org/articles/10.18352/ijc.348)

*Used for:* "each of the 11 villages in Yamaguni district has its own unique institutions for managing its customary common property forests"; no boundary description

### `kichijoji-enwiki`

en.wikipedia Kichijōji (READ 2026-08-27, T36) (https://en.wikipedia.org/wiki/Kichijōji)

*Used for:* a village laid out on strip lots from a road - dropped from the coppice argument

### `phyllostachys-enwiki`

en.wikipedia Phyllostachys bambusoides (READ 2026-08-27, T42) (https://en.wikipedia.org/wiki/Phyllostachys_bambusoides)

*Used for:* madake's uses - baskets, fans, sheaths for food and geta, shakuhachi

### `pmc5723622-bamboo-range`

The moso/madake range study, PMC 5723622 (READ 2026-08-27, T42) (https://pmc.ncbi.nlm.nih.gov/articles/PMC5723622/)

*Used for:* bamboo's distribution and cold tolerance (around -18 to -20 C)

### `bamboo-growers-hardiness`

Grower pages on madake hardiness - completebamboo.com and two others (READ 2026-08-27, T45) (https://completebamboo.com/species_bamboo/Phyllostachys_bambusoides.html)

*Used for:* "-15 C, zone 7" and -18 to -23 C - a spread, not a number

### `tsuijimatsu`

tsuijimatsu.com (READ 2026-08-27, T42) (https://tsuijimatsu.com/)

*Used for:* bamboo in the homestead setting

### `packer-2017-phragmites`

Packer et al. 2017, Biological Flora of *Phragmites australis*, J. Ecology (https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/1365-2745.12797; READ 2026-08-26)

*Used for:* the hydrosere - open water, littoral, reed swamp, sedge meadow, swamp woodland, dry ground

### `kushiro-mire-2014`

Kushiro Mire alder invasion, *Ecohydrology & Hydrobiology* 2014 (https://www.sciencedirect.com/science/article/abs/pii/S1642359314000706; READ 2026-08-26 - abstract)

*Used for:* reed marsh invaded by alder where it dries

### `otanoshike-2004`

Otanoshike wetland, *Ecological Research* 2004 (https://link.springer.com/article/10.1111/j.1440-1703.2004.00644.x; READ 2026-08-26 - abstract)

*Used for:* grassland with *Spiraea* shrubs at the marsh margin

### `mlit-vegetation-classes`

MLIT/NILIM river-environment vegetation classes (https://www.nilim.go.jp/lab/fbg/ksnkankyo/mizukokuweb/system/maegaki.files/shiryo2.pdf; READ 2026-08-26)

*Used for:* the willow (タチヤナギ) and alder (ハンノキ) communities of Japanese wet margins

### `hotes-wetland-diversity`

Hotes, wetland ecosystem diversity, *Global Environmental Research* 12(1) (https://www.airies.or.jp/attach.php/6a6f75726e616c5f31322d316a706e/save/0/0/12_1-04.pdf; READ 2026-08-26)

*Used for:* Japanese wetland zonation

### `plos-2016-pine`

PLOS One 2016 (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0153972; READ 2026-08-26)

*Used for:* pine's intolerance of waterlogged ground

### `gymnosperm-densiflora`

The Gymnosperm Database, *Pinus densiflora* (https://www.conifers.org/pi/Pinus_densiflora.php; READ 2026-08-26) with the Mt. Takao museum page

*Used for:* red pine as a tree of dry, well-drained slopes - never a reed edge

### `maff-drain-shape`

MAFF, 排水路の形状・構造と適用条件 (技術書 20-23; https://www.maff.go.jp/j/nousin/noukan/tyotei/kizyun/pdf/04_hojou_hata_gijutsusho20-23.pdf; READ 2026-08-12)

*Used for:* drain gradients and sections

### `senjochi-jawiki`

ja.wikipedia 扇状地, with MLIT land-classification notes (READ 2026-08-12) (https://ja.wikipedia.org/wiki/扇状地)

*Used for:* the three fan zones 扇頂 / 扇央 / 扇端 and the 扇端 spring line where the wet toe begins

### `kohai-shicchi-jawiki`

ja.wikipedia 後背湿地 and 自然堤防 (with GSI notes; READ 2026-08-12) (https://ja.wikipedia.org/wiki/後背湿地)

*Used for:* backswamp formation behind the natural levee and its land use

### `kashima-kainyo-1987`

The 1987 (昭和62年) survey of Kashima (鹿島), Tonami city, 46 households, as reported by Tonami City's digital archive 砺波正倉, 「砺波市の屋敷林」 (https://1073shoso.jp/www/sankyo/detail.jsp?id=18666; READ 2026-08-28, feature 134 T48): 「昭和６２年の砺波市鹿島（世帯数４６戸）での調査によると、直径１０センチ以上の全樹木数１，５４２本の内、スギは７３５本で全体の約半数の４８パーセントを占め、１戸当たり平均１６本であった」 - 1,542 trees of DBH >= 10 cm over 46 households (33.5 per homestead), 735 sugi (48%), 16 sugi per house. The primary 1987 report is not online; the figures were VERIFIED against the city's page on 2026-08-28 after the GM asked whether the pointer was hallucinated (it was a summary-only pointer from the 2026-07 pass). Corroborating: https://www.city.tonami.lg.jp/info/7389p/ (123,647 / 4,773 = 25.9 trees (>= ~3 m tall) per grove-owning household in 2020 - same order of magnitude as 33.5 trees >= 10 cm per homestead in 1987, consistent with the documented post-2000 decline (wind-throw, felling).); https://www.jstage.jst.go.jp/article/esj/ESJ51/0/ESJ51_0_271/_article/-char/ja/ (Sugi as the dominant kainyo species in Tonami; ~18 woody species per homestead when shrubs are counted (the 1987 figure of ~6 species is for >= 10 cm trunks only).); https://www.jstage.jst.go.jp/article/jjsrt/46/1/46_154/_pdf/-char/ja (A single typical grove (S family, 2020) also has sugi as the dominant species by basal area; confirms a body of Tonami grove surveys from ~1975 onward and names the Research Institute bulletin where the 1987-era survey data would have been published.)

*Used for:* the real scale of a homestead grove stand

### `cssn-sangji-yutang`

中国社会科学网, 从生态美学视角研究桑基鱼塘 (https://www.cssn.cn/ztzl/jzz/rwln/wh/lnfw1/202209/t20220923_5541481.shtml; READ 2026-08-28, feature 143)

*Used for:* the classic ratio named as "基六塘四" (dike six, pond four - note the order); early dikes planted with mulberry, tea, vegetables and fruit, fruit-dike ponds the commonest; mulberry dominant from the late Ming in Nanhai and Shunde

### `cssn-jiangnan-weitian`

中国社会科学网, 古代江南圩田开发及其社会效应 (https://cssn.cn/lsx/lsx_zgs/202502/t20250217_5844872.shtml; READ 2026-08-28)

*Used for:* "中有河渠，外有门闸。旱则开闸引江水之利，涝则闭闸拒江水之害" - channels inside, gates on the outside, opened in drought and shut in flood; the tangpu spacing "五里七里一横塘、七里十里一纵浦"

### `sdlib-shunde-jitang`

顺德图书馆, 发现顺德·经济篇 - 桑基鱼塘 (https://www.sdlib.com.cn/home/article/detail/id/741.html; READ 2026-08-28)

*Used for:* the dike built from the pond's own spoil ("取泥覆四周为基，中凹下为塘"), planted with mulberry ("基种桑"), hemp, soybeans, peanuts and melon trellises; the Song 桑园围, the Jiajing spread, the Xianfeng-Tongzhi peak

### `usu-windbreak`

Utah State University Extension, Windbreak Benefits and Design (READ 2026-08-28) (https://extension.usu.edu/forestry/publications/utah-forest-facts/005-windbreak-benefits-and-design)

*Used for:* "Windbreaks reduce wind speeds up to 30 times their height (H) downwind"

### `miragenews-polders`

Mirage News, "China's Water Heritage: Significance of Polders" (XJTLU; https://www.miragenews.com/chinas-water-heritage-significance-of-polders-955573/; READ 2026-08-28)

*Used for:* "By the early 20th century, they were further compartmented into even smaller islet-like polders, dubbed as fish-scale polders or yulin wei (鱼鳞圩), for their shapes as seen on aerial photos"; after 1949 "the organic forms of polders were replaced by standardised rectangular patterns for industrialised agricultural production"

### `fusekoshi-jawiki`

ja.wikipedia 伏越 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/伏越)

*Used for:* the inverted siphon as a method "historically seen in old waterways" - 見沼代用水の柴山伏越, 大垣輪中の鵜森伏越樋

### `suirokyo-jawiki`

ja.wikipedia 水路橋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/水路橋)

*Used for:* the aqueduct bridge carrying water over rivers and valleys (通潤橋, 明正井路, 水路閣 - the page does not date them)

### `yashikirin-jawiki`

ja.wikipedia 屋敷林 (居久根 redirects here; READ 2026-08-28) (https://ja.wikipedia.org/wiki/屋敷林)

*Used for:* igune on the north and west of the homestead as windbreak and snowbreak; the species named - スギ, マツ, ヒノキ, ケヤキ (three evergreen conifers and one deciduous broadleaf; the page never says "evergreen-heavy")

### `kuwa-jawiki`

ja.wikipedia クワ (READ 2026-08-28) (https://ja.wikipedia.org/wiki/クワ)

*Used for:* cultivated mulberry "低木仕立てが多い" - kept as a low shrub; the height and density figures are SUMMARY-ONLY (search syntheses: low-trunk mulberry under 70 cm, 1.2 m an optimal feeding height; 800-1,000 plants per mu in Jiangsu/Zhejiang, 5,000-6,000 in Guangdong)

### `aburana-jawiki`

ja.wikipedia アブラナ and zh.wikipedia 油菜 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/アブラナ)

*Used for:* rape sown in autumn, overwintering, cut in March-April (the food crop's calendar); rape sown into the harvested paddy and plowed in before the next transplanting (a Taiwan double-crop practice) - neither page gives the rice months

### `wanli-fishpond-summary`

The Shunde (顺德) dike-pond figures, VERIFIED on readable pages on 2026-08-28 (feature 134 T48, after the GM asked whether the summary-only pointer was hallucinated): 40,084 mu of ponds in 1581 (万历九年) and 58,094 mu in 1642 - 广州日报 (https://gzdaily.dayoo.com/h5/html5/2023-07/05/content_871_829964.htm) and the Shunde Archives timeline; the 4.6% / 6.7% shares are those figures over the 8,700 顷 (870,000 mu) of cultivated land 吴建新 gives from 广东通志 (https://gzdaily.dayoo.com/h5/html5/2023-07/05/content_871_829964.htm) - derived, not read as such; "至光绪末年，县境禾田占总耕地面积不到十分之一，大部分成为鱼塘" (https://www.163.com/dy/article/D4OSJLAR0514D0GJ.html); the late-1980s survey - the main dyke-pond area 86,632 ha, 35% fishponds, 25% irrigated rice (https://www.i-sis.org.uk/DykePondSystem.php); the 1581 taxable fishponds of Nanhai, Shunde and Panyu, ~160,000 mu, from 珠江三角洲农业志 (https://www.gz.gov.cn/zt/lmgzssst/content/post_10195754.html). CONTRADICTED and struck: "Longshan (龙山) over half pond in 1581" - the archives give 8,124 of 44,947 mu = 18% in 1581 (https://www.163.com/dy/article/D4OSJLAR0514D0GJ.html); "over half" (75%, 乡之塘倍于田) is the Qianlong-Jiaqing figure; the 1581 wording traced to an uncited blog copied into zh.wikipedia 基塘农业.

*Used for:* the scale of the sixteenth-century dike-pond zone, with that caveat

### `chang-morphology-walled-capitals`

Sen-dou Chang, "The Morphology of Walled Capitals", in Skinner (ed.), *The City in Late Imperial China* (http://web.stanford.edu/~mel1000/sen.pdf; cited by the feature 009 pass, 2026-07, as its strongest source; not re-read 2026-08-28)

*Used for:* the sparse street net of a Chinese county seat, the deliberately unbuilt intramural reserve, the civic share - with 009's own caveat that the circulation percentage is triangulated, not measured

### `tedai-jawiki`

ja.wikipedia 手代 (READ 2026-08-28, feature 143 leftovers) (https://ja.wikipedia.org/wiki/手代)

*Used for:* "手代の多くは、村役人・町役人の子弟である" - most tedai were children of village and town officials, hired from peasants and townsmen who knew the district; nothing about birth order

### `mingguanci-zhwiki`

zh.wikipedia 名宦祠 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/名宦祠)

*Used for:* "名宦祠用以祭祀有政績的地方官" - the hall venerating local officials of merit, standing at the Confucian temple (east of the Dacheng gate), Ming Hongwu onward - a state institution, not a yamen's own predecessor shrine

### `shoinzukuri-jawiki`

ja.wikipedia 書院造 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/書院造)

*Used for:* "これら連続した室の南側には、入り側を介して庭が広がっていた" - the garden on the south of the formal rooms; nothing on the north service side

### `economy-song-enwiki`

en.wikipedia Economy of the Song dynasty (READ 2026-08-28; replaces the Grokipedia page of the same title) (https://en.wikipedia.org/wiki/Economy_of_the_Song_dynasty)

*Used for:* "Historian Robert Hartwell estimates that per capita iron output rose sixfold between 806 and 1078, such that, by 1078 China was producing 127,000,000 kg (125,000 t) in weight of iron per year"; Bao Qingtian on iron households given "government support, such as charcoal supplies and skilled craftsmen"

### `loess-plateau-enwiki`

en.wikipedia Loess Plateau (READ 2026-08-28; replaces the Grokipedia *History of agriculture in China*) (https://en.wikipedia.org/wiki/Loess_Plateau)

*Used for:* "40-60% of the precipitation concentrate in June to August" - the summer concentration; the 400-800 mm range is not on the page

### `kawara-jawiki`

ja.wikipedia 瓦 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/瓦)

*Used for:* "江戸時代になっても一般庶民の家屋は板葺きが一般的で瓦葺きが普及したのは江戸時代末期のこと" - commoners' houses board-roofed; tile widespread only at the end of Edo

### `kashi-jawiki`

ja.wikipedia 河岸 and 雁木 (港湾) (READ 2026-08-28) (https://ja.wikipedia.org/wiki/河岸)

*Used for:* the kashi as a river port and landing that grew into a warehouse and merchant district; gangi as the stairs at a landing used to load and unload cargo

### `chaoguan-zhwiki`

zh.wikipedia 鈔關 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/鈔關)

*Used for:* "税关是中國明清兩代，政府在货物集散地和水陆要冲设立的关卡" - Ming-Qing customs barriers at commodity centers and strategic water and land routes (the eight great chaoguan on the Grand Canal), not at a county seat's gates

### `takayama-coverage-summary`

Takayama Jin'ya site and building areas - SUMMARY-ONLY (2026-08-28): a search synthesis gives "敷地面積は3,000坪、建物面積は1,000坪" (~33% coverage); the 御蔵 "年代、規模共に全国有数の穀物土蔵" (https://www.city.takayama.lg.jp/kurashi/1000021/1000119/1000847/1000954/1000956.html)

*Used for:* the jin'ya's built coverage and the granary's standing, both unread

### `fukagawa-kiba-summary`

Fukagawa kiba, the Edo lumber yards - SUMMARY-ONLY (2026-08-28): fifteen timber wholesalers bought ~300,000 m2 in 1701; the yards were ordered out of the city after the 1657 Meireki fire because in-town timber yards spread fire (https://www.mokuzai-tonya.jp/03about_us/history/index.html)

*Used for:* the lumber yard as a waterfront works far larger than a shophouse, sited out of the built core

### `nanjing-wall-enwiki`

en.wikipedia City Wall of Nanjing (READ 2026-08-28) (https://en.wikipedia.org/wiki/City_Wall_of_Nanjing)

*Used for:* the Ming circuit built "in a winding, free style, based on the city's complicated topography" with the river as its moat; the 35.267 km length is SUMMARY-ONLY (aggregator sites)

### `shanghai-xiancheng-zhwiki`

zh.wikipedia 上海县城 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E4%B8%8A%E6%B5%B7%E8%80%81%E5%9F%8E%E5%8E%A2)

*Used for:* "1553年为抵御溯江而上的倭寇第一次修建了环城的城墙" and its 圆形轮廓; "one season" not stated

### `hyojosho-jawiki`

ja.wikipedia 評定所 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E8%A9%95%E5%AE%9A%E6%89%80)

*Used for:* the Hyōjōsho standing "江戸城外の辰ノ口" - OUTSIDE Edo castle at Tatsunokuchi (present Marunouchi 1-chome)

### `tamagawa-josui-jawiki`

ja.wikipedia 玉川上水 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E7%8E%89%E5%B7%9D%E4%B8%8A%E6%B0%B4)

*Used for:* "高低差92.3メートルの間に全長42.74キロメートル"; distribution into the city from the 水番所 at Yotsuya Ōkido; wooden and stone pipes underground below it (no total km given)

### `suidobashi-jawiki`

ja.wikipedia 水道橋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%B0%B4%E9%81%93%E6%A9%8B)

*Used for:* the bridge renamed for the Kanda josui's 御茶ノ水懸樋 crossing after the Meireki fire

### `edo-36-mitsuke-jawiki`

ja.wikipedia 江戸城三十六見附 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%B1%9F%E6%88%B8%E5%9F%8E%E4%B8%89%E5%8D%81%E5%85%AD%E8%A6%8B%E9%99%84)

*Used for:* "俗に江戸城には36の見付があったといわれ" - and the page's own hedge that the real count was higher ("66、90など諸説あり")

### `karamete-jawiki`

ja.wikipedia 搦手 and 大手門 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%90%A6%E6%89%8B%E9%96%80)

*Used for:* the karamete-mon as the rear gate opposite the ōte-mon (generic; Edo not named; no divination reasoning)

### `xian-moat-zhwiki`

zh.wikipedia 西安城墙 (moat section; READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E8%A5%BF%E5%AE%89%E5%9F%8E%E5%A2%99)

*Used for:* "城墙的外侧有护城河，宽20米，深10米，终年积水，和城墙共同构成完整的防御体系"

### `osaka-castle-jawiki`

ja.wikipedia 大坂城 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%A4%A7%E5%9D%82%E5%9F%8E)

*Used for:* the Yodo and its tributaries below the northern plateau "天然の堀の機能を果たすとともに、城内の堀へと水を引き込むのに利用された"

### `suzaku-oji-jawiki`

ja.wikipedia 朱雀大路 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%9C%B1%E9%9B%80%E5%A4%A7%E8%B7%AF)

*Used for:* Heian-kyō's avenue "幅82メートル（延喜式）"; Chang'an's "幅147メートル"

### `tokaido-jawiki`

ja.wikipedia 東海道 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%9D%B1%E6%B5%B7%E9%81%93)

*Used for:* "慶長9年2月に大久保長安その他に命じて街道の幅員を5間とし" - 5 ken (~9 m, ~29.5 ft) in 1604

### `changan-enwiki`

en.wikipedia Chang'an (READ 2026-08-28) (https://en.wikipedia.org/wiki/Chang%27an)

*Used for:* walled wards and the market drum; the Tang ward count is SUMMARY-ONLY (109-110 usually; "108" the popular figure)

### `kuramae-jawiki`

ja.wikipedia 蔵前 (READ 2026-08-28; 浅草御蔵 404) (https://ja.wikipedia.org/wiki/%E8%94%B5%E5%89%8D)

*Used for:* "浅草御蔵は、隅田川の右岸に上流から一番、二番と数える8本の堀を作り" - eight numbered channels into the storehouse ground

### `horikawa-nagoya-jawiki`

ja.wikipedia 堀川 (名古屋市) (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%A0%80%E5%B7%9D_(%E5%90%8D%E5%8F%A4%E5%B1%8B%E5%B8%82))

*Used for:* dug in 1610 under Fukushima Masanori for the castle's construction materials; the 舟入堀 count of nine in Edo is SUMMARY-ONLY (ja.wikipedia 舟入 is a disambiguation page)

### `sento-jawiki`

ja.wikipedia 銭湯 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E9%8A%AD%E6%B9%AF)

*Used for:* "文化年間（1804〜1818年）には、人口約100万〜120万人の江戸全体で600軒以上の銭湯があった" - the record's "523 in 1810" is a search-summary figure

### `shichiya-jawiki`

ja.wikipedia 質屋 (READ 2026-08-28 - no Edo count on the page; the "2,700+" is SUMMARY-ONLY, also in `town-deep-audit.md`'s darumapedia pointer) (https://ja.wikipedia.org/wiki/%E8%B3%AA%E5%B1%8B)

*Used for:* pawnbroking as the commoner's bank

### `edo-sanza-jawiki`

ja.wikipedia 江戸三座 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%B1%9F%E6%88%B8%E4%B8%89%E5%BA%A7)

*Used for:* the three playhouses licensed by the town magistracy after consolidation from many, to four, to three

### `kasoba-jawiki`

ja.wikipedia 火葬場 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E7%81%AB%E8%91%AC%E5%A0%B4)

*Used for:* by ~1650 almost every temple in Asakusa and Shitaya cremating in its precinct; ~20 temple crematoria moved to the Kozukappara area in 1667 after smoke troubled a shogunal visit; the 1873 proposal to ban cremation over smoke and odor (rescinded ~1875)

### `bernstein-fire-and-earth`

Andrew Bernstein, "Fire and Earth: The Forging of Modern Cremation in Meiji Japan", JJRS 27/3-4 (2000) - the Nanzan copy returned only a stub; READ via the secondary account at unseen-japan.com/meiji-japan-cremation-ban-attempt/ (2026-08-28): "In May 1873, they suggested relocating crematoriums, notably the Senju temple ones, outside the city's 'red line' (shubiki, 朱引)"; "the severe stench injures people's health" (https://doi.org/10.18874/jjrs.27.3-4.2000.297-178)

*Used for:* the May 1873 shubiki proposal and the stench rationale - SUMMARY-ONLY as to Bernstein's own text

### `changmen-zhwiki`

zh.wikipedia 阊门 (READ 2026-08-28) (https://zh.wikipedia.org/wiki/%E9%98%8A%E9%97%A8)

*Used for:* the Ming-Qing Changmen district "全中国最繁盛的商业街区", its radial streets outside the wall and tens of thousands of shops

### `nisshinkan-jawiki`

ja.wikipedia 日新館 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%97%A5%E6%96%B0%E9%A4%A8)

*Used for:* the reconstructed school's 弓道場・武道場; the lecture-hall pairing as doctrine is not stated

### `bodaiji-jawiki`

ja.wikipedia 菩提寺 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E8%8F%A9%E6%8F%90%E5%AF%BA)

*Used for:* the lineage temple "一家が代々その寺の宗旨に帰依して、先祖の菩提を弔う寺院"; 檀那寺 under the danka system

### `sando-jawiki`

ja.wikipedia 参道 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%8F%82%E9%81%93)

*Used for:* the approach "街道筋など人通りの多いところから社寺に至る道"; highways sometimes bent to bring them nearer a shrine

### `azolla-enwiki`

en.wikipedia Azolla (READ 2026-08-28, leftovers pass) (https://en.wikipedia.org/wiki/Azolla)

*Used for:* Azolla planted on flooded paddies, "the rotting plant material ... releases nitrogen into the water for the rice plants"; the Anabaena symbiont is in the page's biology section, not in the passage read

### `daxiangguo-enwiki`

en.wikipedia Daxiangguo Temple (READ 2026-08-28) (https://en.wikipedia.org/wiki/Daxiangguo_Temple)

*Used for:* the Kaifeng monastery managing "64 departments ... with several thousand of monks" - more than the record's "1,000+"

### `adashino-jawiki`

ja.wikipedia 化野 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%8C%96%E9%87%8E)

*Used for:* "かつては風葬の地", later a cremation ground with Toribeyama; one of Kyoto's three great burial grounds (西の化野・東の鳥辺野・北の蓮台野)

### `fukada-kotobank`

コトバンク 深田 and ja.wikipedia ヨシ (READ 2026-08-28) (https://kotobank.jp/word/%E6%B7%B1%E7%94%B0-123763)

*Used for:* 深田 "どろの深い田。沼田" - the deep-mud paddy; reed cutting after the rice harvest as a seasonal custom; the Meiji-drainage persistence and the iriai framing not on either page

### `magariya-jawiki`

ja.wikipedia 曲屋 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%9B%B2%E3%82%8A%E5%AE%B6)

*Used for:* "南側に厩が母屋の下手に接続して突出し" - the stable projecting on the south, joined to the house, warmed by the kitchen hearth; nothing on the well

### `kayabuki-jawiki`

ja.wikipedia 茅葺 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E8%8C%85%E8%91%BA)

*Used for:* thicker thatch "より急勾配が要求される" - the steep pitch as a material requirement; no degree figure

### `weinei-he-summary`

圩内河 canal forms - SUMMARY-ONLY (2026-08-28): a 中国国家地理 feature seen in search: "河道有十字、丁字、月状、弓状等多种形状 ... 河道两端直达圩田堤岸，并建闸控制蓄水和滞洪" (https://www.dili360.com/cng/article/p5fb1f39c3bbad41.htm; unfetched 2026-08-28)

*Used for:* the crescent and bow canal forms and the gated ends of the polder's internal channels

### `dikepond-erosion-summary`

Dike-pond landscape 1949-2020 (Shunde) - SUMMARY-ONLY (2026-08-28): "size of ponds increased while that of dikes decreased between 1967 and 2016"; the 20 m -> <4 m magnitude not seen (https://doi.org/10.1016/j.aquaculture.2021.737741; unfetched 2026-08-28)

*Used for:* the direction of consolidation - ponds growing, dikes shrinking

### `rice-rape-calendar-summary`

Yangtze rice-rape rotation calendar - SUMMARY-ONLY (2026-08-28, agricultural-extension pages in search): rape sown late September to mid-October, harvested early April (southern Jiangxi) to early May (Jiujiang); rice transplanted mid-April to early May (https://www.ecoagri.ac.cn/article/doi/10.12357/cjea.20240340?viewType=HTML)

*Used for:* the two halves of one plot's year - with the sowing window a little earlier than the record's Oct-Nov

### `hancho-jawiki`

ja.wikipedia 藩庁 (READ 2026-08-28, T20) (https://ja.wikipedia.org/wiki/%E8%97%A9%E5%BA%81)

*Used for:* "城持大名以上の藩は城に、城主格以下の城主格と無城大名の藩は城を構えることが許されなかったことから、領内に屋敷を置いて藩庁とした" - a castle-holding han's seat was AT the castle; a castle-less han's was its jin'ya

### `honmaru-jawiki`

ja.wikipedia 本丸 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%9C%AC%E4%B8%B8)

*Used for:* "近世における本丸は、城主とその家族が暮らす奥御殿と政庁である表御殿を置き" - the goten's public half named as the 政庁

### `kakegawa-castle-jawiki`

ja.wikipedia 掛川城 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E6%8E%9B%E5%B7%9D%E5%9F%8E)

*Used for:* "政務所である二ノ丸御殿" at a ~51,000-59,000 koku domain - the administration office in the ninomaru goten; ja.wikipedia 川越城 (170,000 koku) likewise puts the lord's residence and a 武具方役所 in the ninomaru

### `karo-jawiki`

ja.wikipedia 家老 (READ 2026-08-28) (https://ja.wikipedia.org/wiki/%E5%AE%B6%E8%80%81)

*Used for:* the karō deciding in council ("評定所などに集合して合議の上で決裁する") and keeping their mansions "城の近く" - near the castle; no ring named

### `goyobeya-kotobank`

コトバンク 御用部屋 (READ 2026-08-28 - the SHOGUNATE's executive room inside Edo castle, near the shogun's quarters; analogy only, not han evidence) (https://kotobank.jp/word/%E5%BE%A1%E7%94%A8%E9%83%A8%E5%B1%8B-66403)

*Used for:* the executive council room inside the seat of government

### `mineta-2007-tameike`

嶺田拓也, 「生態系配慮の基礎知識（その3）― 水田とため池の植物相 ―」, 農業農村工学会誌 (Journal of the JSIDRE) 75(8), 2007, pp. 745-748 (https://www.jstage.jst.go.jp/article/jjsidre2007/75/8/75_8_745/_pdf) - READ 2026-08-29 (the PDF itself, by a `source-reader`)

*Used for:* the finding that CONTRADICTS "a managed reservoir has a bare margin" - a Kagawa Prefecture study found a statistically significant POSITIVE correlation between emergent- and floating-leaf plant species counts and the practice of dredging silt and cutting algae, and it is the ponds whose water use has stopped that lose diversity; and for the zonation of reed and cattail (ヨシやガマなどの大型抽水植物) by water depth and slope. The one number-bearing source behind the rule that a tameike's shallow shore is reeded.

### `tameike-jawiki`

ウィキペディア日本語版 ため池 (https://ja.wikipedia.org/wiki/%E3%81%9F%E3%82%81%E6%B1%A0) - READ 2026-08-29

*Used for:* the embankment being managed by forbidding cultivation and by mowing and controlled burning, TO KEEP THE BANK STRONG, and the dry-grassland herbs (not wetland plants) that grow there as a result - the independent confirmation of the GM's T54 rule that reeds keep off a raised planted bank. An encyclopedia article, cited for a plainly-stated maintenance practice that the prefectural and MAFF sources corroborate.

### `kagawa-tameike-structure`

香川県 ため池の構造 (https://www.pref.kagawa.lg.jp/tochikai/about_tameike/repair/structure.html) - READ 2026-08-29

*Used for:* the dam's water-contact slope being armored against wave erosion - 捨石、石張り、コンクリートブロック張 - i.e. one part of a reservoir's shore is bare by engineering, which is why the rule is positional rather than a single answer for the whole margin.

### `maff-tameike-shizen`

農林水産省, 自然環境に果たす役割 - 2. ため池 (https://www.maff.go.jp/j/council/seisaku/nousin/seibibukai/gijutu_syoiinkai/h14-1/pdf/data3-2.pdf) - READ 2026-08-29 (the PDF, page 1)

*Used for:* the land-to-water zonation of a gently-sloping natural shore - riparian forest, wet-meadow, emergent, floating-leaf, submerged - with the emergent belt named as ヨシ・ガマ・マコモ. Note the diagram credits 桜井義雄『水辺の環境学』, which was NOT read; the zonation is cited from this document, one step from that figure.

### `nies-tameike`

国立環境研究所, ため池の生物とその環境 (https://www.nies.go.jp/biology/data/tameike.html) - READ 2026-08-29

*Used for:* the low-diversity end of the spectrum being the urbanized, concrete-armored, eutrophic pond (six dragonfly species) rather than the farmed one - the check that "managed" and "bare" are not the same axis.

### `inamino-tameike-museum`

いなみ野ため池ミュージアム, 水生植物 (https://www.inamino-tameike-museum.com/pond-creature/aquatic-plants.html) - READ 2026-08-29

*Used for:* reed, wild rice and lesser cattail forming colonies around LOWLAND tameike specifically - a tameike-scoped corroboration of the zonation, from an institution documenting a real pond cluster in Hyogo.

### `ohmi-yoshi`

公益財団法人淡海環境保全財団, ヨシとは (https://www.ohmi.or.jp/yoshi/about/whats/) - READ 2026-08-29

*Used for:* the reed-harvest economy - winter cutting for yoshizu screens, thatch and summer shoji, and an uncut bed going 荒れる - and, just as importantly, for the SCOPE LIMIT recorded against it: this foundation is named for Lake Biwa and every example on the page is a lake or river reed bed. It is cited as evidence about lake and river reed beds ONLY. Nothing found puts that economy on tameike margins, and the research entry says so rather than extending it.

### `wang-ochiai-2022`

Wang Jingying and Ochiai Chiho, "Spatial composition and building techniques of farmhouses prone to windstorms: a case study in Arakawa Village, Shiga Prefecture, Japan", *Journal of Asian Architecture and Building Engineering* 21:6 (2022), DOI 10.1080/13467581.2021.1972810 (https://doi.org/10.1080/13467581.2021.1972810) - READ 2026-08-29 by a `source-reader`, full text via a text-extraction proxy after tandfonline, DOAJ, CORE and ResearchGate each returned 403 to a direct fetch; the article is Gold open access (CC BY), confirmed through the Semantic Scholar API.

*Used for:* the 72.7% of toilets sited southeast-to-south for solar warmth to speed fermentation of night soil - the figure the GM ruled be used literally as the seat share. Also used for what it does NOT say: its wind-siting finding covers storage buildings and retirement houses rather than toilets, and it contains no leeward/downwind/odor/hygiene language, which is what CONTRADICTED the proposal to seat privies downwind.


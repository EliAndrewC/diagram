# Documents only a person can reach - the list for the GM (feature 232)

*Twelve cases, from 162 notes. Ordered by what each buys the record, not alphabetically. Every one had
all three recovery routes tried first - a browser user agent, an open-access check at Unpaywall and
OpenAlex, and a hunt for a repository copy - and each entry says which route failed and how.*

**Three of these need one browser visit and nothing else. Four need a library or an Internet Archive
borrow. Four are genuinely closed and two of those four are not worth your time; they are listed so the
record shows they were judged rather than forgotten.**

---

## A. One browser visit. Open access or free to read, stopped only by a bot wall.

These are articles whose LICENSE permits anyone to read them. A JavaScript challenge or a TLS quirk stops
an automated client and does not stop a browser. Opening the page and saving the PDF settles each.

### A1. The kabu-ido paper - the highest-value item on this list

- **"The Kabu-ido system and factors affecting local groundwater extraction control: case study of a
  customary groundwater management in Japan"**, *Water History*, 2022. DOI `10.1007/s12685-022-00302-1`.
- **License CC-BY**, confirmed twice (Unpaywall `is_oa: true`, `license: cc-by`; Semantic Scholar the same).
- PDF: `https://link.springer.com/content/pdf/10.1007/s12685-022-00302-1.pdf`
- **Blocked by**: Springer returns HTTP 200 with a 3 KB HTML stub instead of the PDF, to every fetcher.
  No second location exists in OpenAlex, no Wayback capture of the PDF.
- **Why it matters most**: it is the one piece of evidence that CUTS AGAINST this project's deliberate
  two-to-three-times well liberty - villages capping their own well numbers to limit conflict. Evidence
  against our own decision is worth more than evidence for it.
- Being CC-BY, once read it can be quoted at length with no rights question.

### A2. The Manchu village layout paper

- Ushijima, M. et al., **"Spatial composition and premise arrangement of traditional Manchu village in
  Northeast China"**, *Japan Architectural Review*, 2020. DOI `10.1002/2475-8876.12146`. **CC-BY-NC-ND**
  (DOAJ lists CC-BY-SA).
- **Blocked by**: a Cloudflare "Just a moment" JavaScript challenge at Wiley, on both the article and the
  direct PDF, and DOAJ serves the same challenge.
- **Settles**: whether rear-access ground behind housing lots is separately documented, which is what
  makes our back-lane rule a pattern rather than our own invention.

### A3. The linear-borders paper

- Koyama, Naomu, **"The Eastern cousins of European sovereign states? The development of linear borders
  in early modern Japan"**, *European Journal of International Relations*, 2022.
  DOI `10.1177/13540661221133206`. **CC-BY**.
- **Blocked by**: the same Cloudflare challenge, at SAGE.
- **Settles**: that early modern Japanese domains built a territorial order with agreed boundaries - the
  general claim that licenses drawing a linear clan border on a map at all.

### A4. The dike-pond landscape article

- Tian, M., **"Seeing from Above: Observation of Contemporary Dike-Pond Landscape"**, *Landscape
  Architecture Frontiers* 7(4), 2019, pp. 130-138. DOI `10.15302/J-LAF-1-050004`. Free to read at the
  publisher (Semantic Scholar: BRONZE).
- **Blocked by**: `journal.hep.com.cn` refuses this container at the TLS layer on every route tried -
  two TLS profiles, the DOI resolver, the direct PDF link, a third-party mirror. Not a paywall.
- **Settles**: the "mosaic-like ponds, boundary blurred" sentence our record paraphrases. **Note**: the
  record's current quotation does NOT match the source's wording, so this is a correction as well as a
  citation.

### A5. The Takayama Jinya excavation report - a rate limit, not a refusal

- 上嶋善治, 「史跡高山陣屋跡」, 『岐阜県文化財保護センター調査報告書1』, 1992.
- It is in the free national archive of site reports: `https://sitereports.nabunken.go.jp/`
- **Blocked by**: HTTP 429, twice, several minutes apart. The report is there and downloadable; the
  reader simply hit the rate limit.
- **Settles**: the 3,000 tsubo site and 1,000 tsubo built figures, and with them a coverage band the
  record currently carries as a GUESS "pending that report". **This one is a near-certain win.**

### A6. One page carrying the Chinese irrigation standard

- `https://gf.cabr-fire.com/article-61195.htm` - a Chinese building-code mirror that a search result
  showed carrying section 6.4 of **GB 50288-2018**, the canal cross-section design clause.
- **Blocked by**: connection failed outright, HTTP 000, no response at all.
- **Settles**: two numbers nothing readable carries - a canal bed-setting figure and a 5 m main.
- **Context**: the standard itself is otherwise beyond reach (antpedia refuses even a browser user agent;
  the only open mirror is a scan with no text layer; the vendors sell it rather than publish it). But a
  provincial guideline subordinate to it, `T/JSSLKX 002-2021`, was found openly readable and has already
  closed eight notes, so this page is now a top-up rather than a blocker.

---

## B. A library card or an Internet Archive borrow

### B1. Buck, *Land Utilization in China* (1937) - two notes depend on it

- John Lossing Buck, *Land Utilization in China: A Study of 16,786 Farms in 168 Localities...
  1929-1933*. Chicago, 1937, three volumes.
- **Blocked by**: the Internet Archive item `landutilizationi0000buck` is lending-restricted AND has no
  OCR layer at all - its full-text endpoint answers "No hOCR or Abbyy file present", so even
  search-inside does not exist. HathiTrust is search-only on a 1937 US imprint. No DOI, so the
  open-access services have nothing to answer with.
- **Settles**: (a) whether Buck's survey really gives about 2% of farm area under graves, **and at what
  scale** - all farm area, cultivated area or crop area differ materially in Buck and our sentence says
  "all farm area"; (b) his parcel counts per farm.
- **How much it changes**: the grave figure is our only quantitative anchor for the Chinese contrast and
  is currently carried as a guess. A different denominator would change the comparison the maps draw.
- A substitute was found for the parcel half (King, *Farmers of Forty Centuries*, full text at Project
  Gutenberg), so the book is now needed for the grave figure specifically.

### B2. The Kodaira city history, homestead-grove text

- 『小平市史 地理・考古・民俗編』, Kodaira City, in the こだいらデジタルアーカイブ on ADEAC:
  `https://adeac.jp/kodaira-lib/text-list/d100010/ht002070` (and a sibling at `ht002170`).
- **Blocked by**: a JavaScript page-image viewer, 521 pages, no OCR text layer served. A person can read
  the images; a fetcher gets a navigation shell.
- **Settles**: whether the 70 tsubo (231 sq m) figure is a measured one, and **what was measured** - the
  whole homestead lot or the work yard. It is the upper anchor of our work-yard size band, so if it is
  the lot, the top of that band is wrong.

---

## C. Genuinely closed. Two are worth it, two are not.

### C1. Miles 2003 - worth it

- Steven B. Miles, **"From Small Fry to Big Fish: Representing the Rise of Jiujiang Township, Nanhai
  County, 1395-1657"**, *Ming Studies*, 2003. DOI `10.1179/014703703788762953`.
- Unpaywall: `is_oa: false`, `oa_status: closed`, **no open location of any kind**. Not a fetcher problem.
- **Settles**: the whole of our claim that the delta's fry center dates from the Ming.

### C2. The Mekong junction-angle paper - low value, listed for completeness

- **"The occurrence of obtuse junction angles and changes in channel width below tributaries along the
  Mekong River"**, *Earth Surface Processes and Landforms*. DOI `10.1002/esp.2165`. Unpaywall: closed.
- It would turn "tributaries curve to join pointing downstream" from a general reading into a measured
  majority with a named exception class. **It changes nothing the map draws.** Skip unless it is free to you.

### C3. Kinoshita 1995 - skip

- **"Household Size, Household Structure, and Developmental Cycle of a Japanese Village"**, *Journal of
  Family History* 20(3), 1995. DOI `10.1177/036319909502000302`. Unpaywall: closed.
- The claim it supports is a SETTING number - your own "median household size is generally assumed to be
  5" - which is canon and exempt from the citation rule. Only the historical gloss beside it is
  unciteable, and the record already presents that as support rather than as the basis. **Not worth a
  purchase.**

### C4. The Otanoshike wetland paper - skip unless you have institutional access

- **"Effects of scale-dependent factors on herbaceous vegetation patterns in a wetland, northern
  Japan"**, *Ecological Research* 19, 2004. DOI `10.1111/j.1440-1703.2004.00644.x`. Unpaywall: closed,
  no repository copy, CiNii unreachable from here.
- A real paywall, not a bot block, so a person without a subscription cannot read it either. The reader
  named two open J-STAGE papers that carry the same wetland zonation, and one of them has already been
  used to close a neighbouring note. **The smallest stake on this list.**

---

## Part 2 - what came of the first list, and what the second pass added

*Written after you fetched what you could on 2026-09-12 and after three second-pass batches read the notes
the first pass left open.*

### What your fetch settled, and the two that were never blocks

You saved everything reachable to `/host-l7r-repo/academic-sources/`, and four items came back as
something other than a bot wall:

- **`sitereports.nabunken.go.jp`** - the Nara site-report archive. You got a site-is-down error, so the
  429 this session recorded was the host's own trouble and not a refusal aimed at an automated client.
  The 1992 Gifu report behind it is still wanted; it is a matter of trying again another day.
- **`gf.cabr-fire.com`** - times out for you too. Another outage rather than a block.
- **Miles 2003** and the rest of the closed section - not free to read for you either, which is what
  "genuinely closed" was meant to say. Those four are settled: they stay uncited, and the claims they
  would have supported keep their absence notes.

### New asks from the second pass

Five documents, each named to the volume and page where one exists, each with the route that failed.

1. **GB 50288, *Technical code for irrigation and drainage engineering*** (China). Both readable Chinese
   documents in the water pass defer to it BY NUMBER, so it is the parent of two standards already in the
   record. Wanted for the siting of a headworks intake on a bend and for sediment exclusion
   (`cities/river-cities.html` fn-18c). `antpedia.com/standard/7931413-1.html` serves a navigation shell
   with no text; its PDF mirror answers 403. No third location found. A purchased or library copy closes
   one note and firms up another.
2. **Hao Chunwen (郝春文), "The way of life of Dunhuang monks and nuns in the late Tang, Five Dynasties and
   early Song"** - a PUBLIC PDF that no tool here can read:
   `https://buddhist-art.arthistory.northwestern.edu/buddhistweb/essays/ho_chunwen9.PDF`. It downloads at
   127 KB and its font declares a non-standard character collection, so every text extractor returns
   nothing or mojibake. **A normal PDF viewer opens it.** It would settle whether a monastery's own oil
   account is quotable for `religion-and-death.html` fn-38, which currently rests on a page that narrows
   the claim from sale to donation.
3. **Kinoshita Mitsuo (木下光生), "A basic study of early-modern funeral-goods dealers" (近世葬具業者の基礎的研究)**,
   *The History of Osaka* no. 57 (2001), pp. 61-87. NCID AN0026826X, NDL id 5787865, CiNii
   `https://cir.nii.ac.jp/crid/1521699230921906944`. Not online at all - a local historical society's
   journal, bibliographic record only. A Japanese research library, or NDL's in-library digital
   transmission, settles the Japanese half of `religion-and-death.html` fn-43.
4. **Kobayashi Tsutomu (小林力), "The function and form of the yashikibatake in the Koto region"**,
   *Human Culture: Bulletin of the School of Human Cultures, University of Shiga Prefecture* vol. 29
   (2011), pp. 48-61. CiNii `https://cir.nii.ac.jp/crid/1520572359297949696`. The title is the question
   `homesteads.html` fn-91 asks. The university repository answers **HTTP 406** to every request shape
   tried, including full browser headers; university bulletins of this vintage are usually deposited
   openly, so the PDF probably exists behind a request this reader could not produce.
5. **Two older works, lower stakes.** 白井・成瀬 1983 on the ため池台帳 registers, for a village tank's
   command area (no national dataset carries it); and Perkins, *Agricultural Development in China:
   1368-1968* (1969), for farm households per hectare in a premodern paddy plain. Neither is obviously
   online.

### Two questions that are yours to rule on, not to fetch

Neither of these is a document. Each is a claim the record makes that the reading could not support, where
the next step is a decision rather than a search.

- **The caravan inn's second story.** The record draws it two-story; the one attested analogue read in this
  pass is single-story. Keep the two-story form as a deliberate deviation, or bring the drawing down.
- **The Xuxiebian site name** (`urban-features.html` fn-62). A named excavated Sichuan smelting site is
  asserted, and the authority on Han iron names it in neither of the two works of his that are readable in
  full, searched character by character. Either you know where the name came from, or it should go - the
  Han claim itself stands without it, on that author's own hedged wording plus the Hongdaoyuan tomb relief.

---

## Where to put what you find

`/host-l7r-repo/academic-sources/`, as usual. A filename naming the work is enough; this session reads
from there and writes the footnote from the passage, the same as for a page it fetched itself.

# Sources to download - the working list

**This is the canonical list, kept in the diagram repository (feature 313).** Your file in `academic-sources/` is a copy of
it. Mark the copy as you go; nothing else in it needs editing.

**Marking an entry.** Under each heading are three lines. Turn `[ ]` into `[x]` for what happened:

- **downloaded** - you have the whole work, saved in `academic-sources/`.
- **partial** - you have only part of it, such as the abstract or an excerpt.
- **paywalled** - it needs a paid or institutional login. It can be ticked with partial, when the abstract was free.
- **not found** - you could not find it anywhere. Tick it alone.
- **Found elsewhere** - tick it with downloaded or partial when what you have came from somewhere other than the links
  given, and write where after `where:`.
- **Saved as** is optional: the file's name, if you want to save the session matching your download to its entry.

**When you are ready, say "ingest".** The session records your marks here, archives the files you saved, and tells you
about anything it could not settle. **Say "sync"** to have your copy replaced by this list, with the entries added since
your last sync. Sync refuses while your copy holds marks that have not been ingested, so nothing you mark is lost.

New entries are only ever added at the very end of the file, never in between, so once you have worked to the end of a
part, that part stays done.

---

<!-- high-risk: imported from specs/312-uncited-source-catalog/high-risk-sources.md -->
## High-risk sources: download before feature 312 can close

The GM, 2026-10-02 (verbatim in `request.md`): a cited source the archive cannot fetch now may never have been read, so
what the record says it says is at unusually high risk of being wrong. These come FIRST, ahead of the regular
`/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`. Feature 312 is not complete until the GM has downloaded each one (into
`academic-sources/`, which `make archive-inbox` archives) or reported it cannot be found, and a `source-reader` and
`quote-check` have confirmed that each says what the record says it says.

How the list was made (observed 2026-10-02): the cited URLs archived `partial` with under 200 characters of text, captured
again one at a time with `make archive URL=`; these still refused. Their keys from the manifest rows; what rests on each
from a grep of its key over `research/questions/*.notes.html`; how it was read from the HTML comments in its registry entry.

## Tier 1 - a footnote rests on it (7)

Each was recorded as read by an earlier session or a `source-reader`, by a route other than a plain fetch; verify that it
says what the footnotes quote.

### H1. Tokyo Museum Collection (ToMuCo), "炭俵" (charcoal bale), Edo-Tokyo Museum accession 90007940 (`edo-tokyo-sumidawara`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://museumcollection.tokyo/works/6531424/)**
- Fallback: [Google: Tokyo Museum Collection (ToMuCo), "炭俵" (charcoal bale), Edo-Tokyo Museum accessi](https://www.google.com/search?q=Tokyo%20Museum%20Collection%20%28ToMuCo%29%2C%20%22%E7%82%AD%E4%BF%B5%22%20%28charcoal%20bale%29%2C%20Edo-Tokyo%20Museum%20accession%2090007940)
- **Rests on it:** "How our maps draw straw bales of rice and charcoal (tawara)" (`research/questions/0199-straw-bales-of-rice-and-charcoal-tawara.drawing.html`); "Straw bales of rice and charcoal (tawara)" (`research/questions/0199-straw-bales-of-rice-and-charcoal-tawara.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 through WebFetch by a source-reader (feature 267); the host refuses the container's own fetch (403)
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H2. IRRI Rice Knowledge Bank, sun drying and drying-floor area (`irri-drying-floor`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](http://web.archive.org/web/20230624043456/http://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm)**
- Fallback: [Google: IRRI Rice Knowledge Bank, sun drying and drying-floor area](https://www.google.com/search?q=IRRI%20Rice%20Knowledge%20Bank%2C%20sun%20drying%20and%20drying-floor%20area)
- **Rests on it:** "How our maps draw threshing and drying yards (niwa)" (`research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html`); "Threshing and drying yards at farmhouses (niwa)" (`research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at http://web.archive.org/web/20230624043456/http://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm (feature 195) | READ 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 429 (feature 309).

### H3. Storozum et al., "Geoarchaeological evidence of the AD 1642 Yellow River flood that destroyed Kaifeng", Scientific Reports 2020 (PMC 7048742) (`kaifeng-pmc7048742`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7048742/)**
- Fallback: [Google: Storozum et al., "Geoarchaeological evidence of the AD 1642 Yellow River flood t](https://www.google.com/search?q=Storozum%20et%20al.%2C%20%22Geoarchaeological%20evidence%20of%20the%20AD%201642%20Yellow%20River%20flood%20that%20destroyed%20Kaifeng%22%2C%20Scientific%20Repor)
- **Rests on it:** "Cities on rivers" (`research/questions/0175-cities-on-rivers.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7048742/ (feature 195) | READ 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H4. L5R Wiki (Fandom), "Seidō" (`l5r-fandom-seido`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://l5r.fandom.com/wiki/Seid%C5%8D)**
- Fallback: [Google: L5R Wiki (Fandom), "Seidō"](https://www.google.com/search?q=L5R%20Wiki%20%28Fandom%29%2C%20%22Seid%C5%8D%22)
- **Rests on it:** "How our maps draw a village shrine's monk, the monk's dwelling (kuri), its records and its land" (`research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 272), from the page's wikitext as the site's public MediaWiki API returns it, fetched with curl; the page itself refuses automated fetches (403) and opens in a browser
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H5. "Drought characteristics and their impact on vegetation net primary productivity in the climate-sensitive transition zone", PLOS ONE (2026), doi 10.1371/journal.pone.0343746 (`plos-transition-zone-drought`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://pmc.ncbi.nlm.nih.gov/articles/PMC12935246/)**
- Fallback: [Google: "Drought characteristics and their impact on vegetation net primary productivity](https://www.google.com/search?q=%22Drought%20characteristics%20and%20their%20impact%20on%20vegetation%20net%20primary%20productivity%20in%20the%20climate-sensitive%20transition%20zon)
- **Rests on it:** "How our maps place and draw wells (ido)" (`research/questions/0196-communal-wells-ido.drawing.html`); "Communal wells (ido)" (`research/questions/0196-communal-wells-ido.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12 in full through PubMed Central; open access
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H6. Kojima Nobuyasu, 「How the acting superintendent of Sensoji was appointed in the late early-modern period」 (translated; original: 「近世後期における浅草寺別当代の就任過程」), Soka University institutional repository (`kojima-sensoji-bettodai`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://soka.repo.nii.ac.jp/record/35917/files/sokahogaku28_1_2.pdf)**
- Fallback: [Google: Kojima Nobuyasu, 「How the acting superintendent of Sensoji was appointed in the ](https://www.google.com/search?q=Kojima%20Nobuyasu%2C%20%E3%80%8CHow%20the%20acting%20superintendent%20of%20Sensoji%20was%20appointed%20in%20the%20late%20early-modern%20period%E3%80%8D%20%28translated%3B%20o)
- **Rests on it:** "City temples: their precincts, buildings and monks (garan)" (`research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 272 B37); fetched with curl and read through pdftotext, the fetch tool returning only the PDF's bytes
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 406 (feature 309).

### H7. Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Green, Northampton", Post-Medieval Archaeology 30(1), 1996 (`northampton-tannery-1996`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://doi.org/10.1179/pma.1996.002)**
- Fallback: [Google: Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Gre](https://www.google.com/search?q=Shaw%2C%20%22The%20excavation%20of%20a%20late%2015th-%20to%2017th-century%20tanning%20complex%20at%20The%20Green%2C%20Northampton%22%2C%20Post-Medieval%20Archaeol)
- **Rests on it:** "How our maps site tanning yards" (`research/questions/0193-tanning-yards.drawing.html`); "Tanning yards" (`research/questions/0193-tanning-yards.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12: the publisher's abstract, which the DOI address serves to a reader in a browser and which the OpenAlex public API republishes in full as an inverted index, reconstructed here and checked for gaps; the article body is closed - Unpaywall and OpenAlex both report no open copy, and the publisher's own page and the Ingenta copy refuse every automated client
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

## Tier 2 - no claim rests on it (8)

No footnote cites these: each is kept as a record of what was searched, or named only in an absence note that already says
it could not be read. What could be wrong is the registry entry's own description of the source.

### H8. Kushiro Mire alder invasion, Ecohydrology & Hydrobiology 2014 (`kushiro-mire-2014`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://www.sciencedirect.com/science/article/abs/pii/S1642359314000706)**
- Fallback: [Google: Kushiro Mire alder invasion, Ecohydrology & Hydrobiology 2014](https://www.google.com/search?q=Kushiro%20Mire%20alder%20invasion%2C%20Ecohydrology%20%26%20Hydrobiology%202014)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** READ 2026-08-26 - abstract | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H9. Studies in Chinese Religions 5(2), "Giving while keeping: inexhaustible treasuries and inalienable wealth in medieval China" (`inexhaustible-treasuries`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://doi.org/10.1080/23729988.2019.1639463)**
- Fallback: [Google: Studies in Chinese Religions 5(2), "Giving while keeping: inexhaustible treasuri](https://www.google.com/search?q=Studies%20in%20Chinese%20Religions%205%282%29%2C%20%22Giving%20while%20keeping%3A%20inexhaustible%20treasuries%20and%20inalienable%20wealth%20in%20medieval%20Ch)
- **Rests on it:** no claim - it is named only in an absence note on "Temple clergy, their families, and how a temple earned its keep" (`research/questions/0232-temple-clergy-their-families-and-how-a-temple-earned-its-keep.html`), which already says it could not be read.
- **How it was read before (the entry's own notes):** unfetched 2026-08-28 | 2026-09-06, feature 195 | the entry stays as the record of what was searched. 2026-09-27 (feature 272 T): the author is Neil Schmid (Crossref); the ResearchGate copy and the publisher's page both return 403 to curl; on the GM's TO-DOWNLOAD list. The treasury and the 713 order are now cited to wujinzang-zhwiki; the MOTIVE of the order rests on this paper alone
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H10. Baidu Baike, 村庙 (village temple) (`cunmiao-baike`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://baike.baidu.com/item/%E6%9D%91%E5%BA%99/3494869)**
- Fallback: [Google: Baidu Baike, 村庙 (village temple)](https://www.google.com/search?q=Baidu%20Baike%2C%20%E6%9D%91%E5%BA%99%20%28village%20temple%29)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** SUMMARY-ONLY (2026-09-27); the page refused the fetch with HTTP 403 | 2026-09-27, feature 268 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H11. Kinoshita, "Household Size, Household Structure, and Developmental Cycle of a Japanese Village: Eighteenth to Nineteenth Centuries", Journal of Family History 20(3), 1995 (`kinoshita-1995`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://journals.sagepub.com/doi/abs/10.1177/036319909502000302)**
- Fallback: [Google: Kinoshita, "Household Size, Household Structure, and Developmental Cycle of a Ja](https://www.google.com/search?q=Kinoshita%2C%20%22Household%20Size%2C%20Household%20Structure%2C%20and%20Developmental%20Cycle%20of%20a%20Japanese%20Village%3A%20Eighteenth%20to%20Nineteenth)
- **Rests on it:** no claim - it is named only in an absence note on "The five sizes of settlement: hamlet, village, town, provincial city and capital" (`research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html`), which already says it could not be read.
- **How it was read before (the entry's own notes):** unsupported by any readable page - HTTP 403 on one attempt, 2026-08-29 | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H12. G. William Skinner, Marketing and Social Structure in Rural China (1964-65) - consulted at secondhand via retrospectives and reviews (`skinner-marketing`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [x] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://doi.org/10.2307/2050412)**
- Fallback: [Google: G. William Skinner, Marketing and Social Structure in Rural China (1964-65) - co](https://www.google.com/search?q=G.%20William%20Skinner%2C%20Marketing%20and%20Social%20Structure%20in%20Rural%20China%20%281964-65%29%20-%20consulted%20at%20secondhand%20via%20retrospectives)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H13. Steven B. Miles, "From Small Fry to Big Fish: Representing the Rise of Jiujiang Township, Nanhai County, 1395-1657", Ming Studies 48 (2003) (`miles-2003`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://doi.org/10.1179/014703703788762953)**
- Fallback: [Google: Steven B. Miles, "From Small Fry to Big Fish: Representing the Rise of Jiujiang ](https://www.google.com/search?q=Steven%20B.%20Miles%2C%20%22From%20Small%20Fry%20to%20Big%20Fish%3A%20Representing%20the%20Rise%20of%20Jiujiang%20Township%2C%20Nanhai%20County%2C%201395-1657%22%2C%20Min)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unsupported by any readable page (paywalled; the search summary gives the subject: the township's rise on the fish-fry trade in Ming Nanhai) | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H14. Qing local-government scholarship on the 六房三班 ("Six Bureaus and Three Bands", title translated) organization; Pingyao county yamen documentation (`liufang-yamen`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://zhuanlan.zhihu.com/p/660442182)**
- Fallback: [Google: Qing local-government scholarship on the 六房三班 ("Six Bureaus and Three Bands", ti](https://www.google.com/search?q=Qing%20local-government%20scholarship%20on%20the%20%E5%85%AD%E6%88%BF%E4%B8%89%E7%8F%AD%20%28%22Six%20Bureaus%20and%20Three%20Bands%22%2C%20title%20translated%29%20organization%3B%20Pingyao%20co)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unfetched 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H15. Diversion-angle hydraulics (a 30° angle cutting sediment entry by up to 64%; no paper read) (`offtake-angle-studies`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://www.sciencedirect.com/science/article/abs/pii/S1001627920300706)**
- Fallback: [Google: Diversion-angle hydraulics (a 30° angle cutting sediment entry by up to 64%; no ](https://www.google.com/search?q=Diversion-angle%20hydraulics%20%28a%2030%C2%B0%20angle%20cutting%20sediment%20entry%20by%20up%20to%2064%25%3B%20no%20paper%20read%29)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unsupported by any readable page 2026-08-28: search syntheses of several ResearchGate / ScienceDirect papers - "maximum water discharge and minimum sediment discharge when its diversion angle was 30° or 45° among 90°, 75°, 60°, 45°, and 30°"; unfetched 2026-08-28 | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

## Unreachable cited sources (7)

The cited URLs the archive found unreachable, retried 2026-10-02 (see each).

### H16. 陈朝云 / 张晓芊, 「A study of Song-dynasty louzeyuan (漏泽园, the pauper burial grounds) and of social relief」 (translated; original: 「宋代漏泽园及社会救助研究」), 史学月刊 (Henan University), the journal's own listing page - 「The name "louzeyuan" is first seen in the third year of the Chongning era of Emperor Huizong of Song (1104).」 (translated; original: 「"漏泽园"名称始见于宋徽宗崇宁三年（1104年）」) (`shixue-yuekan-louzeyuan`)

- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://sxyk.henu.edu.cn/info/1014/7333.htm)**
- Fallback: [Google: 陈朝云 / 张晓芊, 「A study of Song-dynasty louzeyuan (漏泽园, the pauper burial grounds) a](https://www.google.com/search?q=%E9%99%88%E6%9C%9D%E4%BA%91%20/%20%E5%BC%A0%E6%99%93%E8%8A%8A%2C%20%E3%80%8CA%20study%20of%20Song-dynasty%20louzeyuan%20%28%E6%BC%8F%E6%B3%BD%E5%9B%AD%2C%20the%20pauper%20burial%20grounds%29%20and%20of%20social%20relief%E3%80%8D%20%28translated%3B%20origin)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** abstract READ 2026-09-06, the CNKI full text behind a paywall
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H17. 刘炜, 黄茜, 徐腾, "A study of the building of mid-Northern-Song military cities based on the Wujing zongyao" (title translated; original: 「基于《武经总要》的北宋中期军事城池营建研究」), 『建筑史学刊』 (Journal of Architectural History) 2026(2): 122-132 (`jah-song-military-cities`)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://www.jgcm.ac.cn/jah/cn/article/pdf/preview/10.12329/20969368.2026.02011.pdf)**
- Fallback: [Google: 刘炜, 黄茜, 徐腾, "A study of the building of mid-Northern-Song military cities based ](https://www.google.com/search?q=%E5%88%98%E7%82%9C%2C%20%E9%BB%84%E8%8C%9C%2C%20%E5%BE%90%E8%85%BE%2C%20%22A%20study%20of%20the%20building%20of%20mid-Northern-Song%20military%20cities%20based%20on%20the%20Wujing%20zongyao%22%20%28title%20translated)
- **Rests on it:** "How our maps space and draw wall towers" (`research/questions/0148-towers-along-the-city-wall-mamian.drawing.html`); "Towers along the city wall (mamian)" (`research/questions/0148-towers-along-the-city-wall-mamian.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12; the journal serves the article PDF openly, and its passages were taken from the PDF's own text layer rather than from a page image. The paper is set in two columns, so a sentence is reflowed across them and each fragment was checked separately
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H18. History of Irrigation - irrigation tools (URL: none - the page it was read at, irripro.net, is gone) with Baidu Baike Lulu (a weaker reference) (`irripro-jiegao-lulu`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](http://www.irripro.net/en/nd.jsp?id=113)**
- Fallback: [Google: History of Irrigation - irrigation tools (URL: none - the page it was read at, i](https://www.google.com/search?q=History%20of%20Irrigation%20-%20irrigation%20tools%20%28URL%3A%20none%20-%20the%20page%20it%20was%20read%20at%2C%20irripro.net%2C%20is%20gone%29%20with%20Baidu%20Baike%20Lu)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** READ 2026-08 at http://www.irripro.net/en/nd.jsp?id=113, which returns 404 to every client as of 2026-09-12 and has no Internet Archive capture, so the pointer is unrecoverable rather than blocked | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - unreachable - HTTP 404 (feature 309).

### H19. 旅色 (Tabiiro, a travel guide), 高山陣屋 ("Takayama Jin'ya", title translated) (`tabiiro-takayama-jinya`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://tabiiro.jp/leisure/s/200247-takayama-takayamajinya/)**
- Fallback: [Google: 旅色 (Tabiiro, a travel guide), 高山陣屋 ("Takayama Jin'ya", title translated)](https://www.google.com/search?q=%E6%97%85%E8%89%B2%20%28Tabiiro%2C%20a%20travel%20guide%29%2C%20%E9%AB%98%E5%B1%B1%E9%99%A3%E5%B1%8B%20%28%22Takayama%20Jin%27ya%22%2C%20title%20translated%29)
- **Rests on it:** "How our maps draw the Imperial Magistrate's compound" (`research/questions/0114-the-imperial-magistrates-compound-in-a-capital.drawing.html`); "The Imperial Magistrate's compound in a capital" (`research/questions/0114-the-imperial-magistrates-compound-in-a-capital.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 271)
- Blocked by: the archive's retry on 2026-10-02 - unreachable - HTTP 404 (feature 309).

### H20. 陈凌 (Chen Ling), 建筑空间与礼制文化：宋代地方衙署建筑象征性功能诠释 ("Architectural Space and Ritual-System Culture: An Interpretation of the Symbolic Function of Song-Dynasty Local Yamen Architecture", title translated), 西南大学学报（社会科学版） ("Journal of Southwest University (Social Science Edition)", title translated) 42(5): 182-187, September 2016 (`chen-2016-song-yamen`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://xbgjxt.swu.edu.cn/data/article/preview-pdf?doi=10.13718/j.cnki.xdsk.2016.05.023)**
- Fallback: [Google: 陈凌 (Chen Ling), 建筑空间与礼制文化：宋代地方衙署建筑象征性功能诠释 ("Architectural Space and Ritual-Syste](https://www.google.com/search?q=%E9%99%88%E5%87%8C%20%28Chen%20Ling%29%2C%20%E5%BB%BA%E7%AD%91%E7%A9%BA%E9%97%B4%E4%B8%8E%E7%A4%BC%E5%88%B6%E6%96%87%E5%8C%96%EF%BC%9A%E5%AE%8B%E4%BB%A3%E5%9C%B0%E6%96%B9%E8%A1%99%E7%BD%B2%E5%BB%BA%E7%AD%91%E8%B1%A1%E5%BE%81%E6%80%A7%E5%8A%9F%E8%83%BD%E8%AF%A0%E9%87%8A%20%28%22Architectural%20Space%20and%20Ritual-System%20Culture%3A%20An%20Interpretation%20of%20the%20Symb)
- **Rests on it:** "How our maps place and draw the governor's compound (yamen)" (`research/questions/0163-the-provincial-governments-seat-the-governors-compound-and-where-it-stands-yamen.drawing.html`); "The provincial government's seat: the governor's compound and where it stands (yamen)" (`research/questions/0163-the-provincial-governments-seat-the-governors-compound-and-where-it-stands-yamen.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-14 by a source-reader (feature 242)
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H21. 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿） (Preliminary design report for the 2026 high-standard farmland improvement and upgrading construction project, Conghua District, Guangzhou; client the Conghua District Bureau of Agriculture and Rural Affairs, designer 中联合创设计有限公司 ("Zhonglian Hechuang Design Co., Ltd.", translated)), June 2026 (`conghua-2026-design`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[The cited page](http://nyncj.gz.gov.cn/attachment/8/8037/8037125/10854794.pdf)**
- Fallback: [Google: 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿） (Preliminary design report for the 2026 hi](https://www.google.com/search?q=2026%20%E5%B9%B4%E5%BA%A6%E5%B9%BF%E5%B7%9E%E5%B8%82%E4%BB%8E%E5%8C%96%E5%8C%BA%E9%AB%98%E6%A0%87%E5%87%86%E5%86%9C%E7%94%B0%E6%94%B9%E9%80%A0%E6%8F%90%E5%8D%87%E5%BB%BA%E8%AE%BE%E9%A1%B9%E7%9B%AE%E5%88%9D%E6%AD%A5%E8%AE%BE%E8%AE%A1%E6%8A%A5%E5%91%8A%EF%BC%88%E8%AF%84%E5%AE%A1%E7%A8%BF%EF%BC%89%20%28Preliminary%20design%20report%20for%20the%202026%20high-standard%20farmland%20improvement%20and%20upg)
- **Rests on it:** "How wide canals and ditches are: the ladder of channel widths" (`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12, fetched with curl and a browser user agent, HTTP 200, 23,291,315 bytes, text layer intact; served openly by the district bureau
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H22. The Shunde (顺德) dike-pond figures: 40,084 mu of ponds in 1581 (万历九年) and 58,094 mu in 1642 - 广州日报 and the Shunde Archives timeline; the 4.6% / 6.7% shares are those figures over the 8,700 顷 (870,000 mu) of cultivated land 吴建新 gives from 广东通志 ; 「By the end of the Guangxu era, the grain fields within the county made up less than one tenth of the total cultivated area, most of it having become fish ponds.」 (translated; original: 「至光绪末年，县境禾田占总耕地面积不到十分之一，大部分成为鱼塘」); the late-1980s survey - the main dyke-pond area 86,632 ha, 35% fishponds, 25% irrigated rice; the 1581 taxable fishponds of Nanhai, Shunde and Panyu, ~160,000 mu, from 珠江三角洲农业志. Longshan (龙山) had 8,124 of 44,947 mu in ponds in 1581, 18%; "over half" (75%, 乡之塘倍于田) is the Qianlong-Jiaqing figure; (`wanli-fishpond-summary`)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-10-03

- **[The cited page](https://gzdaily.dayoo.com/h5/html5/2023-07/05/content_871_829964.htm)**
- Fallback: [Google: The Shunde (顺德) dike-pond figures: 40,084 mu of ponds in 1581 (万历九年) and 58,094 ](https://www.google.com/search?q=The%20Shunde%20%28%E9%A1%BA%E5%BE%B7%29%20dike-pond%20figures%3A%2040%2C084%20mu%20of%20ponds%20in%201581%20%28%E4%B8%87%E5%8E%86%E4%B9%9D%E5%B9%B4%29%20and%2058%2C094%20mu%20in%201642%20-%20%E5%B9%BF%E5%B7%9E%E6%97%A5%E6%8A%A5%20and%20the%20Shunde%20Archive)
- **Rests on it:** "How our maps lay cash crops over a village's rice land" (`research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html`); "Cash crops on rice land: dike-ponds, lotus fields and tea rows" (`research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at https://www.163.com/dy/article/D4OSJLAR0514D0GJ.html (feature 195) | verified on readable pages 2026-08-28 | derived, not read as such | contradicted and struck: the record had said over half | the 1581 wording traced to an uncited blog copied into zh.wikipedia 基塘农业 | feature 134 T48, after the GM asked whether the pointer was hallucinated
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Client network socket disconnected before secure TLS connection was established (feature 309).
<!-- high-risk: end -->

---

<!-- imported: the GM's TO-DOWNLOAD.md from here to the end, entries given their mark lines -->

**How to use this.** Go down the list and click. Every link is live. Save whatever comes back into this
same folder (`/host-l7r-repo/academic-sources/`) under any filename that names the work; a later session
reads from here and writes the footnote from the passage. Nothing here needs to be done in order, and
nothing here is urgent enough to be worth your time if a link fights you - skip it and move on.

The other file in this folder, `for-the-gm-fetch-list.md`, is a different list: the documents feature 232's
own reading pass could not reach, which you already worked through once. This file is the registry-wide sweep.

**Part 4 at the bottom is where new items get appended** as the unfootnoted-assertions research pass turns
them up. Nothing will ever be inserted into the middle, so once you have worked down to the end of a part,
that part is done.

---

## STATUS - you worked this list on 2026-09-13

**Thirteen of the sixteen in Part 1 are now in this folder**, and you said everything missing was simply
unavailable to you. That settles the other three: they stay uncited, their claims keep their absence
notes, and nobody should spend time on them again. They are marked CLOSED below rather than deleted, so
the next reader can see they were judged rather than forgotten.

| Part 1 item | file you saved |
|---|---|
| 1. MAFF paddy water depth | `suitou-2.pdf` |
| 2. IGNOU silt control | `Unit-10.pdf` |
| 3. Wagner, Ming iron | `Iron production in three Ming texts.html` |
| 4. Wagner, fining and puddling | `Traditional Chinese fining and puddling.html` |
| 5. Korean village-grove GIS census | `A Study on the analysis ... in South Korea.pdf` |
| 6. Abele dissertation | `ABELE-DISSERTATION-2018.pdf` |
| 8. Desire paths (Gavle copy) | `FULLTEXT01.pdf` |
| 10. IRRI drying floor | CLOSED - unavailable; the Wayback capture already read stands |
| 11. Tencent, Xi'an corner | CLOSED - unavailable |
| 12. Daoist clergy - the three open replacements | `17041744.pdf`, `asie_0766-1177_1988_num_4_1_915.pdf`, `asie_0766-1177_2011_num_20_1_1377.pdf` |
| 13. Han pigsty model | `1971.867 - Model of a Pigsty and Latrines.jpg` |
| 14. Shiroyone Senmaida | `hj_june_2025_p10-11.pdf` |
| 15. Wang and Ochiai, Arakawa farmhouses | `13467581.2021.1972810.pdf` |
| 7. Guangdong gazetteer, dike-pond ratio | CLOSED - unavailable |
| 9. Northampton tannery | CLOSED - genuinely closed; a library item, not a bot wall |

**One file in this folder is not from this list and I have not opened it**: `AMM Minutes 2026-06.docx`.
It looks like it landed here by accident. Say the word and I will read it or ignore it; I have done
neither.

---

## What was actually measured, because the number in the closing report was an estimate

Every one of the 495 URLs in the registry (then the built page `SOURCES.html`, now `research/sources/`) was probed from the container twice - once with the
default client, once with a desktop browser user agent. The result:

- **450 open normally.** (147 of those answered `429 Too Many Requests` on the first pass purely because the
  probe hit Wikipedia 24 ways in parallel; every one of them is fine.)
- **45 do not open here.** Of those, **29 are cited by a live footnote** and 16 are registry-only records of a
  search that no footnote rests on.
- **2 of the 45 are dead links** - the page is gone for everybody. Those are a defect in the record for me to
  fix, not something for you to fetch, and they are listed in Part 3 only so you can see them.

So the honest answer to your question is: **29 cited sources, not sixty**. The closing report's "about sixty"
counted every note a checking agent could not re-verify, which double-counts works cited by several notes and
includes the registry-only ones.

**And 13 of the 29 are already in this folder** - you downloaded them on 2026-09-07 and 2026-09-08. They are
listed in Part 2 so you do not fetch them twice.

That leaves **16 worth your time**, in Part 1.

---

## Part 1 - the ones worth fetching

Ordered by what each buys the record. The "rests on it" line is what the record would lose if the source
turned out not to say what we think it says.

### 1. MAFF, 水稲栽培のポイント (paddy water depth, staged through the season)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Direct PDF - maff.go.jp](https://www.maff.go.jp/j/seisan/gijutsuhasshin/techinfo/attach/pdf/suitou-2.pdf)**
- Fallback: [Google: maff 水稲栽培のポイント suitou-2 pdf](https://www.google.com/search?q=maff+%E6%B0%B4%E7%A8%B2%E6%A0%BD%E5%9F%B9%E3%81%AE%E3%83%9D%E3%82%A4%E3%83%B3%E3%83%88+suitou-2+pdf)
- **Rests on it:** six footnotes on `fields.html` - the whole staged water-depth ladder (3-4 cm until rooting,
  2-3 cm after, the mid-season drain to hairline cracks). This is the single most load-bearing item on the
  list: it is what replaced the wrong "four to six inches" the paddy modal carried for a month.
- Blocked by: maff.go.jp returns 403 to every automated client, browser user agent included.

### 2. IGNOU, "Unit 10: Silt Control", Irrigation Engineering (offtake angles)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Direct PDF - eGyanKosh](https://www.egyankosh.ac.in/bitstream/123456789/32984/1/Unit-10.pdf)**
- Fallback: [Google: egyankosh irrigation engineering "silt control" unit 10](https://www.google.com/search?q=egyankosh+irrigation+engineering+%22silt+control%22+unit+10)
- **Rests on it:** four footnotes across `water.html` and `cities/river-cities.html` - the rule that an offtake
  leaves a river at 30 to 45 degrees pointing downstream and that 90 degrees is the worst orientation. This is
  one of the two load-bearing figures the closing report flagged.
- Blocked by: the host's TLS certificate chain is broken, so every client here refuses the connection. A
  browser will show a warning and let you through.

### 3. Donald Wagner, "Iron production in three Ming texts"

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[donwagner.dk/MingFe/MingFe.html](https://donwagner.dk/MingFe/MingFe.html)**
- **Rests on it:** four footnotes on `urban-features.html` - the chao fining hearth as Song Yingxing describes
  it, and the 200 charcoal producers / 200 furnace tenders / 300 miners labor figures.
- Blocked by: the host answers `455` to our client and `200` to a browser. Save the page as HTML or print to PDF.

### 4. Donald Wagner, "Traditional Chinese fining and puddling"

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[donwagner.dk/arch-iron/eu/fining-puddling-china-eu.html](http://donwagner.dk/arch-iron/eu/fining-puddling-china-eu.html)**
- **Rests on it:** fining as stir-frying pig iron under blast (`urban-features.html`). Same host and same block
  as the item above, so it is one extra click while you are there.

### 5. Park Mee Jeong et al., the 462-grove Korean village-grove GIS census

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Direct PDF - koreascience.kr](https://koreascience.kr/article/JAKO201311637857073.pdf)**
- Fallback: [Google: 전통마을 숲의 GIS-DB구축 및 분포 특성 분석에 관한 연구](https://www.google.com/search?q=%EC%A0%84%ED%86%B5%EB%A7%88%EC%9D%84+%EC%88%B2%EC%9D%98+GIS-DB%EA%B5%AC%EC%B6%95+%EB%B0%8F+%EB%B6%84%ED%8F%AC+%ED%8A%B9%EC%84%B1+%EB%B6%84%EC%84%9D%EC%97%90+%EA%B4%80%ED%95%9C+%EC%97%B0%EA%B5%AC)
- **Rests on it:** the Korean analogue for grove size on `vegetation.html` - national mean 10,375 square meters
  over 462 groves, and the village-entrance grove at 7,149 square meters over a 100-grove field survey. These
  are the numbers standing in where no Japanese survey was found.
- Blocked by: the host refuses our client outright and answers a browser normally.

### 6. Michael Abele, *Peasants, skinners, and dead cattle* (PhD dissertation, Illinois, 2018)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[IDEALS repository record](https://www.ideals.illinois.edu/items/107042)** (open access; the PDF is on that page)
- **Rests on it:** the outcast cluster inside the village territory with a clear separation and no fixed
  distance, and `kawaramono` as the older name behind it (`urban-features.html`).
- Blocked by: IDEALS returns 403 to our client, 200 to a browser.

### 7. Guangdong Provincial Gazetteer Office, 【粤故事】中国第一个机器缫丝厂与桑基鱼塘有何渊源

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[dfz.gd.gov.cn](https://dfz.gd.gov.cn/index/dqyj/content/post_4237091.html)**
- Fallback: [Google: 广东省地方志 桑基鱼塘 水基比 三七至四六开](https://www.google.com/search?q=%E5%B9%BF%E4%B8%9C%E7%9C%81%E5%9C%B0%E6%96%B9%E5%BF%97+%E6%A1%91%E5%9F%BA%E9%B1%BC%E5%A1%98+%E6%B0%B4%E5%9F%BA%E6%AF%94+%E4%B8%89%E4%B8%83%E8%87%B3%E5%9B%9B%E5%85%AD%E5%BC%80)
- **Rests on it:** the dike-pond water-to-dike ratio on `archetypes.html`, quoted as 三七至四六开. It was read on
  2026-08-28 and the host has not answered since, so the quotation cannot be re-checked.
- Blocked by: the connection is refused outright now, to both clients.

### 8. Ma, Brandt, Seipel and Ma, "Simple agents - complex emergent path systems"

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[University of Gavle repository PDF](https://hig.diva-portal.org/smash/get/diva2:1773446/FULLTEXT01)**
- Second copy: [Uppsala repository](https://uu.diva-portal.org/smash/get/diva2:1864894/FULLTEXT01)
- **Rests on it:** that a walker minimizes the number and severity of turns - which is the reason a lane runs
  straight between corners and a switchback within a few paces is treated as a drawing artifact
  (`homesteads.html`).
- Blocked by: the repository starts the transfer and drops it here; the publisher (SAGE) 403s. The article is
  CC-BY, so once you have it there is no rights question.

### 9. Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Green, Northampton"

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[DOI 10.1179/pma.1996.002](https://doi.org/10.1179/pma.1996.002)** (Taylor and Francis; subscription)
- Fallback: [Google Scholar](https://scholar.google.com/scholar?q=Shaw+excavation+tanning+complex+The+Green+Northampton+Post-Medieval+Archaeology)
- **Rests on it:** the largest excavated urban tannery (36-37 pits) as the upper comparison for our tanning
  yards, and the abstract's own "all of the tanneries were small" (`urban-features.html`). Only the abstract
  has ever been read.
- Genuinely closed - a library or an interlibrary loan, not a bot wall. Skip it if that is a nuisance; the
  claim is hedged in the record already.

### 10. IRRI Rice Knowledge Bank, sun drying and drying-floor area

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Live page](https://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm)** (host down)
- **[Internet Archive capture that was actually read](http://web.archive.org/web/20230624043456/http://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm)**
- **Rests on it:** the 2-4 cm spread depth and the 500 square meters per 6 tons figure that converts a crop
  volume into a threshing-yard area (`homesteads.html`). Flagged in the record as modern practice.
- The Wayback copy works, so this one is optional - it is here only because the live host has stopped answering
  and an archive capture can disappear.

### 11. Tencent news, "Why is the southwest corner of the Xi'an city wall round?"

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[news.qq.com](https://news.qq.com/rain/a/20260206A06Z5M00)**
- **Rests on it:** the Tang dating of Xi'an's round southwest corner, which the record uses against the Yuan
  dating an encyclopedia gives (`cities/defenses.html`). A popular-history piece, so it is the weakest citation
  in this part; if it will not open, say so and I will look for a better source or write an absence note.

### 12. Patheos, "Taoism: Ethics and Community - Leadership"

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[patheos.com](https://www.patheos.com/library/taoism/ethics-morality-community/leadershipclergy)**
- **Rests on it:** married Zhengyi priests, marriage required at the highest rank, the role passed down in a
  family (`religion-and-death.html`).
- **Read this one only if the alternatives below fail.** It is an unsigned portal summary with no author and no
  references, and it should be replaced rather than re-verified. Better, all open:
  - [Lai Chi-Tim, "Daoism in China Today, 1980-2002", *The China Quarterly* 174](https://library.fes.de/libalt/journals/swetsfulltext/17041744.pdf) - treats the 火居道士 directly
  - [Lagerwey, "Les lignees taoistes du Nord de Taiwan" (Persee, full text)](https://www.persee.fr/doc/asie_0766-1177_1988_num_4_1_915)
  - [Goossaert, "The Heavenly Master, Canonization ..." (Persee, full text)](https://www.persee.fr/doc/asie_0766-1177_2011_num_20_1_1377)

### 13. Art Institute of Chicago, "Model of a Pigsty and Latrines", Eastern Han, object 37716

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[artic.edu/artworks/37716](https://www.artic.edu/artworks/37716)**
- **Rests on it:** the Han pigsty-privy as one customary structure (`homesteads.html`).
- Low priority: the catalog text was read through the museum's public API, which still answers, so the citation
  is re-verifiable by machine. Only the human-facing page 403s.

### 14. Shiroyone Senmaida - the government's Highlighting Japan feature

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[gov-online.go.jp, June 2025](https://www.gov-online.go.jp/hlj/en/june_2025/june_2025-01.html)**
- Also readable and already used: [wajima-senmaida.jp](https://wajima-senmaida.jp/about/)
- **Rests on it:** five footnotes on `fields.html` for the small end of a real worked paddy - 1,004 basins on
  about 4 hectares, average about 18 square meters. The preservation council's own page carries the figures and
  opens fine, so this is a redundancy fetch rather than a gap.

### 15. Wang Jingying and Ochiai Chiho, farmhouses prone to windstorms (Arakawa Village)

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Kyoto University repository copy](https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/3ffc3bcb-2b8a-4727-96b6-7c76dd5e6f0a/content)**
- Publisher: [DOI 10.1080/13467581.2021.1972810](https://doi.org/10.1080/13467581.2021.1972810) (Gold open access, CC-BY, but Taylor and Francis 403s every automated client)
- **Rests on it:** the 72.7% of privies sited southeast-to-south that you ruled be used literally as the seat
  share, plus what the paper does *not* say about wind siting. Three footnotes on `homesteads.html`. The
  repository copy opens, so this is a redundancy fetch.

### 16. 中山市风水林 - the Zhongshan fengshui-wood article

- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)

- **[Journal page](https://rdswxb.hainanu.edu.cn/cn/article/doi/10.15886/j.cnki.rdswxb.2016.03.016)**
- You already saved a PDF of this as `中山市风水林的药用植物资源.pdf`, so this is here only to record that the
  live journal host stopped answering. Nothing to do.

---

## Part 2 - already in this folder, do not fetch again

These thirteen are cited, their host refuses us, and your earlier downloads are what the record was written
from. Listed so the list is complete and so nobody re-fetches them.

| Work | The file you saved |
|---|---|
| Kweon and Youn 2021, Korean village groves | `1-s2.0-S1389934121000836-main.pdf` |
| Takeuchi 2010, the Satoyama Initiative | `Ecological Research - 2010 - Takeuchi ... .pdf` |
| Ushijima et al. 2020, Manchu village layout | `Japan Architectural Review - 2020 - Ushijima ... .pdf` |
| Packer et al. 2017, *Phragmites australis* | `Journal of Ecology - 2017 - Packer ... .pdf` |
| Hu et al. 2011, fengshui forest patches | `S0006320711000450` |
| Chen et al. 2020, village fengshui forests | `forests-11-01286.pdf` |
| Sho River alluvial fan groundwater 2021 | `geosciences-11-00352-v2.pdf` |
| Mukoyama 2023, linear borders | `mukoyama-2022-the-eastern-cousins-... .pdf` |
| Jiao et al. 2019, satoyama management | `sustainability-11-00454.pdf` |
| Jansing et al. 2020, Kunisaki tameike | `sustainability-12-01180-v2.pdf` |
| Ma et al. 2017, fengshui carbon density | `PatternsOfEcoDensity.txt` |
| Yuan and Liu 2009, Buyi fengshui forests | `FenshuiForestManagement.txt` |
| Zhongshan fengshui wood 2016 | `中山市风水林的药用植物资源.pdf` |

---

## Part 3 - not yours to fix

**Registry entries no footnote cites (16).** Each is a record that a search happened, kept deliberately under
the rule that a source which cannot be read is not cited. Nothing in the record rests on any of them, so there
is nothing to lose by leaving them shut: `inexhaustible-treasuries`, `kinoshita-1995`, `kuramai`,
`kushiro-mire-2014`, `liufang-yamen`, `mdpi-3860`, `miles-2003`, `offtake-angle-studies`, `pingyao-yamen`,
`skinner-marketing`, `mbalib-canal-layout`, `shixue-yuekan-louzeyuan`, `gujianchina-taipinggang`,
`kitsuki-castle`, `sizes-koku`, `irripro-jiegao-lulu`.

**Two dead links in the registry**, where the page is gone for everybody rather than blocked. Both are now
fixed in `SOURCES.html`:

- `irripro-jiegao-lulu` - `irripro.net/en/nd.jsp?id=113` returns 404 to every client and has no Internet
  Archive capture, so the pointer is unrecoverable. The entry now records `URL: none` with the reason.
- `kanto-gakuin-tsuijimatsu` - the Kanto Gakuin column on Izumo tsuijimatsu. The live page is 404, but an
  [Internet Archive capture from 2021-10-17](https://web.archive.org/web/20211017194020/http://kyousei.kanto-gakuin.ac.jp/column/kaneko-tomoya/20140911-1906/)
  answers, and the entry now points there. Nothing has been read from it yet, so the claim it would support
  (Izumo tsuijimatsu standing on the north and west sides of a house) still carries its absence note. The
  research pass will read it; no action needed from you.

---

## Part 4 - appended as the unfootnoted-assertions pass finds them

**Feature 238 closed with nothing to add here, and that is a real result rather than an omission.**

Everything 238 worked was the class that needs no new reading: 142 inline `(unsourced)` markers moved
into notes at their own assertions, the sections whose `Sources:` line already recorded a dated search
while the sentence stood bare, and the defects the readings of your downloads turned up. None of that
required a document anybody lacks - the searches had already been done, and what was missing was the
label's position, not a source.

The successor, **feature 242**, is where documents will start appearing: it works the `CITE` items, each
of which needs its own reading, and the ones that cannot be read are what land in this part. Expect it
to fill up.

New items go here, newest at the bottom, so you can always resume from wherever you stopped.

### 17. Heng Chye Kiang, *Cities of Aristocrats and Bureaucrats: the development of medieval Chinese cityscapes* (University of Hawai'i Press, 1999)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawai'i Press title page](https://uhpress.hawaii.edu/title/cities-of-aristocrats-and-bureaucrats-the-development-of-medieval-chinese-cityscapes/)**
- Fallback: [Google: Heng Chye Kiang "Cities of Aristocrats and Bureaucrats" luocheng zicheng Yangzhou](https://www.google.com/search?q=Heng+Chye+Kiang+%22Cities+of+Aristocrats+and+Bureaucrats%22+luocheng+zicheng+Yangzhou)
- **Rests on it:** two footnotes on `cities/capitals.html` - the yacheng/zicheng/luocheng nesting of a prefectural seat (fn-145, now cited to a Fujian heritage portal's account of Quanzhou) and Tang Yangzhou's luocheng as the residential and commercial annex (fn-118, now cited to Baidu Baike's English edition). This is the standard scholarly treatment of both; the notes stand on weak pages until it is read.
- Blocked by: a print monograph; the only copy online is a pirated scan on dokumen.pub, which is not a page to cite. A library copy or the press's preview would do.

### 18. Sen-dou Chang, "The Morphology of Walled Capitals", in G. William Skinner (ed.), *The City in Late Imperial China* (Stanford University Press, 1977)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Stanford University Press title page](https://www.sup.org/books/title/?id=1305)**
- Fallback: [Google: Sen-dou Chang "The Morphology of Walled Capitals" Skinner "The City in Late Imperial China"](https://www.google.com/search?q=Sen-dou+Chang+%22The+Morphology+of+Walled+Capitals%22+Skinner+%22The+City+in+Late+Imperial+China%22)
- **Rests on it:** fn-116 on `cities/capitals.html` - the absence note on the Chinese prefectural seat having no tenshu, no rank-graded samurai rings and no teramachi rim; this chapter is the treatment of the Chinese administrative seat's form that would settle the comparison.
- Blocked by: a print volume, not online.

### 19. "The Lost Rivers of the Forbidden City", *China Heritage Quarterly* 16 (Australian National University)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[chinaheritagequarterly.org, issue 16 feature](http://www.chinaheritagequarterly.org/016/features/016_lostrivers.inc)**
- Fallback: [Google: "Lost Rivers of the Forbidden City" China Heritage Quarterly Jade Spring Tongzi He](https://www.google.com/search?q=%22Lost+Rivers+of+the+Forbidden+City%22+China+Heritage+Quarterly+Jade+Spring+Tongzi+He)
- **Rests on it:** fn-129 on `cities/capitals.html` - Beijing's moats fed from the Jade Spring hills and draining to the Tonghui, now cited to the Chinese Wikipedia article on the city's walls and moats. This is the scholarly account of the same water system.
- Blocked by: the host's TLS version is refused by every client here; a browser will probably show a warning and let you through.

### 20. 扬州中国大运河博物馆 (Yangzhou China Grand Canal Museum), the 梦华东京 exhibition page on Northern Song Kaifeng

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- No direct address is known for this one - use the search.
- Fallback: [Google: 扬州中国大运河博物馆 梦华东京 北宋开封城 坊市 拆除 商业](https://www.google.com/search?q=%E6%89%AC%E5%B7%9E%E4%B8%AD%E5%9B%BD%E5%A4%A7%E8%BF%90%E6%B2%B3%E5%8D%9A%E7%89%A9%E9%A6%86+%E6%A2%A6%E5%8D%8E%E4%B8%9C%E4%BA%AC+%E5%8C%97%E5%AE%8B%E5%BC%80%E5%B0%81%E5%9F%8E+%E5%9D%8A%E5%B8%82+%E6%8B%86%E9%99%A4+%E5%95%86%E4%B8%9A)
- **Rests on it:** fn-131 on `cities/capitals.html` - Kaifeng's settlement spilling past its wall by 1021, cited to a news feature reporting a doctoral thesis; the museum's exhibition text was seen in a search summary to address the dismantling of the ward-and-market system, which is the COMMERCE half the note says is unread.
- Blocked by: the host canalmuseum.net closed the socket on the one attempt; no exact page address was captured, so the search is the way in.

### 21. Architectura Sinica (University of Tennessee and Tsinghua), the glossary entry for mamian 馬面, the horse-face bastion

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[architecturasinica.org keyword k000121](https://architecturasinica.org/keyword/k000121)**
- Fallback: [Google: Architectura Sinica mamian 馬面 keyword glossary city wall bastion](https://www.google.com/search?q=Architectura+Sinica+mamian+%E9%A6%AC%E9%9D%A2+keyword+glossary+city+wall+bastion)
- Fallback: [Google: 守城录 陈规 "马面旧制六十步立一座" 原文](https://www.google.com/search?q=%E5%AE%88%E5%9F%8E%E5%BD%95+%E9%99%88%E8%A7%84+%22%E9%A9%AC%E9%9D%A2%E6%97%A7%E5%88%B6%E5%85%AD%E5%8D%81%E6%AD%A5%E7%AB%8B%E4%B8%80%E5%BA%A7%22+%E5%8E%9F%E6%96%87)
- **Rests on it:** fn-158 on `cities/capitals.html` - the absence note on Chinese walls carrying horse-face bastions on straight curtains, and the formwork argument; the glossary would give the definition, and Chen Gui's Song manual 守城錄 the primary rule of a bastion every sixty paces (second search below).
- Blocked by: HTTP 403 to every automated client. Chen Gui's text is a classical Chinese primary source; a Wikisource or ctext transcription would be readable once found.

### 22. 日本建築学会 論文報告集 371 - the paper on the bakufu's granted residences (拝領屋敷) and their sizes

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF, aijax 371](https://www.jstage.jst.go.jp/article/aijax/371/0/371_KJ00004066677/_pdf)**
- Fallback: [Google: 旗本屋敷 拝領屋敷 規模 日本建築学会 論文報告集 371 pdf](https://www.google.com/search?q=%E6%97%97%E6%9C%AC%E5%B1%8B%E6%95%B7+%E6%8B%9D%E9%A0%98%E5%B1%8B%E6%95%B7+%E8%A6%8F%E6%A8%A1+%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A+%E8%AB%96%E6%96%87%E5%A0%B1%E5%91%8A%E9%9B%86+371+pdf)
- **Rests on it:** two footnotes on `cities/capitals.html` - the bakufu's table of daimyo residence sizes by stipend (fn-173, now cited to an Edo walking group's blog) and the hatamoto residence band (fn-231, now cited to a commercial hobby site). Both notes say so; this paper is the scholarly edition of the same regulation.
- Blocked by: the PDF fetches as unreadable binary here; a browser opens it.

### 23. 東京都水道歴史館『玉川上水 その歴史と役割 改訂新版』 (the Tokyo Waterworks History Museum's book on the Tamagawa aqueduct), and 大橋欣治「水利遺産探訪 - 玉川上水(2)」『農業農村工学会誌』75(10)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ro-da.jp digital archive record B020](https://www.ro-da.jp/suidorekishida/book/detail/B020)**
- Fallback: [Google: "玉川上水 その歴史と役割" 東京都水道歴史館 改訂新版 pdf](https://www.google.com/search?q=%22%E7%8E%89%E5%B7%9D%E4%B8%8A%E6%B0%B4+%E3%81%9D%E3%81%AE%E6%AD%B4%E5%8F%B2%E3%81%A8%E5%BD%B9%E5%89%B2%22+%E6%9D%B1%E4%BA%AC%E9%83%BD%E6%B0%B4%E9%81%93%E6%AD%B4%E5%8F%B2%E9%A4%A8+%E6%94%B9%E8%A8%82%E6%96%B0%E7%89%88+pdf)
- **[J-STAGE PDF, jjsidre2007 75/10](https://www.jstage.jst.go.jp/article/jjsidre2007/75/10/75_10_939/_pdf)**
- Fallback: [Google: 大橋欣治 水利遺産探訪 玉川上水 農業農村工学会誌 75 939 pdf](https://www.google.com/search?q=%E5%A4%A7%E6%A9%8B%E6%AC%A3%E6%B2%BB+%E6%B0%B4%E5%88%A9%E9%81%BA%E7%94%A3%E6%8E%A2%E8%A8%AA+%E7%8E%89%E5%B7%9D%E4%B8%8A%E6%B0%B4+%E8%BE%B2%E6%A5%AD%E8%BE%B2%E6%9D%91%E5%B7%A5%E5%AD%A6%E4%BC%9A%E8%AA%8C+75+939+pdf)
- **Rests on it:** fn-170 on `cities/capitals.html` - the width of the aqueduct's open earth cut, which the page gives as 1-3 ken and marks UNVERIFIED because the only widths in circulation (4-6 ken above, 2-4 below, widened 3 ken in 1670) would put it too low. Either work states the cut's dimensions.
- Blocked by: the museum's book exists only as a catalog record online; the JSIDRE article is a PDF that fetches as page images here, which a browser renders.

### 24. 玉井哲雄『江戸 - 失われた都市空間を読む』 (平凡社, 1986) and 内藤昌『江戸と江戸城』 (鹿島出版会, 1966)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- No direct address is known for this one - use the search.
- Fallback: [Google: 玉井哲雄 "江戸 失われた都市空間を読む" 平凡社 町割 塀 武家地](https://www.google.com/search?q=%E7%8E%89%E4%BA%95%E5%93%B2%E9%9B%84+%22%E6%B1%9F%E6%88%B8+%E5%A4%B1%E3%82%8F%E3%82%8C%E3%81%9F%E9%83%BD%E5%B8%82%E7%A9%BA%E9%96%93%E3%82%92%E8%AA%AD%E3%82%80%22+%E5%B9%B3%E5%87%A1%E7%A4%BE+%E7%94%BA%E5%89%B2+%E5%A1%80+%E6%AD%A6%E5%AE%B6%E5%9C%B0)
- Fallback: [Google: 内藤昌 江戸と江戸城 鹿島出版会 町割 塀](https://www.google.com/search?q=%E5%86%85%E8%97%A4%E6%98%8C+%E6%B1%9F%E6%88%B8%E3%81%A8%E6%B1%9F%E6%88%B8%E5%9F%8E+%E9%B9%BF%E5%B3%B6%E5%87%BA%E7%89%88%E4%BC%9A+%E7%94%BA%E5%89%B2+%E5%A1%80)
- **Rests on it:** fn-168 on `cities/capitals.html` - the absence note on which interior walls a period city drew (the castle, the yashiki, the sogamae, and nothing else); these are the standard monographs on Edo's urban fabric that would price the claim.
- Blocked by: print monographs, not online; a library.

### 25. 『御府内備考』 and 台東区『台東区史』 on the Asakusa Okura (浅草御蔵), the shogunate's rice granary at Kuramae

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- No direct address is known for this one - use the search.
- Fallback: [Google: 浅草御蔵 御府内備考 米蔵 構造 石垣 河岸 台東区史 pdf](https://www.google.com/search?q=%E6%B5%85%E8%8D%89%E5%BE%A1%E8%94%B5+%E5%BE%A1%E5%BA%9C%E5%86%85%E5%82%99%E8%80%83+%E7%B1%B3%E8%94%B5+%E6%A7%8B%E9%80%A0+%E7%9F%B3%E5%9E%A3+%E6%B2%B3%E5%B2%B8+%E5%8F%B0%E6%9D%B1%E5%8C%BA%E5%8F%B2+pdf)
- **Rests on it:** fn-161 on `cities/capitals.html` - the absence note on the granary's raised floor and stone revetment as its flood answer; the shogunal topography and the ward history are where the storehouses' construction would be described.
- Blocked by: print works; the Wikipedia article on Kuramae cites the 御府内備考 for the site's area, so a digitized edition may exist at the National Diet Library.

### 26. 北京市人民政府 (Beijing Municipal Government), 「北京的鼓楼和钟楼」

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[beijing.gov.cn, 四九城 series, 2017-01-04](https://www.beijing.gov.cn/renwen/jrbj/sjc/201701/t20170104_1874489.html)**
- Fallback: [Google: 北京市人民政府 四九城 "北京的鼓楼和钟楼" 定更 亮更 栅栏](https://www.google.com/search?q=%E5%8C%97%E4%BA%AC%E5%B8%82%E4%BA%BA%E6%B0%91%E6%94%BF%E5%BA%9C+%E5%9B%9B%E4%B9%9D%E5%9F%8E+%22%E5%8C%97%E4%BA%AC%E7%9A%84%E9%BC%93%E6%A5%BC%E5%92%8C%E9%92%9F%E6%A5%BC%22+%E5%AE%9A%E6%9B%B4+%E4%BA%AE%E6%9B%B4+%E6%A0%85%E6%A0%8F)
- **Rests on it:** fn-190 on `cities/capitals.html` - the bell-and-drum tower sounding the hour the gates close and open; the note says the CITY gates are attested and the lane palings are not, and this page's search summary said the towers governed both.
- Blocked by: the host closed the socket on the one attempt.

### 27. 柯桥区人民政府 (Keqiao District, Shaoxing), 「纤道桥」, and 浙江省水利厅, 「浙东运河的历史与价值地位（中）」

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kq.gov.cn, 纤道桥](https://www.kq.gov.cn/art/2018/9/11/art_1504946_20997600.html)**
- Fallback: [Google: "纤道桥" 桥墩 "一顺一丁" 石梁 2.36 kq.gov.cn](https://www.google.com/search?q=%22%E7%BA%A4%E9%81%93%E6%A1%A5%22+%E6%A1%A5%E5%A2%A9+%22%E4%B8%80%E9%A1%BA%E4%B8%80%E4%B8%81%22+%E7%9F%B3%E6%A2%81+2.36+kq.gov.cn)
- **[slt.zj.gov.cn, 浙东运河的历史与价值地位（中）](https://slt.zj.gov.cn/art/2021/2/23/art_1228949755_59017525.html)**
- Fallback: [Google: "浙东运河的历史与价值地位" 纤道 石梁 slt.zj.gov.cn](https://www.google.com/search?q=%22%E6%B5%99%E4%B8%9C%E8%BF%90%E6%B2%B3%E7%9A%84%E5%8E%86%E5%8F%B2%E4%B8%8E%E4%BB%B7%E5%80%BC%E5%9C%B0%E4%BD%8D%22+%E7%BA%A4%E9%81%93+%E7%9F%B3%E6%A2%81+slt.zj.gov.cn)
- **Rests on it:** fn-154 on `cities/capitals.html` - the absence note on the Shaoxing towpath deck standing about half a meter above the water; the search summaries of these two pages give three stone beams 0.49 to 0.52 m WIDE and the deck about a meter up, so the half-meter may be the slab's width misread as a height. Reading either settles the figure.
- Blocked by: both hosts timed out at 300 s.

### 28. 農林水産省『土地改良事業計画設計基準・設計「頭首工」技術書』 (MAFF headworks design standard), and "A numerical study of diversion flow to determine the optimum flow system in open channels", *Water Practice & Technology* 19(4)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[maff.go.jp PDF, tousyukou-59](https://www.maff.go.jp/j/nousin/attach/pdf/tousyukou-59.pdf)**
- Fallback: [Google: 土地改良事業計画設計基準 設計 頭首工 技術書 取水口 流向 角度 site:maff.go.jp](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%AD%E8%A8%88+%E9%A0%AD%E9%A6%96%E5%B7%A5+%E6%8A%80%E8%A1%93%E6%9B%B8+%E5%8F%96%E6%B0%B4%E5%8F%A3+%E6%B5%81%E5%90%91+%E8%A7%92%E5%BA%A6+site%3Amaff.go.jp)
- **[iwaponline.com, WPT 19(4):1330](https://iwaponline.com/wpt/article/19/4/1330/100890/A-numerical-study-of-diversion-flow-to-determine)**
- Fallback: [Google: "A numerical study of diversion flow to determine the optimum flow system in open channels" Water Practice Technology](https://www.google.com/search?q=%22A+numerical+study+of+diversion+flow+to+determine+the+optimum+flow+system+in+open+channels%22+Water+Practice+Technology)
- **Rests on it:** fn-218 on `cities/capitals.html` - the absence note on the aqueduct's take-off leaving the river at a shallow downstream angle; the Japanese standard states the intake's orientation rule and the IWA paper the physics (a 30-45 degree branch takes the most water, 90 degrees the least).
- Blocked by: the MAFF file is over 10 MB, beyond what this container fetches; iwaponline.com returns 403 to automated clients.

### 29. ANA Japan Travel Planner, 「青森県弘前市、城下町の寺町禅林街で歴史散歩」, and 真野俊和「近世城下町における寺町と寺院」頸城野郷土資料室学術研究部研究紀要 1 (2016), full text

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ana.co.jp travel planner, Aomori 0000016](https://www.ana.co.jp/ja/jp/japan-travel-planner/aomori/0000016.html)**
- Fallback: [Google: 弘前 禅林街 33ヶ寺 津軽信枚 藩士 菩提寺 城下町](https://www.google.com/search?q=%E5%BC%98%E5%89%8D+%E7%A6%85%E6%9E%97%E8%A1%97+33%E3%83%B6%E5%AF%BA+%E6%B4%A5%E8%BB%BD%E4%BF%A1%E6%9E%9A+%E8%97%A9%E5%A3%AB+%E8%8F%A9%E6%8F%90%E5%AF%BA+%E5%9F%8E%E4%B8%8B%E7%94%BA)
- **[J-STAGE, kfa 1(1)](https://www.jstage.jst.go.jp/article/kfa/1/1/1_1/_article/-char/ja/)**
- Fallback: [Google: 真野俊和 近世城下町における寺町と寺院 頸城野郷土資料室 pdf](https://www.google.com/search?q=%E7%9C%9F%E9%87%8E%E4%BF%8A%E5%92%8C+%E8%BF%91%E4%B8%96%E5%9F%8E%E4%B8%8B%E7%94%BA%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E5%AF%BA%E7%94%BA%E3%81%A8%E5%AF%BA%E9%99%A2+%E9%A0%B8%E5%9F%8E%E9%87%8E%E9%83%B7%E5%9C%9F%E8%B3%87%E6%96%99%E5%AE%A4+pdf)
- **Rests on it:** fn-214 on `cities/capitals.html` - the absence note on retainer families keeping their family temples in the castle town's temple district; four pages read gave only the lord's patronage. Hirosaki's thirty-three-temple Zenrin-gai is the best-documented case, and the Mano paper's Takada study (about 162 temples) may carry the retainer detail deeper than its abstract.
- Blocked by: the ANA page timed out; the paper's PDF fetched only as far as its abstract.

### 30. 小林正彦ほか「江戸期の河川舟運における川舟の運航方法と河岸の立地」 (Tokyo University of Marine Science and Technology, 2003)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kaiyodai.ac.jp PDF](https://www2.kaiyodai.ac.jp/~kuse/pdf/kobayashi_2003.pdf)**
- Fallback: [Google: "江戸期の河川舟運における川舟の運航方法と河岸の立地" 小林 kaiyodai pdf](https://www.google.com/search?q=%22%E6%B1%9F%E6%88%B8%E6%9C%9F%E3%81%AE%E6%B2%B3%E5%B7%9D%E8%88%9F%E9%81%8B%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E5%B7%9D%E8%88%9F%E3%81%AE%E9%81%8B%E8%88%AA%E6%96%B9%E6%B3%95%E3%81%A8%E6%B2%B3%E5%B2%B8%E3%81%AE%E7%AB%8B%E5%9C%B0%22+%E5%B0%8F%E6%9E%97+kaiyodai+pdf)
- **Rests on it:** fn-211 on `cities/capitals.html` - the absence note on the fairway being kept clear by law, which the page attributes to this project's own log-boom research on another page (that pointer should be checked first); this open PDF is the likeliest readable place for a period rule about keeping the channel navigable.
- Blocked by: not fetched in the pass; it may open directly.

### 31. 喜田川守貞『守貞謾稿』巻之二十五 (the bathhouse chapter, with its floor plan), and 川端美季「「湯屋取締規則」及び「湯屋營業取締規則」に関する考察」*Core Ethics* 2 (2006)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- No direct address is known for this one - use the search.
- Fallback: [Google: "守貞謾稿" 湯屋 巻之二十五 図 釜](https://www.google.com/search?q=%22%E5%AE%88%E8%B2%9E%E8%AC%BE%E7%A8%BF%22+%E6%B9%AF%E5%B1%8B+%E5%B7%BB%E4%B9%8B%E4%BA%8C%E5%8D%81%E4%BA%94+%E5%9B%B3+%E9%87%9C)
- **[r-gscefs.jp PDF, Core Ethics 2](https://www.r-gscefs.jp/pdf/ce02/km02.pdf)**
- Fallback: [Google: 川端美季 湯屋取締規則 湯屋營業取締規則 Core Ethics pdf](https://www.google.com/search?q=%E5%B7%9D%E7%AB%AF%E7%BE%8E%E5%AD%A3+%E6%B9%AF%E5%B1%8B%E5%8F%96%E7%B7%A0%E8%A6%8F%E5%89%87+%E6%B9%AF%E5%B1%8B%E7%87%9F%E6%A5%AD%E5%8F%96%E7%B7%A0%E8%A6%8F%E5%89%87+Core+Ethics+pdf)
- **Rests on it:** fn-206 on `cities/capitals.html` - the absence note on the Edo bathhouse being an ordinary shophouse with a fuel yard; the Morisada manko's illustrated bathhouse chapter is the document that settles both halves, and the Meiji regulations paper may describe the premises the rules assumed.
- Blocked by: the Morisada manko is a period manuscript; a transcription or scan (the National Diet Library digital collection likely has one) is what is wanted. The Core Ethics PDF was not fetched.

### 32. Kukuła et al., "Historical and contemporary cemeteries in the urban area. The modern development of the city vs. human remnants in the soil", *Journal of Soils and Sediments* (2024/2025), doi 10.1007/s11368-024-03870-2

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[link.springer.com article page](https://link.springer.com/article/10.1007/s11368-024-03870-2)**
- Fallback: [Google: "Historical and contemporary cemeteries in the urban area" "Journal of Soils and Sediments" cemeteries enlarged](https://www.google.com/search?q=%22Historical+and+contemporary+cemeteries+in+the+urban+area%22+%22Journal+of+Soils+and+Sediments%22+cemeteries+enlarged)
- **Rests on it:** fn-230 on `cities/capitals.html` - the absence note on burial grounds growing in AREA faster than in number of SITES; a search snippet showed the paper stating that new burial space is obtained by enlarging existing cemeteries, generally by no more than a hectare at a time (modern Poland, so the scope would be disclosed).
- Blocked by: Springer redirected the fetch to an institutional login. A ResearchGate copy is listed under publication 382796353.

### 33. "Environment Impact of Cremation Activities in Manikarnika Ghat, Varanasi, Uttar Pradesh", *IJSRD* 6(4) (2018), and Diana L. Eck, *Banaras: City of Light* (the chapter on the burning ghats)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ijsrd.com article record IJSRDV6I40587](https://ijsrd.com/Article.php?manuscript=IJSRDV6I40587)**
- Fallback: [Google: "Environment Impact of Cremation Activities in Manikarnika Ghat" IJSRD pdf](https://www.google.com/search?q=%22Environment+Impact+of+Cremation+Activities+in+Manikarnika+Ghat%22+IJSRD+pdf)
- Fallback: [Google: Eck "Banaras City of Light" Manikarnika "burning ghat" chapter](https://www.google.com/search?q=Eck+%22Banaras+City+of+Light%22+Manikarnika+%22burning+ghat%22+chapter)
- **Rests on it:** fn-226 on `cities/capitals.html` - the absence note on Varanasi's pyres; the page once said about a hundred a day and now says only that the pyres burn every day, because the readable pages disagree threefold (90 to 300). Either work would give a defensible rate and the ghat's arrangement.
- Blocked by: the IJSRD page shows the abstract only, the number being in the PDF; Eck's book is in print.

### 34. Derk Bodde and Clarence Morris, *Law in Imperial China: Exemplified by 190 Ch'ing Dynasty Cases* (Harvard, 1967)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[archive.org record](https://archive.org/details/lawinimperialchi0000bodd)**
- Fallback: [Google: "Law in Imperial China" Bodde Morris "autumn assizes" capital cases per year](https://www.google.com/search?q=%22Law+in+Imperial+China%22+Bodde+Morris+%22autumn+assizes%22+capital+cases+per+year)
- **Rests on it:** fn-146 on `urban-features.html` - the absence note on the annual execution rate that sets each tier's character (one to three per 100,000 a year); the book tabulates the capital cases that passed through the Board of Punishments and the autumn assizes.
- Blocked by: a print book; the archive.org copy is lending-only and no web search could be run in the pass that needed it.

### 35. Timothy Brook, Jerome Bourgon and Gregory Blue, *Death by a Thousand Cuts* (Harvard, 2008)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Harvard University Press page](https://www.hup.harvard.edu/books/9780674027732)**
- Fallback: [Google: "Death by a Thousand Cuts" Brook Bourgon Blue annual executions Qing "per year"](https://www.google.com/search?q=%22Death+by+a+Thousand+Cuts%22+Brook+Bourgon+Blue+annual+executions+Qing+%22per+year%22)
- **Rests on it:** fn-146 on `urban-features.html`, beside Bodde and Morris - it gives per-year Qing execution counts against population.
- Blocked by: in print.

### 36. Ulrich Theobald, "jia 枷, the cangue", ChinaKnowledge.de, and G. T. Staunton (trans.), *Ta Tsing Leu Lee* (London, 1810)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[chinaknowledge.de penal_jia page](http://www.chinaknowledge.de/History/Terms/penal_jia.html)**
- Fallback: [Google: chinaknowledge "jia 枷" cangue Theobald months inscribed](https://www.google.com/search?q=chinaknowledge+%22jia+%E6%9E%B7%22+cangue+Theobald+months+inscribed)
- Fallback: [Google: "Ta Tsing Leu Lee" Staunton 1810 cangue "number of months"](https://www.google.com/search?q=%22Ta+Tsing+Leu+Lee%22+Staunton+1810+cangue+%22number+of+months%22)
- **Rests on it:** fn-145 on `urban-features.html` - the cangue's statutory terms in months and the inscribing of the offender's name and crime on the boards, which the page now states only as "weeks or months" under the magistrate's seal because the English encyclopedia article carries no more. The Staunton translation gives the code's own terms; archive.org holds a scan at https://archive.org/details/tatsingleuleebei00chin.
- Blocked by: chinaknowledge.de failed the TLS handshake to the container; Britannica returned 403; the Staunton scan was not searched.

### 37. Daniel Botsman, *Punishment and Power in the Making of Modern Japan* (Princeton, 2005), chapter 1

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Princeton University Press page](https://press.princeton.edu/books/paperback/9780691130811/punishment-and-power-in-the-making-of-modern-japan)**
- Fallback: [Google: "Punishment and Power in the Making of Modern Japan" Botsman execution grounds pollution kegare](https://www.google.com/search?q=%22Punishment+and+Power+in+the+Making+of+Modern+Japan%22+Botsman+execution+grounds+pollution+kegare)
- **Rests on it:** fn-147 on `urban-features.html` - whether Edo's execution grounds were pushed to the highway entrances for death pollution (kegare) or for deterrence; the readable popular page gives deterrence, and the page now says so, with kegare unsourced.
- Blocked by: in print.

### 38. The Agency for Cultural Affairs' registered-cultural-property database, sake-brewer entries (酒造家住宅), and the Architectural Institute of Japan's papers on the composition of brewery compounds

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kunishitei.bunka.go.jp heritage list](https://kunishitei.bunka.go.jp/heritage/heritagelist)**
- Fallback: [Google: 国指定文化財等データベース 酒造 仕込蔵 登録有形文化財 棟数 桁行 梁間](https://www.google.com/search?q=%E5%9B%BD%E6%8C%87%E5%AE%9A%E6%96%87%E5%8C%96%E8%B2%A1%E7%AD%89%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9+%E9%85%92%E9%80%A0+%E4%BB%95%E8%BE%BC%E8%94%B5+%E7%99%BB%E9%8C%B2%E6%9C%89%E5%BD%A2%E6%96%87%E5%8C%96%E8%B2%A1+%E6%A3%9F%E6%95%B0+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93)
- Fallback: [Google: 日本建築学会計画系論文集 酒蔵 酒造町 敷地規模 坪](https://www.google.com/search?q=%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A%E8%A8%88%E7%94%BB%E7%B3%BB%E8%AB%96%E6%96%87%E9%9B%86+%E9%85%92%E8%94%B5+%E9%85%92%E9%80%A0%E7%94%BA+%E6%95%B7%E5%9C%B0%E8%A6%8F%E6%A8%A1+%E5%9D%AA)
- **Rests on it:** fn-138 on `urban-features.html` - the absence note on a small-town brewery's dimensions (the 60-120 by 30-40 ft vat hall, the 5-6 ft tanks, the ~1,500 tsubo Nagano compound), which stand unsourced.
- Blocked by: the database is a search interface the container cannot drive, and no web search could be run in the pass.

### 39. Hiroshige, *Kanda Konyachō* (神田紺屋町), *One Hundred Famous Views of Edo*, with a museum's description; and a reference for the length of a tan (反) of cloth

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Brooklyn Museum object 121505](https://www.brooklynmuseum.org/opencollection/objects/121505)**
- Fallback: [Google: Brooklyn Museum Hiroshige "Kanda Konyacho" "One Hundred Famous Views of Edo" dyers drying cloth](https://www.google.com/search?q=Brooklyn+Museum+Hiroshige+%22Kanda+Konyacho%22+%22One+Hundred+Famous+Views+of+Edo%22+dyers+drying+cloth)
- Fallback: [Google: 反物 一反 長さ 鯨尺 二丈八尺 寸法](https://www.google.com/search?q=%E5%8F%8D%E7%89%A9+%E4%B8%80%E5%8F%8D+%E9%95%B7%E3%81%95+%E9%AF%A8%E5%B0%BA+%E4%BA%8C%E4%B8%88%E5%85%AB%E5%B0%BA+%E5%AF%B8%E6%B3%95)
- **Rests on it:** fn-140 on `urban-features.html` - the dyer's drying yard (poles and racks dominating the block, bolts of 35-40 ft, rinsing in open water), all unsourced; ja.wikipedia 紺屋 names the print but describes nothing.
- Blocked by: no web search could be run in the pass.

### 40. Joseph Needham, *Science and Civilisation in China*, vol. V:6 (the wedge-and-beam oil press and the edge-runner mill), and a Japanese local-history account of nagagi-jime (長木締め) rapeseed pressing

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[archive.org Science and Civilisation series](https://archive.org/details/ScienceAndCivilisationInChina)**
- Fallback: [Google: Needham "Science and Civilisation in China" oil press "edge-runner" youfang wedge beam](https://www.google.com/search?q=Needham+%22Science+and+Civilisation+in+China%22+oil+press+%22edge-runner%22+youfang+wedge+beam)
- Fallback: [Google: 江戸時代 搾油 長木締め 玉締め 菜種 油絞り 道具 寸法](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3+%E6%90%BE%E6%B2%B9+%E9%95%B7%E6%9C%A8%E7%B7%A0%E3%82%81+%E7%8E%89%E7%B7%A0%E3%82%81+%E8%8F%9C%E7%A8%AE+%E6%B2%B9%E7%B5%9E%E3%82%8A+%E9%81%93%E5%85%B7+%E5%AF%B8%E6%B3%95)
- **Rests on it:** fn-141 on `urban-features.html` - the oil presser's machinery and barn (a 15-30 ft beam, a 20-25 ft mill track, a 40-60 by 25-30 ft barn), unsourced; ja.wikipedia 菜種油 gives one sentence and no machinery.
- Blocked by: print volumes; no web search could be run in the pass.

### 41. 孟元老《東京夢華錄》 and 吳自牧《夢粱錄》 at the Chinese Text Project, for the Song commercial bathhouse (香水行 / 浴堂)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ctext.org 東京夢華錄](https://ctext.org/wiki.pl?if=gb&res=546316)**
- Fallback: [Google: 宋代 香水行 浴堂 公共浴室 夢粱錄 東京夢華錄 沐浴](https://www.google.com/search?q=%E5%AE%8B%E4%BB%A3+%E9%A6%99%E6%B0%B4%E8%A1%8C+%E6%B5%B4%E5%A0%82+%E5%85%AC%E5%85%B1%E6%B5%B4%E5%AE%A4+%E5%A4%A2%E7%B2%B1%E9%8C%84+%E6%9D%B1%E4%BA%AC%E5%A4%A2%E8%8F%AF%E9%8C%84+%E6%B2%90%E6%B5%B4)
- **Rests on it:** fn-142 on `urban-features.html` - that commercial baths are attested in Song China, which the page asserts and no page read supports; the two memoirs are where the attestation would be read.
- Blocked by: the texts stand at ctext and Wikisource but the bathhouse passages were not located in the pass.

### 42. Historic American Buildings Survey measured drawings of blacksmith shops, or the Museum of English Rural Life's smithy records

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Library of Congress HABS collection](https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-records/)**
- Fallback: [Google: HABS measured drawings "blacksmith shop" plan dimensions feet loc.gov](https://www.google.com/search?q=HABS+measured+drawings+%22blacksmith+shop%22+plan+dimensions+feet+loc.gov)
- Fallback: [Google: village blacksmith shop dimensions "18 feet" OR "20 feet" smithy plan historic building survey](https://www.google.com/search?q=village+blacksmith+shop+dimensions+%2218+feet%22+OR+%2220+feet%22+smithy+plan+historic+building+survey)
- **Rests on it:** fn-133 on `urban-features.html` - the smithy's 18-20 ft shed and 8 ft apron, asserted as true feet and unsourced.
- Blocked by: no web search could be run in the pass.

### 43. A folk-museum or agricultural-history page on the *potro de herrar* (the Spanish ox-shoeing frame) giving its timber dimensions

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[es.wikipedia Potro de herrar](https://es.wikipedia.org/wiki/Potro_de_herrar)**
- Fallback: [Google: "potro de herrar" dimensiones medidas madera herrar bueyes](https://www.google.com/search?q=%22potro+de+herrar%22+dimensiones+medidas+madera+herrar+bueyes)
- Fallback: [Google: "ox shoe" "two shoes" cloven hoof shoeing frame dimensions](https://www.google.com/search?q=%22ox+shoe%22+%22two+shoes%22+cloven+hoof+shoeing+frame+dimensions)
- **Rests on it:** fn-132 on `urban-features.html` - the ox-shoeing frame's 7 by 4 ft and the two plates per cloven hoof, which the page now labels as its own.
- Blocked by: no web search could be run in the pass.

### 44. A study of the medieval distribution of Tokoname storage jars (常滑焼 大甕 流通)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ja.wikipedia 常滑焼](https://ja.wikipedia.org/wiki/常滑焼)**
- Fallback: [Google: 常滑焼 中世 大甕 流通 海運 全国 論文 filetype:pdf](https://www.google.com/search?q=%E5%B8%B8%E6%BB%91%E7%84%BC+%E4%B8%AD%E4%B8%96+%E5%A4%A7%E7%94%95+%E6%B5%81%E9%80%9A+%E6%B5%B7%E9%81%8B+%E5%85%A8%E5%9B%BD+%E8%AB%96%E6%96%87+filetype%3Apdf)
- **Rests on it:** fn-185 on `urban-features.html` - the claim that a heavy storage jar is made near where it is used; Tokoname's large jars are usually described as shipped widely by sea, so the study may cut against it.
- Blocked by: no web search could be run in the pass; the Wikipedia article gives kiln counts but no distribution.

### 45. A kiln-site excavation report giving the kiln body's length and the sheds' footprints (Nara National Research Institute for Cultural Properties site-report repository)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[sitereports.nabunken.go.jp](https://sitereports.nabunken.go.jp/)**
- Fallback: [Google: site:sitereports.nabunken.go.jp 瓦窯 全長 焼成室 窯体 工房 掘立柱建物](https://www.google.com/search?q=site%3Asitereports.nabunken.go.jp+%E7%93%A6%E7%AA%AF+%E5%85%A8%E9%95%B7+%E7%84%BC%E6%88%90%E5%AE%A4+%E7%AA%AF%E4%BD%93+%E5%B7%A5%E6%88%BF+%E6%8E%98%E7%AB%8B%E6%9F%B1%E5%BB%BA%E7%89%A9)
- **Rests on it:** fn-127 on `urban-features.html` - the kiln works' dimensions asserted as true feet (a 46 ft kiln, a 32 by 18 ft shed, a 30 by 24 ft clay pit, 28 by 18 ft cottages).
- Blocked by: a repository search the container cannot drive.

### 46. A study of the danna-ba (旦那場) carcass rights: per-year carcass counts for one territory, the season of livestock deaths, and any designated carcass routes in castle towns

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ja.wikipedia 死牛馬取得権](https://ja.wikipedia.org/wiki/死牛馬取得権)**
- Fallback: [Google: 穢多 旦那場 死牛馬 年間 頭数 史料 近世 被差別部落 研究](https://www.google.com/search?q=%E7%A9%A2%E5%A4%9A+%E6%97%A6%E9%82%A3%E5%A0%B4+%E6%AD%BB%E7%89%9B%E9%A6%AC+%E5%B9%B4%E9%96%93+%E9%A0%AD%E6%95%B0+%E5%8F%B2%E6%96%99+%E8%BF%91%E4%B8%96+%E8%A2%AB%E5%B7%AE%E5%88%A5%E9%83%A8%E8%90%BD+%E7%A0%94%E7%A9%B6)
- Fallback: [Google: 近世 村 牛馬 飼料 冬 春 斃死 季節 農業史 研究](https://www.google.com/search?q=%E8%BF%91%E4%B8%96+%E6%9D%91+%E7%89%9B%E9%A6%AC+%E9%A3%BC%E6%96%99+%E5%86%AC+%E6%98%A5+%E6%96%83%E6%AD%BB+%E5%AD%A3%E7%AF%80+%E8%BE%B2%E6%A5%AD%E5%8F%B2+%E7%A0%94%E7%A9%B6)
- Fallback: [Google: 城下町 斃牛馬 運搬 道筋 かわた 死牛馬取得権 研究](https://www.google.com/search?q=%E5%9F%8E%E4%B8%8B%E7%94%BA+%E6%96%83%E7%89%9B%E9%A6%AC+%E9%81%8B%E6%90%AC+%E9%81%93%E7%AD%8B+%E3%81%8B%E3%82%8F%E3%81%9F+%E6%AD%BB%E7%89%9B%E9%A6%AC%E5%8F%96%E5%BE%97%E6%A8%A9+%E7%A0%94%E7%A9%B6)
- **Rests on it:** fn-126, fn-120 and fn-161 on `urban-features.html` - the yard's couple of dozen carcasses a year, the late-winter peak of draft-stock deaths, and the designated carcass ways; the encyclopedia article gives the territory concept and nothing else.
- Blocked by: no web search could be run in the pass.

### 47. Grattan, Zeng, Shannon and Roberts, "Rice is more sensitive to salinity than previously thought", *California Agriculture* 56(6) (2002)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[calag.ucanr.edu archive](https://calag.ucanr.edu/archive/?article=ca.v056n06p189)**
- Fallback: [Google: "Rice is more sensitive to salinity than previously thought" Grattan California Agriculture 2002 floodwater threshold](https://www.google.com/search?q=%22Rice+is+more+sensitive+to+salinity+than+previously+thought%22+Grattan+California+Agriculture+2002+floodwater+threshold)
- **Rests on it:** fn-124 on `urban-features.html` - the page's old 0.9 dS/m rice threshold, which FAO 29 contradicts (3.0 soil, 2.0 water) and which the page now states FAO's way; this paper argues the lower FLOODWATER threshold and may restore part of the old sentence.
- Blocked by: the publisher URL redirected to a page that returned 404.

### 48. 渡辺尚志『百姓たちの水資源戦争』 (草思社, 2009)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[publisher's page (草思社)](https://www.soshisha.com/book_search/detail/1_1613.html)**
- Fallback: [Google: 渡辺尚志 百姓たちの水資源戦争 用水 争論 村 草思社](https://www.google.com/search?q=%E6%B8%A1%E8%BE%BA%E5%B0%9A%E5%BF%97+%E7%99%BE%E5%A7%93%E3%81%9F%E3%81%A1%E3%81%AE%E6%B0%B4%E8%B3%87%E6%BA%90%E6%88%A6%E4%BA%89+%E7%94%A8%E6%B0%B4+%E4%BA%89%E8%AB%96+%E6%9D%91+%E8%8D%89%E6%80%9D%E7%A4%BE)
- **Rests on it:** fn-122 on `urban-features.html` - village water rights held by custom and litigated over; the ja.wikipedia article on water disputes cites this book, and the Chinese half of the sentence is unread.
- Blocked by: in print.

### 49. A Japanese irrigation-engineering paper on the return-flow reuse rate (反復利用率) in paddy districts, and a prefectural rice water-management calendar (入水, 中干し, 落水)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE](https://www.jstage.jst.go.jp/)**
- Fallback: [Google: 水田 用水 反復利用率 用排兼用水路 下流 再利用 農業土木 論文](https://www.google.com/search?q=%E6%B0%B4%E7%94%B0+%E7%94%A8%E6%B0%B4+%E5%8F%8D%E5%BE%A9%E5%88%A9%E7%94%A8%E7%8E%87+%E7%94%A8%E6%8E%92%E5%85%BC%E7%94%A8%E6%B0%B4%E8%B7%AF+%E4%B8%8B%E6%B5%81+%E5%86%8D%E5%88%A9%E7%94%A8+%E8%BE%B2%E6%A5%AD%E5%9C%9F%E6%9C%A8+%E8%AB%96%E6%96%87)
- Fallback: [Google: 水稲 水管理 暦 入水 中干し 間断灌漑 落水 収穫 10日前 指導](https://www.google.com/search?q=%E6%B0%B4%E7%A8%B2+%E6%B0%B4%E7%AE%A1%E7%90%86+%E6%9A%A6+%E5%85%A5%E6%B0%B4+%E4%B8%AD%E5%B9%B2%E3%81%97+%E9%96%93%E6%96%AD%E7%81%8C%E6%BC%91+%E8%90%BD%E6%B0%B4+%E5%8F%8E%E7%A9%AB+10%E6%97%A5%E5%89%8D+%E6%8C%87%E5%B0%8E)
- **Rests on it:** fn-121 and fn-119 on `urban-features.html` - that lower fields recapture paddy drainage, and that a paddy drain runs in the irrigation season with its flush at the pre-harvest drawdown; both unsourced.
- Blocked by: no web search could be run in the pass.

### 50. FAO, *Hides and skins improvement*, curing and storage periods for wet-salted and dried hides (Agricultural Services Bulletin)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[fao.org x6556e](https://www.fao.org/3/x6556e/x6556e00.htm)**
- Fallback: [Google: FAO "hides and skins" curing "wet-salted" storage period bulletin site:fao.org](https://www.google.com/search?q=FAO+%22hides+and+skins%22+curing+%22wet-salted%22+storage+period+bulletin+site%3Afao.org)
- **Rests on it:** fn-168 on `urban-features.html` - how long a salt-cured raw hide keeps, which the page now states only as a month for a wet-salted pack; the seasonal-mismatch argument between winter carcasses and a summer works rests on the longer duration.
- Blocked by: the URL guessed (fao.org/4/x6556e) turned out to be a different document; no web search could be run.

### 51. 中尾健次 (Nakao Kenji), "The Lodgings at the Township of Shincho in Relation to the Control Exercised over Inferior Castes by Danzaemon", *Shigaku Zasshi* 92(7)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE article page](https://www.jstage.jst.go.jp/article/shigaku/92/7/92_KJ00003673301/_article/-char/en)**
- Fallback: [Google: "Lodgings at the Township of Shincho" Danzaemon shigaku](https://www.google.com/search?q=%22Lodgings+at+the+Township+of+Shincho%22+Danzaemon+shigaku)
- **Rests on it:** fn-166 on `urban-features.html` - the Danzaemon compound's population, workshops and where its residents worked; the encyclopedia article gives the buildings and the officials' families only.
- Blocked by: the J-STAGE record was seen in a listing but the full text was not fetched.

### 52. Timothy Amos, *Embodying Difference: The Making of Burakumin in Modern Japan* (Hawaii, 2011)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press page](https://uhpress.hawaii.edu/title/embodying-difference-the-making-of-burakumin-in-modern-japan/)**
- Fallback: [Google: Amos "Embodying Difference" burakumin castle town carcass rights danna-ba](https://www.google.com/search?q=Amos+%22Embodying+Difference%22+burakumin+castle+town+carcass+rights+danna-ba)
- **Rests on it:** fn-161 on `urban-features.html` - designated carcass routes in castle towns; and more generally the caste's in-town duties (fn-163), which the encyclopedia articles give only in outline.
- Blocked by: in print.

### 53. Kawagoe city's cultural-property designation sheet for the 時の鐘 (the base dimensions in ken)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[city.kawagoe.saitama.jp designated-property page](https://www.city.kawagoe.saitama.jp/kurashi/bunkasports/bunkazai/shiteibunkazai/tokinokane.html)**
- Fallback: [Google: 川越市 指定文化財 時の鐘 桁行 梁間 木造 三層 site:city.kawagoe.saitama.jp](https://www.google.com/search?q=%E5%B7%9D%E8%B6%8A%E5%B8%82+%E6%8C%87%E5%AE%9A%E6%96%87%E5%8C%96%E8%B2%A1+%E6%99%82%E3%81%AE%E9%90%98+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93+%E6%9C%A8%E9%80%A0+%E4%B8%89%E5%B1%A4+site%3Acity.kawagoe.saitama.jp)
- **Rests on it:** fn-94 on `urban-features.html` - the bell tower's base, which the page gives as small rather than broad and as this page's reading; the encyclopedia article gives 16 m and three stories only.
- Blocked by: the city URL guessed returned 404; no web search could be run.

### 54. 定边鼓楼 (玉皇阁), Baidu Baike or the Dingbian county page, for the tower's plan dimension

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike 定边鼓楼](https://baike.baidu.com/item/%E5%AE%9A%E8%BE%B9%E9%BC%93%E6%A5%BC)**
- Fallback: [Google: 定边鼓楼 玉皇阁 "边长16米" 万历三十四年](https://www.google.com/search?q=%E5%AE%9A%E8%BE%B9%E9%BC%93%E6%A5%BC+%E7%8E%89%E7%9A%87%E9%98%81+%22%E8%BE%B9%E9%95%BF16%E7%B1%B3%22+%E4%B8%87%E5%8E%86%E4%B8%89%E5%8D%81%E5%9B%9B%E5%B9%B4)
- **Rests on it:** fn-95 on `urban-features.html` - Dingbian's 52 ft, which the page now marks as on no page read; Xingcheng's 21 m is cited.
- Blocked by: Baidu returned 403 to the container.

### 55. 浦井祥子『江戸の時刻と時の鐘』 (岩田書院, 2002)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[岩田書院 book page](https://www.iwata-shoin.co.jp/bookdata/ISBN4-87294-244-9.htm)**
- Fallback: [Google: 浦井祥子 "江戸の時刻と時の鐘" 岩田書院](https://www.google.com/search?q=%E6%B5%A6%E4%BA%95%E7%A5%A5%E5%AD%90+%22%E6%B1%9F%E6%88%B8%E3%81%AE%E6%99%82%E5%88%BB%E3%81%A8%E6%99%82%E3%81%AE%E9%90%98%22+%E5%B2%A9%E7%94%B0%E6%9B%B8%E9%99%A2)
- **Rests on it:** fn-157 on `urban-features.html` - whether most provincial towns relied on a temple bell rather than building a tower; the page now says only that all but one of Edo's own time bells hung at temples. The standard monograph on the time bells and their fee districts.
- Blocked by: in print.

### 56. World Health Organization, *Night Noise Guidelines for Europe* (2009), and a church-bell noise study giving a bell tower's source level

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[WHO publication page](https://www.who.int/publications/i/item/9789289041737)**
- Fallback: [Google: WHO "Night Noise Guidelines for Europe" 2009 pdf rural night ambient dBA](https://www.google.com/search?q=WHO+%22Night+Noise+Guidelines+for+Europe%22+2009+pdf+rural+night+ambient+dBA)
- Fallback: [Google: church bell tower sound pressure level dB measurement study](https://www.google.com/search?q=church+bell+tower+sound+pressure+level+dB+measurement+study)
- **Rests on it:** fn-159 on `urban-features.html` - the acoustic sentence (110-130 dB at the tower, a 25-35 dBA night floor, 40 dB above ambient at the wall), wholly unsourced.
- Blocked by: no web search could be run in the pass.

### 57. National Research Council, *Nutrient Requirements of Beef Cattle* (8th rev. ed., 2016), the water-intake table; and W. Ross Cockrill (ed.), *The Husbandry and Health of the Domestic Buffalo* (FAO, 1974)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NAP catalog 19014](https://nap.nationalacademies.org/catalog/19014/nutrient-requirements-of-beef-cattle-eighth-revised-edition)**
- Fallback: [Google: "Nutrient Requirements of Beef Cattle" NRC water intake table temperature "gallons per day"](https://www.google.com/search?q=%22Nutrient+Requirements+of+Beef+Cattle%22+NRC+water+intake+table+temperature+%22gallons+per+day%22)
- Fallback: [Google: Cockrill "The Husbandry and Health of the Domestic Buffalo" FAO 1974 wallowing sweat glands](https://www.google.com/search?q=Cockrill+%22The+Husbandry+and+Health+of+the+Domestic+Buffalo%22+FAO+1974+wallowing+sweat+glands)
- **Rests on it:** fn-152 on `urban-features.html` - the working ox's daily water (the page now gives it as its own estimate) and the buffalo's intake and sweating; the horse's figures are cited. The FAO buffalo volume's chapters are PDFs under https://www.fao.org/4/ah847e/AH847E00.htm.
- Blocked by: the NRC book is behind a reader; the FAO chapters were not opened.

### 58. Historic England, *Coaching Inns* (Introductions to Heritage Assets)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[historicengland.org.uk IHA coaching inns](https://historicengland.org.uk/images-books/publications/iha-coaching-inns/)**
- Fallback: [Google: Historic England "coaching inns" introductions to heritage assets yard trough pump water](https://www.google.com/search?q=Historic+England+%22coaching+inns%22+introductions+to+heritage+assets+yard+trough+pump+water)
- **Rests on it:** fn-151 on `urban-features.html` - that a coaching-inn yard shows a single trough, which the page now states as its expectation; and fn-187, the smithy kept apart from the stable range.
- Blocked by: no web search could be run in the pass.

### 59. J. L. Buck, *Land Utilization in China* (1937), the farm-survey tables of village water sources; and the early-1980s national rural drinking-water survey

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[archive.org record](https://archive.org/details/landutilizationi0000buck)**
- Fallback: [Google: Buck "Land Utilization in China" 1937 farm survey water supply wells ponds streams](https://www.google.com/search?q=Buck+%22Land+Utilization+in+China%22+1937+farm+survey+water+supply+wells+ponds+streams)
- Fallback: [Google: 1980 年代 全国农村 饮用水 地表水 比例 调查 改水](https://www.google.com/search?q=1980+%E5%B9%B4%E4%BB%A3+%E5%85%A8%E5%9B%BD%E5%86%9C%E6%9D%91+%E9%A5%AE%E7%94%A8%E6%B0%B4+%E5%9C%B0%E8%A1%A8%E6%B0%B4+%E6%AF%94%E4%BE%8B+%E8%B0%83%E6%9F%A5+%E6%94%B9%E6%B0%B4)
- **Rests on it:** fn-150 on `urban-features.html` - the south-China village's one to three communal wells, the vat-and-boil practice, the subscription financing and the early-1980s surface-water figure, all unsourced; the registry's `buck-survey` entry stands unread.
- Blocked by: the archive.org copy is lending-only.

### 60. A Ming or Qing county gazetteer's 城池 chapter (the gate routine, the drum tower and the execution ground's position), or Sen-dou Chang's papers on the walled city

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project](https://ctext.org/)**
- Fallback: [Google: 明清 县城 鼓楼 钟楼 开城门 闭城门 宵禁 方志 城池 志](https://www.google.com/search?q=%E6%98%8E%E6%B8%85+%E5%8E%BF%E5%9F%8E+%E9%BC%93%E6%A5%BC+%E9%92%9F%E6%A5%BC+%E5%BC%80%E5%9F%8E%E9%97%A8+%E9%97%AD%E5%9F%8E%E9%97%A8+%E5%AE%B5%E7%A6%81+%E6%96%B9%E5%BF%97+%E5%9F%8E%E6%B1%A0+%E5%BF%97)
- Fallback: [Google: "法場" "城外" 里 縣志 浙江 明清 刑場 位置](https://www.google.com/search?q=%22%E6%B3%95%E5%A0%B4%22+%22%E5%9F%8E%E5%A4%96%22+%E9%87%8C+%E7%B8%A3%E5%BF%97+%E6%B5%99%E6%B1%9F+%E6%98%8E%E6%B8%85+%E5%88%91%E5%A0%B4+%E4%BD%8D%E7%BD%AE)
- Fallback: [Google: Sen-dou Chang "morphology of walled capitals" Chinese city suburbs gates](https://www.google.com/search?q=Sen-dou+Chang+%22morphology+of+walled+capitals%22+Chinese+city+suburbs+gates)
- **Rests on it:** fn-160 on `urban-features.html` - the county seat's gate-opening and curfew by bell and drum; fn-167, the noxious trades in the extramural suburb; and fn-236 on `cities/capitals.html`, the one-to-ten-li spread of Zhejiang execution grounds, all unread.
- Blocked by: gazetteer collections are subscription databases or scans; no web search could be run.

### 61. NWCG *Incident Response Pocket Guide* (PMS 461), the safety-zone rule, and Drysdale, *An Introduction to Fire Dynamics* (piloted ignition of wood)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NWCG PMS 461](https://www.nwcg.gov/publications/461)**
- Fallback: [Google: NWCG Incident Response Pocket Guide safety zone "four times the flame height"](https://www.google.com/search?q=NWCG+Incident+Response+Pocket+Guide+safety+zone+%22four+times+the+flame+height%22)
- Fallback: [Google: Drysdale "Introduction to Fire Dynamics" piloted ignition wood critical heat flux](https://www.google.com/search?q=Drysdale+%22Introduction+to+Fire+Dynamics%22+piloted+ignition+wood+critical+heat+flux)
- **Rests on it:** fn-172 on `urban-features.html` - the one-flame-height separation for a charcoal stack, which the page now labels its own rule of thumb.
- Blocked by: the NWCG safety-zone page guessed returned 404; the Drysdale text is in print.

### 62. IMO, IMSBC Code, the CHARCOAL schedule (self-heating test and temperature)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[IMO bulk carriers page](https://www.imo.org/en/OurWork/Safety/Pages/BulkCarriers.aspx)**
- Fallback: [Google: IMSBC Code charcoal schedule self-heating "150" volatile matter self-ignition](https://www.google.com/search?q=IMSBC+Code+charcoal+schedule+self-heating+%22150%22+volatile+matter+self-ignition)
- **Rests on it:** fn-114 on `urban-features.html` - the temperature at which high-volatile charcoal self-ignites, dropped from the page for want of a source.
- Blocked by: the code is a purchased publication.

### 63. The shogunate's survey instruction for the Genroku provincial maps, 「国絵図仕立様之覚」, as transcribed by the National Archives of Japan or a prefectural archive

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[National Archives of Japan](https://www.archives.go.jp/)**
- Fallback: [Google: 元禄国絵図 "国絵図仕立様之覚" 国境 立会 書付](https://www.google.com/search?q=%E5%85%83%E7%A6%84%E5%9B%BD%E7%B5%B5%E5%9B%B3+%22%E5%9B%BD%E7%B5%B5%E5%9B%B3%E4%BB%95%E7%AB%8B%E6%A7%98%E4%B9%8B%E8%A6%9A%22+%E5%9B%BD%E5%A2%83+%E7%AB%8B%E4%BC%9A+%E6%9B%B8%E4%BB%98)
- **Rests on it:** fn-170 on `urban-features.html` - the survey's border procedure, now stated from the encyclopedia's summary (district boundaries drawn clearly, variances settled by inquiry); the instruction itself would give the parties' mutual confirmation the page once claimed.
- Blocked by: the archives' exhibition URL guessed returned 404.

### 64. A castle-studies work on the aspect of the 大手門 and 陰陽道 in castle layout

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ja.wikipedia 日本の城](https://ja.wikipedia.org/wiki/日本の城)**
- Fallback: [Google: 大手門 方位 南 陰陽道 縄張 城郭 論文](https://www.google.com/search?q=%E5%A4%A7%E6%89%8B%E9%96%80+%E6%96%B9%E4%BD%8D+%E5%8D%97+%E9%99%B0%E9%99%BD%E9%81%93+%E7%B8%84%E5%BC%B5+%E5%9F%8E%E9%83%AD+%E8%AB%96%E6%96%87)
- Fallback: [Google: "追手" "搦手" 方位 吉凶 築城 近世城郭](https://www.google.com/search?q=%22%E8%BF%BD%E6%89%8B%22+%22%E6%90%A6%E6%89%8B%22+%E6%96%B9%E4%BD%8D+%E5%90%89%E5%87%B6+%E7%AF%89%E5%9F%8E+%E8%BF%91%E4%B8%96%E5%9F%8E%E9%83%AD)
- **Rests on it:** fn-238 on `cities/capitals.html` - the ote-mon usually faced south (cited); that divination was the reason is this page's reading, on no page read.
- Blocked by: no web search could be run in the pass.

### 65. A study of Song urban entertainment: goulan totals for Hangzhou and touring players in provincial cities

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Wikisource 武林舊事](https://zh.wikisource.org/wiki/武林舊事/卷六)**
- Fallback: [Google: "瓦子" "勾欄" 宋代 城市 娛樂 州縣 廟會 流動戲班 論文](https://www.google.com/search?q=%22%E7%93%A6%E5%AD%90%22+%22%E5%8B%BE%E6%AC%84%22+%E5%AE%8B%E4%BB%A3+%E5%9F%8E%E5%B8%82+%E5%A8%9B%E6%A8%82+%E5%B7%9E%E7%B8%A3+%E5%BB%9F%E6%9C%83+%E6%B5%81%E5%8B%95%E6%88%B2%E7%8F%AD+%E8%AB%96%E6%96%87)
- Fallback: [Google: Song dynasty goulan wazi provincial cities temple fairs itinerant troupes](https://www.google.com/search?q=Song+dynasty+goulan+wazi+provincial+cities+temple+fairs+itinerant+troupes)
- **Rests on it:** fn-237 on `cities/capitals.html` - Hangzhou's goulan total (the memoir gives thirteen in one precinct only) and the provincial cities' touring players, on no page read.
- Blocked by: no web search could be run in the pass.

### 66. A castle's or municipality's page on carp kept in castle moats, and on the dredging of moats (Matsumoto, Hikone, the Imperial Palace outer moats)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Matsumoto castle site](https://www.matsumoto-castle.jp/)**
- Fallback: [Google: 城 内堀 鯉 生息 江戸時代 放流 養魚 非常食](https://www.google.com/search?q=%E5%9F%8E+%E5%86%85%E5%A0%80+%E9%AF%89+%E7%94%9F%E6%81%AF+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3+%E6%94%BE%E6%B5%81+%E9%A4%8A%E9%AD%9A+%E9%9D%9E%E5%B8%B8%E9%A3%9F)
- Fallback: [Google: 江戸城 外堀 浚渫 堀浚え 江戸時代 町人 普請](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8%E5%9F%8E+%E5%A4%96%E5%A0%80+%E6%B5%9A%E6%B8%AB+%E5%A0%80%E6%B5%9A%E3%81%88+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3+%E7%94%BA%E4%BA%BA+%E6%99%AE%E8%AB%8B)
- **Rests on it:** fn-239 on `cities/capitals.html` - carp kept in castle moats and moats maintained by sarae dredging; the dictionary attests sarae for rivers, and the carp are on no page read.
- Blocked by: six pages fetched were silent; no web search could be run.

### 67. A study of the reading aloud of village notices (五人組帳前書 recitation) - Ooms or Walthall on village administration

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ja.wikipedia 五人組 (日本史)](https://ja.wikipedia.org/wiki/五人組_(日本史))**
- Fallback: [Google: 五人組帳前書 読み聞かせ 村人 高札 御触書 論文](https://www.google.com/search?q=%E4%BA%94%E4%BA%BA%E7%B5%84%E5%B8%B3%E5%89%8D%E6%9B%B8+%E8%AA%AD%E3%81%BF%E8%81%9E%E3%81%8B%E3%81%9B+%E6%9D%91%E4%BA%BA+%E9%AB%98%E6%9C%AD+%E5%BE%A1%E8%A7%A6%E6%9B%B8+%E8%AB%96%E6%96%87)
- **Rests on it:** fn-107 on `urban-features.html` - that notices were read aloud by officials; no page read states it.
- Blocked by: no web search could be run in the pass.

### 68. 『昭島市史』, the folk volume, on homestead lots of 100-300 tsubo and the wide front yard a farm needs

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Akishima city history page](https://www.city.akishima.lg.jp/shisei/gaiyo/shishi/)**
- Fallback: [Google: "昭島市史" 屋敷 坪 前庭 農家 民俗編](https://www.google.com/search?q=%22%E6%98%AD%E5%B3%B6%E5%B8%82%E5%8F%B2%22+%E5%B1%8B%E6%95%B7+%E5%9D%AA+%E5%89%8D%E5%BA%AD+%E8%BE%B2%E5%AE%B6+%E6%B0%91%E4%BF%97%E7%B7%A8)
- **Rests on it:** the opening paragraph of `homesteads.html` "How big was the work yard" - that the 100-300 tsubo figure belongs to the LOT and not the yard.
- Blocked by: the Akishima digital archive returned an empty page to the container; no search could be run.

### 69. 砺波市立砺波散村地域研究所 研究紀要 (1996), the model Tonami homestead layout

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tonami dispersed-settlement institute bulletins](https://www.city.tonami.toyama.jp/sansonken/kiyou/)**
- Fallback: [Google: 砺波散村地域研究所 研究紀要 1996 カイニョ 屋敷林 配置 東向き](https://www.google.com/search?q=%E7%A0%BA%E6%B3%A2%E6%95%A3%E6%9D%91%E5%9C%B0%E5%9F%9F%E7%A0%94%E7%A9%B6%E6%89%80+%E7%A0%94%E7%A9%B6%E7%B4%80%E8%A6%81+1996+%E3%82%AB%E3%82%A4%E3%83%8B%E3%83%A7+%E5%B1%8B%E6%95%B7%E6%9E%97+%E9%85%8D%E7%BD%AE+%E6%9D%B1%E5%90%91%E3%81%8D)
- **Rests on it:** the "Where the plots stood, from the record" paragraph of `homesteads.html` - the east-facing house, the front work yard, the 2-3 rows of sugi, the north and west bamboo strip - already labeled a guess.
- Blocked by: no search could be run; the 1073shoso.jp archive of the Kashima survey is Shift_JIS and was not re-read.

### 70. A Miyagi prefectural handbook on igune management - planting list, pruning, felling cycle

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Miyagi prefecture](https://www.pref.miyagi.jp/)**
- Fallback: [Google: 居久根 管理 枝打ち 剪定 屋敷林 宮城県 手引き](https://www.google.com/search?q=%E5%B1%85%E4%B9%85%E6%A0%B9+%E7%AE%A1%E7%90%86+%E6%9E%9D%E6%89%93%E3%81%A1+%E5%89%AA%E5%AE%9A+%E5%B1%8B%E6%95%B7%E6%9E%97+%E5%AE%AE%E5%9F%8E%E7%9C%8C+%E6%89%8B%E5%BC%95%E3%81%8D)
- Fallback: [Google: 宮城県 いぐね 屋敷林 手引き 高木 樹高 スギ ケヤキ クロマツ 15m](https://www.google.com/search?q=%E5%AE%AE%E5%9F%8E%E7%9C%8C+%E3%81%84%E3%81%90%E3%81%AD+%E5%B1%8B%E6%95%B7%E6%9E%97+%E6%89%8B%E5%BC%95%E3%81%8D+%E9%AB%98%E6%9C%A8+%E6%A8%B9%E9%AB%98+%E3%82%B9%E3%82%AE+%E3%82%B1%E3%83%A4%E3%82%AD+%E3%82%AF%E3%83%AD%E3%83%9E%E3%83%84+15m)
- **Rests on it:** the limb-pruning sentence and the 15 m / 10 m planting-list classes on `homesteads.html`, and the grove height band (fn on the 15-25 m stand), all standing as this page's reading.
- Blocked by: the handbook's address could not be located without a search.

### 71. F. H. King, *Farmers of Forty Centuries* (1911), the preface and introduction on fertility kept for forty centuries and on the conservation of human and animal waste

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Project Gutenberg full text](https://www.gutenberg.org/files/5350/5350-h/5350-h.htm)**
- Fallback: [Google: "Farmers of Forty Centuries" King 1911 "forty centuries" night soil full text gutenberg](https://www.google.com/search?q=%22Farmers+of+Forty+Centuries%22+King+1911+%22forty+centuries%22+night+soil+full+text+gutenberg)
- **Rests on it:** the manure-economy sentence in the byre-and-wellhead answer on `homesteads.html`, whose four-thousand-years clause is now labeled; a clean read of the Gutenberg page in a shell would quote it.
- Blocked by: the fetch tool returned the page's passages elided with ellipses, so nothing could be quoted verbatim.

### 72. Wang and Ochiai, the Arakawa-village (Shiga) farmhouse spatial-composition survey, *Journal of Asian Architecture and Building Engineering* (2022), doi 10.1080/13467581.2021.1972810

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Taylor and Francis article page](https://www.tandfonline.com/doi/full/10.1080/13467581.2021.1972810)**
- Fallback: [Google: "10.1080/13467581.2021.1972810" Ochiai Arakawa farmhouse toilets 72.7%](https://www.google.com/search?q=%2210.1080%2F13467581.2021.1972810%22+Ochiai+Arakawa+farmhouse+toilets+72.7%25)
- **Rests on it:** footnotes 85 to 87 of `homesteads.html` (the outhouse facing the sun, the 72.7% share behind the engine's 0.727) and the threshing-yard question whose absence note now stands.
- Blocked by: Taylor and Francis returns 403 to the container; the journal is open access to a person.

### 73. An Architectural Institute of Japan measured survey of minka plan sizes (桁行 and 梁行 distributions), or Ota Hirotaro, 『日本の民家』

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE search](https://www.jstage.jst.go.jp/browse/aija/-char/ja)**
- Fallback: [Google: 日本建築学会 論文 民家 梁行 桁行 規模 分布](https://www.google.com/search?q=%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A+%E8%AB%96%E6%96%87+%E6%B0%91%E5%AE%B6+%E6%A2%81%E8%A1%8C+%E6%A1%81%E8%A1%8C+%E8%A6%8F%E6%A8%A1+%E5%88%86%E5%B8%83)
- **Rests on it:** the bay-extension mechanism and the 1.3-2.5 length-to-depth band on `homesteads.html`, unsourced; Yamada's Kikoba paper carries one village's distribution.
- Blocked by: no search could be run.

### 74. The designation text for the Chiba family residence (千葉家住宅, Tono), giving the main house's bays

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cultural Heritage Online](https://bunka.nii.ac.jp/db/heritages/)**
- Fallback: [Google: "千葉家住宅" 主屋 桁行 梁間 重要文化財](https://www.google.com/search?q=%22%E5%8D%83%E8%91%89%E5%AE%B6%E4%BD%8F%E5%AE%85%22+%E4%B8%BB%E5%B1%8B+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1)
- **Rests on it:** the 20-40 ft separation of horse and well on `homesteads.html`, which has no farmhouse plan dimension behind it.
- Blocked by: the record id could not be found without a search.

### 75. 今和次郎『日本の民家』 (1922), the field survey of farmhouse fixtures including the woodpile

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NDL Digital Collections](https://dl.ndl.go.jp/)**
- Fallback: [Google: 今和次郎 "日本の民家" 1922 国立国会図書館デジタルコレクション](https://www.google.com/search?q=%E4%BB%8A%E5%92%8C%E6%AC%A1%E9%83%8E+%22%E6%97%A5%E6%9C%AC%E3%81%AE%E6%B0%91%E5%AE%B6%22+1922+%E5%9B%BD%E7%AB%8B%E5%9B%BD%E4%BC%9A%E5%9B%B3%E6%9B%B8%E9%A4%A8%E3%83%87%E3%82%B8%E3%82%BF%E3%83%AB%E3%82%B3%E3%83%AC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3)
- **Rests on it:** the open woodstack under the eaves as the simpler and older form on `homesteads.html`, now labeled as this page's reading.
- Blocked by: the digital collection's item id could not be found without a search.

### 76. Oregon State University Extension, *Growing Your Own* (EM 9027), the site-selection section on the sun a vegetable bed needs

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[OSU Extension EM 9027](https://extension.oregonstate.edu/pub/em-9027)**
- Fallback: [Google: "Growing Your Own" EM 9027 Oregon State Extension vegetable garden "full sun" site selection](https://www.google.com/search?q=%22Growing+Your+Own%22+EM+9027+Oregon+State+Extension+vegetable+garden+%22full+sun%22+site+selection)
- **Rests on it:** the kitchen-bed morning-light sentence on `homesteads.html`, whose absence note stands.
- Blocked by: no search could be run.

### 77. Ronald G. Knapp, *China's Old Dwellings* (Hawaii), on village lanes as the residual spaces between compounds

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press](https://uhpress.hawaii.edu/title/chinas-old-dwellings/)**
- Fallback: [Google: Ronald Knapp "China's Old Dwellings" University of Hawaii Press village lanes between compounds](https://www.google.com/search?q=Ronald+Knapp+%22China%27s+Old+Dwellings%22+University+of+Hawaii+Press+village+lanes+between+compounds)
- **Rests on it:** the lanes-as-gaps-between-plots sentence on `homesteads.html`; the GM's copy of the Ushijima Manchu-village paper may already carry it.
- Blocked by: in print.

### 78. An Izumo City or Shimane Prefecture heritage page on the 築地松 pines' clipped height and interval

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Izumo city page](https://www.city.izumo.shimane.jp/www/contents/1553658049429/index.html)**
- Fallback: [Google: 築地松 陰手刈り 高さ メートル 年ごと 出雲市](https://www.google.com/search?q=%E7%AF%89%E5%9C%B0%E6%9D%BE+%E9%99%B0%E6%89%8B%E5%88%88%E3%82%8A+%E9%AB%98%E3%81%95+%E3%83%A1%E3%83%BC%E3%83%88%E3%83%AB+%E5%B9%B4%E3%81%94%E3%81%A8+%E5%87%BA%E9%9B%B2%E5%B8%82)
- **Rests on it:** the 8-12 m every 4-5 years figures on `homesteads.html` (fn-102's absence note).
- Blocked by: no search could be run; the encyclopedia and dictionary pages give the technique and no numbers.

### 79. A prefectural extension or JA page giving the days rice hangs on the hasa rack before threshing

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF children's page on drying](https://www.maff.go.jp/j/heya/kodomo_sodan/0206/03.html)**
- Fallback: [Google: 稲架掛け 天日干し 日数 「２週間」 脱穀 農業試験場](https://www.google.com/search?q=%E7%A8%B2%E6%9E%B6%E6%8E%9B%E3%81%91+%E5%A4%A9%E6%97%A5%E5%B9%B2%E3%81%97+%E6%97%A5%E6%95%B0+%E3%80%8C%EF%BC%92%E9%80%B1%E9%96%93%E3%80%8D+%E8%84%B1%E7%A9%80+%E8%BE%B2%E6%A5%AD%E8%A9%A6%E9%A8%93%E5%A0%B4)
- **Rests on it:** the 10-14 days on `homesteads.html` (fn-100), now labeled as this page's reading.
- Blocked by: no search could be run.

### 80. The unnamed nucleated-village morphology work behind the gridiron-of-lanes and semi-private-lane phrases

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search on the phrase](https://www.google.com/search?q=%22gridiron+of+narrow+lanes%22+%22nucleated+village%22)**
- Fallback: [Google: "gridiron of narrow lanes" "nucleated village"](https://www.google.com/search?q=%22gridiron+of+narrow+lanes%22+%22nucleated+village%22)
- Fallback: [Google: "colonised as semi-private space" lane village](https://www.google.com/search?q=%22colonised+as+semi-private+space%22+lane+village)
- **Rests on it:** the lane paragraphs of `homesteads.html`, whose quotations are now paraphrase; the work would restore them as quotations.
- Blocked by: the phrases appear on no page fetched.

### 81. Downing and colleagues, "Global abundance and size distribution of streams and rivers", *Inland Waters* 2(4) (2012), doi 10.5268/IW-2.4.502

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Taylor and Francis article page](https://www.tandfonline.com/doi/full/10.5268/IW-2.4.502)**
- Fallback: [Google: "Global abundance and size distribution of streams and rivers" Downing "Inland Waters" 2012 pdf](https://www.google.com/search?q=%22Global+abundance+and+size+distribution+of+streams+and+rivers%22+Downing+%22Inland+Waters%22+2012+pdf)
- **Rests on it:** the headwater-stream width of about 0.32 m on `water.html` (its anchor line and the village-creek table row).
- Blocked by: Taylor and Francis returns 403 to the container.

### 82. 農林水産省『土地改良事業計画設計基準 設計「水路工」』, the canal design standard that sizes sections by tier

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF design standards index](https://www.maff.go.jp/j/nousin/noukan/tyotei/kizyun/)**
- Fallback: [Google: 土地改良事業計画設計基準 設計 「水路工」 基準書 技術書 pdf maff](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%AD%E8%A8%88+%E3%80%8C%E6%B0%B4%E8%B7%AF%E5%B7%A5%E3%80%8D+%E5%9F%BA%E6%BA%96%E6%9B%B8+%E6%8A%80%E8%A1%93%E6%9B%B8+pdf+maff)
- **Rests on it:** the canal tier widths on `water.html` (fn-132 and fn-140, the 5 m district main) and the design vocabulary (fn-135).
- Blocked by: the PDF's address below the index could not be located without a search.

### 83. 農林水産省『土地改良事業計画設計基準 計画「ほ場整備（水田）」』, the paddy consolidation standard

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF design standards index](https://www.maff.go.jp/j/nousin/sekkei/kijun/)**
- Fallback: [Google: 土地改良事業計画設計基準 計画 "ほ場整備" 水田 技術書 用水路 断面 標準 pdf 農林水産省](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%88%E7%94%BB+%22%E3%81%BB%E5%A0%B4%E6%95%B4%E5%82%99%22+%E6%B0%B4%E7%94%B0+%E6%8A%80%E8%A1%93%E6%9B%B8+%E7%94%A8%E6%B0%B4%E8%B7%AF+%E6%96%AD%E9%9D%A2+%E6%A8%99%E6%BA%96+pdf+%E8%BE%B2%E6%9E%97%E6%B0%B4%E7%94%A3%E7%9C%81)
- **Rests on it:** the 30-60 cm field ditches and plot crossings, the terminal channel's bed against the field surface (fn-136) and the outlet's size (fn-139) on `water.html`.
- Blocked by: the PDF's address could not be located without a search.

### 84. 農林水産省『土地改良事業計画設計基準 計画「排水」』, the drainage standard with a lowland collector's gradient

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF design standards index](https://www.maff.go.jp/j/nousin/sekkei/kijun/)**
- Fallback: [Google: 土地改良事業計画設計基準 計画 排水 技術書 pdf 排水路 勾配 水田](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%88%E7%94%BB+%E6%8E%92%E6%B0%B4+%E6%8A%80%E8%A1%93%E6%9B%B8+pdf+%E6%8E%92%E6%B0%B4%E8%B7%AF+%E5%8B%BE%E9%85%8D+%E6%B0%B4%E7%94%B0)
- **Rests on it:** the collector's fall of about 0.1% on `water.html`, against which the upland-field standard read gives 1/50 to 1/7.
- Blocked by: the PDF's address could not be located without a search.

### 85. 農林水産省 ため池データベース / 全国ため池一覧, the national pond inventory with areas

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF tameike database](https://www.maff.go.jp/j/nousin/bousai/bousai_saigai/b_tameike/tameike_db.html)**
- Fallback: [Google: 農林水産省 ため池データベース 全国ため池一覧 面積 ha](https://www.google.com/search?q=%E8%BE%B2%E6%9E%97%E6%B0%B4%E7%94%A3%E7%9C%81+%E3%81%9F%E3%82%81%E6%B1%A0%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9+%E5%85%A8%E5%9B%BD%E3%81%9F%E3%82%81%E6%B1%A0%E4%B8%80%E8%A6%A7+%E9%9D%A2%E7%A9%8D+ha)
- Fallback: [Google: ため池 斜樋 底樋 設計指針 取水施設 箇所数](https://www.google.com/search?q=%E3%81%9F%E3%82%81%E6%B1%A0+%E6%96%9C%E6%A8%8B+%E5%BA%95%E6%A8%8B+%E8%A8%AD%E8%A8%88%E6%8C%87%E9%87%9D+%E5%8F%96%E6%B0%B4%E6%96%BD%E8%A8%AD+%E7%AE%87%E6%89%80%E6%95%B0)
- **Rests on it:** the tameike size band (3-26 ha, 150-600 m) and the count of a pond's intakes on `water.html`.
- Blocked by: a database interface the container cannot drive.

### 86. The Palace Museum's hydrology account of the Forbidden City moat, or 《北京志·水利志》

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Palace Museum](https://www.dpm.org.cn/)**
- Fallback: [Google: 故宫 筒子河 金水河 水源 玉泉山 "西北" 进水 "东南" 出水 故宫博物院](https://www.google.com/search?q=%E6%95%85%E5%AE%AB+%E7%AD%92%E5%AD%90%E6%B2%B3+%E9%87%91%E6%B0%B4%E6%B2%B3+%E6%B0%B4%E6%BA%90+%E7%8E%89%E6%B3%89%E5%B1%B1+%22%E8%A5%BF%E5%8C%97%22+%E8%BF%9B%E6%B0%B4+%22%E4%B8%9C%E5%8D%97%22+%E5%87%BA%E6%B0%B4+%E6%95%85%E5%AE%AB%E5%8D%9A%E7%89%A9%E9%99%A2)
- Fallback: [Google: 北京 护城河 疏浚 消防用水 灌溉 城市水系 论文 pdf](https://www.google.com/search?q=%E5%8C%97%E4%BA%AC+%E6%8A%A4%E5%9F%8E%E6%B2%B3+%E7%96%8F%E6%B5%9A+%E6%B6%88%E9%98%B2%E7%94%A8%E6%B0%B4+%E7%81%8C%E6%BA%89+%E5%9F%8E%E5%B8%82%E6%B0%B4%E7%B3%BB+%E8%AE%BA%E6%96%87+pdf)
- **Rests on it:** the Forbidden City moat's own inlet and outfall corners on `water.html` (the city system's are cited), and the dredging, fire-water and irrigation uses now labeled as this page's reading.
- Blocked by: no search could be run.

### 87. 静岡市『登呂遺跡 再発掘調査報告書』, on the sheet-board revetment of the canal and bunds

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Shizuoka city Toro pages](https://www.city.shizuoka.lg.jp/s6532/toroiseki.html)**
- Fallback: [Google: 登呂遺跡 矢板 畦畔 水路 発掘調査報告書](https://www.google.com/search?q=%E7%99%BB%E5%91%82%E9%81%BA%E8%B7%A1+%E7%9F%A2%E6%9D%BF+%E7%95%A6%E7%95%94+%E6%B0%B4%E8%B7%AF+%E7%99%BA%E6%8E%98%E8%AA%BF%E6%9F%BB%E5%A0%B1%E5%91%8A%E6%9B%B8)
- **Rests on it:** fn-138 on `water.html`, the yaita boards at Toro.
- Blocked by: no search could be run; the Wikipedia article and the museum site carry the bunds but not the boards.

### 88. USBR, *Design of Small Canal Structures* (1978), and a canal-headworks text on head-regulator alignment and silt excluders

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[USBR technical references](https://www.usbr.gov/tsc/techreferences/mands/mands-pdfs/SmCanalStruct.pdf)**
- Fallback: [Google: "Design of Small Canal Structures" USBR 1978 pdf turnout](https://www.google.com/search?q=%22Design+of+Small+Canal+Structures%22+USBR+1978+pdf+turnout)
- Fallback: [Google: canal head regulator alignment angle silt excluder "head regulator" irrigation engineering pdf](https://www.google.com/search?q=canal+head+regulator+alignment+angle+silt+excluder+%22head+regulator%22+irrigation+engineering+pdf)
- **Rests on it:** the square tap shedding silt into its own mouth on `water.html`, now labeled as this page's reading.
- Blocked by: the USBR address returned 404; a person may find it moved.

### 89. FAO Irrigation and Drainage Paper 62, *Guidelines and computer programs for the planning and design of land drainage systems*, on the interceptor drain

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[FAO document](https://www.fao.org/3/y4263e/y4263e00.htm)**
- Fallback: [Google: "FAO Irrigation and Drainage Paper 62" "land drainage systems" interceptor drain](https://www.google.com/search?q=%22FAO+Irrigation+and+Drainage+Paper+62%22+%22land+drainage+systems%22+interceptor+drain)
- **Rests on it:** the interceptor-ditch purpose on `water.html` (the contour trench read is for infiltration, not protection).
- Blocked by: no search could be run.

### 90. A Japanese agricultural-history reference on the two-shaku farm channel and the three-shaku path (三尺道)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%22%E4%B8%89%E5%B0%BA%E9%81%93%22+%E8%BE%B2%E9%81%93+%E5%B9%85+%22%E4%BA%8C%E5%B0%BA%22+%E7%94%A8%E6%B0%B4%E8%B7%AF+%E5%B9%85)**
- Fallback: [Google: "三尺道" 農道 幅 "二尺" 用水路 幅 江戸時代 農業土木](https://www.google.com/search?q=%22%E4%B8%89%E5%B0%BA%E9%81%93%22+%E8%BE%B2%E9%81%93+%E5%B9%85+%22%E4%BA%8C%E5%B0%BA%22+%E7%94%A8%E6%B0%B4%E8%B7%AF+%E5%B9%85+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3+%E8%BE%B2%E6%A5%AD%E5%9C%9F%E6%9C%A8)
- **Rests on it:** the 2 shaku channel and 3 shaku path on `water.html`.
- Blocked by: kotobank and weblio have no entry; no search could be run.

### 91. A castle-studies treatment of the 泥田堀 and of paddies as defensive ground around a castle town

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%22%E6%B3%A5%E7%94%B0%E5%A0%80%22+%E6%B7%B1%E7%94%B0+%E9%98%B2%E5%BE%A1+%E7%B8%84%E5%BC%B5+%E5%9F%8E%E4%B8%8B%E7%94%BA)**
- Fallback: [Google: "泥田堀" 深田 防御 縄張 城下町](https://www.google.com/search?q=%22%E6%B3%A5%E7%94%B0%E5%A0%80%22+%E6%B7%B1%E7%94%B0+%E9%98%B2%E5%BE%A1+%E7%B8%84%E5%BC%B5+%E5%9F%8E%E4%B8%8B%E7%94%BA)
- **Rests on it:** the flooded paddies as a glacis on `water.html`, now labeled as this page's reading.
- Blocked by: no search could be run.

### 92. 《續資治通鑑長編》 for the year of He Chengju's Hebei marsh proposal

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project](https://ctext.org/)**
- Fallback: [Google: 續資治通鑑長編 何承矩 端拱 塘泺 屯田 遏敵騎](https://www.google.com/search?q=%E7%BA%8C%E8%B3%87%E6%B2%BB%E9%80%9A%E9%91%91%E9%95%B7%E7%B7%A8+%E4%BD%95%E6%89%BF%E7%9F%A9+%E7%AB%AF%E6%8B%B1+%E5%A1%98%E6%B3%BA+%E5%B1%AF%E7%94%B0+%E9%81%8F%E6%95%B5%E9%A8%8E)
- **Rests on it:** the year of the Hebei marsh belt on `water.html`, dropped from the prose because the History of Song passage carries none.
- Blocked by: no search could be run.

### 93. John Lossing Buck, Land Utilization in China (1937) - parcel counts, mean parcel size, farm households per unit area

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive (lending)](https://archive.org/details/landutilizationi0000buck)**
- Fallback: [Google: Buck "Land Utilization in China" 1937 parcels per farm average size of parcel mou households per hectare](https://www.google.com/search?q=Buck+%22Land+Utilization+in+China%22+1937+parcels+per+farm+average+size+of+parcel+mou+households+per+hectare)
- **Rests on it:** the mean Chinese dry parcel near one mu and the 1.5-2 households per hectare of paddy on `fields.html`, both labeled this page's own.
- Blocked by: the scan is lending-restricted; no page a reader can open quotes the tables.

### 94. MAFF land-improvement design standard for paddy consolidation (土地改良事業計画設計基準 設計 ほ場整備)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF design standards index](https://www.maff.go.jp/j/nousin/sekkei/kijun/)**
- Fallback: [Google: 土地改良事業計画設計基準 設計 ほ場整備 水田 畦畔 排水路 天端 畦畔率 基準書 pdf](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%AD%E8%A8%88+%E3%81%BB%E5%A0%B4%E6%95%B4%E5%82%99+%E6%B0%B4%E7%94%B0+%E7%95%A6%E7%95%94+%E6%8E%92%E6%B0%B4%E8%B7%AF+%E5%A4%A9%E7%AB%AF+%E7%95%A6%E7%95%94%E7%8E%87+%E5%9F%BA%E6%BA%96%E6%9B%B8+pdf)
- **Rests on it:** the bund against the collector, the azemichi width, the bund-and-ditch area share and the ordered layout of bunds on `fields.html`.
- Blocked by: the index page carries no figures itself; the standard is a PDF no address reached this pass.

### 95. Chikuma city's designation text for the Obasute terraces (姨捨の棚田, Important Cultural Landscape) - the paddy count

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chikuma city](https://www.city.chikuma.lg.jp/docs/2014030300010/)**
- Fallback: [Google: "姨捨の棚田" 重要文化的景観 千曲市 棚田 枚数 選定](https://www.google.com/search?q=%22%E5%A7%A8%E6%8D%A8%E3%81%AE%E6%A3%9A%E7%94%B0%22+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E7%9A%84%E6%99%AF%E8%A6%B3+%E5%8D%83%E6%9B%B2%E5%B8%82+%E6%A3%9A%E7%94%B0+%E6%9E%9A%E6%95%B0+%E9%81%B8%E5%AE%9A)
- **Rests on it:** the 'over 2,000 small paddies' at Obasute on `fields.html`, now an absence note.
- Blocked by: ja.wikipedia 姨捨 does not exist and 田毎の月 gives only the 48-paddy temple holding.

### 96. Longsheng county's description of the Longji terraces' plot sizes (龙脊梯田 最大的一块田)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Longsheng county government](http://www.longsheng.gov.cn/)**
- Fallback: [Google: "龙脊梯田" 最大的一块田 亩 "带子丘" 龙胜 梯田 面积](https://www.google.com/search?q=%22%E9%BE%99%E8%84%8A%E6%A2%AF%E7%94%B0%22+%E6%9C%80%E5%A4%A7%E7%9A%84%E4%B8%80%E5%9D%97%E7%94%B0+%E4%BA%A9+%22%E5%B8%A6%E5%AD%90%E4%B8%98%22+%E9%BE%99%E8%83%9C+%E6%A2%AF%E7%94%B0+%E9%9D%A2%E7%A7%AF)
- **Rests on it:** Longsheng's largest terrace at 0.62 mu on `fields.html`, now an absence note.
- Blocked by: zh.wikipedia 龙脊梯田 gives only altitude and slope.

### 97. A Japanese agricultural-history reference on サーベル農政 - police enforcement of Meiji row planting

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kotobank 明治農法](https://kotobank.jp/word/明治農法)**
- Fallback: [Google: "サーベル農政" 正条植 巡査 明治 農事改良 強制 農政史](https://www.google.com/search?q=%22%E3%82%B5%E3%83%BC%E3%83%99%E3%83%AB%E8%BE%B2%E6%94%BF%22+%E6%AD%A3%E6%9D%A1%E6%A4%8D+%E5%B7%A1%E6%9F%BB+%E6%98%8E%E6%B2%BB+%E8%BE%B2%E4%BA%8B%E6%94%B9%E8%89%AF+%E5%BC%B7%E5%88%B6+%E8%BE%B2%E6%94%BF%E5%8F%B2)
- **Rests on it:** the police standing over farmers to enforce straight rows on `fields.html`, now an absence note.
- Blocked by: kotobank サーベル農政 and ja.wikipedia 正条植え do not exist; 田植え, 農会 and 塩水選 carry nothing.

### 98. A cadastral study of Edo-period paddy parcel areas (検地帳 一筆 面積)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE, Japanese Journal of Human Geography](https://www.jstage.jst.go.jp/browse/jjhg)**
- Fallback: [Google: 江戸時代 水田 一筆 面積 検地帳 平均 坪 分布 歴史地理学 論文 pdf](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3+%E6%B0%B4%E7%94%B0+%E4%B8%80%E7%AD%86+%E9%9D%A2%E7%A9%8D+%E6%A4%9C%E5%9C%B0%E5%B8%B3+%E5%B9%B3%E5%9D%87+%E5%9D%AA+%E5%88%86%E5%B8%83+%E6%AD%B4%E5%8F%B2%E5%9C%B0%E7%90%86%E5%AD%A6+%E8%AB%96%E6%96%87+pdf)
- **Rests on it:** the pre-modern 0.02-0.25 acre plot band on `fields.html`, now an absence note.
- Blocked by: the consolidation page's 200-300 and 600-800 m2 are post-consolidation design sizes.

### 99. The Tedori Shichika canal district's own history (手取川七ヶ用水) - the straightening date

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Shichika Yosui land-improvement district](https://www.tedorigawa7ka.or.jp/)**
- Fallback: [Google: 手取川七ヶ用水 耕地整理 明治 改修 直線化 歴史](https://www.google.com/search?q=%E6%89%8B%E5%8F%96%E5%B7%9D%E4%B8%83%E3%83%B6%E7%94%A8%E6%B0%B4+%E8%80%95%E5%9C%B0%E6%95%B4%E7%90%86+%E6%98%8E%E6%B2%BB+%E6%94%B9%E4%BF%AE+%E7%9B%B4%E7%B7%9A%E5%8C%96+%E6%AD%B4%E5%8F%B2)
- **Rests on it:** the Tedori fan's ditches 'straightened in the early 1900s' on `fields.html`.
- Blocked by: ja.wikipedia 手取川 gives the canals no straightening date; 七ヶ用水 and 手取川扇状地 do not exist.

### 100. Takeuchi and colleagues, Satoyama: The Traditional Rural Landscape of Japan (Springer, 2003)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Springer](https://link.springer.com/book/9784431000075)**
- Fallback: [Google: Takeuchi "Satoyama: The Traditional Rural Landscape of Japan" Springer 2003 catena paddy crop fields terraces](https://www.google.com/search?q=Takeuchi+%22Satoyama%3A+The+Traditional+Rural+Landscape+of+Japan%22+Springer+2003+catena+paddy+crop+fields+terraces)
- **Rests on it:** the topographic catena and the household's dry plots round its home on `fields.html`.
- Blocked by: a book; the mekongwatch PDF that summarizes it could not be read.

### 101. The Chinese water-resources definition of the 长藤结瓜 (melon-on-the-vine) irrigation system

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike (a locator only, not citable)](https://baike.baidu.com/item/%E9%95%BF%E8%97%A4%E7%BB%93%E7%93%9C%E5%BC%8F%E7%81%8C%E6%BA%89%E7%B3%BB%E7%BB%9F)**
- Fallback: [Google: "长藤结瓜式" 灌溉系统 塘坝 水库 渠道 中国水利百科全书](https://www.google.com/search?q=%22%E9%95%BF%E8%97%A4%E7%BB%93%E7%93%9C%E5%BC%8F%22+%E7%81%8C%E6%BA%89%E7%B3%BB%E7%BB%9F+%E5%A1%98%E5%9D%9D+%E6%B0%B4%E5%BA%93+%E6%B8%A0%E9%81%93+%E4%B8%AD%E5%9B%BD%E6%B0%B4%E5%88%A9%E7%99%BE%E7%A7%91%E5%85%A8%E4%B9%A6)
- **Rests on it:** the melon-on-the-vine phrase for China's pond-and-canal systems on `fields.html`, now an absence note.
- Blocked by: zh.wikipedia 灌溉 and the beitang paper's readable text carry no such passage.

### 102. Supplementary information to the beitang paper (Nature Communications 14, 2023) - the hilly-region share

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Springer Nature supplementary PDF](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-39454-w/MediaObjects/41467_2023_39454_MOESM1_ESM.pdf)**
- Fallback: [Google: "Enhancing rice production sustainability and resilience via reactivating small water bodies" supplementary information Beitang hilly](https://www.google.com/search?q=%22Enhancing+rice+production+sustainability+and+resilience+via+reactivating+small+water+bodies%22+supplementary+information+Beitang+hilly)
- **Rests on it:** the '~71% in hilly regions' beitang share on `fields.html`, now an absence note.
- Blocked by: the PMC full text carries the 39% sentence and no hilly-region figure; nature.com redirects to a login.

### 103. IRRI Rice Knowledge Bank, 'Water management' - the maintained standing depth of a paddy

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[IRRI Rice Knowledge Bank](http://www.knowledgebank.irri.org/step-by-step-production/growth/water-management)**
- Fallback: [Google: IRRI "Rice Knowledge Bank" water management "5-10 cm" standing water paddy transplanted](https://www.google.com/search?q=IRRI+%22Rice+Knowledge+Bank%22+water+management+%225-10+cm%22+standing+water+paddy+transplanted)
- **Rests on it:** the 5-10 cm maintained depth on `fields.html` and the paddy's 5-9 cm optimum on `archetypes.html`.
- Blocked by: the host refused the connection.

### 104. A study of lotus-field expansion round Lake Kasumigaura and the rice acreage-reduction policy

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE (Japanese human geography)](https://www.jstage.jst.go.jp/browse/jjhg)**
- Fallback: [Google: 霞ヶ浦 レンコン 蓮田 水田 転作 減反 拡大 地理 論文](https://www.google.com/search?q=%E9%9C%9E%E3%83%B6%E6%B5%A6+%E3%83%AC%E3%83%B3%E3%82%B3%E3%83%B3+%E8%93%AE%E7%94%B0+%E6%B0%B4%E7%94%B0+%E8%BB%A2%E4%BD%9C+%E6%B8%9B%E5%8F%8D+%E6%8B%A1%E5%A4%A7+%E5%9C%B0%E7%90%86+%E8%AB%96%E6%96%87)
- **Rests on it:** the Kasumigaura 1970s paddy-to-lotus conversion on `archetypes.html`, now an absence note.
- Blocked by: ja.wikipedia 霞ヶ浦 gives 1,700 ha of lotus ponds with no date and no policy.

### 105. A study of paddy-to-lotus conversion in the Mekong delta

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=Mekong+delta+rice+to+lotus+conversion+farmers+policy+land+use+change+lotus+cultivation)**
- Fallback: [Google: Mekong delta rice to lotus conversion farmers policy land use change lotus cultivation](https://www.google.com/search?q=Mekong+delta+rice+to+lotus+conversion+farmers+policy+land+use+change+lotus+cultivation)
- **Rests on it:** the 'contemporary Vietnam' lotus conversion on `archetypes.html`, now an absence note.
- Blocked by: nothing on Vietnam was reachable by address.

### 106. A preservation-district description of a Kiso post town in its valley farmland (奈良井宿 / 妻籠宿)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Shiojiri city](https://www.city.shiojiri.lg.jp/)**
- Fallback: [Google: 重要伝統的建造物群保存地区 奈良井宿 町並み 街道 沿い 水田 選定理由](https://www.google.com/search?q=%E9%87%8D%E8%A6%81%E4%BC%9D%E7%B5%B1%E7%9A%84%E5%BB%BA%E9%80%A0%E7%89%A9%E7%BE%A4%E4%BF%9D%E5%AD%98%E5%9C%B0%E5%8C%BA+%E5%A5%88%E8%89%AF%E4%BA%95%E5%AE%BF+%E7%94%BA%E4%B8%A6%E3%81%BF+%E8%A1%97%E9%81%93+%E6%B2%BF%E3%81%84+%E6%B0%B4%E7%94%B0+%E9%81%B8%E5%AE%9A%E7%90%86%E7%94%B1)
- **Rests on it:** Japanese post towns strung along highways through continuous paddy on `fields.html`.
- Blocked by: ja.wikipedia 宿場 and en.wikipedia Shukuba carry facilities and history and no morphology.

### 107. A study of grave mounds on North China Plain cropland

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[JSTOR (a guess)](https://www.jstor.org/stable/2942530)**
- Fallback: [Google: "North China Plain" graves farmland "grave mounds" village cropland geography study](https://www.google.com/search?q=%22North+China+Plain%22+graves+farmland+%22grave+mounds%22+village+cropland+geography+study)
- **Rests on it:** the in-field grave island as a north-China dry-plain signature on `fields.html`.
- Blocked by: zh.wikipedia 祖坟 and 殡葬改革 do not exist.

### 108. The PRC funeral-reform campaigns that leveled graves on cropland (平坟还耕)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E6%AE%A1%E8%91%AC%E6%94%B9%E9%9D%A9+%E5%B9%B3%E5%9D%9F%E8%BF%98%E8%80%95+%E8%80%95%E5%9C%B0+%E5%9D%9F%E5%A2%93+%E5%8D%A0%E7%94%A8%E8%80%95%E5%9C%B0+%E6%94%BF%E7%AD%96)**
- Fallback: [Google: 殡葬改革 平坟还耕 耕地 坟墓 占用耕地 政策](https://www.google.com/search?q=%E6%AE%A1%E8%91%AC%E6%94%B9%E9%9D%A9+%E5%B9%B3%E5%9D%9F%E8%BF%98%E8%80%95+%E8%80%95%E5%9C%B0+%E5%9D%9F%E5%A2%93+%E5%8D%A0%E7%94%A8%E8%80%95%E5%9C%B0+%E6%94%BF%E7%AD%96)
- **Rests on it:** the same grave-island half on `fields.html`.
- Blocked by: the zh.wikipedia article does not exist under the title tried.

### 109. An agricultural-engineering paper on bund corner failure and azenuri repair

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE (agricultural machinery)](https://www.jstage.jst.go.jp/browse/jsam)**
- Fallback: [Google: J-STAGE 畦畔 崩壊 畦塗り 隅角部 補修 水田 農業機械学会](https://www.google.com/search?q=J-STAGE+%E7%95%A6%E7%95%94+%E5%B4%A9%E5%A3%8A+%E7%95%A6%E5%A1%97%E3%82%8A+%E9%9A%85%E8%A7%92%E9%83%A8+%E8%A3%9C%E4%BF%AE+%E6%B0%B4%E7%94%B0+%E8%BE%B2%E6%A5%AD%E6%A9%9F%E6%A2%B0%E5%AD%A6%E4%BC%9A)
- **Rests on it:** corners as the part of a puddled bund that slumps on `fields.html`, now an absence note.
- Blocked by: ja.wikipedia 畦 attests the yearly re-plastering and nothing on corners.

### 110. A cadastral-map study of pre-consolidation parcel boundaries (地籍図 不整形 区画)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E5%9C%B0%E7%B1%8D%E5%9B%B3+%E8%80%95%E5%9C%B0%E6%95%B4%E7%90%86+%E5%89%8D+%E4%B8%8D%E6%95%B4%E5%BD%A2+%E5%8C%BA%E7%94%BB+%E5%A2%83%E7%95%8C+%E5%B1%88%E6%9B%B2+%E6%B0%B4%E8%B7%AF+%E7%95%A6%E7%95%94+%E8%AB%96%E6%96%87+%E6%AD%B4%E5%8F%B2%E5%9C%B0%E7%90%86)**
- Fallback: [Google: 地籍図 耕地整理 前 不整形 区画 境界 屈曲 水路 畦畔 論文 歴史地理](https://www.google.com/search?q=%E5%9C%B0%E7%B1%8D%E5%9B%B3+%E8%80%95%E5%9C%B0%E6%95%B4%E7%90%86+%E5%89%8D+%E4%B8%8D%E6%95%B4%E5%BD%A2+%E5%8C%BA%E7%94%BB+%E5%A2%83%E7%95%8C+%E5%B1%88%E6%9B%B2+%E6%B0%B4%E8%B7%AF+%E7%95%A6%E7%95%94+%E8%AB%96%E6%96%87+%E6%AD%B4%E5%8F%B2%E5%9C%B0%E7%90%86)
- **Rests on it:** what stands at a stepped parcel corner on `fields.html`, now an absence note.
- Blocked by: no page read describes it.

### 111. A prefectural tameike manual with storage per irrigated hectare and depth

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kagawa prefecture tameike pages](https://www.pref.kagawa.lg.jp/nochi/tameike/)**
- Fallback: [Google: ため池 貯水量 受益面積 1ha あたり 2000 2500立方メートル 水深 県 手引き pdf](https://www.google.com/search?q=%E3%81%9F%E3%82%81%E6%B1%A0+%E8%B2%AF%E6%B0%B4%E9%87%8F+%E5%8F%97%E7%9B%8A%E9%9D%A2%E7%A9%8D+1ha+%E3%81%82%E3%81%9F%E3%82%8A+2000+2500%E7%AB%8B%E6%96%B9%E3%83%A1%E3%83%BC%E3%83%88%E3%83%AB+%E6%B0%B4%E6%B7%B1+%E7%9C%8C+%E6%89%8B%E5%BC%95%E3%81%8D+pdf)
- **Rests on it:** the 2,000-2,500 m3/ha sole-storage and 1,200-1,500 m3/ha stream-fed pond ratios on `fields.html`, now an absence note.
- Blocked by: ja.wikipedia ため池 and the MAFF portal carry no ratio; the Aomori manual could not be read.

### 112. Timothy Brook, Praying for Power: Buddhism and the Formation of Gentry Society in Late-Ming China (1993)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Harvard University Press](https://www.hup.harvard.edu/books/9780674697751)**
- Fallback: [Google: Timothy Brook "Praying for Power" Buddhism "gentry society" late-Ming monasteries monks](https://www.google.com/search?q=Timothy+Brook+%22Praying+for+Power%22+Buddhism+%22gentry+society%22+late-Ming+monasteries+monks)
- **Rests on it:** the 15-30 monks of a serious Ming urban monastery on `religion-and-death.html`, now labeled this project's own scale.
- Blocked by: a book; no readable page gives a Ming urban monastery's monk count.

### 113. Yü Chün-fang, 'Ming Buddhism', in The Cambridge History of China vol. 8

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cambridge Core](https://www.cambridge.org/core/books/cambridge-history-of-china/ming-buddhism/)**
- Fallback: [Google: Yu Chun-fang "Ming Buddhism" Cambridge History of China volume 8 chapter monks monasteries](https://www.google.com/search?q=Yu+Chun-fang+%22Ming+Buddhism%22+Cambridge+History+of+China+volume+8+chapter+monks+monasteries)
- **Rests on it:** the same monk counts.
- Blocked by: a paywalled chapter.

### 114. A Kyoto municipal or academic account of the Tensho 18 (1591) temple relocation with a count

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kyoto city](https://www.city.kyoto.lg.jp/bunshi/page/0000012161.html)**
- Fallback: [Google: 京都 寺町 天正18年 秀吉 寺院 移転 "ヵ寺" 数 京都市 史料](https://www.google.com/search?q=%E4%BA%AC%E9%83%BD+%E5%AF%BA%E7%94%BA+%E5%A4%A9%E6%AD%A318%E5%B9%B4+%E7%A7%80%E5%90%89+%E5%AF%BA%E9%99%A2+%E7%A7%BB%E8%BB%A2+%22%E3%83%B5%E5%AF%BA%22+%E6%95%B0+%E4%BA%AC%E9%83%BD%E5%B8%82+%E5%8F%B2%E6%96%99)
- **Rests on it:** Kyoto's teramachi count on `religion-and-death.html`, replaced by kotobank's Sakai and Akita figures.
- Blocked by: ja.wikipedia 寺町通, 寺町 and 天正の地割 attest the gathering without a number.

### 115. 土井卓治『墓の民俗学』 - village burial organization and the ratio of temples to burial grounds

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nichibunken (a guess)](https://www.nichibun.ac.jp/)**
- Fallback: [Google: 土井卓治 "墓の民俗学" 村落 共同墓地 寺院 檀家 埋め墓 区画](https://www.google.com/search?q=%E5%9C%9F%E4%BA%95%E5%8D%93%E6%B2%BB+%22%E5%A2%93%E3%81%AE%E6%B0%91%E4%BF%97%E5%AD%A6%22+%E6%9D%91%E8%90%BD+%E5%85%B1%E5%90%8C%E5%A2%93%E5%9C%B0+%E5%AF%BA%E9%99%A2+%E6%AA%80%E5%AE%B6+%E5%9F%8B%E3%82%81%E5%A2%93+%E5%8C%BA%E7%94%BB)
- **Rests on it:** eight precincts sharing three burial grounds on `religion-and-death.html`, now labeled this page's own.
- Blocked by: a book; no page read states any ratio.

### 116. The 2017 Umeda graveyard excavation report (大阪文化財研究所 梅田墓)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Osaka Cultural Heritage Institute](https://www.occpa.or.jp/ippan/kenkyu/index.html)**
- Fallback: [Google: 大阪文化財研究所 梅田墓 2017年 発掘調査 報告 埋葬人骨 1500体 蔵骨器](https://www.google.com/search?q=%E5%A4%A7%E9%98%AA%E6%96%87%E5%8C%96%E8%B2%A1%E7%A0%94%E7%A9%B6%E6%89%80+%E6%A2%85%E7%94%B0%E5%A2%93+2017%E5%B9%B4+%E7%99%BA%E6%8E%98%E8%AA%BF%E6%9F%BB+%E5%A0%B1%E5%91%8A+%E5%9F%8B%E8%91%AC%E4%BA%BA%E9%AA%A8+1500%E4%BD%93+%E8%94%B5%E9%AA%A8%E5%99%A8)
- **Rests on it:** how the Osaka graves lay (pits against plots) on `religion-and-death.html`, dropped from the prose.
- Blocked by: ja.wikipedia 大阪七墓 gives the counts and nothing on the layout.

### 117. A Ming-Qing local-gazetteer study of temple categories (壇廟 against 寺觀)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E6%98%8E%E6%B8%85+%E6%96%B9%E5%BF%97+%22%E5%A3%87%E5%BB%9F%22+%22%E5%AF%BA%E8%A7%80%22+%E4%B8%89%E5%AE%98%E5%BB%9F+%E5%88%86%E9%A1%9E)**
- Fallback: [Google: 明清 方志 "壇廟" "寺觀" 三官廟 分類](https://www.google.com/search?q=%E6%98%8E%E6%B8%85+%E6%96%B9%E5%BF%97+%22%E5%A3%87%E5%BB%9F%22+%22%E5%AF%BA%E8%A7%80%22+%E4%B8%89%E5%AE%98%E5%BB%9F+%E5%88%86%E9%A1%9E)
- **Rests on it:** the Three Officials temples filed under Altars and Shrines on `religion-and-death.html`, now an absence note.
- Blocked by: zh.wikipedia 三官大帝 says nothing of how a gazetteer filed them.

### 118. Morten Schlutter, How Zen Became Zen (2008) - resident-monk figures for the Song public monasteries

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press](https://uhpress.hawaii.edu/title/how-zen-became-zen-the-dispute-over-enlightenment-and-the-formation-of-chan-buddhism-in-song-dynasty-china/)**
- Fallback: [Google: "How Zen Became Zen" Schlutter "public monastery" Song monks number](https://www.google.com/search?q=%22How+Zen+Became+Zen%22+Schlutter+%22public+monastery%22+Song+monks+number)
- **Rests on it:** the great Song public monasteries at several hundred monks on `religion-and-death.html`, now an absence note.
- Blocked by: a book; en.wikipedia Religion in the Song dynasty gives only the 1221 census.

### 119. 黃敏枝《宋代佛教社會經濟史論集》(1989) - Song monastery populations

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E9%BB%83%E6%95%8F%E6%9E%9D+%E5%AE%8B%E4%BB%A3%E4%BD%9B%E6%95%99%E7%A4%BE%E6%9C%83%E7%B6%93%E6%BF%9F%E5%8F%B2%E8%AB%96%E9%9B%86+%E5%AD%B8%E7%94%9F%E6%9B%B8%E5%B1%80+%E5%AF%BA%E9%99%A2+%E5%83%A7%E6%95%B8)**
- Fallback: [Google: 黃敏枝 宋代佛教社會經濟史論集 學生書局 寺院 僧數](https://www.google.com/search?q=%E9%BB%83%E6%95%8F%E6%9E%9D+%E5%AE%8B%E4%BB%A3%E4%BD%9B%E6%95%99%E7%A4%BE%E6%9C%83%E7%B6%93%E6%BF%9F%E5%8F%B2%E8%AB%96%E9%9B%86+%E5%AD%B8%E7%94%9F%E6%9B%B8%E5%B1%80+%E5%AF%BA%E9%99%A2+%E5%83%A7%E6%95%B8)
- **Rests on it:** the same Song monastery sizes.
- Blocked by: a print book cited in Lin 2001's bibliography.

### 120. Aso Shrine's own account of the Aso house's generation count

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Aso Shrine](http://asojinja.or.jp/)**
- Fallback: [Google: 阿蘇神社 阿蘇家 大宮司 第九十一代 宮司](https://www.google.com/search?q=%E9%98%BF%E8%98%87%E7%A5%9E%E7%A4%BE+%E9%98%BF%E8%98%87%E5%AE%B6+%E5%A4%A7%E5%AE%AE%E5%8F%B8+%E7%AC%AC%E4%B9%9D%E5%8D%81%E4%B8%80%E4%BB%A3+%E5%AE%AE%E5%8F%B8)
- **Rests on it:** the shrine priesthoods held 'for scores of generations' on `religion-and-death.html`, whose count is an absence note.
- Blocked by: ja.wikipedia 社家 and 阿蘇神社 attest the hereditary office and give no count.

### 121. Encyclopedia of Shinto (Kokugakuin), 'Shake' - the hereditary priestly houses

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kokugakuin digital museum](https://d-museum.kokugakuin.ac.jp/eos/detail/?id=9330)**
- Fallback: [Google: Encyclopedia of Shinto Kokugakuin "shake" hereditary priestly family generations](https://www.google.com/search?q=Encyclopedia+of+Shinto+Kokugakuin+%22shake%22+hereditary+priestly+family+generations)
- **Rests on it:** the same generation count.
- Blocked by: not reached by address.

### 122. 《宋會要輯稿》食貨六十, the 漏澤園 entry - the pauper cemetery's rows and drainage

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project](https://ctext.org/wiki.pl?if=gb&res=553434)**
- Fallback: [Google: 宋會要輯稿 食貨六十 漏澤園 每三行 溝](https://www.google.com/search?q=%E5%AE%8B%E6%9C%83%E8%A6%81%E8%BC%AF%E7%A8%BF+%E9%A3%9F%E8%B2%A8%E5%85%AD%E5%8D%81+%E6%BC%8F%E6%BE%A4%E5%9C%92+%E6%AF%8F%E4%B8%89%E8%A1%8C+%E6%BA%9D)
- **Rests on it:** the ordered rows and the drainage ditch every three rows on `religion-and-death.html`, now absence notes.
- Blocked by: zh.wikipedia 漏澤園 and 宋史 卷178 give plot size, depth, numbering and fence and nothing on rows or a ditch.

### 123. 三門峽市文物工作隊《北宋陝州漏澤園》(文物出版社, 1999) - the excavated pauper cemetery's grave rows

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Wenwu Press](http://www.wenwu.com/)**
- Fallback: [Google: 北宋陝州漏澤園 三門峽市文物工作隊 文物出版社 1999 墓葬 排列](https://www.google.com/search?q=%E5%8C%97%E5%AE%8B%E9%99%9D%E5%B7%9E%E6%BC%8F%E6%BE%A4%E5%9C%92+%E4%B8%89%E9%96%80%E5%B3%BD%E5%B8%82%E6%96%87%E7%89%A9%E5%B7%A5%E4%BD%9C%E9%9A%8A+%E6%96%87%E7%89%A9%E5%87%BA%E7%89%88%E7%A4%BE+1999+%E5%A2%93%E8%91%AC+%E6%8E%92%E5%88%97)
- **Rests on it:** the same rows and ditch.
- Blocked by: a print excavation report.

### 124. The Tama-area history of cremation grounds (多摩・島しょ地域における火葬場の需給及び運営に関する調査研究), the full PDF

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokyo municipal research institute PDF](https://www.tama-100.or.jp/cmsfiles/contents/0000000/470/all.pdf)**
- Fallback: [Google: 多摩 火葬場 の 歴史 "tama-100.or.jp" 火葬場 沿革 PDF](https://www.google.com/search?q=%E5%A4%9A%E6%91%A9+%E7%81%AB%E8%91%AC%E5%A0%B4+%E3%81%AE+%E6%AD%B4%E5%8F%B2+%22tama-100.or.jp%22+%E7%81%AB%E8%91%AC%E5%A0%B4+%E6%B2%BF%E9%9D%A9+PDF)
- **Rests on it:** the crematory's siting by water and off the temple approach on `religion-and-death.html`, now absence notes; the 1884 set-back and the 1667 removal already rest on it.
- Blocked by: a 6.6 MB PDF that returns undecoded streams to an automated fetch; a browser reads it.

### 125. A Tokyo metropolitan cemetery application booklet (都立霊園申込みのしおり) - plot areas and terms of use

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokyo Metropolitan Park Association](https://www.tokyo-park.or.jp/reien/)**
- Fallback: [Google: 都立霊園 申込みのしおり 区画面積 平方メートル 合葬埋蔵施設 使用期限](https://www.google.com/search?q=%E9%83%BD%E7%AB%8B%E9%9C%8A%E5%9C%92+%E7%94%B3%E8%BE%BC%E3%81%BF%E3%81%AE%E3%81%97%E3%81%8A%E3%82%8A+%E5%8C%BA%E7%94%BB%E9%9D%A2%E7%A9%8D+%E5%B9%B3%E6%96%B9%E3%83%A1%E3%83%BC%E3%83%88%E3%83%AB+%E5%90%88%E8%91%AC%E5%9F%8B%E8%94%B5%E6%96%BD%E8%A8%AD+%E4%BD%BF%E7%94%A8%E6%9C%9F%E9%99%90)
- **Rests on it:** the 10-20 sq ft urn plot and the one-generation reuse on `religion-and-death.html`, now an absence note.
- Blocked by: the portal carries no figures; the booklet is where they live.

### 126. Daimyo-tomb (大名墓) survey literature - the mausoleum precinct's form and siting

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E5%A4%A7%E5%90%8D%E5%A2%93+%E7%A0%94%E7%A9%B6+%E7%9F%B3%E9%80%A0+%E5%AE%9D%E7%AF%8B%E5%8D%B0%E5%A1%94+%E7%8E%89%E5%9E%A3+%E5%A2%93%E6%89%80+%E7%AB%8B%E5%9C%B0+%E5%9F%8E%E4%B8%8B%E7%94%BA+PDF)**
- Fallback: [Google: 大名墓 研究 石造 宝篋印塔 玉垣 墓所 立地 城下町 PDF](https://www.google.com/search?q=%E5%A4%A7%E5%90%8D%E5%A2%93+%E7%A0%94%E7%A9%B6+%E7%9F%B3%E9%80%A0+%E5%AE%9D%E7%AF%8B%E5%8D%B0%E5%A1%94+%E7%8E%89%E5%9E%A3+%E5%A2%93%E6%89%80+%E7%AB%8B%E5%9C%B0+%E5%9F%8E%E4%B8%8B%E7%94%BA+PDF)
- **Rests on it:** the clan mausoleum's precinct on `religion-and-death.html`, now written from Zuihoden's page alone.
- Blocked by: ja.wikipedia 大名墓 does not exist and 霊廟 is a stub.

### 127. A folklore study of shrine-precinct upkeep by the parish (宮掃除, 氏子)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%22%E9%8E%AE%E5%AE%88%E3%81%AE%E6%A3%AE%22+OR+%22%E5%A2%83%E5%86%85%22+%E6%8E%83%E9%99%A4+%E6%B0%8F%E5%AD%90+%E7%B6%AD%E6%8C%81%E7%AE%A1%E7%90%86+%E6%B0%91%E4%BF%97+%E8%AB%96%E6%96%87)**
- Fallback: [Google: "鎮守の森" OR "境内" 掃除 氏子 維持管理 民俗 論文](https://www.google.com/search?q=%22%E9%8E%AE%E5%AE%88%E3%81%AE%E6%A3%AE%22+OR+%22%E5%A2%83%E5%86%85%22+%E6%8E%83%E9%99%A4+%E6%B0%8F%E5%AD%90+%E7%B6%AD%E6%8C%81%E7%AE%A1%E7%90%86+%E6%B0%91%E4%BF%97+%E8%AB%96%E6%96%87)
- **Rests on it:** swept ground produced by tending, with a ragged edge, on `religion-and-death.html`, now an absence note.
- Blocked by: ja.wikipedia 参道 gives the gravel's meaning and nothing on sweeping.

### 128. Robert B. Marks, Tigers, Rice, Silk, and Silt (Cambridge, 1998) - shatian and dike-pond tenure, the Canton market

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cambridge Core](https://www.cambridge.org/core/books/tigers-rice-silk-and-silt/)**
- Fallback: [Google: Marks "Tigers, Rice, Silk, and Silt" shatian "mulberry" fishpond Canton delta tenure](https://www.google.com/search?q=Marks+%22Tigers%2C+Rice%2C+Silk%2C+and+Silt%22+shatian+%22mulberry%22+fishpond+Canton+delta+tenure)
- **Rests on it:** smallholder tenure and water access to Canton, and the shatian staying in rice, on `archetypes.html`, now an absence note.
- Blocked by: a book; zh.wikipedia 桑基魚塘, 珠江三角洲 and 沙田 are silent.

### 129. David Faure, Emperor and Ancestor: State and Lineage in South China (Stanford, 2007) - shatian lineage estates

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Stanford University Press](https://www.sup.org/books/title/?id=4763)**
- Fallback: [Google: David Faure "Emperor and Ancestor" shatian "sands" lineage Pearl River Delta rice](https://www.google.com/search?q=David+Faure+%22Emperor+and+Ancestor%22+shatian+%22sands%22+lineage+Pearl+River+Delta+rice)
- **Rests on it:** the same shatian comparison.
- Blocked by: a book.

### 130. Li Bozhong, Agricultural Development in Jiangnan, 1620-1850 (1998) - the ten mu per farmer

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Springer](https://link.springer.com/book/10.1007/978-1-349-14830-7)**
- Fallback: [Google: Li Bozhong "Agricultural Development in Jiangnan" 1620-1850 farm size mu per household mid-Qing](https://www.google.com/search?q=Li+Bozhong+%22Agricultural+Development+in+Jiangnan%22+1620-1850+farm+size+mu+per+household+mid-Qing)
- **Rests on it:** the mid-Qing Jiangnan farm of ~10 mu on `archetypes.html` and `fields.html`.
- Blocked by: a book; the cssn polder page carries no holding size.

### 131. MAFF documentation of the 1963 paddy consolidation standard (圃場整備事業 昭和38年 標準区画)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF](https://www.maff.go.jp/j/nousin/nouti/hozyo/index.html)**
- Fallback: [Google: 農林水産省 圃場整備事業 昭和38年 1963 標準区画 "30m×100m" 30a 土地改良](https://www.google.com/search?q=%E8%BE%B2%E6%9E%97%E6%B0%B4%E7%94%A3%E7%9C%81+%E5%9C%83%E5%A0%B4%E6%95%B4%E5%82%99%E4%BA%8B%E6%A5%AD+%E6%98%AD%E5%92%8C38%E5%B9%B4+1963+%E6%A8%99%E6%BA%96%E5%8C%BA%E7%94%BB+%2230m%C3%97100m%22+30a+%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF)
- **Rests on it:** the 1963 hojo seibi standard on `archetypes.html`, replaced by ja.wikipedia's 24 by 125 m plot.
- Blocked by: maff.go.jp returned 403.

### 132. Joseph Needham, Science and Civilisation in China vol. 4 part 3 - the 埽 fascine revetment and its antiquity

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cambridge Core](https://www.cambridge.org/core/books/science-and-civilisation-in-china/)**
- Fallback: [Google: Needham "Science and Civilisation in China" volume 4 part 3 "sao" 埽 fascine kaoliang willow dike Hu-tzu breach Han](https://www.google.com/search?q=Needham+%22Science+and+Civilisation+in+China%22+volume+4+part+3+%22sao%22+%E5%9F%BD+fascine+kaoliang+willow+dike+Hu-tzu+breach+Han)
- **Rests on it:** willow-fascine bank protection's Chinese antiquity on `archetypes.html`, now labeled unread.
- Blocked by: a book; zh.wikipedia 埽 does not exist and en.wikipedia Fascine knows only European military uses.

### 133. Hugo Schiechtl, Bioengineering for Land Reclamation and Conservation (1980) - willow row spacing by soil

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive (lending)](https://archive.org/details/bioengineeringfo0000schi)**
- Fallback: [Google: Schiechtl "Bioengineering for Land Reclamation and Conservation" 1980 brush layer spacing rows willow](https://www.google.com/search?q=Schiechtl+%22Bioengineering+for+Land+Reclamation+and+Conservation%22+1980+brush+layer+spacing+rows+willow)
- **Rests on it:** the 1-1.5 m and 1.5-2 m willow row spacings on `archetypes.html`, now an absence note.
- Blocked by: a print manual.

### 134. USDA NRCS Engineering Field Handbook, chapter 18, 'Soil Bioengineering for Upland Slope Protection' - live stake and fascine spacing

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NRCS PDF](https://directives.nrcs.usda.gov/sites/default/files2/1712930731/Chapter%2018%20-%20Soil%20Bioengineering%20for%20Upland%20Slope%20Protection%20and%20Erosion%20Reduction.pdf)**
- Fallback: [Google: NRCS "Engineering Field Handbook" chapter 18 "soil bioengineering for upland slope protection" live stake fascine spacing](https://www.google.com/search?q=NRCS+%22Engineering+Field+Handbook%22+chapter+18+%22soil+bioengineering+for+upland+slope+protection%22+live+stake+fascine+spacing)
- **Rests on it:** the same row spacings.
- Blocked by: not reached by address this pass.

### 135. The Shunde gazetteer on collective silkworm houses (集体蚕房, 1958)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Guangdong gazetteer office](https://dfz.gd.gov.cn/)**
- Fallback: [Google: 顺德 集体蚕房 1958 人民公社 桑基鱼塘 地方志](https://www.google.com/search?q=%E9%A1%BA%E5%BE%B7+%E9%9B%86%E4%BD%93%E8%9A%95%E6%88%BF+1958+%E4%BA%BA%E6%B0%91%E5%85%AC%E7%A4%BE+%E6%A1%91%E5%9F%BA%E9%B1%BC%E5%A1%98+%E5%9C%B0%E6%96%B9%E5%BF%97)
- **Rests on it:** communal rearing halls as a 1950s form on `archetypes.html`, now labeled this page's reading.
- Blocked by: baike 蚕房 describes a modern silkworm house with no date.

### 136. The national intangible-heritage record for 含山轧蚕花 (Tongxiang)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[China ICH network](https://www.ihchina.cn/)**
- Fallback: [Google: 含山轧蚕花 国家级非物质文化遗产 桐乡 清明 蚕花娘娘 蚕神庙](https://www.google.com/search?q=%E5%90%AB%E5%B1%B1%E8%BD%A7%E8%9A%95%E8%8A%B1+%E5%9B%BD%E5%AE%B6%E7%BA%A7%E9%9D%9E%E7%89%A9%E8%B4%A8%E6%96%87%E5%8C%96%E9%81%97%E4%BA%A7+%E6%A1%90%E4%B9%A1+%E6%B8%85%E6%98%8E+%E8%9A%95%E8%8A%B1%E5%A8%98%E5%A8%98+%E8%9A%95%E7%A5%9E%E5%BA%99)
- **Rests on it:** the silk-goddess festival temples as village and town institutions on `archetypes.html`, now an absence note.
- Blocked by: the zh.wikipedia pages do not exist and baike refused.

### 137. The landscape-ecology paper describing the Pearl delta as 'mosaic-like constructed ponds with meandering natural river systems'

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%22mosaic-like%22+%22constructed+ponds%22+%22meandering+natural+river%22+dike-pond+Pearl+River+Delta+landscape)**
- Fallback: [Google: "mosaic-like" "constructed ponds" "meandering natural river" dike-pond Pearl River Delta landscape](https://www.google.com/search?q=%22mosaic-like%22+%22constructed+ponds%22+%22meandering+natural+river%22+dike-pond+Pearl+River+Delta+landscape)
- **Rests on it:** the mosaic description on `archetypes.html`, reduced to paraphrase with an absence note.
- Blocked by: the phrase's host was not identified; Chi and colleagues 2024 does not carry it.

### 138. Japanese tea-history literature on bund-margin tea (畦畔茶)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE (tea research)](https://www.jstage.jst.go.jp/browse/tea)**
- Fallback: [Google: "畦畔茶" 畦畔茶園 自家用茶 歴史 水田 畦](https://www.google.com/search?q=%22%E7%95%A6%E7%95%94%E8%8C%B6%22+%E7%95%A6%E7%95%94%E8%8C%B6%E5%9C%92+%E8%87%AA%E5%AE%B6%E7%94%A8%E8%8C%B6+%E6%AD%B4%E5%8F%B2+%E6%B0%B4%E7%94%B0+%E7%95%A6)
- **Rests on it:** bund-margin tea as a Japanese practice on `archetypes.html`, now an absence note.
- Blocked by: kotobank 畦畔茶 does not exist.

### 139. A PRC tea-industry history of contour-terraced tea gardens after 1949 (等高梯级茶园)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[CNKI](https://www.cnki.net/)**
- Fallback: [Google: "等高梯级茶园" 建设 1950年代 推广 茶园 开垦 历史](https://www.google.com/search?q=%22%E7%AD%89%E9%AB%98%E6%A2%AF%E7%BA%A7%E8%8C%B6%E5%9B%AD%22+%E5%BB%BA%E8%AE%BE+1950%E5%B9%B4%E4%BB%A3+%E6%8E%A8%E5%B9%BF+%E8%8C%B6%E5%9B%AD+%E5%BC%80%E5%9E%A6+%E5%8E%86%E5%8F%B2)
- **Rests on it:** contour-terraced tea as a post-1949 state program on `archetypes.html`, now an absence note.
- Blocked by: zh.wikipedia 茶园 does not exist.

### 140. A Chinese description of polder canal alignment (圩内河 走向) - curves against corners

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Google search](https://www.google.com/search?q=%E5%9C%A9%E7%94%B0+%E5%9C%A9%E5%86%85%E6%B2%B3+%E6%B2%B3%E9%81%93+%E8%B5%B0%E5%90%91+%E5%BC%AF%E6%9B%B2+%E8%BD%AC%E8%A7%92+%E5%A1%98%E6%B5%A6+%E7%81%8C%E6%BA%89+%E6%B8%A0%E9%81%93+%E5%BD%A2%E6%80%81)**
- Fallback: [Google: 圩田 圩内河 河道 走向 弯曲 转角 塘浦 灌溉 渠道 形态](https://www.google.com/search?q=%E5%9C%A9%E7%94%B0+%E5%9C%A9%E5%86%85%E6%B2%B3+%E6%B2%B3%E9%81%93+%E8%B5%B0%E5%90%91+%E5%BC%AF%E6%9B%B2+%E8%BD%AC%E8%A7%92+%E5%A1%98%E6%B5%A6+%E7%81%8C%E6%BA%89+%E6%B8%A0%E9%81%93+%E5%BD%A2%E6%80%81)
- **Rests on it:** rounded canal corners and crookeder laterals on `archetypes.html`, now an absence note.
- Blocked by: the dili360 feature gives only the chessboard lattice.

### 141. Ch'u T'ung-tsu, Local Government in China under the Ch'ing (1962)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Harvard University Press](https://www.hup.harvard.edu/books/9780674537781)**
- Fallback: [Google: Ch'ü T'ung-tsu "Local Government in China under the Ch'ing" magistrate county population clerks runners](https://www.google.com/search?q=Ch%27%C3%BC+T%27ung-tsu+%22Local+Government+in+China+under+the+Ch%27ing%22+magistrate+county+population+clerks+runners)
- **Rests on it:** the 100,000-200,000 inhabitants of a Chinese county on `buildings.html`, now an absence note.
- Blocked by: a book; en.wikipedia County (China) gives counts of counties and no population.

### 142. Watt, The District Magistrate in Late Imperial China (1972)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive (lending)](https://archive.org/details/districtmagistra0000watt)**
- Fallback: [Google: "The District Magistrate in Late Imperial China" Watt 1972 Columbia University Press yamen](https://www.google.com/search?q=%22The+District+Magistrate+in+Late+Imperial+China%22+Watt+1972+Columbia+University+Press+yamen)
- **Rests on it:** the county yamen's program and the absence of a training hall on `buildings.html`.
- Blocked by: a lending-restricted scan.

### 143. 上嶋善治『史跡高山陣屋跡』岐阜県文化財保護センター調査報告書1 - the Takayama excavation report

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nara National Research Institute report archive](https://sitereports.nabunken.go.jp/ja/search?s=%E5%8F%B2%E8%B7%A1%E9%AB%98%E5%B1%B1%E9%99%A3%E5%B1%8B%E8%B7%A1)**
- Fallback: [Google: "史跡高山陣屋跡" 岐阜県文化財保護センター調査報告書 上嶋善治](https://www.google.com/search?q=%22%E5%8F%B2%E8%B7%A1%E9%AB%98%E5%B1%B1%E9%99%A3%E5%B1%8B%E8%B7%A1%22+%E5%B2%90%E9%98%9C%E7%9C%8C%E6%96%87%E5%8C%96%E8%B2%A1%E4%BF%9D%E8%AD%B7%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC%E8%AA%BF%E6%9F%BB%E5%A0%B1%E5%91%8A%E6%9B%B8+%E4%B8%8A%E5%B6%8B%E5%96%84%E6%B2%BB)
- **Rests on it:** the domestic size order, the 37-42% coverage, the forecourt share and the building-to-wall offset on `buildings.html`, all absence notes.
- Blocked by: a print report; the archive search page carries no text itself.

### 144. Agency for Cultural Affairs database entry for the Izumo Taisha main sanctuary (出雲大社本殿)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[national designated-property database](https://kunishitei.bunka.go.jp/heritage/detail/102/00002166)**
- Fallback: [Google: 国指定文化財等データベース 出雲大社本殿 国宝 桁行二間 梁間二間 大社造](https://www.google.com/search?q=%E5%9B%BD%E6%8C%87%E5%AE%9A%E6%96%87%E5%8C%96%E8%B2%A1%E7%AD%89%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9+%E5%87%BA%E9%9B%B2%E5%A4%A7%E7%A4%BE%E6%9C%AC%E6%AE%BF+%E5%9B%BD%E5%AE%9D+%E6%A1%81%E8%A1%8C%E4%BA%8C%E9%96%93+%E6%A2%81%E9%96%93%E4%BA%8C%E9%96%93+%E5%A4%A7%E7%A4%BE%E9%80%A0)
- **Rests on it:** Izumo's 2 by 2 ken on `buildings.html`, now labeled this page's reading and a sanctuary rather than a worship hall.
- Blocked by: the Wikipedia pages give only the 24 m height.

### 145. 『江戸町触集成』 / 黒木喬『江戸の火事』 - Edo's fire-separation ordinances and per-building precautions

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokyo Metropolitan Library Edo collection](https://www.library.metro.tokyo.lg.jp/collection/edo/)**
- Fallback: [Google: 江戸町触集成 火除地 明地 家作 土蔵造 奨励 防火 間隔 塙書房](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8%E7%94%BA%E8%A7%A6%E9%9B%86%E6%88%90+%E7%81%AB%E9%99%A4%E5%9C%B0+%E6%98%8E%E5%9C%B0+%E5%AE%B6%E4%BD%9C+%E5%9C%9F%E8%94%B5%E9%80%A0+%E5%A5%A8%E5%8A%B1+%E9%98%B2%E7%81%AB+%E9%96%93%E9%9A%94+%E5%A1%99%E6%9B%B8%E6%88%BF)
- **Rests on it:** the 6-8 ft and 6-10 ft fire gaps and the placement of fire tubs on `buildings.html`, absence notes.
- Blocked by: print volumes; ja.wikipedia 土蔵 gives no spacing.

### 146. The Edo 拝領屋敷 grade tables (plot size by stipend)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokyo Metropolitan Archives](https://www.soumu.metro.tokyo.lg.jp/01soumu/archives/)**
- Fallback: [Google: 江戸 拝領屋敷 坪数 格式 旗本 御家人 屋敷地 一覧 石高別](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8+%E6%8B%9D%E9%A0%98%E5%B1%8B%E6%95%B7+%E5%9D%AA%E6%95%B0+%E6%A0%BC%E5%BC%8F+%E6%97%97%E6%9C%AC+%E5%BE%A1%E5%AE%B6%E4%BA%BA+%E5%B1%8B%E6%95%B7%E5%9C%B0+%E4%B8%80%E8%A6%A7+%E7%9F%B3%E9%AB%98%E5%88%A5)
- **Rests on it:** the 67 tsubo mid-rank house on `buildings.html`, now labeled this page's reading.
- Blocked by: ja.wikipedia 武家屋敷 carries no tsubo figure.

### 147. Tono city's 千葉家住宅 magariya (a measured stable wing)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tono city](https://www.city.tono.iwate.jp/index.cfm/32,0,203,html)**
- Fallback: [Google: 南部曲り家 厩 馬 頭数 間取り 千葉家住宅 重要文化財 実測](https://www.google.com/search?q=%E5%8D%97%E9%83%A8%E6%9B%B2%E3%82%8A%E5%AE%B6+%E5%8E%A9+%E9%A6%AC+%E9%A0%AD%E6%95%B0+%E9%96%93%E5%8F%96%E3%82%8A+%E5%8D%83%E8%91%89%E5%AE%B6%E4%BD%8F%E5%AE%85+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1+%E5%AE%9F%E6%B8%AC)
- **Rests on it:** the county stable's 55-70 sq ft per stall on `buildings.html`, now labeled this page's figure.
- Blocked by: ja.wikipedia 厩 gives a modern European loose-box minimum only.

### 148. 羅爾綱《綠營兵志》 - where Green Standard county troops drilled

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive](https://archive.org/details/lvyingbingzhi)**
- Fallback: [Google: "绿营兵志" 罗尔纲 中华书局 汛塘 教场](https://www.google.com/search?q=%22%E7%BB%BF%E8%90%A5%E5%85%B5%E5%BF%97%22+%E7%BD%97%E5%B0%94%E7%BA%B2+%E4%B8%AD%E5%8D%8E%E4%B9%A6%E5%B1%80+%E6%B1%9B%E5%A1%98+%E6%95%99%E5%9C%BA)
- **Rests on it:** military drill at separate garrison grounds on `buildings.html`, an absence note.
- Blocked by: a print monograph; the Wikipedia pages list the yamen's buildings without a training hall.

### 149. 内乡县衙博物馆 official site - the yamen's building-by-building inventory

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Neixiang County Yamen Museum](http://www.nxxy.org.cn/)**
- Fallback: [Google: 内乡县衙博物馆 官网 大堂 二堂 三堂 建筑布局](https://www.google.com/search?q=%E5%86%85%E4%B9%A1%E5%8E%BF%E8%A1%99%E5%8D%9A%E7%89%A9%E9%A6%86+%E5%AE%98%E7%BD%91+%E5%A4%A7%E5%A0%82+%E4%BA%8C%E5%A0%82+%E4%B8%89%E5%A0%82+%E5%BB%BA%E7%AD%91%E5%B8%83%E5%B1%80)
- **Rests on it:** the same absence of a training hall, and the yamen's gardens and retinue quarters on `government.html`.
- Blocked by: not reached by address.

### 150. 日本建築学会『建築設計資料集成』体育・レクリエーション編 - floor area per practitioner of a budojo

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Maruzen](https://www.maruzen-publishing.co.jp/item/b294744.html)**
- Fallback: [Google: 建築設計資料集成 体育・レクリエーション 日本建築学会 武道場 面積 丸善](https://www.google.com/search?q=%E5%BB%BA%E7%AF%89%E8%A8%AD%E8%A8%88%E8%B3%87%E6%96%99%E9%9B%86%E6%88%90+%E4%BD%93%E8%82%B2%E3%83%BB%E3%83%AC%E3%82%AF%E3%83%AA%E3%82%A8%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3+%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A+%E6%AD%A6%E9%81%93%E5%A0%B4+%E9%9D%A2%E7%A9%8D+%E4%B8%B8%E5%96%84)
- **Rests on it:** the 90-135 sq ft per drilling samurai on `buildings.html`, an absence note.
- Blocked by: a print reference; the kendo pages give only the 9-11 m match court.

### 151. MEXT school facility guidelines (施設整備指針), the 武道場 section

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MEXT](https://www.mext.go.jp/a_menu/shisetu/seibi/1414870.htm)**
- Fallback: [Google: 文部科学省 中学校施設整備指針 武道場 面積 屋内運動場](https://www.google.com/search?q=%E6%96%87%E9%83%A8%E7%A7%91%E5%AD%A6%E7%9C%81+%E4%B8%AD%E5%AD%A6%E6%A0%A1%E6%96%BD%E8%A8%AD%E6%95%B4%E5%82%99%E6%8C%87%E9%87%9D+%E6%AD%A6%E9%81%93%E5%A0%B4+%E9%9D%A2%E7%A9%8D+%E5%B1%8B%E5%86%85%E9%81%8B%E5%8B%95%E5%A0%B4)
- **Rests on it:** the same per-person practice area.
- Blocked by: not reached by address.

### 152. 飯島千秋『江戸幕府財政の研究』(2004) - the money share of bakufu revenue

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NDL search](https://ndlsearch.ndl.go.jp/search?cs=bib&keyword=%E6%B1%9F%E6%88%B8%E5%B9%95%E5%BA%9C%E8%B2%A1%E6%94%BF%E3%81%AE%E7%A0%94%E7%A9%B6)**
- Fallback: [Google: 飯島千秋 "江戸幕府財政の研究" 吉川弘文館 年貢 金納 石代納](https://www.google.com/search?q=%E9%A3%AF%E5%B3%B6%E5%8D%83%E7%A7%8B+%22%E6%B1%9F%E6%88%B8%E5%B9%95%E5%BA%9C%E8%B2%A1%E6%94%BF%E3%81%AE%E7%A0%94%E7%A9%B6%22+%E5%90%89%E5%B7%9D%E5%BC%98%E6%96%87%E9%A4%A8+%E5%B9%B4%E8%B2%A2+%E9%87%91%E7%B4%8D+%E7%9F%B3%E4%BB%A3%E7%B4%8D)
- **Rests on it:** the 30-40% of tax value as coin on `buildings.html`, an absence note.
- Blocked by: a print monograph; 畑方免 says only that dry-field tax was often paid in coin.

### 153. A museum object record for a surviving tensuioke (法量)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokyo Fire Museum](https://www.tfd.metro.tokyo.lg.jp/ts/museum.html)**
- Fallback: [Google: 天水桶 法量 口径 高さ 銅製 文化財 消防博物館 収蔵](https://www.google.com/search?q=%E5%A4%A9%E6%B0%B4%E6%A1%B6+%E6%B3%95%E9%87%8F+%E5%8F%A3%E5%BE%84+%E9%AB%98%E3%81%95+%E9%8A%85%E8%A3%BD+%E6%96%87%E5%8C%96%E8%B2%A1+%E6%B6%88%E9%98%B2%E5%8D%9A%E7%89%A9%E9%A4%A8+%E5%8F%8E%E8%94%B5)
- **Rests on it:** the 2.5 ft fire tub on `buildings.html`, now labeled this page's estimate.
- Blocked by: ja.wikipedia 天水桶 and the fire department page give no dimension.

### 154. Cultural Heritage Online records for Important Cultural Property worship halls (拝殿, 桁行 and 梁間)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cultural Heritage Online](https://bunka.nii.ac.jp/db/heritages/search/?keyword=%E6%8B%9D%E6%AE%BF)**
- Fallback: [Google: 文化遺産オンライン 拝殿 "桁行三間" "梁間二間" 重要文化財 建造物](https://www.google.com/search?q=%E6%96%87%E5%8C%96%E9%81%BA%E7%94%A3%E3%82%AA%E3%83%B3%E3%83%A9%E3%82%A4%E3%83%B3+%E6%8B%9D%E6%AE%BF+%22%E6%A1%81%E8%A1%8C%E4%B8%89%E9%96%93%22+%22%E6%A2%81%E9%96%93%E4%BA%8C%E9%96%93%22+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1+%E5%BB%BA%E9%80%A0%E7%89%A9)
- **Rests on it:** the 3-5 ken provincial haiden on `buildings.html`, an absence note.
- Blocked by: the Wikipedia pages give no ken figure.

### 155. A folk-implement (民具) survey measuring carts and their working space

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nara National Research Institute report archive](https://sitereports.nabunken.go.jp/ja/search?q=%E8%8D%B7%E8%BB%8A%20%E6%B0%91%E5%85%B7%20%E5%AF%B8%E6%B3%95)**
- Fallback: [Google: 民具調査報告書 荷車 大八車 実測 全長 全幅 尺 報告書 PDF](https://www.google.com/search?q=%E6%B0%91%E5%85%B7%E8%AA%BF%E6%9F%BB%E5%A0%B1%E5%91%8A%E6%9B%B8+%E8%8D%B7%E8%BB%8A+%E5%A4%A7%E5%85%AB%E8%BB%8A+%E5%AE%9F%E6%B8%AC+%E5%85%A8%E9%95%B7+%E5%85%A8%E5%B9%85+%E5%B0%BA+%E5%A0%B1%E5%91%8A%E6%9B%B8+PDF)
- **Rests on it:** the 15-20 ft loading apron on `buildings.html`, an absence note.
- Blocked by: ja.wikipedia 大八車 gives only the cart's eight-shaku bed.

### 156. The 在村剣術 literature - village-based swordsmanship in the late Edo countryside

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE search](https://www.jstage.jst.go.jp/result/global/-char/ja?globalSearchKey=%E5%9C%A8%E6%9D%91%E5%89%A3%E8%A1%93)**
- Fallback: [Google: 在村剣術 幕末 農村 稽古場 論文 J-STAGE 剣道史](https://www.google.com/search?q=%E5%9C%A8%E6%9D%91%E5%89%A3%E8%A1%93+%E5%B9%95%E6%9C%AB+%E8%BE%B2%E6%9D%91+%E7%A8%BD%E5%8F%A4%E5%A0%B4+%E8%AB%96%E6%96%87+J-STAGE+%E5%89%A3%E9%81%93%E5%8F%B2)
- **Rests on it:** rural practice leaving equipment rather than architecture on `buildings.html`, an absence note.
- Blocked by: ja.wikipedia 道場 frames the change by period, not by town and country.

### 157. MDPI Forests 8(10):397 (2017) - the Castanopsis stand at 666 to 404 stems per hectare

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MDPI](https://www.mdpi.com/1999-4907/8/10/397)**
- Fallback: [Google: Forests 2017 8 10 397 Castanopsis stand density 666 404 stems per hectare 28 years](https://www.google.com/search?q=Forests+2017+8+10+397+Castanopsis+stand+density+666+404+stems+per+hectare+28+years)
- **Rests on it:** the 500-800 canopy stems per hectare and the 13 ft spacing on `vegetation.html`, absence notes.
- Blocked by: mdpi.com refuses an automated fetch (403).

### 158. The Kobe satoyama restoration paper, Urban Forestry & Urban Greening (S1618866715000370)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1618866715000370)**
- Fallback: [Google: S1618866715000370 "Urban Forestry & Urban Greening" satoyama Kobe restoration stand density canopy](https://www.google.com/search?q=S1618866715000370+%22Urban+Forestry+%26+Urban+Greening%22+satoyama+Kobe+restoration+stand+density+canopy)
- **Rests on it:** the same density band and the 5-8 m crown width on `vegetation.html`.
- Blocked by: paywalled.

### 159. Jiao and colleagues 2019, Sustainability 11(2):454 - satoyama coppice management

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MDPI](https://www.mdpi.com/2071-1050/11/2/454)**
- Fallback: [Google: Jiao "Sustainability" 2019 11 454 satoyama "coppice" management litter oaks mdpi](https://www.google.com/search?q=Jiao+%22Sustainability%22+2019+11+454+satoyama+%22coppice%22+management+litter+oaks+mdpi)
- **Rests on it:** fn-33 and fn-34 on `vegetation.html` and the shrub-cutting sentence.
- Blocked by: mdpi.com refuses an automated fetch (403).

### 160. Aomori Prefecture 農業農村整備事業標準設計図集 - the bund-as-path section

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Aomori prefecture PDF](https://www.pref.aomori.lg.jp/soshiki/nourin/noson/files/H2904_nnzusyu_H2911syuusei.pdf)**
- Fallback: [Google: 青森県 農業農村整備事業 標準設計図集 畦畔 H2904_nnzusyu_H2911syuusei pdf](https://www.google.com/search?q=%E9%9D%92%E6%A3%AE%E7%9C%8C+%E8%BE%B2%E6%A5%AD%E8%BE%B2%E6%9D%91%E6%95%B4%E5%82%99%E4%BA%8B%E6%A5%AD+%E6%A8%99%E6%BA%96%E8%A8%AD%E8%A8%88%E5%9B%B3%E9%9B%86+%E7%95%A6%E7%95%94+H2904_nnzusyu_H2911syuusei+pdf)
- **Rests on it:** the 3 ft footpath bund on `vegetation.html`, an absence note.
- Blocked by: the PDF is served but its text layer could not be read.

### 161. Marshall and Moonen 2002, Field margins in northern Europe, Agriculture Ecosystems & Environment 89

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[DOI](https://doi.org/10.1016/S0167-8809(01)00315-2)**
- Fallback: [Google: Marshall Moonen "Field margins in northern Europe: their functions and interactions with agriculture" 2002](https://www.google.com/search?q=Marshall+Moonen+%22Field+margins+in+northern+Europe%3A+their+functions+and+interactions+with+agriculture%22+2002)
- **Rests on it:** the 1 m clean strip as traditional margin practice on `vegetation.html`, an absence note.
- Blocked by: paywalled.

### 162. Countryside Stewardship option AB10, unharvested cereal headland (the 6 m width)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[gov.uk (redirects to a National Archives snapshot)](https://www.gov.uk/countryside-stewardship-grants/unharvested-cereal-headland-ab10)**
- Fallback: [Google: Countryside Stewardship AB10 "unharvested cereal headland" minimum width 6m gov.uk](https://www.google.com/search?q=Countryside+Stewardship+AB10+%22unharvested+cereal+headland%22+minimum+width+6m+gov.uk)
- **Rests on it:** the 6 m+ conservation headland on `vegetation.html`.
- Blocked by: the archive snapshot refused an automated fetch (405).

### 163. Chen, Nakama and Kurima 2008, house-embracing trees in an Okinawan fengshui village

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[DOI](https://doi.org/10.1016/j.ufug.2007.11.002)**
- Fallback: [Google: Chen Nakama Kurima "Layout and Composition of House-Embracing Trees in an Island Feng Shui Village in Okinawa"](https://www.google.com/search?q=Chen+Nakama+Kurima+%22Layout+and+Composition+of+House-Embracing+Trees+in+an+Island+Feng+Shui+Village+in+Okinawa%22)
- **Rests on it:** the dooryard copse filling a cluster's gaps on `vegetation.html`.
- Blocked by: paywalled.

### 164. Kort 1988, Benefits of windbreaks to field and forage crops

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[DOI](https://doi.org/10.1016/0167-8809(88)90015-9)**
- Fallback: [Google: Kort 1988 "Benefits of windbreaks to field and forage crops" "Agriculture, Ecosystems & Environment"](https://www.google.com/search?q=Kort+1988+%22Benefits+of+windbreaks+to+field+and+forage+crops%22+%22Agriculture%2C+Ecosystems+%26+Environment%22)
- **Rests on it:** the windbreak's shade and stand-off on `vegetation.html`.
- Blocked by: paywalled; the extension manual gives no sun-shadow length.

### 165. Xu Yinong, The Chinese City in Space and Time: Suzhou (2000)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press](https://uhpress.hawaii.edu/title/the-chinese-city-in-space-and-time-the-development-of-urban-form-in-suzhou/)**
- Fallback: [Google: "The Chinese City in Space and Time" Xu Yinong Suzhou urban form](https://www.google.com/search?q=%22The+Chinese+City+in+Space+and+Time%22+Xu+Yinong+Suzhou+urban+form)
- **Rests on it:** the dock basin inside Suzhou's water gate on `river-cities.html` and the civic land share on `fabric.html`, absence notes.
- Blocked by: a book.

### 166. 国立歴史民俗博物館研究報告 - early-modern river landings (河岸場) and their stone steps

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[National Museum of Japanese History repository](https://rekihaku.repo.nii.ac.jp/)**
- Fallback: [Google: 国立歴史民俗博物館研究報告 近世 河岸場 舟運 石積み 雁木 構造](https://www.google.com/search?q=%E5%9B%BD%E7%AB%8B%E6%AD%B4%E5%8F%B2%E6%B0%91%E4%BF%97%E5%8D%9A%E7%89%A9%E9%A4%A8%E7%A0%94%E7%A9%B6%E5%A0%B1%E5%91%8A+%E8%BF%91%E4%B8%96+%E6%B2%B3%E5%B2%B8%E5%A0%B4+%E8%88%9F%E9%81%8B+%E7%9F%B3%E7%A9%8D%E3%81%BF+%E9%9B%81%E6%9C%A8+%E6%A7%8B%E9%80%A0)
- **Rests on it:** the kashi's stepped landing in a faced bank on `river-cities.html`, an absence note.
- Blocked by: no article address could be located without a search.

### 167. MLIT 水文水質データベース - a station's yearly maximum and minimum stage

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Water Information System](http://www1.river.go.jp/)**
- Fallback: [Google: 国土交通省 水文水質データベース 水位 年最高水位 年最低水位 観測所](https://www.google.com/search?q=%E5%9B%BD%E5%9C%9F%E4%BA%A4%E9%80%9A%E7%9C%81+%E6%B0%B4%E6%96%87%E6%B0%B4%E8%B3%AA%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9+%E6%B0%B4%E4%BD%8D+%E5%B9%B4%E6%9C%80%E9%AB%98%E6%B0%B4%E4%BD%8D+%E5%B9%B4%E6%9C%80%E4%BD%8E%E6%B0%B4%E4%BD%8D+%E8%A6%B3%E6%B8%AC%E6%89%80)
- **Rests on it:** a river's level moving 'by many feet' on `river-cities.html`, labeled this page's.
- Blocked by: the figure must be read off a station's own record.

### 168. Sen-dou Chang 1970, Some Observations on the Morphology of Chinese Walled Cities, Annals AAG 60(1)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Taylor and Francis](https://www.tandfonline.com/doi/abs/10.1111/j.1467-8306.1970.tb00711.x)**
- Fallback: [Google: "Some Observations on the Morphology of Chinese Walled Cities" Sen-dou Chang Annals Association American Geographers 1970](https://www.google.com/search?q=%22Some+Observations+on+the+Morphology+of+Chinese+Walled+Cities%22+Sen-dou+Chang+Annals+Association+American+Geographers+1970)
- **Rests on it:** that most cities sit on a river and that moats watered the fields, on `river-cities.html` and `defenses.html`.
- Blocked by: paywalled.

### 169. Guanzi, 乘馬 chapter - the siting rule 凡立國都…必於廣川之上

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project](https://ctext.org/guanzi/cheng-ma)**
- Fallback: [Google: 管子 乘馬 "凡立國都" "非於大山之下" "必於廣川之上"](https://www.google.com/search?q=%E7%AE%A1%E5%AD%90+%E4%B9%98%E9%A6%AC+%22%E5%87%A1%E7%AB%8B%E5%9C%8B%E9%83%BD%22+%22%E9%9D%9E%E6%96%BC%E5%A4%A7%E5%B1%B1%E4%B9%8B%E4%B8%8B%22+%22%E5%BF%85%E6%96%BC%E5%BB%A3%E5%B7%9D%E4%B9%8B%E4%B8%8A%22)
- **Rests on it:** the same river-siting rule.
- Blocked by: ctext.org served a security page to an automated fetch.

### 170. Howard 1971, Optimal angles of stream junction, Water Resources Research 7(4)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Wiley](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/WR007i004p00863)**
- Fallback: [Google: Howard 1971 "Optimal angles of stream junction" Water Resources Research 863](https://www.google.com/search?q=Howard+1971+%22Optimal+angles+of+stream+junction%22+Water+Resources+Research+863)
- **Rests on it:** tributaries joining pointing downstream on `river-cities.html`, an absence note.
- Blocked by: paywalled.

### 171. USDA NRCS Engineering Field Handbook, chapter 14, Water Management (Drainage) - the drain outlet's angle

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NRCS](https://directives.sc.egov.usda.gov/OpenNonWebContent.aspx?content=17812.wba)**
- Fallback: [Google: NRCS "National Engineering Handbook" "Water Management (Drainage)" chapter 14 drain outlet junction angle "direction of flow"](https://www.google.com/search?q=NRCS+%22National+Engineering+Handbook%22+%22Water+Management+%28Drainage%29%22+chapter+14+drain+outlet+junction+angle+%22direction+of+flow%22)
- **Rests on it:** the engineered drainage return cut to point downstream.
- Blocked by: not reached by address.

### 172. 张驭寰《中国城池史》 - how Chinese city moats were watered

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Douban](https://book.douban.com/subject/1449697/)**
- Fallback: [Google: "中国城池史" 张驭寰 百花文艺出版社 护城河 引水 灌溉](https://www.google.com/search?q=%22%E4%B8%AD%E5%9B%BD%E5%9F%8E%E6%B1%A0%E5%8F%B2%22+%E5%BC%A0%E9%A9%AD%E5%AF%B0+%E7%99%BE%E8%8A%B1%E6%96%87%E8%89%BA%E5%87%BA%E7%89%88%E7%A4%BE+%E6%8A%A4%E5%9F%8E%E6%B2%B3+%E5%BC%95%E6%B0%B4+%E7%81%8C%E6%BA%89)
- **Rests on it:** the moat kept full by the river's stage and moats watering the fields, on `river-cities.html` and `defenses.html`.
- Blocked by: a print book.

### 173. Ministry of the Environment studies of the Imperial Palace outer moats as closed water bodies

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Ministry of the Environment](https://www.env.go.jp/garden/kokyogaien/)**
- Fallback: [Google: 皇居外苑 濠 水質浄化 閉鎖性水域 環境省 報告](https://www.google.com/search?q=%E7%9A%87%E5%B1%85%E5%A4%96%E8%8B%91+%E6%BF%A0+%E6%B0%B4%E8%B3%AA%E6%B5%84%E5%8C%96+%E9%96%89%E9%8E%96%E6%80%A7%E6%B0%B4%E5%9F%9F+%E7%92%B0%E5%A2%83%E7%9C%81+%E5%A0%B1%E5%91%8A)
- **Rests on it:** the same moat water regime.
- Blocked by: not reached by address.

### 174. 廻米 (the annual shipment of tax rice) - its season

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kotobank](https://kotobank.jp/word/%E5%BB%BB%E7%B1%B3)**
- Fallback: [Google: 廻米 年貢米 江戸 大坂 積み出し 秋 収穫後 コトバンク](https://www.google.com/search?q=%E5%BB%BB%E7%B1%B3+%E5%B9%B4%E8%B2%A2%E7%B1%B3+%E6%B1%9F%E6%88%B8+%E5%A4%A7%E5%9D%82+%E7%A9%8D%E3%81%BF%E5%87%BA%E3%81%97+%E7%A7%8B+%E5%8F%8E%E7%A9%AB%E5%BE%8C+%E3%82%B3%E3%83%88%E3%83%90%E3%83%B3%E3%82%AF)
- **Rests on it:** the wharf's seasonal turnover on `river-cities.html`, labeled unread.
- Blocked by: not fetched this pass.

### 175. The Hankou (武汉关) gauge record - flood crest against low water

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Changjiang Water Resources Commission](http://yn.cjw.gov.cn/)**
- Fallback: [Google: 武汉关 水位 历史最高 1954年 29.73米 枯水位 长江 水文](https://www.google.com/search?q=%E6%AD%A6%E6%B1%89%E5%85%B3+%E6%B0%B4%E4%BD%8D+%E5%8E%86%E5%8F%B2%E6%9C%80%E9%AB%98+1954%E5%B9%B4+29.73%E7%B1%B3+%E6%9E%AF%E6%B0%B4%E4%BD%8D+%E9%95%BF%E6%B1%9F+%E6%B0%B4%E6%96%87)
- **Rests on it:** a river's annual stage range on `river-cities.html`.
- Blocked by: not reached by address.

### 176. The restored Kyoto takasebune at Ichinofuneiri - the small type's length

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ja.wikipedia 高瀬川 (a locator)](https://ja.wikipedia.org/wiki/%E9%AB%98%E7%80%AC%E5%B7%9D_(%E4%BA%AC%E9%83%BD%E5%BA%9C))**
- Fallback: [Google: 高瀬舟 復元 一之舟入 長さ メートル 幅 積載 高瀬川](https://www.google.com/search?q=%E9%AB%98%E7%80%AC%E8%88%9F+%E5%BE%A9%E5%85%83+%E4%B8%80%E4%B9%8B%E8%88%9F%E5%85%A5+%E9%95%B7%E3%81%95+%E3%83%A1%E3%83%BC%E3%83%88%E3%83%AB+%E5%B9%85+%E7%A9%8D%E8%BC%89+%E9%AB%98%E7%80%AC%E5%B7%9D)
- **Rests on it:** the small end of the barge range on `river-cities.html`.
- Blocked by: the canal page gives the boat no length.

### 177. Strickland and Hardy, The Great Warbow (2005) - killing range against maximum range

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive (lending)](https://archive.org/details/greatwarbowfromh0000stri)**
- Fallback: [Google: "The Great Warbow" Strickland Hardy "Hastings to the Mary Rose" effective range](https://www.google.com/search?q=%22The+Great+Warbow%22+Strickland+Hardy+%22Hastings+to+the+Mary+Rose%22+effective+range)
- **Rests on it:** the aimed-lethal 60 m and the 100-150 m war-bow reach on `defenses.html`, an absence note.
- Blocked by: a book; no page read gives an effective range.

### 178. Kooi and Bergman 1997, An approach to the study of ancient archery using mathematical modelling, Antiquity 71

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[DOI](https://doi.org/10.1017/S0003598X00084568)**
- Fallback: [Google: Kooi Bergman "An approach to the study of ancient archery using mathematical modelling" Antiquity 1997 pdf](https://www.google.com/search?q=Kooi+Bergman+%22An+approach+to+the+study+of+ancient+archery+using+mathematical+modelling%22+Antiquity+1997+pdf)
- **Rests on it:** the same bow ranges.
- Blocked by: paywalled.

### 179. Karpowicz, Ottoman Turkish Bows: Manufacture and Design (2008) - measured composite-bow performance

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive (lending)](https://archive.org/details/ottomanturkishbo0000karp)**
- Fallback: [Google: Karpowicz "Ottoman Turkish Bows" "manufacture and design" performance range](https://www.google.com/search?q=Karpowicz+%22Ottoman+Turkish+Bows%22+%22manufacture+and+design%22+performance+range)
- **Rests on it:** the same bow ranges, the closest composite-bow data in print.
- Blocked by: a book.

### 180. 箱根町『箱根関所復元報告書』 - the restored barrier's plans and bay dimensions

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Hakone barrier site](https://www.hakonesekisyo.jp/fukugen/index.html)**
- Fallback: [Google: 箱根関所 復元 報告書 大番所 足軽番所 平面図 桁行 梁間](https://www.google.com/search?q=%E7%AE%B1%E6%A0%B9%E9%96%A2%E6%89%80+%E5%BE%A9%E5%85%83+%E5%A0%B1%E5%91%8A%E6%9B%B8+%E5%A4%A7%E7%95%AA%E6%89%80+%E8%B6%B3%E8%BB%BD%E7%95%AA%E6%89%80+%E5%B9%B3%E9%9D%A2%E5%9B%B3+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93)
- **Rests on it:** the guard room and inspection hall footprints on `defenses.html`, absence notes.
- Blocked by: the site's pages carry no dimensions.

### 181. Agency for Cultural Affairs database entry for 新居関所 面番所 (ICP)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[national designated-property database](https://kunishitei.bunka.go.jp/heritage/detail/102/00002037)**
- Fallback: [Google: 新居関所 面番所 重要文化財 桁行 梁間 国指定文化財等データベース](https://www.google.com/search?q=%E6%96%B0%E5%B1%85%E9%96%A2%E6%89%80+%E9%9D%A2%E7%95%AA%E6%89%80+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93+%E5%9B%BD%E6%8C%87%E5%AE%9A%E6%96%87%E5%8C%96%E8%B2%A1%E7%AD%89%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9)
- **Rests on it:** the inspection hall's measured footprint.
- Blocked by: not reached by address.

### 182. A measured survey of the Xi'an wall's 敌楼 (the tower on the mamian)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Xi'an City Wall administration](http://www.xacitywall.com/)**
- Fallback: [Google: 西安城墙 敌楼 面阔 进深 米 实测 敌台 保护规划](https://www.google.com/search?q=%E8%A5%BF%E5%AE%89%E5%9F%8E%E5%A2%99+%E6%95%8C%E6%A5%BC+%E9%9D%A2%E9%98%94+%E8%BF%9B%E6%B7%B1+%E7%B1%B3+%E5%AE%9E%E6%B5%8B+%E6%95%8C%E5%8F%B0+%E4%BF%9D%E6%8A%A4%E8%A7%84%E5%88%92)
- **Rests on it:** the 30-40 ft tower on the bastion on `defenses.html`, an absence note.
- Blocked by: zh.wikipedia gives the bastion's size and not the building's.

### 183. Beijing Municipal Administration of Cultural Heritage - the Zhengyangmen gate tower's measurements

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Beijing cultural heritage administration](https://www.bjww.gov.cn/)**
- Fallback: [Google: 正阳门 城楼 面阔七间 进深三间 米 实测 北京市文物局](https://www.google.com/search?q=%E6%AD%A3%E9%98%B3%E9%97%A8+%E5%9F%8E%E6%A5%BC+%E9%9D%A2%E9%98%94%E4%B8%83%E9%97%B4+%E8%BF%9B%E6%B7%B1%E4%B8%89%E9%97%B4+%E7%B1%B3+%E5%AE%9E%E6%B5%8B+%E5%8C%97%E4%BA%AC%E5%B8%82%E6%96%87%E7%89%A9%E5%B1%80)
- **Rests on it:** the 120-130 ft towers reserved for a capital on `defenses.html`.
- Blocked by: zh.wikipedia's Zhengyangmen figures run larger than the band.

### 184. Steinhardt, Chinese Imperial City Planning (1990) - avenue widths against gate openings

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press](https://uhpress.hawaii.edu/title/chinese-imperial-city-planning/)**
- Fallback: [Google: Steinhardt "Chinese Imperial City Planning" Chang'an avenue width metres gate excavated Mingdemen](https://www.google.com/search?q=Steinhardt+%22Chinese+Imperial+City+Planning%22+Chang%27an+avenue+width+metres+gate+excavated+Mingdemen)
- **Rests on it:** a gate narrowing the road on `defenses.html`, an absence note.
- Blocked by: a book; every page read gives a gate width alone.

### 185. Mozi, 备城门 - the earliest form of the projecting wall tower

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project](https://ctext.org/mozi/quan-bei-men)**
- Fallback: [Google: 墨子 备城门 "行城之法" 高城二十尺 上加堞 广十尺](https://www.google.com/search?q=%E5%A2%A8%E5%AD%90+%E5%A4%87%E5%9F%8E%E9%97%A8+%22%E8%A1%8C%E5%9F%8E%E4%B9%8B%E6%B3%95%22+%E9%AB%98%E5%9F%8E%E4%BA%8C%E5%8D%81%E5%B0%BA+%E4%B8%8A%E5%8A%A0%E5%A0%9E+%E5%B9%BF%E5%8D%81%E5%B0%BA)
- **Rests on it:** the ORIGINAL purpose of the projecting tower on `defenses.html`, now labeled the record's.
- Blocked by: the paper traces the feature to the Mozi; the primary was not fetched.

### 186. The Chinese fire-lane (火巷) literature - fire and the walled city

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[zh.wikipedia (404 to an automated fetch)](https://zh.wikipedia.org/wiki/%E7%81%AB%E5%B7%B7)**
- Fallback: [Google: 火巷 南宋 临安 防火 巷道 城内 木构 密集 火灾](https://www.google.com/search?q=%E7%81%AB%E5%B7%B7+%E5%8D%97%E5%AE%8B+%E4%B8%B4%E5%AE%89+%E9%98%B2%E7%81%AB+%E5%B7%B7%E9%81%93+%E5%9F%8E%E5%86%85+%E6%9C%A8%E6%9E%84+%E5%AF%86%E9%9B%86+%E7%81%AB%E7%81%BE)
- **Rests on it:** the rampart trapping a blaze on `towns.html` and `fabric.html`, absence notes.
- Blocked by: the only address guessed returned 404.

### 187. Skinner 1964, Marketing and Social Structure in Rural China, Journal of Asian Studies 24:1

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[JSTOR](https://www.jstor.org/stable/2050412)**
- Fallback: [Google: Skinner "Marketing and Social Structure in Rural China" 1964 "Journal of Asian Studies" standard marketing community pdf](https://www.google.com/search?q=Skinner+%22Marketing+and+Social+Structure+in+Rural+China%22+1964+%22Journal+of+Asian+Studies%22+standard+marketing+community+pdf)
- **Rests on it:** market-goers at the catchment's edge staying over on `towns.html`, an absence note.
- Blocked by: paywalled.

### 188. 田林明 on the Tonami dispersed settlement and its groves

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE search](https://www.jstage.jst.go.jp/result/global/-char/ja?globalSearchKey=%E5%B1%8B%E6%95%B7%E6%9E%97)**
- Fallback: [Google: 田林明 砺波平野 散村 屋敷林 カイニョ 地理学評論 PDF](https://www.google.com/search?q=%E7%94%B0%E6%9E%97%E6%98%8E+%E7%A0%BA%E6%B3%A2%E5%B9%B3%E9%87%8E+%E6%95%A3%E6%9D%91+%E5%B1%8B%E6%95%B7%E6%9E%97+%E3%82%AB%E3%82%A4%E3%83%8B%E3%83%A7+%E5%9C%B0%E7%90%86%E5%AD%A6%E8%A9%95%E8%AB%96+PDF)
- **Rests on it:** the nucleus sheltering itself on `towns.html`, labeled this page's.
- Blocked by: no article address without a search.

### 189. Brandle, Hodges and Zhou 2004, Windbreaks in North American agricultural systems

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[DOI](https://doi.org/10.1023/B:AGFO.0000028990.31801.62)**
- Fallback: [Google: Brandle Hodges Zhou 2004 "Windbreaks in North American agricultural systems" Agroforestry Systems pdf](https://www.google.com/search?q=Brandle+Hodges+Zhou+2004+%22Windbreaks+in+North+American+agricultural+systems%22+Agroforestry+Systems+pdf)
- **Rests on it:** the shelter belt's across-the-wind rule on `towns.html`, an absence note.
- Blocked by: paywalled.

### 190. USDA NRCS Conservation Practice Standard 380, Windbreak/Shelterbelt Establishment

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NRCS PDF](https://www.nrcs.usda.gov/sites/default/files/2022-09/Windbreak-Shelterbelt-Establishment-and-Renovation-380-CPS.pdf)**
- Fallback: [Google: NRCS "Conservation Practice Standard" 380 "Windbreak/Shelterbelt Establishment" perpendicular "prevailing wind" pdf](https://www.google.com/search?q=NRCS+%22Conservation+Practice+Standard%22+380+%22Windbreak%2FShelterbelt+Establishment%22+perpendicular+%22prevailing+wind%22+pdf)
- **Rests on it:** the same perpendicular rule.
- Blocked by: not reached by address.

### 191. Wu Qingzhou 1989, The Protection of China's Ancient Cities from Flood Damage, Disasters 13

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1467-7717.1989.tb00713.x)**
- Fallback: [Google: "Wu Qingzhou" "protection of China's ancient cities from flood damage" Disasters 1989](https://www.google.com/search?q=%22Wu+Qingzhou%22+%22protection+of+China%27s+ancient+cities+from+flood+damage%22+Disasters+1989)
- **Rests on it:** intramural ponds as flood refuge on `fabric.html` and the moat as storm drain on `hinterland.html`, absence notes.
- Blocked by: paywalled.

### 192. 吴庆洲《中国古城防洪研究》(2009)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[China Architecture and Building Press](http://www.cabp.com.cn/)**
- Fallback: [Google: 吴庆洲 《中国古城防洪研究》 中国建筑工业出版社 蓄洪](https://www.google.com/search?q=%E5%90%B4%E5%BA%86%E6%B4%B2+%E3%80%8A%E4%B8%AD%E5%9B%BD%E5%8F%A4%E5%9F%8E%E9%98%B2%E6%B4%AA%E7%A0%94%E7%A9%B6%E3%80%8B+%E4%B8%AD%E5%9B%BD%E5%BB%BA%E7%AD%91%E5%B7%A5%E4%B8%9A%E5%87%BA%E7%89%88%E7%A4%BE+%E8%93%84%E6%B4%AA)
- **Rests on it:** the same flood storage of city ponds and moats.
- Blocked by: a print monograph.

### 193. Skinner (ed.), The City in Late Imperial China (1977) - the other chapters' land-use budgets

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Stanford University Press](https://www.sup.org/books/title/?id=1795)**
- Fallback: [Google: Skinner "The City in Late Imperial China" Stanford 1977 "Morphology of Walled Capitals"](https://www.google.com/search?q=Skinner+%22The+City+in+Late+Imperial+China%22+Stanford+1977+%22Morphology+of+Walled+Capitals%22)
- **Rests on it:** the civic land share and the wall's cost per length on `fabric.html` and `towns.html`.
- Blocked by: a book; the Chang chapter carries no such figures.

### 194. 成一农《古代城市形态研究方法新探》(2009) - the walled seat's components, the drill ground among them

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Social Sciences Academic Press](https://www.ssap.com.cn/)**
- Fallback: [Google: 成一农 《古代城市形态研究方法新探》 社会科学文献出版社 校场](https://www.google.com/search?q=%E6%88%90%E4%B8%80%E5%86%9C+%E3%80%8A%E5%8F%A4%E4%BB%A3%E5%9F%8E%E5%B8%82%E5%BD%A2%E6%80%81%E7%A0%94%E7%A9%B6%E6%96%B9%E6%B3%95%E6%96%B0%E6%8E%A2%E3%80%8B+%E7%A4%BE%E4%BC%9A%E7%A7%91%E5%AD%A6%E6%96%87%E7%8C%AE%E5%87%BA%E7%89%88%E7%A4%BE+%E6%A0%A1%E5%9C%BA)
- **Rests on it:** the drill ground inside a county seat on `fabric.html`, an absence note.
- Blocked by: a print monograph.

### 195. 李孝聪《中国城市的历史空间》(2015) - late-imperial city plans component by component

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Peking University Press](https://www.pup.cn/)**
- Fallback: [Google: 李孝聪 《中国城市的历史空间》 北京大学出版社 2015](https://www.google.com/search?q=%E6%9D%8E%E5%AD%9D%E8%81%AA+%E3%80%8A%E4%B8%AD%E5%9B%BD%E5%9F%8E%E5%B8%82%E7%9A%84%E5%8E%86%E5%8F%B2%E7%A9%BA%E9%97%B4%E3%80%8B+%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E5%87%BA%E7%89%88%E7%A4%BE+2015)
- **Rests on it:** the same drill-ground placement.
- Blocked by: a print monograph.

### 196. 董鑑泓《中国城市建设史》 - measured street layouts and areas of walled cities

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Douban](https://book.douban.com/subject/1400526/)**
- Fallback: [Google: 董鉴泓 "中国城市建设史" 中国建筑工业出版社 街道 用地 比例](https://www.google.com/search?q=%E8%91%A3%E9%89%B4%E6%B3%93+%22%E4%B8%AD%E5%9B%BD%E5%9F%8E%E5%B8%82%E5%BB%BA%E8%AE%BE%E5%8F%B2%22+%E4%B8%AD%E5%9B%BD%E5%BB%BA%E7%AD%91%E5%B7%A5%E4%B8%9A%E5%87%BA%E7%89%88%E7%A4%BE+%E8%A1%97%E9%81%93+%E7%94%A8%E5%9C%B0+%E6%AF%94%E4%BE%8B)
- **Rests on it:** the 10-20% street share on `fabric.html`, an absence note.
- Blocked by: a print monograph.

### 197. 部落解放・人権研究所 - the siting of outcast villages in early-modern castle towns

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Buraku Liberation and Human Rights Research Institute](https://www.blhrri.org/)**
- Fallback: [Google: 近世 城下町 "かわた村" 立地 城下 町割り 被差別部落 論文 PDF](https://www.google.com/search?q=%E8%BF%91%E4%B8%96+%E5%9F%8E%E4%B8%8B%E7%94%BA+%22%E3%81%8B%E3%82%8F%E3%81%9F%E6%9D%91%22+%E7%AB%8B%E5%9C%B0+%E5%9F%8E%E4%B8%8B+%E7%94%BA%E5%89%B2%E3%82%8A+%E8%A2%AB%E5%B7%AE%E5%88%A5%E9%83%A8%E8%90%BD+%E8%AB%96%E6%96%87+PDF)
- **Rests on it:** the intramural burakumin quarter on `fabric.html`, now labeled the setting's own.
- Blocked by: en.wikipedia Burakumin's one siting is outside Kyoto's walls.

### 198. 李采芹《中国消防通史》 - urban fire in walled Chinese cities

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Douban](https://book.douban.com/subject/1447963/)**
- Fallback: [Google: 李采芹 "中国消防通史" 群众出版社 城市火灾 城墙](https://www.google.com/search?q=%E6%9D%8E%E9%87%87%E8%8A%B9+%22%E4%B8%AD%E5%9B%BD%E6%B6%88%E9%98%B2%E9%80%9A%E5%8F%B2%22+%E7%BE%A4%E4%BC%97%E5%87%BA%E7%89%88%E7%A4%BE+%E5%9F%8E%E5%B8%82%E7%81%AB%E7%81%BE+%E5%9F%8E%E5%A2%99)
- **Rests on it:** the rampart keeping a blaze in on `fabric.html`.
- Blocked by: a print monograph.

### 199. 宿村大概帳 (1843) - hatago counts per post station

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[National Archives of Japan](https://www.digital.archives.go.jp/)**
- Fallback: [Google: 宿村大概帳 天保十四年 宿場 旅籠屋 軒数 国立公文書館](https://www.google.com/search?q=%E5%AE%BF%E6%9D%91%E5%A4%A7%E6%A6%82%E5%B8%B3+%E5%A4%A9%E4%BF%9D%E5%8D%81%E5%9B%9B%E5%B9%B4+%E5%AE%BF%E5%A0%B4+%E6%97%85%E7%B1%A0%E5%B1%8B+%E8%BB%92%E6%95%B0+%E5%9B%BD%E7%AB%8B%E5%85%AC%E6%96%87%E6%9B%B8%E9%A4%A8)
- **Rests on it:** the lodging-house count of a non-station seat on `fabric.html`, an absence note.
- Blocked by: the archive needs a search to reach the item.

### 200. Vaporis, Breaking Barriers: Travel and the State in Early Modern Japan (1994)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Harvard University Press](https://www.hup.harvard.edu/books/9780674081079)**
- Fallback: [Google: Vaporis "Breaking Barriers: Travel and the State in Early Modern Japan" hatago lodging post station](https://www.google.com/search?q=Vaporis+%22Breaking+Barriers%3A+Travel+and+the+State+in+Early+Modern+Japan%22+hatago+lodging+post+station)
- **Rests on it:** the same lodging provision and unofficial lodging.
- Blocked by: a book.

### 201. Knapp, China's Old Dwellings (2000) - party walls of Chinese town housing

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Hawaii Press](https://uhpress.hawaii.edu/title/chinas-old-dwellings/)**
- Fallback: [Google: Knapp "China's Old Dwellings" rammed earth brick party wall courtyard house town](https://www.google.com/search?q=Knapp+%22China%27s+Old+Dwellings%22+rammed+earth+brick+party+wall+courtyard+house+town)
- **Rests on it:** the shared rammed-earth or brick party walls of Chinese courtyard housing on `fabric.html`, an absence note.
- Blocked by: a book; zh.wikipedia 四合院 gives only the blank outer wall.

### 202. MLIT Tokaido Q&A a0217 - the post stations' horses and porters (re-read verbatim)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MLIT Kanto regional bureau](https://www.ktr.mlit.go.jp/yokohama/tokaido/02_tokaido/04_qa/index2/a0217.htm)**
- Fallback: [Google: 東海道 宿場 伝馬 三十六疋 百人百疋 寛永十五年 国土交通省 関東地方整備局](https://www.google.com/search?q=%E6%9D%B1%E6%B5%B7%E9%81%93+%E5%AE%BF%E5%A0%B4+%E4%BC%9D%E9%A6%AC+%E4%B8%89%E5%8D%81%E5%85%AD%E7%96%8B+%E7%99%BE%E4%BA%BA%E7%99%BE%E7%96%8B+%E5%AF%9B%E6%B0%B8%E5%8D%81%E4%BA%94%E5%B9%B4+%E5%9B%BD%E5%9C%9F%E4%BA%A4%E9%80%9A%E7%9C%81+%E9%96%A2%E6%9D%B1%E5%9C%B0%E6%96%B9%E6%95%B4%E5%82%99%E5%B1%80)
- **Rests on it:** the 1638 date of the hundred horses and porters on `fabric.html`.
- Blocked by: the fetch returned the figures with a 1590 date and garbled phrasing; a person should read the page itself.

### 203. Architectural studies of domain-school martial halls (演武場) - plans and room schedules

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE search](https://www.jstage.jst.go.jp/result/global/-char/ja?globalSearchKey=%E6%BC%94%E6%AD%A6%E5%A0%B4)**
- Fallback: [Google: "演武場" 藩校 建築 平面 site:jstage.jst.go.jp](https://www.google.com/search?q=%22%E6%BC%94%E6%AD%A6%E5%A0%B4%22+%E8%97%A9%E6%A0%A1+%E5%BB%BA%E7%AF%89+%E5%B9%B3%E9%9D%A2+site%3Ajstage.jst.go.jp)
- **Rests on it:** the martial hall's changing room, armory and viewing platform on `government.html`, an absence note.
- Blocked by: no article address without a search.

### 204. 旧致道館 (Tsuruoka) repair report - a surviving domain-school martial hall room by room

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cultural Heritage Online](https://bunka.nii.ac.jp/heritages/detail/)**
- Fallback: [Google: 旧致道館 重要文化財 修理工事報告書 演武場 間取](https://www.google.com/search?q=%E6%97%A7%E8%87%B4%E9%81%93%E9%A4%A8+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1+%E4%BF%AE%E7%90%86%E5%B7%A5%E4%BA%8B%E5%A0%B1%E5%91%8A%E6%9B%B8+%E6%BC%94%E6%AD%A6%E5%A0%B4+%E9%96%93%E5%8F%96)
- **Rests on it:** the same three rooms.
- Blocked by: a print report.

### 205. A comparative architectural study of domain-school and commercial martial halls

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE search](https://www.jstage.jst.go.jp/result/global/-char/ja?globalSearchKey=%E7%94%BA%E9%81%93%E5%A0%B4+%E5%BB%BA%E7%AF%89)**
- Fallback: [Google: 町道場 藩校 演武場 建築構造 比較 論文](https://www.google.com/search?q=%E7%94%BA%E9%81%93%E5%A0%B4+%E8%97%A9%E6%A0%A1+%E6%BC%94%E6%AD%A6%E5%A0%B4+%E5%BB%BA%E7%AF%89%E6%A7%8B%E9%80%A0+%E6%AF%94%E8%BC%83+%E8%AB%96%E6%96%87)
- **Rests on it:** that a domain school's construction did not differ from a private hall's on `government.html`, an absence note.
- Blocked by: no page read compares them.

### 206. Agency for Cultural Affairs entry for the Omura family nagayamon in Kishu

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[national designated-property database](https://kunishitei.bunka.go.jp/heritage/heritagelist)**
- Fallback: [Google: "大村八兵衛" 長屋門 紀州 桁行 梁間 文化財](https://www.google.com/search?q=%22%E5%A4%A7%E6%9D%91%E5%85%AB%E5%85%B5%E8%A1%9B%22+%E9%95%B7%E5%B1%8B%E9%96%80+%E7%B4%80%E5%B7%9E+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93+%E6%96%87%E5%8C%96%E8%B2%A1)
- **Rests on it:** the measured nagayamon examples on `government.html`, an absence note.
- Blocked by: no page read carries a gate dimension.

### 207. 旧因州池田屋敷表門 (the Tokyo ICP long-house gate)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cultural Heritage Online](https://bunka.nii.ac.jp/heritages/detail/196036)**
- Fallback: [Google: 旧因州池田屋敷表門 重要文化財 長屋門 桁行 梁間](https://www.google.com/search?q=%E6%97%A7%E5%9B%A0%E5%B7%9E%E6%B1%A0%E7%94%B0%E5%B1%8B%E6%95%B7%E8%A1%A8%E9%96%80+%E9%87%8D%E8%A6%81%E6%96%87%E5%8C%96%E8%B2%A1+%E9%95%B7%E5%B1%8B%E9%96%80+%E6%A1%81%E8%A1%8C+%E6%A2%81%E9%96%93)
- **Rests on it:** the same gate dimensions.
- Blocked by: not reached by address.

### 208. Plans of lower and middle samurai houses by stipend class (Architectural Institute of Japan)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE, AIJ journal](https://www.jstage.jst.go.jp/browse/aija/-char/ja)**
- Fallback: [Google: 下級武士 住宅 平面構成 "納戸" 奉公人 石高 日本建築学会 論文](https://www.google.com/search?q=%E4%B8%8B%E7%B4%9A%E6%AD%A6%E5%A3%AB+%E4%BD%8F%E5%AE%85+%E5%B9%B3%E9%9D%A2%E6%A7%8B%E6%88%90+%22%E7%B4%8D%E6%88%B8%22+%E5%A5%89%E5%85%AC%E4%BA%BA+%E7%9F%B3%E9%AB%98+%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A+%E8%AB%96%E6%96%87)
- **Rests on it:** servants sleeping in the nando below 100-300 koku on `government.html`, an absence note.
- Blocked by: no article address without a search.

### 209. 『仙台市史』通史編 (early modern) - the castle town's ashigaru quarters

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Sendai city](https://www.city.sendai.jp/kyoiku-somu/1211193_2937.html)**
- Fallback: [Google: "仙台市史" 通史編 近世 城下町 足軽 組屋敷](https://www.google.com/search?q=%22%E4%BB%99%E5%8F%B0%E5%B8%82%E5%8F%B2%22+%E9%80%9A%E5%8F%B2%E7%B7%A8+%E8%BF%91%E4%B8%96+%E5%9F%8E%E4%B8%8B%E7%94%BA+%E8%B6%B3%E8%BB%BD+%E7%B5%84%E5%B1%8B%E6%95%B7)
- **Rests on it:** Sendai's ashigaru at the highway ends on `government.html`, an absence note.
- Blocked by: ja.wikipedia 仙台城下町 does not exist.

### 210. 『八戸市史』通史編 近世 - Hachinohe's ashigaru quarters

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Hachinohe city](https://www.city.hachinohe.aomori.jp/kurashi_tetsuduki/shogai_gakushu_bunka_sports/hakubutsukan/shishi/index.html)**
- Fallback: [Google: "八戸市史" 通史編 近世 城下町 足軽屋敷 塩丁](https://www.google.com/search?q=%22%E5%85%AB%E6%88%B8%E5%B8%82%E5%8F%B2%22+%E9%80%9A%E5%8F%B2%E7%B7%A8+%E8%BF%91%E4%B8%96+%E5%9F%8E%E4%B8%8B%E7%94%BA+%E8%B6%B3%E8%BB%BD%E5%B1%8B%E6%95%B7+%E5%A1%A9%E4%B8%81)
- **Rests on it:** Hachinohe's ashigaru at the highway ends.
- Blocked by: ja.wikipedia 八戸城 puts one quarter on the east side.

### 211. A domain's house-building regulation (触書 / 定書) on plot enclosures by rank

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Fukui prefectural archives (the closest institution)](https://www.library-archives.pref.fukui.lg.jp/bunsho/category/tenji/32442.html)**
- Fallback: [Google: 城下町 武家屋敷 塀 規制 "生垣" "板塀" "土塀" 足軽 禁止 触書](https://www.google.com/search?q=%E5%9F%8E%E4%B8%8B%E7%94%BA+%E6%AD%A6%E5%AE%B6%E5%B1%8B%E6%95%B7+%E5%A1%80+%E8%A6%8F%E5%88%B6+%22%E7%94%9F%E5%9E%A3%22+%22%E6%9D%BF%E5%A1%80%22+%22%E5%9C%9F%E5%A1%80%22+%E8%B6%B3%E8%BB%BD+%E7%A6%81%E6%AD%A2+%E8%A7%A6%E6%9B%B8)
- **Rests on it:** the enclosure rank ladder and the walls forbidden to the lowest rank on `government.html`.
- Blocked by: kotobank offers the three enclosures as alternatives with no rank.

### 212. Reed, Talons and Teeth: County Clerks and Runners in the Qing Dynasty (2000)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Stanford University Press](https://www.sup.org/books/title/?id=1440)**
- Fallback: [Google: "Talons and Teeth" Reed "County Clerks and Runners" Qing banfang](https://www.google.com/search?q=%22Talons+and+Teeth%22+Reed+%22County+Clerks+and+Runners%22+Qing+banfang)
- **Rests on it:** the runners' banfang and where they lived on `government.html`, now this page's reading.
- Blocked by: a book.

### 213. 黄六鴻《福惠全書》 - the Qing magistrate's handbook on the 班房

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Chinese Text Project (the tried address was 404)](https://ctext.org/)**
- Fallback: [Google: 黄六鴻 福惠全書 "班房" 衙役 原文](https://www.google.com/search?q=%E9%BB%84%E5%85%AD%E9%B4%BB+%E7%A6%8F%E6%83%A0%E5%85%A8%E6%9B%B8+%22%E7%8F%AD%E6%88%BF%22+%E8%A1%99%E5%BD%B9+%E5%8E%9F%E6%96%87)
- **Rests on it:** the same runners' station.
- Blocked by: Wikisource carries no copy at the address tried.

### 214. The 关厢 dictionary entry (zdic) - the cited page returned 404

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[zdic.net](https://www.zdic.net/hans/%E5%85%B3%E5%8E%A2)**
- Fallback: [Google: "关厢" 汉语大词典 城门外 街市 解释](https://www.google.com/search?q=%22%E5%85%B3%E5%8E%A2%22+%E6%B1%89%E8%AF%AD%E5%A4%A7%E8%AF%8D%E5%85%B8+%E5%9F%8E%E9%97%A8%E5%A4%96+%E8%A1%97%E5%B8%82+%E8%A7%A3%E9%87%8A)
- **Rests on it:** the word guanxiang and its gloss on `hinterland.html`.
- Blocked by: 404 to an automated fetch at the URL the registry cites; a person should check it.

### 215. GB 50288, 灌溉与排水工程设计标准 - canal-system layout clauses

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Ministry of Water Resources](https://www.mwr.gov.cn/)**
- Fallback: [Google: "GB 50288" 灌溉与排水工程设计标准 渠系布置 pdf](https://www.google.com/search?q=%22GB+50288%22+%E7%81%8C%E6%BA%89%E4%B8%8E%E6%8E%92%E6%B0%B4%E5%B7%A5%E7%A8%8B%E8%AE%BE%E8%AE%A1%E6%A0%87%E5%87%86+%E6%B8%A0%E7%B3%BB%E5%B8%83%E7%BD%AE+pdf)
- **Rests on it:** the handedness of an irrigation fan on `hinterland.html`, an absence note.
- Blocked by: no stable file address found.

### 216. J-STAGE papers on irrigation-system layout morphology (用水系統の配置形態)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE, JSIDRE](https://www.jstage.jst.go.jp/browse/jsidre)**
- Fallback: [Google: site:jstage.jst.go.jp 用水系統 配置 形態 水田 論文](https://www.google.com/search?q=site%3Ajstage.jst.go.jp+%E7%94%A8%E6%B0%B4%E7%B3%BB%E7%B5%B1+%E9%85%8D%E7%BD%AE+%E5%BD%A2%E6%85%8B+%E6%B0%B4%E7%94%B0+%E8%AB%96%E6%96%87)
- **Rests on it:** the same fan handedness.
- Blocked by: no article address without a search.

### 217. Ganzhou's Fushou drains (福寿沟) - the municipal account of its outfalls and storage ponds

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Ganzhou city](http://www.ganzhou.gov.cn/)**
- Fallback: [Google: 福寿沟 赣州 池塘 蓄水 排入 章江 政府](https://www.google.com/search?q=%E7%A6%8F%E5%AF%BF%E6%B2%9F+%E8%B5%A3%E5%B7%9E+%E6%B1%A0%E5%A1%98+%E8%93%84%E6%B0%B4+%E6%8E%92%E5%85%A5+%E7%AB%A0%E6%B1%9F+%E6%94%BF%E5%BA%9C)
- **Rests on it:** the moat as storm drain and reservoir on `hinterland.html`, an absence note.
- Blocked by: zh.wikipedia 福寿沟 does not say where the outfalls discharge.

### 218. Esherick and Rankin (eds.), Chinese Local Elites and Patterns of Dominance - the inner chapters

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[UC Press E-Books Collection](https://publishing.cdlib.org/ucpressebooks/view?docId=ft0z09p04n)**
- Fallback: [Google: "Chinese Local Elites and Patterns of Dominance" Esherick Rankin escholarship full text](https://www.google.com/search?q=%22Chinese+Local+Elites+and+Patterns+of+Dominance%22+Esherick+Rankin+escholarship+full+text)
- **Rests on it:** the fragmented elite holdings on `hinterland.html`, on no page read.
- Blocked by: only the public introduction was reachable.

### 219. Twitchett on the Tang-Song great estate (庄园)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[JSTOR](https://www.jstor.org/stable/1178947)**
- Fallback: [Google: Twitchett T'ang estate "chuang" manor Tang Song transition landholding pdf](https://www.google.com/search?q=Twitchett+T%27ang+estate+%22chuang%22+manor+Tang+Song+transition+landholding+pdf)
- **Rests on it:** the single live-on manor as an earlier form on `hinterland.html`.
- Blocked by: paywalled.

### 220. A prefectural 中世城館跡調査報告書 - the medieval moated residences' form and spacing

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nara National Research Institute report archive](https://sitereports.nabunken.go.jp/)**
- Fallback: [Google: site:sitereports.nabunken.go.jp 中世城館跡 調査報告書 土塁 堀](https://www.google.com/search?q=site%3Asitereports.nabunken.go.jp+%E4%B8%AD%E4%B8%96%E5%9F%8E%E9%A4%A8%E8%B7%A1+%E8%AA%BF%E6%9F%BB%E5%A0%B1%E5%91%8A%E6%9B%B8+%E5%9C%9F%E5%A1%81+%E5%A0%80)
- **Rests on it:** the 2-15 mile band and the isolation of rural estates on `hinterland.html`.
- Blocked by: the encyclopedia pages give the form and no distances.

### 221. Beattie, Land and Lineage in China: T'ung-ch'eng County (1979)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Cambridge Core](https://www.cambridge.org/core/books/land-and-lineage-in-china/)**
- Fallback: [Google: Beattie "Land and Lineage in China" T'ung-ch'eng county Anhwei Ming Ch'ing](https://www.google.com/search?q=Beattie+%22Land+and+Lineage+in+China%22+T%27ung-ch%27eng+county+Anhwei+Ming+Ch%27ing)
- **Rests on it:** where gentry lineages held land relative to the county seat on `hinterland.html`.
- Blocked by: a book.

### 222. The walled Chinese lineage compound (圍村 / 土樓 / 碉樓) against banditry

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[zh.wikipedia 围村](https://zh.wikipedia.org/wiki/%E5%9B%B4%E6%9D%91)**
- Fallback: [Google: 围村 碉樓 防盜匪 宗族 墻 城 研究](https://www.google.com/search?q=%E5%9B%B4%E6%9D%91+%E7%A2%89%E6%A8%93+%E9%98%B2%E7%9B%9C%E5%8C%AA+%E5%AE%97%E6%97%8F+%E5%A2%BB+%E5%9F%8E+%E7%A0%94%E7%A9%B6)
- **Rests on it:** the walled lineage compound on `hinterland.html`, on no page read.
- Blocked by: not fetched this pass.

### 223. MAFF land-improvement design standard for farm roads (設計「農道」)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MAFF design standards index](https://www.maff.go.jp/j/nousin/sekkei/kijun/)**
- Fallback: [Google: 土地改良事業計画設計基準 設計 農道 基準書 技術書 農林水産省 PDF](https://www.google.com/search?q=%E5%9C%9F%E5%9C%B0%E6%94%B9%E8%89%AF%E4%BA%8B%E6%A5%AD%E8%A8%88%E7%94%BB%E8%A8%AD%E8%A8%88%E5%9F%BA%E6%BA%96+%E8%A8%AD%E8%A8%88+%E8%BE%B2%E9%81%93+%E5%9F%BA%E6%BA%96%E6%9B%B8+%E6%8A%80%E8%A1%93%E6%9B%B8+%E8%BE%B2%E6%9E%97%E6%B0%B4%E7%94%A3%E7%9C%81+PDF)
- **Rests on it:** a lane's width and where a path may run on `ways.html`, labeled the map's convention.
- Blocked by: the index carries no figures; the standard is a PDF no address reached.

### 224. A J-STAGE study of the bund (畦畔) as a working passage

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE, JSIDRE](https://www.jstage.jst.go.jp/browse/jsidre)**
- Fallback: [Google: 畦畔 農作業 通路 幅 論文 農村計画学会誌 J-STAGE](https://www.google.com/search?q=%E7%95%A6%E7%95%94+%E8%BE%B2%E4%BD%9C%E6%A5%AD+%E9%80%9A%E8%B7%AF+%E5%B9%85+%E8%AB%96%E6%96%87+%E8%BE%B2%E6%9D%91%E8%A8%88%E7%94%BB%E5%AD%A6%E4%BC%9A%E8%AA%8C+J-STAGE)
- **Rests on it:** the path on the baulk and the hem edge on `ways.html`.
- Blocked by: no article address without a search.

### 225. Liu, Huang and Xu 2026, the building of mid-Northern-Song military cities from the Wujing zongyao (基于《武经总要》的北宋中期军事城池营建研究)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Journal of Architectural History PDF](https://www.jgcm.ac.cn/jah/cn/article/pdf/preview/10.12329/20969368.2026.02011.pdf)**
- Fallback: [Google: 基于《武经总要》的北宋中期军事城池营建研究 建筑史学刊 2026](https://www.google.com/search?q=%E5%9F%BA%E4%BA%8E%E3%80%8A%E6%AD%A6%E7%BB%8F%E6%80%BB%E8%A6%81%E3%80%8B%E7%9A%84%E5%8C%97%E5%AE%8B%E4%B8%AD%E6%9C%9F%E5%86%9B%E4%BA%8B%E5%9F%8E%E6%B1%A0%E8%90%A5%E5%BB%BA%E7%A0%94%E7%A9%B6+%E5%BB%BA%E7%AD%91%E5%8F%B2%E5%AD%A6%E5%88%8A+2026)
- **Rests on it:** the mamian spacing and the arc-shaped corner tower on `cities/defenses.html`.
- Blocked by: the journal serves the PDF as compressed streams with no text layer the checker's fetcher can read, so the three passages quoted from it could not be verified by tool.

### 226. Tabayashi 1987, Irrigation Systems in Japan, Geographical Review of Japan Series B 60(1)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/grj1984b/60/1/60_1_41/_pdf)**
- Fallback: [Google: Tabayashi "Irrigation Systems in Japan" "Geographical Review of Japan" 1987](https://www.google.com/search?q=Tabayashi+%22Irrigation+Systems+in+Japan%22+%22Geographical+Review+of+Japan%22+1987)
- **Rests on it:** reservoir siting, canal taper and the separation of supply from drain on `water.html` and `fields.html`.
- Blocked by: J-STAGE serves the article as a PDF the checker's fetcher receives as binary, so its quoted passages could not be verified by tool.

### 227. Obata 1977, the traditional rice-transplanting methods of Wakayama prefecture (和歌山県における慣行田植法の地域性とその成立要因に関する研究)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/jsfwr1966/1977/29/1977_29_24/_pdf/-char/en)**
- Fallback: [Google: 和歌山県における慣行田植法の地域性とその成立要因に関する研究 農作業研究 1977](https://www.google.com/search?q=%E5%92%8C%E6%AD%8C%E5%B1%B1%E7%9C%8C%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E6%85%A3%E8%A1%8C%E7%94%B0%E6%A4%8D%E6%B3%95%E3%81%AE%E5%9C%B0%E5%9F%9F%E6%80%A7%E3%81%A8%E3%81%9D%E3%81%AE%E6%88%90%E7%AB%8B%E8%A6%81%E5%9B%A0%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E7%A0%94%E7%A9%B6+%E8%BE%B2%E4%BD%9C%E6%A5%AD%E7%A0%94%E7%A9%B6+1977)
- **Rests on it:** the village transplanting schedule and its window on `fields.html`.
- Blocked by: a scan whose OCR text layer garbles characters; the passages were read from the page image, which the checker's fetcher cannot do.

### 228. Feng Xianliang, graves and charity graveyards in Ming-Qing Jiangnan (坟茔义冢：明清江南的民众生活与环境保护)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[sinoss.net PDF](https://www.sinoss.net/uploadfile/2010/1130/6012.pdf)**
- Fallback: [Google: 冯贤亮 坟茔义冢 明清江南的民众生活与环境保护](https://www.google.com/search?q=%E5%86%AF%E8%B4%A4%E4%BA%AE+%E5%9D%9F%E8%8C%94%E4%B9%89%E5%86%A2+%E6%98%8E%E6%B8%85%E6%B1%9F%E5%8D%97%E7%9A%84%E6%B0%91%E4%BC%97%E7%94%9F%E6%B4%BB%E4%B8%8E%E7%8E%AF%E5%A2%83%E4%BF%9D%E6%8A%A4)
- **Rests on it:** the packing of a charity graveyard and the size band of charity grounds on `religion-and-death.html`.
- Blocked by: the checker's fetcher receives the PDF as binary, so its quoted passages could not be verified by tool.

### 229. Lin Rongze 2001, the temple fair and Chinese folk society (「廟會」與中國的民間社會), Shiyun 7

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NTNU history department PDF](https://www.his.ntnu.edu.tw/publish03/downloadfile.php?periodicalsPage=2&issue_id=39&paper_id=249)**
- Fallback: [Google: 林榮澤 廟會 與中國的民間社會 清代 華北 東北 西北 史耘](https://www.google.com/search?q=%E6%9E%97%E6%A6%AE%E6%BE%A4+%E5%BB%9F%E6%9C%83+%E8%88%87%E4%B8%AD%E5%9C%8B%E7%9A%84%E6%B0%91%E9%96%93%E7%A4%BE%E6%9C%83+%E6%B8%85%E4%BB%A3+%E8%8F%AF%E5%8C%97+%E6%9D%B1%E5%8C%97+%E8%A5%BF%E5%8C%97+%E5%8F%B2%E8%80%98)
- **Rests on it:** the periodic market on a temple's own ground and the diviners at a temple fair on `religion-and-death.html`.
- Blocked by: a scan whose OCR text layer garbles characters; the passages were read from the page image, which the checker's fetcher cannot do.

### 230. Chi, Plieninger, Lin and Chowdhury 2024, Governing Landscape Simplification in Rapid Commercialization Contexts, International Journal of the Commons 18(1)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[International Journal of the Commons PDF](https://thecommonsjournal.org/articles/1300/files/66151cd3a6d55.pdf)**
- Fallback: [Google: Chi Plieninger "Governing Landscape Simplification in Rapid Commercialization Contexts" dike-pond Pearl River Delta](https://www.google.com/search?q=Chi+Plieninger+%22Governing+Landscape+Simplification+in+Rapid+Commercialization+Contexts%22+dike-pond+Pearl+River+Delta)
- **Rests on it:** the dike eroding from about 20 m to under 4 m and the mechanism behind it on `archetypes.html`.
- Blocked by: the checker's fetcher receives the PDF as binary, so its quoted passages could not be verified by tool.

### 231. Coggins and Minor 2018, Fengshui Forests as A Socio-Natural Reservoir, Asia Pacific Perspectives 15(2)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[USF Asia Pacific Perspectives PDF](https://jayna.usfca.edu/asia-pacific-perspectives/pdfs/1-coggins-minor-fengshui-forests.pdf)**
- Fallback: [Google: Coggins Minor "Fengshui Forests as A Socio-Natural Reservoir" "Asia Pacific Perspectives" 2018](https://www.google.com/search?q=Coggins+Minor+%22Fengshui+Forests+as+A+Socio-Natural+Reservoir%22+%22Asia+Pacific+Perspectives%22+2018)
- **Rests on it:** the village grove as a system of separate patches on `vegetation.html`.
- Blocked by: the fetcher cannot decode the PDF's text stream, so its quoted passages could not be verified by tool.

### 232. University of Missouri Center for Agroforestry, Training Manual for Applied Agroforestry Practices (2024), chapter 6 Windbreaks

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Center for Agroforestry PDF](https://centerforagroforestry.org/wp-content/uploads/2024/04/06_Windbreaks_TrainingManual_2024Master_0410_Digital-7.pdf)**
- Fallback: [Google: "Training Manual for Applied Agroforestry Practices" 2024 Windbreaks "Center for Agroforestry" Missouri pdf](https://www.google.com/search?q=%22Training+Manual+for+Applied+Agroforestry+Practices%22+2024+Windbreaks+%22Center+for+Agroforestry%22+Missouri+pdf)
- **Rests on it:** what a gap in a shelter belt does to the wind and the remedy for an access crossing on `vegetation.html`.
- Blocked by: the checker's fetcher receives the PDF as binary, so its quoted passages could not be verified by tool.

- **L5R fan wiki, "Seidō" and "Shinden (TCG)"** (feature 254, the country shrine, 2026-09-19): the fan wiki's summaries of *Emerald Empire* (FFG 5th edition, pp. 143 and 176-178) on village shrines, shrine keepers and priests, and the resident monk at most temples. The site refuses every automated fetch (402/403), so the record cites it only as an absence note; a browser opens it. Direct links: https://l5r.fandom.com/wiki/Seid%C5%8D and https://l5r.fandom.com/wiki/Shinden_(TCG). Backup search: `"There was no village without some manner of shrine" l5r fandom Seidō`.

### 233. Sugiura Naoshi 1973, the outbuildings of the farmstead by main-house type (tga1948 25(3), pp. 145-), Tables 5 and 6, pp. 150-151

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/tga1948/25/3/25_3_145/_pdf/-char/ja)**
- Fallback: [Google: 杉浦直 1973 付属建物 主屋類型 地理学評論 25 3 145](https://www.google.com/search?q=%E6%9D%89%E6%B5%A6%E7%9B%B4+1973+%E4%BB%98%E5%B1%9E%E5%BB%BA%E7%89%A9+%E4%B8%BB%E5%B1%8B%E9%A1%9E%E5%9E%8B+jstage+tga1948+25+3+145)
- **Rests on it:** the privy (0.87), firewood shed (0.76), compost shed (0.24), bath shed (0.29) and shrine (0.01) figures in "The farmstead's fixtures" on `homesteads.html`; the footnotes quote the session's transcription of the table rather than the table, and one says the shrine column is hard to align on the scan. Read the pre-1944 row and the all-houses row of Table 5 by eye, column by column.
- Blocked by: a scanned PDF with no text layer; this container cannot render its pages.

### 234. Tokushima prefectural library bulletin 50, pp. 131-133, the homestead god (屋敷神)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Tokushima library PDF](https://library.bunmori.tokushima.jp/digital/webkiyou/50/131-133.pdf)**
- Fallback: [Google: 徳島県立図書館 紀要 50 屋敷神 西南隅 131-133](https://www.google.com/search?q=%E5%BE%B3%E5%B3%B6%E7%9C%8C%E7%AB%8B%E5%9B%B3%E6%9B%B8%E9%A4%A8+%E7%B4%80%E8%A6%81+50+%E5%B1%8B%E6%95%B7%E7%A5%9E+%E8%A5%BF%E5%8D%97%E9%9A%85)
- **Rests on it:** the every-house or old-families-only pattern the GM's shrine ruling turns on, the southwest corner and the 40 cm stone shrine in "The farmstead's fixtures" on `homesteads.html`; the first of those passages has no footnote until its page can be read.
- Blocked by: the PDF fetches but no text can be extracted here, so the quotes could not be checked by tool.

### 235. Sendai city, igune planting species list (居久根樹木リスト)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[city.sendai.jp PDF](https://www.city.sendai.jp/ryokuchihozen/kurashi/shizen/midori/hyakunen/documents/igunejyumokurist.pdf)**
- Fallback: [Google: 仙台市 居久根 樹木リスト igunejyumokurist](https://www.google.com/search?q=%E4%BB%99%E5%8F%B0%E5%B8%82+%E5%B1%85%E4%B9%85%E6%A0%B9+%E6%A8%B9%E6%9C%A8%E3%83%AA%E3%82%B9%E3%83%88+igunejyumokurist)
- **Rests on it:** the tall-tree class of 15 m and over for sugi, keyaki, kuromatsu and hinoki in "The garden's sun, and how far the windbreak shades" on `homesteads.html`. Check that the four species sit under the tall-tree heading.
- Blocked by: the PDF serves, but this container cannot extract its text.

### 236. Kurita et al. 2019, measuring igune height (JSIDRE journal 87(10), p. 825)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/jjsidre/87/10/87_825/_pdf/-char/ja)**
- Fallback: [Google: 居久根 高さ レーザー距離計 農業農村工学会誌 87 10 825](https://www.google.com/search?q=%E5%B1%85%E4%B9%85%E6%A0%B9+%E9%AB%98%E3%81%95+%E3%83%AC%E3%83%BC%E3%82%B6%E3%83%BC%E8%B7%9D%E9%9B%A2%E8%A8%88+%E8%BE%B2%E6%A5%AD%E8%BE%B2%E6%9D%91%E5%B7%A5%E5%AD%A6%E4%BC%9A%E8%AA%8C+87+10+825)
- **Rests on it:** the six ground measurements of igune height (22.0, 19.2, 11.0, 13.8, 13.8 and 15.8 m) now held in a comment in "The garden's sun, and how far the windbreak shades" on `homesteads.html`, and whether the 9-16 m band is this paper's or the next one's.
- Blocked by: the PDF serves, but this container cannot extract its text.

### 237. Minami et al. 2024, igune and wind (Wind Engineering Research 28, J14)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/windengresearch/28/0/28_J14/_pdf/-char/ja)**
- Fallback: [Google: 居久根 風 風工学シンポジウム 28 J14 9 m-16 m](https://www.google.com/search?q=%E5%B1%85%E4%B9%85%E6%A0%B9+%E9%A2%A8%E5%B7%A5%E5%AD%A6+jstage+windengresearch+28+J14)
- **Rests on it:** the 9-16 m height of a grove of tall and low trees in "The garden's sun, and how far the windbreak shades" on `homesteads.html`.
- Blocked by: the PDF serves, but this container cannot extract its text.

### 238. Minami, Yonezawa and Okaze 2022, an igune in Osaki (J-STAGE jass 38(2), p. 37), full text

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE full-text PDF](https://www.jstage.jst.go.jp/article/jass/38/2/38_37/_pdf)**
- Fallback: [Google: "10 m high Igune on the prevailing wind direction side"](https://www.google.com/search?q=%2210+m+high+Igune+on+the+prevailing+wind+direction+side%22)
- **Rests on it:** the igune placed on the west and north of the site against the west-northwest winter wind, quoted from the full text, in "The garden's sun, and how far the windbreak shades" on `homesteads.html`; the footnote links the abstract page, where that passage is not.
- Blocked by: the PDF serves, but this container cannot extract its text.

### 239. Welch 1967, The Practice of Chinese Buddhism, 1900-1950 (Harvard University Press)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Harvard University Press search](https://www.hup.harvard.edu/search?q=The+Practice+of+Chinese+Buddhism)**
- Fallback: [Google: Welch "The Practice of Chinese Buddhism" hereditary temples public monasteries](https://www.google.com/search?q=Welch+%22The+Practice+of+Chinese+Buddhism%22+hereditary+temples+public+monasteries)
- **Rests on it:** "small hereditary Chinese temples held a handful of monks" in "City temple size - the setting's deliberate liberty" on `religion-and-death.html`, now an absence note. Look for Welch's figures on how many monks a small hereditary temple held against a public monastery.
- Blocked by: a book, not on any public page; a Welch-based paper on academia.edu ("Questioning the Revival") refused the fetch with a 403.

### 240. Yamamoto, Hirao and Miyauchi 2016, homestead composition (屋敷構え) in Asuka village (AIJ Journal of Architecture and Planning 81(721), p. 675)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE article page](https://www.jstage.jst.go.jp/article/aija/81/721/81_675/_article/-char/ja/)**
- Fallback: [Google: 明日香村 屋敷構え 日本建築学会計画系論文集 81 721 675](https://www.google.com/search?q=%E6%98%8E%E6%97%A5%E9%A6%99%E6%9D%91+%E5%B1%8B%E6%95%B7%E6%A7%8B%E3%81%88+%E6%97%A5%E6%9C%AC%E5%BB%BA%E7%AF%89%E5%AD%A6%E4%BC%9A%E8%A8%88%E7%94%BB%E7%B3%BB%E8%AB%96%E6%96%87%E9%9B%86+81+721)
- **Rests on it:** "Does a farmstead stand whole on one bank of the brook?" on `homesteads.html`, a guess with an absence note. Look for a lot plan where a channel runs through or beside the 屋敷地, and whether the garden, privy or storehouse ever stands across it from the main house.
- Blocked by: the full text is not open; the abstract page does not address the channel.

### 241. Imhof 1975, "Positioning Names on Maps" (The American Cartographer 2(2), pp. 128-144) - the classic rules for placing map names

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Taylor & Francis article page](https://www.tandfonline.com/doi/abs/10.1559/152304075784313304)**
- Fallback: [Google: Imhof "Positioning Names on Maps" American Cartographer 1975 pdf](https://www.google.com/search?q=Imhof+%22Positioning+Names+on+Maps%22+American+Cartographer+1975+pdf)
- **Rests on it:** nothing yet stands on it, but "Where does a caption sit" on `presentation.html` (diagram repo, feature 266) takes the point-label rules - legibility and clear association, close beside the symbol, the corner positions first - from a Penn State course, QGIS and a 1995 paper that all cite Imhof. With the text, the record could quote Imhof's own rules, especially on how far a name should stand from its symbol and when a name may cross a line.
- Blocked by: Taylor & Francis refused the fetch (403); Semantic Scholar and SciSpace render nothing without JavaScript.

### 242. Yoeli 1972, "The logic of automated map lettering" (The Cartographic Journal 9(2), pp. 99-108) - the ranked label positions around a point

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Taylor & Francis search](https://www.tandfonline.com/action/doSearch?AllField=The+logic+of+automated+map+lettering)**
- Fallback: [Google: Yoeli 1972 "The logic of automated map lettering" Cartographic Journal](https://www.google.com/search?q=Yoeli+1972+%22The+logic+of+automated+map+lettering%22+Cartographic+Journal)
- **Rests on it:** the ranked order of positions around a point in "Where does a caption sit" on `presentation.html` (diagram repo, feature 266), now quoted from QGIS and from Christensen, Marks and Shieber 1995, who attribute the objective to Yoeli. Look for his ranking of the positions and whether it matches QGIS's order (upper right first).
- Blocked by: only a bibliographic record could be found; no public full text.

### 243. Krygier and Wood 2011, Making Maps: A Visual Guide to Map Design for GIS (2nd ed., Guilford Press) - the chapter on type and labels

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Guilford Press book page](https://www.guilford.com/books/Making-Maps/Krygier-Wood/9781609181666)**
- Fallback: [Google: Krygier Wood "Making Maps" label placement priorities point symbols](https://www.google.com/search?q=Krygier+Wood+%22Making+Maps%22+label+placement+priorities+point+symbols)
- **Rests on it:** the order of the eight positions in "Where does a caption sit" on `presentation.html` (diagram repo, feature 266), which QGIS attributes to this book. Look for the numbered 1-8 point-label priorities and any guidance on the gap between a symbol and its label.
- Blocked by: a book, not on any public page; Krygier's own lecture page shows the priorities as a figure whose numbers did not come through as text.

### 244. Tanigawa Akio 1992, "Excavating Edo's Cemeteries: Graves as Indicators of Status and Class" (Japanese Journal of Religious Studies 19/2-3)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nanzan Institute PDF](https://nirc.nanzan-u.ac.jp/journal/6/article/832/pdf/download)**
- Fallback: [Google: Tanigawa "Excavating Edo's Cemeteries: Graves as Indicators of Status and Class" Japanese Journal of Religious Studies](https://www.google.com/search?q=Tanigawa+%22Excavating+Edo%27s+Cemeteries%3A+Graves+as+Indicators+of+Status+and+Class%22+Japanese+Journal+of+Religious+Studies)
- **Rests on it:** the excavated sizes of Edo commoner graves (a major axis of 65 cm to 2.4 m by category), which the burial-ground sizes are built up from, in "How much ground does a village burial ground need" and "How much ground does a grave take" on `religion-and-death.html`.
- Blocked by: the PDF serves, but the checker's fetcher receives it as binary, so its quoted passages could not be verified by tool (diagram feature 250, T45).

### 245. Sen-dou Chang, "The Morphology of Walled Capitals" - the scanned chapter with Figure 5, the model street plans (Stanford course copy)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Stanford-hosted scan (sen.pdf)](http://web.stanford.edu/~mel1000/sen.pdf)**
- Fallback: [Google: Sen-dou Chang "Morphology of Walled Capitals" "Latin cross formed by two streets connecting the four gates"](https://www.google.com/search?q=Sen-dou+Chang+%22Morphology+of+Walled+Capitals%22+%22Latin+cross+formed+by+two+streets+connecting+the+four+gates%22)
- **Rests on it:** the cross and T street nets of the model plans (Figure 5, models a and b), the drum tower at the central crossing, the deflected trunk road and the intramural fields and water, in "A county seat's street share" and "Where does the Imperial road run through a city" on `cities/fabric.html`. The same chapter as No. 18, which is the print volume; this is the scan those two questions quote.
- Blocked by: a scan with no text layer; the passages were transcribed from the page images, which no tool in the container can read to verify them (diagram feature 250).

### 246. 陈凌 (Chen Ling), "建筑空间与礼制文化：宋代地方衙署建筑象征性功能诠释", 西南大学学报（社会科学版） 42(5), 2016 - the Song local yamen's central axis

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Journal of Southwest University PDF preview](https://xbgjxt.swu.edu.cn/data/article/preview-pdf?doi=10.13718/j.cnki.xdsk.2016.05.023)**
- Fallback: [Google: "宋代地方衙署建筑象征性功能诠释" 陈凌](https://www.google.com/search?q=%22%E5%AE%8B%E4%BB%A3%E5%9C%B0%E6%96%B9%E8%A1%99%E7%BD%B2%E5%BB%BA%E7%AD%91%E8%B1%A1%E5%BE%81%E6%80%A7%E5%8A%9F%E8%83%BD%E8%AF%A0%E9%87%8A%22+%E9%99%88%E5%87%8C)
- **Rests on it:** the axial, symmetrical yamen inside the walls, in "Wall geometry: rectangles and terrain loops" on `cities/capitals.html` (the Huozhou passage in the Beijing Daily now carries the axis as well).
- Blocked by: read on 2026-09-14, but the journal's host returned HTTP 502 and then timed out on 2026-09-27, to the session and to the checker, so the quoted passage cannot be re-verified (diagram feature 250).

### 247. Baidu Baike, 村庙 (village temple) - the sizes of Fujian's village temples

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike entry](https://baike.baidu.com/item/%E6%9D%91%E5%BA%99/3494869)**
- Fallback: [Google: 村庙 百度百科 闽南村庙多在100平方米左右](https://www.google.com/search?q=%E6%9D%91%E5%BA%99+%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91+%E9%97%BD%E5%8D%97%E6%9D%91%E5%BA%99%E5%A4%9A%E5%9C%A8100%E5%B9%B3%E6%96%B9%E7%B1%B3%E5%B7%A6%E5%8F%B3)
- **Rests on it:** the Fujian village-temple sizes (about 100 m² in the south, over 400 m² in the north-east) in "How large was a village shrine's precinct, and how much of it was built on?" on `religion-and-death.html` (diagram repo, feature 268), which now stand on an absence note. A saved copy of the page would let the record quote the sentence.
- Blocked by: Baidu Baike refused the fetch (HTTP 403); the figures were seen only in a search summary.

### 248. 福建省经济社会状况与村庙信仰 (Fujian's economic and social conditions and village-temple religion), on pishu.com.cn

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Pishu (SSAP) literature page](http://www.pishu.com.cn/skwx_ps/ps/literature?SiteID=14&ID=7591913)**
- Fallback: [Google: "福建省经济社会状况与村庙信仰"](https://www.google.com/search?q=%22%E7%A6%8F%E5%BB%BA%E7%9C%81%E7%BB%8F%E6%B5%8E%E7%A4%BE%E4%BC%9A%E7%8A%B6%E5%86%B5%E4%B8%8E%E6%9D%91%E5%BA%99%E4%BF%A1%E4%BB%B0%22)
- **Rests on it:** the same Fujian village-temple sizes as No. 247, likely the Baidu entry's own source, in the same question on `religion-and-death.html` (diagram repo, feature 268).
- Blocked by: the page failed to fetch from the container.

### 249. Nagaokakyo City Library, 展示コーナーだより 第13号 ("Exhibition Corner News No. 13"), 江戸時代の年貢上納 ("Paying the land tax in the Edo period"), 2003 - a two-page scanned leaflet

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Nagaokakyo city PDF](https://www.city.nagaokakyo.lg.jp/cmsfiles/contents/0000005/5235/hurusatofile13.pdf)**
- Fallback: [Google: 長岡京市 展示コーナーだより 第13号 江戸時代の年貢上納](https://www.google.com/search?q=%E9%95%B7%E5%B2%A1%E4%BA%AC%E5%B8%82+%E5%B1%95%E7%A4%BA%E3%82%B3%E3%83%BC%E3%83%8A%E3%83%BC%E3%81%A0%E3%82%88%E3%82%8A+%E7%AC%AC13%E5%8F%B7+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3%E3%81%AE%E5%B9%B4%E8%B2%A2%E4%B8%8A%E7%B4%8D)
- **Rests on it:** the soybean share of the land tax (a tenth soybeans, three tenths silver, six tenths rice in the shogunal lands paying the Kyoto intendant), in "The granary holds grain, not just rice" on `buildings.html`. Check the quoted passage against the page image character for character.
- Blocked by: the PDF is public, but a scan with no text layer; neither the verbatim script nor the checking agent could confirm the quotation (diagram feature 265, T02).

### 250. Beijing Court Network (北京法院网), 何谓"衙门八字开" ("What is meant by 'the yamen's gate opens like the character eight'"), 2008 - the splayed walls at a county office's gate as its notice wall

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Beijing court article](https://bjgy.bjcourt.gov.cn/article/detail/2008/05/id/861939.shtml)**
- Fallback: [Google: 何谓"衙门八字开" 北京法院网](https://www.google.com/search?q=%E4%BD%95%E8%B0%93%E2%80%9C%E8%A1%99%E9%97%A8%E5%85%AB%E5%AD%97%E5%BC%80%E2%80%9D+%E5%8C%97%E4%BA%AC%E6%B3%95%E9%99%A2%E7%BD%91)
- **Rests on it:** whether a Chinese county office posted its own notices on the splayed walls (八字墙) beside its gate - the counterpart of the magistracy's own notice board, apart from the town's - in "Did the magistrate post notices at the office's own gate, or on the town's notice board?" on `buildings.html` (diagram repo, feature 267, R25), which now stands on an absence note. A saved copy that says what was posted on the walls would let the record quote it. The Beijing civilization office's page on the "八字衙门" (https://www.bjwmb.gov.cn/zxfw/wmwx/wskt/t20180410_863222.htm) says the same in search summaries and would serve as well.
- Blocked by: the page refused the fetch (HTTP 403); the other two candidate pages did not answer from the container, and Baidu Baike returned nothing.

### 251. Yannopoulos and others 2015, "Evolution of Water Lifting Devices (Pumps) over the Centuries Worldwide", Water 7(9), 5031-5060

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[MDPI article PDF](https://res.mdpi.com/d_attachment/water/water-07-05031/article_deploy/water-07-05031.pdf)**
- Fallback: [Google: Yannopoulos "Evolution of Water Lifting Devices (Pumps) over the Centuries Worldwide" Water 2015](https://www.google.com/search?q=Yannopoulos+%22Evolution+of+Water+Lifting+Devices+%28Pumps%29+over+the+Centuries+Worldwide%22+Water+2015)
- **Rests on it:** the shaduf's beam, hinge, upright post and counterweight, and how far a field well's water was carried, in "Wells in crop fields" on `urban-features.html`. Look for the paper's own sentence on the counterweight (probably its general shaduf section).
- Blocked by: open access, but www.mdpi.com refuses automated fetches (403) and the PDF mirror came back with no text the checker could read (diagram feature 265, T11).

### 252. Endo 2013, "The Kabu-ido System: Innovations in an Indigenous Groundwater Management Institution", Digital Library of the Commons (ENDO_0894.pdf)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Indiana University DLC PDF](https://dlc.dlib.indiana.edu/dlc/bitstream/handle/10535/8876/ENDO_0894.pdf)**
- Fallback: [Google: Endo "The Kabu-ido System" Innovations Indigenous Groundwater Management Institution](https://www.google.com/search?q=Endo+%22The+Kabu-ido+System%22+Innovations+Indigenous+Groundwater+Management+Institution)
- **Rests on it:** the kabu-ido well permit, the patrolmen the lower villages provided, and which way the capped artesian wells' drainage ran (upper villages onto lower paddy), in "Wells in crop fields" on `urban-features.html`. Look for the passage that says the water drained onto the lower villages' paddy.
- Blocked by: the PDF is image-based, with no text layer the checker could read (diagram feature 265, T11).

### 253. Miura Osamu (三浦 修) 2019, 「用語「屋敷林」の造語過程と地理学への普及」 ("The coining of the term yashikirin and its spread into geography"), 季刊地理学 (Quarterly Journal of Geography) 71(3), 120-127

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/tga/71/3/71_120/_pdf)**
- Fallback: [Google: 三浦修 用語「屋敷林」の造語過程と地理学への普及 季刊地理学](https://www.google.com/search?q=%E4%B8%89%E6%B5%A6%E4%BF%AE+%E7%94%A8%E8%AA%9E%E3%80%8C%E5%B1%8B%E6%95%B7%E6%9E%97%E3%80%8D%E3%81%AE%E9%80%A0%E8%AA%9E%E9%81%8E%E7%A8%8B%E3%81%A8%E5%9C%B0%E7%90%86%E5%AD%A6%E3%81%B8%E3%81%AE%E6%99%AE%E5%8F%8A+%E5%AD%A3%E5%88%8A%E5%9C%B0%E7%90%86%E5%AD%A6)
- **Rests on it:** the 1684 Mito-domain register's homestead woods (their sizes) and the 1910 description of the Musashino order of groves, fields and outer konara woodland, in "How big was the village's dooryard copse?" and "Where did a village keep its fuel wood?" on `vegetation.html` (diagram repo, feature 269). A saved copy would let the quotations be checked character for character.
- Blocked by: open access, but the PDF came back with no text layer the checker could read (diagram feature 269, V1 check).

### 254. Narumi Kunitada (鳴海 邦匡) 2002, 「近世山論絵図の定義と分類試論 - 北摂山地南麓地域を事例として -」 ("A proposed definition and classification of early modern mountain-dispute maps"), 歴史地理学 (Historical Geography) 44(3), no. 209, 1-21

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[hist-geo.jp PDF](http://hist-geo.jp/img/archive/209_001.pdf)**
- Fallback: [Google: 鳴海邦匡 近世山論絵図の定義と分類試論 北摂山地南麓](https://www.google.com/search?q=%E9%B3%B4%E6%B5%B7%E9%82%A6%E5%8C%A1+%E8%BF%91%E4%B8%96%E5%B1%B1%E8%AB%96%E7%B5%B5%E5%9B%B3%E3%81%AE%E5%AE%9A%E7%BE%A9%E3%81%A8%E5%88%86%E9%A1%9E%E8%A9%A6%E8%AB%96+%E5%8C%97%E6%91%82%E5%B1%B1%E5%9C%B0%E5%8D%97%E9%BA%93)
- **Rests on it:** the 1612 ruling map's boundary rocks and line, and the seals set at the line's ends and bends, in "How is a coppice lot bounded?" on `vegetation.html` (diagram repo, feature 269). A saved copy would let the two quoted originals be checked character for character.
- Blocked by: hist-geo.jp refused the checker's connection (ECONNREFUSED on https; diagram feature 269, V1 check).

### 255. Jiangsu Provincial Water Conservancy Survey and Design Association 2021, T/JSSLKX 002-2021, 小型農田水利工程規劃設計導則 ("Guideline for the planning and design of small farmland water-conservancy works"), draft for comment

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[jsszy.org.cn PDF](http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf)**
- Fallback: [Google: "T/JSSLKX 002-2021" 小型農田水利工程規劃設計導則](https://www.google.com/search?q=%22T%2FJSSLKX+002-2021%22+%E5%B0%8F%E5%9E%8B%E5%86%9C%E7%94%B0%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%E8%A7%84%E5%88%92%E8%AE%BE%E8%AE%A1%E5%AF%BC%E5%88%99)
- **Rests on it:** the ~1 m minimum bank top of a lateral or farm canal (section 9.3.7), and the guideline's own statement (section 9.1.6) that its canal designs follow GB 50288, the national irrigation and drainage standard, in "What drawing at TRUE SIZE left open" on `water.html` (diagram repo, feature 269). A saved copy would let 9.3.7 be checked character for character and 9.1.6 be quoted.
- Blocked by: read in full on 2026-09-12, but jsszy.org.cn refused the checker's https connection (ECONNREFUSED) and timed out on http on 2026-09-27 (diagram feature 269, W1 check).

### 256. Kimura Saburo (木村 三郎), 「植木屋考」 ("An essay on uekiya", the Edo nurserymen), 造園雑誌 (Journal of the Japanese Institute of Landscape Architects) 50(5), 30-

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/jila1934/50/5/50_5_30/_pdf)**
- Fallback: [Google: 木村三郎 植木屋考 造園雑誌](https://www.google.com/search?q=%E6%9C%A8%E6%9D%91%E4%B8%89%E9%83%8E+%E6%A4%8D%E6%9C%A8%E5%B1%8B%E8%80%83+%E9%80%A0%E5%9C%92%E9%9B%91%E8%AA%8C)
- **Rests on it:** whether the Edo nursery villages (Somei, Sugamo) grew chrysanthemums and other flowers in field plots, and how large, in "What is the Imperial chrysanthemum field, and did a town grow flowers for the market or the shrine?" on `fields.html` (diagram repo, feature 271 V3). Look for any area or plot size of a nursery's growing ground.
- Blocked by: open access, but the PDF came back with no text layer the session could read (diagram feature 271, V3 write).

### 257. Shinjuku Gyoen National Garden (Ministry of the Environment), 「江戸菊花壇」 leaflet ("The Edo chrysanthemum bed")

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[env.go.jp PDF](https://www.env.go.jp/garden/shinjukugyoen/%E8%8F%8A%E8%8A%B1%E5%A3%87%E3%83%91%E3%83%B3%E3%83%95%E6%97%A5%E6%9C%AC%E8%AA%9E.pdf)**
- Fallback: [Google: 新宿御苑 菊花壇 パンフ 江戸菊花壇](https://www.google.com/search?q=%E6%96%B0%E5%AE%BF%E5%BE%A1%E8%8B%91+%E8%8F%8A%E8%8A%B1%E5%A3%87+%E3%83%91%E3%83%B3%E3%83%95+%E6%B1%9F%E6%88%B8%E8%8F%8A%E8%8A%B1%E5%A3%87)
- **Rests on it:** the imperial chrysanthemum beds (the court's display beds, the nearest real thing to an "Imperial chrysanthemum field") and their size, in the same fields.html question (diagram repo, feature 271 V3).
- Blocked by: the PDF came back with no text layer the session could read (diagram feature 271, V3 write).

### 258. Vincent Goossaert, "Counting the Monks: The 1736-1739 Census of the Chinese Clergy", Late Imperial China 21(2), December 2000, 40-85

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[HAL-SHS PDF](https://shs.hal.science/halshs-00106193v1/file/Countingthemonks.pdf)**
- Fallback: [Google: Goossaert "Counting the Monks" 1736-1739 census Chinese clergy](https://www.google.com/search?q=Goossaert+%22Counting+the+Monks%22+1736-1739+census+Chinese+clergy)
- **Rests on it:** how many clergy lived in a Chinese monastery, and how the Qing census spread them over counties, in "How many monasteries does a county town keep, and who lives in one?" on `religion-and-death.html` (diagram repo, feature 272 R2), where the head count is now an absence note. Look for clergy per county or per monastery.
- Blocked by: HAL-SHS answers a script with a bot-check page (a normal browser passes it); the academia.edu and ResearchGate copies returned 403, and Project MUSE is paywalled (diagram feature 272, R2 write).

### 259. Funakoshi Tōru (船越 徹), Yajima Unkyo and Mari Yōko 1978, 「参道空間の研究(その2) : 神社の参道空間の構成要素の分析」 ("Study of approach spaces, part 2: an analysis of the elements of shrine approaches"), Architectural Institute of Japan, 学術講演梗概集 計画系 53, 617-

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[AIJ paper page](https://www.aij.or.jp/paper/detail.html?productId=108892)**
- Fallback: [Google: 参道空間の研究(その2) 神社の参道空間の構成要素の分析 船越徹](https://www.google.com/search?q=%E5%8F%82%E9%81%93%E7%A9%BA%E9%96%93%E3%81%AE%E7%A0%94%E7%A9%B6%28%E3%81%9D%E3%81%AE2%29+%E7%A5%9E%E7%A4%BE%E3%81%AE%E5%8F%82%E9%81%93%E7%A9%BA%E9%96%93%E3%81%AE%E6%A7%8B%E6%88%90%E8%A6%81%E7%B4%A0%E3%81%AE%E5%88%86%E6%9E%90+%E8%88%B9%E8%B6%8A%E5%BE%B9)
- **Rests on it:** whether any measured survey gives the spacing of torii along an approach, in "Torii spacing - two regimes and nothing in between" on `religion-and-death.html` (diagram repo, feature 272 S). Look for a table of an approach's elements with the distances between successive torii.
- Blocked by: the paper is on the Architectural Institute of Japan's own paper service (a paid download); CiNii Research indexes it with no text (diagram feature 272, S write).

### 260. Funakoshi Tōru (船越 徹), Tsumita Hiroshi and others 1986, 「参道空間の研究(その8) : 神社参道の空間構造の分析」 ("Study of approach spaces, part 8: an analysis of the spatial structure of shrine approaches"), Architectural Institute of Japan, 学術講演梗概集 E 1986, 699-

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[AIJ paper page](https://www.aij.or.jp/paper/detail.html?productId=155456)**
- Fallback: [Google: 参道空間の研究(その8) 神社参道の空間構造の分析](https://www.google.com/search?q=%E5%8F%82%E9%81%93%E7%A9%BA%E9%96%93%E3%81%AE%E7%A0%94%E7%A9%B6%28%E3%81%9D%E3%81%AE8%29+%E7%A5%9E%E7%A4%BE%E5%8F%82%E9%81%93%E3%81%AE%E7%A9%BA%E9%96%93%E6%A7%8B%E9%80%A0%E3%81%AE%E5%88%86%E6%9E%90)
- **Rests on it:** the same torii-spacing question as entry 259 (diagram repo, feature 272 S). Look for distances between torii, and for any small shrine among those surveyed.
- Blocked by: the AIJ paid paper service, as entry 259 (diagram feature 272, S write).

### 261. Kawasaki Kiyoshi (川崎 清), Kobayashi Masami and Morita Masahiro 1989, 「参道空間の構成に関する研究 : カモ神社の事例を通して」 ("A study of the composition of shrine approaches, through the Kamo shrines"), Architectural Institute of Japan, 学術講演梗概集 E 1989, 729-

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[AIJ paper page](https://www.aij.or.jp/paper/detail.html?productId=156870)**
- Fallback: [Google: 参道空間の構成に関する研究 カモ神社の事例を通して](https://www.google.com/search?q=%E5%8F%82%E9%81%93%E7%A9%BA%E9%96%93%E3%81%AE%E6%A7%8B%E6%88%90%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E7%A0%94%E7%A9%B6+%E3%82%AB%E3%83%A2%E7%A5%9E%E7%A4%BE%E3%81%AE%E4%BA%8B%E4%BE%8B%E3%82%92%E9%80%9A%E3%81%97%E3%81%A6)
- **Rests on it:** the same torii-spacing question as entry 259; the Kamo shrines include small local ones, so this may give a small shrine's approach length or the distance from its innermost torii to the hall, in "Where do the first and the innermost arches stand, and where does the hall's label go?" on `religion-and-death.html` (diagram repo, feature 272 S).
- Blocked by: the AIJ paid paper service, as entry 259 (diagram feature 272, S write).

### 262. Hikino Kyōsuke (引野 亨輔) 2006, 「鎮守のご本尊 : 江戸時代における神仏習合の一事例」 ("The Buddhist image of a village's tutelary shrine: a case of kami-Buddha fusion in the Edo period"), 福山大学人間文化学部紀要 (Journal of the Faculty of Human Cultures and Sciences, Fukuyama University) 6, 63-

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[CiNii Research record](https://cir.nii.ac.jp/crid/1570572702335147008)**
- Fallback: [Google: 引野亨輔 鎮守のご本尊 江戸時代における神仏習合の一事例](https://www.google.com/search?q=%E5%BC%95%E9%87%8E%E4%BA%A8%E8%BC%94+%E9%8E%AE%E5%AE%88%E3%81%AE%E3%81%94%E6%9C%AC%E5%B0%8A+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E7%A5%9E%E4%BB%8F%E7%BF%92%E5%90%88%E3%81%AE%E4%B8%80%E4%BA%8B%E4%BE%8B)
- **Rests on it:** who served a village shrine in the Edo period - a resident monk, a shrine-temple, or the parishioners - in "Does the country monk live at the shrine?" on `religion-and-death.html` (diagram repo, feature 272 S), where how common the monk-served village shrine was is an absence note. Look for who kept the village shrine and its Buddhist image.
- Blocked by: CiNii indexes it with an abstract and no text link; the university's bulletin was not found online by the session (diagram feature 272, S write).

### 263. 「中国文庙建筑格局特色简说」 ("A short account of the layouts of Chinese Confucian temples"), an essay on Zhihu

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Zhihu essay](https://zhuanlan.zhihu.com/p/587315996)**
- Fallback: [Google: 中国文庙建筑格局特色简说 知乎](https://www.google.com/search?q=%E4%B8%AD%E5%9B%BD%E6%96%87%E5%BA%99%E5%BB%BA%E7%AD%91%E6%A0%BC%E5%B1%80%E7%89%B9%E8%89%B2%E7%AE%80%E8%AF%B4+%E7%9F%A5%E4%B9%8E)
- **Rests on it:** how many prefecture and county Confucian temples the Ming had (a search summary credits this essay with about 1,560) and how big a county's Confucian temple was on the ground, in "Does a county seat or a city carry the state cult's altars and temples, and how big are they?" on `religion-and-death.html` (diagram repo, feature 272 R4), where both are an absence note. Look for the count and for any county temple's site area.
- Blocked by: Zhihu returned 403 Forbidden to the fetch tool and to curl (diagram feature 272, R4 write).

### 264. Beijing Municipal Cultural Heritage Bureau, 「大觉寺寺庙建筑布局和艺术（上）」 ("The layout and art of the Dajue temple, part 1")

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Beijing heritage bureau page](https://wwj.beijing.gov.cn/bjww/wwjzzcslm/1731063/1731066/djs/1731072/1731295/index.html)**
- Fallback: [Google: 大觉寺寺庙建筑布局和艺术 北京市文物局](https://www.google.com/search?q=%E5%A4%A7%E8%A7%89%E5%AF%BA%E5%AF%BA%E5%BA%99%E5%BB%BA%E7%AD%91%E5%B8%83%E5%B1%80%E5%92%8C%E8%89%BA%E6%9C%AF+%E5%8C%97%E4%BA%AC%E5%B8%82%E6%96%87%E7%89%A9%E5%B1%80)
- **Rests on it:** the Dajue temple's site - about 40,000 m², 400 by 100 m, by a search summary of this page, against the 6,000 m² that zh.wikipedia gives and the record uses - and the width and depth of its main hall, in "What does a temple precinct hold, and how big are its halls?" on `religion-and-death.html` (diagram repo, feature 272 R4). Look for the site's area and dimensions and the halls' bays.
- Blocked by: the TLS handshake timed out for the fetch tool and for curl (diagram feature 272, R4 write).

### 265. Senjuji (専修寺), Tsu, the head temple of the Takada branch of Jodo Shinshu, its page on its bell tower

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[senjuji.or.jp page](https://www.senjuji.or.jp/sisetsu/shoro.php)**
- Fallback: [Google: 専修寺 鐘楼 senjuji.or.jp](https://www.google.com/search?q=%E5%B0%82%E4%BF%AE%E5%AF%BA+%E9%90%98%E6%A5%BC+senjuji.or.jp)
- **Rests on it:** a temple bell tower's size and date, beside the one bay square of Ryosenji's, in "Does a city temple keep its own bell tower and a pagoda, and how tall are they?" on `religion-and-death.html` (diagram repo, feature 272 R4), where the bell tower's size is a guess. Look for its bays in feet or meters.
- Blocked by: the connection was refused (ECONNREFUSED) to the fetch tool and to curl (diagram feature 272, R4 write).

### 266. 「江戸時代村落における寄合の研究」 ("A study of the village meeting in Edo-period villages"), a PDF served by CORE

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[CORE PDF](https://core.ac.uk/download/pdf/223197506.pdf)**
- Fallback: [Google: 江戸時代村落における寄合の研究](https://www.google.com/search?q=%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3%E6%9D%91%E8%90%BD%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E5%AF%84%E5%90%88%E3%81%AE%E7%A0%94%E7%A9%B6)
- **Rests on it:** where an Edo village held its meeting - the headman's house, a temple or shrine, or a meeting hall of its own - and how big a meeting hall was, in "Where did the village meet?" on `homesteads.html` (diagram repo, feature 271 V7), where the hall's size is an absence note. Look for the meeting places named and any hall's size in ken or tsubo.
- Blocked by: CORE redirected the download to its file server, which returned 403 Forbidden to the fetch tool; the page-saving tool found no text layer (diagram feature 271, V7 write).

### 267. Kohfukuji, 「三重塔」 ("the three-story pagoda"), the temple's own page

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[kohfukuji.com page](https://www.kohfukuji.com/property/a-0002/)**
- Fallback: [Google: 興福寺 三重塔 kohfukuji.com 高さ19.1m](https://www.google.com/search?q=%E8%88%88%E7%A6%8F%E5%AF%BA+%E4%B8%89%E9%87%8D%E5%A1%94+kohfukuji.com+%E9%AB%98%E3%81%9519.1m)
- **Rests on it:** a three-story pagoda's height (19.1 m) and first-story width (three bays, 4.8 m), quoted as 「【規模】 高さ19.1m、初層：方三間4.8ｍ」, in "Does a city temple keep its own bell tower and a pagoda, and how tall are they?" on `religion-and-death.html` (diagram repo, feature 272 R4), where the pagoda's size is a guess drawn from it. A saved copy lets the quotation be checked character for character.
- Blocked by: SSL certificate verification failed (unable to get local issuer certificate) for the fetch tool, the page-saving script and the quote-check agent (diagram feature 272, R4 check).

### 268. Shinagawa city, 『品川区史 通史編 上巻』 (the history of Shinagawa ward, general volume 1), the section 「寺院の増加」 ("the increase in temples"), on the ward's digital archive

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Shinagawa digital archive text page](https://adeac.jp/shinagawa-city/text-list/d000010/ht003320)**
- Fallback: [Google: 品川区史 通史編 上巻 寺院の増加 adeac](https://www.google.com/search?q=%E5%93%81%E5%B7%9D%E5%8C%BA%E5%8F%B2+%E9%80%9A%E5%8F%B2%E7%B7%A8+%E4%B8%8A%E5%B7%BB+%E5%AF%BA%E9%99%A2%E3%81%AE%E5%A2%97%E5%8A%A0+adeac)
- **Rests on it:** how many of a district's Edo villages kept a temple of their own, none or several, in "Does a village keep a Buddhist temple of its own?" on `religion-and-death.html` (diagram repo, feature 272 R3), where that share is an absence note. Look for a count of temples against villages in the old Shinagawa villages.
- Blocked by: the archive serves the text into a JavaScript viewer; the fetch tool and curl get only the navigation shell (diagram feature 272, R3 write).

### 269. Baidu Baike, 「土地庙」 ("the earth-god temple")

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike entry](https://baike.baidu.com/item/%E5%9C%9F%E5%9C%B0%E5%BA%99/9389917)**
- Fallback: [Google: 百度百科 土地庙 中国民间供奉土地神的庙宇](https://www.google.com/search?q=%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91+%E5%9C%9F%E5%9C%B0%E5%BA%99+%E4%B8%AD%E5%9B%BD%E6%B0%91%E9%97%B4%E4%BE%9B%E5%A5%89%E5%9C%9F%E5%9C%B0%E7%A5%9E%E7%9A%84%E5%BA%99%E5%AE%87)
- **Rests on it:** the size and siting of a Chinese village's earth-god shrine and how many a village kept, in "How many wayside shrines does a village or a town's streets carry, how big are they, and where do they stand?" on `religion-and-death.html` (diagram repo, feature 272 R3), which now rests on one Yangzi-delta study. Save the whole entry as a page.
- Blocked by: the fetch tool got 403 Forbidden; curl got the page once and then an anti-bot stub (diagram feature 272, R3 write).

### 270. Kiyose City Local Museum, 「幕藩体制下の農民の居宅」 ("Farmers' houses under the shogunate-domain system")

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[museum-kiyose.jp PDF](http://www.museum-kiyose.jp/image/kenkyu/kyotaku72.pdf)**
- Fallback: [Google: 清瀬市郷土博物館 幕藩体制下の農民の居宅](https://www.google.com/search?q=%E6%B8%85%E7%80%AC%E5%B8%82%E9%83%B7%E5%9C%9F%E5%8D%9A%E7%89%A9%E9%A4%A8+%E5%B9%95%E8%97%A9%E4%BD%93%E5%88%B6%E4%B8%8B%E3%81%AE%E8%BE%B2%E6%B0%91%E3%81%AE%E5%B1%85%E5%AE%85)
- **Rests on it:** the size of an ordinary Edo farmer's house against a headman's, the size of a farm household's house plot, and the size of its kitchen garden, in "What makes the headman's house different?", "How tightly does a nucleated village pack?" and "How big was a dooryard garden?" on `homesteads.html` (diagram repo, feature 269 H3), where each is an absence note or a guess. Look for house sizes in ken or tsubo by status, and any figure for the 屋敷地 or the 屋敷畑.
- Blocked by: both the http and https URLs now land on the museum's home page, and the web archive could not be fetched from the container (diagram feature 269, H3 write).

### 271. fx361.com, a paper on the forms of Cantonese ancestral halls (news/2018/1109/4471412)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[fx361.com page](https://m.fx361.com/news/2018/1109/4471412.html)**
- Fallback: [Google: 广府祠堂 形制 fx361](https://www.google.com/search?q=%E5%B9%BF%E5%BA%9C%E7%A5%A0%E5%A0%82+%E5%BD%A2%E5%88%B6+fx361)
- **Rests on it:** the whole footprint of a south-China village's ancestral hall (its frontage and depth in meters), in "Where did a south-China village's ancestral hall stand, and how big was it?" on `homesteads.html` (diagram repo, feature 271 V7), where the footprint is an absence note and the map's hall a labeled guess. Look for a hall's frontage and depth by number of bays and halls deep.
- Blocked by: the fetch tool got 403 Forbidden (diagram feature 271, V7 write and check).

### 272. Neil Schmid, "Giving while keeping: inexhaustible treasuries and inalienable wealth in medieval China", Studies in Chinese Religions 5(2), 2019

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ResearchGate PDF](https://www.researchgate.net/profile/Neil-Schmid/publication/337457692_Giving_while_keeping_inexhaustible_treasuries_and_inalienable_wealth_in_medieval_China/links/60f2951afb568a7098b6135d/Giving-while-keeping-inexhaustible-treasuries-and-inalienable-wealth-in-medieval-China.pdf)** (publisher: https://doi.org/10.1080/23729988.2019.1639463)
- Fallback: [Google: Schmid "Giving while keeping" inexhaustible treasuries inalienable wealth medieval China](https://www.google.com/search?q=Schmid+%22Giving+while+keeping%22+inexhaustible+treasuries+inalienable+wealth+medieval+China)
- **Rests on it:** why Xuanzong ordered the Chang'an inexhaustible treasury destroyed in 713 (the record once said "as fraudulent banking"), in "Temples as economic institutions with hereditary householder clergy" on `religion-and-death.html` (diagram repo, feature 272 T), where the reason is now an absence note. Look for the 713 order and the reason the court gave.
- Blocked by: the publisher returns 403 (paywall); ResearchGate serves a "temporarily unavailable" page with 403 to both the fetch tool and curl (diagram feature 272, T write).

### 273. 御府内寺社備考 (Gofunai jisha biko, the shogunate's 1820s survey of the temples and shrines of Edo), National Diet Library

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[NDL Search record](https://ndlsearch.ndl.go.jp/books/R100000002-I000001835967)** (the scans are in the NDL Digital Collections, https://dl.ndl.go.jp/)
- Fallback: [Google: 御府内寺社備考 国立国会図書館デジタルコレクション](https://www.google.com/search?q=%E5%BE%A1%E5%BA%9C%E5%86%85%E5%AF%BA%E7%A4%BE%E5%82%99%E8%80%83+%E5%9B%BD%E7%AB%8B%E5%9B%BD%E4%BC%9A%E5%9B%B3%E6%9B%B8%E9%A4%A8%E3%83%87%E3%82%B8%E3%82%BF%E3%83%AB%E3%82%B3%E3%83%AC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3)
- **Rests on it:** the precinct of a single ordinary Edo temple in a temple quarter (its frontage and depth, or its area in tsubo), and the ground of a town ward's small shrine, in "How big is a temple in a temple quarter, and how do the temples line the street?" and "How big is a small shrine in a town, and what stands on it?" on `religion-and-death.html` (diagram repo, feature 272 T), where both are absence notes and the map's plots guesses. Look in the volumes for Yanaka, Asakusa or Shitaya for each temple's 境内 in 坪 and any 間口 and 奥行.
- Blocked by: the survey is on no text page the session could find; the NDL scans are page images in a viewer, not text (diagram feature 272, T write).

### 274. Baidu Baike, 明代佛教 ("Buddhism in the Ming dynasty")

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike page](https://baike.baidu.com/item/%E6%98%8E%E4%BB%A3%E4%BD%9B%E6%95%99)**
- Fallback: [Google: 明代佛教 百度百科 度僧 府 四十人](https://www.google.com/search?q=%E6%98%8E%E4%BB%A3%E4%BD%9B%E6%95%99+%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91+%E5%BA%A6%E5%83%A7+%E5%BA%9C+%E5%9B%9B%E5%8D%81%E4%BA%BA)
- **Rests on it:** how many monks a Ming city monastery held, in "City temple size - the setting's deliberate liberty" on `religion-and-death.html` (diagram repo, feature 272 B37), where it is an absence note and the map's 15-30 and 50+ monks per complex are a guess. A search snippet had the article citing a Ming quota of no more than 40 ordinations for each prefecture; look for that quota with its source, and for any monk count of a named Ming city monastery. Save the whole article as a page.
- Blocked by: HTTP 403 on every fetch, by the fetch tool and by curl (diagram feature 272, B37 write).

### 275. S. K. Mazumder, conference paper on sediment exclusion at river intakes (Con_Ref_83), profskmazumder.com

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[PDF on the author's site](https://www.profskmazumder.com/assets/img/conferencepapers/Con_Ref_83.pdf)**
- Fallback: [Google: Mazumder sediment exclusion intake angle 120 Mosonyi](https://www.google.com/search?q=Mazumder+sediment+exclusion+intake+angle+120+Mosonyi)
- **Rests on it:** that a branch's share of bed load follows its share of flow, and that the best intake angle in a straight channel is 120 degrees, in "Does a moat have a current?" on `water.html` (diagram repo, feature 269 W2). Look at Figure 1 for which way the angle is measured (from the downstream or the upstream direction of the main channel); that would settle whether the record's guess about a square tap on a moat can be promoted or dropped. Save the whole PDF.
- Blocked by: the host answers every fetch, by the fetch tool and by curl, with a "One moment, please..." script-challenge page instead of the PDF (diagram feature 269, W2 check-a).

### 276. 弘前市立弘前図書館 (Hirosaki city library), ADEAC digital archive: 【辻番・自身番・木戸番】

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ADEAC page](https://adeac.jp/hirosaki-lib/text-list/d100030/ht010130)**
- Fallback: [Google: 弘前 辻番 自身番 木戸番 adeac](https://www.google.com/search?q=%E5%BC%98%E5%89%8D+%E8%BE%BB%E7%95%AA+%E8%87%AA%E8%BA%AB%E7%95%AA+%E6%9C%A8%E6%88%B8%E7%95%AA+adeac)
- **Rests on it:** how many guard boxes, watch houses and ward gates a provincial castle town kept, in "How many watch houses and guard boxes did a city keep?" on `urban-features.html` (diagram repo, feature 271 U3), where the provincial count is an absence note and the map's one guard box to each crossing of a samurai ward a guess. Look for counts of 辻番, 自身番 and 木戸 in the Hirosaki castle town, and any hut sizes.
- Blocked by: the page is script-rendered; the fetch returned 253 characters of chrome and no text (diagram feature 271, U3 write).

### 277. 国立歴史民俗博物館研究報告 67, "東北の河原町の特色" (the character of the kawara-machi of the Tohoku castle towns)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[rekihaku repository PDF](https://rekihaku.repo.nii.ac.jp/record/789/files/kenkyuhokoku_067_12.pdf)**
- Fallback: [Google: 東北の河原町の特色 国立歴史民俗博物館研究報告](https://www.google.com/search?q=%E6%9D%B1%E5%8C%97%E3%81%AE%E6%B2%B3%E5%8E%9F%E7%94%BA%E3%81%AE%E7%89%B9%E8%89%B2+%E5%9B%BD%E7%AB%8B%E6%AD%B4%E5%8F%B2%E6%B0%91%E4%BF%97%E5%8D%9A%E7%89%A9%E9%A4%A8%E7%A0%94%E7%A9%B6%E5%A0%B1%E5%91%8A)
- **Rests on it:** how many households a provincial castle town's outcaste quarter held and where in the town it lay, in "How many households does a burakumin quarter hold, and what stands in it besides the houses?" and "Where does a town's burakumin quarter stand?" on `urban-features.html` (diagram repo, feature 271 U3), where the small quarter's count is an absence note. Look for household counts (軒, 戸) of named castle towns' quarters, their placement against the river and the town's edge, and any well or shrine.
- Blocked by: the PDF has no text layer the container can read (diagram feature 271, U3 write).

### 278. 阿部貴弘・篠原修, "近世城下町大坂，江戸の町人地における城下町設計の論理" (the design logic of the commoner quarters of the castle towns of Osaka and Edo), 土木学会論文集D2 68(1)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/jscejhsce/68/1/68_69/_pdf)**
- Fallback: [Google: 近世城下町大坂，江戸の町人地における城下町設計の論理 阿部貴弘](https://www.google.com/search?q=%E8%BF%91%E4%B8%96%E5%9F%8E%E4%B8%8B%E7%94%BA%E5%A4%A7%E5%9D%82%EF%BC%8C%E6%B1%9F%E6%88%B8%E3%81%AE%E7%94%BA%E4%BA%BA%E5%9C%B0%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E5%9F%8E%E4%B8%8B%E7%94%BA%E8%A8%AD%E8%A8%88%E3%81%AE%E8%AB%96%E7%90%86+%E9%98%BF%E9%83%A8%E8%B2%B4%E5%BC%98)
- **Rests on it:** what share of a city's ground its streets took, in "A county seat's street share, open reserve and civic share" on `cities/fabric.html` (diagram repo, feature 269 C3), where the 10-20% band is an absence note checked only by arithmetic on Heian-kyo's grid; and the block sizes and street widths in "How do a city's streets make a grid?" on the same page. Look for street widths (道幅, in 間), block dimensions and any road-area ratio (道路率) for the surveyed quarters of Osaka (Uemachi, Senba, Shimanouchi) and Edo (Nihonbashi, Kyobashi, Ginza).
- Blocked by: the PDF has no text layer the container can read (diagram feature 269, C3 write).

### 279. 西沢淳男, 『代官の日常生活』 (the daily life of the intendants), 講談社 (dated 2014 by the blog that cites it)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kodansha's page for the book](https://bookclub.kodansha.co.jp/search?q=%E4%BB%A3%E5%AE%98%E3%81%AE%E6%97%A5%E5%B8%B8%E7%94%9F%E6%B4%BB)** (the session believes it lives here; a print book, so the GM's copy or a library scan)
- Fallback: [Google: 代官の日常生活 西沢淳男](https://www.google.com/search?q=%E4%BB%A3%E5%AE%98%E3%81%AE%E6%97%A5%E5%B8%B8%E7%94%9F%E6%B4%BB+%E8%A5%BF%E6%B2%A2%E6%B7%B3%E7%94%B7)
- **Rests on it:** "Poverty texture is historically genuine" on `buildings.html` (diagram repo, feature 269 X1B), where the figure that nine intendants in ten carried hikioi debt, that the office allowance fell short after 1725, and gundai Toyoda Tomonao's letter from Takayama about snow on his veranda rest only on a blog's retelling of this book. Look for the hikioi share and its date range, what the post-1725 office allowance (諸入用) covered and whether offices ran deficits, and the letter's wording and date.
- Blocked by: a print book with no public full text (diagram feature 269, X1B write). Its edition and year were not checked; the blog's "2014" is all the session read.

### 280. 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿） (preliminary design report, 2026 high-standard farmland project, Conghua District, Guangzhou)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[nyncj.gz.gov.cn PDF](http://nyncj.gz.gov.cn/attachment/8/8037/8037125/10854794.pdf)**
- Fallback: [Google: 2026年度广州市从化区高标准农田改造提升建设项目初步设计报告](https://www.google.com/search?q=2026%E5%B9%B4%E5%BA%A6%E5%B9%BF%E5%B7%9E%E5%B8%82%E4%BB%8E%E5%8C%96%E5%8C%BA%E9%AB%98%E6%A0%87%E5%87%86%E5%86%9C%E7%94%B0%E6%94%B9%E9%80%A0%E6%8F%90%E5%8D%87%E5%BB%BA%E8%AE%BE%E9%A1%B9%E7%9B%AE%E5%88%9D%E6%AD%A5%E8%AE%BE%E8%AE%A1%E6%8A%A5%E5%91%8A)
- **Rests on it:** the modern corroboration row of the canal-width ladder in "Water-width ladder - the real-world tiers" on `water.html` (diagram repo, feature 280 W1): the lateral (斗渠) at 1.0 and 1.2 m and the farm canal (农渠) at 0.4 and 0.6 m. Look for whether these are design figures or completed works, and the table rows quoted.
- Blocked by: the checker's fetch failed ("Socket is closed") on 2026-09-28, and the PDF has no text layer the container can read (diagram feature 280, W1 check).

### 281. 馬一龍 (Ma Yilong), 『農說』 (Nongshuo, "Discourse on farming"), Ming, 16th century

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[ctext.org 農說_梭山農譜](https://ctext.org/wiki.pl?if=gb&res=5869563&remap=gb)** (the session believes the full text lives here; a save of the page as HTML or text is enough)
- Fallback: [Google: 農說 馬一龍 疏者每畝約七千二百科](https://www.google.com/search?q=%E8%BE%B2%E8%AA%AA+%E9%A6%AC%E4%B8%80%E9%BE%8D+%E7%96%8F%E8%80%85%E6%AF%8F%E7%95%9D%E7%B4%84%E4%B8%83%E5%8D%83%E4%BA%8C%E7%99%BE%E7%A7%91)
- **Rests on it:** the pre-modern density of transplanted rice hills in "Why ruled rows waited for Meiji" on `fields.html` (diagram repo, feature 280 F3, item M06). A search summary quotes the book as 「譬疏者每亩约七千二百科，密则数逾于万」 (sparse planting about 7,200 hills a mu, dense over 10,000), which at a mu of about 614 m2 is hills about 25-29 cm apart. Look for that sentence, its context (the Liyang district of Jiangsu), and any spacing in cun.
- Blocked by: ctext.org returns an access notice to the container, not the text; the other copies found (up18.com.cn, zhonghuadiancang.com) timed out or refused the connection on 2026-09-28 (diagram feature 280, F3 write).

### 282. 游修龄 (You Xiuling) et al., 《中国稻作史》 (A history of rice farming in China), chapter 4 part 3, "播种和育秧" (sowing and raising seedlings)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[economy.guoxue.com, 中国经济史论坛](http://economy.guoxue.com/?p=417)** (a web copy of the chapter; the book itself, 中国农业出版社, 1995, is the fallback)
- Fallback: [Google: 播种和育秧 中国稻作史 第四章](https://www.google.com/search?q=%E6%92%AD%E7%A7%8D%E5%92%8C%E8%82%B2%E7%A7%A7+%E4%B8%AD%E5%9B%BD%E7%A8%BB%E4%BD%9C%E5%8F%B2+%E7%AC%AC%E5%9B%9B%E7%AB%A0)
- **Rests on it:** the same M06 finding as entry 281: a search summary says the chapter reads Ma Yilong's 7,200 and over 10,000 hills a mu for Liyang, about 20,000 a mu for Jiaxing reckoned from the 沈氏農書, and Yuan and Qing planting frames and ropes (秧弹, 秧绳) keeping hills within five cun. Look for those passages and the mu the chapter converts with. The author named here is the session's belief from the book's title; check it.
- Blocked by: the page timed out on every fetch from the container on 2026-09-28 (diagram feature 280, F3 write).
### 283. T/JSSLKX 002-2021, 小型農田水利工程規劃設計導則 (Guideline for the planning and design of small farmland water-conservancy works), Jiangsu Provincial Water Conservancy Survey and Design Association, 2021

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- **[jsszy.org.cn PDF](http://jsszy.org.cn/UserFiles/file/20221103/20221103155002_6437.pdf)**
- Fallback: [Google: T/JSSLKX 002-2021 小型农田水利工程规划设计导则](https://www.google.com/search?q=T%2FJSSLKX+002-2021+%E5%B0%8F%E5%9E%8B%E5%86%9C%E7%94%B0%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%E8%A7%84%E5%88%92%E8%AE%BE%E8%AE%A1%E5%AF%BC%E5%88%99)
- **Rests on it:** the modern design rule in "Why are the dry plots beside a canal square to the canal?" on `fields.html` (diagram repo, feature 280 F2): successive canal grades at right angles on flat ground and the watering direction following the field's fall (§7.4.3-7.4.9). Look for those clauses, the guideline's title page and its scope.
- Blocked by: read in full on 2026-09-12, but on 2026-09-28 the host refused the connection (ECONNREFUSED on 443, and plain http timed out), so the quote-check could not re-read it (diagram feature 280, F2 check).

### 284. 今石みぎわ (Imaishi Migiwa), 「莚と莚織りの技術」 (The straw mat and the technique of mat weaving), Tokyo National Research Institute for Cultural Properties, intangible cultural heritage research report, 2012 (file 06_55_Imaishi.pdf)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[tobunken.repo.nii.ac.jp PDF](https://tobunken.repo.nii.ac.jp/record/3166/files/06_55_Imaishi.pdf)** (repository record 3166)
- Fallback: [Google: 今石 西谷 莚 経糸 上糸 21本 下糸 21本](https://www.google.com/search?q=%E4%BB%8A%E7%9F%B3+%E8%A5%BF%E8%B0%B7+%E8%8E%9A+%E7%B5%8C%E7%B3%B8+%E4%B8%8A%E7%B3%B8+21%E6%9C%AC)
- **Rests on it:** the measured straw mat of about 3 by 6 shaku (90 x 180 cm) in "How big was the work yard, and how did the sizes spread?" on `homesteads.html` (diagram repo, feature 280 H2), which turns the mat counts into yard areas. Look for the sentence 「西谷では経糸の数は上糸 21 本・下糸 21 本の計 42 本で、これで幅およそ３尺、長さ６尺（90 × 180㌢）程度の莚が織りあがる。」 and its page.
- Blocked by: the repository redirects to a signed object-storage URL that expires in 60 seconds and serves the 3.9 MB file as application/octet-stream; the checker could not read it as text, and the one fetch that returned content described a different document, on trowels (diagram feature 280, H2 check, 2026-09-28).

### 285. Nakanishi Ryotaro (中西僚太郎) 1994, 「明治前期における耕牛・耕馬の分布と牛馬耕普及の地域性について」 ("The distribution of plow cattle and plow horses in the early Meiji period and the regional character of the spread of animal plowing"), 歴史地理学 (Historical Geography) no. 169

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[hist-geo.jp PDF](http://hist-geo.jp/img/archive/169_002.pdf)** (CiNii record: https://cir.nii.ac.jp/crid/1520009408289452416)
- Fallback: [Google: 中西僚太郎 明治前期における耕牛・耕馬の分布と牛馬耕普及の地域性について](https://www.google.com/search?q=%E4%B8%AD%E8%A5%BF%E5%83%9A%E5%A4%AA%E9%83%8E+%E6%98%8E%E6%B2%BB%E5%89%8D%E6%9C%9F%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E8%80%95%E7%89%9B%E3%83%BB%E8%80%95%E9%A6%AC%E3%81%AE%E5%88%86%E5%B8%83)
- **Rests on it:** the plow-horse east, plow-ox west and mixed Kyushu and Shikoku regions in "How big is a draft-animal byre, and what stands in it?" on `homesteads.html` (diagram repo). A saved copy would let the quoted original 「全国はおおまかには，東日本の耕馬地域，近畿・中国地方を主とする西日本の耕牛地域，九州・四国の耕牛・耕馬混合地域にわけることができると考える。」 be checked character for character.
- Blocked by: hist-geo.jp refused the checker's connection (ECONNREFUSED on https) and the script found no text layer it could read (diagram feature 280, H2 check, 2026-09-28).
### 286. 新藤正夫・安ヶ川恵子 (Shindo Masao and Yasugawa Keiko) 2011, 「鷹栖村のお藪史料にみる江戸時代後期の散村の屋敷林」 ("The homestead groves of a dispersed village in the late Edo period, as seen in the o-yabu records of Takanosu village"), 砺波散村地域研究所研究紀要 (Bulletin of the Tonami Dispersed Settlement Research Institute) no. 28, pp. 38-46

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):
- **[1073shoso.jp (Tonami city archive, where the institute bulletins are posted as e-books)](https://1073shoso.jp/www/sankyo/result.jsp?genre=8)**
- Fallback: [Google: 鷹栖村のお藪史料にみる江戸時代後期の散村の屋敷林](https://www.google.com/search?q=%E9%B7%B9%E6%A0%96%E6%9D%91%E3%81%AE%E3%81%8A%E8%97%AA%E5%8F%B2%E6%96%99%E3%81%AB%E3%81%BF%E3%82%8B%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3%E5%BE%8C%E6%9C%9F%E3%81%AE%E6%95%A3%E6%9D%91%E3%81%AE%E5%B1%8B%E6%95%B7%E6%9E%97)
- **Rests on it:** "Was the homestead grove there before 1868, and what size and shape was it?" on `homesteads.html` (diagram repo, feature 280 H1): the drawn grove is sized from a 1987 count of about 33 trees a homestead, and no premodern count was found. This study of one Tonami village's late-Edo grove records may count the trees or bamboo of each homestead grove before 1868; look for any per-household tree or sugi count and any statement of which sides of the house the grove stood on.
- Blocked by: found only as a reference in Miura 2014 (J-STAGE, tga 65(4)); no web search found the bulletin issue, and the Tonami city archive answered HTTP 500 to every fetch on 2026-09-28 (diagram feature 280, H1 write).

### 287. 高浦秀明 (Takaura Hideaki) 1986, 「江戸時代における隅田川の橋梁の景観に関する研究」 ("A study of the landscape of the Sumida River's bridges in the Edo period"), 第6回日本土木史研究発表会論文集 (Proceedings of the 6th Japan Civil Engineering History Conference)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[J-STAGE PDF](https://www.jstage.jst.go.jp/article/journalhs1981/6/0/6_0_189/_pdf/-char/ja)**
- Fallback: [Google: 高浦秀明 江戸時代における隅田川の橋梁の景観に関する研究](https://www.google.com/search?q=%E9%AB%98%E6%B5%A6%E7%A7%80%E6%98%8E+%E6%B1%9F%E6%88%B8%E6%99%82%E4%BB%A3%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E9%9A%85%E7%94%B0%E5%B7%9D%E3%81%AE%E6%A9%8B%E6%A2%81%E3%81%AE%E6%99%AF%E8%A6%B3%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E7%A0%94%E7%A9%B6)
- **Rests on it:** the 10 ft of deck our maps draw past the water at each end of a bridge, in "How far past the bank does a bridge land?" on `ways.html` (diagram repo, feature 280 Y1), a guess with no period figure. Look for any Edo-period dimension of a bridge's abutment (橋台) or of how far its deck or girders ran onto the bank beyond the water, and for how the ends of the Sumida bridges sat on their stone-faced banks.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, Y1 write, 2026-09-28).

### 288. 「日本の木造橋の構造とデザイン」 ("The structure and design of Japan's timber bridges"), Japan Society of Civil Engineers, 2003 (library.jsce.or.jp open file 00902/2003/23-0075)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[JSCE library PDF](http://library.jsce.or.jp/jsce/open/00902/2003/23-0075.pdf)**
- Fallback: [Google: 日本の木造橋の構造とデザイン 土木学会](https://www.google.com/search?q=%E6%97%A5%E6%9C%AC%E3%81%AE%E6%9C%A8%E9%80%A0%E6%A9%8B%E3%81%AE%E6%A7%8B%E9%80%A0%E3%81%A8%E3%83%87%E3%82%B6%E3%82%A4%E3%83%B3+%E5%9C%9F%E6%9C%A8%E5%AD%A6%E4%BC%9A)
- **Rests on it:** the same 10 ft bridge landing on `ways.html` ("How far past the bank does a bridge land?", diagram feature 280 Y1). Look for how a traditional Japanese beam bridge's end was seated on its bank - an abutment, a stone wall, a buried girder tail - and any length given for it, with the period it applies to.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, Y1 write, 2026-09-28).

### 289. "Paddy", Encyclopaedia Britannica (britannica.com/topic/paddy)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Britannica: paddy](https://www.britannica.com/topic/paddy)**
- Fallback: [Google: britannica paddy rice farming harvesting processing](https://www.google.com/search?q=britannica+paddy+rice+farming+harvesting+processing)
- **Rests on it:** the depth of standing water in a rice paddy, set against deep-water lotus in "The three overlays a village may carry" on `archetypes.html` (diagram feature 280 A1). A search summary gave "4-6 inches (10-15 centimetres) of water ... for three-quarters of the growing season"; save the page as HTML or PDF so the sentence can be quoted.
- Blocked by: HTTP 403 to the fetcher (diagram feature 280, A1 check, 2026-09-28).

### 290. Michael Abele, *Peasants, skinners, and dead cattle* (PhD dissertation, Illinois, 2018) - the PDF's own link

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[IDEALS repository record](https://www.ideals.illinois.edu/items/107042)** (open access; the PDF is a separate file on that page)
- Fallback: [Google: Abele "Peasants, skinners, and dead cattle" ideals illinois](https://www.google.com/search?q=Abele+%22Peasants%2C+skinners%2C+and+dead+cattle%22+ideals+illinois)
- **Rests on it:** nothing new to download - the copy is already saved as `ABELE-DISSERTATION-2018.pdf` (item 6), and its four passages were matched in it. What is needed is the PDF's own address: copy the record's download link (the form is `https://www.ideals.illinois.edu/items/107042/bitstreams/<n>/data.pdf`) into this entry, so the kawata note on `urban-features.html` ("Caste geography and status zoning") can link the full text rather than the landing page.
- Blocked by: HTTP 403 to the fetcher, so the file link cannot be read off the record page (diagram feature 280, U4 check, 2026-09-28).

### 291. 服部周平・二井昭佳 「洪水常襲地における神社立地に関する基礎的研究 - 黒部川扇状地・富山県入善町を対象として」 ("A basic study of shrine siting in ground often flooded: the Kurobe River fan, Nyuzen, Toyama"), JSCE, 2012

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[JSCE library PDF](http://library.jsce.or.jp/jsce/open/00897/2012/B43D.pdf)**
- Fallback: [Google: 洪水常襲地における神社立地に関する基礎的研究 黒部川扇状地 入善町](https://www.google.com/search?q=%E6%B4%AA%E6%B0%B4%E5%B8%B8%E8%A5%B2%E5%9C%B0%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E7%A5%9E%E7%A4%BE%E7%AB%8B%E5%9C%B0%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E5%9F%BA%E7%A4%8E%E7%9A%84%E7%A0%94%E7%A9%B6+%E9%BB%92%E9%83%A8%E5%B7%9D%E6%89%87%E7%8A%B6%E5%9C%B0+%E5%85%A5%E5%96%84%E7%94%BA)
- **Rests on it:** the rule that no shrine stands on a marsh, in "Was wet ground kept free of graves, houses and wells before modern times?" on `water.html` (diagram feature 280 W4), which rests on the GM's ruling alone. Look for whether old shrines stand on the natural levees or other raised ground rather than the wet ground, and whether the paper dates the shrines or the siting to before 1868.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, W4 write, 2026-09-29).

### 292. 尾崎信・正水裕介・中井祐 「水害常襲地における神社立地特性 - 高知県高知市・須崎市を対象として」 ("Shrine siting in ground often flooded: Kochi and Susaki, Kochi"), University of Tokyo landscape laboratory

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[University of Tokyo PDF](http://keikan.t.u-tokyo.ac.jp/documents/research/osaki.pdf)**
- Fallback: [Google: 水害常襲地における神社立地特性 高知市 須崎市 尾崎信](https://www.google.com/search?q=%E6%B0%B4%E5%AE%B3%E5%B8%B8%E8%A5%B2%E5%9C%B0%E3%81%AB%E3%81%8A%E3%81%91%E3%82%8B%E7%A5%9E%E7%A4%BE%E7%AB%8B%E5%9C%B0%E7%89%B9%E6%80%A7+%E9%AB%98%E7%9F%A5%E5%B8%82+%E9%A0%88%E5%B4%8E%E5%B8%82+%E5%B0%BE%E5%B4%8E%E4%BF%A1)
- **Rests on it:** the same shrine rule on `water.html` (feature 280 W4). A search summary said shrines near the mountains stand higher than the settlements while on levees and low ground they stand at about the same height or lower - which would bear on whether a shrine ever stood on wet ground. Look for that finding and any date for the shrines.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, W4 write, 2026-09-29).

### 293. 百姓伝記 巻七 「防水集」, a full modern Japanese translation by a retired river engineer (motosanhomepage.com, 2017, revised 2025)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[the post, with the PDF attached](https://motosanhomepage.com/2017/09/10/hyakusyo-denki-bousui-syu/)** (the translation is the attached file 防水集ver-2)
- Fallback: [Google: 百姓伝記 防水集 全文訳 流域環境防災研究所](https://www.google.com/search?q=%E7%99%BE%E5%A7%93%E4%BC%9D%E8%A8%98+%E9%98%B2%E6%B0%B4%E9%9B%86+%E5%85%A8%E6%96%87%E8%A8%B3+%E6%B5%81%E5%9F%9F%E7%92%B0%E5%A2%83%E9%98%B2%E7%81%BD%E7%A0%94%E7%A9%B6%E6%89%80)
- **Rests on it:** the reed-free pond bank, in "Were a pond's reeded shore and reed-free bank only modern?" on `water.html` (feature 280 W4), which has no Japanese source before 1868 for what an embankment carried. A search summary said the Hyakusho denki (1680s) has a new embankment turfed, willow used for stakes, no tree that grows large, and only a small bamboo planted and cut back every year. Look for those passages and for anything on mowing or burning an embankment.
- Blocked by: the translation is an attached PDF the fetcher could not read; the post itself carries only the translator's introduction (diagram feature 280, W4 write, 2026-09-29).

### 294. "Hong Kong's Fung Shui Woodland", a University of Hong Kong thesis (HKU Scholars Hub)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[HKU Scholars Hub PDF](https://hub.hku.hk/bitstream/10722/192800/1/FullText.pdf)**
- Fallback: [Google: "Hong Kong's Fung Shui Woodland" hub.hku.hk](https://www.google.com/search?q=%22Hong+Kong%27s+Fung+Shui+Woodland%22+hub.hku.hk)
- **Rests on it:** "How big were a village's groves before modern times?" on `vegetation.html` (feature 280 V1), which finds no area for any fengshui wood before 1912. A thesis on Hong Kong's woods may date a wood's extent from the 1899-1904 New Territories survey or the 1924 aerial photographs, or say whether the woods shrank in the war years. Look for any area, boundary or tree count dated before 1912, and any finding that the woods grew or shrank.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, V1 write, 2026-09-29).

### 295. 「明清民国顺德的基塘农业与经济转型」 ("Dike-pond farming and economic change in Shunde, Ming, Qing and Republic"), Zhongguo jingjishi luntan (中国经济史论坛)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[economy.guoxue.com](http://economy.guoxue.com/?p=2483)**
- Fallback: [Google: 明清民国顺德的基塘农业与经济转型](https://www.google.com/search?q=%E6%98%8E%E6%B8%85%E6%B0%91%E5%9B%BD%E9%A1%BA%E5%BE%B7%E7%9A%84%E5%9F%BA%E5%A1%98%E5%86%9C%E4%B8%9A%E4%B8%8E%E7%BB%8F%E6%B5%8E%E8%BD%AC%E5%9E%8B)
- **Rests on it:** the pig sty on a pond dike, in "Does a pig sty have to stand back from the water, or from the pond's sluice?" and "Does a dike-pond hamlet keep pigs and ducks on its pond dikes?" on `archetypes.html` (diagram feature 280 A4), which find no premodern date for a shed built on the dike so its waste flows into the pond. A search summary said the article quotes a Qing silkworm book of Shunde on households raising fish, pigs, silkworms and mulberry together (「鱼、猪、蚕、桑四者齐养」). Look for that passage, its book and date, and anything on where the pigs were penned or whether their dung went into the pond.
- Blocked by: the site timed out on every fetch (diagram feature 280, A4 write, 2026-09-29).

### 296. 劉翠溶「明清時代南方地區的專業生產」 (Liu Ts'ui-jung, "Specialized production in south China in the Ming and Qing"), 《大陸雜誌》 56.3-4 (1978)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Academia Sinica PDF](https://idv.sinica.edu.tw/ectjliu/%E5%8A%89%E7%BF%A0%E6%BA%B6%E5%AD%B8%E8%A1%93%E8%91%97%E4%BD%9C/W5-%E7%B6%93%E6%BF%9F%E5%8F%B21pdf/1978%E5%8D%97%E6%96%B9%E5%9C%B0%E5%8D%80%E5%B0%88%E6%A5%AD%E7%94%9F%E7%94%A2.pdf)**
- Fallback: [Google: 劉翠溶 明清時代南方地區的專業生產 大陸雜誌](https://www.google.com/search?q=%E5%8A%89%E7%BF%A0%E6%BA%B6+%E6%98%8E%E6%B8%85%E6%99%82%E4%BB%A3%E5%8D%97%E6%96%B9%E5%9C%B0%E5%8D%80%E7%9A%84%E5%B0%88%E6%A5%AD%E7%94%9F%E7%94%A2+%E5%A4%A7%E9%99%B8%E9%9B%9C%E8%AA%8C)
- **Rests on it:** the same pig-sty finding on `archetypes.html` (feature 280 A4). The paper works from Ming-Qing gazetteers on the delta's specialized farming; look for pigs in the dike-pond district, where they were penned, and pig dung fed to fish ponds, with the gazetteer and its date.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, A4 write, 2026-09-29).

### 297. 「江戸の墓制・葬制の考古学的研究」 (Tanigawa, "An archaeological study of Edo burial and funerary practice"), 『人間科学研究』 23-1, Waseda University

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Waseda repository PDF](https://waseda.repo.nii.ac.jp/record/22229/files/NingenKagakuKenkyu_23_1_Tanigawa.pdf)**
- Fallback: [Google: 谷川 江戸の墓制・葬制の考古学的研究 人間科学研究](https://www.google.com/search?q=%E8%B0%B7%E5%B7%9D+%E6%B1%9F%E6%88%B8%E3%81%AE%E5%A2%93%E5%88%B6%E3%83%BB%E8%91%AC%E5%88%B6%E3%81%AE%E8%80%83%E5%8F%A4%E5%AD%A6%E7%9A%84%E7%A0%94%E7%A9%B6+%E4%BA%BA%E9%96%93%E7%A7%91%E5%AD%A6%E7%A0%94%E7%A9%B6)
- **Rests on it:** "Were a town's and a city's burial grounds that size before modern times?" and "How far from its houses does a village bury its dead, and on which side?" on `religion-and-death.html` (diagram feature 280 R4), which find no area for an Edo temple's or village's burial ground and no distance from a village's houses before 1868. Look for any excavated Edo graveyard's area, its count of graves (a density), the population or parish it served, and where a village graveyard lay relative to the houses.
- Blocked by: the repository redirects to object storage and the fetcher got a binary it could not read as a PDF (diagram feature 280, R4 write, 2026-09-29).

### 298. 「本所に埋葬された人々」 ("The people buried in Honjo"), 『みやこどり』 33-2, Sumida ward board of education

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Sumida ward PDF](https://www.city.sumida.lg.jp/kosodate_kyouiku/tiiki_kyouiku_shien/bunkazai_hogo/maizoubunkazai/index.files/miyakodori-33-2.pdf)**
- Fallback: [Google: 本所に埋葬された人々 墓跡発見の端緒 普賢寺遺跡](https://www.google.com/search?q=%E6%9C%AC%E6%89%80%E3%81%AB%E5%9F%8B%E8%91%AC%E3%81%95%E3%82%8C%E3%81%9F%E4%BA%BA%E3%80%85+%E5%A2%93%E8%B7%A1%E7%99%BA%E8%A6%8B%E3%81%AE%E7%AB%AF%E7%B7%92+%E6%99%AE%E8%B3%A2%E5%AF%BA%E9%81%BA%E8%B7%A1)
- **Rests on it:** "How much ground does a village burial ground need, and whose dead lie in it?" on `religion-and-death.html` (diagram feature 280 R4), whose grave density (40 m² holding ten graves, one box coffin and nine barrel coffins, at the Fugenji site in Higashi-Komagata) and the stacked graves at Jojuji in Honjo are quoted from this PDF. A checker saw the page's numbers but could not read its Japanese text; confirm the two quoted passages word for word and the Jojuji placement.
- Blocked by: the fetcher found no Japanese text layer it could read in the PDF (diagram feature 280, R4 check, 2026-09-29).

### 299. 「"无锡"之城探赜」 ("An inquiry into the city of Wuxi"), 无锡日报 (Wuxi Daily), 18 June 2020

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Wuxi Daily page](https://www.wxrb.com/doc/2020/06/18/14929.shtml)**
- Fallback: [Google: 无锡之城探赜 池深二丈 阔七丈](https://www.google.com/search?q=%E6%97%A0%E9%94%A1%E4%B9%8B%E5%9F%8E%E6%8E%A2%E8%B5%9C+%E6%B1%A0%E6%B7%B1%E4%BA%8C%E4%B8%88+%E9%98%94%E4%B8%83%E4%B8%88)
- **Rests on it:** "How wide and deep is a city's moat?" on `cities/defenses.html` (diagram feature 280 C5), which finds a Ming county town's moat (Pingyao, one zhang) and the Ming treatise's floor (three and a half zhang) but no period figure for a larger city's moat. A search summary said this page quotes Wuxi's wall at the end of the Yuan and start of the Ming as nine li round, two zhang high, its moat two zhang deep and seven zhang wide. Quote that passage word for word, with the record it cites and its date.
- Blocked by: the site's TLS connection closed on every fetch (diagram feature 280, C5 write, 2026-09-29).

### 300. 王世礼、胡丹「明代云南府州县治城池的规模等级与分布」 (Wang Shili and Hu Dan, "The scale, rank and distribution of the walled seats of Ming Yunnan"), 2024

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[journal PDF](https://www.jgcm.ac.cn/jah/cn/article/pdf/preview/10.12329/20969368.2024.02014.pdf)**
- Fallback: [Google: 明代云南府州县治城池的规模等级与分布 王世礼 胡丹](https://www.google.com/search?q=%E6%98%8E%E4%BB%A3%E4%BA%91%E5%8D%97%E5%BA%9C%E5%B7%9E%E5%8E%BF%E6%B2%BB%E5%9F%8E%E6%B1%A0%E7%9A%84%E8%A7%84%E6%A8%A1%E7%AD%89%E7%BA%A7%E4%B8%8E%E5%88%86%E5%B8%83+%E7%8E%8B%E4%B8%96%E7%A4%BC+%E8%83%A1%E4%B8%B9)
- **Rests on it:** the same moat question on `cities/defenses.html` (feature 280 C5). The paper tabulates the Ming gazetteer *Dian zhi*'s figures for Yunnan's prefectural, departmental and county walls; look for any moat (池, 濠) width or depth by rank, which would give the period figure the band lacks for a prefectural seat.
- Blocked by: the fetcher found no text layer it could read in the PDF (diagram feature 280, C5 write, 2026-09-29).

### 301. Aichi Prefectural Library, old-book collection, item 143 (the reviewer's page on Ieyasu's testament in a hundred articles, 御遺状百ヶ条)

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Aichi Prefectural Library page](https://websv.aichi-pref-library.jp/wahon/detail/143.html)**
- Fallback: [Google: 愛知県図書館 和本 御遺状百ヶ条](https://www.google.com/search?q=%E6%84%9B%E7%9F%A5%E7%9C%8C%E5%9B%B3%E6%9B%B8%E9%A4%A8+%E5%92%8C%E6%9C%AC+%E5%BE%A1%E9%81%BA%E7%8A%B6%E7%99%BE%E3%83%B6%E6%9D%A1)
- **Rests on it:** "What was a village lane surfaced with, and does it show?" and "What vehicle used a village lane, and how wide was it?" on `ways.html` (diagram feature 291 R10), which give the field road's 3-shaku width as a figure from the testament and rest its standing on two English sources. A settlement-review read this page as saying the testament is a later forgery; quote its words on the testament's authorship and date, in Japanese.
- Blocked by: the host's TLS certificate does not match its name, and the www. host returns 404 for the same path (diagram feature 291, R10 write, 2026-09-30).

### 302. 『小平市史』 ("Kodaira City History"), the page on the Mawarita Shinden (回田新田) farmstead's yard

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kodaira library digital archive page](https://adeac.jp/kodaira-lib/text-list/d100010/ht002170)**
- Fallback: [Google: 小平市史 回田新田 庭 七十坪](https://www.google.com/search?q=%E5%B0%8F%E5%B9%B3%E5%B8%82%E5%8F%B2+%E5%9B%9E%E7%94%B0%E6%96%B0%E7%94%B0+%E5%BA%AD+%E4%B8%83%E5%8D%81%E5%9D%AA)
- **Rests on it:** "Threshing and drying yards at farmhouses (niwa)" on `homesteads.html` (diagram feature 292). An early pass (2026-08-28) recorded this page as giving the one directly measured farm yard: about 70 tsubo (約七十坪, 231 sq m) of swept working ground inside a 700-tsubo homestead, a large Musashino dry-field holding. No later pass could read it, so the figure was taken out of the record. If the page says it, quote the passage word for word, in Japanese, and it goes back in.
- Blocked by: the archive serves a page viewer that loads its text by script; every fetch got the viewer shell and no text (diagram features 195 and 292, 2026-09-06 and 2026-09-30).

### 303. 金沢市『寺町台伝統的建造物群保存地区保存計画』 ("Kanazawa Teramachidai preservation district plan"), the shrine entries

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Kanazawa city digital library PDF](https://digilib.city.kanazawa.ishikawa.jp/preview/pdf/FXHmogAAA)** (catalogue page: https://digilib.city.kanazawa.ishikawa.jp/doc/89/)
- Fallback: [Google: 寺町台伝統的建造物群保存地区保存計画 諏訪神社 泉野菅原神社](https://www.google.com/search?q=%E5%AF%BA%E7%94%BA%E5%8F%B0%E4%BC%9D%E7%B5%B1%E7%9A%84%E5%BB%BA%E9%80%A0%E7%89%A9%E7%BE%A4%E4%BF%9D%E5%AD%98%E5%9C%B0%E5%8C%BA%E4%BF%9D%E5%AD%98%E8%A8%88%E7%94%BB+%E8%AB%8F%E8%A8%AA%E7%A5%9E%E7%A4%BE+%E6%B3%89%E9%87%8E%E8%8F%85%E5%8E%9F%E7%A5%9E%E7%A4%BE)
- **Rests on it:** "Shrines in towns and cities" on `religion-and-death.html` and its rendering section (diagram feature 292), notes kanazawa-teramachidai-plan-9 and -10: the Suwa shrine's composite hall, shrine office and Inari subsidiary shrine, and the Izuno-Sugawara shrine taking the west side of a temple's precinct. Five quotations (諏訪神社は明治末期の再建で…, 社殿 １棟, 社務所 １棟, 稲荷社 １棟, 泉野菅原神社は玉泉寺天満宮と称され…) have not been checked character for character against the page.
- Blocked by: the PDF is over the 10 MB fetch limit; the catalogue page has no text of its own (diagram feature 292, religion-and-death G07 check, 2026-09-30).

### 304. Kenneth Ruddle and Gongfu Zhong, *Integrated Agriculture-Aquaculture in South China: The Dike-Pond System of the Zhujiang Delta* (Cambridge University Press), 1988

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Internet Archive search](https://archive.org/search?query=Ruddle+Zhong+dike-pond+Zhujiang+delta)**
- Fallback: [Google: Ruddle Zhong Integrated Agriculture-Aquaculture in South China dike-pond](https://www.google.com/search?q=Ruddle+Zhong+%22Integrated+Agriculture-Aquaculture+in+South+China%22+dike-pond)
- **Rests on it:** "Dike-ponds: fish ponds ringed by mulberry dikes (sangji yutang)" on `archetypes.html` (diagram feature 292). An earlier pass said, from search summaries, that this book has a pond on sloping ground plumbed inlet-high and outlet-low, so water flows downhill through it, and the whole dike-pond network running in series from a high intake to a low outfall; that claim was taken out because no one has read the book. If it says so, quote the passage word for word, with its page, and say whether it describes the system before 1949 or as the authors found it. The pages on how wide a pond's dike was, and what stood on it, are wanted too.
- Blocked by: a print monograph with no readable copy found; Cambridge's pages and the GeoJournal paper (BF00645312) return 403 or a login wall (diagram features 195 and 292, 2026-09-06 and 2026-10-01).

### 305. Baidu Baike, 县衙 ("County yamen"), the encyclopedia entry

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike page](https://baike.baidu.com/item/%E5%8E%BF%E8%A1%99/946005)**
- Fallback: [Google: 百度百科 县衙 946005](https://www.google.com/search?q=%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91+%E5%8E%BF%E8%A1%99+946005)
- **Rests on it:** "Servants in a samurai household: where they sleep and how they were hired (hokonin)" on `cities/government.html` (diagram feature 292), the absence note on how a Chinese county office's clerks were lodged. Quote, in Chinese, any passage on where the clerks (书吏, 胥吏) or runners lodged - a clerks' lodging (吏舍, 公廨房) and where in the yamen it stood - and any figure for a county yamen's area or room count.
- Blocked by: Baidu's security check; the WebFetch tool and curl with a browser user agent both get 403 and the "百度安全验证" page (diagram, an earlier pass on 2026-09-12, and feature 292, 2026-10-01).

### 306. Baidu Baike, 平遥县衙 ("Pingyao county yamen"), the encyclopedia entry

- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found
- [ ] Found elsewhere (only with downloaded or partial) - where:
- Saved as (optional, the file's name):

- **[Baidu Baike page](https://baike.baidu.com/item/%E5%B9%B3%E9%81%A5%E5%8E%BF%E8%A1%99/2409876)**
- Fallback: [Google: 百度百科 平遥县衙 2409876](https://www.google.com/search?q=%E7%99%BE%E5%BA%A6%E7%99%BE%E7%A7%91+%E5%B9%B3%E9%81%A5%E5%8E%BF%E8%A1%99+2409876)
- **Rests on it:** the same absence note on `cities/government.html` (diagram feature 292): an early pass (2026-08-28) took from this entry, unfetched, a clerks' lodging (公廨房) built behind the west office range in 1619 and a yamen about 200 by 100 m; the registry entry `pingyao-yamen` stays *Not cited* until someone reads it. If the entry says so, quote the passages word for word, in Chinese.
- Blocked by: Baidu's security check; the WebFetch tool and curl with a browser user agent both get 403 and the "百度安全验证" page (diagram features 195 and 292, 2026-08-28 and 2026-10-01).

# High-risk sources: download before feature 312 can close

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

- **[The cited page](https://museumcollection.tokyo/works/6531424/)**
- Fallback: [Google: Tokyo Museum Collection (ToMuCo), "炭俵" (charcoal bale), Edo-Tokyo Museum accessi](https://www.google.com/search?q=Tokyo%20Museum%20Collection%20%28ToMuCo%29%2C%20%22%E7%82%AD%E4%BF%B5%22%20%28charcoal%20bale%29%2C%20Edo-Tokyo%20Museum%20accession%2090007940)
- **Rests on it:** "How our maps draw straw bales of rice and charcoal (tawara)" (`research/questions/0199-straw-bales-of-rice-and-charcoal-tawara.drawing.html`); "Straw bales of rice and charcoal (tawara)" (`research/questions/0199-straw-bales-of-rice-and-charcoal-tawara.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 through WebFetch by a source-reader (feature 267); the host refuses the container's own fetch (403)
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H2. IRRI Rice Knowledge Bank, sun drying and drying-floor area (`irri-drying-floor`)

- **[The cited page](http://web.archive.org/web/20230624043456/http://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm)**
- Fallback: [Google: IRRI Rice Knowledge Bank, sun drying and drying-floor area](https://www.google.com/search?q=IRRI%20Rice%20Knowledge%20Bank%2C%20sun%20drying%20and%20drying-floor%20area)
- **Rests on it:** "How our maps draw threshing and drying yards (niwa)" (`research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html`); "Threshing and drying yards at farmhouses (niwa)" (`research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at http://web.archive.org/web/20230624043456/http://www.knowledgebank.irri.org/grainQuality/module_4/popups/pu_drying.htm (feature 195) | READ 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 429 (feature 309).

### H3. Storozum et al., "Geoarchaeological evidence of the AD 1642 Yellow River flood that destroyed Kaifeng", Scientific Reports 2020 (PMC 7048742) (`kaifeng-pmc7048742`)

- **[The cited page](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7048742/)**
- Fallback: [Google: Storozum et al., "Geoarchaeological evidence of the AD 1642 Yellow River flood t](https://www.google.com/search?q=Storozum%20et%20al.%2C%20%22Geoarchaeological%20evidence%20of%20the%20AD%201642%20Yellow%20River%20flood%20that%20destroyed%20Kaifeng%22%2C%20Scientific%20Repor)
- **Rests on it:** "Cities on rivers" (`research/questions/0175-cities-on-rivers.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7048742/ (feature 195) | READ 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H4. L5R Wiki (Fandom), "Seidō" (`l5r-fandom-seido`)

- **[The cited page](https://l5r.fandom.com/wiki/Seid%C5%8D)**
- Fallback: [Google: L5R Wiki (Fandom), "Seidō"](https://www.google.com/search?q=L5R%20Wiki%20%28Fandom%29%2C%20%22Seid%C5%8D%22)
- **Rests on it:** "How our maps draw a village shrine's monk, the monk's dwelling (kuri), its records and its land" (`research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 272), from the page's wikitext as the site's public MediaWiki API returns it, fetched with curl; the page itself refuses automated fetches (403) and opens in a browser
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H5. "Drought characteristics and their impact on vegetation net primary productivity in the climate-sensitive transition zone", PLOS ONE (2026), doi 10.1371/journal.pone.0343746 (`plos-transition-zone-drought`)

- **[The cited page](https://pmc.ncbi.nlm.nih.gov/articles/PMC12935246/)**
- Fallback: [Google: "Drought characteristics and their impact on vegetation net primary productivity](https://www.google.com/search?q=%22Drought%20characteristics%20and%20their%20impact%20on%20vegetation%20net%20primary%20productivity%20in%20the%20climate-sensitive%20transition%20zon)
- **Rests on it:** "How our maps place and draw wells (ido)" (`research/questions/0196-communal-wells-ido.drawing.html`); "Communal wells (ido)" (`research/questions/0196-communal-wells-ido.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12 in full through PubMed Central; open access
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H6. Kojima Nobuyasu, 「How the acting superintendent of Sensoji was appointed in the late early-modern period」 (translated; original: 「近世後期における浅草寺別当代の就任過程」), Soka University institutional repository (`kojima-sensoji-bettodai`)

- **[The cited page](https://soka.repo.nii.ac.jp/record/35917/files/sokahogaku28_1_2.pdf)**
- Fallback: [Google: Kojima Nobuyasu, 「How the acting superintendent of Sensoji was appointed in the ](https://www.google.com/search?q=Kojima%20Nobuyasu%2C%20%E3%80%8CHow%20the%20acting%20superintendent%20of%20Sensoji%20was%20appointed%20in%20the%20late%20early-modern%20period%E3%80%8D%20%28translated%3B%20o)
- **Rests on it:** "City temples: their precincts, buildings and monks (garan)" (`research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 272 B37); fetched with curl and read through pdftotext, the fetch tool returning only the PDF's bytes
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 406 (feature 309).

### H7. Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Green, Northampton", Post-Medieval Archaeology 30(1), 1996 (`northampton-tannery-1996`)

- **[The cited page](https://doi.org/10.1179/pma.1996.002)**
- Fallback: [Google: Shaw, "The excavation of a late 15th- to 17th-century tanning complex at The Gre](https://www.google.com/search?q=Shaw%2C%20%22The%20excavation%20of%20a%20late%2015th-%20to%2017th-century%20tanning%20complex%20at%20The%20Green%2C%20Northampton%22%2C%20Post-Medieval%20Archaeol)
- **Rests on it:** "How our maps site tanning yards" (`research/questions/0193-tanning-yards.drawing.html`); "Tanning yards" (`research/questions/0193-tanning-yards.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12: the publisher's abstract, which the DOI address serves to a reader in a browser and which the OpenAlex public API republishes in full as an inverted index, reconstructed here and checked for gaps; the article body is closed - Unpaywall and OpenAlex both report no open copy, and the publisher's own page and the Ingenta copy refuse every automated client
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

## Tier 2 - no claim rests on it (8)

No footnote cites these: each is kept as a record of what was searched, or named only in an absence note that already says
it could not be read. What could be wrong is the registry entry's own description of the source.

### H8. Kushiro Mire alder invasion, Ecohydrology & Hydrobiology 2014 (`kushiro-mire-2014`)

- **[The cited page](https://www.sciencedirect.com/science/article/abs/pii/S1642359314000706)**
- Fallback: [Google: Kushiro Mire alder invasion, Ecohydrology & Hydrobiology 2014](https://www.google.com/search?q=Kushiro%20Mire%20alder%20invasion%2C%20Ecohydrology%20%26%20Hydrobiology%202014)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** READ 2026-08-26 - abstract | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H9. Studies in Chinese Religions 5(2), "Giving while keeping: inexhaustible treasuries and inalienable wealth in medieval China" (`inexhaustible-treasuries`)

- **[The cited page](https://doi.org/10.1080/23729988.2019.1639463)**
- Fallback: [Google: Studies in Chinese Religions 5(2), "Giving while keeping: inexhaustible treasuri](https://www.google.com/search?q=Studies%20in%20Chinese%20Religions%205%282%29%2C%20%22Giving%20while%20keeping%3A%20inexhaustible%20treasuries%20and%20inalienable%20wealth%20in%20medieval%20Ch)
- **Rests on it:** no claim - it is named only in an absence note on "Temple clergy, their families, and how a temple earned its keep" (`research/questions/0232-temple-clergy-their-families-and-how-a-temple-earned-its-keep.html`), which already says it could not be read.
- **How it was read before (the entry's own notes):** unfetched 2026-08-28 | 2026-09-06, feature 195 | the entry stays as the record of what was searched. 2026-09-27 (feature 272 T): the author is Neil Schmid (Crossref); the ResearchGate copy and the publisher's page both return 403 to curl; on the GM's TO-DOWNLOAD list. The treasury and the 713 order are now cited to wujinzang-zhwiki; the MOTIVE of the order rests on this paper alone
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H10. Baidu Baike, 村庙 (village temple) (`cunmiao-baike`)

- **[The cited page](https://baike.baidu.com/item/%E6%9D%91%E5%BA%99/3494869)**
- Fallback: [Google: Baidu Baike, 村庙 (village temple)](https://www.google.com/search?q=Baidu%20Baike%2C%20%E6%9D%91%E5%BA%99%20%28village%20temple%29)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** SUMMARY-ONLY (2026-09-27); the page refused the fetch with HTTP 403 | 2026-09-27, feature 268 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H11. Kinoshita, "Household Size, Household Structure, and Developmental Cycle of a Japanese Village: Eighteenth to Nineteenth Centuries", Journal of Family History 20(3), 1995 (`kinoshita-1995`)

- **[The cited page](https://journals.sagepub.com/doi/abs/10.1177/036319909502000302)**
- Fallback: [Google: Kinoshita, "Household Size, Household Structure, and Developmental Cycle of a Ja](https://www.google.com/search?q=Kinoshita%2C%20%22Household%20Size%2C%20Household%20Structure%2C%20and%20Developmental%20Cycle%20of%20a%20Japanese%20Village%3A%20Eighteenth%20to%20Nineteenth)
- **Rests on it:** no claim - it is named only in an absence note on "The five sizes of settlement: hamlet, village, town, provincial city and capital" (`research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html`), which already says it could not be read.
- **How it was read before (the entry's own notes):** unsupported by any readable page - HTTP 403 on one attempt, 2026-08-29 | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H12. G. William Skinner, Marketing and Social Structure in Rural China (1964-65) - consulted at secondhand via retrospectives and reviews (`skinner-marketing`)

- **[The cited page](https://doi.org/10.2307/2050412)**
- Fallback: [Google: G. William Skinner, Marketing and Social Structure in Rural China (1964-65) - co](https://www.google.com/search?q=G.%20William%20Skinner%2C%20Marketing%20and%20Social%20Structure%20in%20Rural%20China%20%281964-65%29%20-%20consulted%20at%20secondhand%20via%20retrospectives)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H13. Steven B. Miles, "From Small Fry to Big Fish: Representing the Rise of Jiujiang Township, Nanhai County, 1395-1657", Ming Studies 48 (2003) (`miles-2003`)

- **[The cited page](https://doi.org/10.1179/014703703788762953)**
- Fallback: [Google: Steven B. Miles, "From Small Fry to Big Fish: Representing the Rise of Jiujiang ](https://www.google.com/search?q=Steven%20B.%20Miles%2C%20%22From%20Small%20Fry%20to%20Big%20Fish%3A%20Representing%20the%20Rise%20of%20Jiujiang%20Township%2C%20Nanhai%20County%2C%201395-1657%22%2C%20Min)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unsupported by any readable page (paywalled; the search summary gives the subject: the township's rise on the fish-fry trade in Ming Nanhai) | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H14. Qing local-government scholarship on the 六房三班 ("Six Bureaus and Three Bands", title translated) organization; Pingyao county yamen documentation (`liufang-yamen`)

- **[The cited page](https://zhuanlan.zhihu.com/p/660442182)**
- Fallback: [Google: Qing local-government scholarship on the 六房三班 ("Six Bureaus and Three Bands", ti](https://www.google.com/search?q=Qing%20local-government%20scholarship%20on%20the%20%E5%85%AD%E6%88%BF%E4%B8%89%E7%8F%AD%20%28%22Six%20Bureaus%20and%20Three%20Bands%22%2C%20title%20translated%29%20organization%3B%20Pingyao%20co)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unfetched 2026-08-28
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

### H15. Diversion-angle hydraulics (a 30° angle cutting sediment entry by up to 64%; no paper read) (`offtake-angle-studies`)

- **[The cited page](https://www.sciencedirect.com/science/article/abs/pii/S1001627920300706)**
- Fallback: [Google: Diversion-angle hydraulics (a 30° angle cutting sediment entry by up to 64%; no ](https://www.google.com/search?q=Diversion-angle%20hydraulics%20%28a%2030%C2%B0%20angle%20cutting%20sediment%20entry%20by%20up%20to%2064%25%3B%20no%20paper%20read%29)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** unsupported by any readable page 2026-08-28: search syntheses of several ResearchGate / ScienceDirect papers - "maximum water discharge and minimum sediment discharge when its diversion angle was 30° or 45° among 90°, 75°, 60°, 45°, and 30°"; unfetched 2026-08-28 | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - partial HTTP 403 (feature 309).

## Unreachable cited sources (7)

The cited URLs the archive found unreachable, retried 2026-10-02 (see each).

### H16. 陈朝云 / 张晓芊, 「A study of Song-dynasty louzeyuan (漏泽园, the pauper burial grounds) and of social relief」 (translated; original: 「宋代漏泽园及社会救助研究」), 史学月刊 (Henan University), the journal's own listing page - 「The name "louzeyuan" is first seen in the third year of the Chongning era of Emperor Huizong of Song (1104).」 (translated; original: 「"漏泽园"名称始见于宋徽宗崇宁三年（1104年）」) (`shixue-yuekan-louzeyuan`)

- **[The cited page](https://sxyk.henu.edu.cn/info/1014/7333.htm)**
- Fallback: [Google: 陈朝云 / 张晓芊, 「A study of Song-dynasty louzeyuan (漏泽园, the pauper burial grounds) a](https://www.google.com/search?q=%E9%99%88%E6%9C%9D%E4%BA%91%20/%20%E5%BC%A0%E6%99%93%E8%8A%8A%2C%20%E3%80%8CA%20study%20of%20Song-dynasty%20louzeyuan%20%28%E6%BC%8F%E6%B3%BD%E5%9B%AD%2C%20the%20pauper%20burial%20grounds%29%20and%20of%20social%20relief%E3%80%8D%20%28translated%3B%20origin)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** abstract READ 2026-09-06, the CNKI full text behind a paywall
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H17. 刘炜, 黄茜, 徐腾, "A study of the building of mid-Northern-Song military cities based on the Wujing zongyao" (title translated; original: 「基于《武经总要》的北宋中期军事城池营建研究」), 『建筑史学刊』 (Journal of Architectural History) 2026(2): 122-132 (`jah-song-military-cities`)

- **[The cited page](https://www.jgcm.ac.cn/jah/cn/article/pdf/preview/10.12329/20969368.2026.02011.pdf)**
- Fallback: [Google: 刘炜, 黄茜, 徐腾, "A study of the building of mid-Northern-Song military cities based ](https://www.google.com/search?q=%E5%88%98%E7%82%9C%2C%20%E9%BB%84%E8%8C%9C%2C%20%E5%BE%90%E8%85%BE%2C%20%22A%20study%20of%20the%20building%20of%20mid-Northern-Song%20military%20cities%20based%20on%20the%20Wujing%20zongyao%22%20%28title%20translated)
- **Rests on it:** "How our maps space and draw wall towers" (`research/questions/0148-towers-along-the-city-wall-mamian.drawing.html`); "Towers along the city wall (mamian)" (`research/questions/0148-towers-along-the-city-wall-mamian.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12; the journal serves the article PDF openly, and its passages were taken from the PDF's own text layer rather than from a page image. The paper is set in two columns, so a sentence is reflowed across them and each fragment was checked separately
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H18. History of Irrigation - irrigation tools (URL: none - the page it was read at, irripro.net, is gone) with Baidu Baike Lulu (a weaker reference) (`irripro-jiegao-lulu`)

- **[The cited page](http://www.irripro.net/en/nd.jsp?id=113)**
- Fallback: [Google: History of Irrigation - irrigation tools (URL: none - the page it was read at, i](https://www.google.com/search?q=History%20of%20Irrigation%20-%20irrigation%20tools%20%28URL%3A%20none%20-%20the%20page%20it%20was%20read%20at%2C%20irripro.net%2C%20is%20gone%29%20with%20Baidu%20Baike%20Lu)
- **Rests on it:** no claim - no footnote cites it; its registry entry is kept as the record of what was searched.
- **How it was read before (the entry's own notes):** READ 2026-08 at http://www.irripro.net/en/nd.jsp?id=113, which returns 404 to every client as of 2026-09-12 and has no Internet Archive capture, so the pointer is unrecoverable rather than blocked | 2026-09-06, feature 195 | the entry stays as the record of what was searched
- Blocked by: the archive's retry on 2026-10-02 - unreachable - HTTP 404 (feature 309).

### H19. 旅色 (Tabiiro, a travel guide), 高山陣屋 ("Takayama Jin'ya", title translated) (`tabiiro-takayama-jinya`)

- **[The cited page](https://tabiiro.jp/leisure/s/200247-takayama-takayamajinya/)**
- Fallback: [Google: 旅色 (Tabiiro, a travel guide), 高山陣屋 ("Takayama Jin'ya", title translated)](https://www.google.com/search?q=%E6%97%85%E8%89%B2%20%28Tabiiro%2C%20a%20travel%20guide%29%2C%20%E9%AB%98%E5%B1%B1%E9%99%A3%E5%B1%8B%20%28%22Takayama%20Jin%27ya%22%2C%20title%20translated%29)
- **Rests on it:** "How our maps draw the Imperial Magistrate's compound" (`research/questions/0114-the-imperial-magistrates-compound-in-a-capital.drawing.html`); "The Imperial Magistrate's compound in a capital" (`research/questions/0114-the-imperial-magistrates-compound-in-a-capital.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-27 by a source-reader (feature 271)
- Blocked by: the archive's retry on 2026-10-02 - unreachable - HTTP 404 (feature 309).

### H20. 陈凌 (Chen Ling), 建筑空间与礼制文化：宋代地方衙署建筑象征性功能诠释 ("Architectural Space and Ritual-System Culture: An Interpretation of the Symbolic Function of Song-Dynasty Local Yamen Architecture", title translated), 西南大学学报（社会科学版） ("Journal of Southwest University (Social Science Edition)", title translated) 42(5): 182-187, September 2016 (`chen-2016-song-yamen`)

- **[The cited page](https://xbgjxt.swu.edu.cn/data/article/preview-pdf?doi=10.13718/j.cnki.xdsk.2016.05.023)**
- Fallback: [Google: 陈凌 (Chen Ling), 建筑空间与礼制文化：宋代地方衙署建筑象征性功能诠释 ("Architectural Space and Ritual-Syste](https://www.google.com/search?q=%E9%99%88%E5%87%8C%20%28Chen%20Ling%29%2C%20%E5%BB%BA%E7%AD%91%E7%A9%BA%E9%97%B4%E4%B8%8E%E7%A4%BC%E5%88%B6%E6%96%87%E5%8C%96%EF%BC%9A%E5%AE%8B%E4%BB%A3%E5%9C%B0%E6%96%B9%E8%A1%99%E7%BD%B2%E5%BB%BA%E7%AD%91%E8%B1%A1%E5%BE%81%E6%80%A7%E5%8A%9F%E8%83%BD%E8%AF%A0%E9%87%8A%20%28%22Architectural%20Space%20and%20Ritual-System%20Culture%3A%20An%20Interpretation%20of%20the%20Symb)
- **Rests on it:** "How our maps place and draw the governor's compound (yamen)" (`research/questions/0163-the-provincial-governments-seat-the-governors-compound-and-where-it-stands-yamen.drawing.html`); "The provincial government's seat: the governor's compound and where it stands (yamen)" (`research/questions/0163-the-provincial-governments-seat-the-governors-compound-and-where-it-stands-yamen.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-14 by a source-reader (feature 242)
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H21. 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿） (Preliminary design report for the 2026 high-standard farmland improvement and upgrading construction project, Conghua District, Guangzhou; client the Conghua District Bureau of Agriculture and Rural Affairs, designer 中联合创设计有限公司 ("Zhonglian Hechuang Design Co., Ltd.", translated)), June 2026 (`conghua-2026-design`)

- **[The cited page](http://nyncj.gz.gov.cn/attachment/8/8037/8037125/10854794.pdf)**
- Fallback: [Google: 2026 年度广州市从化区高标准农田改造提升建设项目初步设计报告（评审稿） (Preliminary design report for the 2026 hi](https://www.google.com/search?q=2026%20%E5%B9%B4%E5%BA%A6%E5%B9%BF%E5%B7%9E%E5%B8%82%E4%BB%8E%E5%8C%96%E5%8C%BA%E9%AB%98%E6%A0%87%E5%87%86%E5%86%9C%E7%94%B0%E6%94%B9%E9%80%A0%E6%8F%90%E5%8D%87%E5%BB%BA%E8%AE%BE%E9%A1%B9%E7%9B%AE%E5%88%9D%E6%AD%A5%E8%AE%BE%E8%AE%A1%E6%8A%A5%E5%91%8A%EF%BC%88%E8%AF%84%E5%AE%A1%E7%A8%BF%EF%BC%89%20%28Preliminary%20design%20report%20for%20the%202026%20high-standard%20farmland%20improvement%20and%20upg)
- **Rests on it:** "How wide canals and ditches are: the ladder of channel widths" (`research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-12, fetched with curl and a browser user agent, HTTP 200, 23,291,315 bytes, text layer intact; served openly by the district bureau
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Timeout 60000ms exceeded. (feature 309).

### H22. The Shunde (顺德) dike-pond figures: 40,084 mu of ponds in 1581 (万历九年) and 58,094 mu in 1642 - 广州日报 and the Shunde Archives timeline; the 4.6% / 6.7% shares are those figures over the 8,700 顷 (870,000 mu) of cultivated land 吴建新 gives from 广东通志 ; 「By the end of the Guangxu era, the grain fields within the county made up less than one tenth of the total cultivated area, most of it having become fish ponds.」 (translated; original: 「至光绪末年，县境禾田占总耕地面积不到十分之一，大部分成为鱼塘」); the late-1980s survey - the main dyke-pond area 86,632 ha, 35% fishponds, 25% irrigated rice; the 1581 taxable fishponds of Nanhai, Shunde and Panyu, ~160,000 mu, from 珠江三角洲农业志. Longshan (龙山) had 8,124 of 44,947 mu in ponds in 1581, 18%; "over half" (75%, 乡之塘倍于田) is the Qianlong-Jiaqing figure; (`wanli-fishpond-summary`)

- **[The cited page](https://gzdaily.dayoo.com/h5/html5/2023-07/05/content_871_829964.htm)**
- Fallback: [Google: The Shunde (顺德) dike-pond figures: 40,084 mu of ponds in 1581 (万历九年) and 58,094 ](https://www.google.com/search?q=The%20Shunde%20%28%E9%A1%BA%E5%BE%B7%29%20dike-pond%20figures%3A%2040%2C084%20mu%20of%20ponds%20in%201581%20%28%E4%B8%87%E5%8E%86%E4%B9%9D%E5%B9%B4%29%20and%2058%2C094%20mu%20in%201642%20-%20%E5%B9%BF%E5%B7%9E%E6%97%A5%E6%8A%A5%20and%20the%20Shunde%20Archive)
- **Rests on it:** "How our maps lay cash crops over a village's rice land" (`research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html`); "Cash crops on rice land: dike-ponds, lotus fields and tea rows" (`research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.html`).
- **How it was read before (the entry's own notes):** READ 2026-09-06 at https://www.163.com/dy/article/D4OSJLAR0514D0GJ.html (feature 195) | verified on readable pages 2026-08-28 | derived, not read as such | contradicted and struck: the record had said over half | the 1581 wording traced to an uncited blog copied into zh.wikipedia 基塘农业 | feature 134 T48, after the GM asked whether the pointer was hallucinated
- Blocked by: the archive's retry on 2026-10-02 - unreachable - Client network socket disconnected before secure TLS connection was established (feature 309).

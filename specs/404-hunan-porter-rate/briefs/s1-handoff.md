# Session 1 handoff - feature 404 (0260)

- SECTION=0260/what-did-hiring-a-horse-or-a-porter-cost (`research/questions/0260-what-did-hiring-a-horse-or-a-porter-cost.html`, the "China" subsection)
- New registry key: `hunan-wuliao-jiazhi-zeli` (`research/sources/010-works-cited/33770-hunan-wuliao-jiazhi-zeli.html`; https://commons.wikimedia.org/wiki/File:SSID-11354707_欽定物料價值則例_第1卷.pdf; the page and the PDF archived)
- New notes: `hunan-wuliao-jiazhi-zeli`, `-2`, `-3`, `bochum-zhili-wuliao-jiazhi-3`, `hunan-date-arithmetic`, `hunan-porter-arithmetic`; rewritten: `qing-fare-absence`

## Figures and verdicts, old -> new

- Official Qing porter rate: old SILENT (Zhili's unit unsettled) -> new ATTESTED ONLY FOR official building-work reimbursement in Hunan, Changsha and Shanhua counties: 夫運捌拾斤每里銀叁釐, 0.003 tael a li for 80 jin (PDF p. 38), under the memorial presented 乾隆三十三年十二月二十日 (p. 12; early 1769 by this project's arithmetic).
- Official Qing boat rate: old SILENT -> new ATTESTED ONLY FOR the same: 船運壹百斤每拾里銀貳釐, 0.002 tael every 10 li for 100 jin (p. 39).
- Day wages beside them: new ATTESTED ONLY FOR the same, same page (p. 38): 匠每工銀肆分, craftsman 0.04 tael a workday; 夫每名銀叁分, laborer 0.03 tael a man (read as a man's day, as the Zhili database reads 名).
- Porter's 100 li: new 0.3 tael = 10 laborer-days = 7.5 craftsman-days; boat's 100 li for 100 jin: 0.02 tael = 0.67 laborer-day (this project's arithmetic).
- Zhili (Tianjin districts) porter, pack-animal and boat rates: old SILENT, "unit unsettled" -> still SILENT, left out; the absence note now names the search (no public scan of the Zhili original; Tsinghua's copy is the one the database transcribes; NLC, Internet Archive, Commons, National Archives of Japan), and a new citation quotes the Bochum chapter 13 rows for Qingxian, 28b (車運, 船運 labeled 里) against 29a (馬騾驢馱運, 夫運 labeled 百里). No unit chosen for Zhili.
- Official pack-animal rate: old SILENT -> still SILENT: Hunan's Changsha rows are two items only (以上貳欵), Zhili's left out.
- Retries: Moll-Murata, Song and Vogel (eds.), *Chinese Handicraft Regulations of the Qing Dynasty* (2005) - Google Books API 429 (daily quota) and the web search a script redirect; HathiTrust full-text and catalog searches for 物料價值則例 - Cloudflare 403. Failed in feature 404's pass and again in this session, both 2026-10-19; outcomes recorded `unreadable`.
- Leads still open: the Jiangsu edition (National Archives of Japan, 内閣文庫); the Hunan edition's chapters 2-8 on Commons (SSID-11354708 to -10); the 2005 volume.

## Checks

- source-reader run in session 1: `hunan-wuliao-jiazhi-zeli` bundle 11 READ (page images pp. 1, 12, 24, 27, 38, 39); `bochum-zhili-wuliao-jiazhi` bundle 2 READ (the chapter 13 transport rows, read with xlrd, added to the bundle as `pages/ch13-transport-rows.txt`); both recorded.
- Its remarks for session 2: the p. 12 decree runs on, 知道了准其議叙欽此 - the note quotes only to 知道了 (complete as quoted); 册 or 冊: re-read at 400 dpi in this session, the print has two separate frames, 册, as the notes write it. The date: 乾隆三十三年十二月二十日 = 27 January 1769 by new moons computed with PyEphem (the grounds note `hunan-date-arithmetic` gives the working); the prose says "early 1769". Outside the change: the Bochum registry entry says "per li in the districts around it", exact for Jinghai, Cangzhou and Nanpi but Qingxian mixes the labels.
- Still owed (session 2): quote-check, translation-check (three Hunan notes), record-format (0260), source-applicability (`hunan-wuliao-jiazhi-zeli`).

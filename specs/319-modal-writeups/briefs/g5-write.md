# Brief - feature 319, G5: who kept a village's shelter grove, and what it looked like. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**Why.** The windbreak forest's map modal is being rewritten to answer what a reader asks of it: what it was and for whom, what
it looked like, how big. The record (0071 the southern Chinese village's fengshui woods; 0072 shelter belts on a village's
windward side) answers where the groves stood, what they were planted with and their size. It does not say who owned, kept and
protected a VILLAGE grove, what a village could take from it, how tall and dense it stood, or what its keepers said it was for.

**What a research pass found** (a sonnet agent, 2026-10-04, fetching raw pages with curl and pdftotext; read each page yourself
before you cite it - `make archive-find` first, then `make source-pages`, then the `source-reader` agent from a bundle on every
passage you will quote, in the FOREGROUND; the translations below are the pass's and must be your own, marked as translations):

- 卞利《明清时期徽州森林保护禁碑研究》 (Anhui University Huizhou Studies Centre), open PDF at
  `https://crlhd.xmu.edu.cn/virtual_attach_file.vsb?...oid=2097398489&tid=1037&nid=5175&e=.pdf` (find the full URL by
  searching the title; the pass reached it from a first search result). Ming-Qing Huizhou village and lineage groves (water
  mouth, dragon hill, tomb shade), thirty steles mostly Qianlong to Daoguang. Passages:
  - Wangkou village stele, 1785: 「乡聚族而居，前籍向山以为屏障，但拱对逼近削石巉岩，若不栽培，多主凶祸。以故历来掌养树木，垂荫森森。…」 and, after stealthy cutting since 1778, 「酌立条规，重行封禁，永远毋得入山残害」 - the lineage's screen hill, kept planted against misfortune; the hill closed again by agreed rules.
  - Wentang Chen lineage covenant, 1572: 「本里宅墓来龙朝山水口，皆祖宗血脉，山川形胜所关，各家宜戒谕长养林木，以卫形胜，毋得泥为己业，掘损盗砍。犯者，公同众罚理治。」 - the groves not anyone's own; offenders fined by the assembly.
  - Yeyuan village stele, 1813, Qimen: 「一、坟林水口庇木，毋许砍斫，违者，罚戏一部。倘风吹雪压，鸣众公取。或正用，告众采取。」 - no cutting; the fine one opera performance; a tree felled by wind or snow announced and taken in common; a proper use told to the assembly first. And the author: 「而对禁止性条款的违犯者，明清徽州还具有独特的罚戏、罚酒等惩罚性规定。」
  Limit: inland upland Huizhou, not the Pearl River Delta; state it.
- HK Herbarium (AFCD), "The Fung Shui Story of Lai Chi Wo", https://www.herbarium.gov.hk/en/special-topics/fung-shui-woods/the-fung-shui-story-of-lai-chi-wo/index.html - "Anyone causing damage to the fung shui wood would be fined and publicly denounced. For only one or two days in a year, villagers are allowed to enter the wood to gather sticks for firewood." A modern (2021) account of a Hakka village's custom, citing no stele: state it.
- HK Herbarium, "An Overview of Fung Shui Woods in Hong Kong", https://www.herbarium.gov.hk/en/special-topics/fung-shui-woods/an-overview-of-fung-shui-woods-in-hong-kong/index.html - "the canopy of the tree stratum is dense. The uppermost storey is made up of very tall trees ... Often growing to more than 20m, the canopies of these trees are clearly visible from the outside of the wood, while inside the forest you can only see their trunks."; "a secluded and dark domain as most of the sunlight is blocked out". Modern survey (from 2002). The record may already cite this site (grep the registry for herbarium.gov.hk / afcd).
- 日本森林学会 林業遺産 No. 34, https://www.forestry.jp/forestryheritage/2018-3231/ - Sai On encouraged the coastal 潮垣 and the inland village belt 抱護; 「この蔡温の指示で整備された「抱護」のうち最も良好に保存されているものが、1742年に造成された多良間島の「抱護」である。」
- MAFF GIAHS dossier on Tarama, https://www.maff.go.jp/j/nousin/kantai/attach/pdf/giahs_7_tarama-1.pdf - the 1741 survey on Sai On's orders, reported to Shuri in 1742; 「林帯の村抱護の幅は、造成時には 16m であったが、道路拡張で 4m 減じ、現在は 12m の林帯幅になっている。」; the upper layer fukugi, tera-hiboku, mokutachibana, tabu, evergreen; the largest fukugi 10.36 m high, about 275 years old. Its keeping by the hamlet's wards today is modern: if used, say so.
- Searched and NOT found (for absence notes): the Ryukyu royal ordinances' penalties for the belts, and what a Tarama villager could take from one; a Pearl River Delta stele naming a penalty for a village fengshui wood.

## Your items (two questions; at most ten new registry keys)

- 0071 (`research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html`):
  a group on who kept a village's grove and what it could take from it (the Huizhou covenants and steles, Lai Chi Wo), with
  dates, places and limits; what the keepers said the grove was for (Wangkou's screen against misfortune), beside the record's
  existing account of its sheltering role; how a fengshui wood stood (tall, dense, dark within - the Hong Kong survey, modern).
- 0072 (`research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html`): Tarama's belt - who ordered it
  (Sai On, 1741-42), its width when planted, its trees and their height today; absence notes for the ordinances' penalties
  and what villagers could take.

Do NOT edit any drawing page or any modal file - a later step writes the modal.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0071"` and `KEY="0072"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | G5 in progress (0071, 0072 grove keeping) | 2026-10-04"`.
2. Read the fragments and their notes; `make archive-find` for each source first, then `make source-pages`, then the source-reader
   agent from a bundle on every passage you will quote. Reserve any new key with `make reserve KIND=registry KEY=<key>`, and write
   its two write-ups and tags as the record's CLAUDE.md requires.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root (split a question that passes the cap along its topics).
4. Write `specs/319-modal-writeups/briefs/g5-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 G5:`), do not push. Your last message is one paragraph.

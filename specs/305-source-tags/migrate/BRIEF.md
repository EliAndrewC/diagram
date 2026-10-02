# Feature 305 - classify registry entries and trim their limits paragraphs

You are classifying works cited by a research record that grounds maps of a FICTIONAL premodern East Asian setting
(Rokugan, modeled on imperial China and pre-Meiji Japan). Each work gets tags on three facets, and each tag will be shown
to readers as a label whose tooltip carries a STANDARD explanation (below). Because the label now carries those
standard limits, each entry's "Why it applies, and its limits" paragraph is to be TRIMMED of whatever only restates them.

Read your batch file (JSON lines: file, key, cite, host, what, why, used). For EVERY line, write one output line.

## The vocabulary - each value with the explanation its label will show

- **period=premodern** (Premodern): Evidence from before the region's industrial era - the period the setting is modeled on, so its forms and its numbers apply most directly. The cut-off is where factory goods, foreign trade and state reform began to reach the countryside: in Japan the Meiji Restoration of 1868; in China about 1895, when treaty-port factories and railways began; in Korea 1876, when its ports were opened; in Vietnam, Ryukyu and Taiwan the start of colonial rule or annexation (the French conquest of about 1860-1885, 1879, 1895); in Europe about 1800, with enclosure, new crops and the first factories; elsewhere, when railways, factory goods or colonial cash crops reached the countryside. The tag follows the evidence, not the publication: a modern study of Edo-period village registers is premodern evidence. A work about no one place (the General region) takes the period of its evidence by the rule of the regions that evidence comes from; one about facts that do not change with the era is Not period-bound.
- **period=modern-preindustrial** (Modern, preindustrial): Evidence from the modern era, recorded while farming was still done by hand and with draft animals: from each region's premodern cut-off until about 1950 (about 1955 in Japan). Village forms, field layouts and building ways carry over from earlier times. But the countryside already had cheap factory iron for tools, kerosene, purchased fertilizer, railways tying it to markets, modern land surveys and state reforms such as Japan's land tax of 1873, and populations were at or near their peak. So densities, plot sizes and yields can run higher than in the setting. The period ends where land reform, collectivization, war or the spread of the tractor and chemical fertilizer remade the village - about 1950 in China, Korea, the rest of East Asia, Europe and most places elsewhere, about 1955 in Japan.
- **period=present-day** (Present day): The landscape since about 1950 (about 1955 in Japan): after land reform, mechanization, chemical fertilizer and the consolidation of fields into large regular plots. A present-day source is good evidence that a form exists and how it is laid out, especially where it survives from earlier times. Its counts and sizes describe a modern economy and a modern population, so the record uses them as anchors, not as measurements of the past.
- **period=timeless** (Not period-bound): Facts that do not change with the era: how a tree grows, how water holds in a ditch, what a material weighs. They apply to the setting as they apply to any time, and whatever limits remain are the source's own, stated in its write-up. A work about one period's practice is never this tag, even when written in general terms: it takes the period of its evidence.
- **region=japan** (Japan): Japan, one of the two models for Rokugan. Its castles, shrines, paddies and farmhouses are drawn on directly. Japan varies by region, from snowy Hokuriku to subtropical Kyushu, so a source about one prefecture speaks for that kind of country first.
- **region=china** (China): China, the other model for Rokugan, especially its walled cities, counties and imperial government. China is vast: the dry wheat and millet north and the wet rice south farm and build very differently. A source about one region speaks for that region first.
- **region=korea** (Korea): Korea, a close analog: East Asian rice farming, village groves and Confucian institutions shared with China and Japan, but with its own building traditions, such as heated floors and its own house plans. The record uses it where the practice is shared, often where no Japanese or Chinese source could be read.
- **region=east-asia-other** (Other East Asia): The wider region: the Ryukyu Islands, Taiwan, Vietnam and the borderlands. These are analogs that share rice farming and many practices with China and Japan, under their own climates and traditions. The record uses them where the practice is shared.
- **region=europe** (Europe): Europe. It has different crops (wheat and the heavy plow rather than rice and the hoe), different building traditions and different law, so it says little about how an East Asian place looked. The record uses it only for constraints that cross cultures: how a moat holds water, how large a tannery's pits are, how far a bell carries.
- **region=elsewhere** (Elsewhere): Outside East Asia and Europe: South and Southeast Asia beyond Vietnam, the Middle East, Africa, the Americas. Like Europe, it is used only for constraints that cross cultures, and its forms are not the setting's.
- **region=general** (General): Not about one place: botany, hydraulics, materials, or comparisons across many regions. It applies wherever its facts hold, and any regional limit is stated in the write-up.
- **kind=primary** (Primary): A document of the time itself: a gazetteer, a register, a land survey, a treatise, a period map or picture. It is the closest the record gets to the facts. But it was written for its own purposes (a tax count, an official's report, an ideal), so it can idealize, under-count or follow conventions of its own. It is often read in translation.
- **kind=scholarship** (Scholarship): A peer-reviewed article, an academic book, a thesis or an excavation report. Its methods and its sources are stated, so its claims can be checked. But it is one study, often of one place, and its conclusions are its author's interpretation.
- **kind=reference** (Reference): An encyclopedia or dictionary, including Wikipedia. It is broad, summarized and usually right about what a thing is. But it is secondhand: Wikipedia is edited by its community and can change, and a figure it gives is only as good as the reference behind it. The record relies on it for what a thing is, and for a number only where its own source carries the number.
- **kind=institutional** (Institutional): A museum, a government office, a preservation society or a university's public page. It is generally careful and often first-hand about its own site or collection. But it is written for visitors, so it can simplify, rarely cites its evidence, and may describe a restoration rather than the original.
- **kind=popular** (Popular): A blog, a tourism board, a travel account or a news story. It is readable, often first-hand, and often has photographs of what it describes. But it rarely cites a study, a promotional page shows its subject at its best, and its numbers are usually round.

## Period cut-offs by region (the same as in the period explanations)

| Region | Premodern | Modern preindustrial | Present day |
|---|---|---|---|
| Japan | before 1868 | 1868 to about 1955 | after about 1955 |
| China | before about 1895 | about 1895 to about 1950 | after about 1950 |
| Korea | before 1876 | 1876 to about 1950 | after about 1950 |
| Other East Asia | before colonial rule/annexation (Vietnam ~1860-1885, Ryukyu 1879, Taiwan 1895) | then to about 1950 | after about 1950 |
| Europe | before about 1800 | about 1800 to about 1950 | after about 1950 |
| Elsewhere | before railways, factory goods or colonial cash cropping reached the countryside | then until farm machinery spread, about 1950 in most places | after that |
| General | the period of its evidence by the rule of the regions it comes from; facts that do not change with the era are `timeless` | | |

## Classification rules

- PERIOD FOLLOWS THE EVIDENCE the record takes from the work - read "used" (what the record uses it for) and "what" -
  NOT the publication date. A 2004 article reading 1771 house registers is `premodern`. A Wikipedia article on Edo moats
  is `premodern`. A modern tourism page counting today's farmhouses is `present-day`. If the uses rest on evidence from
  several periods, list each, the one MOST of the uses rest on first.
- A present-day page DESCRIBING a premodern thing (a museum page on an Edo farmhouse, a preserved Edo terrace, a
  rebuilt barrier): `premodern` when the record takes the premodern form from it; `present-day` when it takes
  present-day counts or the present working landscape.
- `timeless`: botany, hydraulics, materials, physical facts. A work about one period's practice is never timeless.
- REGION is where the evidence is from (Ryukyu, Taiwan, Vietnam = `east-asia-other`; no one place = `general`). The
  language of the page does not decide it: a Japanese Wikipedia article on a Chinese city wall is `china`. List several
  only when the uses genuinely rest on several; primary first.
- KIND is the publication: `primary` (period documents - gazetteers, registers, land surveys, treatises, period maps
  and pictures, classical texts; a modern edition, transcription or translation of one, e.g. Wikisource or ctext, is
  still primary); `scholarship` (peer-reviewed articles, academic books, theses, excavation reports, J-STAGE papers,
  research bulletins); `reference` (encyclopedias incl. every Wikipedia and Baidu Baike, dictionaries, kotobank's
  dictionary entries); `institutional` (museums, ministries, prefectures, municipalities, preservation societies, FAO,
  universities' public pages, cultural-heritage databases); `popular` (blogs, tourism boards, travel accounts, news,
  commercial or hobby sites). Usually one kind.
- The host is a HINT only. Never tag by host alone; read the entry.
- If the period table genuinely does not settle an entry (e.g. evidence from a region and date the table cannot
  place), still give your best tags AND add `"unsettled": "<one sentence why>"`. Do not invent a cut-off.

## Trimming the limits paragraph ("why")

Goal: the paragraph keeps WHY THE SOURCE APPLIES and EVERY LIMIT SPECIFIC TO THIS SOURCE, and loses what ONLY restates
a standard explanation of the labels you gave it.

Remove (examples - only when it is generic to the category, not a specific fact about this work):
- that it is a tertiary/encyclopedia/community-edited/Wikipedia article, that it may change, that a figure is only as
  good as its reference, that it is used for what a thing is rather than for numbers (reference);
- that it is a tourism/promotional/blog page citing no study, written for visitors, with round numbers (popular,
  institutional);
- that it describes the present day / a living landscape in the present tense / modern counts used as an anchor for a
  premodern pattern (present-day);
- that it dates from the modern era with factory iron, railways, purchased fertilizer, population at its peak, so
  numbers may run high (modern-preindustrial);
- that it is a Korean / other-region analog standing in where the practice is shared / where nothing closer could be
  read, said generically (korea, east-asia-other, europe, elsewhere);
- that a primary source was written for its own purposes / may idealize, said generically (primary); that a study is
  one study of one place, said generically (scholarship).

Keep (these are source-specific - never remove them):
- what the work gives us and why it fits; the particular place, date, scale or method; a figure the page does NOT
  state but we derived; which part is reliable and which is not; a specific error, gap, bias or restoration; a
  specific translation issue; anything naming THIS work's particulars.

Mechanical rules (a script checks them; a trim that breaks one is refused and redone by hand):
1. DELETE ONLY. Never add words, never reword, never summarize. You may delete whole sentences or clauses. To mend a
   joint you may use ONLY these words, which need not appear in the original: and, but, its, it, the, that, this, is,
   are, for, of, a, an, to, in, on, as, so, only, which, here, used - plus changes of capitalization and punctuation.
2. Keep every inline HTML tag around text you keep (`<em>`, `<code>`, `<a href=...>`, `<span ...>`) exactly as written,
   and keep every HTML comment `<!-- ... -->` in the paragraph, verbatim.
3. Keep the paragraph's statement of why the source applies (usually its first sentence). Never leave it empty.
4. If nothing in the paragraph only restates a label, return `"why": null`. If the entry has no "why", return null.

## Output

Write your output file (the path the dispatch names) as JSON lines, one per input line, in input order:

    {"key": "<key>", "period": ["..."], "region": ["..."], "kind": ["..."], "why": "<trimmed paragraph>" | null}

plus `"unsettled": "<why>"` where it applies. Use the Write tool once at the end (or a few times appending, for size).
Your final reply: one line - the count of entries written, how many trimmed, how many unsettled. Nothing else.

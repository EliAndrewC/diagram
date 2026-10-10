# Research - feature 343: is the receiving court "swept"?

## R1 - the research pass (2026-10-10, an agent, read-only)

**Method** (observed 2026-10-10; method: a sonnet agent's search of the record, the archive and the web, in that order,
reading and reporting only). The record was grepped for sweep, raked, gravel, sand, 掃, 砂利, 白洲 and juniper, and 0104,
0110, 0224 and 0099 were read in full. Japanese web searches covered 武家屋敷 前庭 砂利 掃き清める, 玄関 式台 駕籠寄せ 砂利,
門前 掃除 辻番 門番, 高山陣屋 玄関前 and 大名屋敷 発掘 玄関前 砂利敷. Morse's 1886 book was searched in full for sweep, swept,
raked, gravel, sprinkl, paved, pebbles and approach. The archive's `make archive-find` was asked with joined terms and
answered "nothing held"; that was a fault of the tool's output (its terms are all required), fixed alongside by this
session (`scripts/record/archive_ops.py`, a tooling commit of its own).

**Answer: silent** (observed 2026-10-10; method: the search above).
- No premodern source read attests the ground between a residence's or an office's gate and its formal entrance as swept,
  raked, graveled or sanded, nor as bare earth.
- The record's 0104 already finds no garden there. Its 1869 Joge drawing (Meiji 2) labels 「玄関・敷台・大門」 with no
  surface.
- A Qing yamen's front court is planted: 「步入大门就是空阔的前庭，内植数十株粗大的桧柏」 ("stepping through the main gate
  is an open front court, planted with dozens of stout junipers", translation the agent's).
- The white sand or gravel of 0090 and 0099 is the hearing court's, not the approach's.
- 0224 records swept ground for graves (Ming, 1630s) and finds Japanese grave cleaning and swept shrine precincts only in
  modern custom.
- Morse (1886) saw a "well swept" Kyoto yard and swept garden paths in the 1880s, which is modern.
- Morse's reproduction of a Sakai garden drawing shows a stone path through a second gateway to the genka (Morse's spelling of genkan), inside a garden
  with lanterns. Morse dates it loosely ("nearly two hundred years ago").

**Not reached:** Edo machi-fure on sweeping before a house, the Takayama Jin'ya's own site, the Joge pamphlet itself, and
daimyo-residence excavation reports.

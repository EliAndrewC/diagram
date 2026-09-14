## Scope read

- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/homesteads.html` — notes `fn-100`…`fn-153` (54 notes: 37 citations, 17 absence, 0 grounds)
- `/diagram/.clones/diagram-research/.claude/skills/diagram/research/citations/water.html` — notes `fn-132`…`fn-185` (54 notes: 34 citations, 19 absence, 1 grounds)
- Assertions read on `research/homesteads.html` and `research/water.html`. 61 distinct URLs fetched, one attempt per URL.

---

## 1. NOT-READABLE (the finding that changes the record)

**homesteads `fn-128` — `ushijima-2020-manchu`** — the footnote's own link is `https://doi.org/10.1002/2475-8876.12146`, which 302s to `onlinelibrary.wiley.com/doi/10.1002/2475-8876.12146`, which returns **HTTP 403**. The quoted English (「farmers who resided around the village were gathered at the rim of the old residential area around 1968.」) could not be read on any page. Quotation **UNFETCHABLE**; support unjudged. The record discloses this at the point of use ("Wiley serves a JavaScript challenge to every fetcher; the paper is CC-BY-NC-ND and was read from the copy the GM downloaded"), and under the GM's 2026-09-07 test a page they can open is public — so this is a re-point-or-disclose call for the session, not a quote error.

### Public pages this tool cannot decode (recorded as such, **not** as NOT-ON-PAGE)

| note | key | what happened |
|---|---|---|
| homesteads `fn-108` | `sinyoken-madori` | `sinyoken.sakura.ne.jp/caffee/camadori.htm` served in Shift_JIS; the fetch returns mojibake (`���A�E����������@`). The note already discloses this and says it was read with a decoding shell. Quotation **not verifiable by this tool**. |
| homesteads `fn-120`, `fn-121`, `fn-124` | `sugiura-1973-fuzoku` | the J-STAGE PDF is a **scanned image** (CCITT fax streams, 1.1 MB, no text layer). Public and human-readable; no machine can verify the four Japanese quotations or the Table 5 / Table 6 figures. |
| homesteads `fn-143` | `kurita-2019-igune`, `minami-2024-igune` | both J-STAGE PDFs (3.8 MB / 2.2 MB) returned as FlateDecode binary; text not extractable. |
| water `fn-152` | `maff-drain-shape` | the MAFF PDF returned as compressed binary; text not extractable. |

---

## 2. DIFFERS (the page's own wording)

**homesteads `fn-111` — `kotobank-warazuka`** — DIFFERS.
Record: 「脱穀後の**藁束**を刈田やあぜに円筒形に積み上げたもの」
Page (デジタル大辞泉): 「脱穀後の**わら束**を刈田やあぜに円筒形に積み上げたもの。」 — the page writes わら in kana, not 藁.

**homesteads `fn-114` — `shizen-teibo-jawiki`, second quote** — TRANSLATION-DIFFERS / truncation changes the sense.
Record: 「河川や旧河道（右上）脇に曲線状に発達する古くからの集落と後背湿地」, translated "Old settlements developed in a curving line along the river or the old channel (upper right), and the back marsh".
Page (image caption): 「河川や旧河道（右上）脇に曲線状に発達する古くからの集落と後背湿地**の新興住宅地（新潟市郊外）**」 — the caption's second noun phrase is *the new housing estate on the backswamp*, not "the back marsh". The quoted span is a verbatim prefix, but it is cut mid-phrase and the English renders the truncation as the caption's meaning. Accept: "...and the new housing estate on the backswamp (outskirts of Niigata city)".

**water `fn-150` — `kotobank-shimogoe`** — DIFFERS (punctuation).
Record original: 「市中に青物類を供給する周辺農村では**、**近世中期になって…」
Page (改訂新版 世界大百科事典): 「市中に青物類を供給する周辺農村では**，**近世中期になって諸肥料の値段が高騰してくると下屎を大幅に利用することになり」 — the encyclopedia uses full-width `，` (U+FF0C), the record `、` (U+3001).

**water `fn-159` — `beijing-chengchi-zhwiki`** — DIFFERS (two dropped words).
Record: 「内城七座水关：德胜门西水关（进水口，三孔）、…」
Page: 「内城**有**七座水关：德胜门西水关（**内城**进水口，三孔）、东直门南（排水口，一孔）、…」

**water `fn-161` — `endorheic-basin-enwiki`, second quote** — DIFFERS (truncated at a comma, presented as a full stop).
Record: 「…endorheic lakes are usually more sensitive to environmental pollutant inputs than water bodies that have access to oceans.」
Page: "...than water bodies that have access to oceans**, as pollution can be trapped in them and accumulate over time.**"

**water `fn-171` — `weir-enwiki`, first quote** — DIFFERS (leading word), flag for a character check.
Record: 「**Typically, the** reduced river velocity upstream can lead to increased siltation (deposition of fine particles of silt and clay on the river bottom).」
Page text returned: "The reduced river velocity upstream can lead to increased siltation (deposition of fine particles of silt and clay on the river bottom)." — no "Typically,". Worth one confirming read before editing, since a fetch summary can normalize a sentence opening.

**water `fn-173` — `jawiki-yosuiro`** — DIFFERS (the opening is not the page's).
Record: 「**古くは**土を掘って踏み固めただけのものであることが多かった。」
Page: 「日本の近世以前の用水路は、主に農業用水路として使われており、**また**土を掘って踏み固めただけのものであることが多かった。」

**water `fn-176` — `fao-irrigation-canals-ch5`, second quote** — DIFFERS (truncated at a comma).
Record: 「Earthen canals are simply dug in the ground and the bank is made up from the removed earth.」
Page: "...made up from the removed earth**, as illustrated in Figure 77a.**"

**Could not confirm the exact character** — water `fn-164` (`nanjing-chengqiang-zhwiki`): the record writes 三山门又称`'水西门'` with straight apostrophes; the fetch's rendering of the page also shows `'水西门'`, so whether the page uses `“”`, `「」` or `''` is unresolved by this pass. Not counted as DIFFERS.

---

## 3. DOES-NOT-SUPPORT

None.

---

## 4. PARTIAL — the part not in the quote

**Not disclosed by the note:**

- **water `fn-148`** (`songshi-273-wikisource`) — the assertion is that the Northern Song **built** an artificial marsh-and-pond belt as anti-cavalry terrain. The quoted passage is He Chengju's **memorial proposing** it (「若於順安砦西開易河蒲口…可以遏敵騎之奔軼。」 — verbatim on the page). It grants the design and the anti-cavalry intent, not the execution.
- **water `fn-146`** (`weir-enwiki`) — assertion: "a sluice-fed head-race genuinely IS **slower** (and, in this page's reading, wider) than the stream that feeds it". The quote ("Mill ponds are created by a weir that impounds water that then flows over the structure.") grants impoundment above a weir; "slower" is not in it. Only "wider" is labeled an inference.
- **water `fn-160`** (`weir-enwiki` ×2) — assertion: "an overflow weir/sluice that **holds a set level** and sheds only the surplus". Neither quote says a weir holds a level; the work's own registry limits state this ("it does not… say in so many words that a weir holds a level").
- **water `fn-156`** (`beijing-chengchi-zhwiki`) — supports the Chinese half (water led from the Jade Spring hills through the ring). The same sentence's "Edo turned the Hirakawa into its moat **spiral**" is not in this quote, and the record's own registry line for `sotobori-jawiki` records that the page's word for the shape is 「の」の字, not "spiral".
- **homesteads `fn-140`** (`yashikirin-jawiki`) — assertion "Tohoku: the S-facing side is the open one". The quote says the igune stand on the **north and west**; "the south side is the open one" is an inference from that (and the same page in fact puts Tonami's storehouses, fruit trees and **bamboo on the south** — 「南側には蔵や納屋などがあり、無花果や葡萄、柿などの果実がなる植物や竹などが植えられていた。」).

**Disclosed by the note itself (quote grants part, the note names the rest as the record's own reading):** homesteads `fn-100` (the 10-14 day rack-drying figure is on no page read), `fn-120` / `fn-121` / `fn-124` (the per-function Table 5/6 figures are read off a scanned table, not quotable), `fn-122` (direction of growth), `fn-126` (paddy for a watercourse), `fn-133` (neither form corrects the other), `fn-136` (a well and pump beside the trough), `fn-137` (cattle and chicken sheds; the "millennia" manure economy), `fn-139` (the bed's size consequence), `fn-151` (the grove as largest appurtenance), `fn-152` (per-holding water control); water `fn-135` (terminal rung and the drainage-side mirror), `fn-137` (passage through the bund, ditchless interiors), `fn-151` (moat/pond/inundation as the page's synthesis), `fn-152` (the superlative and the placing below the collector), `fn-155` (nobody needed a whole-course name), `fn-157` (an abandoned bed vanishing), `fn-164` (the drain cut short of the patrol ring), `fn-174` (a contour ditch keeping water out of the ground below), `fn-183` (canal seepage in particular; localization below the command).

---

## 5. The rest — VERBATIM and SUPPORTS

**homesteads:** `fn-103`, `fn-107`, `fn-109`, `fn-113`, `fn-115`, `fn-116`, `fn-117`, `fn-118`, `fn-119`, `fn-125`, `fn-127`, `fn-129`, `fn-131`, `fn-134`, `fn-135`, `fn-145`, `fn-147`, `fn-148`, `fn-149`
**water:** `fn-133`, `fn-141`, `fn-142`, `fn-143`, `fn-144`, `fn-145`, `fn-154`, `fn-158`, `fn-162`, `fn-165`, `fn-166`, `fn-177`, `fn-178`, `fn-180`, `fn-181`

All READABLE on the footnote's own link, all passages found character-for-character (including full-width ｍ in `fn-178`, the FAO page's own "Co" typo in `fn-161`, and the ö in Reihendörfer at `fn-116`).

Two notes worth a line each: homesteads `fn-107`'s page returned the inner quoted clause 「開墾した田畑は藩主に属すが、開墾した百姓にはその田畑を自前で耕作することを許された」 verbatim and described the surrounding clause rather than returning it; homesteads `fn-151`'s page returned 「明治時代以前には家の全周を囲っていた」 and not the rest of the sentence. Both look right; neither was returned whole.

---

## 6. ABSENCE and GROUNDS notes — form

**The grounds note.** water `fn-170` — `no source is owed: measured on our own maps; a drawing convention`. The sentence is "A real ditch narrowing from ~1.4 m to ~0.45 m over 460 m is not visually dramatic from above either." The two widths and the run **are** this project's own drawn figures (4.5 → 1.5 ft over 1,504 ft), so the first reason fits and nothing here is a research question in disguise. Two things for the session to judge: the second reason, `a drawing convention`, does not describe this sentence — the sentence is the argument for *not* adopting a convention; and the sentence's grammatical subject is "a real ditch", i.e. it states how a real object looks, which a strict reading of the prohibition on claims about the physical world could catch. Reported, not decided.

**A duplicated date in the new absence notes.** Every absence note written today opens `searched 2026-09-14: searched 2026-09-14:` — the phrase is doubled. homesteads `fn-101`, `fn-102`, `fn-106`, `fn-110`, `fn-112`, `fn-123`, `fn-130`, `fn-132`, `fn-138`, `fn-141`, `fn-142`, `fn-144`, `fn-146`, `fn-150`, `fn-153`; water `fn-132`, `fn-134`, `fn-136`, `fn-138`, `fn-139`, `fn-140`, `fn-147`, `fn-149`, `fn-153`, `fn-163`, `fn-167`, `fn-168`, `fn-169`, `fn-172`, `fn-175`, `fn-179`, `fn-182`, `fn-184`, `fn-185` — 34 of the 36 absence notes.

**"no query could be run in this pass."** The same 34 notes say this and then name the pages that *were* read and the work that would settle the question. The feature-195 form asks for what was **tried**; "no query could be run" states that no search was performed, which reads oddly beside a list of pages read. Whether that satisfies the form is the session's call; it is uniform across the batch.

**Two notes name no search at all.** homesteads `fn-104` and `fn-105`: `no publicly readable source (searched 2026-09-13: the sentence rests on general reading and no source was cited for it when it was written)`. That records the sentence's provenance, not what was searched.

**An absence note under a verbatim foreign-language quotation.** homesteads `fn-101` — the visible prose quotes 「田畑を保有しない百姓も含め全百姓が屋敷を持つようになり」 with a translation, and its note says no publicly readable source carries it. A quoted passage whose page cannot be read is the exact shape feature 195 addresses; it is honestly labeled, but it is a quotation presented as one.

**Every other absence note in scope** is in the right form for its sentence: the sentence owes a source, none was found, and the note says what was read and what work would carry the figure. I checked each against its assertion and found no absence note sitting on a sentence that a cited page actually supports.

---

## 7. Assertions with NO footnote that rest on something outside the record

Skipping (as instructed) the project's own measurements, drawing conventions, GM rulings, setting canon, derived solar/hydraulic arithmetic, and sentences the page labels as its own reading or as a GUESS.

**`homesteads.html` — "May a byre stand beside a wellhead?"**
- *"And the well (ido), where a house had one, sat "in the rear corner of the earthen-floored doma or in a rear projection room" - i.e. inside the same building."* — a **quotation in the visible prose with no footnote and no key**. The nearest mark, `fn-138`, sits on the following sentence and is an absence note about farmhouse plan dimensions, not about the in-house well.

**`homesteads.html` — "Is every farmhouse reached by a lane, and in what FORM?"**
- *""every house in the nucleated village is accessible via the INTERCONNECTED system of narrow lanes and alleys""* (in the GM's-question paragraph) — a quotation with no footnote. `fn-132` earlier in the section is an absence note saying the two passages this page paraphrases are on no page fetched; the quotation is repeated here unmarked.

**`homesteads.html` — "The garden's sun, and how far the windbreak shades"**
- *"house faces E, away from the SW wind; the front (E) yard is the work yard, "securing adequate open space" with only fruit trees and a persimmon in the yard center; S and W carry 2-3 rows of sugi; the N/W bamboo strip is "shady ... always damp""* — three quoted fragments from the Tonami model homestead, with an inline `no publicly readable source, searched 2026-09-06` in the prose but **no footnote** on any of them.

**`homesteads.html` — "The threshing yard's sun"**
- *"which agrees with surviving farmhouses (~6-7 m)"* — a measurement of real buildings, no footnote. (The section's Sources line discloses the figure is unsourced; the assertion itself carries nothing.)

**`homesteads.html` — "The farmstead's fixtures"**
- *"Stable litter and grass composted into stable manure (kyuhi, 厩肥)"* — carries an inline "(no readable page supports it)" but **no footnote**.

**`water.html` — "One name per river"**
- *"within Edo itself one river carried different names neighborhood by neighborhood (Asakusa-gawa / **Ryogoku-gawa** / Okawa / Sumida-gawa, all the same water)"* — the Ryogoku-gawa element is supported by nothing in scope: `fn-154` is the Yodo, and I confirmed **両国川 does not appear on the Sumida page** (only 両国橋 / 両国大橋). The absence is recorded in an HTML comment on the Sources line and in out-of-scope `fn-15`, so a reader meets the name as sourced.

**`water.html` — "No toe marsh at town/city scale"**
- *"ditch discharge went into an engineered moat/canal/river network (**Suzhou's canal grid**; Edo's canals and the immediate infill of the Hibiya inlet after 1590)"* — the footnote on that clause (`fn-23`, out of scope) quotes the Hibiya page only; Suzhou rests on nothing, and the section's own HTML comment records it as "not re-read - leftover".

**Skipped for the stated reason, in the sections the scope touches:** every drawn width, berm, radius, share and pixel figure (measured on this project's own maps); the 38 ft byre-to-well span on Kashikawa; the 39 ft and 50 ft sun corridors and the 38N solar table (derived geometry); the Lacey/Manning arithmetic; the 0.727 privy share and the 1.5 ft bund (GM rulings, footnoted elsewhere); the Inashiro/Sawada/Tango counts; and every sentence carrying "this page's reading", "our own", "a GUESS" or an inline unsourced label.

---

## 8. Summary

| verdict | homesteads `fn-100`-`153` | water `fn-132`-`185` | total |
|---|---|---|---|
| notes in scope | 54 | 54 | **108** |
| citation notes | 37 | 34 | 71 |
| absence notes | 17 | 19 | 36 |
| grounds notes | 0 | 1 | 1 |
| READABLE | 36 | 34 | 70 |
| NOT-READABLE | 1 (`fn-128`, Wiley 403) | 0 | **1** |
| public but tool cannot decode | 5 (`fn-108`, `120`, `121`, `124`, `143`) | 1 (`fn-152`) | 6 |
| VERBATIM | 30 | 26 | **56** |
| DIFFERS | 2 (`fn-111`, `fn-114`) | 6 (`fn-150`, `159`, `161`, `171`, `173`, `176`) | **8** |
| NOT-ON-PAGE | 0 | 0 | **0** |
| UNFETCHABLE / unverifiable quotation | 6 | 1 | 7 |
| translations judged against their originals | 26 | 22 | 48 faithful, 1 TRANSLATION-DIFFERS (`fn-114`) |
| SUPPORTS | 24 | 21 | **45** |
| PARTIAL | 13 | 13 | **26** (5 not disclosed by the note) |
| DOES-NOT-SUPPORT | 0 | 0 | **0** |

**Hosts that refused or could not be decoded** (recorded, not retried):
- `doi.org` → 302 → `onlinelibrary.wiley.com` — **HTTP 403** (homesteads `fn-128`).
- `sinyoken.sakura.ne.jp` — served, Shift_JIS, returns mojibake through this tool (homesteads `fn-108`).
- `www.jstage.jst.go.jp` — three PDFs served and saved, no readable text layer: `tga1948/25/3/25_3_145` is a **scanned image** (homesteads `fn-120`, `121`, `124`); `jjsidre/87/10/87_825` and `windengresearch/28/0/28_J14` are compressed binaries (homesteads `fn-143`).
- `www.maff.go.jp` — `04_hojou_hata_gijutsusho20-23.pdf` served, compressed binary, text not extractable (water `fn-152`).

**One structural oddity, not a citation failure:** on `citations/water.html` the note `<li id="fn-75">` sits at line 541, physically between `fn-131` and `fn-132`, out of numeric order; the research page references it twice (`fnref-75` at `water.html` line 38 and `fnref-75b` at line 1012).
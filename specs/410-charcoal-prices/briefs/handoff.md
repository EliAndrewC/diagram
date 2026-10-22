# Feature 410 - handoff

## Session 1

- SECTION=0279/what-did-charcoal-cost
- Fragment: `research/questions/0279-what-did-charcoal-cost.html` (notes `.notes.html`, originals `.originals.html`). Prose about 15.7 KB, under the 20,000-byte cap; no split.

Per figure the issue asks for (#11), verdict and where it stands:

- Price per bale, Japan, with its weight: ATTESTED ONLY FOR Edo's ward headmen's return of 1842, six grades by the bale (上中下炭 500/448/364 -> 466/422/342 mon; 佐倉炭 144/132/120 -> 135/124/112), no bale weight printed, not called black or white, not said to be retail or wholesale; the "before" column is itself the fifth month's cut price. `#charcoal-edo-1842`.
- Bale weight: SILENT for the Edo period. Nearest: 0197/0199's Iburi (Hokkaido, undated) 4, 10 and 8 kan by grade; the Itsukaichi bulletin's Tama 4, 5 or 6.5 kan (undated) and a 5-kan Hikawa bale of 1887-1896. `#charcoal-bale`.
- White charcoal price: ATTESTED ONLY FOR 1716 at second hand (Mitamura Engyo via the bulletin): Kumano (bincho) 500 / 400 mon a bale, 8-9 bales a ryo of 4,000 mon; Hachioji (Tama, white) about 20 a ryo, so about 200 mon a bale (arithmetic). `#charcoal-white`.
- White-to-black ratio: Japan SILENT (Kumano against Hachioji is white against white, 2.2-2.5, arithmetic). China: ATTESTED ONLY FOR Beijing's official list of 1736, white 1.1 against black 0.5/0.6 tael per 100 jin, 1.8-2.2 (arithmetic). `#charcoal-white`, `#charcoal-china`.
- Retail by small measure in a city: SILENT. `#charcoal-trade` (absence note `charcoal-open-absence`).
- Wholesale at the kiln, by boat or cartload: SILENT. Found instead: the Itsukaichi brokers' tax (運上金) of 8, later 12, mon per 8-bale horse-load; horse-loads of 6 (Ome) and 8 (Itsukaichi) bales; 809,710 bales by ship to Edo in 1726 (aozorapota, citing 『多摩と江戸』). `#charcoal-trade`.
- What carriage added: SILENT (an 1863 village record names carriage money to Edo with no amount). `#charcoal-trade`.
- Burner-days per bale; yield from wood: SILENT. Kiln output ATTESTED ONLY FOR the bulletin author's general undated statement: earth kiln of black 20-30 bales in 3-4 days, stone kiln of white 2-3. `#charcoal-kiln`.
- Nearest only: Akita 1600, 181 kanmon for 120 bales of smith's charcoal (about 1,508 mon a bale, arithmetic), pre-Tokugawa coinage, no weight. `#charcoal-trade`.
- Ming/Qing: ATTESTED ONLY FOR official lists: Beijing 1736 (炭 0.225, 黑炭 0.5/0.6, 白炭 1.1, 紅螺炭 1.06 per 100 jin; wages 154 / 75 cash = 0.1925 / 0.09375 tael at Gao's 800); the 1615 handbook (炭 0.12-0.75, 白炭 0.49-1.113; wages 0.03-0.07); Zhili 1769, 137 木炭 rows 0.0018-0.008 tael a jin (51 at 0.005), five districts with 匠 and 夫 wages; Wubian (before 1560) 0.30 and 0.17 tael per 100 jin, smiths 0.03-0.04 a day. `#charcoal-china`.
- Wages beside each figure: SILENT for Edo 1842 (nearest: Nagata 1842 farm laborer 132 mon, 0262; Edo tobi 300 mon and carpenter 5-5.5 monme, undated 1830s-50s, 0275), for 1716 (nearest: Tama carpenters 1749 1-1.7 monme, 0255, 33 years; Kyoto laborer 2.82 g silver 1745-1754, 0250, about 30 years; no copper rate of 1716 in the record, so no day count), for Akita 1600 (nearest: Osaka-area building laborers 1620-1628, 0276); Wubian's laborer SILENT (nearest the 1615 handbook).

Searches: the archive (`make archive-inbox`, `archive-find` for every key and URL); the Itsukaichi bulletin read through curl and pdftotext; Oishi table (12) on page images pp. 86-87; Takahashi p. 11 on its Wayback copy and page image; Gao and the Wubian from the archive's text; all 24 Bochum Zhili chapters read for charcoal rows with xlrd; web searches 守貞謾稿 炭売 (twice, nothing). Morisada (pid 991466): NDL full-text and IIIF refuse this item; shot.py screenshots of koma 100, 115, 130 rendered blank.

Checks run: source-reader on all seven sources (34 passages READ, 0 CONTRADICTED, 0 NOT-FOUND; fixes applied: 1863 not 1862, the Meiji 20s as 1887-1896 and of Hikawa charcoal, the bulletin's "also" hedge, Takahashi's main verb). Still owed for session 2: quote-check, translation-check, record-format, intro-check, source-applicability (`make record-owed`).

New registry keys (2): `saito-2022-tama-no-sumi`, `takahashi-1995-akita-sumiyaki`. Moved from uncited to cited: `aozorapota-2024-tama-sumi`. Updated: `oishi-1966-tenpo13-bukka-kakiage` (table (12) read, limits), `gao-shouxian-jiuqing-wuliao`, `wubian-qianji-05`, `bochum-zhili-wuliao-jiazhi` (chapters 3, 18, 24 on its citation line, archived).

Leads not followed: Morisada's 生業 pages (pid 991466, pp. 87-186) for 炭売 - shot.py rendered blank here, so try again from a session where the NDL viewer draws; the 飯能市 1822 炭問屋仲間議定書 (city.hanno.lg.jp/material/files/group/65/14176b5b3725b.pdf); Mitamura Engyo's collected works (vols 6, 7, 9, 23) and the 「商人職人懐日記」 behind the 1716 prices; 九卿議定物料價值 卷三 柴炭煤斤 itself (IA nlc-892-312002001644); 邱仲麟 on Ming Beijing fuel; the bulletin's 1814 women carriers (two bales or one a trip, no amount) were not written in.

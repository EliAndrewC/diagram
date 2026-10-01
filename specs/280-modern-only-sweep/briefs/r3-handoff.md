# Handoff - feature 280, group R3 (religion-and-death: temple precincts and clergy homes), session 1

- SECTION=religion-and-death/740
- SECTION=religion-and-death/460
- SECTION=religion-and-death/040
- KEY=ranzan-senjudo-1843
- KEY=ranzan-senjuin
- KEY=kotobank-bomori
- KEY=koshoji-yoshizaki-taya
- KEY=takabatake-naragoround
- KEY=sakamoto-satobo-otsu
- KEY=ranzan-koshoji-senjudo (existing entry; its Used for line widened, re-cited in 740 as -2, -3, -4)

## Items

M72 MIXED - the new question 740 ("Were a town monastery's precinct and main hall that size before modern times?") records the precinct form (hall, kuri, bell tower, gate) as attested before 1868; it also records an Edo village record of 1843 (Senjudō, Hiki district), which gives two of the register's own temples exempt holdings of 742 and 694 tsubo (fields included), against their post-1868 precincts of 813 and 453 tsubo; it notes that the one Edo-dated main hall read (Eijuji, 1697, about 54 by 47 ft) lies inside the 24-63 ft band and that the register's median-width hall (Senjuin, 7 ken) was built after an 1876 fire; 460 now points to 740 and its decision says the defaults sit where the Edo figures put them - nothing for the generator to stop drawing: the town monastery stays, its defaults (16,400 sq ft precinct, 42 ft hall) stand, calibrated to the Edo holdings of about 700 tsubo (about 25,000 sq ft, a ceiling since it counts fields), and the bands' ends (285 and 1,944 tsubo; 4 and 10.5 ken) are labeled a guess in degree with no Edo figure behind them; if the GM wants the band clipped to Edo evidence, the only Edo-backed span is roughly 450-750 tsubo for the precinct and about 18-54 ft for halls - searched 2026-09-29, in Japanese, on the web: 新編武蔵風土記稿 比企郡 寺 除地 境内 坪; 村明細帳 寺 境内 坪 江戸時代 除地 寺院 本堂 間口; "境内除地" 坪 寺 風土記稿 本堂; 江戸時代 寺院 境内 面積 坪 平均 村の寺 研究 寺社書上; "寺社書上" 境内 坪 本堂 間口 奥行 翻刻; the ADEAC municipal histories; "御府内備考" 境内 坪; "寺社備考" 境内 坪 拝領地; 江戸時代 城下町 寺町 寺院 境内 坪数 一覧; the Ranzan web museum's eleven Edo village accounts (01_01-01_11). Found but not usable: the Gofunai bikō zokuhen (1829) records each Edo temple's precinct area, but no public transcription of its figures was found; one figure (Shinpukuji, 1,363 tsubo) appeared only in a search summary from a page under maintenance; a J-STAGE PDF on Edo's religious space could not be read here. Not searched in Chinese (the bands are Japanese measurements). The GM ruled the form in: the town monastery is canon (a monastery just outside a town, in the campaign notes), knowingly; the bands themselves were a feature 272 research decision, not a GM ruling.

M73 PREMODERN-ATTESTED - 040 now cites these as attested before modern times: a Shin priest's wife (bōmori) from a list of 1343 and in Rennyo's letters; priests' lodging houses built round the Yoshizaki temple from 1471; shrine priest families' quarters at Kamigamo (Muromachi to the Restoration) and at Takabatake in Nara (until Meiji); and old monks' retirement residences at Sakamoto below Mount Hiei in the Edo period, which matches the rule's "retired abbot's hermitage" exception; it records that no source read counts the clergy homes round one temple, so the 2-3 (5-9 hereditary) count within about 500 ft is the GM's ruling and a guess in degree - nothing for the generator to stop drawing: the clergy homes near a temple and the hermitage exception stay as specified. The setting canon supports the form too: "For married monks ... their families ... usually live in or next to the temple complex in temple housing" (l7r.md, Temple Daily Life). The GM ruled the form and the count in (the 040 spec, GM ruling 2026-07-24, and the canon), knowingly for the form; the count is the GM's own figure with no source behind it either way. Searched 2026-09-29, in Japanese, on the web, Kotobank and the Japanese Wikipedia: 坊守 浄土真宗 江戸時代 住職 妻帯; 吉崎 多屋 坊主 蓮如; 坂本 里坊 江戸時代 延暦寺; 奈良 高畑 社家町 春日大社 江戸時代; 高畑 社家町 春日社 禰宜.

## Left open

- No section was held: religion-and-death 040 and 460 are neither 279's (124-129) nor 269's (no unlanded 269 commit on religion-and-death).
- Not committed: `research/sources/`, the glossary assets and the fields/archetypes files, which also carry another session's uncommitted work in this clone. The six new registry fragments are committed; `make record` must run again before the checks so SOURCES.html carries them.
- `tests/interactive/test_footnotes.py` fails on towns.html [^99] (a grounds note with a reason not on the closed list). That comes from other uncommitted work, not R3.
- The source-reader found that the Ranzan register pages do not themselves say "Meiji" (the site files them as the prefecture's 1963 papers). 460 and 740 now say "a register made after 1868". The older entries (ranzan-temple-register, ranzan-koshoji-senjudo) still call it Meiji-era, as "this page's inference".
- Checks owed: quote-check, record-format and source-applicability on 040, 460 and 740 and on the six new keys.

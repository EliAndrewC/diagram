# Feature 414, session 7 (money marks): the gold bu and shu, and 0290-0294 - handoff

Commits c02551d73..HEAD of 2026-10-24, each opening "413: marks - ". Markup only: `make record CHECK=1` builds,
`make money-candidates CHECK=1` exits 0 (0 owed), `make record-owed` reports 586 units, 0 unanswered (this session ran no
check, so a unit its edits caused would show as unanswered, and none does).

## Tooling

- `scripts/record/money_candidates.py` reads `ryō` and `shū` as `ryo` and `shu` (`_plain` folds the macron, so a marked and
  an unmarked amount are compared alike); test `test_a_coin_with_its_macron_is_found_as_the_coin`. No new owed amount came
  of it: 0251's three `ryō` were already marked, and no `shū` amount is in the record.
- Removed as dead now that `research/assets/money-eras-awaiting.json` is empty: the AWAITING branch of `_eras` (an awaiting
  era given its place's coins), with `AWAITING`, `JAPAN_PLACES`, `CHINA_COINS`, `CHINA_PLACES` and `DOLLAR_PLACES`, and the
  test `test_an_awaiting_era_counts_as_built_with_every_coin_of_the_period`. An era listed there again counts as no era in
  the scanner (test `test_an_awaiting_era_is_no_era_here`); amounts are listed either way, only the "nearest era" column
  changes. `record/money.py` still honors the awaiting list (FR-008), untouched. The Chinese-coins test now reads vendored
  rows. `make test-file FILE=tests/tooling/test_money_candidates.py`: 7 passed.

## Re-marking asked on diagram#13

1. **osaka-1700 split by `data-paid` year** (a script, then by hand): 39 to `osaka-1695` - by script 35 (0251 2, 0257 24,
   0260 3, 0266 4, 0269 1, 0279 1, the last Edo 1710-1713 by its midpoint), by hand 4 with no `data-paid`, all in Osaka:
   0266's 43 monme (page and notes) and 4,300 mon (notes), Osaka 1702; 0286's rice of the 1700s (71.2). 4 to `osaka-1736`
   (0266, Edo 1737). Stayed `osaka-1700`: Edo 1710-1716 and Funai 1690-1737 by midpoint, every 1712-1735 year, and 0286's
   Osaka 1713 figures and its other decades (the 1690s' midpoint 1694.5, the 1730s' 1734.5). 0286's rice li lost its
   `data-era`; its ten spans each carry their own.
2. **kyoto-1745 to osaka-1780**, `data-paid` kept: 0273 Kashimo 32 (1763 to 1774, the group as the brief lists it, not split
   year by year), 0256 Osaka 1772 8, 0270 Osaka 1774 8 and Nagasaki 1774 3, 0268 Miyazu 1777 3; and 0256's Edo 1772-1773 2,
   which the list did not name but the rule covers (midpoint 1772.5, 7.5 years from osaka-1780). Tama 1764-1770 stays (0255
   3, 0268 1).
3. **Hamamatsu 1665** (0260, page and notes, 83, 54, 151 and 104 mon each): `osaka-1620`, `data-paid="Hamamatsu 1665"`, as
   the Takamiya fares; its per-ri figures (30 and 19 mon a ri) stay unmarked, as Takamiya's do. It had no own backfill line
   (it sat under 0260's `*` line).

## Gold bu and shu marked (55 spans, plus one compound in ryo)

- `kyoto-1745` (Tama 1749): 5 - "1 bu of gold" a Kasuga carpenter's 9-15 days, in 0255 and its notes, 0256 notes, 0257
  notes, 0273 notes; and 0256 notes' "43 ryo 1 bu" as 43.25 ryo.
- `osaka-1736` (Edo 1737): 2 - the Nakamura theater's 2 bu a bay of boxes, 0266 and its notes.
- `osaka-1780` (Kashimo 1765, 1774): 3 - 0273 notes.
- `edo-1818` (Osaka 1818-1830): 2 shu - the beka cart fee, 0278 and its notes.
- `edo-1830`: 36 - Morisada's 2 shu of a Kyoto inn (0259 and notes, Kyoto 1837-1853); the Edo tarudai and sekku-sen,
  "2 shu or 1 bu", and the arithmetic of them (0265 6, notes 4, Edo 1837-1853); the Shibasaki diary (0268 8 and notes 5,
  0269 5 and notes 3, 0270 2 and notes 1, Shibasaki 1840 or 1841, the joiner's Shimowada 1841, a "2-shu gift" included).
  Compounds as one span in bu: 2 bu 2 shu = 2.5, 2 bu 1 shu = 2.25, 3 bu 2 shu = 3.5.
- `edo-1860` (Fushimi 1864): 7 - the installation fees' 3 bu and 2 bu, 0258 and its notes.

## The compound gold-and-copper sums

- 0273 notes, Kashimo: "1 bu 756 mon" (Meiwa 2, 1765) and "1 bu and 400 mon" (An'ei 3, 1774, given twice) are marked as two
  spans each, the gold `bu` and the copper `mon`, at `osaka-1780`. The source gives no rate for 1765; for 1774 it gives only
  the total (27 days at 60 mon = 1,620 mon), which implies 1 bu = 1,220 mon but does not state it, so the sum was not put in
  one coin. Their two own lines ("the row has no unit for bu") are dropped.
- 0268's "2 bu and some copper coins" and "2 bu 1 shu and some copper coins": the gold marked, the copper uncounted.

## 0290-0294 (53 marks, 57 of the scanner's 89 amounts passed over)

- 0290: Osaka rice by year, `osaka-1700` 2 (1731, 1732), `osaka-1780` 4 (1782-1786), `edo-1830` 6 (`data-paid` Osaka 1835 to
  1840, the daily quotes of 1836-1837), `edo-1850` 1 (Osaka 1858), `edo-1860` 1 (Osaka 1866); Qian Yong's Suzhou rice,
  `suzhou-1750` 3 and notes 4 (1755, after 1755, 1785, and the 27-35 cash "from then on", as 0288 marked it); Songjiang's
  new rice of 1670, `songjiang-1680` 1.
- 0292: Kami-Kawarabayashi's 1.0 monme (`kyoto-1800`, Kami-Kawarabayashi 1802-1804) and Kyoto's 0.92, page and notes, 4.
- 0293: the Ministry of Works lists, `beijing-1615` 6 (1615, and the Wanli salt and wages) and notes 3; `beijing-1736` 7 (the
  1736 list, 75 cash and its 0.094 tael) and notes 1; Tao Shu's Jiangxi and Huguang salt, `canton-1835` 2 (`data-paid`
  "Jiangxi and Huguang about 1830"); the Huaibei license, old over 10 taels (`data-paid` "Huaibei before 1832") and the ticket
  salt's 5 (Huaibei 1832-1833), page 2 and notes 4; Kyoto's 0.86 monme of 1741-1762 (`kyoto-1745`) and 1.03 of 1818-1829
  (`edo-1818`).
- 0291 and 0294: nothing to mark.

## Passed over, a line each

- Area, length or fraction, not coin: every `bu` of 0005-0285 the brief names; 0251's paddy measures; 0256's 3 sun 5 bu
  nails; 0257's tsubo-bu; 0261's 9 sun 5 bu; 0268's 3 shaku 8 sun 7 bu; 0273's "9 bales 2 or 3 bu" (tenths of a bale, a
  clause added to its notes' `*` line); 0280's and 0281's "N shu M mi", shares of a cargo (a clause added to each `*` line).
- 0251 notes' "2 kan 964 mon 3 bu" of 1698: ei, a money of account.
- 0287 notes' mintages ("13,936,220 ryo 1 bu"): coin counted as struck.
- 0276's polishing fee of 1662, 6 and 8 bu a sun: outside every era's years.
- 0268 notes' Fukuchiyama 1 monme 5 bu: silver, no year (its line stands).
- 0115's servant wage of 2 ryo 2 bu: no year; its four lines now give only that reason.
- 0258's "the 3-bu grade" and "the 20-ryo grade": grade names, left unmarked like the 20-ryo before.
- 0290 and 0293: price changes and drifts (0.001 tael raised in 1732, 0.067 tael a decade, the 2-cash cuts of 1791, 1848,
  1858); rates between coins (1,000 and 2,000 cash to the tael, 2,205 and 4,970 cash to the tael, 1 ryo = 1 yen in 0294);
  Songjiang rice of 1642 and 1651 and cotton and cloth of 1644-1654, Qian Yong's rice of 1707, rural Beijing's wage of 1807
  and 1853, and every Song price and wage (before 1068 to 1181), all outside every era's years; Gao's "old rule" wages (no
  year); Kyoto's 0.85 monme of 1791-1817, Edo's 0.91 of 1830-1858 and the 0.85-1.03 of 1741-1858, spans crossing several
  eras. Each fragment's `*` line names them.

## Could not decide, for the GM or gm-assistant

1. Kashimo's single years 1763 and 1765 (4 amounts in 0273) moved to `osaka-1780` with the group, as the brief and #13 list
   "Kashimo 1763-74"; by each amount's own year they lie nearer `kyoto-1745` (9 and 11 years against 17 and 15). A per-amount
   reading would move them back.
2. 0293's row of the 1830s gives rural Beijing's "88 local cash in 1827 and 91 in 1838 (44 and 45.5 standard cash)"; the
   scanner does not see "local cash", and which count `beijing-1820` and `canton-1835` mean is session 6's open question
   (1), so they stay unmarked.
3. "Rice stayed near 74" (0293, 1818-1829) names no coin in its sentence; left unmarked.
4. The 2 kan mon beside the theater's 2 bu (0266 notes) is the same sum restated in copper; only the bu is marked.

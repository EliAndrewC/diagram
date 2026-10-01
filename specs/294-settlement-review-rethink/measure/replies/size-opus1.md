The privy on hoshigaoka-shrine is drawn about 2.3 times too large on each side (about 5.4 times the area), so the verdict is **NEEDS-WORK**. On main it was drawn at 5 ft, so this revision made it bigger.

```
UNIT: size-audit--latrine   KIND: latrine   SHEET: hoshigaoka-shrine
privy (308,425; the only instance): drawn 14.0 x 14.0 ft (42 x 42 px, 196 sq ft) -> anchor 5 x 5 to 6 x 6 ft
  (5 shaku x 5 shaku to 1 x 1 ken; household records of 1885 in a municipal history, read there as the farm scale
  at the end of the Edo period - recorded dimensions) -> ratio 2.3 per side, 5.4 by area -> WRONG
BAND TO RECORD: latrine: 4.5-9 ft per side - Oamishirasato town history, table 18 (5 shaku square to 1 ken square,
  up to about 1 x 1.5 ken for a privy with its paired urinal)
VERDICT: needs-work
```

**ERRORS**
1. **The privy is the wrong size** (norm: the size of a privy for one household). It is drawn 14 x 14 ft. The [Oamishirasato town history](https://adeac.jp/oamishirasato-city/texthtml/d100010/mp100010-100010/ht011770) lists privies of 「雪隠　1　5尺　5尺」 (5 shaku square, about 5 x 5 ft) and 「雪隠　1　1　1」 (1 ken square, about 6 x 6 ft). On main this privy was 15 x 15 px (5 ft), which was right. The fix is about 15-21 px square (5-7 ft), still attached at the back corner of the west gable.

**QUESTIONABLE**
1. **The large privy buildings belong to a different form** (norm: a size range written for one function does not cover another). The same table lists privies of 3 x 2 to 4.5 x 2.5 ken (about 18 x 12 to 27 x 15 ft). The page calls a farm's privy 「貴重な肥料の供給所」 ("a supply point for valuable fertilizer"). A surviving late-Edo privy at the Wada house in Shirakawa is also large: 「桁行7.3m、梁間4.3m」 (about 24 x 14 ft) ([Cultural Heritage Online](https://online.bunka.go.jp/heritages/detail/155645)). The monk's household privy on this sheet is attached to a one-roof hall that has only a kitchen garden to supply. Those large buildings do not justify 14 ft here. If a sheet ever needs a farm privy building, it should be its own kind with its own band, not a wider band for `latrine`.

**CONFIRMATIONS**
1. **The 4.5-9 ft band fits every existing latrine.** It agrees with `buildings.md`'s own figure of about 14-20 px (4.7-6.7 ft). Every latrine on the three magistracy sheets falls inside it (14-22 px, 4.7-7.3 ft), and so does this shrine's 5 ft privy on main. I did not review where the privy is placed; that is outside this unit.

The gate printed `green` before and after the review. The verdict line printed:
`recorded NEEDS-WORK for size-audit--latrine (engine key NONE - no dispatch recorded, gate green)`
The "no dispatch recorded" part is consistent with the dispatch's "Engine key: not computed".

Sources:
- [Oamishirasato town history (adeac.jp)](https://adeac.jp/oamishirasato-city/texthtml/d100010/mp100010-100010/ht011770)
- [Wada house privy, Cultural Heritage Online](https://online.bunka.go.jp/heritages/detail/155645)
- Searched, but they give no privy dimensions: [Japaaan](https://mag.japaaan.com/archives/55054), [Kotobank 雪隠](https://kotobank.jp/word/%E9%9B%AA%E9%9A%A0-547851), [Wikipedia 日本の便所](https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E3%81%AE%E4%BE%BF%E6%89%80)

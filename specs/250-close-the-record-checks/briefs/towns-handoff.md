# Handoff - feature 250, page `towns` (T04), session 1 -> session 2

Session 1 located, read and wrote. Nothing was checked, ticked or pushed.

## Changed questions

- SECTION=040 (the market-day flophouse - who actually stays over)
- SECTION=080 (the gate market exists for TRAFFIC, not taxes)
- SECTION=090 (a street is access infrastructure for the buildings it serves)
- SECTION=100 (a rampart's cost scales with its LENGTH)
- SECTION=130 (how is a town farmstead laid out?)

All are under the 20,000-byte cap (`scripts/check-question-size.py` names none), so nothing was split.

## Registry keys

- KEY=thepaper-night-gates (NEW, `9490-thepaper-night-gates.html`; a 2020 国家人文历史 article on The Paper about the night curfew and city gates). It needs source-applicability.
- Existing keys newly cited: KEY=kichinyado-jawiki (note `kichinyado-jawiki-4`), KEY=jishi-zhwiki and KEY=caoshi-zhwiki (note `jishi-zhwiki-2`), KEY=desire-path-enwiki (notes `desire-path-enwiki`, `-2`, now on 090's roster), KEY=thepaper-city-walls (note `thepaper-city-walls-2`), KEY=visit-toyama-sankyoson (note `visit-toyama-sankyoson`, now on 130's roster). `jishi-zhwiki` is on 080's roster, and `thepaper-night-gates` is on the rosters of 040 and 080.

## FR-002 items

| item | form | note |
|---|---|---|
| 040 spec: "large, plain and barn-like" | citation (partial) | `kichinyado-jawiki-4` - 最下層の旅籠, 大部屋; the gloss says the page does not describe the building's outside |
| 040 spec: "no awning, a long row of plain doorways ... beds dozens on market eve" | absence | `the-market-day-flophouse---who-actually-stays-over-2` - no frontage or nightly count on ja.wikipedia 木賃宿, kotobank 木賃宿 or the MLIT Tokaido Q&A; the 1932 Tokyo figures are a YEAR's total |
| 040 spec: "since the gate shuts at dusk ... cannot get in" | citation (partial) | `thepaper-night-gates` - 日暮鼓八百声而门闭, the outer wall's gates (外郭门) barred by night checkpoints, late-Ming gate watch; the gloss says the county town and getting IN are the page's extension |
| 080 "the market-day chokepoint where the rural catchment trades" | citation (partial) | `jishi-zhwiki-2` - 集市 rural, periodic, 買賣雙方都以附近村民為主; 草市's 前身 is the rural periodic market; the gloss says "chokepoint at the gate" is this page's reading. The same sentence's dusk clause now also carries `thepaper-night-gates-2`, and its wording is rewritten to match what the source says: ward gates closed, outer gates barred |
| 090 "paved or worn into the ground by the foot traffic" | citation (partial) | `desire-path-enwiki` - "formed by erosion caused by human or animal traffic"; the gloss says paving is not on the page |
| 090 "a desire path forms only between real destinations" | citation (partial) | `desire-path-enwiki-2` - "shortest or the most easily navigated route", "convenient shortcuts"; the gloss says "only" is this page's reading |
| 090 hutong quotation observation | already fixed | the prose quotes the page verbatim, which source-reader confirmed (G1/G2). I removed the stale session comment that recommended the fix from the `hutong-enwiki` note |
| 100 "its cost scales with its length" | absence | `a-ramparts-cost-scales-with-its-length` - the two cited pages price no wall. The nearest passage is Beijing's Jiajing-era outer wall, cut short 由于经济不济, and the note names it. The visible "(this page's reasoning ...)" label stays |
| 100 spec: "a wall climbs or skirts a hill rather than leveling it" | citation (partial) | `thepaper-city-walls-2` - 将周围的制高点纳入城内; the gloss says leveling is mentioned nowhere |
| 100 "no empty ground" in source brackets | already fixed | it is now `<em>`, not 「」; nothing written |
| 130 "a farmer builds close to the ground they work" | citation | `visit-toyama-sankyoson` - Tonami farmers built "in the middle of their cultivated rice fields so that they could easily manage the water". The "(this page's reasoning)" label is removed. The gloss says the ring outside the wall is this page's application |

source-reader, one dispatch over `/tmp/l7r-check/towns-pages/`: 8 READ, 4 NOT-FOUND (frontage, nightly count, cost per length, leveling), 0 CONTRADICTED. Each NOT-FOUND is exactly what an absence note or a partial gloss states.

## FR-006

- none owed.

## Open for session 2

- quote-check and record-format on SECTION=040, 080, 090, 100 and 130. source-applicability on KEY=thepaper-night-gates, a popular magazine article about Tang Chang'an: is it fit for a county town's gate?
- Several citations are partial and each says so in its gloss. quote-check may call them PARTIAL. If a gloss is not enough, the fallback is an absence note for the unsupported half.
- For the GM, through escalation-check: the flophouse spec's "beds dozens on market eve" rests on no source. The only count read, from Tokyo in 1932, averages about two lodgers per house per night. That figure is modern and says nothing of a market eve, so it does not refute the spec, but nothing supports "dozens" either.

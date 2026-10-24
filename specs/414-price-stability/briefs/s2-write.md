# Brief - feature 414, how stable prices were. Session 2: write (new questions B and C)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** Issue EliAndrewC/diagram#15 (verbatim in `specs/414-price-stability/request.md`): how far prices differed from
place to place at one time (question 3), and - the GM's addition on question 2 - each good's price in each period the record can
reach, in a common measure, how far apart the periods were and what drove the difference, salt and its monopoly first. Your
passes: `passes/japan.md`, `passes/qing.md`, `passes/salt-periods.md` (leads, not citations). This project's arithmetic:
`measure/mitsui_stability.py` (city spreads, 1818-1858) with its `.out.md`. Session 1 wrote question A: read `briefs/handoff.md`.

## Your items

- `B` **"How far apart were prices from one city or village to the next?"** (new). The literature's co-movement (Shinbo: Kyoto
  and Osaka in parallel; Takatsuki 2012: Otsu following Osaka within 1-2 days; Bassino and van der Eng: the east diverging more;
  Shiue and Keller: Qing rice correlations by distance); level spreads as this project's arithmetic from Mitsui (rice in Osaka
  within about 1% of Kyoto, Edo about 3%; firewood a third below in Edo, 43% above in Osaka; Kyoto salt's break named and left out);
  Iwahashi's rice in 14 places (GPIH `Japan_rice_P_1620-1867.xls`, castle towns among them; compute the spread across places by
  year, a script in `measure/`, labeled); town against country (Saito's village and Kyoto wages; 0273's Kashimo against Kyoto),
  SILENT where no source sets them side by side; China's levels (Allen et al.: Beijing, Canton, Suzhou about the same in silver in
  the 1700s). 0280-0283 named for carriage and distance, not repeated. Against its canon: gm-assistant's eras are each one place.
- `C` **"How did a good's price change from one dynasty or era to the next, and why?"** (new). Salt first, in days of an unskilled
  wage per local unit (the pass's arithmetic): Song about 1.2-1.75 days a jin (ATTESTED ONLY FOR a second-hand wage of 40-50 cash,
  its rice measure beside it: a jin of salt about a dou of rice before 1068, a fifth by 1122 - 宋史 卷182), Ming about 0.2
  (Wanli), Qing about 0.13 at Beijing in 1736 and 0.35-0.8 in the far Huai markets about 1830 (ATTESTED ONLY FOR a rural Beijing
  wage, a different region), Edo 0.14-0.5 days a sho (0273, named); Japan and China side by side, not converted (no source gives
  a sho of Edo salt's weight). The drivers the sources name: the Song monopoly's reach (Hebei doubled in 1084), private salt a
  third under official (1086), the Ming license price tenfold by 1534, the Qing official-private gap (60-70+ against about 30
  cash), the 2-cash cuts of 1791 and 1848, the ticket reforms of 1832 and 1849, Japan's domain monopolies (Kanazawa, Sendai, Ako
  1680- and 1809-1821). Other goods: 高壽仙 2022's Beijing official prices of 1615 against 1736 (food and fuel about doubled,
  cloth flat, pig iron down); 閱世編's Songjiang cotton and cloth; Peng's silver purchasing power (via 高壽仙); Mitsui's goods
  across the Edo sub-periods with the drivers named (harvests, recoinage, 1859). Against its canon: the standard basket and the
  day wage.

**New registry keys** (at most ten): 宋史 卷181-183, 明史 卷80 (check the archive first), 吳海波, 高壽仙 2022 (check), kotobank 藩専売制
and 赤穂塩田, Takatsuki 2012, Bassino and van der Eng (abstract only: cite only what a readable page gives), Iwahashi's GPIH file,
閱世編 (check) - the rest to the continuation brief.

## The procedure (session 2: write)

Steps 1-6 as session 1's, with questions `<B> <C>`, commits opening `414: `, and a `## Session 2` handoff section.

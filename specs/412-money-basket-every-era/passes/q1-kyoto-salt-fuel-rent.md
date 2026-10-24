# Pass q1 (feature 412): Kyoto/Osaka salt, firewood, rent, salt use, 1745-1754

research-pass agent, 2026-10-24; filed by the session (the agent writes nothing).

## Sources

1. Mitsui Bunko Kyoto retail prices (Table 6) as transcribed in Japan_1710-1871.xls, https://gpih.ucdavis.edu/files/Japan_1710-1871.xls
   (J.-P. Bassino 2006, appendix to Bassino & Ma 2005; from 三井文庫『近世後期における主要物価の動態』1989). Read with xlrd.
   - Sheet notes, verbatim: "Retail prices in local physical units and daily wages of unskilled workers (hiyatoi) recorded by branches
     of Mitsui House in Kyoto, Edo (Tokyo) and Osaka; monetary unit: silver monme"; "Quarterly average (Spring and Autumn), probably
     based on daily prices".
   - Headers: `塩 | 1石ニ付 | 銀匁` (salt per koku, silver monme); `薪 | 10貫匁ニ付 | 銀匁` (firewood per 10 kanme).
   - Salt 1745-54 (spring/autumn): 1745 19.62/25.69; 1746 20.23/19.61; 1747 18.81/18.67; 1748 18.05/19.65; 1749 17.13/19.44;
     1750 15.27/14.81; 1751 17.3/14.3; 1752 16.1/14.54; 1753 16.14/14.65; 1754 17.86/17.53.
   - Firewood 1745-54: 1745 2.67/2.55; 1746 2.55/2.62; 1747 2.73/2.76; 1748 2.63/2.59; 1749 2.56/2.54; 1750 2.61/2.58;
     1751 2.76/2.58; 1752 2.42/2.70; 1753 2.77/2.66; 1754 2.76/2.77.
   - Day laborer 日雇賃 1人ニ付, same rows: 0.72-1.31 monme.
   - Other sheets: Edo per 10 kan 炭 7.25-16.64, 薪 2.73-4.67 (1710-16); 炭 ~5.0, 薪 2.0 (1818-20). Osaka 炭 3.1-3.7, 薪 3.3-3.9
     (1818-23); salt 15-20 monme a koku. Kyoto has no charcoal column.
2. 黄国信「市场导向与行政理性：清代盐政运作的原则和机制」《深圳大学学报》2021 no.1, https://ha.sysu.edu.cn/article/90 :
   「综合嘉庆《两广盐法志》、《元史》和《明史》的3个数据，清代人均食盐消费量应该在今市秤11斤也就是当时的计量9斤多。」 Shandong 1783: 6.35 jin
   per head (quota / population).

## Readings

- Salt price: ATTESTED, Kyoto 1745-54 retail in silver. 20-season mean 17.8 monme a koku (~0.18 monme a sho), range 14.3-25.7.
  ~12 mon a sho at 66 mon/monme (Osaka 1766, 0277; arithmetic). No period weight of a sho of salt found (塩 一升 目方; 赤穂 四斗俵 貫;
  塩 一俵 重さ; archived 俵).
- Firewood: ATTESTED, Kyoto 1745-54, priced BY WEIGHT. Mean 2.64 monme per 10 kan (37.5 kg) = ~0.070 monme a kg, range 2.42-2.77.
  Per million BTU (arithmetic, modern assumption ~15 MJ/kg air-dry): ~70 kg, ~4.9 monme. Units are Bassino's transcription.
- Charcoal: ATTESTED ONLY FOR Edo 1710-16 and 1818+, Osaka 1818+. FLAG: Osaka 1818-23 charcoal cheaper per 10 kan than firewood -
  check the unit against the book before citing.
- Rent: SILENT for Kyoto and Osaka (京都 裏借家 家賃 銀 匁; 近世京都 借家 家賃 論文; 杉森哲也/塚田孝 借家 店賃; 三井 京都 貸家 家賃;
  osaka-angenet Tsukada lecture - no amounts). Edo 300-500 mon (0265) stays nearest.
- Salt per person: ATTESTED ONLY FOR Qing official reckoning, a little over 9 jin (~5.4 kg, arithmetic) a year, 1776-1850.
  Japan SILENT (yanagihara.pdf production totals only; mealtime.jp SSL-refused; 一人一年 塩, 渡辺則文, 廣山堯道, 塩業史 no hit).

## Leads not followed

- The 1989 Mitsui Bunko book (confirm 10貫匁 for 薪/炭).
- 黄国信 2017《中国经济史研究》2017 no.4 (verbatim 两广盐法志 卷19 「每日口食不过三钱」).
- Kashimo diary (0273): 52 sho of salt bought one day of 1772 - with household size, a yearly use.
- 0277's Edo table from 1751: a closer copper rate than 1766.

Downloads: /tmp/l7r-pass/gpih-xls-raw/mitsui.xls, kumon.xlsx

# Implementation Plan: the work a household did that was never paid, who did it, and how long it took (feature 431, diagram#21)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-26

## Summary

A research-record feature answering the GM's seven questions from five search passes (`passes/a-japan-household.md`,
`b-china-household.md`, `c-fiber-chain.md`, `d-city-and-days-off.md`, `e-proverb-and-historiography.md`). Two write sessions,
each followed by a check-and-apply session, in two clones side by side, their registry keys disjoint: this clone,
`/diagram/.clones/diagram-money-research` (S1: the farm household's unpaid work and the fiber chain - passes A, B and C, which
share Tanimoto, Nagashima and Pomeranz), and `/diagram/.clones/diagram-money-research-2` (S2: city households, other workers'
days off, the proverb and why the record is thin - passes D and E). Then the reply on #21. No code, map or canon change.

## Technical Context

- **The passes** are leads, not citations: each write session reads every passage on its page before citing it. Pages the passes
  read through local copies (Tanimoto's and Pomeranz's LSE drafts and the Hitotsubashi PDF by pdftotext, Nagashima 2017 and the
  JAS 2003 exchange as page images) go through `make source-pages` or the archive; an image-only page goes to the checks with
  `IMAGES=`.
- **Drafts and secondary readings** are cited as what they are: Tanimoto's and Pomeranz's conference drafts carry "not to be
  quoted" headers (cited with the header said, the published versions on the leads list); Bray through Waltner's review; Furukawa
  through 0311's summaries; Nagahara's tenfold ramie figure through Nagashima and Tanimoto; the Seiryoki through the Sukumo city
  history and Nagashima; the Keian edict through modern paraphrase, its 1649 date disputed (the Gunma archives).
- **Who owns each shared source** (the two writes run side by side): S1 holds Tanimoto, Nagashima, Pomeranz's draft and Allen
  et al.; S2 holds the Keian edict pages (S1 names night work from Tomioku and Nagashima without them). A key the other session
  needs is named by file in its brief as the other's, never reserved twice.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - the farm household's unpaid work (Q1, Q2; FR-001)

A new money question, its title asking what work a farm household did that was never paid, with pointers from 0311, 0004 and
0183. Japan: the Seiryoki's annual man-days for one cho 2 tan 5 se (293 male and "over 200" female field days a cho of paddy,
night work uncounted; fuel 120, ox and horse care 120, fertilizer grass 40, silkworms 20, house repair 20, ditch dredging 20,
tool and mat-and-rain-cape materials 12, tea 10; 811 in all) - ATTESTED ONLY FOR one Iyo farm book of the mid-17th century,
through the Sukumo city history; its peasant wife "like an actor playing every part" (through Nagashima); Nagashima's division
of tasks and women's wages (the Imai accounts of 1821, the Muramatsu house rules); the Tomioku memory of women's midday work and
yonabe (Meiji-Taisho, labeled); Saito's 1879 Yamanashi by-employment shares; Kumon's 310-330 days and the rest days by file
(0311). China: the Shen-shi nongshu's rainy-day work for hired men and rope at 5-8 jin a day (c. 1640); the Bu nongshu's two
women weaving 120 bolts of silk a year and a man working ten mu (1658); Buck's productive man-work units (1921-25: about a fourth
of the year, women 31.6% of farm labor in East Central China, 11.8% in the North, ATTESTED ONLY FOR 1921-25; household and repair work excluded); Fei's
Kaixiangong (1936: women out of the fields, sewing at home, cloth bought); Lu Village through Hu Yukun (third-hand, labeled). Per
member by hours: SILENT with the searches. The task list covers every item of the request's starting list and whatever the sources add, each with who did
it and its time, or SILENT: hemp or cotton growing, retting, spinning, weaving, dyeing, sewing, araihari, mending; hulling and
polishing rice, cooking, pickling, miso and soy; firewood, charcoal, water; straw rope, sandals, mats, rain capes, bags; roof, wall
and tool repair; care of children, the sick and the old. The GM's hypothesis, both halves, said to be tested on the CLOTH stage only (growing,
dyeing and sewing SILENT, so the cloth days are a minimum for "making clothes"): cotton era
NOT ATTESTED for clothing as the largest claim (about 51 days a year of household cloth, Tanimoto, against 200-plus female field
days a cho); hemp and ramie era ATTESTED ONLY FOR an estimate (Nagahara's tenfold, through Nagashima; any days-a-year product
of it this project's arithmetic, labeled); Jiangnan's textile year about level with a man's field year (Li and Pomeranz, for
cloth made for sale); fieldwork larger in total ATTESTED for Japan, NOT ATTESTED for Jiangnan. The record says, where women's
household figures are missing, that the work was rarely written down and why, pointing at D4. Against the canon (`make canon`):
`budgets.md`'s peasants weaving waraji and umagutsu "the same evening" matches the attested night work; `l7r.md`'s silk "heavily
gendered", women harvesting and boiling cocoons in the 5th month, matches the women's sericulture of the Bu nongshu and Fei; its
family of five on 7.5 koku providing the rest of its needs itself is unmatched by a time figure, not contradicted.

## D2 - the fiber chain in hours (Q3; FR-001)

A new money question, its title asking how long it took to make cloth, with pointers from 0209 and 0306 and from D1. Cotton from
ginned fiber: 4 days a tan (spin 2, prepare 1, weave 1; Niikawa, mid-19th century; a tan about 0.35 x 11 m, ATTESTED ONLY FOR Tanimoto's definition), 12.8 tan a year for
a household of about five (51.2 days) and 39.4 for sale, one woman about seven months (Tanimoto); China about 7 days a bolt with
hand-spun yarn (6 in one place - the draft disagrees with itself, both given), 3 with machine yarn, spinning about four hours to
one of weaving (Pomeranz's draft and the JAS 2003 exchange); a woman's 200-day maximum (Allen et al., Li); the Songnan poems on
women hoeing by day and spinning by night (through Zheng Tianting, c. 1800). Single steps: silk reeling 30 liang a day, ramie
splitting 3-5 zhu a day (Tiangong kaiwu, 1637). Hemp and silk per tan in Japan, growing the plant, dyeing and sewing a robe:
SILENT with the searches. Bought against made: Akita 1808-10 (cotton cloth bought, ginned cotton spun and woven at home, used
cloth, home-grown hemp; the shares and the 1.23 tan a head this project's arithmetic). Units kept as each source gives them; any
per-square-meter comparison is this project's arithmetic. The European experiments (Mannering 2021, Bender Jorgensen 2012) are
cited as the request permits ("a measured modern craft rate is acceptable as a COMPARATIVE source where no period figure exists";
FR-001): in their own question in the "Comparative money" section, `subject=comparative,money`, their source kind `comparative`,
labeled as wool on a warp-weighted loom, the comparison for the SILENT hemp and silk stages - Bender Jorgensen only if more than
the abstract is readable; S1 also searches for a measured modern rate in hemp, ramie, cotton or silk (Japanese and Chinese craft
studies first) and records it or SILENT. Their limits stated: wool, a warp-weighted loom, a modern experimenter, never a Rokugani figure.

## D3 - city households, and other workers' days off (Q4, Q5; FR-001)

A new money question, its title asking what a city household bought that a farm household made, with pointers from 0183 and
0004. Edo: polished rice (only the polishers sold white rice; about 2,100 polishers in 1744, 1,100 street polishers in 1727);
the Bunsei budgets (a peddler's daily rice, miso and soy and a child's sweets; a carpenter's 128 monme a month, seasonings and
firewood 58), through the modern paper summarizing the Bunsei-era manuscript; bath fees (8 mon from 1841 to 24 in 1866) through
the article reporting Morisada; the tenement's shared well, no bath, and the wives washing and rinsing rice at the well; used
cotton clothing; water sellers in many cities until early Meiji; washing shops from about 1688 (whose clothes SILENT). Home-work
days a year for a single tenement laborer and for a family household: SILENT with the searches; the one single-against-married
contrast, a journalist's unsourced line (nippon.com 2020: married men worked every day, single peddlers idled), is GIVEN, labeled
as unsourced, because it is the only statement on the comparison the GM asked for; who did the household's work: the wives (the well scenes).
Rental shops: a popular page with no source - a lead, not a citation. Kyoto and Osaka: the Morisada paraphrase on baths only.
China: SILENT beyond Beijing's two water-carrier systems. Q5 extends 0311: merchant-house live-ins' days off were the two
yabuiri with pocket money and new clothes; no household of their own until head clerk; a Kyoto house's Edo staff first home in the
ninth year (chapter titles of a book on Shirokiya's papers, cited as that); a side trade SILENT; porters, guards and footmen SILENT
with the searches.

## D4 - the proverb, and why the record is thin (Q6, Q7; FR-001)

A new money question, its title asking why women's household work was so rarely recorded, with pointers from D1 and D2. Japan
ATTESTED: Makihara 2020 (the records were written by male officials for governing) and the Hitotsubashi survey of 2007 (headmen's
diaries, temple registers, commendation records, prescriptive texts as the historians' sources); China ATTESTED ONLY FOR narrower
statements (Bray through Waltner: cloth taxed in kind until the Single Whip reform, then "masked"; Pomeranz on Li Bozhong's narrow
documentary base; Li Shizhong on gazetteer biographies shaped by gentry virtue). The GM's addendum carried as the question's
point: this is itself a fact about what we can know. The proverb, in the same question's neighbor or its own small question by
size: the 360-day form SILENT; its halves ATTESTED ONLY FOR the farming almanac of Lu Mingshan (begun 1314, addressed to those who
farm: rise in the hour before dawn, three early mornings make a day's work, a lifetime's plan lies in diligence) and Lou Yue's
poem (before 1213: the line already a saying); Zhu Yongchun's household rule (rise at first light; a gentry rule, nothing on
wealth); the Zengguang xianwen lines undated by layer, not cited as premodern unless dated; the Keian edict's "rise early" as a
late-Tokugawa official text, its date disputed. The original text is carried for each attested part (the almanac's 一日之計在寅…早起，三朝當一工…一生之計在勤, Lou Yue's
早起三朝當一工), translations marked. The GM's guess (a farming saying) ATTESTED by the almanac's audience. Japan's
early-rising proverb's origin: SILENT.

## D5 - the implementation check and the reply (FR-003, FR-004)

`implementation-check.md` holds each touched question's line; the reply on #21 gives each figure with its fragment file and
verdict, what is still open (the leads: Smith 1969 and Nishikawa 1978 on Choshu, Nagahara 2004 p. 212, Li Bozhong 1996-2008 and
*Agricultural Development* pp. 139-152, Xu Xinwu, Walthall 1991, Nagashima 2006, Hayami's industrious revolution and Bray's *Technology and Gender* (both
named in the request; Hayami's own work not reached, Bray read only through Waltner's review), the 日本農書全集 manuals, Bunsei-era manuscript
and Morisada in the original, Hokuetsu seppu). Anything for the GM goes through
`escalation-check` first.

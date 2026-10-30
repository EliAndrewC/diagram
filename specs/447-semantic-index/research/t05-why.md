# T05 why the four runs reported different sources (the GM, 2026-10-30: "analyze why it is that we got different results")

Method, one-shot 2026-10-30: `analysis/why.py` reads each run's transcript (arm S, arm T, validations 1 and 2) and, for each of the
twelve target sources and three others, marks SEEN (its id in any tool's output), OPENED (its id in a tool call's input) and
REPORTED (its id in the final report); `analysis/why2.py` prints what a run was shown for the sources it dropped. The table is
`t05-why-table.txt`. (OPENED undercounts: a grep over the whole archive reads a file without naming it.)

## Where the twelve were lost

| run | never seen | seen, not reported |
|---|---|---|
| S | Shicang, Shiroyone, Ofuro | Yayoi, Hattori, Konosu |
| T | Shizuoka, Hattori, Ofuro, Konosu | Huizhou |
| V1 | Shiroyone, Ofuro, Konosu | Huizhou, Yayoi, Hattori |
| V2 | Shicang, Huizhou, Konosu | Shizuoka, Hattori, Ofuro |

Thirteen losses before the source was seen, ten after: the two halves weigh about the same.

## Why a seen source was dropped

1. **The passage shown was not the one that answers** (Hattori three times, Ofuro, Huizhou twice, Bray in V1, Konosu in S). The
   combined search prints one passage a source - the one nearest the question's meaning, or the text around a term's first
   appearance - and the agent judged the source from it. Hattori was shown a passage on the texture of the paddy floor; its sizes
   ("小さいもので10㎡ほど、大きいもので180㎡程度") are elsewhere in the file. Ofuro was shown its page's opening; Huizhou a debate on
   whether the registers were surveyed, not its 0.715-mu parcel; Bray a passage on rice's domestication, not "a field twenty yards
   square would be considered large". In S, Konosu appeared only as a file path in a grep's list, with no text at all. A meaning
   match finds the right DOCUMENT and shows the wrong PASSAGE: the question is about a size, and the measure of nearness is weak on
   numbers.
2. **Each run drew its own line on scope** (Shizuoka 1872 out in V2 as Meiji, in elsewhere; Buck's holdings out in T and V1; Yayoi
   plots out in S and V1 as too early). The brief said "premodern" and left the agent to decide; four agents decided four ways.

## Why a source was never seen

Each run wrote its own wordings and terms, and a source turns up only for the words that reach it: T, with text search alone and
its own terms, never met Hattori, Ofuro, Konosu or Bray; Konosu was seen once in four runs, Ofuro once. Which sources a run meets
depends on the words its agent happens to choose.

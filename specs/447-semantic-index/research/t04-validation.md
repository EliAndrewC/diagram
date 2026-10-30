# T04 the end-to-end validation of `make research-search` (amendment 3, SC-A3)

Run 2026-10-30, a `research-pass` agent on feature 444's field-size question, the brief of arms S and T but for the search tool
(`make research-search` under KEY=field-size-validation, then Grep and Read; archive and record only, no web, at most 40 calls).
Its usage, from its completion notice:

```
<usage><subagent_tokens>63827</subagent_tokens><tool_uses>22</tool_uses><duration_ms>222943</duration_ms></usage>
21 Bash calls, of which 3 were research-search and 18 were greps and reads run through Bash and Python. Grep tool 0, Read tool 0, advisor 1.
```

What the command printed (60 sources, read from `/diagram/.specify/search-seen/field-size-validation.json` after the run) and
what the agent reported, against SC-A3's list:

| source | SC-A3 group | printed by the command | in the agent's report |
|---|---|---|---|
| Shicang 1898 `83/831d8174fa8b` | SOME/HIGH | no | yes (its own grep) |
| Shizuoka 1872 `e5/e542a5322e62` | SOME/HIGH | yes | yes (as not premodern) |
| Huizhou 1581 `04/04c46c135344` | SOME/HIGH | yes | no |
| Shiroyone `f4/...`, `56/...` | SOME/HIGH | no | yes (through record 0005) |
| Yayoi small plots `d1/d1f4b30193e3` | SOME/HIGH | yes | no |
| Iwamuro 1602 `75/7588a47ce738` | both arms | no | yes (its own grep) |
| Kami-Baba 1684 `27/27341e70863d` | both arms | no | yes (its own grep) |
| King `e8/e81890ad0ea3` | both arms | yes | yes |
| Taipingqiao 1897 `29/29423acf58a9` | both arms | yes | yes |
| Hattori `97/97f6d769ce72` | both missed | yes | no |
| Ofuro `10/100916836bb9` | both missed | no | no |
| Konosu 1902 `c3/c36ae8c62a1c` | both missed | no | no |
| Fei Xiaotong 1936 `67/675c43301bf7` | new: in neither arm | yes | yes |

Printed by the command: 6 of the 12 (Shizuoka, Huizhou, Yayoi, King, Taipingqiao, Hattori); with the agent's own greps and record
0005, 10 of 12 surfaced; reported: 7 of 12 - the same count as arm T - plus one new source neither arm found (Fei, Kaixiangong,
"few belts are above six mow ... most of them are not more than one or two mow"). Three the command printed were never opened
(Huizhou, Yayoi, Hattori); Ofuro and Konosu were neither printed nor found. The agent's report says the key "still holds about
159 sources that were never printed" (three calls under the key); this record does not hold that count otherwise.

**SC-A3: partly met.** The search surfaced more of the list than either arm, but the agent read only part of what it printed - the
contract already said to read what the command names -
and its tokens and time (63,827, 223 s) were above both arms' (51,261 and 59,011; 127 s and 201 s).

# T02 the blind judge of the two arms (amendment 1)

Run 2026-10-30, a general-purpose agent on opus, told only "Report A" (arm S, with the index) and "Report B" (arm T, today's search),
never how either was made; it opened each finding unique to one report, spot-checked two shared ones and searched for what both
missed. Its usage, from its completion notice:

```
<usage><subagent_tokens>65326</subagent_tokens><tool_uses>13</tool_uses><duration_ms>101031</duration_ms></usage>
```

Its verdict, verbatim: "Report B gives the one direct measurement of named premodern Chinese bunded fields (about 0.47 mu per qiu
at Shicang), and it takes its terrace and Yayoi figures straight from the source rather than through the record. Report A adds a
useful Meiji figure (2-3 se at Shizuoka), but its most prominent China number, Buck's 0.34-0.39 ha average and 5.58 ha largest,
measures separate holdings of one or more fields and would give a wrong answer for "at its largest". Neither report has a sound
"largest single plot" figure for either country. Report B is better on Chinese plot-level evidence and avoids Report A's
misleading figure."

Its ratings of the unique findings: arm S - Shizuoka 1872 SOME, Buck LOW (misleading), the unopened Huizhou lead SOME (a 1581
parcel of about 0.715 mu), the library lead LOW; arm T - Shiroyone SOME, Yayoi SOME, Shicang 1898 HIGH, Wanchun LOW. What both
missed: Hattori (`97/97f6d769ce72`, Yayoi plots of 10-180 m²), Ofuro (`10/100916836bb9`, 3-5 m²), Konosu 1902
(`c3/c36ae8c62a1c`), a modern 3-tan standard (`71/71ad2d8933fa`).

## The measurement, together

| | arm S (with the index) | arm T (today's search) |
|---|---|---|
| tokens | 51,261 | 59,011 |
| wall time | 127 s | 201 s |
| tool calls | 14 | 22 |
| the judge | worse: one misleading headline figure | better: the one direct premodern Chinese measurement |

One run of each arm on one question: the 13% in tokens is inside what two runs of one brief can differ by, so it is a reading,
not a result.

## A correction on reading (2026-10-30, after the GM asked what exactly went wrong)

- Arm S did not misread Buck: its own report says, beside the figure, "Its 'plot' is a holding that can hold several bunded fields,
  and the figures cover dry farms in North China too" (arm S's finding 9, in the session). The judge marked the figure misleading
  as a headline; the arm had stated its limit.
- Each arm found sources the other did not: arm S Buck, Shizuoka 1872 and the Huizhou 1581 parcel (unopened); arm T Shicang 1898
  and Wanchun. Neither report was put through the record's checks (quote-check, source-reader, source-applicability), which run
  when a pass's findings are written into a page; the judge graded the raw passes.

# T02 arm S - the field-size question with today's search plus `make semantic-find` (amendment 1)

Run 2026-10-30, a `research-pass` agent, its brief identical to arm T's but for the search tools (archive and record only, no
web, English/Japanese/Chinese, at most 40 tool calls). The agent's own usage, from its completion notice:

```
<usage><subagent_tokens>51261</subagent_tokens><tool_uses>14</tool_uses><duration_ms>126859</duration_ms></usage>
Searches: semantic-find 7, archive-find 0, Grep 5, Read 4 (by script; one failed on a wrong path).
```

Its findings, by file (the full report is the agent's reply, summarized here for the judge):

- Japan: Iwamuro village survey 1602 (`75/7588a47ce738`), parcels 3 se 22 bu to 1 tan 8 se 1 bu; Kami-Baba survey 1684
  (`27/27341e70863d`), 16 x 10.5 ken, 5 se 18 bu; land readjustment replacing small irregular early-modern plots
  (`52/522ad93fe1bd`); planned 1-tan plots, Gifu 1849 and 1869 and the jori half-fold (record 0005's originals); Shizuoka
  readjustment 1872, 2-3 se (`e5/e542a5322e62`); King, Farmers of Forty Centuries (`e8/e81890ad0ea3`), the official average paddy
  1.14 se, 31 by 40 feet, 53% under 1/8 acre - not yet in the record; Yayoi plots and Shiroyone Senmaida down to 5-18 m² (record
  0005).
- China: Taipingqiao fish-scale registers 1897 (`29/29423acf58a9`), 3,700 qiu on 11,000 mu, about 3 mu a qiu (its arithmetic);
  Buck, Chinese Farm Economy (`b6/b647a7ae9f1a`), plots of 0.34-0.39 ha, the largest 5.58 ha in Su Hsien - not yet in the record,
  a plot being one or more fields.
- Reading: ATTESTED for the Japanese registered parcel and the single basin (King); ATTESTED ONLY FOR the registered parcel in
  China; SILENT on a pre-1912 Chinese single bunded field.
- Leads not followed: Buck's Tungchiao layout; the Huizhou fish-scale study (`04/04c46c135344`); a library reference case on Edo
  farmland areas (`11/1127358db884`).

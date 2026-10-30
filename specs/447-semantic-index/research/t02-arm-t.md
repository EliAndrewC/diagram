# T02 arm T - the field-size question with today's search only (amendment 1)

Run 2026-10-30, a `research-pass` agent, its brief identical to arm S's but for the search tools (`make archive-find`, Grep,
Read; no `make semantic-find`; archive and record only, no web, English/Japanese/Chinese, at most 40 tool calls). The agent's own
usage, from its completion notice:

```
<usage><subagent_tokens>59011</subagent_tokens><tool_uses>22</tool_uses><duration_ms>201169</duration_ms></usage>
Searches: 20 tool calls in all: archive-find 3 (in one call), Grep-type searches 12 (grep and python pattern scans), Reads 6
```

Its findings, by file (the full report is the agent's reply, summarized here for the judge):

- Japan: Iwamuro village survey 1602 (`75/7588a47ce738`); Kami-Baba survey 1684 (`27/27341e70863d`); King, Farmers of Forty
  Centuries (`e8/e81890ad0ea3`), the official average paddy 1.14 se - not yet in the record; Shiroyone Senmaida, about 800 plots
  averaging 18-20 m² (`f4/f457740405c1`, `56/5649138bf1c5`); Yayoi small plots down to 5 m² (`d1/d1f4b30193e3`); planned 1-tan
  plots, 1849 and 1869 and the jori half-fold (`52/522ad93fe1bd`, through record 0005's originals).
- China: Taipingqiao fish-scale registers 1897 (`29/29423acf58a9`), about 3 mu a qiu; Shicang village, Songyang, an 1898 pawn
  contract whose three qiu measure 1.4 mu together today (`83/831d8174fa8b`, Cao Shuji) - not yet in the record; Wanchun polder
  1061, ditched blocks of one qing (`6b/6b0d3db9d121`); King's China terraces "no larger than a dining table".
- Reading: ATTESTED ONLY FOR register parcels and small terraced plots; one post-1868 Japanese figure for a typical single paddy;
  no source gives the largest ordinary bunded paddy in either country.
- Leads not followed: more of King's Kiangsu field passages; the rest of Cao Shuji's article.

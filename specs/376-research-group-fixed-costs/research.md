# Research - feature 376: does a research group's cost sit in a fixed part, or per thing?

## R1 - the measurement, before choosing a lever (2026-10-10)

**Method** (observed 2026-10-10; method: `measure/fixed_and_marginal.py`, output `measure/results.txt`, over the
sessions feature 347 collected). For each complete group, its cost is fitted by least squares against the things it
checked: a fixed part per group plus a part per thing. This is done for its write sessions, its check sessions, its
agents and the whole, before 274 (R1's window) and after it (the research groups of features 269, 280, 291 and 317).
Feature 269 ran on both sides of the landing.

| (observed 2026-10-10; method: `measure/fixed_and_marginal.py`) | groups | write | check | agents | total |
|---|---|---|---|---|---|
| before 274 | 48 | 3.14 M + 0.374 M a thing | 1.04 + 0.342 | 1.20 + 0.063 | **5.39 + 0.778** |
| 269 before | 12 | 2.70 + 0.347 | -1.20 + 0.558 | -0.36 + 0.199 | 1.05 + 1.113 |
| 269 after | 11 | 1.03 + 0.407 | -2.38 + 0.927 | -0.50 + 0.256 | -1.85 + 1.590 |
| research groups after | 66 | 2.08 + 0.421 | 0.93 + 0.464 | 0.51 + 0.133 | **3.52 + 1.018** |

**The fixed part fell, and the cost per thing rose** (observed 2026-10-10; method: the table above). The fixed part per
group went from 5.4 M to 3.5 M, which is what 274's cap was for. The cost per thing went from 0.78 M to 1.02 M. Feature
269, which ran on both sides, shows the same: 1.11 M a thing to 1.59 M (its fixed part fits near zero over 11-12 groups
and is noise). So 347's R3, which explained the rise as a fixed part spread over fewer things, had the mechanism
backward. This feature was filed on that explanation.

**Where the per-thing cost went** (observed 2026-10-10; method: the same script, every tool call in the complete
groups, with the tokens its result carries over the later turns). Per thing checked, before 274 against after:
- **Reading and searching doubled.** Read calls went from 1.04 to 2.18 a thing, carrying 27 K to 66 K. Web searches
  went from 0.65 to 1.60, carrying 19 K to 39 K.
- **Agents and edits rose.** Agents went from 1.67 to 2.23 a thing, edits from 2.11 to 3.39.
- **`make lines` carries 33 K a thing**, replacing the whole-file `cat` reads 347 measured gone.

The post-landing groups did more research per item. Feature 280 was a sweep asking of each source whether it was
modern-only, which means searching for premodern evidence, often many searches for one item. 269's second half was its
fixes and splits. Neither is the same work as R1's first-pass write-ups, and a cap on session length cannot change how
much searching an item needs.

**What 376's two levers are worth** (observed 2026-10-10; method: the fits above):
- **One check pass over several write sessions** saves at most the check sessions' fixed part, about 0.9 M a merged
  group. Merging the 66 groups in pairs saves about 30 M of 738 M, about 4%.
- **A claims lookup that answers only the claim** saves part of the 16 M `make lines` carried on the claims file, at
  most about 2%.

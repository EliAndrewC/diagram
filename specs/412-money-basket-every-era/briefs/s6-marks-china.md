<!-- page-load: kind=assertions -->
# Brief - feature 412, session 6: the Chinese era marks (T06, second half)

You are a FRESH session for one part of one feature. This brief is the whole of what you need; do not read the feature's spec
or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Session 5 marked every Japanese amount of money dated inside an era of
`research/assets/money-eras-awaiting.json` (feature 413's tooltip; `l7r/diagram/interactive/record/money.py`'s docstring is the
rule). gm-assistant has now confirmed the Chinese coin keys on diagram#13 (issuecomment-6390801447, verbatim):

> Confirmed: `tael`, `cash` and `dollar`, as proposed; mark the Chinese amounts now against the awaiting eras, no need to wait.
> A string is marked as its count of cash (a nominal string of 1,000 marked as 1,000 unless the source says it ran short), and
> cents as hundredths of a `dollar`.

Your job: mark every Chinese amount of money in the record whose date falls within a Chinese era's years, and decide every
other one. MARKUP ONLY - never a visible word - so it owes no record check (`make record-owed` must name nothing you caused).
0288 and 0289 are free now (their check rounds closed).

## The tool first

`scripts/record/money_candidates.py` gives an awaiting era of a place outside `JAPAN_PLACES` no coin at all (session 5's
change). Give those eras the Chinese coins instead: a `CHINA_COINS = ("tael", "cash", "dollar")` beside `COINS_ALSO`, the
Chinese places (Beijing, Songjiang, Suzhou, Canton) carrying them, and the scanner's coin words extended so a Chinese amount is
found: tael(s), cash, wen, string(s) (of cash), dollar(s), cents, mace (a tenth of a tael), candareen(s) (a hundredth), guan
and tiao where they count cash. A Japanese era carries no Chinese coin, and a Chinese era no Japanese one. Tests in
`tests/tooling/test_money_candidates.py` (a Chinese amount found and owed inside a Chinese era; a tael inside a Japanese era's
years not offered that era; `dollar` only where the place is Canton or Beijing). Run `make test-file
FILE=tests/tooling/test_money_candidates.py`. Commit, message opening `412: marks - `.

## The mark

`<span class="money" data-amount="0.094" data-coin="tael" data-era="beijing-1736">0.094 tael</span>` around the amount's own
words; `data-era` once on an enclosing `<ul>`, `<li>`, `<table>` or `<td>` holding one era's amounts is fine.
- A compound amount is ONE span with its total in the coin named: "1 tael 2 mace" is 1.2 tael; "3 mace" is 0.3 tael; cents
  are hundredths of a dollar ("14 cents" is 0.14 dollar); a string of cash is its count (1,000 unless the source says fewer).
- An amount paid at another place inside a Chinese era's years: `data-paid="<place> <year>"` (a Lower Yangzi wage of 1760
  against `suzhou-1750` needs none: Suzhou is the Lower Yangzi; a Zhili wage of 1769 against `beijing-1736` takes
  `data-paid="Zhili 1769"`).
- NOT money, never marked: a rate between coins ("800 cash to the tael", "0.72 tael a dollar"), a weight (a tael as 37 g,
  "36.9 g a tael"), grams of silver, a price per unit stated only in grams, a percentage.
- PASSED OVER with its reason in `specs/413-money-tooltip-on-the-record/backfill.md`: an amount dated outside every Chinese
  era's years (the Song, Liu's Lower Yangzi of 1530-1549, Tang 764); Ming paper money (the 1497 table's guan are paper
  notes, not strings of cash - `beijing-1500`'s tael amounts are marked, its paper guan are not); an amount with no year.

## The list

`make money-candidates` lists every unmarked amount with its distance in years from the nearest era. Work it question by
question. Each amount: mark it, or add `- <stem> | <amount> | <reason>` to the backfill (or `- <stem> | * | <reason>` for a
fragment whose remaining amounts share one reason). Remove a backfill line whose amount you marked.

## The procedure

1. The tool, its tests, a commit.
2. Mark question by question; after each, `make record CHECK=1` (it refuses a bad mark, naming it). Commit every few
   questions with messages opening `412: marks - `.
3. At the end: `make money-candidates CHECK=1` exits 0; `make record-owed` names no unit in a question you marked; `make
   record CHECK=1` builds.
4. Append to `specs/412-money-basket-every-era/briefs/handoff.md` a `## Session 6 (Chinese marks)` section: per era, how many
   amounts marked and in which questions; what was passed over and why, in a line each; anything you could not decide. Do
   not push. Your last message is one paragraph.

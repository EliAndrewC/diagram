<!-- page-load: kind=assertions -->
# Brief - feature 412, session 5: the era marks (T06)

You are a FRESH session for one part of one feature. This brief is the whole of what you need; do not read the feature's spec
or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Every amount of money in the record converts on hover at an era's rates (feature 413's tooltip:
`l7r/diagram/interactive/record/money.py`'s docstring is the rule). Feature 412 defined new eras with gm-assistant; they are on
`research/assets/money-eras-awaiting.json` (each id with its place and years). Your job: mark every amount of money in the
record whose date falls within one of those eras' years with that era, and decide every other listed amount. This changes MARKUP
ONLY - never a visible word - so it owes no record check (`make record-owed` must name nothing you caused).

## The mark

`<span class="money" data-amount="20" data-coin="mon" data-era="edo-1830">20 mon</span>` around the amount's own words.
- `data-amount`: a number or a range ("15-20"); a compound amount ("9 ryo 2 bu", "1 kan 219 mon") is ONE span with its total in
  the coin named (9.5 ryo; 1219 mon).
- `data-coin`: the unit key - `mon`, `kanmon`, `monme`, `ryo` (the units gm-assistant's table will carry; a coin no era carries,
  such as `bu` or `shu` alone, is passed over with that reason).
- `data-era` on the span, or once on an enclosing `<ul>`, `<li>`, `<table>` or `<td>` that holds one era's amounts.
- An amount paid in another place within the era's years: add `data-paid="<place> <year>"` (the tooltip then says "at Edo
  1830-44 prices"). An amount dated outside every era's years is NOT marked with a borrowed era unless gm-assistant asked for it
  (below); pass it over.
- NOT money, never marked: a rate between coins ("60 monme to the ryo", "108 mon to the monme"), a weight (ryo and monme as
  weights), an area (bu, se, tan), a percentage.
- The Takamiya-Toriimoto fares of 1665 in 0260 and its notes are marked `kyoto-1745` with `data-paid="Takamiya 1665"`;
  re-mark them `data-era="osaka-1620"`, keeping `data-paid` (gm-assistant's request on #13: borrow the nearest era). Kyoto
  1652-1656 amounts and the 1611 and 1658 post-station fees in 0185 may borrow `osaka-1620` the same way (confirmed on #13).
- Do NOT touch `research/questions/0288-*` or `0289-*` (another session holds them) - their amounts are in Chinese money,
  which this pass does not mark.

## The list

`make money-candidates` lists every unmarked amount, with its distance in years from the nearest built era - the awaiting eras
count as built for this pass if `scripts/record/money_candidates.py` reads only the vendored table: in that case extend its
`_eras` to read `research/assets/money-eras-awaiting.json` too (place and years, every coin of COINS_ALSO), with a test in
`tests/tooling/test_money_candidates.py`, and run `make test-file FILE=tests/tooling/test_money_candidates.py`. Then work the list
question by question. Each amount: mark it, or add `- <stem> | <amount> | <reason>` to
`specs/413-money-tooltip-on-the-record/backfill.md` (or `- <stem> | * | <reason>` for a fragment whose remaining amounts share one
reason). Remove a backfill line whose amount you marked.

## The procedure

1. Mark question by question; after each, `make record CHECK=1` (it refuses a bad mark, naming it). Commit every few questions
   with messages opening `412: marks - `.
2. At the end: `make money-candidates CHECK=1` exits 0; `make record-owed` names no unit in a question you marked; `make record
   CHECK=1` builds.
3. Append to `specs/412-money-basket-every-era/briefs/handoff.md` a `## Session 5 (marks)` section: per era, how many amounts
   marked and in which questions; what was passed over and why, in a line each; anything you could not decide. Do not push.
   Your last message is one paragraph.

<!-- page-load: kind=assertions -->
# Brief - feature 416, session 4: the money marks of 0295 and 0296

You are a FRESH session for one part of one feature. This brief is the whole of what you need; do not read the feature's spec
or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Sessions 1-2 wrote 0295 (were gold, silver and copper one money or three in Edo Japan?) and 0296 (the same
for China). Their amounts of money are not yet marked for feature 413's tooltip (`l7r/diagram/interactive/record/money.py`'s
docstring is the rule; `research/assets/money-conversions.json` holds the 21 eras and their coins). `make money-candidates
CHECK=1` names 188 (125 in 0295, 63 in 0296). Mark or pass over each. MARKUP ONLY - never a visible word - so it owes no
record check (`make record-owed` must name nothing you caused). Touch no other question.

**The precedent:** the marks sessions of features 412 and 414 - read `specs/412-money-basket-every-era/briefs/handoff.md`'s
Session 5 and 6 sections and `specs/414-price-stability/briefs/s5-marks-bu-shu-handoff.md` first, and a marked neighbor in
0273, 0277, 0288 or 0290 for the form.

## The mark

`<span class="money" data-amount="2" data-coin="bu" data-era="edo-1830">2 bu</span>` around the amount's own words; `data-era`
once on an enclosing `<ul>`, `<li>`, `<table>` or `<td>` holding one era's amounts is fine.
- The coin must be one the era carries (Japanese eras: mon, monme, kanmon, ryo, bu, shu; Chinese: tael, cash, and dollar at
  Canton and Beijing 1900). A compound amount is ONE span with its total in one coin (2 bu 2 shu = 2.5 bu; 1 tael 2 mace = 1.2
  tael; a string = its count of cash); a sum in two metals at once is two spans, each its own coin, unless the source gives the
  rate between them for that year.
- An amount paid at another place or year inside an era's span: `data-paid="<place> <year>"`. An amount dated outside every era
  is not marked unless the nearer era, by the midpoint of its years, is within the era's own no-note span by 0294
  (`research/questions/0294-*.html`) and crosses no break (1859; a recoinage that changed the silver; a change of money system;
  domain notes; a move in China's cash rate) - then mark it with `data-paid`, which is the note.
- NOT money, never marked - and these are most of 0295 and 0296: a rate between coins ("60 monme to the ryo", "4 kanmon a
  ryo", "1,000 cash to the tael", "4 bu to the ryo"), a coin's face value or legal value, a weight or fineness, a percentage, a fee
  stated as a share, a coin's denomination named as a kind ("the five-monme piece", "the 100-mon Tenpo coin", "a 1-bu silver"),
  an amount of coin minted or held.
- PASSED OVER with its reason in `specs/413-money-tooltip-on-the-record/backfill.md` (`- <stem> | <amount> | <reason>`, or `- <stem>
  | * | <reason>` for a fragment whose remaining amounts share one reason): every amount you do not mark.

## The procedure

1. `make money-candidates ALL=1 Q=0295 CONTEXT=1` (then Q=0296) shows each amount in its sentence. Work question by question;
   after each, `make record CHECK=1` (it refuses a bad mark, naming it). Commit, messages opening `416: marks - `.
2. At the end: `make money-candidates CHECK=1` exits 0; `make record-owed` names no unit you caused; `make record CHECK=1`
   builds.
3. Write `specs/416-three-metals/briefs/s4-marks-handoff.md`: per era, how many amounts marked and in which question; what was
   passed over and why, a line per kind; anything you could not decide. Do not push. Your last message is one paragraph.

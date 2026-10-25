<!-- page-load: kind=assertions -->
# Brief - money marks, session 7: the gold bu and shu, now that every Japanese era carries them

You are a FRESH session for one part of the money record's marking. This brief is the whole of what you need; do not read a
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What is asked.** Feature 412's marks pass (sessions 5 and 6) marked every amount of money dated inside an era's years for
feature 413's tooltip (`l7r/diagram/interactive/record/money.py`'s docstring is the rule) and PASSED OVER every gold `bu` and
`shu`, because no era carried those coins then. gm-assistant has since added `bu` and `shu` to every Japanese era of its
conversion table (diagram#13 issuecomment-6391712228, gm-assistant 2ed9f087); the vendored copy
`research/assets/money-conversions.json` now has them, and `research/assets/money-eras-awaiting.json` is empty (all 19 eras are
built). Your job: mark every gold bu and shu amount dated within a Japanese era's years, and re-decide the backfill lines that
passed one over. MARKUP ONLY - never a visible word - so it owes no record check (`make record-owed` must name nothing you
caused).

**Also yours: questions 0290-0294** (feature 414; their checks are closed). Their 89 amounts in taels, cash, monme and ryo are
not marked yet: mark or pass over each exactly as sessions 5 and 6 did (Session 5 and 6 sections of
`specs/412-money-basket-every-era/briefs/handoff.md` are the precedent), after the bu and shu. Much in them is NOT money by
the rules below - a price change ("a 2-cash cut"), an index, a rate between coins, a per-unit spread - so read each in its
sentence. **Leave alone** 0295 onward (feature 416, being written now); add no backfill lines for them.

## The tool first

1. `scripts/record/money_candidates.py` misses amounts written with macrons (`ryō`, `shū`, `bū` is not a spelling; 0251's three
   were marked by hand): make the scanner find `ryō` and `shū` as `ryo` and `shu`. A test in
   `tests/tooling/test_money_candidates.py` (a `2 shū` amount found as `shu`).
2. With the awaiting list empty, the AWAITING path and its comments (the "until its row is vendored" wording, `JAPAN_PLACES`'s
   role) may now be dead: if a branch can no longer run, remove it with its test, and say so in your handoff; keep the file's
   behavior otherwise.
3. `make test-file FILE=tests/tooling/test_money_candidates.py`. Commit, message opening `413: marks - `.

## The mark

`<span class="money" data-amount="2" data-coin="bu" data-era="edo-1830">2 bu</span>` around the amount's own words; `data-era`
once on an enclosing `<ul>`, `<li>`, `<table>` or `<td>` holding one era's amounts is fine.
- A compound amount is ONE span with its total in ONE coin the era carries: "1 bu 2 shu" is 1.5 bu (4 shu to the bu, 4 bu to
  the ryo); "2 ryo 1 bu" is 2.25 ryo; a sum in gold and copper together ("1 bu 756 mon", 0273's notes) is ONE span in the
  larger coin only if the source gives the rate between them for that year - otherwise mark the gold part and the copper part
  as two spans, each its own coin, and say so in the handoff.
- An amount paid at another place inside an era's years: `data-paid="<place> <year>"`, exactly as sessions 5 and 6 did (read a
  marked neighbor in the same question first).
- NOT money, never marked: `bu` as an area or length (most `bu` in the record: 0037, 0080, 0130, 0174, 0185, 0228, 0229,
  0237, 0261 - their lines stay), a rate between coins, a coin's weight or fineness.
- PASSED OVER, its line kept or written: an amount dated outside every Japanese era's years (Morisada's inns of 1837-1853 fall
  INSIDE edo-1830 or edo-1850 - decide by the year the source gives), an amount with no year, a bu or shu of silver (the
  isshu-gin and nishu-gin are silver coins counted in gold units: mark them as the gold unit they are counted in, which is how
  the table's `bu` and `shu` are defined - read the era row's `note` for each unit first and follow it).

## The list

1. In `specs/413-money-tooltip-on-the-record/backfill.md`, every line whose reason passes over a gold bu or shu - the own-line
   ones ("in a coin no era carries", "the row has no unit for bu") and the `*` lines whose reason lists "a gold bu or shu (no
   era carries them)" (77 lines) - is now stale in part.
2. For a `*` line: delete the clause "a gold bu or shu (no era carries them), " from its reason (keep the rest of the
   sentence), then run `make money-candidates ALL=1 Q=<n> CONTEXT=1` for that question to see its bu and shu amounts.
   Note: the `*` line still covers them; to see what it hides, read the fragment itself (grep for ` bu\b`, ` shu\b`, `shū`,
   `分`, `朱`). Mark each money bu or shu dated within an era's years.
3. For an own-line: mark it, or rewrite its reason to the one that still holds (a year outside every era's years, no year).
4. `make record CHECK=1` after each question (it refuses a bad mark, naming it). Commit every few questions, messages opening
   `413: marks - `.

## The end

1. `make money-candidates CHECK=1` exits 0 (if 0295 onward has landed in your clone, its amounts are excepted).
2. `make record-owed` names no unit you caused; `make record CHECK=1` builds.
3. Append to `specs/413-money-tooltip-on-the-record/backfill.md`'s opening paragraph one sentence: the bu/shu pass of
   2026-10-24 marked the gold bu and shu once gm-assistant's table carried them.
4. Write `specs/414-price-stability/briefs/s5-marks-bu-shu-handoff.md`: per era, how many bu and shu amounts marked and in
   which questions; the same for 0290-0294's amounts; the compound gold-and-copper sums and how each was marked; what stays passed over and why, a line each;
   anything you could not decide. Do not push. Your last message is one paragraph.

# Implementation Plan: a tooltip converting every historical amount of money in the record (feature 413, diagram#14)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-24

## Summary

The record vendors gm-assistant's conversion table; the site build reads each marked amount, refuses a bad mark, and writes
the conversion into the amount's span as the text its hover box shows; `record.js` shows it in the box the glossary and the
source labels already use. Every amount in the record's fragments in the two eras with rows is marked. The site build is engine code
(`l7r/diagram/interactive/record/`), so the feature lands on the gated route.

## Technical Context

- `l7r/diagram/interactive/record/site.py` `Build.__init__` reads every question's page (`store.page_html`) and
  `Build.notes_of` its notes; `Build.run` gathers every refusal into one `RecordError` (`archive.refusals`,
  `blocked.refusals`).
- `research/assets/record.js`: the hover box (`tip`, `place`, `keep`, `hideSoon`); the source labels (`span.srctag[data-def]`)
  show their `data-def` in it, which is the form a marked amount takes; `wrapGlossary` wraps glossary words, and inside the box
  gives them a `title`.
- gm-assistant (read only, no git): `webapp/l7r/money/data/conversions.json`; the Rokugani format is `conversions.rokugani()`
  with `coins.everyday()` and `coins.fmt()`.
- `scripts/record/record_units.py`: a block's words are its text with markup normalized away, so wrapping an amount in a span
  owes no record check.
- Tests: `tests/interactive/test_record_*.py` (the site build), `tests/tooling/` (the refresh script).

## Performance bookends

N/A: no generator change (the record build gains one regex pass per question page).

## Constitution Check

- I-XI: N/A. XII: the tasks are `research: rendering` (the record's presentation and tooling). XIII: the record build and its
  tests stay green; `make done` on the gated route. XVI: built as the spec's FRs.

## D1 - the vendored table and its refresh (FR-001)

`scripts/record/money_conversions.py` copies `/host-l7r-repo/gm-assistant/webapp/l7r/money/data/conversions.json` to
`research/assets/money-conversions.json` byte for byte; `--check` writes nothing and exits 1 naming `make money-conversions`
while the two differ, and exits 0 with a note when gm-assistant's checkout is absent (a container without the mount). `make
money-conversions [CHECK=1]` runs it. The copy is committed; the build never reads gm-assistant.

## D2 - the mark (FR-002)

`<span class="money" data-amount="20" data-coin="mon">20 mon</span>`. `data-amount` is a number (commas allowed) or two joined
by a hyphen; `data-coin` a unit key of the era's row. The era is `data-era` on the span or on its nearest enclosing element
that carries one (a `<li>`, `<td>`, `<table>` or `<ul>`), so a table or list of one era declares it once. A borrowed era adds
`data-paid="<place> <year>"` or `"<place> <year>-<year>"` on the span or an ancestor. An era id gm-assistant has not built yet
may be written only if it is listed in `research/assets/money-eras-awaiting.json` (ids feature 412 defines, each with its place
and years), so a typo is never mistaken for an era to come.

## D3 - the build reads and refuses (FR-003, FR-005)

New `l7r/diagram/interactive/record/money.py`:
- `load(record_dir)`: the vendored table and the awaiting list (absent files read as empty).
- `annotate(markup, where, table) -> (markup, errors)`: for each `span.money`, resolve the era (span, then ancestors: a small
  stack-based scan of the fragment's tags, no HTML parser), check it, and on success add `data-def="<box text>"`. Refused, each
  naming `where` and the span's text: no era; an unknown era not awaiting; a coin not in the era's units; an amount not a number
  or a range; a `data-paid` with no year. No distance in years is refused (the GM withdrew the 25-year default, #14). An awaiting era or no
  row: the span is left as written (the glossary tooltip only, FR-005). No fallback to another era anywhere.
- `Build.__init__` annotates each question page and `notes_of` each notes file; their errors join `self.errors`, deduplicated.

## D4 - the box text (FR-004)

`box(amount, unit_row, era_row, paid)`, pure and tested: line 1 "20 mon: about $4.07 in goods, $41.71 in wages, 4.2 sen in
Rokugan" (a range gives each end, "$61-$81"); dollars rounded to the cent under $100 (the issue's worked example gives $41.71), to the dollar under $10,000 and to three
significant figures above; Rokugani coin by a port of gm-assistant's `rokugani()` (under 10 sen one decimal; else
`everyday()`: the two largest coins it needs, rounded, "about" when rounded). Line 2, borrowed only: "at <place> <years>
prices". Line 3: "<place> <years>: <basket_coverage>" plus "; leaves out <goods>" when any. Line 4: the era's confidence.
Lines are joined with newlines; the box shows them as lines (`white-space: pre-line` on a box opened from a money span).

## D5 - the hover (FR-004)

`record.js`: every `span.money[data-def]` opens the box with its `data-def` on hover or focus, as a source label does, and
appends the glossary definition of its coin word when the glossary has one (FR-004's last clause, spec US1 scenario 5); inside
the box (a note shown in it) the span gets the text as a `title`. `wrapGlossary` still wraps the coin word inside the span; the
span's own listener is on the span, and a glossary word inside a money span is left to the money box (its own listener is not
added). `record.css`: a dotted underline for `span.money[data-def]`, as for `.gl`. A `page-check`-style browser test is not
added (GM 2026-09-07: no browser tests on full pages); the synthetic record page test, if one exists for record.js, gains a
money span.

## D6 - the back-fill (FR-006)

`scripts/record/money_candidates.py` (run by `make money-candidates`): every amount in every fragment under `research/questions/`
(questions, drawing pages and their notes; the build converts all of them, since `Record.pages()` holds both halves) that is
not inside a `span.money` and whose coin is any coin word of these money systems - every unit of the vendored table and of the
awaiting list, plus the period's other Japanese coins (`COINS_ALSO`: mon, monme, kanmon, ryo, bu, shu, koban, yen, sen, rin) -
with its question, its block, and the years its block names, else those its heading names. An amount in a coin its era's row
has no unit for (a gold bu at Kyoto 1745-54) is listed like any other and passed over with that reason. The listing names each amount's distance in years from the nearest built era carrying its coin and lists the nearest first; the
order decides nothing (no distance in years is compared - the GM withdrew the 25-year default, #14). EVERY amount
listed is owed a decision, whatever its years: marked by hand (D2), or passed over with its reason in
`specs/413-money-tooltip-on-the-record/backfill.md` (one line per amount: question, amount, reason - "Edo 1804-30; the author judges no built era close enough to borrow, pending diagram#15", "no unit for bu in the kyoto-1745 row"); where one reason covers every amount a fragment still holds
unmarked, the author may judge the fragment whole in one line, `- <stem> | * | <reason>`, the reason holding for every amount
it covers; `--check` compares no distance in years. The script's `--check` exits 1 while a listed amount is
neither marked nor named in that file, so the duty cannot stop at the flagged ones.
The marking is checked by `make record CHECK=1` and `make record-owed` (which must name nothing for it).

## D7 - tests (SC-001 to SC-004)

`tests/interactive/test_record_money.py`: the worked example (20 mon at kyoto-1745 = about $4.07, $41.71, 4.2 sen); the
Rokugani port against gm-assistant's function on 0.5, 9.95, 42, 137 and 1,234 sen (expected strings written in the test from
gm-assistant's output, taken once); each refusal of D3 and an unmarked and an awaiting amount passing; an ancestor's `data-era`
inherited; a borrowed era's line. `tests/tooling/test_money_conversions.py`: fresh exits 0, stale exits 1 naming the command,
absent source exits 0. Each new test proved red with its change removed.

## D8 - the reply (FR-007)

A comment on #14: how an amount is marked, the awaiting list, the refresh command, and how to verify (build, open a question,
hover a marked amount).

## T - the order

1. D1, D3, D4, D7 (the build and its tests). 2. D5 (the hover). 3. D6 (the back-fill). 4. The reply and the gated landing.

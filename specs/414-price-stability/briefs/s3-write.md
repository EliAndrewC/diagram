# Brief - feature 414, how stable prices were. Session 3: write (new question D, the closeness rule)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-pages`). The project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** Issue EliAndrewC/diagram#15, question 4 (verbatim in `specs/414-price-stability/request.md`): how far in time
and in place an amount may be converted at another era's or place's rates before the conversion should say so, and how far
before it should not be made at all; whether that differs by good class or by the size of the amount. The GM: an amount of time
should be stated "only if that amount of time is based on something". Sessions 1 and 2 wrote A (time scales), B (places), C
(periods), E (today): read `briefs/handoff.md`.

## Your items

- `D` **"When does a price borrowed from another year or place need a note?"** (new). The rule is THIS PROJECT'S DERIVATION (no
  source states one; the passes searched), labeled so throughout. From `measure/closeness.py` and its `.out.md`:
  - The within-era spread: an era row converts any year in its ten-year span at one price level, so the SD of log change at 5
    years is the uncertainty the table already accepts.
  - No note: a gap whose SD is within that spread plus twice its standard error, the bound the last gap of an unbroken run from 5
    years, each gap on at least 20 pairs - by good and city (Kyoto rice 25 years, Edo rice 20, Osaka rice 10; steady goods such
    as firewood and soy sauce only 5, since their own spread is small). Say why the Edo and Osaka bounds stop at 20 or less (their
    series run 1818-1858). Kyoto's salt is left out (a unit change from 1791).
  - Do not convert: across a structural break whatever the gap - the 1859 opening, a recoinage that changed the money's silver, a
    change of money system (mon to yen, cash to dollars), a domain's own notes; for China, the copper-silver rate's moves for an
    amount in cash.
  - Between them: a note. A further numeric limit is NOT set: the measured swing-by-gap curve (the `.out.md` table) goes to the GM
    for his choice - say so on the page, as a decision left to him, in the form the record uses for an open decision.
  - China: the same no-note bound from `measure/qing_stability.py` (Allen et al.'s Suzhou and Canton basket costs; Beijing's a
    reconstruction, said so; Kishimoto's rice too sparse to reach long gaps - say how sparse), per good class where the series
    carries the good, a class it lacks stated open with the measured reason.
  - Place: a city whose spread to the era's city is within the within-era spread needs no note (`closeness.py`'s place table:
    rice, miso, lamp oil within; soy sauce, firewood beyond); breaks are place's do-not-convert bound too.
  - Size of the amount: no measurement gives a basis to vary the bounds by size; say so and what was searched.
  - Against its canon: feature 413's marking (the author picks an era per amount, the tooltip names a borrowed era) - the rule as
    the author's guide.

**New registry keys**: none expected (the sources are A-C's); the scripts are cited as this project's arithmetic.

## The procedure (session 3: write)

Steps 1-6 as session 1's, with question `<D>`, commits opening `414: `, and a `## Session 3` handoff section.

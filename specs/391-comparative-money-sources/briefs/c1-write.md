# Brief - feature 391, The Complete Servant as comparative money questions. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`); the project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all. Read its section "Comparative money sources" first: these are the record's
first COMPARATIVE questions.

**What is asked** (EliAndrewC/diagram#2, from gm-assistant's money skill; the GM approved it as an openly comparative
question): record what *The Complete Servant* (Samuel and Sarah Adams, London, 1825) says a Regency English household paid
and spent. Research only: edit no code, modal or sheet.

## The source

- Project Gutenberg #69487: https://www.gutenberg.org/ebooks/69487, plain text at
  https://www.gutenberg.org/ebooks/69487.txt.utf-8 (a local copy: `/tmp/claude-1000/-diagram/97f1184b-851e-49f6-84e3-b457598c8fdf/scratchpad/cs/complete-servant.txt`).
- `make archive URL=https://www.gutenberg.org/ebooks/69487.txt.utf-8`, then register it: `make reserve KIND=registry
  KEY=adams-1825-complete-servant URL=https://www.gutenberg.org/ebooks/69487 TAGS="period=modern-preindustrial;
  region=europe; kind=comparative,primary"`.
- Its two write-ups state what it is (a London household manual of 1825 by two former servants) and its limits: a
  comparative source for players' yardsticks, never the setting's own figures, which is the category's rule. Give the
  edition and page of the figures where the Gutenberg text keeps the original page numbers; where it does not, say the
  Gutenberg text carries none.
- `specs/391-comparative-money-sources/extraction/check.md` is an independent reading of the wage lines, with line
  numbers in the Gutenberg text. Use it as leads: read each passage yourself before quoting it.

## Your items (three new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=comparative,money; setting=city;
level=counts-and-measurements`, with no drawing page. The first one written deletes the `"awaiting"` line of the
`comparative-money` section in `research/contents.json`. Each opens with an intro (`<p class="intro">`): a comparative
question, a yardstick from another society for players, never Rokugan's own figures.

- C1 **"What did a Regency English household pay its servants?"** Wages by post with what came in kind as the book gives
  it, from the post's own section and the country-gentleman establishment table. Include the housekeeper (THE
  HOUSEKEEPER, "twenty-five to fifty guineas per annum") and the house steward ("Salary from 100l. to 250l. and upwards").
  Note that THE COOK section states no wage; the 12-14 guineas belong to the kitchen-maid. Include board wages (10s.
  female, 12s. male a week).
- C2 **"How did a Regency English household divide its income?"** The book's expense table (the shares the asker gave:
  33 / 25 / 25 / 12.5 / 4.5 percent, incomes 1,000 to 10,000) and its servants-by-income list, verbatim, with the heads
  each share pays for.
- C3 **"What did provisions and household goods cost in Regency England?"** Every price the book quotes for food (bread,
  meat, butter, tea, sugar, beer), candles and fuel, cloth, and keeping a horse, verbatim with its unit. Each of those the
  book does not price is stated as silent (an absence note).

Keep each question under the 20,000-byte cap; split along a topic if one runs over.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=391` once reserved.
2. Quote from the archived text. Run the `source-reader` agent on the notes from a bundle (`make check-bundle
   KEY=adams-1825-complete-servant FOR=source-reader`).
3. Edit the fragments, then run `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_comparative_sources.py"`).
   Commit with messages opening `391: `.
4. Write `specs/391-comparative-money-sources/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - a comparative money question consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/391-comparative-money-sources/briefs/c1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per question;
   - per question, the figures with their verdicts (ATTESTED / SILENT) and their edition and page.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

# Brief - feature 390, the money foundation questions. Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all, along with `research/money-requests.md` (the money protocol).

**What is asked.** gm-assistant's money skill asked for four questions on EliAndrewC/diagram#1. The request's text,
verbatim, is in `specs/390-money-foundation-research/request.md`; read its four questions and their "Canon beside it"
lines. Write the four as NEW questions in the record's money section. This is research only: edit no code, modal or
sheet, and never edit the GM's canon (`l7r.md`, `budgets.md`), which you quote only where a comparison needs it.

## The passes (leads, not citations)

`specs/390-money-foundation-research/passes/` holds one file per question: `q1-land.md`, `q2-wages.md`, `q3-koku.md` and
`q4-basket.md`, each with verbatim passages, URLs and local copies.

**Verify each passage yourself on its page before citing it.** For a PDF that `make source-pages` cannot read: download
it, read it with `pdftotext`, `make archive URL=<public url>`, and cite the public URL. The local copies the passes made
are listed in each file.

## Your items (four new questions)

Reserve each with `make reserve KIND=question KEY=<heading id>`. Tag each `subject=money` first, with no drawing page. The
first one written deletes the `"awaiting"` line of the `money` section in `research/contents.json`, in the same commit
(the build refuses it once a question is homed).

- Q1 **"What did farmland sell for, against what it yielded?"** (`setting=countryside; level=counts-and-measurements`)
   - China: the Minnan pledged-rent returns (Cao Shuji: 6.5-37% a year, mean 12.6% over 36 cases; dian about two-thirds
     of the outright price; the 1792 outright sale at 7%). Pomeranz's 60-80%, and village credit at 12%, often 36%. The
     Songjiang price-and-rent pairs from 閱世編, with the pass's computed multiples labeled as the project's arithmetic
     (gross rent; the grain form not stated). 履園叢話's price series.
   - Japan: the pledged-land terms (岡安家文書's three pledges; kotobank 質地; 中林 2020; Wigmore), and 鷲崎 2007's 20x net
     (5%) multiple for Edo TOWN LOTS, labeled as town lots, not farmland.
   - The answers: the years-of-net-yield multiple for Japanese farmland is SILENT; irrigated against dry land is
     attested only through the tax form; near-city against remote is SILENT.
   - Set the canon's ~50-koku, ~20x farm and its 15-20% city and ~25% countryside interest beside these, as the asker's
     comparison.
- Q2 **"What did an unskilled laborer earn?"** (`setting=countryside,city; level=counts-and-measurements`)
   - Kyoto ~0.9 monme, ~1.9-2 kg of rice a day (Bassino & Ma; cite the econhistdbm.com copy); Edo the same from 1818.
   - City against village (Saito 2003): higher in the city early, equal from the 1750s-60s (1.0 against 0.92 monme in
     1802-4).
   - Qing (Allen et al.): Canton 0.08-0.1 tael, the delta baseline 0.0456, farm day labor 0.045, the annual hand
     10.4-13.4 taels, with the 0.024 tael/kg rice price.
   - The 250 working days is a modern convention (both papers say so), not a premodern count.
   - A verdict on each 2017 working figure: 1.33 zeni a day, 3.32 koku a year (~2 kg a day, 250 days), farm labor 3.5
     koku a year.
- Q3 **"How much rice was a koku?"** (`setting=countryside; level=foundational`)
   - The new Kyōmasu (1669; in use from the 1620s) at 180.39 L, the earlier one ~3.6% smaller, and domain measures.
   - Brown rice ~150 kg (the 1950 government basis of 400 monme a shō, ~0.83 kg/L; MAFF 1949 146.3 kg; MAFF 2023
     827 g/L): modern measurements applied by analogy, and say so.
   - Polished and paddy: no weight per koku-volume. Milling took 4 to down to ~3.5 to; Nara paddy ~20 kg against 30 kg
     pounded per bale.
   - The ration: 5 gō of brown rice a day, 1.8 koku a year, against the "1 koku a year" convention.
   - The Chinese shi (Song 10 dou; Tang ~59.44 L; modern 100 L and the 50 kg dan).
   - A verdict on each figure the request names: budgets.md's ~180 L, ~150 kg brown, ~136 kg polished, ~187 kg paddy,
     ~138 kg per koku and 0.021 koku/gallon, and ~1.5 koku of grain a person a year; l7r.md's "about 40 gallons" and
     "feeds a man for a year"; the 2017 spreadsheet's 151.5 kg; and the asker's ~120 kg (40 gallons at 0.8 kg/L).
   - The pass reads ~136 and ~187 as brown-rice equivalents. Say what the sources support, never which the canon
     "means".
- Q4 **"What did a Kyoto laborer's year of goods cost?"** (`setting=city; level=counts-and-measurements`)
   - Bassino & Ma's Table 1 (baskets A and B) and Table 3 (the Kyoto 1745-54 prices and the basket's total of 326 g),
     verbatim.
   - The source note on which prices were recorded (rice and lamp oil only) and which were derived.
   - The footnote 8 mislabel, and the 0.99 that is not 1.49 x 0.63.
   - Against the 2017 snapshot: every figure matches; the snapshot's own labels ("adzuki", "cotton") are not the
     paper's.

Keep each question under the 20,000-byte cap; split along a topic if one runs over. An intro (`<p class="intro">`) where
a casual reader would not know why the question is here: Rokugan's money rules rest on it.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each new number>" FEATURE=390` once reserved.
2. For each page you cite: `make archive-find URL=<u>`, then `make source-pages ... QUESTION=<NNNN> SOUGHT=...`, then the
   `source-reader` agent on the passage, from a bundle. A new source takes `make reserve KIND=registry KEY=<k> URL=<u>
   TAGS="..."` and its two write-ups. At the eleventh new key, follow the record's continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_money_section.py"`).
   Commit with messages opening `390: `.
4. Write `specs/390-money-foundation-research/implementation-check.md`, one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Write `specs/390-money-foundation-research/briefs/w1-handoff.md`:
   - one `- SECTION=NNNN/<id>` line per new question;
   - per question, the figures with their verdicts (ATTESTED / ATTESTED ONLY FOR / NOT ATTESTED / SILENT);
   - each place a finding contradicts the canon or the 2017 snapshot;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

# Tasks - 205 tsubo in the glossary

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: procedure
      verify: DONE. FAITHFUL at round 1; its one note (D2's false whole-word clause) struck and recorded in the spec
- [x] T02 the `tsubo` entry in `glossary.py` (FR-001, FR-003), its definition from the record (D1)
      research: physical
      verify: DONE. `GLOSSARY["tsubo"]`, one variant, the definition from homesteads.html fn 12 and 15 with the pointer beside it; nothing else in the file changed
      - [x] research pass - the record already answers it: `research/homesteads.html`, "How big was the work yard, and how did the sizes spread?", footnotes 12 (two mats to the tsubo) and 15 (the mat is 3 x 6 shaku, 90 x 180 cm); research.md R1
      - [x] source-reader confirmed - both footnotes are READ quotes in the record (feature 143's pass; the translation marked per feature 202)
      - [x] recorded and cited - the definition's grounds in spec.md D1 and research.md R1, pointing at the entry's footnotes
      - [x] quote-check confirmed - the footnotes it rests on passed feature 195's sweep of `homesteads.html`; no new footnote was written
- [x] T03 the `glossary_for` unit test (FR-004); the existing glossary test green
      research: rendering
      verify: DONE. tests/interactive/test_page.py `test_glossary_for_defines_tsubo_where_an_explanation_counts_in_it` - the entry returned for an explanation that says "20 to 30 tsubo", absent for one that says "66 to 99 sq m"; the whole file 74 passed
- [x] T04 the reference page regenerated and the threshing-yard modal's tooltips seen (SC-001); `make done` green; land GATED (SC-002)
      research: procedure
      verify: DONE. Inashiro regenerated (`make maps SCOPE=reference`, 35.9 s); the page opened in headless Chromium, the threshing-yard modal opened through the page's own API - 3 `span.gl` tsubo tooltips, hovering one shows the definition (the `#tip` element, not hidden); `make done` green, 589 s, the whole suite; both `make maps` and `make done` took `PAIR_OK` (no manifest or glyph moved, nothing for settlement-review to judge), the reasons in dev/bypass-log/; landing GATED (LOCAL-GATED)

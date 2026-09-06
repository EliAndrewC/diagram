# Tasks - feature 195

Spec: [`spec.md`](spec.md). Every task is `research: rendering` - the FORM of a citation (what a footnote may link
to, what it says when nothing readable exists); no task decides how a place was built. Readers fetch pages to
establish whether a passage can be read, not to settle a physical question.

- [x] T01 FR-001: the rule in the GM's words - constitution XII "CITE ONLY WHAT CAN BE READ" (v2.19.0, the SUMMARY-ONLY citation clauses struck), root CLAUDE.md research bullet, research/CLAUDE.md quote + link sections
      research: rendering
      verify: DONE. constitution v2.19.0 CITE ONLY WHAT CAN BE READ (SUMMARY-ONLY citation clauses superseded in both XII paragraphs, sync report + footer), root CLAUDE.md research bullet, research/CLAUDE.md new section + quote section; verified by reading each diff
- [x] T02 FR-003 / FR-004: quote-check gains the READABLE / NOT-READABLE verdict and the "cannot land as a citation" rule; its stale Markdown Input paragraph fixed (XIV); source-reader's SUMMARY-ONLY = not citable
      research: rendering
      verify: DONE. quote-check.md: READABLE/NOT-READABLE per footnote, the cannot-land rule, HTML Input paragraph (XIV fix), fetch the footnote's OWN link; source-reader.md: SUMMARY-ONLY = not citable
- [ ] T03 FR-005: the census - search space 780 footnotes; SEEN 485 (194 quote-check on document links + the 2026-09-06 re-fetch); A1 4; candidates 311 (104 dispatched as wave 1 before the derivation widened, 244 more as wave 2; 37 of wave 1 turned out SEEN)
      research: rendering
- [ ] T04 FR-006: the sweep - readers' verdicts applied by script: RE-POINT (link -> the readable page, registry entry gains the URL) or ABSENCE (footnote -> absence note, key off the section roster if unquoted, registry entry marked not cited); DIFFERS listed
      research: rendering
- [ ] T05 FR-002: tests - test_footnotes.py two forms + by-key carve-out; test_sources.py classifier: a SUMMARY-ONLY / unfetched key may not appear in a footnote
      research: rendering
- [ ] T06 FR-007 / FR-008: labels listed for the GM; second census at zero; push; the answer to the GM (re-pointed, removed, dropped sources, absence notes, labels, the A1 carve-out)
      research: rendering

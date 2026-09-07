# Tasks - feature 202

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Every task is `research: rendering` - the FORM of a
quotation; no task decides how a place was built.

- [x] T01 FR-001 / FR-003: the rule in the constitution (v2.20.0), root CLAUDE.md, research/CLAUDE.md; quote-check and source-reader definitions
      research: rendering
      verify: DONE. constitution v2.21.0 (2.20.0 had gone to feature 197 meanwhile) - QUOTE THE TRANSLATION in XII with the GM's words; root CLAUDE.md research bullet; research/CLAUDE.md quote-form bullet; quote-check.md TRANSLATION-FAITHFUL / TRANSLATION-DIFFERS; source-reader.md TRANSLATION line
- [x] T02 FR-002: the form test in test_footnotes.py (derived from the NOTE: a 「」 quote that is not English and not followed by a translation note fails; the German and Korean footnotes prove it fires)
      research: rendering
      verify: DONE. test_a_foreign_language_quote_is_a_marked_translation over 16 pages + SOURCES.html; foreign = non-Latin script or a run of German function words (English carries macrons and the sources' own dashes, so 'not ASCII' was the wrong derivation - the spec's stated limit holds); anchors exempt to bracket depth; RED on all 16 files before the sweep, green after
- [x] T03 FR-004: the sweep over footnotes, body prose and SOURCES.html entries - a census script, Opus translators per file (promote a faithful gloss, translate the rest), the original moved after the note
      research: rendering
      verify: DONE. census 472 units (437 footnotes, 27 registry entries, 8 prose) -> 24 Opus translator batches -> 730 translations (466 glosses judged faithful, 165 partial, 8 paraphrase, 52 terms, 19 table rows); apply202.py placed 657, then two repair passes for the nested-quote fault (an inner 「」 converted before its outer sentence truncated 14 translations and left stray parentheses in 24 anchors - all restored, the complete renderings promoted from the glosses; 58 glosses that merely repeated the translation dropped) and ten body-prose quotes translated by hand; 20 English quotes carrying a kanji term marked 'the source's own English'
- [x] T04 FR-005 / FR-006: quote-check over every converted footnote; the Huangshan page quoted as a GM-saved machine translation; tests; push; the answer to the GM (A1 stated)
      research: rendering
      verify: quote-check: 15 per-file Opus checks over every research page and the registry (~640 translated passages; TRANSLATION-DIFFERS in ~45, all corrected with the checkers' accepted renderings; the systemic nested-quote fault repaired record-wide; ~130 restating glosses dropped) plus a final confirmation pass over the hand-rewritten footnotes; two container crashes mid-check - the cut-off checkers' reports were recovered from their transcripts. Huangshan: vegetation fn-80 quotes the GM's browser translation, marked as such, the original unread. The registry's 70 straight-quoted passages (missed by the 「」 census, found by the towns+SOURCES check) translated in a 25th batch. Push: DIRECT after a green make done on the merged tree (main renumbered homesteads.html's footnotes meanwhile - rebuilt from main's version with every pass replayed)

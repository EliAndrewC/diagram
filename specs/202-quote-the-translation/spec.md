# Feature 202 - quote the translation, and say so

**Request**: [`request.md`](request.md), the GM's words verbatim (2026-09-07). **Status**: IMPLEMENTED 2026-09-07 (tasks.md); spec-fidelity round 1 CHANGES (three: the sweep covers body prose and the registry, not footnotes only; the test derives from the note, not from CJK - German and Korean are the fixtures; no house-style duty on quote-check), applied; round 2 CHANGES (three consistency fixes: FR-005/SC-002 verify every converted passage, the Edge Cases bullet matches D2, FR-002 states the test's limit), applied; round 3 FAITHFUL.

## Summary

The GM: *"for foreign language things we want to quote the English translation rather than the original text but we
also want to note that it is a translation."* Today a foreign-language footnote quotes the original in 「」 and adds an
English gloss in parentheses; from now on the QUOTE is the English translation, marked as a translation - from which
language, and by whom - and every foreign-language quoted passage in the record - 436 footnotes, and the quoted passages in body prose and in `SOURCES.html` registry entries (38 more lines) - is brought to that form. The checks change
with it: a translated quote is verified by finding the ORIGINAL passage on the page and judging the translation
faithful to it, since a translation is by construction not on the page.

## User Scenarios & Testing

### User Story 1 - the reader reads the quote in English and knows it is a translation (P1)

A player hovers a footnote on a Japanese or Chinese source and reads an English sentence, followed by a note that it
is a translation from that language and whose translation it is. They never meet a bare 「日本語」 quote with no
English, and never an English sentence presented as the source's own words.

**Acceptance**: every quoted passage in the record whose source is not in English - in a footnote, in body prose, in a
registry entry - quotes an English translation and carries the translation note; `tests/interactive/test_footnotes.py`
fails on a quote that is neither English nor marked as a translation.

### User Story 2 - the translation can still be checked (P1)

The quote-check agent, or a reader who knows the language, can find the passage on the page and judge the
translation. So the footnote keeps the original passage after the translation note, as the verification anchor -
secondary, never the quote (A1).

**Acceptance**: `quote-check` returns, for a translated quote, whether the original is on the page (VERBATIM /
DIFFERS / NOT-ON-PAGE as today) and whether the translation is faithful (`TRANSLATION-FAITHFUL` /
`TRANSLATION-DIFFERS`, giving the rendering it would accept); `source-reader` returns the original and a translation.

### User Story 3 - a source the GM saved in translation is quotable (P2)

The GM's browser translated a Chinese page and they saved the English. The footnote quotes that English, notes that it
is a machine translation saved by the GM on that date from the named page, and gives the original where the
original-language page has been read; where it has not, the note says the original was not read.

### Edge Cases

- A source that publishes its own English (an English abstract of a Chinese paper; an English page of a Japanese
  museum): quote the source's English as today, no translation note - it is the source's own words.
- A passage already quoted in English translation by an English source (Coggins translating a Chinese term): the
  English source is the source; unchanged.
- A gloss that is a paraphrase or summary rather than a translation ("the intake width is kept within 50 cm" for a
  longer sentence): not a quote; the sweep replaces it with a translation of the whole quoted passage.
- Kanji, place names and terms inside an English sentence (「陰手刈り」 as a term): a term is not a quote; it stays
  as it is, with its reading where the record gives one (constitution XI).
- A GM-note (`l7r.md`) quote: English already; unchanged.
- The house-style guard exempts 「」 spans (2026-09-06, quotations keep the source's characters). A translation is
  the project's own English, so it FOLLOWS house style - American spellings, hyphens - by convention; the guard
  cannot tell a translation from an original inside 「」, so the convention is held by the translator, by hand (D2).

## Requirements

- **FR-001 (the rule)**: constitution XII gains the form (v2.20.0, the GM's words verbatim): a foreign-language passage
  is quoted in English translation, marked as a translation; root `CLAUDE.md` and `research/CLAUDE.md` state the
  form and the reason (the reader is a casual RPG enthusiast, feature 180).
- **FR-002 (the form)**: `<li id="fn-n"><a href="url"><code>key</code></a> - 「English translation」 (translated from the
  Japanese by this project; original: 「原文」) ... <a class="fnback">back</a></li>` - the translator named (this
  project; the GM's browser, machine translation, saved YYYY-MM-DD; the source's own English elsewhere on the page);
  the original after, as the anchor. Two quoted passages carry two translations. The same form holds in body prose and
  in a `SOURCES.html` entry: the quote is the translation, the note follows, the original after the note.
  `tests/interactive/test_footnotes.py`: foreign is not CJK - the record quotes German (`waldrand-dewiki`,
  vegetation.html) and Korean (`park-2013-maeulsup`) as well as Japanese and Chinese - so the test derives the rule
  from the NOTE, not the script: every 「」 quote in a research page is either ASCII-only or is followed, within its
  footnote or sentence, by a translation note; the original inside the note is exempt because it stands after
  "original:". The German (non-ASCII letters) and Korean (non-Latin script) footnotes are the fixtures that prove it
  fires. The test's limit, stated: a Latin-script foreign quote with no non-ASCII character reads as English and
  passes - the sweep and the quote-check carry those, not the test.
- **FR-003 (the checks)**: `quote-check` verifies the original on the page and the translation against it, with the
  two new verdicts; `source-reader` returns the original passage AND an English translation in its QUOTE block.
- **FR-004 (the sweep)**: every foreign-language quoted passage in `research/**/*.html` - footnote, body prose, or
  `SOURCES.html` registry entry - is converted: where the existing
  gloss is a faithful translation of the whole quoted passage it becomes the quote; where it paraphrases, summarizes
  or covers part, an Opus translator renders the passage in full; the original moves after the note. A translation is
  never produced from memory of the source - the passage in the footnote is what is translated.
- **FR-005 (verification)**: `quote-check` over every converted passage - footnote, body prose or `SOURCES.html`
  registry entry - (the translation half) before the landing;
  the record tests green; `make page-check` if any class docstring changes (none expected).
- **FR-006 (the Huangshan page)**: the GM's saved translation of the Huangshan Daily piece is quoted under this rule
  as a machine translation saved by the GM, with the original marked unread until the Chinese page is saved.

## Success Criteria

- **SC-001**: zero quoted foreign-language sentences anywhere in the record - footnotes, body prose, registry - that are not marked as translations; every translated quote carries the note.
- **SC-002**: quote-check `TRANSLATION-FAITHFUL` on every converted passage - footnote, body prose or registry entry - or the translation corrected.
- **SC-003**: the rule text in the constitution, both CLAUDE.md files and both agents; the test derived, not listed.

## Decisions Recorded

- **D1 - the original stays, after the note** (A1): the GM asked for the translation to be the quote; the original is
  kept as the verification anchor so a translation can be checked against the page it came from. If the GM wants the
  original dropped, it is one regex.
- **D2 - house style holds on translations by convention**: the guard's 「」 exemption (GM 2026-09-06) cannot tell a
  translation from an original; the translator writes American spellings and hyphens, and that convention is held by
  hand - an accepted limitation, recorded, not a duty bolted onto the checking agent.
- **D3 - a gloss is not automatically a translation**: 421 of 436 footnotes carry a gloss, and many gloss a part or
  a paraphrase; each is judged before it is promoted.

## Assumptions

- **A1**: keeping the original passage after the translation note does not contradict *"rather than the original
  text"* - the quote is the translation; the original is an anchor, not a second quote. Reported to the GM as such.
- **A2**: the sweep runs on Opus agents (GM 2026-09-07); one translator per file, then quote-check.

## Review history

- Round 1 (spec-fidelity, Opus, 2026-09-07): CHANGES - the sweep covered footnotes only (the GM said "foreign language things": body prose and the registry added); the test derived from CJK script, not from the note (German and Korean fixtures named); a house-style duty had been bolted onto quote-check (removed).
- Round 2: CHANGES - FR-005/SC-002 still verified footnotes only; the Edge Cases bullet contradicted D2; FR-002 claimed a coverage the ASCII test could not give (limit stated).
- Round 3: FAITHFUL.

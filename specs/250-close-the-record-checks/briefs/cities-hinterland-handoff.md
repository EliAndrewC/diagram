# Handoff - feature 250, page `cities/hinterland` (T71), session 1 -> session 2

Written 2026-09-27. Session 1 located, read and wrote. The checks (quote-check, record-format,
source-applicability, entry-drift), the ticks and the push are session 2's.

## Changed questions

- `SECTION=010` (gentry-estates-are-dispersed-not-clustered-at-the-wall): 19,380 bytes with notes, under the cap
- `SECTION=050` (does-a-city-farm-inside-its-walls): 14,558 bytes with notes

## New or changed registry keys

- `KEY=cdlib-local-elites` (changed: the citation line and write-ups now cover Brook's ch. 1, Bell's ch. 4 and the
  editors' concluding remarks as well as the introduction; the source-reader flagged that the entry named only the
  introduction)
- `KEY=walled-village-enwiki` (new, 9370)
- `KEY=heino-bunri-jawiki` (new, 9380)
- `KEY=chinese-units-enwiki` (new, 9390)

## FR-002 items and their forms

| item | form | note key(s) |
|---|---|---|
| "elite holdings were fragmented, scattered parcels" | citation (sentence reworded to the source: "built up slowly, in small pieces and scattered plots") | `cdlib-local-elites-3` (editors' concluding remarks) |
| "(the single live-on manor was an earlier Tang-Song form)" | citation, sentence REWRITTEN: the Tang-Song dating was contradicted (chinaknowledge zhuangtian: Tang owners lived off rent through managers); now "the large estate under a single resident landlord was the earlier form, which in the Lower Yangzi gave way at the Ming-Qing transition" | `cdlib-local-elites-4` (Bell, ch. 4) |
| "walled lineage compounds" | citation, reworded to "in southern China the walled village of a single clan" | `walled-village-enwiki` |
| "in an Edo reading they don't commute - they're resident inside" | citation, sentence given the source's own limits ("most are resident in the castle town, though no policy ever moved the whole warrior class there and some domains kept many retainers in the countryside to the end") | `heino-bunri-jawiki` |
| "~2-15 miles out (the distance unsourced)" | citation for the inner ~6 miles + absence note for the reach beyond | `cdlib-local-elites-5` (Brook, ch. 1, Ningbo) + `gentry-estates-are-dispersed-not-clustered-at-the-wall` (absence, searched 2026-09-27) |
| "on the two common reckonings it comes out at roughly 5 by 10 ft" | citation; the reckoning now reads "about 4 by 8 ft or 5 by 10 ft", and "five to eleven beds wide" became "five to thirteen", the spec's "a fifth to a tenth" became "a fifth to a thirteenth of its width" to match | `chinese-units-enwiki` |

Also changed to stay true: the `chinese-kinship-enwiki`, `zaichi-ryoshu-jawiki`, `cdlib-local-elites-2` and
`horinouchi-jawiki` glosses lost their "on no page read" / "no cited source" clauses for the items now cited; the 050
Evidence comment moved the bed size from guess to attested; 050's "The area, like the bed, ..." lost "like the bed".

## FR-006

- none owed.

## Left open

- 010's third paragraph ("out to perhaps fifteen miles", in "Where the full pattern would show") repeats the outer
  reach with no note of its own. It was not on the work list; the absence note in the first paragraph covers the same
  figure. Session 2's quote-check may name it. The fix is a pointer to the first paragraph, or the same absence note.
- The source-reader's other limits are in the glosses: one Ningbo prefecture; home villages, not estates; the
  heinō bunri article flagged as short of sources; no Wei-Sui table row for the 540s.
- Modals: 010 and 050 bodies changed, so `scripts/_entry_owed.py` may name classes written from them. Session 2 runs
  entry-drift on what it names.
- `specs/250-close-the-record-checks/tasks.md` had an uncommitted edit (T68-T70 ticked) when this session started.
  It is not this session's and was left uncommitted.

Saved pages: `/tmp/l7r-check/cities-hinterland-pages` (MANIFEST.txt). Files 18 (cdlib full text), 01, 04, 06 hold
the quoted passages.

## From session 2a (010 and its four keys)

- For 050 (group 2b): source-applicability on `chinese-units-enwiki` found the Wei-Sui foot (25.5 cm) is probably short for
  the Qimin yaoshu's 540s - zh.wikipedia 中国度量衡 (itself unsourced by dynasty) gives the northern foot as about 29.6 cm - so
  050's "about 4 by 8 ft or 5 by 10 ft" bed may be some 14% small. The registry write-up now says so; 050's prose does not.

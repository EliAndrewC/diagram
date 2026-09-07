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
- [x] T03 FR-005: the census - search space 780 footnotes; SEEN 485 (194 quote-check on document links + the 2026-09-06 re-fetch); A1 4; candidates 311 (104 dispatched as wave 1 before the derivation widened, 244 more as wave 2; 37 of wave 1 turned out SEEN)
      research: rendering
      verify: DONE. census2.py first run: 780 / A1 4 / SEEN 485 / candidates 311; second run after the sweep: 780 / A1 4 / ABSENCE 57 / SEEN 729 / candidates 0
- [x] T04 FR-006: the sweep - readers' verdicts applied by script: RE-POINT (link -> the readable page, registry entry gains the URL) or ABSENCE (footnote -> absence note, key off the section roster if unquoted, registry entry marked not cited); DIFFERS listed
      research: rendering
      verify: DONE. 11 reader batches (348 verdicts: 280 READABLE, 58 NOT-READABLE, 10 DIFFERS); apply195.py: 26 keys re-pointed (J-STAGE abstract -> PDF, archive.org landing -> full text, registry -> the page the entry named, five summary-only entries READ), 38 passages restored to the page's characters or original language, 20 footnotes rebuilt around a passage now read, 57 absence notes; 9 DIFFERS accepted as the page's own wording, 3 hand edits (woods-westbrook-2006 and yashikirin-jawiki keys swapped in, a Pingyao framing sentence dropped); the Lacey coefficient corrected 4.75 -> 4.8 (the open PDF's figure; the file's 0.75 m -> 0.76 m)
- [x] T05 FR-002: tests - test_footnotes.py two forms + by-key carve-out; test_sources.py classifier: a SUMMARY-ONLY / unfetched key may not appear in a footnote
      research: rendering
      verify: DONE. test_footnotes.py: footnote_form() - CITATION (http(s) key link) / ABSENCE (no key, no link) / canon carve-out derived from SOURCES.html entries citing l7r.md or budgets.md; RED on the 50 registry-linked footnotes before the sweep, green after; test_sources.py needed no change (its classifier follows the READ registry lines); test_page.py's uncited roster is eight now (docstring says why); make quick 155 passed
- [x] T06 FR-007 / FR-008: labels listed for the GM; second census at zero; push; the answer to the GM (re-pointed, removed, dropped sources, absence notes, labels, the A1 carve-out)
      research: rendering
      verify: DONE. labels listed above (copse, windbreak: accurate; stream: convention - none changed); census second run 0 candidates; route DIRECT (no engine code: research HTML, tests, agents, constitution, CLAUDE.md); pushed by sync-with-main.sh done; the answer to the GM carries the per-file counts, the 36 dropped sources, the labels, the MDPI note and the A1 carve-out

- [x] T07 follow-up 2026-09-07: the GM downloaded the six papers this container cannot fetch (l7r/academic-sources/, mounted at /host-l7r-repo/academic-sources/); six Opus readers read them for the ten footnotes that had cited them; the record follows what the papers say
      research: physical
      - [x] research pass (the six papers read from the GM's copies, one Opus reader each; verdicts in the session transcript)
      - [x] source-reader confirmed (the readers ARE the reading; passages returned verbatim with page or section)
      - [x] recorded and cited (six footnotes restored as citations linking the public page and saying the copy was read; four stay absence notes quoting what the paper does say)
      - [x] quote-check confirmed (Opus quote-check over the six restored footnotes and the four absence notes' inline passages against the saved texts; result recorded below)
      verify: DONE. forests-2020 supports ONLY 'two fengshui forests on average' (Fujian, reported from Xu et al. 2012) and reads AGAINST the record's 1-2 ha grove area (its Table 1: whole-village forests over 3, 6 and 20 ha) - fn-1 cited, fn-4/fn-6 absence + the prose labeled GUESS; hu-2011: the public abstract carries 3403 plants/ha, 49.1 m2/ha, 32 patches - fn-2/fn-9 cited to the ScienceDirect abstract page, the 'closed canopy' gloss replaced by the authors' comparison; mdpi-kunisaki: fn-34 cited (5 systems / 11 farmers / 50 ha), fn-35 absence + GUESS (no typical range in the paper); mdpi-3860: describes NO layout - fn-81 stays absence, the entry's Evidence line no longer says corroborated; sho-fan: fn-64 cited for river + precipitation and the fan spanning the Tonami plain, the 'easily-reached water table' labeled GUESS (wells up to 100 m, levels unknown, no paddy mentioned); packer: fn-65 cited for the hydrosere open water - littoral - reed - marsh - alluvial forest; the sedge/wet-meadow step is NOT in Packer. copse and windbreak are cited again (test_page roster back to six)

## FR-007 - map class labels whose entry lost every cited source (listed for the GM, none changed)

| class | label | entry | what it rested on | why it is uncited now |
|---|---|---|---|---|
| `copse` | accurate | research/vegetation.html - 'The fengshui forest' | `forests-2020`, `hu-2011-fengshui-patches` (MDPI) | mdpi.com refuses every fetch from this container (403 / bot wall); the papers are open access, but nobody here has read them, and the quotes came from a search summary |
| `windbreak` | accurate | research/vegetation.html - 'The fengshui forest - real scale, and why ours is honest' | `forests-2020` (MDPI) | same |
| `stream` | convention | research/water.html - 'Water-width ladder - the real-world tiers' | `gb50288` (Chinese design standard, never read) | no public page carries the sections the record quoted; `toro-site` remains cited elsewhere |

## A1 - the carve-out, reported (FR-008)

Four footnotes quote the GM's own campaign notes (`l7r-median-domain`, `URL: none`) and keep their registry link:
archetypes.html fn-72, fn-75, fn-76 and fn-77 (by key; see `test_footnotes.py::canon_keys`). They are canon, not a source
claimed to support a historical point. If the GM rules otherwise they become absence notes in one pass.

<!-- page-load: kind=assertions -->
# Brief - feature 417, the torii, graves, retirement houses and wells' sources. Session S2: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Feature 417 T36 relabeled the engine's research claims from research passes. Some claims rest on a source a
pass found that NO page of the record holds yet. The plan (D37 b) puts each such source on the page its question belongs to,
so the claim can cite the page. Record each finding below on its page, as the record's rules say: the passage verbatim from a
page a reader can open (English translation marked as one, the original after), its date of evidence, and the reading
(ATTESTED / ATTESTED ONLY FOR / NOT ATTESTED). Write what the page says; where a source does not read as the pass says, write
what it does say, or SILENT. Do not edit any engine code or claim.

**Your passes (leads, not citations):** `pass-P4-docs-buildings.md`, `pass-P6-shrines-wells.md`, `pass-P7-other.md`, `pass-P2b-fields.md`, `pass-P1-farm-buildings.md` under `specs/417-all-seeds-pass/evidence/t29/`. Read each passage on its own
page (`make archive-find` first) before citing it.

## Your items

1. **0220 (torii): an arch's size and its posts.** Passes P4 (source E), P6 and P7: a torii's beam (kasagi) of 5.87 m
   (Kitakyushu, undated), posts 2.5 m apart (Kawataka, about 1600 - the pass says 0220 already holds it: check), a post span of
   5.53 m (Kameoka, 1683), posts at 0.615 of the beam's length, and a 2.5 m span with 2.8 m height (P4's E). Also the
   Encyclopedia of Shinto torii entry (registry key `kokugakuin-eos-torii`, already cited on 0220): torii as integral parts of
   sacred fences (tamagaki) - record whether the entry says so.
2. **0008 (graves in the fields): a commoner's grave ground.** Pass P2b: the Ming History (明史 卷60), commoners' grave ground of
   18 bu round, about 23.5 ft a side, and rank seven and below a mound 6 chi high.
3. **0028 (the farmstead): the retirement house's size and seat.** Pass P1: Kakimochi's 1885 Table 18 (already a source of
   0028) - eight retirement houses of 3 to 15 tsubo, the historian's middling 9 tsubo, and most households keeping one; the
   Yokota house's retirement house of 1820, 7.7 x 4.6 m on the left of the main house.
4. **0196 (communal wells): a well house's size.** Pass P6: Nakamori's late-Edo well house and fence, at most about 12 sq m.

**New registry keys** (at most ten): the Kitakyushu torii; the Kameoka torii; the Ming History grave rule; the Yokota house (if not registered); Nakamori.

## The procedure (session S2: write)

1. `make archive-inbox`. Then `make research-claim Q="<each question>" FEATURE=417`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `417: `.
4. Append to `specs/417-all-seeds-pass/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S2` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per item, its verdict and fragment file and the block's words a claim
   can quote; each search named; the new keys; leads not followed.
5. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

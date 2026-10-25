<!-- page-load: kind=assertions -->
# Brief - feature 417, the magistracy's sources. Session S3: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Feature 417 T36 relabeled the engine's research claims from research passes. Some claims rest on a source a
pass found that NO page of the record holds yet. The plan (D37 b) puts each such source on the page its question belongs to,
so the claim can cite the page. Record each finding below on its page, as the record's rules say: the passage verbatim from a
page a reader can open (English translation marked as one, the original after), its date of evidence, and the reading
(ATTESTED / ATTESTED ONLY FOR / NOT ATTESTED). Write what the page says; where a source does not read as the pass says, write
what it does say, or SILENT. Do not edit any engine code or claim.

**Your passes (leads, not citations):** `pass-P4-docs-buildings.md` under `specs/417-all-seeds-pass/evidence/t29/`. Read each passage on its own
page (`make archive-find` first) before citing it.

## Your items

1. **0123 (the magistrate's manor): the armory, the granary and the hall's front.** Pass P4 (sources A-D): Pingyao's armory
   standard, in the hall bay; its granary north and behind; the Neixiang hall north, facing south with a broad terrace before it.
2. **0093 (the main gate): a drum at the gate, and the prisoners' door.** Pass P4: a drum at the main gate at Pingyao and
   Neixiang; prisoners led through the ceremonial gate's west side door.
3. **0104 (the genkan): the shikidai's size.** Pass P4 (source F): the Sayama shikidai, 2 ken wide and 6 mats, about 12 x 9 ft.
4. **0096 (holding cells): where the cell stood.** Pass P4: the cell in the first court at Neixiang (0096 already has a
   magistracy's temporary cell in the quarter that held its court rooms) - record the Neixiang case beside it.

**New registry keys** (at most ten): each of pass P4's sources A-D and F that is not registered.

## The procedure (session S3: write)

1. `make archive-inbox`. Then `make research-claim Q="<each question>" FEATURE=417`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `417: `.
4. Append to `specs/417-all-seeds-pass/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S3` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per item, its verdict and fragment file and the block's words a claim
   can quote; each search named; the new keys; leads not followed.
5. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

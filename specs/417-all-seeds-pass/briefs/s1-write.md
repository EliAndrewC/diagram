<!-- page-load: kind=assertions -->
# Brief - feature 417, the water and the fields' sources. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-backlog-pages`). The project's CLAUDE.md files apply to you, the research
record's `CLAUDE.md` above all.

**What is asked.** Feature 417 T36 relabeled the engine's research claims from research passes. Some claims rest on a source a
pass found that NO page of the record holds yet. The plan (D37 b) puts each such source on the page its question belongs to,
so the claim can cite the page. Record each finding below on its page, as the record's rules say: the passage verbatim from a
page a reader can open (English translation marked as one, the original after), its date of evidence, and the reading
(ATTESTED / ATTESTED ONLY FOR / NOT ATTESTED). Write what the page says; where a source does not read as the pass says, write
what it does say, or SILENT. Do not edit any engine code or claim.

**Your passes (leads, not citations):** `pass-P2a-hamlet-water.md`, `pass-P2b-fields.md` under `specs/417-all-seeds-pass/evidence/t29/`. Read each passage on its own
page (`make archive-find` first) before citing it.

## Your items

1. **0059 (the intake and its weir): the weir's skew.** Pass P2a: Murakami's survey of weirs, a mean skew of 30 degrees to
   the stream, range 5-78, most under 30. Record it where 0059 speaks of the weir's line across the stream.
2. **0054 (how channels bend): straight runs.** Pass P2a: Leopold and Wolman (with Langbein) - straight reaches longer than
   about ten channel widths are rare in natural streams. Record it beside 0054's bend radius (meander-enwiki already cited).
3. **0064 (water mills): the wheel's size.** Pass P2b: the Shinguruma wheel, 4.8 m across, called large (the 1959 rebuild;
   0064 already cites the Oguruma and Shinguruma). Record the size and its date.
4. **0005 (paddies and their plots): the Kami-Baba parcel's shape.** Pass P2b: the 1684 Kami-Baba survey parcel of 16 x 10.5
   ken (0.656 its sides' ratio). 0005's drawing page already names the parcel's size; record its sides.

**New registry keys** (at most ten): Murakami's weir survey; Leopold and Wolman (if not registered); the Shinguruma source (if not registered); the Kami-Baba survey (if not registered).

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="<each question>" FEATURE=417`.
2. For each page or file you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`). A new source takes `make reserve KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `417: `.
4. Append to `specs/417-all-seeds-pass/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S1` section:
   `- SECTION=<NNNN>/<id>` for each section you changed; per item, its verdict and fragment file and the block's words a claim
   can quote; each search named; the new keys; leads not followed.
5. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

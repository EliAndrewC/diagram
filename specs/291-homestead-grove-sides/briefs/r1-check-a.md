<!-- page-load: kind=check -->
# Brief - feature 291 (how many sides a homestead grove takes), group R1, session 2a: check and apply

You are a FRESH session for one part of feature 291. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-readability-2`); the project's CLAUDE.md files
apply to you, the research record's `CLAUDE.md` above all.

**What the feature is for.** The record said, flatly, that before 1868 a farmstead's grove went round the whole house.
Session 1 rewrote the homestead grove's entries so each shape is attributed to the region that attests it (Izumo's
ring, Sendai's two sides, Tonami's open front) and stated the GM's decision of 2026-09-29: the grove's sides are
rolled per settlement, 50 / 30 / 20 for two / three / four sides, 37.5 / 22.5 / 40 on flood-prone ground. Its handoff
is `specs/291-homestead-grove-sides/briefs/r1-handoff.md` - read only your own lines
(`make lines FILE=<handoff> KEY="SECTION=homesteads/(010|710)"`).

**Your questions:** Q=0036, PAGE=homesteads SECTION=710
**Your registry keys:** none

**Two facts the engine work fixed after session 1, for 710's rule paragraph** (write them in; they are this feature's
decisions, each labeled): the thinner band of a grove's sides away from the wind is ONE TREE deep - 17 ft, two mean
crown radii (the crown size is at `vegetation.html#forest-density-and-crown-size`) - a GUESS, since no page read gives
its depth; and a grove on all four sides is broken once, at the middle of its front, for a way in about 12 ft wide - a
physical necessity (the farm must be reached), its width a GUESS (no old page gives an opening's width). 710 is at
19,941 bytes with its notes, the cap being 20,000: make room by tightening its own prose, or split its shape half into
its own question (the record's `CLAUDE.md`, "A question has a size") - never by cutting a finding.

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle Q=<NNNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format` (in `.claude/skills/diagram`), each agent naming its own MANIFEST.md and nothing else; and
   `make check-bundle KEY=irie-2020-igune` for `source-applicability` - the key is now also used to date the two-sided
   grove to the early Edo period, and its write-up must say honestly what it can and cannot carry (a 2020 paper
   reporting a 1963 book and a 1993 local society). An ABSENCE note that says what was searched is checked as one.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source
   `source-applicability` rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess) and the
   key is listed in your report. Add the two facts above to 710 in the same message. Then `make glossary` if a term was
   added, `make record && make citations`, the four record tests (`make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`) and
   `python3 scripts/check-question-size.py` from the clone root, ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`; a
   `record-format` on 710 again if its prose moved much). A PARTIAL left after it is labeled honestly and left.
4. **Commit** only the files you changed (`git -C` with paths), message beginning `291 R1 check:`; do not push.
5. **Report.** Append to `specs/291-homestead-grove-sides/briefs/r1-checks.md` (with `make append`) one line per
   question and key: its verdicts and anything left open. Your last message is one paragraph.

<!-- page-load: kind=assertions -->
# Brief - feature 444 T18, the single-field cap. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** The GM, 2026-10-29: "do a research pass if needed on what is the maximum size of a single rice paddy field for
these kinds of settlements. we can cap out at something approximating whatever that size is, and then larger settlements just have
multiple fields". The research pass is done: `specs/444-work-budget-program/research/t18-field-cap-pass.md` holds every source with
its verbatim passage. Record it.

## Your items

1. In 0017 ("How much farmland a settlement works, and in what tracts"), a section on HOW LARGE ONE TRACT GROWS: one contiguous paddy
   tract, watered from one pond, canal or spring, ran from about 1 to about 45 ha (Shaanxi's village canals 10-700 mu, Chongyang's
   ponds 210-730 mu, Dojita's 7 chō from one pond, the Yayoi blocks of 1.5-7.5 ha); the largest found is Fei's 986-mow yu (about
   60 ha), which Fei says was cut into smaller drainage units for working; a settlement with more farmland had several tracts (Fei's
   eleven yu, Huapi's three channels); above about 100 ha the sources describe a multi-village canal in shares, not one field. Each
   claim footnoted to its source as the record cites; Chinese and Japanese quotations with their English marked as translation.
   If 0017 has no room (research/CLAUDE.md "A question has a size"), make it a new question and point 0017 at it.
2. Its drawing page: the map's single field capped near the largest tract (about 60 ha), a settlement past it drawing more than one
   field - labeled as the record labels a drawing decision (the cap: historically accurate, Fei's largest yu; the exact figure a
   knob within the attested band).
3. Record each source the pass read with `make source-outcome URL=<u> OUTCOME=cited:<key>` once cited.

## The procedure (session W: write)

1. `make research-claim Q="0017" FEATURE=444` (and the new question's, if you make one).
2. Edit the fragments, then `make record && make citations` and the record tests; `make quick`'s question-size check passes. Commit
   with messages opening `444 T18: `.
3. Append to `specs/444-work-budget-program/briefs/t18-handoff.md` (with `make append`) a `## Session W` section: each section changed
   (`- SECTION=<NNNN>/<id>`), the cap's figure and its label as written.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

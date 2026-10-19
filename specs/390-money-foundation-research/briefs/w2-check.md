<!-- page-load: kind=check -->
# Brief - feature 390, session 3: finish the owed checks and the open findings

You are a FRESH session for one part of one feature. This brief is the whole of what you need. Work in this clone
(`/diagram/.clones/money`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**Where it stands.** Sessions 1-2 wrote and checked four money questions: 0248 (the koku), 0249 (the Kyoto basket), 0250
(unskilled wages) and 0251 (land against yield). Read the last line of
`specs/390-money-foundation-research/briefs/w1-checks.md`, "STILL OWED:". It names 20 units that only round 2's own
fixes moved, and the open findings no check could EDIT.

## The procedure

1. **The open findings first.** Fix each by hand, each in the record's own form:
   - 0248's "the manual does not give the sheng's size" becomes an absence note, with its search in a comment.
   - maff-2023 gets a quoted caption naming the 2023 brown-rice crop. Read it on the PDF; if no caption says so, narrow
     the sentence instead.
   - ihns-bunongshu-1 is PARTIAL: quote the words that make it a hired hand and the old rule, or narrow the claim to
     what the quote carries.
   - 0248's 100 L shi against en.wiki's 103 L dan: give each with its own source, or one where only one is quoted.
   - kin and zhong: gloss them only from a sized source; otherwise state the unit without a size.
   - 0251's Kumehara "headman's family, Saitama plain": footnote it or cut it.
   - The miyashiro 1700 deed's two-year term: quote it.
   - The l7r-budgets registry entry names its "Imperial budget scale" section.

   Then run `make record && make citations` and the record tests, and commit with `390: `.
2. **Then the checks.** `make record-owed` names what is owed now. In one message, dispatch one agent per unit from its
   own bundle. A check owed a third round on one subject goes to `round-arbiter` first; with several at their cap, use
   `make arbiter-bundle BATCH=1` for one ruling. Run `make apply-edits` on each reply, apply what it refuses by hand, run
   `make record-checked`, and commit with `390: `.
3. Re-check only what moved, once. Do not push.
4. Append one line per check to `specs/390-money-foundation-research/briefs/w1-checks.md` with `make append`, then a
   final `STILL OWED:` line (or `STILL OWED: none`). Your last message is one paragraph.

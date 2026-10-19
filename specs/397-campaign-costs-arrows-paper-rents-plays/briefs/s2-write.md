# Brief - feature 397, campaign costs II. Session 2: write (the English players and the notice board)

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you, the
research record's `CLAUDE.md` above all: read its section "Comparative money sources" before item P1.

**What is asked.** EliAndrewC/diagram#4 (gm-assistant's money skill), the request verbatim in `specs/397-campaign-costs-arrows-paper-rents-plays/request.md`. Session 1
wrote the four money questions (its handoff: `specs/397-campaign-costs-arrows-paper-rents-plays/briefs/s1-handoff.md`). This session writes the two remaining items.
Research only: edit no code, modal, sheet or canon.

## The passes (leads, not citations)

`specs/397-campaign-costs-arrows-paper-rents-plays/passes/q-plays.md` (its "England (comparative)" lines) and `specs/397-campaign-costs-arrows-paper-rents-plays/passes/q-notices.md`. Read each passage on its page
before citing it.

## Your items

- P1 **A new comparative question: "Did English traveling players gather their money at the door or pass a hat?"**
  Reserve it with `make reserve KIND=question KEY=<heading id>`. Tag it `subject=comparative,money; setting=city;
  level=counts-and-measurements`, with no drawing page; it goes in the `comparative-money` section. Register its sources
  with `kind=comparative` in their TAGS. It opens with the category's intro (`<p class="intro">`): a yardstick from another
  society for players, never Rokugan's own figures. The GM asked for it himself ("pass around a hat ... That's what my
  high school English teacher said anyway. I don't know if that's true.").
  - Gathering at the door, ATTESTED ONLY FOR that: the 1583 inn-yard depositions (the gatekeeper still taking coin after
    the play began) and Platter 1599 (a penny at each further door).
  - Passing a hat mid-play: NOT ATTESTED by any period source; Lawrence 1912's "secondary gathering in the galleries" is a
    modern inference, labeled as one.
  - An English day wage beside it: silent (an absence note) unless a usable source is found.
- N1 **Extend 0190 (`research/questions/0190-notice-boards-kosatsuba.html`, the research page only; the drawing page is
  unchanged).** Add, ATTESTED ONLY FOR Edo: what an official notice was made of (a wooden plaque written in ink) and who
  could post (pasted paper only on structures the magistrate permitted). The village case is silent (an absence note).
  Claim it with `make research-claim Q=0190 FEATURE=397`.

## The procedure (session 2: write)

1. `make archive-inbox`. Then `make research-claim` on the new number and 0190, `FEATURE=397`.
2. For each page you cite: `make archive-find`, `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`). New sources: `make reserve KIND=registry ...` and their two write-ups.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_comparative_sources.py"`).
   Commit with messages opening `397: `.
4. Append to `specs/397-campaign-costs-arrows-paper-rents-plays/implementation-check.md`:
   - for P1: `- NNNN: no code implements it - a comparative money question consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`;
   - for 0190: a line saying what code draws the notice board (`grep -rniE 'kosatsu|notice.?board' l7r pool`) and that the
     added facts (material, who could post) change nothing it draws.
5. Write `specs/397-campaign-costs-arrows-paper-rents-plays/briefs/s2-handoff.md`: a `- SECTION=NNNN/<id>` line for P1 and `- SECTION=0190/<id>`; the figures and verdicts;
   the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

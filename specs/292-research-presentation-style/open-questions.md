# Open questions for the GM - feature 292

The sweep's check sessions left 26 items "for the GM". Each was put to the `escalation-check` agent (2026-10-01), which
cut 24 as decisions the project's own rules already settle (they are listed at the bottom, with what the session does
about each, for your information - no answer needed) and merged the other two into the one question below.

Write your answer under **Your answer:**, in your own words; the session reads this file and applies it. The feature
does not close until every question here has an answer.

---

## Q1. Inside a provincial city's wall, is a senior samurai's house walled?

Two sections of the record, both written for the city generator that has not been built yet, say opposite things:

- **No.** "How our maps draw the samurai quarter" (`rendering/cities/government`, section 030) says no samurai house
  inside the wall is walled - the governor's compound is the city's only walled samurai compound - and labels that a
  **deliberate deviation** from history. "How our maps draw a capital differently from a provincial city"
  (`rendering/cities/capitals`, 390) builds on it: walled compounds are ordinary in a domain capital, not in a
  provincial city.
- **Yes.** "How our maps draw a samurai's lot and house" (`rendering/cities/government`, 280) encloses every lot by
  rank, a senior house behind an earthen wall with a long-house gate, as the sources say castle-town senior retainers
  had; the servants'-quarters section (080) rests on that wall.

No ruling of yours stands behind the deviation: a research session labeled it in feature 269, and the feature-271 audit
already noticed the two disagree. Nothing drawn depends on it yet (no provincial city is generated), but the generator
will be written from one rule or the other, and whether the setting departs from history here is the setting's call.

- **(a)** Keep the deviation: inside a provincial city's wall, senior samurai houses are unwalled; 280's earthen wall
  and gate apply to capitals and to country estates.
- **(b)** Drop the deviation: every lot inside the wall is enclosed by rank, as 280 says, and the capital-versus-
  provincial-city contrast in 390 is rewritten around something else.

**Recommendation: (a)** - it keeps the one visible thing that tells a provincial city's map from a capital's.

**Your answer:** (b) the earlier ruling was never intended to be a deviation from historical norms, so when we eventually get to rendered city maps then we should render whatever our research shows was actually true based on historical Japan and China

---

## For your information - a fact about the shipped maps, not a question

The domain capital's magistrate's office is drawn at 224 by 148 ft, about three times the area the provincial cities
draw - against your ruling of 2026-08-09 that a capital gets no bigger an office (a code comment there still says
"roughly 2x"). The provincial size is a calibration, so the session brings the two into line itself as part of this
feature's closing pass and records it.

---

## Cut by the escalation check - what the session does instead (no answer needed)

1. The `l7r-budgets` registry link (two items) needs no ruling: your campaign notes are canon and keep their registry
   link. The two PARTIAL quotes and the grounds note there get their stored originals and a citation or absence note.
2. BenchNoticeBoard is relabeled a guess, matching the rendering section it is written from.
3. The town-framing question is already answered (presentation 010: a town map is as much about its surroundings);
   the spec heading is corrected to "for a provincial city".
4. The Takayama survey's figure (site 9,807 m², total floor 3,018 m², about 31%, floor area not footprint) is written in
   as a citation, and the 37-42% built-cover guess revisited against it.
5. The byre's drawn share is calibrated or labeled; the StorageShed modal is narrowed to what its sections say, and
   labeled as its rendering section is; the Privy and HenCoop modal fixes are applied.
6. The Garden modal is relabeled a guess, matching its rewritten section.
7. The road at a compound gate is the road the compound stands on, at that road's width (ways 070); the Imperial road
   is 30 ft on every sheet, and Ochiba's 13.3 ft approach is checked against that.
8. The paddy's shoot-scatter rule moves to the rendering section, as the style guide says.
9. The dike band past the Echizen 18 ft bound is brought under it or labeled a convention with its reason, and the
   PerimeterDike modal's "6-10 m" (the pond dikes' figure) is corrected.
10. The county-yamen encyclopedia and the fujita-2007 PDF go on your download list, as the rules say.
11. A small practice ground inside the wall is attested (Chongming); whether a map draws it is a knob.
12. The T-shaped town plan (ways 180) joins the four-form town knob in towns 230; the crank at a town's ends is noted
    as future work for the generator.
13. The day-office and official-study bullet moves to the office-hall rendering section, and the DayOffice and
    OfficialStudy modals follow it.
14. The retitles the checks proposed are made where the style guide calls for them, their links re-aimed.
15. A seventeenth-century date is inside the record's pre-1868 window, so nothing is gated by period.
16. The town's inn count is reconciled (a calibration), and a walled town's inn stands in its gate market, as towns 080
    says.
17. The downstream intake side, attested only in modern practice, is dropped under your ruling of 2026-09-28.
18. The KarosHouse modal gives the guess for the hand-drawn house and "accurate" for the county-town house.

# Research: what the place card may state

**Run**: `source-reader`, 2026-08-29, before the spec was finished (constitution XII, "a guess is the
last resort - run the research pass first, always"). One fetch attempt per host; no AI-generated
encyclopedia; a search summary is a pointer, never a source.

The pass was commissioned to answer one question the GM raised in their own words - *"the fact that
this is a hamlet where rice is farmed, like, if this is the most common type of hamlet that exists
or whatever"* - and it came back with an answer that changed the spec twice.

---

## R1 - The historical record does NOT rank settlement forms by frequency

**Asked**: may the page say that an outlying wet-rice hamlet under a parent village is the ordinary
or commonest kind of rural settlement?

**Found**: the CATEGORY is well attested, its administrative mechanism is attested, and its
prevalence varies by terrain - but nothing read ranks it against other forms, and no fetchable
source gives a national frequency.

- ja.wikipedia, 枝郷 (*edagō*), READ:
  「もとの村を本郷（本郷、元郷、親郷、親村、本村）とよぶのに対し、新村を枝郷（枝村、子村）と称した。」
  and 「多くの場合、本郷の庄屋・名主から村高が分け与えられていた。」 - the parent settlement is the
  *hongō*, the newly founded one the *edagō*, and in MOST cases its assessed yield was allocated from
  the parent village's headman.
- National Diet Library reference service (crd.ndl.go.jp), READ:
  「対外的に村を代表する集落が本郷・親村、支配行政上で本郷・親村に従属しているのが枝郷（枝村）・小村です。」
  and 「年貢の賦課徴収では検地帳・年貢免定は親村の名義で、小村の年貢納入は親村を通してしかできませんでした。」
  - the land registers and tax quotas stood in the PARENT village's name, and the branch could pay
  its tax only through the parent. This is the mechanism, and it is the good reason a branch hamlet
  has no headman of its own standing: there is no separate tax unit for one to administer.
- J-STAGE, *The Relation between Administrative Village and Natural Village in the Edo Era*
  (abstract level), READ: "Some of the administrative villages were composed of one natural village,
  and others several natural villages. The former was found mostly in a plain area, and the latter in
  a mountainous area. ... Of all Konas a remotely situated Kona was called Edago, a branch village."
  A regional case study; a terrain pattern, not a frequency ranking.

**Decision**: the page states NO historical ranking. It states the SETTING's ranking, which is
decisive and is the GM's own: `l7r.md`'s median-domain table gives ~1,296 hamlets against ~216
villages, ~36 towns, ~6 provincial cities and one capital, with **~40% of a domain's inhabitants
living in a hamlet** - the largest single share of any tier. That answers the GM's question honestly
without borrowing authority the historical record did not lend.

**Sources:** `edago-ja`, `ndl-hongo-edago`, `jstage-admin-natural-village`

---

## R2 - Wet-rice dominance: NOT FOUND, and `kokudaka` must not be pressed into service

**Asked**: was wet-rice paddy the dominant agricultural regime, so that a rice-farming hamlet is the
typical case?

**Found**: NOT-FOUND. Every specific source either did not address the paddy-versus-dry-field land
share or could not be fetched (cambridge.org returned an unrelated extract; an OUP property-systems
paper discusses productivity and taxation but no land share; a Japanese government land-history PDF
came back unparseable; apjjf.org and gov-online.go.jp returned 403 on their single attempt).

**The trap, recorded because it is inviting**: `kokudaka` is universal and rice-denominated, so it
LOOKS like evidence. It is not. en.wikipedia's Kokudaka entry, READ: "The amount of taxation was not
based on the actual quantity of rice harvested, but was an estimate based on the total economic
yield of the land in question, with the value of other crops and produce converted to their
equivalent value in terms of rice." That is a FISCAL convention covering dry field as well as paddy.
Citing it for paddy-dominance would be citing a source for something adjacent to what it says - the
exact failure "read what you cite" exists to stop.

**Decision**: the page does not claim wet-rice dominance. It says what the map draws - this hamlet
farms rice - which needs no ranking at all.

**Sources:** `kokudaka-en`

---

## R3 - "A hamlet has no headman of its own" is SETTING CANON, and a deliberate deviation

**Asked**: is the project's long-standing rule attested?

**Found**: CONTRADICTED as a flat rule. The same ja.wikipedia 枝郷 entry that supports the common
case records the exceptions: 「中には庄屋や組頭などが置かれ、本郷並の扱いを受けていた枝郷も存在した。」
- some branch hamlets had their own *shōya* and *kumigashira* and were treated on a par with the
parent village. en.wikipedia's *Nanushi* entry ("For each village there was one nanushi") does not
resolve whether "village" means the natural hamlet or the administrative unit containing several,
which is exactly the ambiguity at issue.

**This is not a defect in the project's rule.** The rule is not a historical finding: it is the GM's
canon, stated twice in `l7r.md` - a hamlet "is overseen by a village headsman who lives in the main
village and not in the hamlet", and, under *Do hamlets have their own village headsman?*, "No, but
with a caveat" (the caveat being about the headman's workload and stipend, not about hamlets having
one). Rokugan is deliberately simpler than Edo Japan here.

**Decision**: the place card states the rule as the setting's, and the modal DISCLOSES that history
is messier - which is precisely what constitution XII's "deliberate deviation ... Legend of the Five
Rings canon" class is for. The reader is never told a simplification is a finding.

**Sources:** `edago-ja`, `nanushi-en`

---

## R4 - Population per household: the setting is firmer than the record

**Asked**: a citable source for ~5 inhabitants per household.

**Found**: SUMMARY-ONLY. Kinoshita 1995, *Household Size, Household Structure, and Developmental
Cycle of a Japanese Village: Eighteenth to Nineteenth Centuries* (journals.sagepub.com, HTTP 403 on
its single attempt) - the abstract synopsis reads "The mean household size also rose from about five
to six persons during the same period" (1760-1870). That is ONE village in Tōhoku and a RISING
trend, not a fixed typical figure. Cornell and Hayami 1986 on the *shūmon aratame chō* registers
likewise 403'd. encyclopedia.com's Hayami entry was READ but gives no absolute figure, only "a trend
toward smaller households".

**Decision**: the card rests on the setting, which is unambiguous and is the authority for this map
anyway: `l7r.md`, "The median household size is generally assumed to be 5", and "Most hamlets have a
population of 50-100 (i.e. 10-20 households)". The historical figure is recorded here as
SUMMARY-ONLY support rather than as the basis.

**Sources:** `kinoshita-1995` (SUMMARY-ONLY), `hayami-encyclopedia`

---

## R5 - The shrine and the burial ground: no historical support found either way

The pass found NOTHING on whether a branch hamlet had its own shrine (*chinju*) or graveyard - not
CONTRADICTED, simply absent from every page that could be read. The project's existing rule already
rests elsewhere and is not reopened here: `settlements/religion-and-death.md` carries the researched
district-catchment finding for the burial ground (including the honest note that Edo Japan DID bury
per-settlement, and why the drawn convention stays defensible), and the shrine's absence is the
GM's tier rule in `settlements.md`.

**Decision**: the place card states the shrine and burial ground as the setting's tier rule, in the
same breath as the headman, and links the burial ground's own recorded reasoning rather than making
a fresh claim.

---

## What the page ended up allowed to say

| Claim | Rests on | Class |
|---|---|---|
| this is a hamlet: a small outlying farming community belonging to a village district | `l7r.md` line 153 | setting canon |
| the commonest kind of settlement in a domain; ~40% of inhabitants live in one | `l7r.md` median-domain table | setting canon (NOT a historical ranking) |
| ~N farmhouses, population ~5N | `l7r.md` household size 5, hamlet 50-100 / 10-20 households | setting canon |
| no headman, shrine or burial ground of its own | `l7r.md`, `settlements.md` | setting canon, with the historical messiness disclosed |
| the district is named for its main village | `l7r.md` "Place Names" (a GM SOURCE block) | setting canon |
| it grows rice / millet / soy / ... | the map's own ink | measured |
| the district lies east; an Imperial road runs south | the map's `.notes.md` | authored |

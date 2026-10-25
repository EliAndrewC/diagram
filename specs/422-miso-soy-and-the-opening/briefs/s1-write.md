<!-- page-load: kind=assertions -->
# Brief - feature 422, miso and soy sauce: how much, and era by era. Session S1: write

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-money-marks`). The project's CLAUDE.md files apply
to you, the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant asked on EliAndrewC/diagram#18 (verbatim in `specs/422-miso-soy-and-the-opening/request.md`):
Q1, how much miso (kg) and soy sauce (liters) an ordinary adult of a laborer's household used a year (Kyoto or Osaka, mid-1700s,
or the nearest with a figure); failing that, the soybean per kg of miso and per liter of soy sauce in Edo-period practice and the
share of a household's soybeans going to miso, soy sauce, tofu and natto; the source of Bassino and Ma's 52 kg; and what of the
52 kg is left for tofu and natto. Q2, miso and soy sauce (and in China soy sauce or bean paste, 醬) priced in any era the record
holds (`research/assets/money-conversions.json`, "eras").

**Your passes:** `specs/422-miso-soy-and-the-opening/passes/q1-quantities.md` and `passes/q2-eras.md` (its script
`passes/q2-red.py` reads the GPIH sheet) - leads, not citations: read each passage on its page before citing it; where a page does
not read as the pass says, write what it says, or SILENT. No quantity is estimated; every per-person division, unit conversion and
cross-source sum is this project's arithmetic, labeled so (the pass's "about 31 kg left for tofu and natto" combines two sources:
if you give it, say so; the verdict for the remainder is that no source attests it).

**The silver rate:** the Mitsui cells are monme. Give each era's means in monme, and in grams of pure silver at the era's own coin
rate (`money-conversions.json`, `units.monme.silver_g`, from 0287), labeled; 0249's existing grams at Bassino and Ma's 3.11 g
stay as 0249 states them, and the new question says which rate each figure uses (gm-assistant takes the monme at its era rates:
#18 issuecomment-6402725625).

**Already in the record - name by file, do not repeat:** 0249 (the basket; feature 420 added the Mitsui Kyoto miso and soy sauce
of 1745-54 at 3.11 g), 0286 (the Japanese eras), 0301 and 0302 (observed or reconstructed, era by era), 0262 (sake), 0273 (salt).

## Your items

1. **A new question** in "Money and prices", `subject=money`, its title asking how much miso and soy sauce a household used and
   what they cost, era by era. Sections:
   - **How much**: no consumption figure for a city household (SILENT, with the search); the beans for miso (『家訓全書』 1760,
     Shinano, through Shigematsu 2022; Hirosaki 1816), the beans for soy sauce (『廣益國産考』 1844), each ATTESTED ONLY FOR its
     place, a household average including children; the recipes' proportions (『本朝食鑑』, 『和漢三才図会』) and that none gives a
     yield (SILENT); Edo's 1821 soy sauce arrivals only if a readable source names the document, as an upper bound, the population
     assumption stated with its source or left out; Bassino and Ma's 52 kg from their calorie and protein target (their words) and
     their 1921-25 12.9 kg; the tofu and natto remainder as above; and the MODERN yields gm-assistant's addendum asks for (kg of
     miso per kg of dry soybeans for a rice-koji miso; liters of soy sauce per kg of soybeans with equal parts wheat), from
     `passes/q1-yields.md`, each with its source's proportions set beside the Edo prescriptions', labeled modern; whether a
     modern yield may stand in for an Edo one is the GM's call, not the page's.
   - **What they cost, era by era**: a table of the Mitsui means per era (n, mean, range; miso per 10 kan, soy sauce per koku;
     grams at the era rate), with the city each row is from; edo-1860's rise within the era; osaka-1712 (one Osaka 1713 soy sauce
     cell) and osaka-1706 (Edo rows only) as what they are; Kimura's osaka-1620 "Soya" as the sheet heads it, soy sauce a reading;
     tokyo-1882 SILENT within its years, the 1887 "Soy" nearest; the other Japanese eras and every Chinese era SILENT for miso,
     soy sauce and 醬, with the searches (Timkovski prices vinegar, not soy; the 1736 list prices a 醬 mold, not 醬).
2. **Pointers**: one sentence each in 0249 (the new question for quantities and the other eras; and that its 1.28 g and 1.57 g
   are at 3.11 g, the era rate giving 0.71 and 0.87 - as this project's arithmetic), 0301 and 0302 (a miso and soy sauce column is
   in the new question).

**New registry keys** (at most ten): Shigematsu 2022 (if not registered); the eonet pages for 『廣益國産考』 and the recipes; the
GPIH Osaka_1600-1650 (Kimura) file if not registered; the matsu-haku leaflet only if cited.

## The procedure (session S1: write)

1. `make archive-inbox`. Then `make research-claim Q="0249" FEATURE=422` (and `Q="0301"`, `Q="0302"`), and claim the new
   question's number (`make reserve`).
2. For each page or file you cite, `make archive-find`, then `make source-pages`, then `source-reader` from a bundle (`make
   check-bundle KEY=<k> WHOLE=1`; page images with `IMAGES=`; spreadsheet cells as a row dump). A new source takes `make reserve
   KIND=registry KEY=<k> URL=<u> TAGS="..."` and its two write-ups.
3. Write the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Mark each new amount that is a sum paid for the money tooltip as `research/CLAUDE.md` says (`make money-candidates CHECK=1`
   must exit 0). Commit with messages opening `422: `.
4. Append to `specs/422-miso-soy-and-the-opening/implementation-check.md` (create it if absent) one line per touched question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/422-miso-soy-and-the-opening/briefs/handoff.md` (with `make append`; create it if absent) a `## Session S1`
   section: `- SECTION=<NNNN>/<id>` per section changed; per figure asked, its verdict and fragment file; searches; new keys; leads
   not followed. This is task T01.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

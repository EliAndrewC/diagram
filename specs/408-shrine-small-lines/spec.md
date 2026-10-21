# Feature 408: the shrine builder's small lines (diagram#10)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-21

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-21, "The GM assistant repo is currently watching that, so please go ahead and do it."

The GM asked for issue #10 to be worked (his words, quoted above); a money research request gm-assistant opens for him is
approved by his asking (GM 2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future").

**Input**: `request.md` (issue #10 verbatim), `passes/` (four search passes, 2026-10-21, one per group of the issue)

## Why

gm-assistant's shrine builder prices about fifty small lines (earthwork and grounds, small carpentry and furnishings,
remains and small rites, two small buildings, carrying stone) by its own estimate. The record answers a few of them
already (0255-0258, 0260, 0268-0271) and is silent on the rest; the issue asks for a verdict on each, the lines marked (S)
first.

## User Scenarios & Testing

### User Story 1 - Every line of #10 has a verdict and a fragment (Priority: P1)

gm-assistant reads, per line of the issue, the fragment file that answers it, the verdict, and what is still open.

**Acceptance Scenarios**:

1. **An item an earlier fragment already answers:** the reply names that file and the estimate it answers, and the record
   is not repeated (gm-assistant, #10: "just name the file and say which estimate it answers").
2. **An item a pass found:** the figure is written into the existing money question it belongs to (grounds and earthwork
   0257/0269, small carpentry and furnishings 0258/0270, remains and small rites 0271, the two halls 0268, carrying stone
   0260), quoted verbatim from a public page, with its verdict (ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED); a
   new question only where none of those fits.
3. **Several items priced together:** the combined figure is given with the list of what it covers (gm-assistant, #10).
4. **An item no pass found:** SILENT means no NEW source was found. Where the record already holds a figure for the line
   (or its nearest), the reply names that file and the line is not given a new absence note; only a line the record is
   silent on gets one, with the search named.
5. **Wages beside each figure:** the craftsman's and the laborer's day wage of the same place and period where a source
   gives them; otherwise SILENT naming the nearest, with its class, place, unit and gap in years.

### User Story 2 - The (S) lines are searched first (Priority: P1)

**Acceptance Scenarios**:

1. Each pass searches its group's (S) lines before the rest, and the reply lists the (S) lines first.

### Edge Cases

- A source only the GM can fetch goes on `research/to-download.md` (`make download-add`), named in the reply as a lead.
- A figure the project computes (a per-tsubo rate, a conversion to days) is labeled as the project's arithmetic.
- No price is converted to koku; that is gm-assistant's step.

## The findings, item by item (the passes, 2026-10-21, checked against the record's pages; leads until read on the page)

Verdicts are the passes' readings; the write sessions confirm each on its page before citing it, and a passage that does
not read as the pass says is written as SILENT or NOT ATTESTED instead. "Already answered" names the page that holds the
line or its nearest figure (FR-005): the reply points there and the record does not repeat it.

**Group 1, grounds (new figures into 0257):**
- Already answered: clearing and leveling (0257, Osaka 1620s earthwork 7-18 monme a tsubo with the ledger's laborer
  wages); raising a standing stone (0257, 1620 hill stone at 1.3 monme a man to bring out, 1.5 on the sledge; a 150 kg
  block on one man's back); raising a burial mound (0257, SILENT).
- New: (S) swept earth path, ATTESTED ONLY FOR sweeping a road or house grounds for an official's visit, Kawachi 1704
  (Murata 1986, Table 2): crews of 7 to 40 laborer-days at 1.5 monme a man-day. Clearing and leveling gains a second case
  beside the Osaka one: the same works' estimates, 5.98 monme of laborers' wages a tsubo of earth (5 for one section),
  against the same 1.5 monme day; about 4 man-days a tsubo is the project's arithmetic.
- New, Qing comparison: sakaki hedge, one laborer per 4 zhang of palisade or bamboo hedge; standing stone, two laborers a
  zhang lifting stone for a bridge (揚州畫舫錄 卷十七, 1795), no wage given.
- SILENT, the search named: (S) himorogi, (S) moss court, (S) dipping place at a stream, white-gravel court and path, ring
  of river stones (Qing pebble paving reckoned by the square zhang, no labor figure), sakaki hedge in Japan.

**Group 2, small carpentry and furnishings (new figures into 0258; sawing into 0268):**
- Already answered: (S) origin-story board under a little roof, nearest (0255, Kumehara 1830, rebuilding a notice board,
  50 carpenter-days at 2 monme printed, its sums fitting 20); felling own-woods timber (0268, Shibasaki 1840, ten
  woodcutters' wages and food 2 bu and some coppers); lattice door, nearest (0268, Shibasaki 1841, twelve doors and
  screens by a joiner, 1 ryo 2 bu 2 shu); (S) founder's plaque, the writing side (0271, no Japanese fee; Zheng Banqiao's
  1759 list) and its painting (0258, SILENT); offering chest and lock (0270, SILENT); wooden torii (0257, SILENT); the
  cover-shed and pavilion roofs (0256, the 1749 Kasuga re-roofing; 0268, Shibasaki's roofs); name-stone, nearest stele
  (0269, SILENT); offering table (0258, SILENT).
- New: (S) founder's plaque, the carving side, ATTESTED ONLY FOR carvers' day rates: the Nakai carvers of Tanba, 3 monme a
  day and 0.6 for meals (1810s-20s), beside the region's carpenters' 1.5-2.5 monme (AIJ 396, 1989); a Kyoto carver's
  per-piece prices for temple carvings, 32-225 monme (year not given).
- New: (S) origin-story board, an upper bound beside 0255's notice board: Edo's carved standing shop signboards, 70-80 ryo
  small and 140-150 large with posts and official fees (Morisada, 上 koma 82, 1837-53); its painting SILENT.
- New: pair of carved wooden guardians, ATTESTED ONLY FOR the carver's day rate, komainu at 3 monme a carver-day (1814-15),
  days not given (0269's guardian lions stay SILENT for stone).
- New (0268): sawing, the sawyer's day wage, 1.8 monme at Miyazu in 1777 (with carpenters and roofers) and about 1.5 monme
  with rice at Fukuchiyama; sawing by the amount SILENT.
- New, Qing comparison: a Yunnan county hall's restoration stele of 1902 (至聖殿重修碑記): incense burner, stele core and
  carving 8,650 wen; tablets, niche and lattices 280,000 wen; 1,300 wen a tael by the stele; no wage given.
- SILENT, the search named: (S) flat stone as offering table, (S) bamboo offering tube, refitted table, paper wand, wooden
  chest, stone-set box, low fence, bamboo spout.

**Group 3, remains, small rites and two buildings (new figures into 0271):**
- Already answered: the mortuary hall and the water pavilion, nearest (0268, Shibasaki's small worship hall 11.5 ryo, its
  thatch helpers 2 ryo 3 bu and roof boards; 0255, the Mitake repair with its covering house); four green bamboo with a
  rope, the ground rite (0258, no fee found; gains the new search and the 1544 fee below); stone coffer (0269, SILENT);
  the burial mound (0257, SILENT).
- New: (S) head mound, marker and rite, ATTESTED ONLY FOR its funding as a whole, Sannohe 1784-85 (Aomori prefecture's
  page): heads bought at 24 mon each, 60 kanmon given by worshippers, from which four earth mounds and a stone memorial
  were built and three winters of rites held; the combined figure with what it covered, no builder's cost.
- New: the ground rite's four bamboo with a rope NOT ATTESTED for the Edo period (Sekai Daihyakka calls it the present form,
  the rite gaining its place only in late Edo); a ground rite's fee ATTESTED ONLY FOR 1544, 2 kan 500 mon at Koyasan.
- New: unveilings (kaicho), ATTESTED ONLY FOR a per-head fee at the temple, 100 mon at Tsu (1790, 1834), and Zenkoji's
  travelling unveilings in Edo: 1692 takings 10,210 ryo against 914 spent; 1820 3,062 against 3,819; 1803 a temporary
  hall built for 93 ryo, the takings short of the costs.
- New, Qing comparison: the shroud, a Fuzhou widow's 15 dollars set aside for her coffin and part of her burial, beside
  carpenters' 20-30 cents a day (Doolittle, 1865).
- SILENT, the search named: (S) rope between two trees as a gate, precinct rope, naming a tree, hallowing a grove, the
  shroud in Japan. Stone coffer digging: no new source; it stays 0269's SILENT, the pass's search named only in the reply.

**Group 4, carrying stone (new figures into 0260):**
- Already answered in part, Japan: 0257 (1620 hill stone brought out and sledged at 1.3-1.5 monme a man; a 150 kg block on
  one man's back; carrying stone a ri not found) and 0260 (porter fares per stage for a 5-kan load, about 13 mon a ri at
  Takamiya in 1665). Qing already in 0260: the Hunan porter rate (0.003 tael a li for 80 jin) and the Zhili cart rates.
- New, Qing, stone by cart, ATTESTED: Yunnan 1769, oxcart 0.001 tael per 100 jin per li, craftsman 0.06-0.07 and laborer
  0.04-0.05 a day; Gansu 1769, 600-jin carts at 0.01-0.012 tael per cart per li, craftsman 0.06-0.07, laborer 0.05-0.06.
- New, Qing, porters into mountains, ATTESTED ONLY FOR timber and unnamed loads: Yunnan porters 0.0013-0.0025 tael per 100
  jin per li; Gansu, Qinzhou 0.04 tael a porter-day (the laborer's wage), 50 jin for 60 li; Guide, rugged mountain timber,
  0.009 (old rule) or 0.003 (the register) per 60 jin per li; Gansu sets no separate porter rate for stone.
- SILENT, the search named: an Edo cart hire by the day or the load, and porters into forest with no trail (Morisada's
  Osaka cart fee is a license, not a hire).

## Requirements

- **FR-001**: Every line of the issue's four groups gets, in the reply on #10, its fragment file, its verdict and what is
  still open.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names before landing.
- **FR-003**: The feature closes with `make impl-check F=408` (money questions: no code implements them).
- **FR-004**: The reply is posted on #10; gm-assistant verifies and closes it.
- **FR-005**: Before a line gets its verdict it is checked against 0255-0258, 0260 and 0268-0271; where a page already
  answers it or holds its nearest figure, the reply names that file and the estimate it answers, and nothing new repeats it.

## Success Criteria

- **SC-001** (FR-001, FR-004, FR-005): every line of the issue carries a fragment file, a verdict and what is still open in
  the reply, the already-answered lines naming the earlier page.
- **SC-002** (FR-002, FR-003): `make record-owed` shows no unanswered unit for the touched questions at landing, and `make
  impl-check F=408` reports nothing missing.

## Assumptions

- Japan first, China as comparison (the issue); GM canon overrides both.
- The estimates gm-assistant gives in koku are its own; this feature reports sources, not judgments on them.

## Review history

- **spec-fidelity, MODE 2, round 1 (2026-10-21): CHANGES REQUIRED.** The findings missed lines the record's own pages
  already answer (0255's notice board, 0268's woodcutters, doors and worship hall, 0257's earthwork and hill stone, 0260's
  porter fares); SILENT was to mean no new source; FR-001/SC-001 lacked "what is still open"; the approval line's date;
  spec-lint's eight findings. All applied: FR-005, the "Already answered" lines per group, US1 scenario 4, FR-001/SC-001,
  the GM's 2026-10-21 words, the success criteria tied to their FRs.
- **spec-fidelity-verify, round 2 (2026-10-21): CHANGES REQUIRED.** The five round-1 items RESOLVED; three new: plan D1 and
  its paragraph contradicted the already-answered lines and FR-005 was untraced in D1/T04; s1's brief said "keep Japan
  SILENT" for carrying stone a ri; stone coffer digging was both already answered and SILENT. Each fixed in the
  reviewer's wording. A third round goes to the round arbiter (ask:408-spec-round3).

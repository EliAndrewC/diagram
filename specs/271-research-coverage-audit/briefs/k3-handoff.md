# K3 handoff - cities/government: samurai houses and the garrison (session 1: research and write)

Written 2026-09-27 in clone diagram-research-3, commit 97458704a. Nothing pushed; no record checks run.

## Sections

- SECTION=cities/government/280
- SECTION=cities/government/290
- SECTION=cities/government/300
- SECTION=cities/government/310
- SECTION=cities/government/320
- SECTION=cities/government/330
- SECTION=buildings/180
- SECTION=urban-features/120
- SECTION=cities/sizing/020

## Registry keys

- KEY=touken-bukeyashiki-madori
- KEY=bunka-akasaka-bukeyashikimon
- KEY=kotobank-baba
- KEY=baba-jawiki
- KEY=takadanobaba-jawiki
- KEY=kotobank-yaba
- KEY=toshiya-jawiki
- KEY=kotobank-oimawashi
- KEY=fuzhou-nanjiaochang-zhwiki
- KEY=mancheng-zhwiki
- KEY=xian-mancheng-zhwiki
- KEY=matsushiro-castle-jawiki
- KEY=rehouse-meidaimae-enshogura
- KEY=jta-aoyagi-kakunodate
- KEY=semboku-bukeyashiki
- KEY=semboku-kakunodate-en
- KEY=chiran-kagoshima-kankou
- KEY=fujiclean-ido
- KEY=l7r-toshi-ranbo-barracks (the GM's canon; URL: none)

Two more keys are cited here but OWNED elsewhere: `make reserve` refused them, so their entries were copied
byte for byte from the owning clones (same file name, so the merge is clean) and must not be edited here:
`doshin-jawiki` (14720, diagram-research-6) and `chongming-yanwuchang` (15090, diagram-research-4). Their
owners should add "cities/government" to the "Used for" line. Glossary terms added: `baba`, `jiaochang`.

## Items

- B36 B37 C74 D120 ACCURATE - a samurai's lot was granted by stipend, and Fukui's own table gives the ladder (300 koku 400 tsubo, 150-260 koku 360, 100 koku 225, yoriki 96, lower posts 90/66/55), with 1,000-tsubo plots for 1,000-1,200-koku retainers, Edo's yoriki 300 and constables 100 tsubo, the foot soldiers' 165-230 m², and houses of 67 tsubo (senior) down to 66-91 m² (junior); the setting's ranks map onto it by place in the hierarchy (this project's decision), the middle house size is a labeled guess, and a town's generosity (Kakunodate's roomy lots) is a calibration - the generator should stop pricing every samurai house at one size (citybudget C_SPACED; the drawn 2,322 sq ft house is a 500-1,000-koku retainer's, the top of a provincial city's ladder): senior lots about 8,000-14,200 sq ft with 1,200-2,400 sq ft houses, junior lots about 2,000-3,400 sq ft with 700-1,000 sq ft houses, the manor or a minister's compound about 35,000 sq ft.
- C75 KNOB - every lot was enclosed: senior houses by an earthen wall with a long-house gate (a building about 15 ft deep holding the gatekeeper and servants), junior houses by a board fence or a hedge (a stone wall with a hedge a regional third form), the lowest by brushwood with no formal gate; a front garden, the well and a storehouse by the gate; the kitchen's side of the lot is a labeled guess - the city generator draws every samurai lot enclosed, walls and long-house gates on senior lots, and rolls board fence or hedge per settlement for junior lots.
- C76 ACCURATE - provincial samurai houses had their own wells (Kakunodate's Aoyagi and Iwahashi houses), a well having become affordable once a cheaper boring method cut its cost; the foot soldiers sharing a well is a labeled guess - each samurai lot draws its own well inside the fence near the gate, which is what the samurai ward's exemption from public wells (urban-features 120, now cited) rests on.
- C43 KNOB - the setting has barracks (canon: Toshi Ranbo's district barracks), and the history gives two ways to site them: a walled garrison quarter in a corner of the city laid out as barracks with its own drill ground, stables and armory (Qing), or barracks beside the drill ground at a gate (Fuzhou, Chongming); gates carry guard companies with the commander's house by the gate (Fukui); the armory and powder store stand inside the castle, a capital adding an outside powder magazine on a main road (Edo) - a provincial city draws barracks, rolling the garrison quarter against the barracks-by-the-drill-ground per settlement.
- C44 KNOB - a Chinese seat of county rank and above kept a drill ground, about 5-6 acres (Chongming's 37.5 mu; Fuzhou's 30+ mu), earth-walled with a review hall and platform, either outside a gate or in a corner inside the wall (both at Chongming; Xi'an's garrison inside) - the drill-ground reserve quarter should be about 5-6 acres and its place rolled per settlement; inside the wall it counts against the one-fifth reserve cap (sizing 020, whose absence note on a drill ground inside a walled seat is corrected).
- C142 ACCURATE - castle towns always kept riding grounds, banked and fenced strips about 100 by 10 ken (600 by 60 ft; Ako's 2.5 cho by 5 ken on a moat-side embankment) in the samurai ground by the castle or the lord's residence, with a viewing stand; the samurai archery range was 33 bow-lengths (about 250 ft) by 1 with an earth butt, set in the castle, a residence or the thinly built outskirts - the city generator should draw one riding ground near the castle or governor's compound and roll whether an archery range shows at the town's edge.

## Corrections owed to other owners (for the orchestrator to send)

- **269 B39, cities/government/030**: its rule "NONE of them is walled: a walled samurai estate stands OUTSIDE the rampart, and the only walled samurai compound within the city is the governor's" contradicts 290 - senior retainers' houses inside the town had earthen walls and long-house gates (bukeyashiki-wiki, jta-nagayamon, kotobank-bukeyashiki), and every samurai lot was enclosed by something. 030 should say senior houses are walled and junior ones fenced or hedged, and point at 290; its "rank" size split should point at 280 for the lot and house sizes.
- **G2 (diagram-research-4), cities/capitals/100** (renamed there, so not edited here): its detached samurai house (2,322 sq ft drawn, the Matsue 67 tsubo) is a 500-1,000-koku retainer's house - the top of the ladder - and a pointer to government 280 for the whole ladder belongs beside it. Its Fukui note quotes the page's meters, which the page transposes (28 ken is about 51 m, 32.5 ken about 59 m); the feet in its prose are right.
- **K5 (diagram-research-2), cities/capitals/360**: the OUTSIDE column should add the garrison's barracks (canon, government 310), the drill ground (320) and the riding ground (330); the inside column's castle-guard barracks and armory stand.
- **267, buildings 320/380/390/400/420**: 280 and 290 name those questions in plain text with the links in HTML comments, because the anchors are not in this clone yet; turn the comments into links once 267 lands.

## Left open

- The house of a 100-300-koku retainer (no page read gives one), the kitchen yard's place, and the foot soldiers' shared well stay labeled guesses, each with a dated absence note.
- Fuzhou's two drill-ground figures (four li round, over thirty mu) disagree on the page itself; the 5-6 acre band rests on Chongming's 37.5 mu and Fuzhou's thirty.
- Nothing claimed by another session was skipped: the claims file named no other session on K3's items.

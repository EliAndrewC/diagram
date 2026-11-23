# Brief - feature 449 T358, T360, T361, T362, T369, T370 (0091, 0082, 0093, 0113), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone (including this bundle's own earlier, checked edits in 0101, 0106,
0190 and 0218: keep them, do not touch those pages); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push, and never push the archive by hand (`make reserve`'s own archive step does what it does by design; let
it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any `docs/` file, any `rust/` file
or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run `make claims-*`. Read narrowly: grep with `-o`
and a short context, read by line range; send the lookups you know you need in one message.

**Claims.** The orchestrator claimed 0082 0091 0093 0101 0106 0113 0190 0218 for this clone (feature 449);
`make research-claims Q="0082 0091 0093 0113"` shows them. Nothing to claim.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). A defect is a wrong outcome: restate a record line to what its sources and the sheets say rather
than invent. Where the record is silent, the line says it is this project's GUESS or a map drawing convention, with an
absence note listing what was searched (and when). Look in the archive before the web (`make archive-find`,
`make research-search`); every page read goes on the ledger (`make source-pages`, `make source-outcome`). A source the
record already keys is cited by its key (a new `-N` note for a new passage); a kept, uncited source is moved in with
`make cite-uncited`. This write takes at most ten NEW registry keys (`make reserve` refuses the eleventh: then follow
the rules file's continuation step); most sources below are already keyed.

## Your items

- **B1 (T361) `0091`: the inner court's grounds and enclosure.** A research pass of 2026-11-22 (KEY t348-inner-court)
  asked what lay underfoot in a magistrate's or samurai house's family court and how it was closed off from the rest;
  read its report whole: `.git/l7r-handoffs/T361-pass-inner-court.md`. It is SILENT on the ground's material (no page
  gives beaten earth, gravel, sand, moss or paving for any family court, Japanese or Chinese) and ATTESTED ONLY FOR a
  few enclosures. In 0091's findings page, in the grounds section that opens "Outside, the sunny south of a house's
  grounds was the garden's" (line ~47), add what the pass's readable sources carry, each cited by a note you key from
  the page you read yourself (archive first; the archived copies are named in the report):
  (a) the Kochi domain's Osaka residence (a plan of about 1790-1800): the lord's living rooms faced, beyond the
  veranda, a garden enclosed by a wall (塀), and the West residence divided the middle of its site with a wall - the
  paper is already keyed `kochi-hantei-jstage` (0104's notes; reuse the key, a new `-N` note for this passage); the
  p. 43 passage was read from the page image, so quote only what you can read on it;
  (b) Kanazawa's four kinds of ground at a samurai house (forecourt before the genkan; the kitchen's katte yard; the
  viewing garden before the zashiki; the rear sedo of fruit trees and vegetables) - a blog's summary of Shimamura
  Noboru's book, at second hand: say so;
  (c) Morse's *Japanese Homes* (1886): a Tokyo house "of one of the better classes" whose kitchen back-yard was
  separated from the area before the main entrance by a high fence - not said to be a samurai house: say so, and date
  the observation as the page itself does (Morse's own years in Japan, read from the book, not from memory).
  Do NOT state any ground material. Give the silence an absence note (`no publicly readable source`, the pass's
  searches in a comment, a visible sentence: no page we read says what lay underfoot in a house's family court, in
  Japan or China). Then, in 0091's drawing page's grounds section (line ~36-42), add one bullet if none says it: our
  maps draw the residence court's open ground as bare earth, its earth showing unfilled - a GUESS, the record silent
  (the same absence note). Do not restate the Chinese yamen's residence gate (宅門) if 0090 already carries it; link
  0090 instead.
- **B2 (T361) `0082` drawing page: the cart gate's width.** The page says a compound that ships bulk goods has a cart
  gate (line 9) and gives the cart lane about 6 ft (line 10), but nothing of the cart gate's width, which our plans draw
  in the side gate's 5-8 ft band (449 T341; another builder is moving gates on those sheets now, so state the band in
  visible text and put any per-gate figure, dated, in an HTML comment only: Hayakawa's west service gate and east
  landing gate and Ubame's south service gate and east cart gate 8 ft, measured 2026-11-22 by `make pack-audit`). A research pass of 2026-11-22 (KEY
  t341-cart-gate) found no cart gate's width at a jin'ya, a samurai house, a merchant house or a yamen; read its report
  whole: `.git/l7r-handoffs/T361-pass-cart-gate.md`. Add a bullet after the cart lane's, e.g. "How wide is a cart
  gate?": drawn within our plans' side-gate band of 5 to 8 ft, so the 6 ft lane passes through it - a GUESS; a cart gate
  was a gate of its own name in Japan - the Kochi domain's town residences of about 1789-1801 listed a cart gate
  (車御門) apart from the rear gate (`kochi-hantei-jstage`; its gate table's scan is garbled: quote only what is legible,
  and do NOT say which residence had it, which the pass could not tell), and Himeji castle's Kurumamon was its main
  entrance for carrying supplies in, "kuruma" meaning the carts (https://www.mlit.go.jp/tagengo-db/R2-00200.html, read
  it yourself) - but no page we read gives one's width (an absence note naming the pass's searches). The Meiji temple
  register's side gate (1.5 ken frontage) is a temple's structure frontage, not a cart gate: leave it out or say so.
  Add the cart gate's width to the Evidence comment's guess list.
- **B3 (T361) `0093` drawing page: the gate drum, not drawn.** 0093's findings page (line ~32) records that both county
  yamen we read of kept a grievance drum at the main gate (`netease-pingyao-yamen`: Pingyao's under the gate's porch,
  1368; `neixiang-yamen-baike-weixin`: Neixiang's in the front half of the gate's east end bay). Our plans keep that drum
  at every seat's main gate, under the gate's roof, and do not draw it as a mark of its own; no page attests a petition
  window or a bell, and our plans draw neither. Add one bullet to the drawing page saying so - the drum at every seat
  following the record's two county yamen (China first), not drawing it a map drawing convention - with the two notes
  (copy them to the drawing page's notes file as the record does when a drawing page cites a findings note), and the
  Evidence comment to match. Keep the page's existing bullets as they are.
- **B4 (T358) `0113`: a corridor (roka) to the back rooms and the house.** Our office-hall plans draw no corridor: the
  way from the hall's entrance to its back rooms and to the residence runs through working rooms (building reviews of
  2026-11-22: on Ochiba's plan from the genkan room to the rear door through the day office and the clerks' room; on
  Ubame's, the household's back door opens into the clerks' room on the way to the dais; on the Ochiba round-trip test
  plan, the way to the house passes through the magistrate's study). A research pass of 2026-11-23 (KEY t358-roka)
  asked whether a jin'ya office hall kept a corridor instead; read its report whole first:
  `.git/l7r-handoffs/T358-pass-roka.md`. Its verdict is ATTESTED ONLY FOR the Edo town magistracies, with corridors at
  jin'ya halls but no route. Grade what it found before writing:
  - quotable TEXT: the North Town Magistracy's page (`edo-ashigaru-bugyosho`, http://edo.ashigaru.net/?eid=23, archived)
    gives the household its own ways in - the inner entrance (内玄関) for the household side to the north, a back gate by
    which the magistrate's family, retainers and servants went in and out, and an entrance for the private side (the
    oku) between the office and the residence (the report's three sentences; read them on the archived page);
  - read from PLAN IMAGES, under the blogger's modern red labels: the 1841 North and 1842 South plans' corridors (廊下)
    and inner corridors (入側) from the genkan and the inner entrance past the office room (用部屋) toward the residence
    wing. Write this in the form 0113's drawing page already uses for the 調之間 ("the plans ... show"), citing
    `edo-ashigaru-bugyosho` and `edo-ashigaru-minami-plan` as it does, and say the plans were read from the images;
  - jin'ya halls with corridors and no route: Kaibara's front palace of 1820, its genkan's formal rooms surrounded by
    inner corridors (入側) (https://online.bunka.go.jp/heritages/detail/205913, kept uncited as registry
    `24490-bunka-kaibara-han-jinya-ato`: `make cite-uncited`), Sayama's council hall of 1775 with corridors (`sayama-jinya-uematsu`),
    Takayama's office of 1816, the envoys' room across a corridor from the great hall (`takayama-jinya-viewing-guide`);
    for houses below the great houses, link 0091's corridor bullets (`irikawa-kotobank`) rather than restating them;
  - NOT evidence for the verdict: Takayama's residence passages (the 1996 rebuild), Iijima (the 1993 rebuild), the
    Nagasaki Tateyama reconstruction - leave them out or name them as rebuilds.
  Before the absence note, run ONE more batch of the search with each language's terms in a group of its own (a
  `;`-joined set is ANDed): `make research-search Q="Did a jin'ya office hall keep a corridor to its back rooms and the
  residence?" Q_JA="陣屋 役所 廊下 役宅" TERMS="陣屋 廊下|役所 廊下|入側|役宅 廊下" KEY=t358-roka`, then
  `TERMS="jinya corridor|roka|irikawa" KEY=t358-roka`, and read what bears (the same KEY prints only sources not yet
  shown).
  Then write: on 0113's FINDINGS page, beside the Edo town magistracy bullet (line ~19), what those sources carry (the
  household's own entrances; the plans' corridors; the jin'ya halls' corridors without a route). On 0113's DRAWING
  page, one bullet saying what the plans draw today - no corridor, the way to the back rooms and the house through the
  working rooms - a GUESS for a county office, bounded by the Edo town magistracies, whose plans ran corridors from the
  entrance past the office rooms and gave the household entrances of its own; no premodern plan of a small intendant's
  office we could read shows the way (the Takayama plan of 1851, https://www.city.takayama.lg.jp/s/_res/projects/default_project/_page_/001/000/842/027.pdf,
  unreadable at its published resolution), with an absence note naming the pass's searches, what stayed unread and
  where the search stopped. Add the routes to the drawing page's Grounds comment and the GUESS to its Evidence comment.
  Write nothing about any redraw (the orchestrator files that separately).

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t358b-handoff.md`: `- SECTION=0091 0082 0093 0113`, one line per
   item `B1|...|B4 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`, the new
   note keys and registry keys you added (each page's), the searches you ran, and anything left open and why. Do NOT
   run the record checks - the next session does, fresh. Your last message is one paragraph saying what you wrote.

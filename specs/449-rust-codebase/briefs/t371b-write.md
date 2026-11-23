# Brief - feature 449 T371, T372, T373, T376, T381, T382, T385 (0097, 0096), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything** - this overrides the rules file's "commit as you finish".
Other builders have uncommitted work in this clone: keep it, edit around it; the orchestrating session commits your
files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s own archive step does
what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file, any
`docs/` file, any `rust/` file, the `Makefile` or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message. Do not touch 0104, 0123, 0090, 0009, 0113, 0099, 0103, 0107 or 0059 (the other briefs').

**Claims.** The orchestrator claimed 0096 and 0097 (with the bundle's other questions) for this clone (feature 449);
`make research-claims Q="0097 0096"` shows them. A question you reserve with `make reserve KIND=question` is yours: claim
it with `make research-claim Q="<NNNN>" FEATURE=449`.

**Rules that bind every item.** A citation quotes its passage verbatim from a public page you read (translation marked
as one); an unreadable source is not cited (a source only the GM can fetch goes on `research/to-download.md` with
`make download-add`). Look in the archive before the web (`make archive-find`, `make research-search`); every page read
goes on the ledger (`make source-pages`, `make source-outcome`). A defect is a wrong outcome: restate a record line to
what its sources and the sheets say rather than invent. Where the record is silent, the line says it is this project's
GUESS, with an absence note listing what was searched (and when).

**The two passes these items record** (research-pass, 2026-11-22 and 2026-11-23, for 449 T356; their full reports, with
each source's URL, archived copy where there is one, verbatim passage and translation, are in two files - read them
first, by line):
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t356-junior-lodging.md` - where a magistracy's junior
  staff lodged and how large a dwelling was: Sakai town magistracy's plan of 1728 (Takaya, zokei.repo.nii.ac.jp, p.148,
  Fig.5: the retainers' rowhouses inside the grounds, apart from the yoriki houses and the doshin rowhouse; the doshin's
  dwelling 2 ken across the beams by 3 along the ridge a man); the Sayama domain jin'ya (Uematsu on note.com, archived
  `2d/2deb775751d7`; Komoto 1999, sitereports.nabunken.go.jp: middle and lower retainers along the East Gate street and
  side lanes; the lower ranks' rowhouses 2.5 ken deep, 4 to 6 ken long by rank); Omori (the gate rowhouses 33 m by about
  4 m, occupants unnamed; a mid-ranking official's house outside the office, mlit tagengo-db R2-00289); Sano (Fukushige,
  Ochanomizu shigaku 66, p.34: in 1739 the grounds held two rowhouses and an accounts rowhouse, yet the staff of about 55
  lived in the Four Towns, only the jin'ya-keeper inside). The verdicts: on the grounds ATTESTED ONLY FOR a town magistracy
  and a domain jin'ya (side or rear parts, apart from the gate), SILENT for a shogunate intendancy; men a dwelling SILENT.
- `/diagram/.clones/diagram-backlog/.git/l7r-handoffs/T371-pass-t356-cell-seat.md` - where a cell stood and whether it was
  joined: Naruto (成東陣屋, the Chiba bulletin kiyo_028_p2.pdf at echiba.org: "a gate on the south side, and the jail and
  storehouses on the west side"); the Maruyama office (the same bulletin, from 『丸山町史』: besides the office, a jail and
  rowhouses); neither says the jail was a building of its own; whether a cell stood joined to a guardroom, rowhouse or
  gatehouse is SILENT. Its other readings (no cell beside a main gate; Edo North's 1841 kariro in the court quarter, which
  0096 already cites) are context. Its Uraga lead: a search summary's claim that the Uraga magistracy's 「中島家御役所絵図」
  showed a jail of about half a tsubo beside the main gate, from a page (lovefumiyo.hp-ez.com) that returned 403 -
  unverified.

Every passage you cite you READ yourself from the page or its archived copy (`make archive-find URL=<u>`), never from the
reports; a page the reports read from a PDF image you check against the page image as they did. Each source cited takes
its registry key (`make reserve KIND=registry KEY=<k> TAGS="..."`, at most ten new keys this session; the rules file says
what to do at the eleventh).

**What the county plan draws** (measured 2026-11-23 by the orchestrator from
`pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json`, read-only): a "junior retainers'
quarters" 48 x 24 ft on the outer court's south wall (`w 48, h 24, wall S, order 4, bays [12, 24, 36]`: four dwellings of
12 x 24 ft, at most three men a dwelling), between the stables and the gatehouse, 57 ft west of the main gate's west post;
a cell 10 x 12 ft joined to that rowhouse's east end (`joins: "junior retainers' quarters", end E`).

## Your items

- **B1 (T372) `0097`: the junior staff's lodging, findings and drawing.** `research/questions/0097-staff-rowhouses-and-barracks-nagaya.html`
  is 19,541 bytes of prose against the 20,000-byte cap (`make question-sizes`), so the new findings do not fit on it: split
  it along a topic first - e.g. the bullets on WHERE an office's staff lodged (on the grounds, in a district of their own,
  outside the office; its lines 12-17 and the findings below) into a question of its own (`make reserve KIND=question`,
  its heading a question title like the record's others, its tags marker filled from `research/tags.json`), the joins
  pointing, not restating, a finding staying with its decision - and put on it, cited: Sakai 1728 (the rowhouses inside
  the grounds, three places, rowhouse A an east-west row beside the main house, as the report gives it; the doshin
  rowhouse's dwelling 2 by 3 ken a man), Sayama (the lower ranks' rowhouses 2.5 ken deep, 4-6 ken long by rank; the middle
  and lower retainers along the East Gate street and side lanes), Omori's mid-ranking official's house outside the office,
  and Sano's 1739 staff living in the town though the grounds held rowhouses. Restate line 12's "An intendant's office or a
  small lord's jin'ya kept its staff's quarters on its grounds" to what the sources now say (Sano is a counterexample for a
  domain's detached jin'ya). Then 0097's drawing page: its bullet "Where does a county magistrate's office on our maps lodge
  its staff?" (line 9) and, where it fits, the dwelling-size bullets say what the county plan draws (above): the junior
  retainers' quarters on the south wall, its seat a GUESS (on the grounds attested at Sakai and Sayama in side or rear parts
  apart from the gate; SILENT for an intendancy; the outer court's front wall the one free run), its dwelling 12 x 24 ft
  (Obata's 2-ken frontage at the page's depth cap, a GUESS against Sakai's doshin dwelling of 2 by 3 ken a man), at most
  three men a dwelling a GUESS, with an absence note naming the passes' searches (KEY t356-nagaya-place-size and the
  2026-11-22 pass, 2026-11-23). Keep both pages under the cap.
- **B2 (T372) `0096`: the cell's seat and join.** Put on 0096 (its findings, near "A magistracy that judged cases kept a
  temporary cell inside its compound" and "An intendant's compound generally held a jail of its own"), cited: Naruto's jail
  on the west side with its gate on the south; the Maruyama office's jail and rowhouses besides the office; and that no
  page read says whether a cell stood joined to a guardroom, a rowhouse or the gatehouse, or alone - an absence note naming
  the searches (the 2026-11-23 pass). The Uraga lead: try the page once (`make source-pages`); if it cannot be read, it is
  not cited - a session note (HTML comment) names it as an unverified lead, and if only the GM could fetch it, add it with
  `make download-add`. Then 0096's drawing page: its bullet "A cell may stand on any side of the compound" (line 10) or a
  new bullet says the county plan's cell is joined to the junior rowhouse's east end on the south wall, below the hearing
  court - the join a GUESS on the record's silence (that absence note), the seat in the court's quarter bounded by Edo
  North's 1841 kariro as the page already cites it.

## The procedure (session 1: write)

1. **Write.** Read the two reports and the line ranges you need, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (neither 0097 nor its new part listed).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t371b-handoff.md`: `- SECTION=0097 0096 <the new question's NNNN>`,
   one line per item `B1|B2 <DONE|NARROWED|LEFT> - <what the page now says>`, the new question's file and heading id, the
   anchors a claim should cite for (a) the junior quarters' seat and dwelling and (b) the cell's join (the fragment file and
   the note or absence-note id), every file you changed under `## Files`, the registry keys you reserved, the searches you
   ran, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.

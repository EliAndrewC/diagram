# Brief - feature 449 bundle T289 (armories, the main gate, the record's leftovers), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec, plan or tasks to
orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in every command; `git -C` for
every git call). The research record's own `CLAUDE.md` loads when you touch `research/`; `scripts/container/page-session-rules.md`
is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the orchestrating
session commits your files by name. Touch only the files your items need, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up;
do not run `make claims-*`. Read narrowly: grep with `-o` and a short context, `make notes Q=<n> KEYS=<k,k>`, read by line range;
send the lookups you know you need in one message.

First: `make research-claim Q="0093 0097 0123 0116" FEATURE=449` (release with `STATUS=done` at the end).

## What three research passes found (2026-11-22; fetched copies under /tmp/l7r-pass/)

- **Jiexiu county yamen** (介休縣署), the same 古今圖書集成 職方典 338 page the registry already holds as
  `gujin-tushu-jicheng-juan338-zhwikisource` (archive 5a/5a06a30df294; punctuation the Wikisource editors'):
  「大堂舊制三間，萬曆十九年，知縣王一魁增為五間，中三間蒞政，匾曰：「牧愛堂。」 東西二間為庫藏，貯火藥兵器等物。」 ("The great hall was
  formerly three bays. In Wanli 19 (1591) the magistrate Wang Yikui enlarged it to five: the middle three for holding court ...; the east
  and west bays were storerooms, holding gunpowder, weapons and the like", translated). After the Kangxi 16 (1677) rebuild:
  「東西角門，門內西為把門、皂隸、禁卒房。東為武庫，為獄箭道，在協亭西。」 ("East and west side gates; inside the gates, on the west, the
  rooms of the gate-keepers, runners and jailers. On the east the armory, and the jail and arrow lane, west of the Xie pavilion",
  translated) and 「正南臨街豎古「定陽坊」，坊內左營房、輕犯鋪三。」 ("... inside the arch, on the left, the barracks (營房) and three
  lock-ups for minor offenders", translated). Limits: whether the 1591 seat had a barracks is not said; who the 營房 housed is not said;
  where exactly the 武庫 stood (inside the side gates, or west of the Xie pavilion) is ambiguous. No source found puts a seat's arms in
  its barracks, and none states any armory's doors (Pingyao's bay, Jiexiu's, Kaibara's gun store: SILENT).
- **The Neixiang county yamen's great hall**, measured: 「面阔27.22米，进深12.37米」 (China Daily, cn edition,
  https://cn.chinadaily.com.cn/a/202103/12/WS604b0287a3101e7ce9743b4c.html; five bays per zh.wikipedia 内乡县衙 「均面阔五间」) - about
  89 x 40.6 ft, a mean bay about 17.9 x 40.6 ft. Secondary, modern figures of a surviving (restored) hall.
- **The main gate's build.** kotobank 長屋門 (archive 39/39f1760bb1ee; Nihon Kokugo Daijiten): 「長屋を設け、その一部をあけて門としたもの。
  屋根は長屋と一つづきとなる。」 ("a rowhouse built, part of it opened as the gate. The roof is continuous with the rowhouse's",
  translated). Tamba City's Kaibara page (archive 26/262777be7b79, already `kaibara-jinya-tamba` / `tamba-kashiwara-jinya` - check which):
  「間口十三間一尺二寸、奥行二間の単層長屋門形式で屋根は入母屋造桟瓦葺平入。」 ("frontage 13 ken 1 shaku 2 sun, depth 2 ken, a single-story
  nagaya-mon; roof hip-and-gable, pantile, entered on the long side", translated). Bunka Isan Online, the Mikazuki domain's Noino jin'ya
  front gate (https://online.bunka.go.jp/heritages/detail/434033, copy /tmp/l7r-pass/t296-mikazuki; NOT yet in the registry or the
  archive): 「江戸／1774木造薬医門形式、切妻造本瓦葺、両脇に袖塀付幅約6.8ｍ、奥行約2.1ｍ」 ("Edo, 1774; a timber yakuimon, gabled,
  full-tile roof, with a short wall on each side; width about 6.8 m, depth about 2.1 m", translated) and 「表門は、三日月藩の大手門にあたり」
  ("the front gate served as the domain's main gate", translated). **Gatekeepers: no count** at any jin'ya (ashigaru guarded jin'ya,
  bushijyoshi archive b4/b4e3a8f28a5e, no number). **A conflict**: 0093 says a yamen gate was "by law three bays wide"; Douban's
  清代衙门图说 (archive 85/858f78f5102f) quotes the Hongwu 26 (1393) rule kept by the Qing for 6th-9th rank officials 「门一间」 ("gate of
  one bay", translated), and the 古今圖書集成 gives Xi'e county 「大門三間」 (1686) and minor offices 「大門一間」 (archive 64/6441eea90cde).

## Your items (four questions)

- B1 `0093`, three parts:
  - **T295.1 - 0093's drawing page** (`research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html`): record the
  armory's gate-range seat - where the main gate is drawn as a gate range, the store of arms may be one of the range's rooms beside the
  passage (Kaibara's), a knob rolled from the map's seed between that room and the office hall's end bay (the program's armory-site
  knob; Ubame's plan rolled the gate range: its range's west room, about 13 x 12 ft). One short block, labeled as the page labels its
  choices.
  - **T295.2 - 0093's drawing notes**: the kitain-bansho drawing note quotes 「山門右側に接し」, which is not on its page: re-quote from the
  page (or re-point to the page that holds it), or drop it if no reachable page holds it.
  - **T296 - 0093's findings page**: add, briefly, what the main gate was built of - a gate range's roof ran on unbroken from the range's
  (kotobank), Kaibara's one hip-and-gable pantile roof; a jin'ya's one-bay gate could be a yakuimon with a short wall each side
  (Mikazuki; a NEW registry key, archive it first) - and that no page gives how many gatekeepers kept a jin'ya's gate. Restate the
  yamen gate's "by law three bays" to what the sources support (the conflict above).
- **T295.3 - 0097's findings page** (`research/questions/0097-staff-rowhouses-and-barracks-nagaya.html`; it is about 19,250 bytes of a
  20,000 cap: trim first if an edit grows it): "junior officials lived in rowhouses which served as their barracks" rests on
  `kaibara-jinya-tamba`, which supports only "long, narrow, single-story": re-source it or restate it to what the source says.
- **T295.4 and T289 - 0123** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html`
  and its `.drawing.html`): on the findings page, add Jiexiu (the 1591 end bays holding gunpowder and weapons; the separate 武庫 after 1677;
  the barracks at its street front) with the limits above, footnoted to the existing key, original then a marked translation; and that no
  source puts a seat's arms in its barracks or states an armory's doors. Add the Neixiang hall's measured depth (a NEW key) as the one
  county great hall measured, a measured analog for how deep an end bay could run. On the drawing page, the granary's seat: it gives the
  granary "a flank column's inner end" - restate it to cover both drawn seats (the county example's granary at the head of the office
  court's east column; Ochiba's round-trip plan's granary below its barracks, which heads that column).
- **T295.5 - 0116** (`research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.html` and `.drawing.html`):
  `japan-heritage-takayama-onkura` is NOT-READABLE on both pages - replace it with a readable source for the same statement or drop the
  statement's dependence on it; `fuchu-joge-jinya` fn-8's two NOT-CHECKED quotations - verify against the archived page or remove; the
  `takayama-jinya-gifu` SESSION NOTE - resolve it.

Keep each addition to a sentence or two; a findings page states the finding, the footnote holds the source.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="armory|armoury|gate|gatekeeper|Jiexiu|Neixiang"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>`. Register each new source with its write-ups
   (`make reserve` for keys).
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and labels by the record's rules; no history in
   the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`, `make glossary`, `make question-sizes`.
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t289-handoff.md`: `- SECTION=0093`, `- SECTION=0097`, `- SECTION=0123`,
   `- SECTION=0116`, one line per item `<item> <DONE|NARROWED|LEFT> - <what the record now says>`, the new keys and notes, every file
   you changed under `## Files`, and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last
   message is one paragraph saying what you wrote.

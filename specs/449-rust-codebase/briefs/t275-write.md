# Brief - feature 449 bundle T275 (Kaibara's store of arms, Pingyao's armory), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, pool/, l7r/); the orchestrating session commits your files by name. Touch only
the files your items need, and list every file you changed in the handoff. Never run `scripts/sync-with-main.sh`,
never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file or any pop-up - the
orchestrator does the claims. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short context,
`make notes Q=<n> KEYS=<k,k>`, read by line range; send the lookups you know you need in one message.

First: `make research-claim Q="0093 0097 0123" FEATURE=449` (release with `STATUS=done` at the end).

## What a research pass found (2026-11-22; its pages fetched under /tmp/l7r-pass/t275-*)

- **Kaibara's rowhouse gate, the room order.** Tamba City's page on the gate (updated 2024-03-19),
  https://www.city.tamba.lg.jp/soshiki/shakaikyoikubunkazaika/gyomuannai/7/1/2558.html (not yet in the registry or the
  archive): 「向って左が番所、右が馬見所、続いて砲庫となっている。」 ("To the left as you face it is the guardroom; to the
  right the horse-viewing room, and following on from it the gun store", translated). Tamba City's page on the jin'ya
  site (already the source behind `kaibara-jinya-tamba` / `tamba-kashiwara-jinya`; archive 26/262777be7b79):
  「門戸を挟んで北側に番所・土間、南側に馬見所・砲庫があります」 and 「馬見所は板敷になっているが砲庫との境に段差があって、
  当初は番所と同様に畳敷であったと推測されます」 ("across the gate, a guardroom and earth floor to the north, a
  horse-viewing room and gun store to the south"; "the horse-viewing room is board-floored, but there is a step at its
  boundary with the gun store, so it is thought to have been tatami-floored at first, like the guardroom", translated).
- **The silence.** No source says how many of the three eight-mat rooms south of the gate the gun store took (one or
  two): the designation text (三室 / 八畳三間), the 1992 prefectural signboard (kojodan, archive c5/c510c2b0309a:
  「門扉を挟んで右側が板張りの馬見所と砲庫の三室に仕切られている」, its 三室 readable either way), the city pages and
  Japanese Wikipedia all name the rooms without their share.
- **A mislabel.** The text "13.5 ken long, 2 ken deep. To the south, three 8-mat rooms; ..." (桁行十三間半、梁間二間、南に
  八畳三間...) sits on the city's site page under the NATIONAL historic-site (史跡) section, not a prefectural one;
  0097's findings page calls it "The prefectural designation". Check the archived page (26/262777be7b79) and correct
  the attribution if it holds.
- **Pingyao's armory, its depth.** No source gives the depth of the great hall or of its armory. The one premodern
  text, the imperial encyclopedia 古今圖書集成, 職方典 vol. 338 (zh.wikisource; archive 5a/5a06a30df294), says only
  「大堂東為錢糧庫，西為武備庫，堂東贊政亭，西鑾駕庫」 ("east of the great hall [or: the hall's east part] the
  money-and-grain store, west the armory; east of the hall the Zanzheng pavilion, west the imperial-regalia store",
  translated) - the same east/west form names separate side buildings, so it does not put the stores inside the hall.
  The "east end bay / west end bay" (東梢間 / 西梢間) wording of `pingyao-yamen` (Baidu Baike) is a modern retelling; the
  "inside the hall" description is of the 1996 restoration.

## Your items

- **T275.1 - 0093's findings page** (`research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html`,
  line 17, the bullet "Some gatekeepers sat in a guardroom built into the gate range."). Add the order - the
  horse-viewing room next to the gate and the gun store beyond it at the south end - and that no source says whether
  the gun store took one of the three eight-mat rooms or two. Footnote the order to the Tamba City gate page (a NEW
  registry key; archive it first, `make archive-inbox` / the archive's add path the record rules give), quoting
  verbatim with the translation marked.
- **T275.2 - 0097's findings page** (`research/questions/0097-staff-rowhouses-and-barracks-nagaya.html`, line 23, "The
  Kaibara rowhouse gate was divided into rooms on either side of its gateway."). Correct "The prefectural designation"
  if the archived page puts that text under the national historic-site section; add the same one-clause silence (which
  of the three rooms, and how many, the gun store took is not recorded).
- **T275.3 - 0123's findings page** (`research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html`,
  line 20, "Pingyao kept its money, grain tax and arms inside the great hall, and its granary behind the offices.").
  Add, briefly: the oldest account (the 1720s imperial encyclopedia) says only that the money-and-grain store stood
  east and the armory west "of the great hall", a phrase that reads either way, the end-bay wording being a modern
  account's; and that no source gives how deep the armory ran. Footnote to a NEW registry key for the 古今圖書集成
  passage (archive 5a/5a06a30df294), original then a marked English translation. Consider whether the bullet's
  heading "inside the great hall" overstates: if it does, soften it to what the sources support.

At most four questions; these are three. Keep each addition to a sentence or two; a findings page states the finding,
the footnote holds the source.

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="armory|armoury|gun|Kaibara|Pingyao"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>`. Two sources are new (the Tamba
   City gate page and the 古今圖書集成 page); register each with its write-ups (`make reserve` for keys).
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and labels by the record's
   rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`.
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t275-handoff.md`: `- SECTION=0093`, `- SECTION=0097`,
   `- SECTION=0123`, one line per item `T275.<n> <DONE|NARROWED|LEFT> - <what the record now says>`, the new keys and
   notes, every file you changed under `## Files`, and anything left open and why. Do NOT run the record checks - the
   next session does, fresh. Your last message is one paragraph saying what you wrote.

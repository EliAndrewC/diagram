# Brief - feature 449 T330 and T333.5 (0101, 0104, 0113, 0123, registry 14040), session 1: write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone; the
orchestrating session commits your files by name. Touch only the files your items need, and list every file you changed
in the handoff. Never run `scripts/sync-with-main.sh`, never push, and never push the archive by hand (`make reserve`'s
own archive step does what it does by design; let it). Do not edit any `Research:` claim, `dev/claims-index.json`, any
`pool/` file, any `docs/` file, any `rust/` file or any pop-up (`l7r/diagram/interactive/assets/modals/`). Do not run
`make claims-*`. Read narrowly: grep with `-o` and a short context, read by line range; send the lookups you know you
need in one message.

The orchestrator already claimed 0101, 0104, 0113 and 0123 for this clone; keep the claims for the check session.

## The research passes you write from

Four research passes of 2026-11-22 (the T312 bundle). Their full reports, with every passage verbatim, its URL, its
archive id and the pass's reading, are:

- `.git/l7r-handoffs/T330-pass-nightsoil-fujomon.md` - for A1 (0101)
- `.git/l7r-handoffs/T330-pass-county-genkan.md` - for A2 (0104)
- `.git/l7r-handoffs/T330-pass-small-office-rooms.md` - for A3 (0113)
- `.git/l7r-handoffs/T330-pass-armory-frontage.md` - section "T312 Q1 (Q-A)" only, for A4 (0123)

Read the section you need by line (`grep -n '^## \|^\*\*' <file>`, then a range). A report is a lead, not a citation:
every passage you cite you check against the page itself (`make archive-find URL=<u>` names the archived copy; a page
not archived is fetched through `make source-pages URL=<u> QUESTION=<NNNN>`), quote it verbatim from that copy, and
record its outcome (`make source-outcome URL=<u> OUTCOME=cited:<key>`). Most of the sources already have registry keys:
`make archive-find URL=<u>` or a grep of `research/sources/` names them (kasama-iwama-jinya, fuchu-joge-jinya and
fuchu-joge-pamphlet, sayama-jinya-uematsu, wheatbaku-machibugyosho-yashiki, kazusa-bugyosho, edo-ashigaru-*,
takayama-jinya-en-tour, takayama-jinya-gifu, iijima-jinya-*, pingyao-yamen, netease-pingyao-yamen,
gujin-tushu-jicheng-juan338-zhwikisource, gujin-tushu-nanyang-wikisource). Reserve a new key only for a page with none.

**The caveats every passage carries - write them where the passage is used, or the page will overstate:**
- Kotobank's 不浄門 entries are modern dictionary definitions of an Edo-period thing: they name no residence, give no
  size, and Nikkoku's earliest quoted use is a kabuki play of 1875. The URL in the report is mis-encoded; the page is
  `https://kotobank.jp/word/%E4%B8%8D%E6%B5%84%E9%96%80-618268` (a saved fetch is at
  `/tmp/l7r-pass/kotobank-fujomon/01-kotobank.jp.txt`; it is not archived, so fetch it through `make source-pages`).
- Joge (1869 plan, redrawn in a modern pamphlet): the room labels were read from the drawing, not from text. Only the
  pamphlet's sentence and its key 「＊数字は畳数」 are text. See how the existing notes of `fuchu-joge-jinya` /
  `fuchu-joge-pamphlet` cite it, and say "the drawing shows" rather than quoting a label as a passage.
- Sayama (1775 council hall): the rooms are a list, not a plan order, and its shikidai is itself a 6-mat room with a
  closet; it is a domain's council hall, not an intendant's office.
- Iijima (rebuilt 1993) and Suibara (rebuilt 1995) are modern reconstructions: report them as such; they count toward
  no verdict.
- Neixiang's 「門左為軍器房」: that 左 means east is the pass's reading, not the source's words.
- The Takayama official guide reads 書役 as shoyaku; 0113 and its sources say kakiyaku. Record what each source says
  (each reading beside its source), never pick one.

## Your items

- **A1 `0101` (T330: the fujomon rear wicket).** 0101 now says only a merchant house's back gate served the collectors
  and nothing of a samurai house's gate. Add the fujomon (不浄門, also imimon 忌門) from Kotobank: a gate or wicket set
  at the rear of a samurai residence, castle or the like for carrying out night soil, the dead and criminals (Daijisen,
  Nikkoku, Nipponica), with its caveat. Only this finding from that pass; the rest of its report (Morisada's hatch,
  Shirobito, the others) is not this task's. Then restate 0101's drawing page where it speaks of a samurai compound's
  way for the night-soil collector, if it does, against this: the round trip sheet draws a 6 ft side gate in the north
  wall as a rear wicket, a GUESS; the record now attests a rear wicket for night soil at a samurai residence in
  general terms, and nothing of its size or of its place along the rear wall. Label it so.
- **A2 `0104` (T330: the genkan on the gate's line, and the genkan room).** From the county-genkan pass, Q2 and Q4:
  (a) at Iwama (1827), Joge (1869) and both Edo town magistracies, the genkan and its shikidai stood straight ahead of
  the main gate, the hearing court (shirasu) to one side (left at both Edo offices, south at Joge); in China the gate's
  line led to the hearing hall itself. (b) A room stood between the step and the working rooms at Joge and at Takayama
  (the genkan room rebuilt in 1816; the step kept for the shogunate's envoys); Sayama's council hall lists a genkan of
  8 mats, a shikidai of 6 and a next room of 8 (its caveat). Check what 0104 already says (it cites Iwama, Sayama and
  Joge already) and add only what it lacks. (c) The pop-up's questions the record must answer first, or say are
  unrecorded with what was searched: what the genkan room was for (guests waiting or received - Takayama's guide on the
  envoy room and guest room, the Kochi residence's envoys' room south of the front entrance), and what a genkan was
  built of (search the record's own sources and the archive first; if none says, an absence note saying what was
  searched). (d) 0104's drawing page: record that the plan draws the genkan room behind the step, at the office hall's
  end between the porch and the working rooms (county example: a room 12 x 38 ft, full depth, at the hall's east end),
  a GUESS for its place and size; record what the porch's dark block stands for (read the genkan's drawn parts in
  `rust/mode_a/src/compound/gen_tests_seat.rs`, test of "the genkan's parts drawn", and the genkan code it calls, read
  only); if no page says what the block depicts, say so on the drawing page and label it a map drawing convention.
  Do not edit `pool/` or the pop-up: the county notes' and the pop-up's genkan-room size (26 mats from Sayama's three)
  are reconciled afterwards by another builder from what the page then says; give the page the pass's figures exactly.
- **A3 `0113` (T330: a small office's writing and binding rooms).** From the small-office-rooms pass: no premodern
  source gives a small office a writing or a binding room; a writing room (書役部屋) at a small office appears only in
  Iijima's 1993 rebuild (the first room inside the entrance, next to the court room; the museum blog and a visitor
  blog disagree on who used it, apprentices on night duty or hired local writers); the binding room appears only at
  Takayama, whose official guide says the chotojiba drew up and bound official documents and ledgers, kept in the
  adjoining ledger storehouse (new to 0113), and gives no size. The pop-up's questions: who worked in the writing
  rooms (Takayama's guide: officials called shoyaku; 0113's tedai-jawiki: kakiyaku hired from village officials'
  children) and how many (unrecorded, unless a source says - with what was searched). The drawing page: record that
  the plans draw the writing room and the binding room in the office hall's back row, west to east the armory, the
  writing room, the binding room, the clerks' room, the day office and the official study, so the clerks' room adjoins
  the day office as the drawing page places it at Takayama; the two new rooms' place, and the official study's place at
  the back row's east end, east of the day office, each a GUESS on the record's silence.
  - **A5 (0113's citation) registry `14040` kaibara-jinya-tamba (T333).** Its `Used for` names only the rowhouse gate though 0113 now
    cites it (note `kaibara-jinya-tamba-2`, the hall's form and its rooms). Add that use.
- **A4 `0123` (T330: the armory's side varies).** From the armory pass, Q-A only: 0123 already cites Pingyao (west
  end bay) and Jiexiu (both end bays, 1591; an armory by the east side gate after 1677). Add what it lacks from
  Gujin tushu jicheng juan 338 and juan 451 (Nanyang: Neixiang 1666, weapons room at the ceremonial gate's left;
  Wuyang c.1652, the armory right of the hall with the money store; Zhenping, both end bays stores; Dengzhou, regalia
  store on the west) and Fenzhou (silver on the west), and the reading: across county yamen the armory's side varied;
  no page ties it to the war office's side or to 左文右武, which the modern pages apply to the six offices.


Carry the four new findings' labels onto the pages exactly; where a finding bounds a drawn choice (the rear wicket,
the genkan room, the writing and binding rooms), the drawing page's GUESS or DEVIATION label says what the record now
attests and what it leaves open.

## The procedure (session 1: write)

1. **Write.** `Read` the line ranges you need in ONE message, then `Edit`. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes`. At most ten new registry keys (`make reserve` refuses the eleventh; then
   follow the continuation rule).
2. **Hand off.** Write `specs/449-rust-codebase/briefs/t330a-handoff.md`: `- SECTION=0101 0104 0113 0123`, one line
   per item `A1|A2|A3|A4|A5 <DONE|NARROWED|LEFT> - <what the page now says>`, every file you changed under `## Files`,
   and anything left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is
   one paragraph saying what you wrote.

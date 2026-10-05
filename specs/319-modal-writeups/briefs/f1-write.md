# Brief - feature 319 (modal write-ups), F1: the farmhouse's walls and how it closed. Session 1: write

You are a FRESH session for one part of feature 319. This brief is the whole of what you need; do not read the feature's spec or
plan. Work in this clone (`/diagram/.clones/diagram-html`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all.

**Why.** The farmhouse's map modal is being rewritten to answer what a reader asks of a building - among them what its walls were
made of and whether its doorways closed. The record says neither (a reader pass, 2026-10-03: no page describes a farmhouse's wall;
0117 has the big sliding door and its wicket but not whether or how it was shut; 0102 has the amado's late-sixteenth-century
origin but not that farmhouses had them).

**What a research pass found** (a sonnet agent, 2026-10-03; read each page yourself before you cite it - `make archive-find`
first, then `make source-pages`, then the `source-reader` agent from a bundle on every passage you will quote; the translations
below are the pass's and must be your own, marked as translations):

- 日本大百科全書(ニッポニカ) 「民家」 on kotobank, https://kotobank.jp/word/民家-146600 - 「外壁の種別では柱を外に見せた真壁（しんかべ）式と，壁の中に柱を塗り籠めた大壁式に大別される。真壁式は東日本，大壁式は西日本の民家に多い。特殊な外壁として茅壁，土蔵造がある。」 Outer walls: posts left showing (shinkabe), commoner in the east; posts plastered in (ōkabe), commoner in the west; thatch walls and the storehouse style as special cases. Undated, all minka. The record may already cite this entry under a `kotobank-minka*` key - reuse the key if so.
- Miyoshi town (Saitama) museum series くらしの民具, 1998, on the relocated former Ikegami house, a farmhouse (the page dates it; confirm), http://www.jade.dti.ne.jp/~miyoshir/mingu/mingu98.html (http-only: `curl -sL http://...` if a fetch refuses) - 「大戸口は三つの中で一番大きく、昼間は開けていますが、夜間や雨風の日などは閉めてあります。そんなときは、大戸口についているくぐリ戸から出入りしました。…戸締まりは、戸の左右の柱につけられた貫本（かんぬき）の穴に心張棒（しんばりぼう）と呼ばれる　棒を通して締めていました。」 The big door open by day, shut at night and in wind and rain, the household then using its wicket, barred with a pole. And 「昼は雨戸を戸袋に繰り込むことによってほとんど開放し、夜はすべて閉じ込むことができます。また、縁側の座敷側は障子で仕切られ」 - the veranda's storm shutters stowed by day and closed at night, paper screens on the room side. One well-off house; museum text.
- Morse, *Japanese Homes and Their Surroundings* (1886), archived at `/diagram/.specify/source-archive/a1/a1598f801a5c/20261003T033126Z/text.txt` (Gutenberg 52868; the record may already have a key): "In the southern provinces a rough house-wall is made of wide slabs of bark, placed vertically, and held in place by thin strips of bamboo nailed cross-wise. This style is common among the poorer houses in Japan"; and "The amado, or rain-doors, by which the verandah is closed at night and during stormy weather ... Not only the verandah but the entrance to the house, as well as the windows when they occur, are closed at night by amado." Meiji-era, mostly town and samurai houses: state the limit.
- Weak, do not cite unless nothing better: a plastering firm's blog (liq-takayasu.com/blog/39) on Edo board walls on windy coasts.

## Your items (two questions at most; at most four new registry keys)

- 0029 (`research/questions/0029-farmhouses-minka.html`): a short group on what a farmhouse's walls were made of - the
  east-west split of shinkabe and ōkabe, the bark walls Morse saw on poorer houses in the south - with the limits, and an absence
  note for what was searched and not found (how common each wall was; the panels' fill on an ordinary house). The page is at the
  20,000-byte cap (`python3 scripts/check-question-size.py`): if the group will not fit, make room by tightening this page's own
  wording without dropping a finding, or put the walls in a NEW question "Farmhouse walls" (tags `subject=homesteads,buildings;
  setting=countryside; level=detail`, placed by `research/contents.json`'s rule) and link it from 0029's look group.
- 0117 (`research/questions/0117-doorways-and-doors-to.html`): that the big door stood open by day and was shut and barred at
  night and in wind and rain, the household using the wicket then (Ikegami house); that a farmhouse's veranda could be closed by
  storm shutters at night with paper screens on the room side (the same house; Morse as the general Meiji form, with its limit).

Do NOT edit any drawing page or any modal class - a later step writes the modal.

## The procedure (session 1: write)

1. Claims: `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="0029"` and `KEY="0117"`, then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram HTML (diagram-html) | 319 | F1 in progress (0029 walls, 0117 closing) | 2026-10-03"`.
2. Read the fragments and their notes; `make archive-find` for each source first, then `make source-pages`, then the source-reader
   agent from a bundle on every passage you will quote. Reserve any new key with `make reserve KIND=registry KEY=<key>`, and write
   its two write-ups and tags as the record's CLAUDE.md requires.
3. Edit the fragments (never a built page). In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`; `python3 scripts/check-question-size.py` from the clone root.
4. Write `specs/319-modal-writeups/briefs/f1-handoff.md` (one `- SECTION=<NNNN>/<id>` line per question touched and a sentence
   each), commit only your files (message beginning `319 F1:`), do not push. Your last message is one paragraph.

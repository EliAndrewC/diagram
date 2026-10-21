# Brief - feature 408, the shrine builder's small lines. Session 1: write (0257, 0260)

You are a FRESH session for the record edits of one part of one feature. This brief is the whole of what you need; do not
read the feature's spec or plan. Work in this clone (`/diagram/.clones/money`). The project's CLAUDE.md files apply to you,
the research record's `CLAUDE.md` above all, along with `research/money-requests.md`.

**What is asked.** gm-assistant's shrine builder prices about fifty small lines by its own estimate (issue
EliAndrewC/diagram#10, verbatim in `specs/408-shrine-small-lines/request.md`; the lines marked (S) come first). Four search
passes have run: `specs/408-shrine-small-lines/passes/` (leads, not citations: read each passage on its page before citing
it; where it does not read as the pass says, write what the page does say, or SILENT). Write the found figures into your
questions; where a line stays SILENT, name in the question's absence note the search that found nothing. Each new figure
sits beside the craftsman's AND the unskilled laborer's day wage of the same place and period; where no source gives one,
say that wage is SILENT and name the nearest already in the record (0250, 0255, 0257, 0275 hold them), with its class,
place, unit and gap in years. Where a source prices several items together, give the combined figure and say what it
covers. Label every figure the project computes as the project's arithmetic. No price is converted to koku; between coins
only by a rate the source gives or 0277's, labeled. Research only: edit no code, modal, sheet or canon. Change only the
sections the new figures or searches touch, and keep each question under the 20,000-byte cap (a question that would pass
it splits its new material into a new money question, tagged as its parent is).

**Already answered.** Lines a page already answers, or holds the nearest figure for, are NOT rewritten and get no new
absence note; your handoff names the file and what it holds (gm-assistant on #10: "just name the file and say which
estimate it answers"). SILENT means no NEW source was found, and an absence note goes only where the record is silent on
the line. The already-answered lines are listed under your items.

**Reading what the reader cannot.** A PDF `make source-pages` cannot read: download it with curl into its own empty
directory and read it with pdftotext, or render its pages (pdftoppm) and pass the images to source-reader with `IMAGES=`.
Morisada 上 (NDL pid 991466): `specs/402-money-open-leads/measure/shot.py` takes a viewer screenshot per koma (run with
`/usr/bin/python3`). A Bochum chapter .xls: read the cells with xlrd and give source-reader a text dump of the rows cited
(a cell of a public spreadsheet counts as a readable page, the GM, feature 407).

## Your items

- **0257 "What did a torii, stonework and earthwork cost?"** - issue group 1 (`passes/g1-grounds.md`):
  - (S) swept earth path: Murata 1986, Table 2 (Kawachi, Ota village, 1704): sweeping crews for officials' visits, 7 to 40
    laborer-days at 1.5 monme a man-day; the estimates' 1.5 monme day wage and the 200-mon-with-meals harvest hand (p. 36).
    ATTESTED ONLY FOR sweeping for a visit, not building a path. The paper gives no craftsman's wage: name the nearest.
  - Clearing and leveling (the great tree, the rock seat): the same paper p. 30, 5.98 monme of laborers' wages a tsubo of
    earth (5 for the Honda section); the tsubo there is earth dug or embanked. ATTESTED ONLY FOR river works.
  - Already answered in 0257, not repeated (the new figures sit beside them): the Osaka 1620s earthwork (clearing,
    leveling); the 1620 hill stone at 1.3-1.5 monme a man and the 150 kg block on one man's back (standing stone); the
    burial mound (SILENT).
  - Sakaki hedge: Japan SILENT. Sakaki hedge and standing stone, Qing comparison: 揚州畫舫錄 卷十七 (1795): one strong laborer per 4 zhang of palisade
    or bamboo hedge; two per zhang lifting stone into place for a stone bridge. No wage in the book: name the nearest Qing
    wage in the record.
  - (S) himorogi, (S) moss court, (S) dipping place at a stream, the white-gravel court and path, the ring of river
    stones: SILENT, the pass's searches named (pebble paving was reckoned by the square zhang, with no labor figure).
  - "What did carrying stone cost a ri?": point it to 0260: its Japanese porter fares per stage (a 5-kan load, not stone)
    as the nearest, and its Qing rates as the comparison. Carrying stone a ri in Japan stays not found.
  - The ledger row the pass recorded `nothing-found` for 揚州畫舫錄/17 bears: supersede it with `make source-outcome` when
    you cite it.
- **0260 "What did hiring a horse or a porter cost?"** - issue group 4 (`passes/g4-porterage.md`): a load of stone by cart
  near a road, and by porters into deep forest.
  - Qing, stone by cart, ATTESTED: Yunnan 1769 (Bochum `yunnan_transport_costs.xls`, wages `yunnan_wages.xls`): oxcart
    for stone 0.001 tael per 100 jin per li (曲靖/南寧 and 臨安/建水), beside each place's craftsman and laborer wage; Gansu
    1769 (`database_of_transport_cost.xls`, `database_of_wages.xls`): stone in 600-jin carts, 0.01-0.012 tael per cart per
    li, and 玉門's remark (0.0138 claimed, the 1760 case's rate fixed instead); 欽定大清會典則例 卷130 (key
    daqing-huidian-zeli-130): the Peking cart rate, 200 cash in the city, 300 within 10 li, 0.02 tael a li beyond, for the
    loads it names (not stone; say so).
  - Qing, porters into mountains, ATTESTED ONLY FOR timber and unnamed loads: the Yunnan porter rows (0.0013-0.0025 tael
    per 100 jin per li, the 挑運/抬運 pair at 順寧); Gansu 秦州 (0.04 tael a porter-day, the laborer's wage; 50 jin for
    60 li) and 歸德 (rugged mountain timber, 0.009 by the old rule, 0.003 by the register, per 60 jin per li); and Gansu's
    repeated rule that stone takes no separate porter rate.
  - Already answered in part, Japan, not repeated: 0257's 1620 hill stone and 150 kg back-load, 0260's porter fares per
    stage (a 5-kan load). Qing already in 0260: Hunan and Zhili.
  - Japan, an Edo cart hire by the day or the load, and porters into forest with no trail: SILENT, the pass's searches named; Morisada's Osaka cart fee (下 p. 469) is a
    license fee, not a hire - name it as such only if you read it on the page. The Edo oxcart freight tables of 1726 and
    1742 (都史紀要32 『江戸の牛』, print only) are a lead not publicly readable: `make download-add` it.
  - No rate is scaled to 400 kg in the record; the reply does that, labeled.

## The procedure (session 1: write)

1. `make archive-inbox`. Then `make research-claim Q="0257 0260" FEATURE=408`.
2. For each page you cite, run `make archive-find`, then `make source-pages`, then `source-reader` from a bundle
   (`make check-bundle KEY=<k> WHOLE=1`, page images with `IMAGES=`). A new source takes `make reserve KIND=registry
   KEY=<k> URL=<u> TAGS="..."` and its two write-ups. At the eleventh new key, follow the continuation rule.
3. Edit the fragments, then `make record && make citations` and the record tests (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with messages opening `408: `.
4. Append to `specs/408-shrine-small-lines/implementation-check.md` (create it if absent) one line per question:
   `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.
5. Append to `specs/408-shrine-small-lines/briefs/handoff.md` (create it if absent) a `## Session 1` section:
   - one `- SECTION=NNNN/<id>` line per question;
   - per line of the issue you own, its verdict and the fragment file (the reply on #10 is built from this);
   - each changed figure or verdict, old and new, and each search named;
   - the new registry keys.
6. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.

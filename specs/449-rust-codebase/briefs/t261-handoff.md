# T261 handoff - session 1 (research and write)

- SECTION=0031
- T261.1 DONE - 0031's drawing page, bullet "Where does a village's cluster sit?": the windward high margin is now the rule "wherever their fall is rolled" (deviation, note -8 as before); a new sentence gives the declared case - where a map declares a fall toward the wind no margin is both high and windward, so the cluster takes the high, dry margin, its back to the hill and off the wind, labeled a GUESS (new absence note `how-our-maps-choose-and-draw-clustered-and-scattered-villages-shuson-sanson-9`), while each house still faces south (new citation note `sakamoto-tsubaki-1985-omoya-muki-4`, Sakamoto and Tsubaki 1985 p.114, original moved to the originals file by `make record`). The line-4 Evidence comment's guess list now names "the cluster's back to the hill on a declared fall into the wind". 0029's line-32 bullet (houses within about 11 degrees of south) is not contradicted.

## Files

- research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html
- research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.notes.html
- research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.originals.html (written by `make record`)
- specs/449-rust-codebase/briefs/t261-handoff.md

## For the check session

- **The brief's p.114 quotation had two slips**: the page reads 「主屋の向きの最多方位が傾斜方向と一致するのは，南東から西南西まで」, not 「最多方位と傾斜方向が一致するのは，南東から南西南まで」. Checked against the archived copy's page image (pdftoppm of page 2 of `/diagram/.specify/source-archive/f9/f94580bcd0a1/20261002T121839Z/served.pdf`, printed p.114, left column, bottom) and its text layer, which agree. The note quotes the page; the English says "from southeast to west-southwest".
- `make quote-verbatim Q=0031` reports the -4 note NOT-CHECKED ("not found verbatim in the archived text"): the PDF's text layer interleaves the two columns, so no long passage matches as one run. Quote-check should read it against the page image (page 2 of the PDF).
- The absence note -9 paraphrases the survey's findings (no link, per the absence form); its HTML comment quotes the three p.115 passages verbatim from the page image (right column top: 「このことを勘案すると，集落の南寄りに山が位置する場合は，台風時の風向に対する配慮が必要でなければ，最多方位は山に背を向けた方位となる。」 and 「この原因は主屋の表座からの見晴らしにあると考えられる。」; left column: 「7箇所の最多方位は，山に背を向けるか，あるいは，山に横向きになるかのいずれかである。」). Note the survey also says the hill-foot back-to-the-hill holds "unless the typhoon wind called for otherwise", which the note states. The search pass's own summary rule is not stated anywhere.
- The Kindai University theses on Oda were not cited and not put on the download list (no archived copy; not needed for the note).
- **Size**: the page was 19,845 bytes before and the addition took it over 20,000, so session comments on the page were cut (line 2's feature-292 sweep provenance comment removed; the history tails of the comments on the shares bullet, the no-lanes bullet, the row-village bullet and the channel-or-well bullet trimmed). It is now 19,987 bytes. No visible text outside the one bullet changed. The page sits 13 bytes under the cap; its next addition will need a split along its topics.
- No new registry key; no source page fetched (the archive copy was read), so no `source-pages`/`source-outcome` rows.
- Checks owed (not run, per the brief): quote-check on notes -4 and -9, translation-check on -4's original, record-format on 0031's drawing page.
## Check session (T261 session 2, 2026-11-22)
CHECKED quote-check 0031.drawing (notes -7, -8, -9, sakamoto-tsubaki-1985-omoya-muki-4, shizen-teibo-jawiki) - round 1: 2 VERBATIM+SUPPORTS (-4 read against the p.114 page image), 2 absence, 1 grounds, 0 unfootnoted - nothing; round 2 (-7, -8 after the trims): same, 0 findings - nothing
CHECKED record-format 0031 - round 1: 7 of 7 ruled, 1 VOCABULARY ('rolled'), 3 EDITs - applied; round 2: 6 of 6 ruled, 0 VOCABULARY/SESSION NOTE/HISTORY, 1 wording EDIT ('it is never drawn' -> 'chance never draws it', byte-neutral) - applied
CHECKED translation-check 0031.drawing#sakamoto-tsubaki-1985-omoya-muki-4 - FAITHFUL 0, LOOSE 1, WRONG 0 - applied ('matches the direction of the slope where the slope runs from southeast to west-southwest')
CHECKED source-reader 0031.drawing#sakamoto-tsubaki-1985-omoya-muki-4 - 1 READ (quote verbatim on p.114 page image), scope notes only - nothing (see OPEN)
CHECKED round-arbiter ask:449-T261-quote-check-0031-note-8-round-3 - accept: no third quote-check round on note -8 (its claim moved only by record-format's round-2 EDIT) - unit answered with record-checked REASON= citing the ruling
CHECKED modal-triage 0031.drawing pop-ups - 42 units, twice (before and after the EDITs); 13 TOUCHES (union of both rounds: cluster_position x6, cluster_shape x4, settlement_form--nucleated/--linear, hamlet/windbreak), 29 untouched - nothing (the 13 are OPEN). The triage bundle was hand-filtered to the units naming 0031 (plus hamlet/well and sheet/well, whose other page 0028.drawing had no changed block); 0028's own units were left to their builder
CHANGED research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html (the one bullet 'Where does a village's cluster sit?': record-format's EDITs, plus a hand trim of 50 bytes to keep the page under 20,000 - 'Which corner that is', 'the high windward margin', 'the land falls away'; now 19,998 bytes)
CHANGED research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.notes.html (note -9 'unless the typhoon wind had to be allowed for'; note -4's translation)
CHANGED research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.originals.html (rewritten by make record)
OPEN modal-depiction on 13 pop-ups the triage named (choice/cluster_position--flank, --high_margin, --mid_margin, --on_rise, --valley_head, --valley_mouth; choice/cluster_shape--crescent, --elongated, --round, --split; choice/settlement_form--linear, --nucleated; hamlet/windbreak) - pop-ups are the orchestrator's, not checked here
OPEN source-reader scope on -4 (no edit owed): the survey gives each gentle-slope village's COMMONEST bearing, SE to SW, not every house due south, so 'each house still faces south' states our maps' rule more tightly than the source; and p.115 finds hill-foot villages with a hill to the south turn their backs to it (face north), so the cited support holds for a gentle slope only, not a hill-foot cluster. Left: the page is 2 bytes under its cap and the sentence states the maps' rule; a reword or a split is the orchestrator's call
OPEN record-format OUTSIDE THE CHANGE: the 'Half our settlements are drawn clustered...' bullet shows 'a calibrated liberty' to the reader unexplained (the arbiter: file it as a row, not fixed in T261)
OPEN 0031.drawing.html is at 19,998 bytes, 2 under the cap: its next addition needs a split along its topics
OPEN every check dispatch this session carried ARBITER_OK (8 dispatches: 4 checks in round 1, 2 in round 2, the arbiter and the second triage) because another builder's tripwire reversal:/diagram/.clones/diagram-backlog/pool/hamlets/sawada/sawada.notes.md blocked all dispatches; its ruling is still owed (not mine to rule on, pool/ is out of this brief)
Nothing committed or staged (the brief's rule).

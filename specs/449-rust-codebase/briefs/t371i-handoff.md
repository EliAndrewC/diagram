# t371i handoff - session 1: write (cleanup 3)

- SECTION=0106 0113

I1 NARROWED - 0106's opening now says only what `jinya-kotobank` (archived copy, read 2026-11-23) carries: an intendant's office counted among its parts the small houses and long-houses that were the official quarters of its junior officials, the tetsuki and tedai (「手付(てづき)や手代(てだい)の官舎である小屋や長屋」), then links `0331-where-an-offices-staff-lived.html` for whether all staff lived there. The same overreach ("the staff lived inside the walls") was narrowed the same way in 0106's line 12 paragraph, its Evidence comment, and three places on 0106's drawing page (the opening paragraph twice, the long-house bullet) plus its Evidence comment.
I2 DONE - not one continuous passage: the archived text runs 「…ここを執務室にしていたのは、地元採用を中心とした地役人。 こちらの畳は黒の無地ヘリ 【高山陣屋×役人の仕事部屋】幕府から来た役人の職場「御役所」 幕府から派遣されてきた代官直属の役人…が仕事をする部屋。」 (a photo caption and a heading between), so the two passages are now joined with `; ` in both notes files, with the gloss "(the second passage is of the goyakusho)" after the second.
I3 DONE - `9731-mapple-takayama-jinya`: 1996, 1830, 1777 are on neither the archived text nor served.html; the limits now say what the page carries (buildings basically Edo-period with parts repaired, rebuilt and restored - 「一部で整備・改築・復元などの手が加えられていますが、基本的には江戸時代の建物」 - and officials sent from Edo were daikan or gundai, 「江戸から派遣された代官や郡代」). `0660-shimane-toshuko-lecture`: the lecture's line 213 reads 「渓流河川では片岸取入にする．急流河川においても片岸取入とする．緩流河川でも片岸取入を原則とする．」; its limits now say "on torrent and steep rivers, and as the rule on gentle ones", and its Used-for line "the practice on torrent and steep rivers and the rule on gentle ones".

Ledger: source-outcome cited for jinya-kotobank (0106), mapple-takayama-jinya (0113), shimane-toshuko-lecture. No new registry keys. `make record CHECK=1`, `make record`, `make glossary` clean; `make question-sizes`: 0 over 20,000.

## Files

- research/questions/0106-the-chief-retainers-house-karo-yashiki.html
- research/questions/0106-the-chief-retainers-house-karo-yashiki.drawing.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.notes.html
- research/questions/0113-the-office-hall-and-its-clerks-goyakusho.drawing.notes.html
- research/sources/010-works-cited/9731-mapple-takayama-jinya.html
- research/sources/010-works-cited/0660-shimane-toshuko-lecture.html
- specs/449-rust-codebase/briefs/t371i-handoff.md

## Left open

- 0106's drawing page was changed beyond the brief's named paragraph (same defect); its checks are owed with the findings page's.
- The barracks and retainers' quarters pop-ups that raised I1 were not touched (pop-ups are out of this brief's scope); their modal-research re-run is the next session's.
## Session 2 (t371i-checks)
CHECKED quote-check 0106 (7 units) - round 1: 8 READABLE, 6 VERBATIM, 2 NOT-CHECKED (canon l7r-budgets), 8 SUPPORTS, 2 unfootnoted (1 needs a source) - applied: its EDIT (jinya-kotobank note on 'At an intendancy the junior officials' official quarters...'); by hand: 'the head of that staff' narrowed to 'the head of its tedai, the motojime' with the daikan-tetsuki-jawiki note
CHECKED quote-check 0106 (round 2, daikan-tetsuki-jawiki) - 9 VERBATIM, 9 SUPPORTS, 0 unfootnoted - nothing
CHECKED quote-check 0113 (mapple-takayama-jinya-2, both pages) - 2 VERBATIM, 2 SUPPORTS, 0 unfootnoted - nothing
CHECKED record-format 0106 - 1 of 1 words ruled on, 0 VOCABULARY/SESSION NOTE/HISTORY (round 2 after the hand fix: same) - nothing
CHECKED record-format 0113 - 26 of 26 words ruled on, 0 VOCABULARY/SESSION NOTE/HISTORY - nothing
CHECKED translation-check 0113.drawing#mapple-takayama-jinya-2 - FAITHFUL 1 - nothing
CHECKED source-applicability mapple-takayama-jinya, shimane-toshuko-lecture - 2 APPLICABLE-WITH-LIMITS (each limits MISSING one), 1 tag WRONG - applied: 0660 limits (modern-design rules not said to bind premodern intakes; one uncited history paragraph, stone weirs from early Edo), 0660 period tag present-day,premodern; 9731 limits (family-in-residence sentence names the gundai, the daikan's family is our reading)
CHECKED modal-triage sheet/inner-rooms (0106, 0107) - 0 TOUCHES, 3 units answered triage: untouched - nothing
CHANGED research/questions/0106-the-chief-retainers-house-karo-yashiki.html
CHANGED research/sources/010-works-cited/0660-shimane-toshuko-lecture.html
CHANGED research/sources/010-works-cited/9731-mapple-takayama-jinya.html
CHANGED specs/449-rust-codebase/briefs/t371i-handoff.md
OPEN pop-ups owed because 0113 moved - modal-accuracy/gaps/references for sheet/clerks--room, sheet/office-hall, sheet/official-study; modal-depiction for sheet/office-hall, sheet/official-study, sheet/writing-rooms - in record-owed's batched pop-up checks, not triageable here; pop-ups are another builder's
OPEN barracks and retainers' quarters pop-ups (raised I1) - modal-research re-run still owed; pop-ups out of scope
OPEN other builders' owed units in this clone (0009, 0059, 0099, 0103, 0107 pop-ups; record-format 0009; source-applicability daozuofang) - untouched

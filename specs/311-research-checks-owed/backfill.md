# The intro-check backfill (feature 311, T08; spec FR-008, SC-003)

Every question in the record read once by `intro-check`, 2026-10-02: 236 questions in ten batches of 23-24
(`make check-bundle FOR=intro-check QS=... NOT_OWED_OK="feature 311 backfill, batch NN"`), and 0094 on its own after its
intro was written (INTRO-OK). The check ran as an ad-hoc Opus agent handed `.claude/agents/intro-check.md`'s contract
verbatim: a defined agent added in a session is not dispatchable until the session restarts (research R3).

| batch | questions | NO-INTRO-NEEDED | NEEDS-INTRO | flagged |
|---|---|---|---|---|
| 00 | 24 | 22 | 2 | 0003 place names (chimei); 0015 the chrysanthemum field (kiku) |
| 01 | 24 | 24 | 0 | - |
| 02 | 23 | 22 | 1 | 0056 river names |
| 03 | 24 | 24 | 0 | - |
| 04 | 23 | 22 | 1 | 0110 border posts and their crossing court |
| 05 | 24 | 24 | 0 | - |
| 06 | 24 | 23 | 1 | 0157 firebreaks (hiyokechi) |
| 07 | 23 | 22 | 1 | 0173 country estates around a city |
| 08 | 24 | 22 | 2 | 0212 pleasure quarters (yukaku); 0216 shrines in towns and cities |
| 09 | 23 | 22 | 1 | 0240 salt heaps at doorways (morijio) |
| 0094 | 1 | - | - | the GM's own example: written first (T07), INTRO-OK |

**Ten questions of 237 take an intro**; every other question explains itself from its heading and opening, most because
its subject is something the maps draw and history had. The nine the backfill flagged share one shape: the findings are
about something our maps do NOT draw, or draw differently from history, and the page never said so - a firebreak, a salt
heap, a licensed quarter, a town shrine left out; a river's one name, an Imperial flower field, a reception court, a near
estate, a village placed by its name. Each intro was written from that question's drawing page (and, for 0212, the GM's
notes: prostitution illegal by Imperial decree, `make canon`), and each owed `intro-check` and `record-format` alone -
never a source-reading check (`make record-owed`, 20 units for the ten). Their rulings: below, once returned.

## The written intros' checks

Each written intro owed exactly `intro-check` and `record-format` (`make record-owed`: 20 units for the ten), answered with
`make record-checked BUNDLE=...`.

| question | intro-check round 1 | record-format round 1 | round 2 |
|---|---|---|---|
| 0094 parley room | INTRO-OK (noted: the GM's table and tea against the drawing page's mats) | 0/0/0 (the same note) | - |
| 0003 place names | INTRO-OK | 0/0/0 | - |
| 0015 chrysanthemum field | INTRO-OK | 0/0/0 | - |
| 0056 river names | INTRO-OK | 0/0/0 | - |
| 0110 border court | INTRO-OK | 0/0/0 | - |
| 0157 firebreaks | INTRO-FIX: "a gap between houses" (the findings: never gaps between single houses), and "real towns" from Edo alone | 0/0/0, the same wording note | rewritten from the drawing page's reason; INTRO-OK, 0/0/0 |
| 0173 country estates | INTRO-OK | 0/0/0 | - |
| 0212 pleasure quarters | INTRO-FIX: the serving women's omission hung on the ban, where the drawing page says they worked in the inns | 0/0/0 | rewritten; INTRO-OK, 0/0/0 |
| 0216 town and city shrines | INTRO-FIX: implied no shrine at all is drawn; the small temple-quarter shrines are | 0/0/0, the same note | rewritten; INTRO-OK, 0/0/0 |
| 0240 salt heaps | INTRO-OK | 0/0/0 | - |

No written intro needed a third round; `make record-owed UNANSWERED=1` reports nothing owed.

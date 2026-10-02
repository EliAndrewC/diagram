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

(filled in as each returns)

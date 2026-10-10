# Feature Specification: Lower a research group's fixed cost, which feature 274's write cap spread over fewer things

**Status**: Filed - from feature 347's measurement (2026-10-10), `specs/274-leaner-research-sessions/research.md` R3

**Affects**: research process

**Input**: deferred work found by measurement. Feature 347 measured feature 274's caps on the 662 page sessions that
ran after it landed; the cost per thing checked ROSE where 274 expected it to fall. Rewriting this into a full spec, a
plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory).

## What was measured

(observed 2026-10-10; method: `specs/347-measure-feature274-write-cap-line-reads/measure/run_all.sh`, its `results.txt`
and `split.py`; R3 has every figure and the method's validation against R1.)

- The research groups after 274 (features 269, 280, 291 and 317) cost 1.36 M tokens per thing checked against R1's 1.04 M.
  Feature 269, which ran on both sides of the landing, rose from 1.18 M to 1.36 M.
- A write session got shorter (median 54 turns against 76) and lighter per turn (105 K against 152 K). A group now
  checks about 8 things where it checked 21.
- **The mechanism - CORRECTED by `research.md` R1 (2026-10-10):** a fit of each group's cost against its things shows
  the fixed part per group FELL (5.4 M to 3.5 M) and the cost per thing ROSE (0.78 M to 1.02 M), in more reading and
  searching per item; the explanation below, as filed, is wrong, and with it the size of the levers (about 4% and 2%).
  As filed: A group's sessions have a fixed part that does not shrink with the work. Check sessions run
  about 37 turns each, two a group, whatever they check, and a write session's setup is paid per session. So a write
  costs 6.8 turns a thing against 3.5, and a check 0.53 M a thing against 0.37 M.
- **Coordination.** Whole reads of coordination files are gone (0.5 M against 50.8 M), but the line reads still
  carry 30.5 M. `make lines` on the 170 KB claims file carries 16.0 M over 266 calls. Its median result is 4,147
  characters, largest 20,553, because a session greps it by a page name that matches many lines.

## The levers (a sketch, to be measured before choosing)

1. **One check pass over several write sessions.** Keep the write cap (it is what lowered the peak), but let the
   check sessions of two or three capped write sessions run as one set, so a group's checks again cover about 20
   things. To measure first: a check session's cost against the things it checks, from 347's `sessions-post.json`.
   Is it flat, as the medians suggest, or does it grow with the things?
2. **A claims lookup that answers the claim.** `make lines FILE=RESEARCH-CLAIMS.md KEY=<page>` returns every line that
   names the page. A session needs only to know whether its own questions are held. A lookup by question number (or
   only the live claims) would return a line or two.
3. **Re-measure with 347's scripts** (`run_all.sh`; set `LANDED` in `collect.py` to this feature's landing) and close
   with the figures in this feature's research.

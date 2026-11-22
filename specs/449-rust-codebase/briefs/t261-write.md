# Brief - feature 449 task T261 (0031's drawing page: the seat where a declared fall runs into the wind), session 1: research and write

You are a FRESH headless page session. This brief is the whole of what you need: do not read feature 449's spec,
plan or tasks to orient. Work only in this clone, `/diagram/.clones/diagram-backlog`, from its root (`cd` into it in
every command; `git -C` for every git call). The research record's own `CLAUDE.md` loads when you touch `research/`;
`scripts/container/page-session-rules.md` is in your system prompt.

**Do NOT commit, stage, stash, checkout or restore anything.** Other builders have uncommitted work in this clone
(rust/, dev/, specs/, Makefile, docs/, and another page session's research pages); the orchestrating session commits
your files by name. Touch only the files your item needs, and list every file you changed in the handoff. Never run
`scripts/sync-with-main.sh`, never push. Do not edit any `Research:` claim, `dev/claims-index.json`, any `pool/` file
or any pop-up - the orchestrator does the claims. Do not run `make claims-*`. Read narrowly: grep with `-o` and a short
context, `make notes Q=0031 KEYS=<k,k>`, read by line range; send the lookups you know you need in one message.

First: `make research-claim Q="0031" FEATURE=449` (0029 is read, not edited; claim it too if you must edit it) (release with `STATUS=done` at the end).

## Your items

No new registry key should be needed (`sakamoto-tsubaki-1985-omoya-muki` is already in the registry,
`research/sources/010-works-cited/10350-sakamoto-tsubaki-1985-omoya-muki.html`, archived: `make archive-find
KEY=sakamoto-tsubaki-1985-omoya-muki`); if one is, `make reserve` it.

- T261.1 **0031's drawing page** (`research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`,
  the bullet "Where does a village's cluster sit?", line 36). It says "Our hamlets take it on every map, a deliberate
  deviation: a hamlet's land is rolled to fall away from the wind or square across it, its high side windward or level,
  so its houses keep their back to the wind". That holds for every ROLLED fall. A map may DECLARE its fall (Sawada,
  `down_deg` 225, falls toward its northwest wind). Then every margin that faces the wind lies on the wet toe, and the
  seat (`rust/phases/src/seat.rs::seat`, feature 444 T27) takes the HIGH margin - the dry ground the bullet's first
  sentence gives - with the cluster's back to the hill, recording that seat as off the wind. Each house still faces
  south as 0029's drawing page draws it (its bullet "How near due south does a settlement's common bearing lie?"), so
  the houses' backs stay to the north. The page says none of this, so it reads as if every hamlet's back is to the wind.
  Write:
  (a) narrow "on every map" to the maps whose fall is rolled;
  (b) add the declared case in one or two plain sentences: where a declared fall runs toward the wind, no margin backs
  both; the cluster takes its high, dry margin with its back to the hill, off the wind, while each house keeps facing
  south. Footnote the house-bearing half to a NEW note in `0031-...drawing.notes.html` (the next free
  `how-our-maps-choose-and-draw-clustered-and-scattered-villages-shuson-sanson-<n>` or a `sakamoto-tsubaki-...` key per the
  record's note-key rules) quoting verbatim Sakamoto and Tsubaki 1985, p.114 (original, then English marked as a
  translation; check the archived copy with `make quote-verbatim`):
  「以上から，緩傾斜地に立地する集落で，主屋の向きの最多方位と傾斜方向が一致するのは，南東から南西南までであり，傾斜方向が北北東，北東，および，西北西の場合には，最多方位が南東から南西までの範囲となるように，傾斜方向とは90度ないしは180度異なる方位が選ばれる。」
  ("So on gentle slopes, the house bearing matches the fall only when the fall is between southeast and
  south-southwest. Where the ground falls north-northeast, northeast or west-northwest, a bearing 90 or 180 degrees off
  the fall is chosen, so that the commonest bearing lies between southeast and southwest.")
  (c) LABEL the cluster's back to the hill as a GUESS, with an absence note (a note entry whose text says what was
  searched and found): searched 2026-11-22 (feature 449 T261's search pass: the archive and the web, Japanese and
  Chinese terms on a settlement whose ground falls toward its wind - 背山面水, 坐北朝南, 屋敷林 and 防風林 on slopes, 主屋の向き,
  山を背). Findings to state in the note, each only as far as it goes: the one survey that sees the case is of 42 Okinawan
  villages, 1974-84, so after 1868; at a hill's foot its houses turned their back to the hill, which it puts down to
  the view from the front rooms, not to the wind (p.115: 「7箇所の最多方位は，山に背を向けるか，あるいは，山に横向きになるかのいずれかである。」);
  on gentle slopes its houses turned south whatever the fall (the p.114 passage above); no page read says which way a
  CLUSTER's back faced, the hill or the wind, when the two lay on opposite sides; China: nothing found. Quote any passage
  you put in a note verbatim from the archived copy. (The search pass also read two Kindai University theses on Oda,
  Higashi-Hiroshima, whose copies are not archived; do NOT cite them unless `make archive-find` names a copy - put them on
  `research/to-download.md` with `make download-add` if you want them recorded.) The search pass's own summary rule
  ("gentle slope: back to the wind; hill foot: back to the hill") is its synthesis, NOT a finding: do not state it.
  (d) the line-4 `<!-- Evidence: ... -->` comment: add "the cluster's back to the hill on a declared fall into the
  wind" to its guess list.
  A drawing page states the map's rule and its label; keep findings to the footnote and note. Check 0029's drawing page
  is not contradicted (read its bullet at line 32 only).

## The procedure (session 1: research and write)

1. **Canon once**: `make canon TERMS="wind|hill|northwest"`.
2. **Archive before the web**: `make archive-inbox`, then `make archive-find KEY=<k>` for any source before a fetch. No
   new source should be needed. A page you do read goes through
   `make source-pages OUT=/tmp/l7r-check/t261-pages URL=<u> QUESTION=0031 SOUGHT="<what>"` and `make source-outcome`.
3. **Write.** `Read` every file you will change in ONE message, then `Edit`. Footnotes and the four labels by the
   record's rules; no history in the text; a session note is an HTML comment. Then `make record CHECK=1`, `make record`,
   `make glossary`, and `make question-sizes` (no page over 20,000 bytes of prose).
4. **Hand off.** Write `specs/449-rust-codebase/briefs/t261-handoff.md`: `- SECTION=0031`, one line
   `T261.1 <DONE|NARROWED|LEFT> - <what the record now says>`, every file you changed under `## Files`, and anything
   left open and why. Do NOT run the record checks - the next session does, fresh. Your last message is one paragraph
   saying what you wrote.

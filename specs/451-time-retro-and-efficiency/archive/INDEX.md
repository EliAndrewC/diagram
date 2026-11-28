# 451-time-retro-and-efficiency - its finished records, in parts

Load this file when: you need a finished (ticked) task of feature 451 - its archived plan section, or its task line and verify
note - or you are about to open, read or grep this feature's plan-done.md or tasks-done.md, which stand here in parts.

WHY: these records grew to megabytes (451's plan-done.md 3.6 MB, its tasks-done.md 0.6 MB); a session that read or grepped one whole
spent its context on it (the GM 2026-11-27; 451 T536, T537). `make archive-split` cut them, in their own order, into parts of about
65536 bytes (a task larger than that alone in its part); a part's name is its sequence and its lowest and highest id, and the ranges overlap, so find a task by index.json.

## How to find one task

- Its plan section: `make plan-section F=451 T=T<n>` - it opens only the part that holds the task.
- Its part by hand: `index.json` here maps each task to its part(s) (`tasks` -> the record -> `T<n>`); read that part alone.
- A task archived since the last fold is in the flat plan-done.md or tasks-done.md beside this directory (the tail; a tick folds it
  in).

## Do not

- Read every part, `cat archive/*`, or Read a part when one task's section is all you need (`make plan-section`).
- Grep this directory or the feature directory broadly: a common word matches thousands of lines. Grep with `-l` or `-c` first,
  then read the one part it names.
- Read the feature's plan-review.json whole: it is not cut here (451's stood at 5.0 MB; 462 T545 splits it). `make plan-section`
  and `make plan-delta` read it for you.

## The parts

| record | part | bytes |
|---|---|---|
| plan-done.md | `plan-done/001-T01-T30.md` | 65652 |
| plan-done.md | `plan-done/002-T12-T20.md` | 57121 |
| plan-done.md | `plan-done/003-T21-T39.md` | 55987 |
| plan-done.md | `plan-done/004-T38-T43.md` | 64537 |
| plan-done.md | `plan-done/005-T07-T47.md` | 57886 |
| plan-done.md | `plan-done/006-T08-T55.md` | 61263 |
| plan-done.md | `plan-done/007-T09-T66.md` | 65155 |
| plan-done.md | `plan-done/008-T59-T68.md` | 54552 |
| plan-done.md | `plan-done/009-T54-T70.md` | 49460 |
| plan-done.md | `plan-done/010-T67-T75.md` | 56111 |
| plan-done.md | `plan-done/011-T48-T77.md` | 58154 |
| plan-done.md | `plan-done/012-T78-T85.md` | 62465 |
| plan-done.md | `plan-done/013-T81-T93.md` | 61488 |
| plan-done.md | `plan-done/014-T82-T101.md` | 62515 |
| plan-done.md | `plan-done/015-T92-T108.md` | 65641 |
| plan-done.md | `plan-done/016-T57-T113.md` | 63851 |
| plan-done.md | `plan-done/017-T80-T123.md` | 57644 |
| plan-done.md | `plan-done/018-T83-T105.md` | 54335 |
| plan-done.md | `plan-done/019-T89-T129.md` | 58884 |
| plan-done.md | `plan-done/020-T91-T157.md` | 59973 |
| plan-done.md | `plan-done/021-T90-T161.md` | 48297 |
| plan-done.md | `plan-done/022-T155-T171.md` | 46615 |
| plan-done.md | `plan-done/023-T100-T175.md` | 48677 |
| plan-done.md | `plan-done/024-T165-T183.md` | 62508 |
| plan-done.md | `plan-done/025-T184-T194.md` | 59523 |
| plan-done.md | `plan-done/026-T193-T207.md` | 56349 |
| plan-done.md | `plan-done/027-T192-T212.md` | 61755 |
| plan-done.md | `plan-done/028-T203-T222.md` | 64784 |
| plan-done.md | `plan-done/029-T15-T241.md` | 57225 |
| plan-done.md | `plan-done/030-T23-T244.md` | 59481 |
| plan-done.md | `plan-done/031-T23-T247.md` | 56452 |
| plan-done.md | `plan-done/032-T151-T249.md` | 61370 |
| plan-done.md | `plan-done/033-T252-T259.md` | 63781 |
| plan-done.md | `plan-done/034-T227-T263.md` | 62738 |
| plan-done.md | `plan-done/035-T265-T272.md` | 51723 |
| plan-done.md | `plan-done/036-T281-T292.md` | 51796 |
| plan-done.md | `plan-done/037-T289-T309.md` | 52235 |
| plan-done.md | `plan-done/038-T104-T316.md` | 57741 |
| plan-done.md | `plan-done/039-T274-T339.md` | 60540 |
| plan-done.md | `plan-done/040-T336-T347.md` | 50873 |
| plan-done.md | `plan-done/041-T324-T359.md` | 46369 |
| plan-done.md | `plan-done/042-T139-T394.md` | 58491 |
| plan-done.md | `plan-done/043-T314-T424.md` | 63412 |
| plan-done.md | `plan-done/044-T164-T428.md` | 65220 |
| plan-done.md | `plan-done/045-T143-T426.md` | 65476 |
| plan-done.md | `plan-done/046-T294-T408.md` | 60911 |
| plan-done.md | `plan-done/047-T286-T454.md` | 60128 |
| plan-done.md | `plan-done/048-T230-T457.md` | 64067 |
| plan-done.md | `plan-done/049-T437-T464.md` | 61192 |
| plan-done.md | `plan-done/050-T444-T466.md` | 64415 |
| plan-done.md | `plan-done/051-T231-T474.md` | 65470 |
| plan-done.md | `plan-done/052-T353-T482.md` | 61690 |
| plan-done.md | `plan-done/053-T310-T485.md` | 59302 |
| plan-done.md | `plan-done/054-T388-T499.md` | 56874 |
| plan-done.md | `plan-done/055-T470-T504.md` | 64879 |
| plan-done.md | `plan-done/056-T363-T515.md` | 61869 |
| plan-done.md | `plan-done/057-T36-T530.md` | 65141 |
| plan-done.md | `plan-done/058-T167-T334.md` | 59880 |
| plan-done.md | `plan-done/059-T307-T410.md` | 62519 |
| plan-done.md | `plan-done/060-T36-T412.md` | 60661 |
| plan-done.md | `plan-done/061-T325-T525.md` | 61852 |
| plan-done.md | `plan-done/062-T513-T537.md` | 65281 |
| plan-done.md | `plan-done/063-T536-T536.md` | 6792 |
| tasks-done.md | `tasks-done/001-T01-T88.md` | 65255 |
| tasks-done.md | `tasks-done/002-T89-T160.md` | 65221 |
| tasks-done.md | `tasks-done/003-T161-T240.md` | 65156 |
| tasks-done.md | `tasks-done/004-T241-T300.md` | 64876 |
| tasks-done.md | `tasks-done/005-T301-T344.md` | 64682 |
| tasks-done.md | `tasks-done/006-T345-T393.md` | 64658 |
| tasks-done.md | `tasks-done/007-T394-T433.md` | 64555 |
| tasks-done.md | `tasks-done/008-T434-T466.md` | 65165 |
| tasks-done.md | `tasks-done/009-T467-T517.md` | 65226 |
| tasks-done.md | `tasks-done/010-T518-T539.md` | 23130 |

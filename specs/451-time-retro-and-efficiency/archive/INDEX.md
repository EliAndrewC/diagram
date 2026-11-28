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
- Read the feature's plan-review.json whole, or its parts here: `make archive-split` keeps its live entries flat (451's stood at
  5.0 MB) and moves a closed task's verdicts and rounds to `plan-review/` parts, `index.json` naming each task's (462 T545).
  `make plan-section` and `make plan-delta` read it for you.

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
| plan-done.md | `plan-done/064-T18-T420.md` | 33395 |
| plan-done.md | `plan-done/065-T313-T373.md` | 62006 |
| plan-done.md | `plan-done/066-T369-T413.md` | 58138 |
| plan-done.md | `plan-done/067-T404-T428.md` | 65119 |
| plan-done.md | `plan-done/068-T341-T364.md` | 21703 |
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
| plan-review.json | `plan-review/001-T03-T07.json` | 53594 |
| plan-review.json | `plan-review/002-T08-T10.json` | 55743 |
| plan-review.json | `plan-review/003-T11-T13.json` | 57803 |
| plan-review.json | `plan-review/004-T14-T16.json` | 55367 |
| plan-review.json | `plan-review/005-T17-T21.json` | 56599 |
| plan-review.json | `plan-review/006-T23-T28.json` | 60812 |
| plan-review.json | `plan-review/007-T29-T34.json` | 60749 |
| plan-review.json | `plan-review/008-T35-T40.json` | 64097 |
| plan-review.json | `plan-review/009-T41-T44.json` | 63808 |
| plan-review.json | `plan-review/010-T45-T48.json` | 55983 |
| plan-review.json | `plan-review/011-T49-T54.json` | 64254 |
| plan-review.json | `plan-review/012-T55-T59.json` | 60736 |
| plan-review.json | `plan-review/013-T60-T65.json` | 58021 |
| plan-review.json | `plan-review/014-T66-T71.json` | 61520 |
| plan-review.json | `plan-review/015-T72-T77.json` | 63717 |
| plan-review.json | `plan-review/016-T78-T82.json` | 55246 |
| plan-review.json | `plan-review/017-T83-T86.json` | 52449 |
| plan-review.json | `plan-review/018-T87-T88.json` | 52280 |
| plan-review.json | `plan-review/019-T89-T93.json` | 62987 |
| plan-review.json | `plan-review/020-T94-T98.json` | 50706 |
| plan-review.json | `plan-review/021-T99-T101.json` | 48293 |
| plan-review.json | `plan-review/022-T102-T105.json` | 63614 |
| plan-review.json | `plan-review/023-T106-T110.json` | 56677 |
| plan-review.json | `plan-review/024-T111-T116.json` | 65217 |
| plan-review.json | `plan-review/025-T117-T140.json` | 45940 |
| plan-review.json | `plan-review/026-T141-T150.json` | 57363 |
| plan-review.json | `plan-review/027-T151-T156.json` | 60127 |
| plan-review.json | `plan-review/028-T157-T159.json` | 48372 |
| plan-review.json | `plan-review/029-T160-T167.json` | 60794 |
| plan-review.json | `plan-review/030-T168-T170.json` | 50490 |
| plan-review.json | `plan-review/031-T171-T175.json` | 64590 |
| plan-review.json | `plan-review/032-T176-T182.json` | 60846 |
| plan-review.json | `plan-review/033-T183-T185.json` | 48822 |
| plan-review.json | `plan-review/034-T186-T189.json` | 64593 |
| plan-review.json | `plan-review/035-T190-T193.json` | 62896 |
| plan-review.json | `plan-review/036-T194-T197.json` | 43659 |
| plan-review.json | `plan-review/037-T198-T201.json` | 61590 |
| plan-review.json | `plan-review/038-T202-T211.json` | 57226 |
| plan-review.json | `plan-review/039-T212-T216.json` | 58232 |
| plan-review.json | `plan-review/040-T217-T223.json` | 61936 |
| plan-review.json | `plan-review/041-T224-T227.json` | 55486 |
| plan-review.json | `plan-review/042-T228-T231.json` | 42607 |
| plan-review.json | `plan-review/043-T232-T235.json` | 64274 |
| plan-review.json | `plan-review/044-T236-T240.json` | 59517 |
| plan-review.json | `plan-review/045-T241-T242.json` | 17173 |
| plan-review.json | `plan-review/046-T243-T243.json` | 70116 |
| plan-review.json | `plan-review/047-T244-T247.json` | 61647 |
| plan-review.json | `plan-review/048-T248-T250.json` | 49551 |
| plan-review.json | `plan-review/049-T251-T253.json` | 55831 |
| plan-review.json | `plan-review/050-T254-T258.json` | 55986 |
| plan-review.json | `plan-review/051-T259-T262.json` | 59865 |
| plan-review.json | `plan-review/052-T263-T264.json` | 50855 |
| plan-review.json | `plan-review/053-T265-T270.json` | 62537 |
| plan-review.json | `plan-review/054-T271-T280.json` | 59225 |
| plan-review.json | `plan-review/055-T281-T284.json` | 47669 |
| plan-review.json | `plan-review/056-T285-T285.json` | 47385 |
| plan-review.json | `plan-review/057-T286-T291.json` | 45098 |
| plan-review.json | `plan-review/058-T292-T294.json` | 57063 |
| plan-review.json | `plan-review/059-T295-T298.json` | 51956 |
| plan-review.json | `plan-review/060-T299-T303.json` | 58621 |
| plan-review.json | `plan-review/061-T304-T307.json` | 59318 |
| plan-review.json | `plan-review/062-T308-T309.json` | 47430 |
| plan-review.json | `plan-review/063-T310-T312.json` | 39122 |
| plan-review.json | `plan-review/064-T313-T314.json` | 54686 |
| plan-review.json | `plan-review/065-T315-T321.json` | 52094 |
| plan-review.json | `plan-review/066-T324-T331.json` | 47348 |
| plan-review.json | `plan-review/067-T332-T335.json` | 60059 |
| plan-review.json | `plan-review/068-T336-T345.json` | 57142 |
| plan-review.json | `plan-review/069-T346-T354.json` | 64513 |
| plan-review.json | `plan-review/070-T355-T363.json` | 60268 |
| plan-review.json | `plan-review/071-T364-T369.json` | 59989 |
| plan-review.json | `plan-review/072-T370-T387.json` | 64349 |
| plan-review.json | `plan-review/073-T388-T396.json` | 65054 |
| plan-review.json | `plan-review/074-T397-T412.json` | 52247 |
| plan-review.json | `plan-review/075-T413-T424.json` | 58052 |
| plan-review.json | `plan-review/076-T425-T435.json` | 64543 |
| plan-review.json | `plan-review/077-T436-T442.json` | 64935 |
| plan-review.json | `plan-review/078-T443-T445.json` | 60258 |
| plan-review.json | `plan-review/079-T446-T452.json` | 63830 |
| plan-review.json | `plan-review/080-T453-T462.json` | 58476 |
| plan-review.json | `plan-review/081-T463-T472.json` | 64970 |
| plan-review.json | `plan-review/082-T473-T489.json` | 50475 |
| plan-review.json | `plan-review/083-T490-T505.json` | 63557 |
| plan-review.json | `plan-review/084-T506-T511.json` | 39839 |
| plan-review.json | `plan-review/085-T512-T515.json` | 58668 |
| plan-review.json | `plan-review/086-T517-T529.json` | 64051 |
| plan-review.json | `plan-review/087-T530-T537.json` | 63062 |
| plan-review.json | `plan-review/088-other-other.json` | 26240 |

#!/bin/bash
# feature 317 T07: the whole feature against origin/main (/tmp/main317, 2ba3c353c), one process at a time (the host at its memory cap)
cd /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard
CLOCK=cpu bash ../314-seat-before-settle/abab.sh 15 1,2,3,4,5,6,7,8 /tmp/main317 /diagram/.clones/diagram-performance /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/t07-15 > t07-15.out 2>&1
CLOCK=cpu bash ../314-seat-before-settle/abab.sh 40 2,6,10,13 /tmp/main317 /diagram/.clones/diagram-performance /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/t07-40 > t07-40.out 2>&1
ROOT=/diagram/.clones/diagram-performance timeout 3000 python3 /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/passage_smoke.py 40 2,6,10,13 > t07-passages-40.log 2>&1
ROOT=/diagram/.clones/diagram-performance timeout 3000 python3 /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/passage_smoke.py 15 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16 > t07-passages-15.log 2>&1
for s in 4 13 39 2 6 8 25 47; do
  echo "base $s $(ROOT=/tmp/main317 timeout 1500 python3 /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/stagetime.py 20 $s 2>&1 | tail -1)"
  echo "new  $s $(ROOT=/diagram/.clones/diagram-performance timeout 1500 python3 /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/stagetime.py 20 $s 2>&1 | tail -1)"
done > t07-20.log
(cd /diagram/.clones/diagram-performance/.claude/skills/diagram && make cohort N=24 JOBS=2 > /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/t07-cohort-new2.log 2>&1)
echo T07 DONE

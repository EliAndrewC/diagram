#!/bin/bash
# feature 317 T06: the route searched per layout round its own parts, against the base (the fixed judge without it)
# - stage times at 20 households (feature 314 R12's leg: seed 13 refused, seeds 4 and 39 slow web), base and new alternated
# - why the corridor-only layouts found no path, both engines (corridor_only.py)
# - the homesteads stage in CPU seconds, alternated (abab.sh)
cd /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard
for s in 4 13 39 2 6 8 25 47; do
  echo "base $s $(ROOT=/tmp/base317 timeout 1500 python3 /tmp/claude-1000/-diagram/bf917120-9a91-46b2-b9b1-10b792b1a311/scratchpad/stagetime.py 20 $s 2>&1 | tail -1)"
  echo "new  $s $(ROOT=/diagram/.clones/diagram-performance timeout 1500 python3 /tmp/claude-1000/-diagram/bf917120-9a91-46b2-b9b1-10b792b1a311/scratchpad/stagetime.py 20 $s 2>&1 | tail -1)"
done > t06-20.log
for leg in base new; do
  root=/tmp/base317; [ $leg = new ] && root=/diagram/.clones/diagram-performance
  ROOT=$root timeout 3000 python3 corridor_only.py 15 1,2,3,4,5,6,7,8 > t06-only-15-$leg.log 2>&1
  ROOT=$root timeout 3000 python3 corridor_only.py 40 2,6,10,13 > t06-only-40-$leg.log 2>&1
done
CLOCK=cpu bash ../314-seat-before-settle/abab.sh 15 1,2,3,4,5,6,7,8 /tmp/base317 /diagram/.clones/diagram-performance /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/t06-15 > t06-15.out 2>&1
CLOCK=cpu bash ../314-seat-before-settle/abab.sh 40 2,6,10,13 /tmp/base317 /diagram/.clones/diagram-performance /diagram/.clones/diagram-performance/specs/317-reached-across-a-yard/t06-40 > t06-40.out 2>&1
echo T06 DONE

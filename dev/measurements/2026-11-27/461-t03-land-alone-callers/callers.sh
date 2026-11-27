#!/usr/bin/env bash
# 461 T03 (plan D11): who asks `alone_owed`, who runs `land-alone.sh`, and who reaches `l7r-gate land`'s landing - a grep over
# rust/, scripts/ and the Makefile. Run from the clone's root; the output is this folder's output.txt.
set -u
echo '== alone_owed: where it is defined and asked'
grep -rn 'alone_owed' rust/ scripts/ Makefile
echo '== land-alone.sh: the runner (the SCRIPT constant and its one use)'
grep -rn 'SCRIPT' rust/gate/crates/land/src/land/alone.rs
echo '== land-alone.sh named in an executable line of rust/ or scripts/ or the Makefile (comments, the script itself and tests left out)'
grep -rn 'land-alone\.sh' rust/ scripts/ Makefile | grep -v -E '^[^:]+:[0-9]+:\s*(//|#)' | grep -v -E '/tests(\.rs|/)' | grep -v '^scripts/land-alone\.sh:'
echo '== l7r-gate land: the Makefile targets that run it (LAND_RUN), and the other scripts that call it'
grep -n 'LAND_RUN' Makefile
grep -rn 'l7r-gate.sh" land' scripts/
echo '== the landing dispatch: the arms of land::cli that never reach Land::land'
grep -n 'Some("--unfinished")\|Some("--carry")\|"--stop"' rust/gate/crates/land/src/land.rs

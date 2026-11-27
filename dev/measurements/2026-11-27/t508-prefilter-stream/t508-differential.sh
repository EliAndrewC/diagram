#!/usr/bin/env bash
# t508: the differential test in the scratch build B's source (never the tree): the old prefilters against the stream over copies of the state
set -euo pipefail
S=$1
cd "$S/b/src/rust"
T508_DIFF=$S/diff T508_OUT=$S/t508-differential.tsv CARGO_TARGET_DIR=$S/b/target cargo test --offline --profile tool -p l7r_shared --lib t508_differential

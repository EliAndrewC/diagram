#!/bin/bash
# T515: a warm build stays warm after the prune. On COPIES of the mirror's `tool` profile (the real one never written: copied with
# O_NOATIME so its atimes do not move), build every package that profile serves, (A) unpruned, then (B) with the prune's list
# (computed from the REAL profile by stat alone) removed from the copy; count Fresh and Compiling units and time each build.
set -u
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad
SRC=$HOME/.cache/l7r-cargo-target/diagram
COPY=$S/t515-warm-target
LIST=$S/t515-warm-list.txt
rm -f "$LIST"
SIG=nojson MODE=rel KEY=kind LIST=$LIST ROOT=$SRC "$S/t515-measure.sh" > "$S/t515-warm-measure.txt"
# the list is a profile's path line, then its entries; only the tool profile's are kept
awk -v want="$SRC/tool" '/^\// {cur=$0; next} NF && cur==want {print}' "$LIST" | sort -u > "$LIST.rel"
echo "prune list: $(wc -l < "$LIST.rel") entries"
copy() { rm -rf "$COPY"; mkdir -p "$COPY"; tar -C "$SRC" --atime-preserve=system -cf - tool | tar -C "$COPY" -xf -; }
build() {
  label=$1
  for p in "-p l7r_gate" "-p l7r_guard" "-p l7r_mode_a" "-p l7r_phases --bin hamlet"; do
    log="$S/t515-warm-$label-$(echo "$p" | tr ' ' _).log"
    start=$(date +%s.%N)
    ( cd /diagram/rust && env -u RUSTFLAGS -u CARGO_ENCODED_RUSTFLAGS -u RUSTC_WRAPPER -u RUSTC_WORKSPACE_WRAPPER \
        CARGO_TARGET_DIR="$COPY" cargo build --profile tool --locked -v --manifest-path /diagram/rust/Cargo.toml $p ) > "$log" 2>&1
    rc=$?
    end=$(date +%s.%N)
    printf '%s\t%s\trc=%s\t%.1f s\tfresh=%s\tcompiling=%s\n' "$label" "$p" "$rc" "$(echo "$end - $start" | bc)" \
      "$(grep -c '^ *Fresh ' "$log")" "$(grep -c '^ *Compiling ' "$log")"
  done
}
copy
echo "copy A: $(du -s --block-size=1M "$COPY" | cut -f1) MB"
build A-unpruned
copy
n=0
while read -r rel; do
  case "$rel" in *..*) continue ;; esac
  rm -rf -- "$COPY/tool/$rel" && n=$((n+1))
done < "$LIST.rel"
echo "copy B: $n entries pruned, $(du -s --block-size=1M "$COPY" | cut -f1) MB"
build B-pruned
build B-again
rm -rf "$COPY"

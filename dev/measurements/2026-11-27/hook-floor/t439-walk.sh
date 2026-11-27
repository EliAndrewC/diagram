#!/usr/bin/env bash
# in-process: time N calls of the wrapper's newer() over the tree's sources
TREE=$1 GOOD=$2 N=${3:-20}
SOURCES=("$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock" "$TREE/.cargo/config.toml")
shopt -s globstar nullglob
newer() { [ -e "$1" ] || return 0; local f; for f in "${SOURCES[@]}" "$TREE"/rust/guard/**; do [ "$f" -nt "$1" ] && return 0; done; return 1; }
for ((i=0;i<N;i++)); do s=$EPOCHREALTIME; newer "$GOOD"; e=$EPOCHREALTIME; echo "$s $e"; done

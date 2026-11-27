#!/usr/bin/env bash
# t508: four scratch guards, never the tree itself - clean (HEAD), A (HEAD, the prefilter's split_once made memmem over the whole
# string), C (A, and under a hold the prefilter's text handed to Part::read), B (the tree's working files: the stream).
# usage: t508-build.sh <tree> <scratch dir>
set -euo pipefail
TREE=$1 OUT=$2
mkdir -p "$OUT/bin"
export CARGO_TARGET_DIR="$OUT/target"
build() { (cd "$OUT/src/rust" && cargo build --offline --profile tool -p l7r_guard --bin l7r-guard >"$OUT/build-$1.log" 2>&1); cp "$CARGO_TARGET_DIR/tool/l7r-guard" "$OUT/bin/l7r-guard-$1"; }
fresh() { rm -rf "$OUT/src" && mkdir -p "$OUT/src" && git -C "$TREE" archive HEAD rust .cargo | tar -x -C "$OUT/src"; }
fresh; build clean
G=$OUT/src/rust/guard
python3 - "$G" <<'PY'
import sys
g = sys.argv[1]
p = g + '/Cargo.toml'; s = open(p).read()
s = s.replace('fancy-regex = "0.14"\n', 'fancy-regex = "0.14"\nmemchr = "2"\n', 1); open(p, 'w').write(s)
p = g + '/src/guards/record_edit_gate.rs'; s = open(p).read()
old = '''    state
        .split_once("\\"plan_holds\\":")
        .is_some_and(|(_, rest)| {'''
new = '''    memchr::memmem::find(state.as_bytes(), b"\\"plan_holds\\":")
        .map(|i| ("", &state[i + 13..]))
        .is_some_and(|(_, rest)| {'''
assert old in s; s = s.replace(old, new); open(p, 'w').write(s)
PY
build A
python3 - "$G" <<'PY'
import sys
g = sys.argv[1]
p = g + '/src/guards/record_edit_gate.rs'; s = open(p).read()
old = '''        .is_some_and(|p| std::fs::read_to_string(p).is_ok_and(|s| holds_text(&s)))'''
new = '''        .is_some_and(|p| std::fs::read_to_string(p).is_ok_and(|s| { let h = holds_text(&s); if h { *crate::shared::checks::handle::part::GIVEN.lock().unwrap() = Some(s); } h }))'''
assert old in s; s = s.replace(old, new); open(p, 'w').write(s)
p = g + '/shared/src/checks/handle/part.rs'; s = open(p).read()
old = '''        Self::parse(std::fs::read_to_string(path).unwrap_or_default(), rows)'''
new = '''        let given = GIVEN.lock().unwrap().take();
        Self::parse(given.unwrap_or_else(|| std::fs::read_to_string(path).unwrap_or_default()), rows)'''
assert old in s; s = s.replace(old, new)
s = s.replace('impl Part {', '/// t508 C\npub static GIVEN: std::sync::Mutex<Option<String>> = std::sync::Mutex::new(None);\n\nimpl Part {', 1); open(p, 'w').write(s)
p = g + '/shared/src/checks/handle.rs'; s = open(p).read()
s = s.replace('mod part;', 'pub mod part;', 1); open(p, 'w').write(s)
PY
grep -n "mod part" "$G/shared/src/checks/handle.rs"
build C
fresh
for f in rust/guard/shared/src/checks/scan.rs rust/guard/shared/src/checks/scan/tests.rs rust/guard/shared/src/checks.rs rust/guard/src/guards/record_edit_gate.rs rust/guard/src/guards/checks_hooks.rs rust/guard/src/guards/checks_hooks/tests.rs; do mkdir -p "$OUT/src/$(dirname $f)"; cp "$TREE/$f" "$OUT/src/$f"; done
build B
ls -la "$OUT/bin"

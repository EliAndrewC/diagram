//! The counter-only clear on Rust (feature 449 T165): a unit that only gained counter statements is the base's version, anything else is
//! code; and the clear end to end on a scratch repository - a Rust claim cleared, a `.py` one still asked of the Python.

use serde_json::{json, Value};

use super::counter_only;
use crate::claims::tests::{claims, fixture};
use crate::claims::units::{rust_units, Unit};
use crate::record::testkit::{commit, git, put};

const BASE: &str = "/// Research: the reach - NONE: plumbing
pub fn reach(counts: &mut Counts, xs: &[u32]) -> u32 {
    let n = xs.len();
    tally(counts, \"read@reach\", n as u64);
    n as u32
}
";

fn unit(src: &str) -> Unit {
    rust_units(src, "rust/phases/src/x.rs").1.remove(0)
}

/// Is `now` the base with counters only added, the row recorded at the base's code?
fn only(now: &str) -> bool {
    let u = unit(now);
    let claim = u.claims[0].clone();
    let was = unit(BASE).code(&claim);
    counter_only(BASE, now, &u, &claim, Some(&was))
}

fn with(line: &str) -> String {
    BASE.replace("    n as u32\n", &format!("{line}\n    n as u32\n"))
}

#[test]
fn a_unit_that_only_gained_counters_is_its_base() {
    for added in [
        "    tally(counts, \"test@reach\", 2 * xs.len() as u64 + n as u64);",
        "    crate::counts::tally(\n        &mut out.counts,\n        \"write@reach\",\n        (n + 3) * 4 as usize,\n    ); // a comment",
        "    add(counts, \"pt_test@reach\", n as u64);",
        "    self.counts.add(\"candidate@reach\", self.ring.len());",
        "    crate::counts::merge(&mut s.counts, &counts);",
        "    tally(counts, \"read@reach\", before.0 as u64);",
        "    #[cfg(feature = \"counters\")]\n    {\n        let k = expensive(xs);\n        counts.0.insert(k, 1);\n    }",
        "    #[cfg(feature = \"counters\")]\n    eprintln!(\"{n}\");",
        "    #[cfg(feature = \"counters\")]\n    let k = vec![1, 2];",
    ] {
        let now = format!("use crate::counts::tally as add;\n{}", with(added));
        assert!(only(&now), "{added}");
    }
    // the base's own counter kept in place, a second copy added
    assert!(only(&with("    tally(counts, \"read@reach\", n as u64);")));
}

#[test]
fn anything_else_is_code() {
    for added in [
        "    tally(counts, \"read@reach\", n - 1);", // a `-` may underflow
        "    tally(counts, \"read@reach\", xs[0] as u64);", // indexing may panic
        "    tally(counts, \"read@reach\", f(n));",  // a call runs code
        "    tally(counts, \"read@reach\", n.pow(2));", // a method other than `len`
        "    tally(counts, \"read@reach\", n as f64);", // a float cast
        "    tally(counts, \"not a key\", n);",      // a key out of the counters' form
        "    tally(other, \"read@reach\", n);",      // a place that is not the counts
        "    tally(counts, \"read@reach\");",        // the wrong arity
        "    merge(&mut s.counts, &counts, 3);",
        "    tally(&mut 3, \"read@reach\", n);",
        "    merge(&mut s.counts, f());",
        "    counts.add(\"read@reach\", n, 1);",
        "    counts.adds(\"read@reach\", n);",
        "    other.add(\"read@reach\", n);",
        "    log(counts, \"read@reach\", n);", // not a counter function
        "    let t = tally(counts, \"read@reach\", n);", // not at a statement's start
        "    if n > 2 { tally(counts, \"read@reach\", n); }", // a new branch around it
        "    tally(counts, \"read@reach\", n)", // not ended by `;`
        "    tally(counts, \"read@reach\", (n", // never closed
        "    tally(counts, \"read@reach\", (n - 1));",
        "    tally(counts, \"read@reach\", n as);",
        "    tally(counts, \"read@reach\", n as u64 as);",
        "    tally(counts, \"read@reach\", );",
        "    tally(counts, \"read@reach\", n.len(1));",
        "    a::b;",
        "    x.0;",
        "    tally[0];",
        "    #[cfg(feature = \"counters\")]\n    let k = (1",
        "    #[cfg(feature = \"counters\")]\n    {",
        // a gated `for` or `if` ends at its block: the statement after it is code
        "    #[cfg(feature = \"counters\")]\n    for x in xs { counts.0.insert(x, 1); }\n    let n = n + 1;",
        "    #[cfg(feature = \"counters\")]\n    if n > 0 { eprintln!(\"{n}\"); }\n    #[cfg(not(feature = \"counters\"))]\n    let _ = n;",
    ] {
        assert!(!only(&with(added)), "{added}");
    }
    // a base counter removed, or rewritten
    assert!(!only(
        &BASE.replace("    tally(counts, \"read@reach\", n as u64);\n", "")
    ));
    assert!(!only(&BASE.replace("n as u64);", "n as u64 * 2);")));
    // the recorded version is not the base's; the unit gone from either side
    let u = unit(BASE);
    let claim = u.claims[0].clone();
    assert!(!counter_only(BASE, BASE, &u, &claim, Some("another")));
    assert!(!counter_only("pub fn other() {}\n", BASE, &u, &claim, None));
    assert!(!counter_only(BASE, "", &u, &claim, None));
}

fn index(root: &std::path::Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
        .unwrap()
}

/// The Python half's own clear, and a module unit's, are `commands::more`'s test; here a Rust claim is cleared, on a tree with no `.py`
/// file (no runner started). The rows are written as a check records them (their code the base's), so no bundle round is run.
#[test]
fn the_clear_records_a_rust_claim() {
    let root = fixture("claims-counters-rs");
    std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    let path = "rust/phases/src/lib.rs";
    let lib = std::fs::read_to_string(root.join(path)).unwrap();
    let counted = lib.replace(
        "    x + GAP + y\n",
        "    tally(counts, \"read@reach\", 2);\n    x + GAP + y\n",
    );
    put(&root, path, &counted);
    commit(&root, "a counter");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let mut idx = serde_json::Map::new();
    for u in rust_units(&counted, path).1 {
        for c in &u.claims {
            idx.insert(u.key(c), json!({"code": u.code(c), "verdict": "IN-STEP"}));
        }
    }
    put(
        &root,
        "dev/claims-index.json",
        &Value::Object(idx).to_string(),
    );
    let gained = counted.replace(
        "    x + GAP + y\n",
        "    tally(counts, \"test@reach\", y as u64);\n    x + GAP + y\n",
    );
    put(&root, path, &gained.replace("a[1] + 42", "a[1] + 43"));
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("claims-owed: 1 claim(s) cleared without a triage - their units only gained counter blocks"), "{}", got.stdout);
    let idx = index(&root);
    assert_eq!(
        idx["rust/phases/src/lib.rs::reach#reach"]["cleared"],
        "counter-only (feature 446)"
    );
    assert!(idx["rust/phases/src/lib.rs::Thing.m#method guess"]
        .get("cleared")
        .is_none());
    assert!(
        got.stdout
            .contains("code triage      rust/phases/src/lib.rs::Thing.m#method guess"),
        "{}",
        got.stdout
    );
}

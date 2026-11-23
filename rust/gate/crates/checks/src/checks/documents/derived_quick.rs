//! The derived files are checked by `make quick` (feature 451 T198; the GM 2026-11-23, "check whether there are any other gaps like
//! this"; the gap audit's item 10). `make done`'s preflight (`measure/src/preflight.rs`, `DERIVED`) regenerates each derived file and
//! names it to commit, but `make quick` and the closing checks did not look at two of them, so a stale `docs/building-programs.md` or
//! glossary passed every check a builder runs and cost a red `make done`, about an hour each time (372's wave 106 met
//! `building-programs.md` stale twice). So each derived target preflight regenerates has its `--check` line in `make quick`'s recipe,
//! which the closing checks run, and a new derived file added to preflight is red here until quick checks it.
//!
//! A stale file through each check fails naming its regenerate command, pinned in its own crate: `mode_a`'s
//! `programs/tests.rs` ("is STALE - run `make building-programs`"), `research`'s `tools/glossary/tests.rs` ("STALE against its
//! per-term files - run `make glossary`") and `cohort`'s `make_docs` tests ("run `make docs`").

use super::{re, read, root};

/// Each derived target preflight regenerates, and the line of `make quick` that checks it (each 0.05 to 0.11 s, measured 2026-11-23).
const CHECKED: [(&str, &str); 3] = [
    ("docs", "make-docs . --check"),
    ("building-programs", "mode-a building-programs --check"),
    ("glossary", "record check glossary"),
];

/// The recipe of `target:` in `makefile`: its tab-indented lines after the rule line, up to the first line that is not one.
fn recipe(makefile: &str, target: &str) -> String {
    let head = format!("{target}:");
    makefile
        .lines()
        .skip_while(|l| !l.starts_with(&head))
        .skip(1)
        .take_while(|l| l.starts_with('\t'))
        .collect::<Vec<_>>()
        .join("\n")
}

/// The names in preflight's `const DERIVED: [&str; N] = [...]`.
fn derived(preflight: &str) -> Vec<String> {
    let Ok(Some(c)) = re(r"const DERIVED: \[&str; \d+\] = \[([^\]]*)\]").captures(preflight) else {
        return Vec::new();
    };
    re(r#""([^"]+)""#)
        .captures_iter(&c[1])
        .map_while(Result::ok)
        .map(|n| n[1].to_owned())
        .collect()
}

/// Each problem with its fix: a derived target quick does not check, and one this table does not know.
fn problems(makefile: &str, preflight: &str) -> Vec<String> {
    let quick = recipe(makefile, "_quick");
    let mut out = Vec::new();
    for name in derived(preflight) {
        match CHECKED.iter().find(|(t, _)| *t == name) {
            None => out.push(format!(
                "preflight regenerates `make {name}` and make quick checks no such file - add its check line to `_quick:` in the Makefile and to CHECKED here"
            )),
            Some((_, line)) if !quick.contains(line) => out.push(format!(
                "make quick does not check `make {name}`'s file - add `\"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" {line}` to `_quick:` in the Makefile"
            )),
            Some(_) => {}
        }
    }
    if derived(preflight).is_empty() {
        out.push("no `const DERIVED` in measure/src/preflight.rs - update this test to where preflight lists its derived files".to_owned());
    }
    out
}

#[test]
fn make_quick_checks_every_derived_file_preflight_regenerates() {
    let r = root();
    let said = problems(
        &read(&r.join("Makefile")),
        &read(&r.join("rust/gate/crates/measure/src/preflight.rs")),
    );
    assert_eq!(said.join("\n"), "");
}

#[test]
fn a_missing_check_line_and_an_unknown_derived_target_are_named() {
    let pre = r#"const DERIVED: [&str; 2] = ["glossary", "footnote-census"];"#;
    let make =
        "_quick:\n\t@x record check glossary\n\nother:\n\t@x mode-a building-programs --check\n";
    assert_eq!(problems(make, pre).len(), 1);
    assert!(problems(make, pre)[0]
        .contains("`make footnote-census` and make quick checks no such file"));
    let make = "_quick:\n\t@x check file-scale .\n";
    let said = problems(make, pre).join("\n");
    assert!(said.contains("does not check `make glossary`'s file"));
    assert!(problems(make, "nothing")[0].contains("no `const DERIVED`"));
}

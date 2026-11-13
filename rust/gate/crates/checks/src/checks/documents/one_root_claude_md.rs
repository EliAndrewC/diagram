//! A session loads the project's root instructions once (feature 383 amendment 6, FR-037, plan D40) - the port of
//! `tests/test_one_root_claude_md.py` by feature 449 T133, `ask:449-phase3-remainder` Q3.
//!
//! The GM, 2026-10-17: a session started in the checkout that works in its clone loaded CLAUDE.md twice - the checkout's at launch and
//! the clone's own copy, ~9k tokens, when it first touched a file there. `claudeMdExcludes` skips the clone's copy and leaves its nested
//! files to load where they are needed (specs/383 research R15).

use super::super::rust_tooling::fnmatches;
use super::{read, root};

const CLONE_ROOT: &str = "/diagram/.clones/diagram-performance/CLAUDE.md";
const KEPT: [&str; 4] = [
    "/diagram/CLAUDE.md",
    "/diagram/.clones/x/tests/CLAUDE.md",
    "/diagram/.clones/x/l7r/diagram/CLAUDE.md",
    "/diagram/.clones/x/research/CLAUDE.md",
];

/// `claudeMdExcludes` of the settings, [] where it is absent.
fn excludes(settings: &str) -> Vec<String> {
    serde_json::from_str::<serde_json::Value>(settings)
        .ok()
        .and_then(|v| v.get("claudeMdExcludes").cloned())
        .and_then(|v| serde_json::from_value(v).ok())
        .unwrap_or_default()
}

/// A glob over absolute paths where `*` stays within one directory, as the settings' globs do: the same number of parts, each matched
/// by `fnmatch`.
fn matches(path: &str, pattern: &str) -> bool {
    let (parts, globs): (Vec<&str>, Vec<&str>) =
        (path.split('/').collect(), pattern.split('/').collect());
    parts.len() == globs.len() && parts.iter().zip(&globs).all(|(a, b)| fnmatches(a, b))
}

fn excluded(path: &str, excludes: &[String]) -> bool {
    excludes.iter().any(|p| matches(path, p))
}

fn problems(excludes: &[String]) -> Vec<String> {
    let mut out = Vec::new();
    if !excluded(CLONE_ROOT, excludes) {
        out.push("the clone's root CLAUDE.md loads beside the checkout's - add \"/diagram/.clones/*/CLAUDE.md\" to claudeMdExcludes in .claude/settings.json".to_owned());
    }
    out.extend(KEPT.iter().filter(|k| excluded(k, excludes)).map(|k| {
        format!("{k} is excluded, and only the clone's copy of the ROOT file is a duplicate - narrow claudeMdExcludes in .claude/settings.json")
    }));
    out
}

#[test]
fn the_clones_copy_of_the_root_claude_md_is_excluded_and_nothing_needed_once_is() {
    assert_eq!(
        problems(&excludes(&read(&root().join(".claude/settings.json")))),
        Vec::<String>::new()
    );
}

#[test]
fn a_seeded_exclusion_is_caught() {
    assert_eq!(excludes("{}"), Vec::<String>::new());
    assert_eq!(excludes("not json"), Vec::<String>::new());
    let real = excludes(r#"{"claudeMdExcludes": ["/diagram/.clones/*/CLAUDE.md"]}"#);
    assert_eq!(problems(&real), Vec::<String>::new());
    assert!(problems(&[])[0].starts_with("the clone's root CLAUDE.md loads beside"));
    let wide = [
        "/diagram/*.md".to_owned(),
        "/diagram/.clones/*/tests/CLAUDE.md".to_owned(),
    ];
    let got = problems(&wide);
    assert_eq!(got.len(), 3, "{got:?}");
    assert!(
        got[1].starts_with("/diagram/CLAUDE.md is excluded")
            && got[2].starts_with("/diagram/.clones/x/tests/CLAUDE.md is excluded")
    );
}

//! ONE FEATURE SET A LIBRARY IN EVERY TEST BUILD (feature 451 T325). The gate builds a crate's tests one manifest a call and the
//! coverage build with `-p` for the crates that owe it, and cargo unifies features over what one call selects: a feature a
//! dev-dependency turns on - `testkit` of `core`, `research`, `registry`, `owed` and `archive` - was on in one call and off in the
//! next, so the library and every crate above it was compiled again under another hash. After a touch of `core` the 28 gate
//! manifests' test builds ran rustc 75 times for 58 targets (measured 2026-11-26, `dev/measurements/2026-11-26/feature-unify/`).
//!
//! THE RULE: over the test build of every crate under `rust/` - the crate, what it names in `[dependencies]` and
//! `[dev-dependencies]`, and what those name in `[dependencies]`, a feature turning on what its `[features]` line lists - a
//! workspace crate gets the SAME features whichever crate is the root. A root that gets fewer is told the line to add to its
//! `[dev-dependencies]`; a crate that is the root itself names itself there (`path = "."`), which cargo allows of a
//! dev-dependency. A production build reads no `[dev-dependencies]`, so the lines change nothing the tools compile in.
//!
//! This reads the manifests as cargo's feature resolver (version 2) does for the forms the workspace writes - a path dependency
//! on one line, `name = { path = "..", features = [".."] }`. What it cannot see (a feature named on the command line, as
//! `counters` is) it does not judge.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use super::{manifests, uncommented};

/// A feature that is NOT one set across the workspace, on purpose: the crate, the feature, and the directory whose crates alone are
/// held to it. `l7r_shared`'s `test-env` makes `env` read a test thread's own map (feature 451 T32, T58): the guard's tests need
/// it, and a gate crate's tests read the process's environment, so only the guard's family is held to one set.
const APART: [(&str, &str, &str); 1] = [("l7r_shared", "test-env", "rust/guard")];

/// What a manifest says of its crate.
#[derive(Default)]
struct Crate {
    name: String,
    /// Each feature with what it turns on.
    features: BTreeMap<String, Vec<String>>,
    /// Each path dependency: its directory, the features named, and whether it is a dev-dependency.
    deps: Vec<(String, Vec<String>, bool)>,
}

/// The quoted words of `list`.
fn quoted(list: &str) -> Vec<String> {
    list.split('"')
        .skip(1)
        .step_by(2)
        .map(str::to_owned)
        .collect()
}

/// `path` from the directory `dir`, its `.` and `..` resolved.
fn joined(dir: &str, path: &str) -> String {
    let mut parts: Vec<&str> = dir.split('/').collect();
    for part in path.split('/') {
        match part {
            ".." => {
                parts.pop();
            }
            "." => {}
            _ => parts.push(part),
        }
    }
    parts.join("/")
}

/// The directory `to` as a manifest in the directory `from` names it.
fn relative(from: &str, to: &str) -> String {
    let (a, b): (Vec<&str>, Vec<&str>) = (from.split('/').collect(), to.split('/').collect());
    let same = a.iter().zip(&b).take_while(|(x, y)| x == y).count();
    let mut parts = vec![".."; a.len() - same];
    parts.extend(&b[same..]);
    if parts.is_empty() {
        return ".".to_owned();
    }
    parts.join("/")
}

/// The crate of the manifest `text`, which stands in the directory `dir`.
fn parse(dir: &str, text: &str) -> Crate {
    let mut out = Crate::default();
    let mut section = "";
    for raw in text.lines() {
        let line = uncommented(raw).trim();
        if line.starts_with('[') {
            section = line;
        }
        let Some((key, value)) = line.split_once('=') else {
            continue;
        };
        let (key, value) = (key.trim(), value.trim());
        match section {
            "[package]" if key == "name" => out.name = quoted(value).concat(),
            "[features]" => {
                out.features.insert(key.to_owned(), quoted(value));
            }
            "[dependencies]" | "[dev-dependencies]" => {
                let path = value
                    .split_once("path = \"")
                    .and_then(|(_, rest)| rest.split_once('"'));
                let Some((path, _)) = path else {
                    continue;
                };
                let features = value
                    .split_once("features = [")
                    .and_then(|(_, rest)| rest.split_once(']'))
                    .map_or(Vec::new(), |(list, _)| quoted(list));
                let dev = section == "[dev-dependencies]";
                out.deps.push((joined(dir, path), features, dev));
            }
            _ => {}
        }
    }
    out
}

/// Every crate under `root/rust`, by its directory.
fn read_all(root: &Path) -> BTreeMap<String, Crate> {
    let mut found = Vec::new();
    manifests(&root.join("rust"), &mut found);
    let mut out = BTreeMap::new();
    for manifest in &found {
        let dir = manifest.parent().unwrap().strip_prefix(root).unwrap();
        let dir = dir.display().to_string();
        let krate = parse(&dir, &std::fs::read_to_string(manifest).unwrap());
        // the workspace's own manifest is no crate
        if !krate.name.is_empty() {
            out.insert(dir, krate);
        }
    }
    out
}

/// The features each crate is compiled with in the test build of the crate at `root`: a dev-dependency counts for the root alone.
fn resolved(crates: &BTreeMap<String, Crate>, root: &str) -> BTreeMap<String, BTreeSet<String>> {
    let mut on: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut walked = BTreeSet::new();
    let mut todo: Vec<(String, Option<String>)> = vec![(root.to_owned(), None)];
    while let Some((dir, feature)) = todo.pop() {
        let Some(krate) = crates.get(&dir) else {
            continue;
        };
        let Some(feature) = feature else {
            if walked.insert(dir.clone()) {
                on.entry(dir.clone()).or_default();
                for (to, features, _) in krate.deps.iter().filter(|d| !d.2 || dir == root) {
                    todo.push((to.clone(), None));
                    todo.extend(features.iter().map(|f| (to.clone(), Some(f.clone()))));
                }
            }
            continue;
        };
        if on.entry(dir.clone()).or_default().insert(feature.clone()) {
            for turned in krate.features.get(&feature).into_iter().flatten() {
                let (to, turned) = match turned.split_once('/') {
                    // a dependency's feature, the dependency named as its package
                    Some((name, its)) => (crates.iter().find(|(_, c)| c.name == name), its),
                    None => (crates.get_key_value(&dir), turned.as_str()),
                };
                todo.extend(to.map(|(d, _)| (d.clone(), Some(turned.to_owned()))));
            }
        }
    }
    on
}

/// Each root whose test build compiles a crate with fewer features than another root's does, with the line that mends it.
fn problems(crates: &BTreeMap<String, Crate>) -> Vec<String> {
    let each: Vec<_> = crates.keys().map(|r| (r, resolved(crates, r))).collect();
    let mut most: BTreeMap<&String, BTreeSet<&String>> = BTreeMap::new();
    for (dir, features) in each.iter().flat_map(|(_, got)| got) {
        most.entry(dir).or_default().extend(features);
    }
    let mut out = Vec::new();
    for (root, got) in &each {
        for (dir, features) in got {
            let name = &crates[dir].name;
            let held = |f: &&&String| {
                !features.contains(**f)
                    && !APART
                        .iter()
                        .any(|(n, a, under)| n == name && a == **f && !root.starts_with(under))
            };
            for feature in most[dir].iter().filter(held) {
                out.push(format!(
                    "{root}/Cargo.toml: its test build compiles {name} without `{feature}`, and another crate's compiles it with - add \
                     `{name} = {{ path = \"{}\", features = [\"{feature}\"] }}` to its [dev-dependencies], so the library is built \
                     once for both (one feature set a library in every test and coverage build, feature 451 T325)",
                    relative(root, dir)
                ));
            }
        }
    }
    out
}

#[test]
fn every_test_build_under_rust_compiles_a_library_with_one_feature_set() {
    let real = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let crates = read_all(&real.canonicalize().unwrap());
    assert!(crates.len() > 30);
    assert_eq!(problems(&crates), Vec::<String>::new());
}

/// A workspace of four: `low` and `mid` carry a test-only feature, `top` turns `mid`'s on, `other` does not.
fn seeded() -> BTreeMap<String, Crate> {
    let low = "[package]\nname = \"low\" # the base\n\n[features]\nkit = []\n";
    let mid = "[package]\nname = \"mid\"\n[features]\nkit = [\"low/kit\", \"more\", \"gone/kit\"]\nmore = []\n[dependencies]\n\
               serde = { workspace = true }\nlow = { path = \"../low\" }\n[dev-dependencies]\nfar = { path = \"../far\", features = [\"kit\"] }\n";
    let top = "[package]\nname = \"top\"\n[dependencies]\nmid = { path = \"../mid\" }\nout = { path = \"../../out\" }\n\
               [dev-dependencies]\nmid = { path = \"./../mid\", features = [\"kit\"] }\n[[bin]]\npath = \"src/main.rs\"\n";
    let other = "[package]\nname = \"other\"\n[dependencies]\nmid = { path = \"../../x/mid\" }\n";
    let far = "[package]\nname = \"far\"\n[features]\nkit = []\n";
    [
        ("rust/x/low", low),
        ("rust/x/mid", mid),
        ("rust/x/top", top),
        ("rust/y/other", other),
        ("rust/x/far", far),
    ]
    .into_iter()
    .map(|(dir, text)| (dir.to_owned(), parse(dir, text)))
    .collect()
}

#[test]
fn a_root_that_gets_fewer_features_is_told_its_line() {
    let mut crates = seeded();
    let top = resolved(&crates, "rust/x/top");
    let on = |dir: &str| top[dir].iter().map(String::as_str).collect::<Vec<_>>();
    // a feature turns on its own and its dependency's; a dev-dependency below the root (`far`) and a path outside are not followed
    assert_eq!(on("rust/x/mid"), ["kit", "more"]);
    assert_eq!(on("rust/x/low"), ["kit"]);
    assert_eq!(top.len(), 3);
    let got = problems(&crates);
    assert_eq!(got.len(), 8, "{got:#?}");
    let line = "rust/y/other/Cargo.toml: its test build compiles low without `kit`, and another crate's compiles it with - add `low = \
                { path = \"../../x/low\", features = [\"kit\"] }` to its [dev-dependencies], so the library is built once for both (one \
                feature set a library in every test and coverage build, feature 451 T325)";
    assert!(got.iter().any(|p| p == line), "{got:#?}");
    // the crate that is the root names itself
    assert!(got.iter().any(|p| p.starts_with("rust/x/low/Cargo.toml:")
        && p.contains("`low = { path = \".\", features = [\"kit\"] }`")));
    assert!(got.iter().any(|p| p.starts_with("rust/x/far/Cargo.toml:")));
    assert!(!got.iter().any(|p| p.starts_with("rust/x/top/Cargo.toml:")));
    for (dir, line) in [
        ("rust/x/low", "low = { path = \".\", features = [\"kit\"] }"),
        ("rust/x/far", "far = { path = \".\", features = [\"kit\"] }"),
        ("rust/x/mid", "mid = { path = \".\", features = [\"kit\"] }"),
        (
            "rust/y/other",
            "mid = { path = \"../../x/mid\", features = [\"kit\"] }",
        ),
    ] {
        let krate = parse(dir, &format!("[dev-dependencies]\n{line}\n"));
        crates.get_mut(dir).unwrap().deps.extend(krate.deps);
    }
    assert_eq!(problems(&crates), Vec::<String>::new());
}

#[test]
fn a_feature_held_apart_is_one_set_in_its_own_family_alone() {
    let shared = "[package]\nname = \"l7r_shared\"\n[features]\ntest-env = []\n";
    let guard = "[package]\nname = \"l7r_guard\"\n[dev-dependencies]\nl7r_shared = { path = \"shared\", features = [\"test-env\"] }\n";
    let gate = "[package]\nname = \"l7r_gate\"\n[dependencies]\nl7r_shared = { path = \"../guard/shared\" }\n";
    let crates: BTreeMap<String, Crate> = [
        ("rust/guard/shared", shared),
        ("rust/guard", guard),
        ("rust/gate", gate),
    ]
    .into_iter()
    .map(|(dir, text)| (dir.to_owned(), parse(dir, text)))
    .collect();
    let got = problems(&crates);
    assert_eq!(got.len(), 1, "{got:#?}");
    assert!(got[0].starts_with(
        "rust/guard/shared/Cargo.toml: its test build compiles l7r_shared without `test-env`"
    ));
}

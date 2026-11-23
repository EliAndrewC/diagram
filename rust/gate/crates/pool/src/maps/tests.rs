use std::path::Path;

use super::{cli, read, run, state_file, Judge, Launch, Launcher, Row, Scope, TIERS};
use crate::walk::tests::{fixture, put};

/// The fixture's table: a hamlet row (reference `a`) and a Mode A row (reference `c`, a generated compound; `h` a hand sheet).
const ROWS: &[Row] = &[
    Row {
        name: "hamlets",
        folders: &["hamlets"],
        reference: "a",
        judge: Judge::Hamlet,
    },
    Row {
        name: "mode-a",
        folders: &["magistracies", "country-shrines"],
        reference: "c",
        judge: Judge::ModeA,
    },
];

/// A launcher stand-in: each command line it was handed, and a failure wherever one of `failing` is among its words.
#[derive(Default)]
struct Fake {
    ran: Vec<String>,
    failing: Vec<&'static str>,
}

impl Launch for Fake {
    fn run(&mut self, args: &[String]) -> (bool, String) {
        let line = args.join(" ");
        let ok = !self.failing.iter().any(|f| line.contains(f));
        self.ran.push(line.clone());
        (ok, format!("ran {line}\n"))
    }
}

fn git(root: &Path) {
    std::fs::create_dir_all(root.join(".git")).unwrap();
}

/// No last run is a failed one: each row's reference map drawn and judged first; the first problem stops the run there, and the
/// record says it failed on it.
#[test]
fn with_no_last_run_the_reference_maps_go_first_and_the_first_problem_stops_it() {
    let root = fixture("maps-first");
    git(&root);
    let mut f = Fake {
        failing: vec!["--check"],
        ..Fake::default()
    };
    let (out, _, code) = run(&root, ROWS, Scope::Auto, None, &mut f);
    assert_eq!(code, 1);
    assert_eq!(f.ran.len(), 2);
    assert_eq!(f.ran[0], "pool map pool/hamlets/a");
    assert!(f.ran[1].starts_with("hamlet --check "));
    assert!(out.starts_with(
        "make maps: no last run -> the reference maps first, stopping at the first problem"
    ));
    let last = read(&root).unwrap();
    assert_eq!((last.ok, last.scope.as_str()), (false, "reference"));
    assert_eq!(last.failed, vec!["hamlets: a judged".to_owned()]);
}

/// A clean reference run widens in the same run: every row's whole run follows, the reference first in each.
#[test]
fn a_clean_reference_run_widens_to_every_tier() {
    let root = fixture("maps-widen");
    git(&root);
    let mut f = Fake::default();
    let (out, _, code) = run(&root, ROWS, Scope::Auto, None, &mut f);
    assert_eq!(code, 0);
    assert_eq!(
        f.ran,
        vec![
            "pool map pool/hamlets/a".to_owned(),
            format!(
                "hamlet --check {}",
                root.join("pool/hamlets/a/a.spec.json").display()
            ),
            "pool map pool/magistracies/c".to_owned(),
            "mode-a sweep pool/magistracies/c".to_owned(),
            "pool map pool/hamlets/a".to_owned(),
            format!(
                "hamlet --check {}",
                root.join("pool/hamlets/a/a.spec.json").display()
            ),
            "hamlet --cohort 1 48".to_owned(),
            "pool map pool/magistracies/c pool/magistracies/h".to_owned(),
            "rust test --crate rust/mode_a".to_owned(),
        ]
    );
    assert!(out.contains("the reference maps are clean - widening"));
    let last = read(&root).unwrap();
    assert_eq!((last.ok, last.scope.as_str()), (true, "all"));
}

/// After a pass the whole of every tier runs, and every failure is reported together rather than the first stopping it.
#[test]
fn after_a_pass_every_tier_runs_whole_and_every_failure_is_reported() {
    let root = fixture("maps-wide");
    git(&root);
    let first = run(&root, ROWS, Scope::Auto, None, &mut Fake::default());
    assert_eq!(first.2, 0);
    let mut f = Fake {
        failing: vec!["--cohort", "rust test"],
        ..Fake::default()
    };
    let (out, _, code) = run(&root, ROWS, Scope::Auto, None, &mut f);
    assert_eq!(code, 1);
    assert!(
        out.starts_with("make maps: last run PASSED -> every tier whole, reporting every failure")
    );
    assert_eq!(f.ran.len(), 5);
    let last = read(&root).unwrap();
    assert_eq!(
        last.failed,
        vec![
            "hamlets: the cohort, 48 seeds".to_owned(),
            "mode-a: the crate's tests and the pool sweep".to_owned()
        ]
    );
    // the failure is read back: the next run is narrow again
    let mut f = Fake::default();
    let (out, _, _) = run(&root, ROWS, Scope::Auto, None, &mut f);
    assert!(out.starts_with("make maps: last run FAILED on hamlets: the cohort, 48 seeds, mode-a: the crate's tests and the pool sweep -> the reference maps first"));
}

/// SCOPE= says what is meant: `reference` after a pass runs the reference maps alone and widens nothing; `all` after a failure runs
/// every tier whole, stopping at nothing.
#[test]
fn scope_says_what_is_meant() {
    let root = fixture("maps-scope");
    git(&root);
    let first = run(&root, ROWS, Scope::Auto, None, &mut Fake::default());
    assert_eq!(first.2, 0);
    let mut f = Fake::default();
    let (out, _, code) = run(&root, ROWS, Scope::Reference, None, &mut f);
    assert_eq!((code, f.ran.len()), (0, 4));
    assert!(out.starts_with("make maps: SCOPE=reference -> the reference maps alone"));
    assert_eq!(read(&root).unwrap().scope, "reference");
    let mut f = Fake {
        failing: vec!["pool map"],
        ..Fake::default()
    };
    let (out, _, code) = run(&root, ROWS, Scope::All, None, &mut f);
    assert_eq!((code, f.ran.len()), (1, 5));
    assert!(out.starts_with("make maps: SCOPE=all -> every tier whole"));
}

/// TIER= runs its row alone; a tier no row names is refused with the rows' names.
#[test]
fn tier_runs_its_row_alone() {
    let root = fixture("maps-tier");
    git(&root);
    let mut f = Fake::default();
    let (_, _, code) = run(&root, ROWS, Scope::Reference, Some("mode-a"), &mut f);
    assert_eq!((code, f.ran.len()), (0, 2));
    assert!(f.ran.iter().all(|l| l.contains("magistracies")));
    let (_, err, code) = run(
        &root,
        ROWS,
        Scope::Auto,
        Some("villages"),
        &mut Fake::default(),
    );
    assert_eq!(code, 2);
    assert!(err.contains("no tier row villages - the rows: hamlets, mode-a"));
}

/// A reference map the walk does not find live in its row's folders is the row's first problem, named with the fix.
#[test]
fn a_missing_reference_map_is_a_problem() {
    let root = fixture("maps-missing");
    git(&root);
    let rows = [Row {
        name: "hamlets",
        folders: &["hamlets"],
        reference: "gone",
        judge: Judge::Hamlet,
    }];
    let mut f = Fake::default();
    let (out, _, code) = run(&root, &rows, Scope::Auto, None, &mut f);
    assert_eq!((code, f.ran.len()), (1, 0));
    assert!(out.contains("hamlets: the reference map gone is no live map of pool/hamlets"));
    let (out, _, code) = run(&root, &rows, Scope::All, None, &mut f);
    assert_eq!(code, 1);
    assert!(out.contains("hamlets: the reference map gone is no live map"));
}

/// A worktree's `.git` names its own git directory, and the record goes there; a record that does not read is no last run.
#[test]
fn the_record_is_the_checkouts_own() {
    let root = fixture("maps-worktree");
    put(&root, ".git", "gitdir: gd\n");
    std::fs::create_dir_all(root.join("gd")).unwrap();
    assert_eq!(state_file(&root), root.join("gd").join("maps-state.json"));
    let first = run(&root, ROWS, Scope::Reference, None, &mut Fake::default());
    assert_eq!(first.2, 0);
    assert!(root.join("gd/maps-state.json").is_file());
    std::fs::write(root.join("gd/maps-state.json"), "not json").unwrap();
    assert!(read(&root).is_none());
    // a record that cannot be written is said, never a pass taken for recorded
    std::fs::remove_dir_all(root.join("gd")).unwrap();
    let (_, err, code) = run(&root, ROWS, Scope::Reference, None, &mut Fake::default());
    assert_eq!(code, 1);
    assert!(err.contains("make maps: the run's record could not be written"));
}

/// The command line: the scope and tier read; anything else is the usage, exit 2.
#[test]
fn the_command_line() {
    let root = fixture("maps-cli");
    for bad in [&["--scope", "most"][..], &["--tier"], &["stray"]] {
        let (_, err, code) = cli(&root, bad);
        assert_eq!((code, err.as_str()), (2, super::USAGE));
    }
    // the real table's references, and no launcher in the fixture: every step fails to start, and the run says so
    git(&root);
    put(&root, "pool/hamlets/inashiro/inashiro.spec.json", "{}");
    put(
        &root,
        "pool/magistracies/county-magistracy-example/county-magistracy-example.compound.json",
        "{}",
    );
    let (out, _, code) = cli(&root, &["--scope", "reference", "--tier", "hamlets"]);
    assert_eq!(code, 1);
    assert!(out.contains("did not start"));
    let (_, _, code) = cli(&root, &["--scope", "all", "--tier", "mode-a"]);
    assert_eq!(code, 1);
    let (_, _, code) = cli(&root, &["--scope", "auto"]);
    assert_eq!(code, 1);
}

/// The launcher runs `scripts/gates/l7r-gate.sh` with the words, from the root, its output and its exit kept.
#[test]
fn the_launcher_runs_the_gate_script() {
    let root = fixture("maps-launcher");
    // written by `install`, never this process: a script it wrote itself failed "Text file busy" under load (451 T160)
    let script = root.join("scripts/gates/l7r-gate.sh");
    std::fs::create_dir_all(script.parent().unwrap()).unwrap();
    l7r_gate_core::write_executable(
        &script,
        "#!/bin/sh\necho \"said $*\"; echo err >&2; [ \"$1\" = ok ]\n",
    );
    let mut l = Launcher {
        root: root.to_path_buf(),
    };
    assert_eq!(
        l.run(&["ok".to_owned(), "x".to_owned()]),
        (true, "said ok x\nerr\n".to_owned())
    );
    assert!(!l.run(&["no".to_owned()]).0);
}

/// The real table: every row's reference is a live map in one of its folders, and every Mode A tier the building types declare with a
/// pool folder is some row's - a renamed reference, or a new tier with no row, goes red here.
#[test]
fn the_real_table_names_live_maps_and_covers_every_tier() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let w = crate::walk(&root);
    for row in TIERS {
        let found = w
            .in_tree(crate::LIVE)
            .find(|m| m.name == row.reference && m.kind.is_live());
        assert!(found.is_some_and(|m| row.folders.contains(&m.tier.as_str())));
    }
    let text = std::fs::read_to_string(root.join(crate::DECLARATION)).unwrap();
    let types: serde_json::Value = serde_json::from_str(&text).unwrap();
    let rowed: Vec<&str> = TIERS
        .iter()
        .flat_map(|r| r.folders.iter().copied())
        .collect();
    let unrowed: Vec<&str> = types
        .as_array()
        .unwrap()
        .iter()
        .filter_map(|t| t.get("tier").and_then(serde_json::Value::as_str))
        .filter(|t| root.join("pool").join(t).is_dir() && !rowed.contains(t))
        .collect();
    assert_eq!(unrowed, Vec::<&str>::new());
    assert!(rowed.contains(&"hamlets"));
}

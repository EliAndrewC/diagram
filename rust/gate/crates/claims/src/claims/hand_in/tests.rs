//! 461 T38 and T40 on a phase-1 hand-in's tree: every claim recorded on `origin/main`, another task's staged batch committed above it
//! (the hand-in's base, the clone's HEAD), and the builder's work applied on that base uncommitted.

use std::path::Path;

use crate::claims::carry::touches_engine;
use crate::claims::report::delta_form_problems;
use crate::claims::tests::{claims, commit_as_origin, fixture, record_all};
use crate::claims::units::Unit;
use crate::record::testkit::{commit, git, put};

const LIB: &str = "rust/phases/src/lib.rs";
const METHOD: &str = "rust/phases/src/lib.rs::Thing.m#method guess";
const REACH: &str = "rust/phases/src/lib.rs::reach#reach";

fn edit(root: &Path, from: &str, to: &str) {
    let text = std::fs::read_to_string(root.join(LIB)).unwrap();
    assert!(text.contains(from));
    put(root, LIB, &text.replace(from, to));
}

/// The tree: `Thing.m`'s code changed by another task's staged batch (its claim owed), `reach`'s by the work; the tree's root and the
/// hand-in base.
fn staged_below(tag: &str) -> (l7r_shared::tempdir::TempDir, String) {
    let root = fixture(tag);
    record_all(&root);
    commit_as_origin(&root, "recorded");
    edit(&root, "a[1] + 42", "a[1] + 43");
    commit(&root, "another task's staged batch");
    let base = git(&root, &["rev-parse", "HEAD"]).trim().to_owned();
    edit(&root, "x + GAP + y", "x + GAP + y * 1.0");
    (root, base)
}

/// What `claims gate` refuses, given `top` (`--delta-base=...`, or nothing: a call that gives none).
fn refused(root: &Path, top: &[&str]) -> (Vec<String>, String) {
    let mut args = top.to_vec();
    args.push("gate");
    let out = claims(root, &args).stdout;
    let lines = out
        .lines()
        .filter_map(|l| l.strip_prefix("claims-gate: REFUSED owed ("))
        .map(|l| l.split_once("): ").unwrap().1.to_owned())
        .collect();
    (lines, out)
}

/// T40's red-first: a claim owed by other staged work is quiet at hand-in and said as the landing's, one the delta touches refused there,
/// and the first refused at a landing - which gives no base, an empty one, or one that names no commit (bound 2).
#[test]
fn at_a_hand_in_only_the_claims_its_work_touches_are_refused_owed() {
    let (root, base) = staged_below("claims-hand-in-owed");
    let given = format!("--delta-base={base}");
    let (owed, out) = refused(&root, &[&given]);
    assert_eq!(owed, vec![REACH.to_owned()], "{out}");
    let lane = format!("claims-gate: pre-existing: owed below the hand-in base, the landing's to ask (461 T40; code triage): {METHOD}");
    assert!(out.contains(&lane), "{out}");
    assert!(!out.contains("pre-existing: owed ("), "{out}");
    for top in [&[][..], &["--delta-base="], &["--delta-base=no-such-rev"]] {
        let (owed, out) = refused(&root, top);
        assert_eq!(owed, vec![METHOD.to_owned(), REACH.to_owned()], "{out}");
    }
}

/// Bound 1: a claim owed at the base that the work touches again is the builder's - and so is one the work adds.
#[test]
fn a_claim_owed_at_the_base_and_touched_by_the_work_is_the_builder_s() {
    let (root, base) = staged_below("claims-hand-in-touched");
    edit(&root, "a[1] + 43", "a[1] + 44");
    edit(
        &root,
        "pub fn helper() -> u32 {",
        "/// Research: helped - GUESS: one\npub fn helper() -> u32 {",
    );
    let (owed, out) = refused(&root, &[&format!("--delta-base={base}")]);
    let all = [METHOD, "rust/phases/src/lib.rs::helper#helped", REACH].map(str::to_owned);
    assert_eq!(owed, all, "{out}");
}

/// T38's red-first: from the base a hand-in names, another task's staged engine code is not the work's (the carry's target), and a form
/// problem is the work's own file's, not the staged batch's.
#[test]
fn at_a_hand_in_the_engine_and_the_form_problems_are_the_work_s() {
    let root = fixture("claims-hand-in-delta");
    edit(&root, "a[1] + 42", "a[1] + 43");
    put(&root, "a.rs", "x\n");
    commit(&root, "another task's staged batch");
    let base = git(&root, &["rev-parse", "HEAD"]).trim().to_owned();
    put(&root, "b.rs", "x\n");
    let at = |f: &dyn Fn() -> bool| l7r_gate_core::delta_base::with(&base, f);
    assert!(touches_engine(&root));
    assert!(!at(&|| touches_engine(&root)));
    let bad = |path: &str| Unit {
        path: path.into(),
        qualname: "a".into(),
        kind: "function".into(),
        lineno: 1,
        end_lineno: 1,
        claims: Vec::new(),
        inherited: false,
        core: String::new(),
        errors: vec!["bad".into()],
        names: Vec::new(),
        blocks: Vec::new(),
        reads: String::new(),
    };
    let pairs = vec![(bad("a.rs"), Vec::new()), (bad("b.rs"), Vec::new())];
    let file = |p: &[String]| p.iter().map(|x| x[..4].to_owned()).collect::<Vec<_>>();
    assert_eq!(file(&delta_form_problems(&root, &pairs)), ["a.rs"]);
    let work = l7r_gate_core::delta_base::with(&base, || delta_form_problems(&root, &pairs));
    assert_eq!(file(&work), ["b.rs"]);
}

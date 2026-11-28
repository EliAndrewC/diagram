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

/// A section's `fix: code` drift owed because the engine moved (451 T220): the landing's where the work leaves the engine as the base
/// held it, the builder's where the work moved it; the engine is compared once for every such claim, and a claim owed for another
/// reason is split without it.
#[test]
fn a_claim_owed_because_the_engine_moved_is_the_builder_s_only_where_the_work_moved_it() {
    use std::rc::Rc;

    use super::{split, Base};
    use crate::claims::drawn::DRAWN;
    use crate::claims::grammar::parse_claim;
    use crate::claims::index::{Cur, Index, Row};

    let claim = parse_claim("porch - GUESS: drawn 8 by 6 ft").unwrap();
    let unit = Unit {
        path: "docs/buildings.md".into(),
        qualname: "Genkan".into(),
        kind: "section".into(),
        lineno: 1,
        end_lineno: 2,
        claims: Vec::new(),
        inherited: false,
        core: "core".into(),
        errors: Vec::new(),
        names: Vec::new(),
        blocks: Vec::new(),
        reads: String::new(),
    };
    let mut cur = Cur::default();
    for key in [
        "docs/buildings.md::Genkan#porch",
        "docs/buildings.md::Genkan#other",
    ] {
        cur.insert(Row {
            key: key.into(),
            code: unit.code(&claim),
            unit: Rc::new(unit.clone()),
            claim: claim.clone(),
            research: String::new(),
        });
    }
    let index = Index::new();
    let tree = |tag: &str, genkan: &str| {
        let root = crate::checks::scratch(tag);
        put(
            &root,
            "rust/mode_a/src/compound/layout.rs",
            &format!("const GENKAN: (f64, f64) = {genkan};\n"),
        );
        root
    };
    let at_base = tree("claims-hand-in-drawn-base", "(8.0, 6.0)");
    let base = Base {
        rows: &cur,
        index: &index,
        tree: &at_base,
    };
    let due = || {
        vec![
            (
                "docs/buildings.md::Genkan#porch".to_owned(),
                DRAWN.to_owned(),
            ),
            (
                "docs/buildings.md::Genkan#other".to_owned(),
                DRAWN.to_owned(),
            ),
            (
                "docs/buildings.md::Genkan#gone".to_owned(),
                "code changed".to_owned(),
            ),
        ]
    };
    let gone = vec![due().remove(2)];
    let kept = tree("claims-hand-in-drawn-kept", "(8.0, 6.0)");
    assert_eq!(
        split(&kept, due(), &cur, &index, &base),
        (gone.clone(), due()[..2].to_vec())
    );
    let moved = tree("claims-hand-in-drawn-moved", "(12.0, 9.0)");
    assert_eq!(
        split(&moved, due(), &cur, &index, &base),
        (due(), Vec::new())
    );
}

const BOUND_ONE: &str = "rust/phases/src/lib.rs::reach#reach";

/// What a case of bound 1 changes of the claim's row and its unit.
type Edit = fn(&mut crate::claims::index::Row, &mut Unit);

/// The claim of [`a_claim_the_work_moves_in_any_one_thing_an_owed_reason_reads_is_the_builder_s`] as the base held it, `edit` applied.
fn reach_row(edit: Edit) -> crate::claims::index::Row {
    use crate::claims::grammar::parse_claim;

    let claim = parse_claim("reach - GUESS: within the gap").unwrap();
    let mut unit = Unit {
        path: "rust/phases/src/lib.rs".into(),
        qualname: "reach".into(),
        kind: "function".into(),
        lineno: 1,
        end_lineno: 2,
        claims: vec![claim.clone()],
        inherited: false,
        core: "core".into(),
        errors: Vec::new(),
        names: Vec::new(),
        blocks: Vec::new(),
        reads: "GAP".into(),
    };
    let mut row = crate::claims::index::Row {
        key: BOUND_ONE.into(),
        code: "code".into(),
        unit: std::rc::Rc::new(unit.clone()),
        claim,
        research: "research".into(),
    };
    edit(&mut row, &mut unit);
    row.unit = std::rc::Rc::new(unit);
    row
}

/// Bound 1, field by field (461 T40): a claim owed at the base is the landing's only where the work leaves it as the base held it in
/// everything an owed reason reads - its code, its claim's text, its research, its unit's constant reads, its unit's other claims and
/// its index row; the work moving any one of them makes it the builder's.
#[test]
fn a_claim_the_work_moves_in_any_one_thing_an_owed_reason_reads_is_the_builder_s() {
    use super::{split, Base};
    use crate::claims::grammar::parse_claim;
    use crate::claims::index::{Cur, Index, Row};

    let one = |r: Row| {
        let mut cur = Cur::default();
        cur.insert(r);
        cur
    };
    let indexed = |code: &str| {
        let mut index = Index::new();
        index.insert(BOUND_ONE.into(), serde_json::json!({ "code": code }));
        index
    };
    let (at_base, base_index) = (one(reach_row(|_, _| {})), indexed("code"));
    let nowhere = Path::new("/nonexistent");
    let base = Base {
        rows: &at_base,
        index: &base_index,
        tree: nowhere,
    };
    let due = vec![(BOUND_ONE.to_owned(), "code triage".to_owned())];
    let builders = (due.clone(), Vec::new());
    let moved: [(&str, Edit); 5] = [
        ("code", |r, _| r.code = "code moved".into()),
        ("claim text", |r, _| {
            r.claim = parse_claim("reach - GUESS: past the gap").unwrap();
        }),
        ("research", |r, _| r.research = "research moved".into()),
        ("constant reads", |_, u| u.reads = "GAP, FAR".into()),
        ("other claims", |_, u| {
            u.claims.push(parse_claim("far - GUESS: one").unwrap());
        }),
    ];
    for (what, edit) in moved {
        let now = one(reach_row(edit));
        let got = split(nowhere, due.clone(), &now, &base_index, &base);
        assert_eq!(got, builders, "{what}");
    }
    let now = one(reach_row(|_, _| {}));
    let answered = indexed("answered");
    assert_eq!(
        split(nowhere, due.clone(), &now, &answered, &base),
        builders
    );
    assert_eq!(
        split(nowhere, due.clone(), &now, &base_index, &base),
        (Vec::new(), due)
    );
}

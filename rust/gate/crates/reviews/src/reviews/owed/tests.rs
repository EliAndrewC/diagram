//! What a delta owes, on scratch repositories: detected occasions, declared ones, the dedupe, the refusal for undeclared code, the
//! command line.

use std::path::Path;

use serde_json::json;

use super::super::tests::{commit, events, feature, map, put, repo, sh, sheet};
use super::*;

fn slugs(units: &[Unit]) -> Vec<String> {
    units.iter().map(Unit::slug).collect()
}

fn owed_slugs(root: &Path) -> Vec<String> {
    slugs(&all_owed(root).1)
}

fn cli_in(root: &Path, extra: &[&str]) -> Reply {
    let mut a = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    a.extend(extra.iter().map(|s| (*s).to_owned()));
    cli(&a)
}

#[test]
fn a_slug_is_file_safe_and_a_glyph_unit_names_its_map() {
    let u = Unit::new(
        "glyph-check",
        "Village Lane!",
        "Ochiba Magistracy",
        String::new(),
    );
    assert_eq!(u.slug(), "glyph-check--village-lane--ochiba-magistracy");
    // no copy anywhere: every kind is new
    // 901 is still touched and changed by the delta
    assert_eq!(
        Unit::new("glyph-check", "x", "", String::new()).slug(),
        "glyph-check--x"
    );
    assert_eq!(
        Unit::new("size-audit", "--a--b--", "m", String::new()).slug(),
        "size-audit--a-b"
    );
}

#[test]
fn the_base_is_the_merge_base_else_head_else_nothing() {
    let empty = super::super::tests::dir("unborn");
    sh(&empty, "git init -q");
    assert_eq!(
        base_of(&empty),
        (String::new(), "no commits yet".to_owned())
    );
    // with no base, every folder is new, every declared line owed, and untracked code needs declaring
    put(&empty, "l7r/diagram/x.py", "x\n");
    assert!(check_declared(&empty).is_some());
    feature(&empty, "900-x", "- [ ] T1\n\n## Occasions\n\n- gm-fix: m\n");
    assert_eq!(owed_slugs(&empty), ["fix-check--m"]);
    let r = repo("base");
    let head = git(&r, &["rev-parse", "HEAD"]).unwrap();
    let (b, desc) = base_of(&r);
    assert_eq!(b, head);
    assert!(desc.starts_with("origin/main (merge base "));
    sh(&r, "git update-ref -d refs/remotes/origin/main");
    let (b, desc) = base_of(&r);
    assert_eq!(b, head);
    assert_eq!(desc, format!("HEAD ({}; no origin/main)", &head[..8]));
    // an origin/main with no history in common: no merge base, so HEAD
    sh(&r, "b=$(git symbolic-ref --short HEAD) && git checkout -q --orphan other && git commit -q --allow-empty -m other && git update-ref refs/remotes/origin/main HEAD && git checkout -q \"$b\"");
    assert!(base_of(&r).1.contains("no origin/main"));
}

#[test]
fn ink_classes_and_sheet_kinds_read_their_census() {
    assert_eq!(
        ink_classes(Some(r#"{"ink_classes": {"well": 1, "-": 2, "place": 3}}"#)),
        ["well".to_owned()].into()
    );
    assert!(ink_classes(Some("[1]")).is_empty());
    assert!(ink_classes(Some(r#"{"ink_classes": [1]}"#)).is_empty());
    assert!(ink_classes(Some("not json")).is_empty());
    assert!(ink_classes(None).is_empty());
    assert_eq!(
        sheet_kinds(Some(r#"<g data-kind="a"/><g data-kind="b"/>"#)).len(),
        2
    );
    assert!(sheet_kinds(None).is_empty());
}

#[test]
fn new_maps_and_sheets_are_occasions_and_their_elements_too() {
    let r = repo("new");
    map(&r, "pool", "old", &["well"]);
    commit(&r, "old map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    map(&r, "pool", "fresh", &["well", "kiln"]);
    sheet(&r, "pool", "hall", &["engawa", "well"]);
    put(&r, "pool/compounds/genonly/genonly.gen.py", "#\n");
    put(&r, "pool/hamlets/empty/readme.txt", "x");
    // a legacy hand-drawn map owes nothing; a legacy sheet keeps its review
    map(&r, "legacy-hand-authored-pool", "handmap", &["tannery"]);
    sheet(&r, "legacy-hand-authored-pool", "oldhall", &["altar"]);
    assert_eq!(
        owed_slugs(&r),
        [
            "settlement-review--fresh",
            "building-review--genonly",
            "building-review--hall",
            "building-review--oldhall",
            "glyph-check--altar--oldhall",
            "glyph-check--engawa--hall",
            "glyph-check--kiln--fresh",
            "size-audit--altar",
            "size-audit--engawa",
        ]
    );
    assert_eq!(
        pool_map_names(&r),
        ["fresh", "genonly", "hall", "handmap", "old", "oldhall"]
    );
    let units = all_owed(&r).1;
    let kiln = units.iter().find(|u| u.subject == "kiln").unwrap();
    assert_eq!(
        kiln.occasion,
        "'kiln' is new to the pool's legend (on the new map fresh)"
    );
}

#[test]
fn an_element_new_to_a_standing_map_is_owed_and_a_moved_folder_is_not_new() {
    let r = repo("element");
    map(&r, "pool", "m", &["well"]);
    sheet(&r, "pool", "s", &["gate"]);
    put(&r, "pool/hamlets/m/m.notes.md", "notes\n");
    commit(&r, "maps");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    map(&r, "pool", "m", &["well", "shrine"]);
    sheet(&r, "pool", "s", &["gate", "bell"]);
    let units = all_owed(&r).1;
    assert_eq!(
        slugs(&units),
        [
            "glyph-check--bell--s",
            "glyph-check--shrine--m",
            "size-audit--bell"
        ]
    );
    assert_eq!(units[1].occasion, "'shrine' is new to m");
    // renamed by the delta: no new map, its legend the one it had
    sh(&r, "git checkout -q -- pool && git mv pool/hamlets/m pool/hamlets/moved && git mv pool/hamlets/moved/m.json pool/hamlets/moved/moved.json && git mv pool/hamlets/moved/m.gen.py pool/hamlets/moved/moved.gen.py");
    commit(&r, "rename");
    assert!(owed_slugs(&r).is_empty(), "{:?}", owed_slugs(&r));
}

#[test]
fn an_untracked_render_is_read_from_mains_mirror() {
    let top = super::super::tests::dir("mirror");
    let r = top.join(".clones/c");
    std::fs::create_dir_all(&r).unwrap();
    sh(
        &r,
        "git init -q && git config user.email t@t && git config user.name t",
    );
    put(&r, ".gitignore", "*.svg\n");
    put(&r, "pool/compounds/s/s.gen.py", "#\n");
    sheet(&r, "pool", "s", &["gate", "bell"]);
    commit(&r, "sheet");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    // the base has no svg; main's mirror copy has the gate, so only the bell is new
    sheet(&top, "pool", "s", &["gate"]);
    assert_eq!(owed_slugs(&r), ["glyph-check--bell--s", "size-audit--bell"]);
    std::fs::remove_file(top.join("pool/compounds/s/s.svg")).unwrap();
    assert_eq!(owed_slugs(&r).len(), 4);
}

const OCCASIONS: &str = "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: well - redrawn\n- placement-changed: well on m - moved\n- placement-changed: well on nowhere\n- glyph-redrawn: ghost\n- new-form: m\n- new-program: granary s - the stores\n- gm-fix: m\n- none: nothing\n- bogus: x\n\n## Notes\n";

#[test]
fn a_feature_declares_its_occasions() {
    let r = repo("declared");
    map(&r, "pool", "m", &["well"]);
    sheet(&r, "pool", "s", &["gate"]);
    commit(&r, "maps");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    feature(&r, "900-x", OCCASIONS);
    let (_, units, problems) = all_owed(&r);
    assert_eq!(
        slugs(&units),
        [
            "settlement-review--m",
            "building-review--s",
            "glyph-check--ghost",
            "glyph-check--well--m",
            "glyph-check--well",
            "size-audit--granary",
            "fix-check--m",
        ]
    );
    let well = units
        .iter()
        .find(|u| u.slug() == "glyph-check--well--m")
        .unwrap();
    assert_eq!(
        well.occasion,
        "declared glyph-redrawn (specs/900-x): redrawn; moved"
    );
    assert_eq!(
        problems,
        [
            "specs/900-x: placement-changed: 'well' is not drawn on 'nowhere'",
            "specs/900-x: glyph-redrawn: 'ghost' is drawn on no pool map or sheet",
            "specs/900-x: unknown occasion 'bogus' (one of glyph-redrawn, placement-changed, new-form, new-tier, layout-revised, new-program, gm-fix, none)",
        ]
    );
    let ruled = ruling("d", &units, &problems);
    assert!(ruled
        .starts_with("owed against d: settlement-review:m on m (declared new-form (specs/900-x))"));
    assert!(ruled.contains("glyph-check:ghost on ? (") && ruled.contains(" | PROBLEMS: "));
    assert_eq!(
        ruling("d", &[], &[]),
        "no review owed against d: no occasion in the delta"
    );
    // the lines the base already had were judged when they landed
    commit(&r, "declared");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    put(
        &r,
        "specs/900-x/tasks.md",
        &(OCCASIONS.to_owned() + "\n## Occasions\n\n- gm-fix: other\n"),
    );
    assert!(owed_slugs(&r).is_empty());
    put(
        &r,
        "specs/900-x/tasks.md",
        &OCCASIONS.replace("- gm-fix: m", "- gm-fix: m - again"),
    );
    assert_eq!(owed_slugs(&r), ["fix-check--m"]);
}

#[test]
fn a_detected_unit_gathers_the_declared_waves_words() {
    let r = repo("merge");
    map(&r, "pool", "m", &["well"]);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    map(&r, "pool", "m", &["well", "kiln"]);
    feature(&r, "900-x", "- [ ] T1\n\n## Occasions\n\n- placement-changed: kiln on m - wave one\n- glyph-redrawn: kiln on m - wave one\n");
    let units = all_owed(&r).1;
    assert_eq!(units[0].occasion, "'kiln' is new to m: wave one");
}

#[test]
fn the_active_features_are_the_open_pointer_and_the_touched_unlanded_ones() {
    let r = repo("active");
    map(&r, "pool", "m", &["well"]);
    feature(
        &r,
        "901-landed",
        "- [x] T1\n\n## Occasions\n\n- gm-fix: m\n",
    );
    put(&r, "specs/903-notasks/x.md", "x");
    commit(&r, "features");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    put(
        &r,
        "specs/902-open/tasks.md",
        "- [ ] T1\n\n## Occasions\n\n- gm-fix: m - open\n",
    );
    // the pointer names a closed feature, a later record written into its folder is no work of it
    put(&r, "specs/901-landed/note.md", "a later record\n");
    put(&r, "specs/902-open/note.md", "x\n");
    put(&r, "specs/903-notasks/y.md", "x\n");
    put(&r, "specs/top.md", "x\n");
    commit(&r, "touch");
    let (_, units, _) = all_owed(&r);
    assert_eq!(slugs(&units), ["fix-check--m"]);
    assert_eq!(units[0].occasion, "declared gm-fix (specs/902-open): open");
    // the pointer, open, declares; a pointer that is not JSON names none
    put(
        &r,
        "specs/901-landed/tasks.md",
        "- [ ] T2\n\n## Occasions\n\n- new-tier: m\n",
    );
    assert_eq!(owed_slugs(&r).len(), 2);
    put(&r, ".specify/feature.json", "{");
    assert_eq!(owed_slugs(&r).len(), 2);
}

#[test]
fn a_tweak_declares_in_its_commit_message() {
    let r = repo("tweak");
    map(&r, "pool", "m", &["well"]);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    sh(&r, "git commit -q --allow-empty -m 'tweak' -m 'Occasion: glyph-redrawn: well - its second crossbar' -m 'Occasion: nonsense'");
    let units = all_owed(&r).1;
    assert_eq!(
        units[0].occasion,
        "declared glyph-redrawn (the delta's commit messages): its second crossbar"
    );
}

#[test]
fn a_section_and_its_lines_read_as_python_split_them() {
    assert_eq!(occasions_section("no section"), None);
    assert_eq!(
        occasions_section(
            "## Occasions  \r\n- a-b : c d  \u{2028}- x: y\r\n- not one\r## Next\n- z: w"
        ),
        Some(vec![
            ("a-b".to_owned(), "c d".to_owned()),
            ("x".to_owned(), "y".to_owned()),
            // a heading after a bare `\r` ends no section: Python's `^` follows `\n` alone
            ("z".to_owned(), "w".to_owned())
        ])
    );
    assert_eq!(occasions_section("## Occasions\n"), Some(Vec::new()));
}

#[test]
fn undeclared_drawing_code_is_refused() {
    let r = repo("code");
    assert_eq!(check_declared(&r), None);
    for i in 0..7 {
        put(&r, &format!("l7r/diagram/t{i}.py"), "x = 1\n");
    }
    put(&r, "l7r/diagram/ci/gate.py", "x\n");
    put(&r, "l7r/diagram/tests/t.py", "x\n");
    put(&r, "pool/hamlets/m/m.svg", "<svg/>\n");
    let refusal = check_declared(&r).unwrap();
    assert!(refusal.starts_with("drawing or placement code moved (l7r/diagram/t0.py, l7r/diagram/t1.py, l7r/diagram/t2.py, l7r/diagram/t3.py, l7r/diagram/t4.py and 3 more)"));
    let r2 = repo("code2");
    put(&r2, "l7r/diagram/x.py", "x\n");
    commit(&r2, "code");
    assert!(check_declared(&r2).unwrap().contains("(l7r/diagram/x.py)"));
    feature(&r2, "900-x", "- [ ] T1\n\n## Occasions\n\n- none: a test\n");
    assert_eq!(check_declared(&r2), None);
    // code the delta only moved is no change
    let r3 = repo("code3");
    put(&r3, "l7r/diagram/a.py", "x = 1\n");
    commit(&r3, "a");
    sh(
        &r3,
        "git update-ref refs/remotes/origin/main HEAD && git mv l7r/diagram/a.py l7r/diagram/b.py",
    );
    assert_eq!(check_declared(&r3), None);
}

#[test]
fn the_command_line_reads_as_argparse_did() {
    let r = repo("cli");
    map(&r, "pool", "m", &["well"]);
    let out = |extra: &[&str]| cli_in(&r, extra);
    assert_eq!(out(&[]).stdout, "settlement-review--m\n");
    assert_eq!(
        out(&["--units"]).stdout,
        "settlement-review--m\tsettlement-review\tm\tm\ta map new to the pool\n"
    );
    let why = out(&["--why"]);
    assert!(why
        .stdout
        .starts_with("owed against origin/main (merge base "));
    assert!(why.stdout.contains("glyph checks owed and not yet due (feature 375 amendment 9 - on the feature's hour, or at landing): glyph-check--well--m (at landing)\n"));
    assert_eq!(
        out(&["--landing"]).stdout,
        "settlement-review--m\nglyph-check--well--m\n"
    );
    assert!(!out(&["--why", "--landing"]).stdout.contains("not yet due"));
    let refused = out(&["--check-declared"]);
    assert_eq!(
        (
            refused.code,
            refused
                .stdout
                .starts_with("drawing or placement code moved (pool/hamlets/m/m.gen.py)")
        ),
        (1, true)
    );
    feature(&r, "900-x", "- [ ] T1\n\n## Occasions\n\n- none: a test\n");
    assert_eq!(out(&["--check-declared"]).code, 0);
    std::fs::remove_file(r.join(".specify/feature.json")).unwrap();
    assert_eq!(out(&["--why", "--units"]).code, 2);
    assert_eq!(out(&["--landing-mark", "maybe"]).code, 2);
    assert_eq!(out(&["--glyph-gate"]).code, 2);
    assert!(out(&["--help"])
        .stdout
        .starts_with("usage: l7r-gate reviews owed"));
    assert_eq!(out(&["--landing-mark", "on"]).code, 0);
    assert!(r.join(".git/glyph-landing").is_file());
    assert_eq!(out(&["--landing-mark", "off"]).code, 0);
    assert!(!r.join(".git/glyph-landing").exists());
    let gate = out(&["--glyph-gate", "glyph-check--well--m"]);
    assert_eq!(gate.code, 1);
    assert!(gate
        .stdout
        .starts_with("glyph-check--well--m is owed but not yet due - due at landing ("));
    assert_eq!(out(&["--glyph-dispatched", "glyph-check--well--m"]).code, 0);
    let not = cli(&["--root".to_owned(), "/".to_owned()]);
    assert_eq!(
        (not.code, not.stderr.as_str()),
        (1, "_review_owed: / is not a git repository\n")
    );
}

#[test]
fn the_glyph_hour_keeps_the_due_units_only() {
    let r = repo("hour");
    map(&r, "pool", "m", &["well"]);
    feature(&r, "900-x", "- [ ] T1\n");
    events(&r, "900-x", &[(7200, "PreToolUse", false)]);
    assert_eq!(
        slugs(&owed(&r, false).1),
        ["settlement-review--m", "glyph-check--well--m"]
    );
    events(&r, "900-x", &[(60, "PreToolUse", false)]);
    assert_eq!(slugs(&owed(&r, false).1), ["settlement-review--m"]);
    assert_eq!(owed(&r, true).1.len(), 2);
}

#[test]
fn a_folder_of_one_name_in_both_trees_keeps_its_first_place() {
    let r = repo("twice");
    sheet(&r, "pool", "s", &["a"]);
    sheet(&r, "legacy-hand-authored-pool", "s", &["b"]);
    map(&r, "pool", "z", &["b"]);
    let tree = Tree::read(&r);
    assert_eq!(tree.legends.get("s").unwrap(), &["b".to_owned()].into());
    assert_eq!(tree.legends.first_drawing("b"), "s");
    assert_eq!(tree.legends.first_drawing("nothing"), "");
    let _ = json!(null);
}

#[test]
fn a_map_in_a_repository_with_no_commits_is_new_to_the_pool() {
    let root = super::super::tests::dir("unborn-map");
    sh(&root, "git init -q");
    put(&root, "pool/hamlets/m/m.json", "{}");
    let (_, units, _) = super::owed(&root, true);
    assert_eq!(slugs(&units), ["settlement-review--m"]);
}

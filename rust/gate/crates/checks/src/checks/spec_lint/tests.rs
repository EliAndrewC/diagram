//! The six checks of a spec, each written by breaking its rule.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::super::scratch;
use super::{
    at_base, bare, check_approval, check_duplicate_tasks, check_figures, check_orphans,
    check_stale_tasks, checks_one_to_four, cli, introduced, lint, touched_spec_dirs, wrong_rows,
    Row, CHECK6_MARK, GOOD, ID, POINTER, TASK,
};

fn feature(
    spec: &str,
    tasks: Option<&str>,
    research: Option<&str>,
) -> (l7r_guard::shared::tempdir::TempDir, PathBuf) {
    let root = scratch("spec-lint-test");
    let dir = root.join("specs/999-a-feature");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("spec.md"), spec).unwrap();
    if let Some(text) = tasks {
        std::fs::write(dir.join("tasks.md"), text).unwrap();
    }
    if let Some(text) = research {
        std::fs::write(dir.join("research.md"), text).unwrap();
    }
    (root, dir)
}

fn found(spec: &str, research: Option<&str>) -> Vec<String> {
    let (_dir, dir) = feature(spec, Some(TASK), research);
    checks_one_to_four(&dir)
}

fn owned(args: &[&str]) -> Vec<String> {
    args.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    std::fs::create_dir_all(root.join(rel).parent().unwrap()).unwrap();
    std::fs::write(root.join(rel), text).unwrap();
}

#[test]
fn check_6_a_new_feature_without_the_approval_line_and_never_before_377() {
    let (_dir, dir) = feature(GOOD, None, None);
    let bad = check_approval(&dir);
    assert!(
        bad[0].contains(CHECK6_MARK)
            && bad[0].contains("has none")
            && bad[0].contains("**Approved**: the GM")
    );
    std::fs::write(
        dir.join("spec.md"),
        format!("{GOOD}\n**Approved**: the GM, 2026-10-10, \"Yes\"\n"),
    )
    .unwrap();
    assert!(check_approval(&dir)[0].contains("fewer than three words"));
    std::fs::write(
        dir.join("spec.md"),
        format!("{GOOD}\n**Approved**: the GM, 2026-10-10, \"please file it then\"\n"),
    )
    .unwrap();
    assert_eq!(check_approval(&dir), Vec::<String>::new());
    let old_dir = scratch("old");
    let old = old_dir.join("376-older");
    std::fs::create_dir_all(&old).unwrap();
    std::fs::write(old.join("spec.md"), GOOD).unwrap();
    assert_eq!(check_approval(&old), Vec::<String>::new());
    let name_dir = scratch("name");
    let unnumbered = name_dir.join("a-feature");
    std::fs::create_dir_all(&unnumbered).unwrap();
    std::fs::write(unnumbered.join("spec.md"), GOOD).unwrap();
    assert_eq!(check_approval(&unnumbered), Vec::<String>::new());
}

#[test]
fn the_correct_form_is_quiet() {
    assert_eq!(found(GOOD, None), Vec::<String>::new());
}

#[test]
fn check_1_a_figure_with_no_pointer_a_count_and_the_narrating_sections() {
    let line = "It took 91 min, measured in `research.md` R1.";
    assert!(found(&GOOD.replace(line, "It took 91 min."), None)[0].contains("no pointer"));
    assert_eq!(
        found(
            &GOOD.replace(line, "Twenty rounds of review, and 8 of them mechanical."),
            None
        ),
        Vec::<String>::new()
    );
    assert_eq!(
        found(
            &GOOD.replace(
                "Round 1 said 6.7 m and we withdrew it.",
                "Round 1 said 6.7 m, 22 ft and 91 min, all withdrawn."
            ),
            None
        ),
        Vec::<String>::new()
    );
    assert!(POINTER
        .is_match("near 1-2 s (`research/estimate-exercise.md`)")
        .unwrap());
    assert!(!POINTER.is_match("near 1-2 s, by the estimate").unwrap());
}

#[test]
fn check_2_still_standing_narrated_and_too_short() {
    assert!(found(
        &GOOD.replace(
            "**FR-001** A thing.",
            "**FR-001** Keep the 22 ft clearance."
        ),
        Some("WITHDRAWN: the 22 ft clearance\n")
    )[0]
    .contains("withdrawn text still standing"));
    assert_eq!(
        found(GOOD, Some("WITHDRAWN: the 22 ft figure out\n")),
        Vec::<String>::new()
    );
    assert!(found(GOOD, Some("WITHDRAWN: 22 ft\n"))[0].contains("twelve characters"));
}

#[test]
fn check_2_reaches_the_whole_tree_and_leaves_a_verbatim_record_alone() {
    let (root, dir) = feature(GOOD, Some(TASK), Some("WITHDRAWN: the 22 ft clearance\n"));
    for (rel, body) in [
        (
            "specs/998-elsewhere/spec.md",
            "## Summary\n\nthe 22 ft clearance\n",
        ),
        ("docs/outside.md", "the 22 ft clearance\n"),
        ("CLAUDE.md", "a rule resting on the 22 ft clearance\n"),
        (
            "scripts/tool.py",
            "\"\"\"Keeps the 22 ft clearance.\"\"\"\n",
        ),
        ("Makefile", "\t: \"the 22 ft clearance\"\n"),
        ("tests/hooks/fixtures/corpus.json", "the 22 ft clearance\n"),
        ("dev/run-log/a.json", "the 22 ft clearance\n"),
        ("a.png", "the 22 ft clearance\n"),
        (".clones/x/y.md", "the 22 ft clearance\n"),
        ("bin.dat", "\0 the 22 ft clearance\n"),
    ] {
        put(&root, rel, body);
    }
    let got = checks_one_to_four(&dir);
    for place in [
        "998-elsewhere",
        "outside.md",
        "CLAUDE.md",
        "tool.py",
        "Makefile",
    ] {
        assert!(got.iter().any(|x| x.contains(place)), "{place}: {got:?}");
    }
    assert_eq!(got.len(), 5, "{got:?}");
}

#[test]
fn check_2_reads_the_tracked_tree_when_it_is_a_repository_and_only_a_marker_that_opens_a_line() {
    let (root, dir) = feature(GOOD, Some(TASK), Some("A `research.md` may mark text WITHDRAWN: <text> like this.\n- WITHDRAWN: a figure of ours here\n"));
    put(
        &root,
        "docs/outside.md",
        "<text> like this.\na figure of ours here\n",
    );
    assert!(Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    let got = checks_one_to_four(&dir);
    assert_eq!(got.len(), 1, "{got:?}");
    assert!(
        got[0].contains("outside.md:2:")
            && got[0].contains("research.md:2 marks 'a figure of ours here'")
    );
}

#[test]
fn a_narrating_section_runs_to_the_next_heading_of_its_level() {
    let spec = "## Review history\n\n### Round 1\n\nthe withdrawn phrase here\n\n## Summary\n\nthe withdrawn phrase here\n";
    let (root, dir) = feature(spec, None, Some("WITHDRAWN: the withdrawn phrase here\n"));
    let got = lint(&dir, &root);
    let standing: Vec<&String> = got
        .iter()
        .filter(|x| x.contains("still standing"))
        .collect();
    assert_eq!(standing.len(), 1);
    assert!(standing[0].contains("spec.md:9:"));
}

#[test]
fn check_3_orphans_ranges_letters_and_a_criterion_naming_nothing() {
    assert!(
        found(&GOOD.replace("(FR-001, FR-001a)", "(FR-001)"), None)[0]
            .contains("FR-001a is named by no success criterion")
    );
    assert_eq!(
        found(&GOOD.replace("(FR-001, FR-001a)", "(FR-001-FR-002)"), None),
        Vec::<String>::new()
    );
    let ids: Vec<(String, String)> = ID
        .captures_iter("see FR-001a and SC-002")
        .flatten()
        .map(|c| (c[1].to_owned(), c[2].to_owned()))
        .collect();
    assert_eq!(
        ids,
        [
            ("FR".to_owned(), "001a".to_owned()),
            ("SC".to_owned(), "002".to_owned())
        ]
    );
    assert!(found(
        &GOOD.replace(
            "**SC-002** (spec-wide) The gate is green.",
            "**SC-002** The gate is green."
        ),
        None
    )[0]
    .contains("names no FR"));
}

#[test]
fn a_criterion_under_a_sub_heading_counts() {
    let spec = "## Functional requirements\n\n**FR-001** A thing.\n\n## Success criteria\n\n### Measurable outcomes\n\n**SC-001** (FR-001) It holds.\n";
    let (_dir, dir) = feature(spec, Some(TASK), None);
    assert_eq!(check_orphans(&dir.join("spec.md")), Vec::<String>::new());
}

#[test]
fn check_4_a_task_citing_a_lost_id_and_another_feature_s_requirement() {
    let (_dir, dir) = feature("## Functional requirements\n\n**FR-001** A thing.\n\n## Success criteria\n\n**SC-001** (FR-001) It holds.\n", Some("- [ ] T01 carried by the claims gate (385 FR-013) and feature 385's FR-014 (FR-001)\n- [ ] T02 bare (FR-013)\n"), None);
    let got = check_stale_tasks(&dir.join("spec.md"), &dir.join("tasks.md"));
    assert_eq!(got.len(), 1);
    assert!(got[0].contains(":2: cites FR-013") && got[0].contains("spec.md does not define"));
}

#[test]
fn check_7_a_task_id_taken_twice() {
    let (_dir, dir) = feature(
        GOOD,
        Some(
            "- [ ] T93 a figure\n      research: rendering\n- [x] T94 a page\n- [ ] T93 a carry\n",
        ),
        None,
    );
    let got = check_duplicate_tasks(&dir.join("tasks.md"));
    assert!(
        got[0].contains(":4: task id T93 is taken (line 1)") && got[0].contains("make task-add")
    );
    std::fs::write(
        dir.join("tasks.md"),
        "- [ ] T93 a figure\n- [ ] T93a its half\n",
    )
    .unwrap();
    assert_eq!(
        check_duplicate_tasks(&dir.join("tasks.md")),
        Vec::<String>::new()
    );
}

#[test]
fn a_freshly_claimed_spec_and_an_empty_directory_pass() {
    let (root, dir) = feature("# Feature 999\n\n## Summary\n\nIt took 91 min.\n\n## Functional requirements\n\n**FR-001** A thing.\n", None, None);
    assert_eq!(checks_one_to_four(&dir), Vec::<String>::new());
    let empty = root.join("specs/241-just-claimed");
    std::fs::create_dir_all(&empty).unwrap();
    assert_eq!(lint(&empty, &root), Vec::<String>::new());
}

#[test]
fn this_feature_s_own_spec_passes_checks_1_and_3() {
    let own = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../../../specs/236-catch-mistakes-early-and-cheaply/spec.md");
    assert_eq!(check_figures(&own), Vec::<String>::new());
    assert_eq!(check_orphans(&own), Vec::<String>::new());
}

#[test]
fn a_self_test_row_with_the_wrong_verdict_is_named() {
    let rows: [Row; 2] = [
        ("", "", "", TASK, "a finding that is not there"),
        ("", "", "", "", ""),
    ];
    assert_eq!(wrong_rows(&rows), [0]);
}

#[test]
fn the_multiset_of_what_a_push_introduced() {
    let list = |x: &[&str]| owned(x);
    assert_eq!(
        introduced(
            list(&["a.md:3: FR-002 is named by no success criterion"]),
            &list(&["a.md:9: FR-002 is named by no success criterion"])
        ),
        Vec::<String>::new()
    );
    assert_eq!(
        introduced(
            list(&["a.md:3: x at r.md:4 marks y", "a.md:5: new"]),
            &list(&["a.md:1: x at r.md:7 marks y"])
        ),
        ["a.md:5: new"]
    );
    assert_eq!(
        introduced(
            list(&["a.md:3: same", "a.md:4: same"]),
            &list(&["a.md:1: same"])
        ),
        ["a.md:4: same"]
    );
    assert_eq!(bare("a.md:3: same"), "same");
}

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

#[test]
fn a_landed_spec_is_judged_on_what_the_push_introduces() {
    let root = scratch("landed");
    let dir = root.join("specs/200-landed");
    put(
        &root,
        "specs/200-landed/tasks.md",
        "- [x] T01 do the thing (FR-001)\n",
    );
    put(&root, "specs/200-landed/spec.md", "# x\n\n## Functional requirements\n\n**FR-001** A thing.\n\n**FR-002** Old, named by nothing.\n");
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "landed"]);
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let base = "origin/main";
    let before = at_base(&root, base, &dir).unwrap();
    assert_eq!(
        introduced(checks_one_to_four(&dir), &before),
        Vec::<String>::new()
    );
    assert_eq!(at_base(&root, base, &root.join("specs/999-new")), None);
    std::fs::write(
        dir.join("spec.md"),
        std::fs::read_to_string(dir.join("spec.md")).unwrap()
            + "\n**FR-003** New, named by nothing.\n",
    )
    .unwrap();
    assert!(introduced(checks_one_to_four(&dir), &before)[0].contains("FR-003"));
    assert_eq!(
        touched_spec_dirs(&root),
        [std::fs::canonicalize(&dir).unwrap()]
    );
    let done = cli(&owned(&["--delta", &root.display().to_string()]));
    assert_eq!(done.code, 1);
    assert!(
        done.stdout.contains("FR-003")
            && !done.stdout.contains("FR-002")
            && done.stdout.contains("spec-lint: 1 finding(s).")
    );
    put(&root, "specs/not-a-dir", "x");
    git(&root, &["add", "-A"]);
    assert_eq!(touched_spec_dirs(&root).len(), 1);
}

#[test]
fn the_command_line_names_directories_a_self_test_and_the_one_figure() {
    assert!(cli(&owned(&["--selftest"])).stdout.contains("selftest ok"));
    assert!(cli(&owned(&["--figure-pattern"]))
        .stdout
        .contains("(?:minutes|"));
    let (_dir, dir) = feature(GOOD, Some(TASK), None);
    let done = cli(&[dir.display().to_string()]);
    assert_eq!(done.code, 1);
    assert_eq!(cli(&[]).code, 0);
}

#[test]
fn a_clean_directory_says_nothing_and_a_tree_with_no_base_reads_its_worktree() {
    let spec = "## Functional requirements\n\n**FR-001** A thing.\n\n## Success criteria\n\n**SC-001** (FR-001) It holds.\n\n**Approved**: the GM, 2026-10-10, \"please file it then\"\n";
    let (root, dir) = feature(spec, Some(TASK), None);
    assert_eq!(cli(&[dir.display().to_string()]).code, 0);
    git(&root, &["init", "-q", "-b", "main"]);
    put(&root, "other.txt", "x");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    put(&root, "specs/999-a-feature/new.txt", "x");
    put(&root, "elsewhere.txt", "x");
    assert_eq!(
        touched_spec_dirs(&root),
        [std::fs::canonicalize(&dir).unwrap()]
    );
}

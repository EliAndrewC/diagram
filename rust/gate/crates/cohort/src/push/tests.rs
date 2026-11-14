//! What each push gate judges, and the push's runner.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    binary_id, checks_cli, gate_cli, holds, judged, judges, parse_skips, run_checks,
    scripts_version, skip, Row, Tool, Tools, CHECKS,
};
use crate::checks::scratch;
use l7r_guard::shared::sha256;

fn git(repo: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(repo)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "{args:?}");
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

fn repo() -> l7r_guard::shared::tempdir::Held<PathBuf> {
    let tmp = scratch("push");
    let (origin, work) = (tmp.join("origin.git"), tmp.join("work"));
    git(
        &tmp,
        &["init", "-q", "--bare", &origin.display().to_string()],
    );
    git(
        &tmp,
        &["init", "-q", "-b", "main", &work.display().to_string()],
    );
    std::fs::create_dir_all(work.join("scripts")).unwrap();
    std::fs::create_dir_all(work.join("l7r")).unwrap();
    std::fs::write(work.join("scripts/g.sh"), "gate\n").unwrap();
    std::fs::write(work.join("l7r/a.py"), "x = 1\n").unwrap();
    git(&work, &["add", "-A"]);
    git(&work, &["commit", "-qm", "base"]);
    git(
        &work,
        &["remote", "add", "origin", &origin.display().to_string()],
    );
    git(&work, &["push", "-q", "origin", "HEAD:main"]);
    git(&work, &["fetch", "-q", "origin"]);
    let held = work;
    tmp.hold(held)
}

fn ask(work: &Path, gate: &str) -> String {
    let (prefixes, what) = judges(gate).unwrap();
    skip(work, gate, prefixes, what)
}

fn pass(work: &Path, gate: &str) {
    gate_cli(&["pass".to_owned(), gate.to_owned()], work);
}

fn real(rel: &str) -> String {
    std::fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../../..")
            .join(rel),
    )
    .unwrap()
}

fn constant<'t>(text: &'t str, name: &str) -> &'t str {
    text.lines()
        .find_map(|l| l.strip_prefix(&format!("{name} = ")))
        .unwrap()
}

fn quoted(line: &str) -> Vec<&str> {
    line.split('"').skip(1).step_by(2).collect()
}

fn covered(gate: &str, path: &str) -> bool {
    let probe = if crate::checks::has_ext(path, "json") || crate::checks::has_ext(path, "md") {
        path.to_owned()
    } else {
        format!("{}/x", path.trim_end_matches('/'))
    };
    !judged(judges(gate).unwrap().0, &[probe]).is_empty()
}

#[test]
fn each_gate_judges_every_path_its_own_constants_name() {
    assert!(
        covered("claims", "specs/430-x/tasks.md")
            && covered("claims", "specs/430-x/gm-review.jsonl")
    );
    for p in [
        crate::record::units::QUESTIONS.rsplit_once('/').unwrap().0,
        "l7r/diagram/interactive/classes",
        "l7r/diagram/interactive/compound_kinds",
    ] {
        assert!(covered("entry", p), "{p}");
    }
    for (path, name) in [
        ("scripts/record/entry_owed.py", "CLASSES"),
        ("scripts/record/entry_owed.py", "COMPOUND_KINDS"),
    ] {
        assert!(covered("entry", quoted(constant(&real(path), name))[0]));
    }
    for p in [
        "l7r/diagram/x/law.py",
        "pool/hamlets/m/m.json",
        "pool/hamlets/m/m.gen.py",
    ] {
        assert!(!judged(judges("cohort").unwrap().0, &[p.to_owned()]).is_empty());
    }
    assert!(judges("nothing").is_none());
}

#[test]
fn a_records_only_delta_skips_every_gate() {
    let work = repo();
    std::fs::create_dir_all(work.join("dev/run-log")).unwrap();
    std::fs::write(work.join("dev/run-log/r.json"), "{}").unwrap();
    git(&work, &["add", "-A"]);
    git(&work, &["commit", "-qm", "a record"]);
    for gate in ["claims", "entry", "cohort"] {
        assert!(ask(&work, gate).contains("nothing to judge"), "{gate}");
    }
}

#[test]
fn a_pass_is_served_only_for_the_same_committed_content() {
    let work = repo();
    std::fs::write(work.join("l7r/a.py"), "x = 2\n").unwrap();
    assert_eq!(ask(&work, "claims"), "");
    pass(&work, "claims");
    assert_eq!(ask(&work, "claims"), "");
    git(&work, &["commit", "-qam", "code"]);
    assert_eq!(ask(&work, "claims"), "");
    pass(&work, "claims");
    assert!(ask(&work, "claims").contains("passed already"));
    std::fs::write(work.join("l7r/a.py"), "x = 3\n").unwrap();
    assert_eq!(ask(&work, "claims"), "");
    git(&work, &["commit", "-qam", "more code"]);
    assert_eq!(ask(&work, "claims"), "");
    std::fs::write(work.join("scripts/g.sh"), "gate, changed\n").unwrap();
    git(&work, &["commit", "-qam", "the gate's own code"]);
    pass(&work, "claims");
    assert!(ask(&work, "claims").contains("passed already"));
}

#[test]
fn with_no_merge_base_nothing_is_skipped() {
    let tmp = scratch("nobase");
    git(&tmp, &["init", "-q", "-b", "main"]);
    std::fs::write(tmp.join("a.txt"), "a\n").unwrap();
    git(&tmp, &["add", "-A"]);
    git(&tmp, &["commit", "-qm", "only"]);
    assert_eq!(ask(&tmp, "claims"), "");
    pass(&tmp, "claims");
    assert_eq!(ask(&tmp, "claims"), "");
}

#[test]
fn the_gate_verbs_answer_and_say_how_to_use_them() {
    let work = repo();
    let run = |words: &[&str]| {
        gate_cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &work,
        )
    };
    assert_eq!(run(&["skip", "claims"]).code, 0);
    std::fs::write(work.join("l7r/a.py"), "x = 9\n").unwrap();
    let judged = run(&["skip", "claims"]);
    assert_eq!((judged.code, judged.stdout.as_str()), (1, ""));
    assert_eq!(run(&["pass", "claims"]).code, 0);
    assert_eq!(run(&["what", "claims"]).code, 2);
    assert_eq!(run(&["skip", "nope"]).code, 2);
    assert_eq!(run(&[]).code, 2);
}

fn tools(tree: &Path, off: bool) -> Tools {
    Tools {
        tree: tree.to_owned(),
        python: "bash".to_owned(),
        off,
        binary: Some(tree.join("gate-binary")),
    }
}

fn tree() -> l7r_guard::shared::tempdir::Held<PathBuf> {
    let root = repo();
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    crate::write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/usr/bin/env bash\necho gate \"$@\" >> gate.log\n[ \"$1\" != bad ]\n",
    );
    std::fs::write(root.join("scripts/ok.py"), "echo ran >> ran.log\n").unwrap();
    std::fs::write(root.join("scripts/no.py"), "exit 3\n").unwrap();
    root
}

const OK: Row = Row("ok", Tool::Py("ok.py"), &["{root}"], "unused", false, "");
const KEPT: Row = Row("kept", Tool::Py("ok.py"), &[], "unused", true, "");
const BAD: Row = Row("no", Tool::Py("no.py"), &[], "no refused", false, "");
const CLOSING: Row = Row(
    "closing",
    Tool::Py("no.py"),
    &[],
    "closing refused",
    false,
    "",
);
const GATE_OK: Row = Row("gate", Tool::Gate, &["good", "{root}"], "unused", false, "");
const GATE_NEEDS: Row = Row(
    "needs",
    Tool::Gate,
    &["good"],
    "unused",
    false,
    "no/such/path",
);

fn lines(path: &Path) -> usize {
    std::fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .count()
}

#[test]
fn the_runner_stops_at_the_first_refusal_with_the_shell_s_line() {
    let root = tree();
    let got = run_checks(&tools(&root, false), &[OK, BAD, KEPT], &root, &[]);
    assert_eq!(got.code, 1);
    assert_eq!(got.stderr, "sync-with-main: no refused\n");
    // the rows run side by side (T115), so a self-test after the refusal ran too, but a refusal ends the run: it keeps nothing
    assert_eq!(lines(&root.join("ran.log")), 2);
    let stamps =
        std::fs::read_to_string(super::stamps_file(&root, false).unwrap()).unwrap_or_default();
    assert!(!stamps.contains("\"kept\""));
}

#[test]
fn a_row_that_needs_what_the_tree_does_not_hold_is_not_run_and_a_skip_is_honored() {
    let root = tree();
    assert_eq!(
        run_checks(
            &tools(&root, true),
            &[GATE_NEEDS, GATE_OK],
            &root,
            &["gate".to_owned()]
        )
        .code,
        0
    );
    assert!(!root.join("gate.log").exists());
    assert_eq!(
        run_checks(&tools(&root, true), &[GATE_OK], &root, &[]).code,
        0
    );
    assert!(std::fs::read_to_string(root.join("gate.log"))
        .unwrap()
        .contains(&format!("gate good {}", root.display())));
    assert!(holds(&root, "scripts") && !holds(&root, "nope") && holds(&root, ""));
    assert!(holds(&root, "delta:unknown-check"));
}

#[test]
fn a_passed_self_test_is_kept_until_its_code_changes_and_a_failure_never_is() {
    let root = tree();
    assert_eq!(
        run_checks(&tools(&root, false), &[KEPT], &root, &[]).code,
        0
    );
    assert_eq!(
        run_checks(&tools(&root, false), &[KEPT], &root, &[]).code,
        0
    );
    assert_eq!(lines(&root.join("ran.log")), 1, "kept");
    git(&root, &["add", "scripts"]);
    assert_eq!(
        run_checks(&tools(&root, false), &[KEPT], &root, &[]).code,
        0
    );
    assert_eq!(lines(&root.join("ran.log")), 2, "the index moved");
    std::fs::write(
        root.join("scripts/ok.py"),
        "echo ran >> ran.log\n# changed\n",
    )
    .unwrap();
    assert_eq!(
        run_checks(&tools(&root, false), &[KEPT], &root, &[]).code,
        0
    );
    assert_eq!(lines(&root.join("ran.log")), 3, "its code changed");
    assert_eq!(run_checks(&tools(&root, true), &[KEPT], &root, &[]).code, 0);
    assert_eq!(lines(&root.join("ran.log")), 4, "the cache off runs it");
    assert_ne!(scripts_version(&root), "");
    let failing = Row("kept-fails", Tool::Py("no.py"), &[], "failed", true, "");
    assert_eq!(
        run_checks(&tools(&root, false), &[failing], &root, &[]).code,
        1
    );
}

const GATE_KEPT: Row = Row("gate-kept", Tool::Gate, &["good"], "unused", true, "");

/// A Rust self-test is kept per binary and per version of `scripts/` (T109): run again when the binary is rebuilt, when the scripts
/// move, with the cache off, and every time where the binary's file cannot be read.
#[test]
fn a_passed_rust_self_test_is_kept_until_the_binary_or_the_scripts_change() {
    let root = tree();
    let binary = root.join("gate-binary");
    std::fs::write(&binary, "one").unwrap();
    let runs = || lines(&root.join("gate.log"));
    let push = |tools: &Tools| run_checks(tools, &[GATE_KEPT], &root, &[]).code;
    assert_eq!(push(&tools(&root, false)), 0);
    assert_eq!(push(&tools(&root, false)), 0);
    assert_eq!(runs(), 1, "kept");
    // a rebuild writes a new file
    std::fs::remove_file(&binary).unwrap();
    std::fs::write(&binary, "two").unwrap();
    assert_eq!(push(&tools(&root, false)), 0);
    assert_eq!(runs(), 2, "the binary was rebuilt");
    std::fs::write(root.join("scripts/codeid.py"), "# moved\n").unwrap();
    git(&root, &["add", "scripts"]);
    assert_eq!(push(&tools(&root, false)), 0);
    assert_eq!(runs(), 3, "the scripts moved");
    assert_eq!(push(&tools(&root, false)), 0);
    assert_eq!(runs(), 3, "kept again");
    assert_eq!(push(&tools(&root, true)), 0);
    assert_eq!(runs(), 4, "the cache off runs it");
    let unread = Tools {
        binary: Some(root.join("no-binary")),
        ..tools(&root, false)
    };
    // no binary, no keeping
    let twice = (push(&unread), push(&unread), runs());
    assert_eq!(twice, (0, 0, 6));
    assert!(binary_id(&root.join("no-binary")).is_none());
}

#[test]
fn a_closing_refusal_ends_the_run() {
    let root = tree();
    assert_eq!(
        run_checks(&tools(&root, true), &[CLOSING], &root, &[]).code,
        1
    );
}

#[test]
fn a_tool_that_cannot_start_refuses() {
    let root = tree();
    let tool = Tools {
        tree: root.clone(),
        python: "/no/such/python".to_owned(),
        off: true,
        binary: None,
    };
    assert_eq!(run_checks(&tool, &[OK], &root, &[]).code, 1);
}

#[test]
fn the_table_lists_its_rows_and_the_arguments_are_checked() {
    assert_eq!(CHECKS.len(), 23);
    let root = tree();
    let run = |words: &[&str]| {
        checks_cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &root,
            true,
        )
    };
    assert!(run(&["--list"]).stdout.starts_with("file-scale selftest\n"));
    assert_eq!(run(&[]).code, 2);
    assert_eq!(run(&["/tmp", "--nope"]).code, 2);
    assert!(run(&["/tmp", "--skip", "nothing"])
        .stderr
        .contains("no check named nothing"));
    assert_eq!(
        parse_skips(&["--skip".to_owned(), "conflict".to_owned()]),
        Ok(vec!["conflict".to_owned()])
    );
    assert!(parse_skips(&["--skip".to_owned()]).is_err());
    let all: Vec<String> = CHECKS.iter().map(|r| r.0.to_owned()).collect();
    let mut args = vec![root.display().to_string()];
    for name in &all {
        args.extend(["--skip".to_owned(), name.clone()]);
    }
    assert_eq!(checks_cli(&args, &root, true).code, 0);
    args[0] = "/no/such/root".to_owned();
    assert_eq!(checks_cli(&args, &root, true).code, 0);
}

#[test]
fn a_key_is_the_sha_of_the_gate_the_base_the_scripts_tree_and_the_listing_with_its_newline() {
    let work = repo();
    let head = git(&work, &["rev-parse", "HEAD"]);
    let (head, scripts) = (head.trim(), git(&work, &["rev-parse", "HEAD:scripts"]));
    let listing = git(&work, &["ls-tree", "-r", "HEAD", "--", "l7r/a.py"]);
    let want =
        sha256::hex(format!("claims\n{head}\n{}\n{}\n", scripts.trim(), listing.trim()).as_bytes());
    assert_eq!(
        super::store_key(&work, "claims", head, &["l7r/a.py".to_owned()]),
        want
    );
    let none = sha256::hex(format!("claims\n{head}\n{}\n", scripts.trim()).as_bytes());
    assert_eq!(
        super::store_key(&work, "claims", head, &["nope".to_owned()]),
        none
    );
}

/// The checks of the real table whose `delta:` need the tree holds.
fn delta_rows_that_run(root: &Path) -> Vec<&'static str> {
    let mut ran: Vec<&str> = CHECKS
        .iter()
        .filter(|r| r.5.starts_with("delta:") && holds(root, r.5))
        .map(|r| r.0)
        .collect();
    ran.retain(|n| !n.ends_with("selftest"));
    ran.sort_unstable();
    ran
}

#[test]
fn the_checks_still_in_python_do_not_start_on_a_rust_only_change() {
    let root = repo();
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::create_dir_all(root.join("rust")).unwrap();
    std::fs::write(root.join("rust/a.rs"), "fn f() {}\n").unwrap();
    assert_eq!(delta_rows_that_run(&root), Vec::<&str>::new());
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    std::fs::write(
        root.join("research/questions").join("0001-a.notes.html"),
        "y",
    )
    .unwrap();
    assert_eq!(
        delta_rows_that_run(&root),
        ["entry-headings", "partial-citations"]
    );
}

#[test]
fn the_push_runs_the_make_page_check_and_the_money_check() {
    let row = |name: &str| CHECKS.iter().find(|r| r.0 == name).unwrap();
    assert!(
        matches!(row("make-docs").1, Tool::InProcess(_))
            && row("make-docs").2 == ["make-docs", "{root}", "--check"]
    );
    assert!(row("make-docs").3.contains("make docs"));
    assert!(
        matches!(row("money-candidates").1, Tool::Gate)
            && row("money-candidates").2 == ["record", "money-candidates", "--check"]
    );
    assert!(row("money-candidates").3.contains("backfill.md"));
}

#[test]
fn every_makefile_line_starting_a_retained_python_check_asks_first() {
    let makefile = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../Makefile");
    let text = std::fs::read_to_string(makefile).unwrap();
    let names = ["partial-citations"].map(|n| format!("l7r-gate.sh\" check {n} "));
    let lines: Vec<&str> = text
        .lines()
        .filter(|l| l.starts_with('\t') && names.iter().any(|n| l.contains(n.as_str())))
        .collect();
    assert_eq!(lines.len(), 1);
    assert!(lines.iter().all(|l| l.contains("check needs ")));
}

#[test]
fn the_timing_rows_start_with_the_one_process_run() {
    let work = repo();
    let rows = super::timing_rows(&work, &work);
    assert_eq!(rows[0].0, "push checks (one process)");
    assert!(rows[0].1.is_some() && rows.len() == CHECKS.len() + 1);
}

/// The make-targets page asked in process (feature 449 T135, where the row ran `scripts/make-docs.py`): a current page passes, a stale one
/// refuses with the row's line; its timing form is the gate command.
#[test]
fn the_make_page_row_runs_in_process() {
    let root = tree();
    let docs = std::slice::from_ref(CHECKS.iter().find(|r| r.0 == "make-docs").unwrap());
    std::fs::write(
        root.join("Makefile"),
        "a:   ## [tests] a target\n\techo a\n",
    )
    .unwrap();
    assert_eq!(crate::make_docs::write(&root).code, 0);
    assert_eq!(run_checks(&tools(&root, true), docs, &root, &[]).code, 0);
    std::fs::write(root.join("Makefile"), "b:   ## [tests] another\n\techo b\n").unwrap();
    let refused = run_checks(&tools(&root, true), docs, &root, &[]);
    assert_eq!(
        (refused.code, refused.stderr.contains("make docs")),
        (1, true)
    );
    let timed = super::row_command(&tools(&root, true), &docs[0], &root);
    assert!(timed
        .get_program()
        .to_string_lossy()
        .ends_with("l7r-gate.sh"));
}

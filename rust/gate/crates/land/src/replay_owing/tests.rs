//! `l7r-gate replay-owing` on a scratch history: the OLD side the commits' own Python (a stand-in `modal_owed.py` and `claims.py`), the
//! NEW side the port in process, the worktrees removed on every way out.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use serde_json::json;

use super::{counted, depicted, full, not_in, revs_of, run, wants_triage, with_triage, Env, Spec};

const OLD_MODAL_OWED: &str = "def owed(root, base):\n    return [('modal-depiction:hamlet/well', 'w', 'f'), ('modal-form:x', 'w', 'f')]\n";
const OLD_CLAIMS: &str = "QUESTIONS = 'research/questions'\n\ndef current(root):\n    return root\n\ndef owed(cur, index, qdir, store):\n    import pathlib\n    return [['k1', 'new'], ['k2', 'triage']] if (pathlib.Path(cur) / 'second').exists() else [['k1', 'new']]\n";

/// A history of three commits, the last two the replayed ones, its own `scripts/record/` stand-ins.
fn history(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, PathBuf, Vec<String>) {
    let dir = scratch(tag);
    let root = dir.join("repo");
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    put(&root, "scripts/record/modal_owed.py", OLD_MODAL_OWED);
    put(&root, "scripts/record/claims.py", OLD_CLAIMS);
    put(&root, "dev/claims-index.json", "{}\n");
    let mut revs = Vec::new();
    for (i, file) in ["first", "second", "third"].iter().enumerate() {
        put(&root, file, &format!("{i}\n"));
        if i == 1 {
            std::fs::remove_file(root.join("dev/claims-index.json")).unwrap();
        }
        git(&root, &["add", "-A"]);
        git(&root, &["commit", "-qm", &format!("commit {file}")]);
        revs.push(git(&root, &["rev-parse", "HEAD"]));
    }
    (dir, root, revs)
}

fn env(root: &Path, cwd: &Path) -> Env {
    Env {
        root: root.to_path_buf(),
        cwd: cwd.to_path_buf(),
        python: "python3".to_owned(),
    }
}

/// A run that prints nothing a test reads.
fn quiet(_: &str) {}

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn each_commit_is_replayed_through_the_old_owing_and_the_new() {
    quiet("unused");
    let (dir, root, revs) = history("replay-run");
    let out = dir.join("out");
    let mut said = Vec::new();
    let done = run(
        &args(&[
            &revs[1],
            &revs[2],
            "--out",
            &out.to_string_lossy(),
            "--triage",
        ]),
        &env(&root, &dir),
        &mut |l| said.push(l.to_owned()),
    );
    assert_eq!((done.code, done.stderr.as_str()), (0, ""));
    let first: serde_json::Value = serde_json::from_str(&said[0]).unwrap();
    assert_eq!(first["subject"], "commit second");
    assert_eq!(first["modal_depiction_old"], 1);
    // owed at `second` less what `first` owed already
    assert_eq!(first["impl_drift_old"], 0);
    assert!(said[2].starts_with("{\"totals\": {\"modal_depiction_old\": 2"));
    // every worktree removed
    assert!(git(&root, &["worktree", "list"]).lines().count() == 1);
    assert!(out.join(format!("{}.index.json", &revs[2][..10])).is_file());
}

#[test]
fn a_relative_out_is_read_from_the_working_directory() {
    let (dir, root, revs) = history("replay-relative");
    let done = run(
        &args(&[&revs[1], "--out", "rel"]),
        &env(&root, &root),
        &mut quiet,
    );
    // the OLD snippet opens the index relative to its worktree, as the Python's did: a raise
    assert_eq!(done.code, 1);
    assert!(done.stderr.contains("Traceback"));
    assert!(root.join("rel").is_dir());
    let _ = dir;
}

#[test]
fn a_failure_is_a_raise_and_the_arguments_are_argparse_s() {
    let (dir, root, revs) = history("replay-fail");
    let out = dir.join("out").to_string_lossy().into_owned();
    let bad = run(
        &args(&["no-such-rev", "--out", &out]),
        &env(&root, &dir),
        &mut quiet,
    );
    assert_eq!(bad.code, 1);
    assert!(bad.stderr.contains("returned non-zero exit status"));
    // the root commit has no parent
    assert_eq!(
        run(
            &args(&[&revs[0], "--out", &out]),
            &env(&root, &dir),
            &mut quiet
        )
        .code,
        1
    );
    // an OLD snippet that cannot start
    let mut gone = env(&root, &dir);
    gone.python = "/no/such/python".to_owned();
    assert_eq!(
        run(&args(&[&revs[1], "--out", &out]), &gone, &mut quiet).code,
        1
    );
    put(&dir, "afile", "x");
    let under_file = dir.join("afile/out").to_string_lossy().into_owned();
    assert_eq!(
        run(
            &args(&[&revs[1], "--out", &under_file]),
            &env(&root, &dir),
            &mut quiet
        )
        .code,
        1
    );
    assert_eq!(run(&args(&[]), &env(&root, &dir), &mut quiet).code, 2);
    assert!(super::cli(&args(&["--bogus"]))
        .stderr
        .contains("unrecognized arguments"));
    let specs = [Spec::value("--out"), Spec::flag("--triage")];
    assert!(revs_of(&args(&["a", "--triage", "b"]), &specs)
        .unwrap_err()
        .contains("unrecognized arguments: b"));
    assert!(revs_of(&args(&["a", "--out", "x", "b"]), &specs).is_err());
    let (revs, out, triage) = revs_of(&args(&["--triage", "a", "b", "--out=/o"]), &specs).unwrap();
    assert_eq!(
        (revs, out.as_str(), triage),
        (args(&["a", "b"]), "/o", true)
    );
    assert_eq!(revs_of(&args(&["a"]), &specs).unwrap().1, "/tmp/l7r-replay");
}

#[test]
fn the_counts_are_the_python_s() {
    let rows = vec![
        ("a".to_owned(), "new".to_owned()),
        ("b".to_owned(), "triage".to_owned()),
        ("c".to_owned(), "section triage".to_owned()),
    ];
    assert_eq!(full(&rows), 1);
    assert_eq!(not_in(rows.clone(), &rows[..1].to_vec()).len(), 2);
    let modals = with_triage(vec![(
        "modal-depiction:a".to_owned(),
        "its own words moved".to_owned(),
        String::new(),
    )]);
    assert_eq!(counted(&modals, false) + counted(&modals, true), 1);
    let triaged = vec![
        ("modal-depiction:a".to_owned(), true),
        ("modal-form:b".to_owned(), true),
    ];
    assert!(wants_triage(true, &triaged) && !wants_triage(false, &triaged));
    assert!(!wants_triage(true, &[("modal-form:b".to_owned(), true)]));
    assert_eq!(
        depicted(&json!([["modal-depiction:a", "w"], ["x", "w"], [1, 2]])),
        1
    );
    assert_eq!(
        super::rows("[[\"k\", \"why\"]]").unwrap(),
        vec![("k".to_owned(), "why".to_owned())]
    );
    assert!(super::rows("nope").is_err());
    let dir = scratch("replay-objects");
    put(&dir, "list.json", "[]");
    put(&dir, "bad.json", "{");
    assert!(super::object(&dir.join("list.json")).is_err());
    assert!(super::object(&dir.join("bad.json")).is_err());
    assert!(super::object(&dir.join("none.json")).is_err());
    assert!(super::write_json(&dir.join("no/such/x.json"), &serde_json::Map::new()).is_err());
    assert!(super::loads("x").is_err());
    assert!(
        super::undecodable(String::from_utf8(vec![0xff]).unwrap_err())
            .starts_with("UnicodeDecodeError")
    );
    super::print_line("a replay row");
    // the bundle: none asked, then one on a tree with no pop-ups (its store variable put back as it was)
    assert_eq!(
        super::triage_bundle(false, "0123456789", &dir, "HEAD", &dir),
        Ok(())
    );
    assert!(super::triage_bundle(true, "0123456789", &dir, "HEAD", &dir).is_ok());
    assert!(std::env::var_os("RECORD_CHECKS_DIR").is_none());
    super::restore("L7R_REPLAY_TEST_RESTORE", Some("x".into()));
    assert_eq!(std::env::var("L7R_REPLAY_TEST_RESTORE").as_deref(), Ok("x"));
    super::restore("L7R_REPLAY_TEST_RESTORE", None);
    assert!(std::env::var_os("L7R_REPLAY_TEST_RESTORE").is_none());
}

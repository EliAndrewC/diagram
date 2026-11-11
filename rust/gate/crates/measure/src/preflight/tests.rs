//! The cases of `test_preflight.py` the phase and the tree check answer, with a stand-in for `make` and for the Python door.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use super::{
    parse, rolled_outputs, run, seen_moves, stray_probes, tree, tree_moved, unseen, Asked, Tools,
};

fn git(dir: &Path, args: &[&str]) -> String {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success());
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

const A: &str = "l7r/diagram/a.py";

fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    std::fs::create_dir_all(root.join("l7r/diagram")).unwrap();
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    std::fs::write(root.join(A), "x = 1\ny = 2\n").unwrap();
    std::fs::write(root.join("notes.md"), "n\n").unwrap();
    git(&root, &["init", "-q"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    root
}

/// Stand-ins for `make` (exit 0, or 3 for the target named in `fail`) and the door (answering `body`).
fn tools(root: &Path, fail: &str, door: &str) -> Tools {
    let (make, python) = (root.join("fake-make"), root.join("fake-python"));
    crate::write_executable(&make, &format!("#!/bin/sh\necho \"$@\" >> {}/make-ran\n[ \"$2\" = \"{fail}\" ] && {{ echo make-out; echo make-err >&2; exit 3; }}\nexit 0\n", root.display()));
    crate::write_executable(
        &python,
        &format!(
            "#!/bin/sh\necho \"$@\" >> {}/door-ran\n{door}\n",
            root.display()
        ),
    );
    crate::write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/bin/sh\nexit 0\n",
    );
    Tools {
        make: make.display().to_string(),
        python: python.display().to_string(),
    }
}

fn asked(root: &Path) -> Asked {
    Asked {
        root: root.display().to_string(),
        workers: "1".to_owned(),
        ..Asked::default()
    }
}

fn go(a: &Asked, t: &Tools) -> (i32, String) {
    let mut out = Vec::new();
    let code = run(a, t, &mut out);
    (code, String::from_utf8_lossy(&out).into_owned())
}

fn snap_of(root: &Path, t: &Tools) -> String {
    let snap = root.join("snap.json").display().to_string();
    assert_eq!(
        go(
            &Asked {
                tree_snap: snap.clone(),
                ..asked(root)
            },
            t
        )
        .0,
        0
    );
    snap
}

#[test]
fn flags_are_read() {
    let a = parse(
        &[
            "--root",
            "r",
            "--workers",
            "9",
            "--tree-snap",
            "s",
            "--tree-check",
            "c",
            "--census",
            "e",
            "--would-write",
            "w",
            "--content",
            "t",
            "--skip-quick",
            "--quiet",
            "--no-coverage",
            "--other",
        ]
        .map(str::to_owned),
    );
    assert_eq!(
        (
            a.root.as_str(),
            a.workers.as_str(),
            a.tree_snap.as_str(),
            a.tree_check.as_str(),
            a.census.as_str(),
            a.would_write.as_str(),
            a.content.as_str()
        ),
        ("r", "9", "s", "c", "e", "w", "t")
    );
    assert!(a.skip_quick && a.quiet);
    assert_eq!(parse(&[]).root, ".");
}

#[test]
fn a_tree_that_moves_while_the_gate_runs_is_named() {
    let root = repo("pf-moved");
    let t = tools(&root, "", "exit 1");
    std::fs::write(root.join("notes.md"), "an edit before the gate\n").unwrap();
    let snap = snap_of(&root, &t);
    let kept: BTreeMap<String, String> =
        serde_json::from_str(&std::fs::read_to_string(&snap).unwrap()).unwrap();
    assert_eq!(kept.keys().collect::<Vec<_>>(), ["HEAD", "notes.md"]);
    let check = Asked {
        tree_check: snap.clone(),
        ..asked(&root)
    };
    assert_eq!(go(&check, &t).0, 0);
    std::fs::write(root.join(A), "x = 9\n").unwrap();
    let (code, out) = go(&check, &t);
    assert!(code == 1 && out.contains(A) && out.starts_with("GATE NOT GREEN"));
    git(&root, &["commit", "-qam", "mid-gate"]);
    let (code, out) = go(&check, &t);
    assert!(code == 1 && out.contains(A));
    let quiet = Asked {
        quiet: true,
        tree_check: snap,
        ..asked(&root)
    };
    assert_eq!(go(&quiet, &t), (1, String::new()));
    let none = Asked {
        tree_check: root.join("missing.json").display().to_string(),
        ..asked(&root)
    };
    assert_eq!(go(&none, &t).0, 0);
}

#[test]
fn a_head_that_cannot_be_read_stays_and_the_map_arithmetic_holds() {
    let root = repo("pf-head");
    let t = tools(&root, "", "exit 1");
    let side = |s: &str| BTreeMap::from([("HEAD".to_owned(), s.repeat(40))]);
    assert_eq!(seen_moves(&root, &t, &side("0"), &side("1")), ["HEAD"]);
    assert!(seen_moves(&root, &t, &side("0"), &side("0")).is_empty());
    let a = BTreeMap::from([
        ("HEAD".to_owned(), "a".to_owned()),
        ("x".to_owned(), "1".to_owned()),
    ]);
    let b = BTreeMap::from([
        ("HEAD".to_owned(), "a".to_owned()),
        ("x".to_owned(), "2".to_owned()),
        ("y".to_owned(), "3".to_owned()),
    ]);
    assert_eq!(tree_moved(&a, &b), ["x", "y"]);
}

#[test]
fn the_tree_records_what_differs_and_not_what_the_gate_writes() {
    let root = repo("pf-tree");
    std::fs::create_dir(root.join("dev")).unwrap();
    std::fs::write(root.join("dev/known-seeds.txt"), "1\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "seeds"]);
    std::fs::write(root.join("dev/known-seeds.txt"), "2\n").unwrap();
    assert_eq!(tree(&root).len(), 1);
    std::fs::write(root.join("notes.md"), "z\n").unwrap();
    let got = tree(&root);
    assert!(got["notes.md"].len() == 40 && got.len() == 2);
    std::fs::remove_file(root.join("notes.md")).unwrap();
    assert_eq!(tree(&root)["notes.md"], "?", "a path that cannot be hashed");
}

fn change(path: &str, old: Option<&[u8]>, new: Option<&[u8]>) -> super::Change {
    (
        path.to_owned(),
        old.map(<[u8]>::to_vec),
        new.map(<[u8]>::to_vec),
    )
}

#[test]
fn a_change_the_gate_does_not_see_does_not_move_the_tree() {
    let root = repo("pf-unseen");
    std::fs::create_dir(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        "{\"feature_directory\": \"specs/405-x/\"}",
    )
    .unwrap();
    let door = "cat > /dev/null; exit 1";
    let t = tools(&root, "", door);
    let is = |c: super::Change| unseen(&root, &t, std::slice::from_ref(&c)).contains(&c.0);
    assert!(is(change("notes.md", Some(b"a"), Some(b"a"))));
    assert!(is(change(
        "dev/claims-index.json",
        Some(b"{}"),
        Some(b"{1}")
    )));
    assert!(is(change("specs/405-x/found.jsonl", None, Some(b"r"))));
    assert!(is(change(
        "dev/cohort-log/20261021T1046Z-x.json",
        None,
        Some(b"{}")
    )));
    assert!(!is(change(
        "dev/cohort-log/20261021T1046Z-x.json",
        Some(b"{}"),
        Some(b"{1}")
    )));
    assert!(!is(change("dev/cohort-log/CLAUDE.md", None, Some(b"x"))));
    assert!(!is(change("notes.md", Some(b"a"), Some(b"b"))));
    assert!(!is(change("specs/405-x/plan.md", Some(b"a"), Some(b"b"))));
    assert!(!is(change("specs/406-y/tasks.md", Some(b"a"), Some(b"b"))));
    assert!(!is(change(A, Some(b"a"), None)));
    assert!(!root.join("door-ran").exists());
    assert!(!is(change(A, Some(b"a"), Some(b"b"))));
    assert!(root.join("door-ran").exists());
    std::fs::write(root.join(".specify/feature.json"), "not json").unwrap();
    assert!(!is(change(
        "specs/405-x/found.jsonl",
        Some(b"a"),
        Some(b"b")
    )));
}

#[test]
fn the_door_is_asked_once_for_every_python_file() {
    let root = repo("pf-door");
    let t = tools(&root, "", "cat > /dev/null; printf '1\\n0\\n'");
    let batch = [
        change("l7r/one.py", Some(b"a"), Some(b"b")),
        change("l7r/two.py", Some(b"c"), Some(b"d")),
    ];
    let got = unseen(&root, &t, &batch);
    assert_eq!(got, BTreeSet::from(["l7r/one.py".to_owned()]));
    assert_eq!(
        std::fs::read_to_string(root.join("door-ran"))
            .unwrap()
            .lines()
            .count(),
        1
    );
}

#[test]
fn the_guards_question_about_a_write_is_answered() {
    let root = repo("pf-would");
    let t = tools(&root, "", "exit 1");
    let snap = snap_of(&root, &t);
    let content = root.join("c");
    std::fs::write(&content, "x = 1\ny = 2\n").unwrap();
    let ask = |rel: &str, from: &Path| Asked {
        tree_check: snap.clone(),
        would_write: rel.to_owned(),
        content: from.display().to_string(),
        ..asked(&root)
    };
    assert_eq!(go(&ask(A, &content), &t).0, 0);
    std::fs::write(&content, "z\n").unwrap();
    assert_eq!(go(&ask("notes.md", &content), &t).0, 1);
    assert_eq!(
        go(
            &Asked {
                content: String::new(),
                ..ask("dev/claims-index.json", &content)
            },
            &t
        )
        .0,
        0
    );
    assert_eq!(
        go(
            &Asked {
                tree_check: root.join("missing").display().to_string(),
                ..ask(A, &content)
            },
            &t
        )
        .0,
        1
    );
    std::fs::write(root.join("notes.md"), "edited\n").unwrap();
    let edited = snap_of(&root, &t);
    assert_eq!(
        go(
            &Asked {
                tree_check: edited,
                ..ask("notes.md", &content)
            },
            &t
        )
        .0,
        1
    );
}

#[test]
fn a_snapshot_that_cannot_be_written_fails() {
    let root = repo("pf-nosnap");
    let t = tools(&root, "", "exit 1");
    assert_eq!(
        go(
            &Asked {
                tree_snap: "/nonexistent/x/snap".to_owned(),
                ..asked(&root)
            },
            &t
        )
        .0,
        1
    );
}

#[test]
fn a_pool_map_the_gate_rolled_itself_is_no_tree_move_and_another_maps_still_is() {
    let root = repo("pf-rolled");
    for m in ["kuwa", "other"] {
        let d = root.join("pool/hamlets").join(m);
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join(format!("{m}.gen.py")), "x = 1\n").unwrap();
        std::fs::write(d.join(format!("{m}.json")), "{}\n").unwrap();
    }
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "maps"]);
    let t = tools(&root, "", "exit 1");
    let snap = snap_of(&root, &t);
    let census = root.join("census.jsonl");
    std::fs::write(
        &census,
        format!(
            "{{\"kind\": \"roll\", \"gen\": \"{}/pool/hamlets/kuwa/kuwa.gen.py\"}}\n",
            root.display()
        ),
    )
    .unwrap();
    std::fs::write(
        root.join("pool/hamlets/kuwa/kuwa.json"),
        "{\"rolled\": 1}\n",
    )
    .unwrap();
    let check = Asked {
        tree_check: snap,
        census: census.display().to_string(),
        ..asked(&root)
    };
    let (code, out) = go(&check, &t);
    assert!(code == 0 && out.contains("re-rolled by the gate - commit them"));
    std::fs::write(
        root.join("pool/hamlets/other/other.json"),
        "{\"hand\": 1}\n",
    )
    .unwrap();
    let (code, out) = go(&check, &t);
    assert!(code == 1 && out.contains("pool/hamlets/other/other.json"));
}

#[test]
fn only_a_rolled_generator_under_the_root_names_outputs() {
    let root = repo("pf-census");
    let census = root.join("c.jsonl");
    std::fs::write(&census, "not json\n{\"kind\": \"view\", \"gen\": \"x/a.gen.py\"}\n{\"kind\": \"roll\", \"gen\": \"/elsewhere/b.gen.py\"}\n{\"kind\": \"roll\", \"gen\": \"x/c.py\"}\n{\"kind\": \"roll\"}\n").unwrap();
    assert!(rolled_outputs(&root, &census).is_empty());
    assert!(rolled_outputs(&root, &root.join("none")).is_empty());
}

#[test]
fn a_probe_test_left_in_the_tree_stops_the_gate() {
    let root = crate::checks::scratch("pf-probe");
    std::fs::create_dir_all(root.join("tests/tooling")).unwrap();
    assert!(stray_probes(&root).is_empty());
    std::fs::write(root.join("tests/tooling/test_zz_probe_a05.py"), "").unwrap();
    std::fs::write(
        root.join("tests/tooling/test_zz_probe_old.cpython-314.pyc"),
        "",
    )
    .unwrap();
    assert_eq!(stray_probes(&root), ["tests/tooling/test_zz_probe_a05.py"]);
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    let t = tools(&root, "", "exit 1");
    let (code, out) = go(&asked(&root), &t);
    assert!(code == 1 && out.contains("test_zz_probe_a05.py"));
}

#[test]
fn skip_quick_runs_no_quick_and_a_regenerated_file_is_named() {
    let root = repo("pf-skip");
    let mut t = tools(&root, "", "exit 1");
    let make = root.join("fake-make2");
    crate::write_executable(&make, &format!("#!/bin/sh\n[ \"$2\" = docs ] && echo more >> {}/notes.md\n[ \"$2\" = quick ] && touch {}/quick-ran\nexit 0\n", root.display(), root.display()));
    t.make = make.display().to_string();
    let (code, out) = go(
        &Asked {
            skip_quick: true,
            ..asked(&root)
        },
        &t,
    );
    assert!(code == 0 && out.contains("regenerated, commit them with the change:\n  notes.md"));
    assert!(!root.join("quick-ran").exists());
}

#[test]
fn each_step_that_fails_stops_the_phase_and_says_so() {
    for (target, words) in [
        ("docs", "`make docs` failed"),
        ("record", "the record does not build"),
        ("quick", "`make quick` failed"),
    ] {
        let root = repo(&format!("pf-fail-{target}"));
        let t = tools(&root, target, "exit 1");
        let (code, out) = go(&Asked { ..asked(&root) }, &t);
        assert!(code == 1 && out.contains(words));
        if target != "quick" {
            assert!(out.contains("make-out") && out.contains("make-err"));
        }
    }
    let root = repo("pf-fail-pointers");
    let t = tools(&root, "", "exit 1");
    crate::write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/bin/sh\nexit 1\n",
    );
    let (code, out) = go(&Asked { ..asked(&root) }, &t);
    assert!(code == 1 && out.contains("a research pointer does not resolve"));
    let mut gone = tools(&root, "", "exit 1");
    gone.make = "/nonexistent/make".to_owned();
    assert_eq!(go(&Asked { ..asked(&root) }, &gone).0, 1);
}

#[test]
fn a_tree_outside_a_repository_says_nothing_and_an_unreadable_head_is_named() {
    let bare = crate::checks::scratch("pf-norepo");
    assert_eq!(tree(&bare)["HEAD"], "");
    let root = repo("pf-headname");
    let t = tools(&root, "", "exit 1");
    let snap = root.join("h.json");
    std::fs::write(&snap, format!("{{\"HEAD\": \"{}\"}}", "0".repeat(40))).unwrap();
    let (code, out) = go(
        &Asked {
            tree_check: snap.display().to_string(),
            ..asked(&root)
        },
        &t,
    );
    assert!(code == 1 && out.contains("HEAD (a commit or a checkout)"));
}

#[test]
fn a_long_failure_shows_its_tail() {
    let root = repo("pf-long");
    let mut t = tools(&root, "", "exit 1");
    let make = root.join("fake-make3");
    crate::write_executable(
        &make,
        "#!/bin/sh\nhead -c 4000 /dev/zero | tr '\\\\0' x\nexit 3\n",
    );
    t.make = make.display().to_string();
    let (code, out) = go(&Asked { ..asked(&root) }, &t);
    assert!(code == 1 && out.matches('x').count() < 3100);
}

#[test]
fn a_root_that_is_not_there_stops_the_phase() {
    let root = crate::checks::scratch("pf-noroot");
    let t = tools(
        &{
            std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
            root.to_path_buf()
        },
        "",
        "exit 1",
    );
    assert_eq!(
        go(
            &Asked {
                root: "/nonexistent/r".to_owned(),
                ..Asked::default()
            },
            &t
        )
        .0,
        1
    );
}

#[test]
fn the_command_line_runs_the_snapshot() {
    let root = repo("pf-cli");
    let snap = root.join("s.json");
    let got = super::cli(
        &[
            "--root",
            &root.display().to_string(),
            "--tree-snap",
            &snap.display().to_string(),
        ]
        .map(str::to_owned),
    );
    assert_eq!(got.code, 0);
    assert!(snap.is_file());
}

#[test]
fn the_phase_runs_its_steps_and_ends_clean() {
    let root = repo("pf-steps");
    let t = tools(&root, "", "exit 1");
    let (code, out) = go(&asked(&root), &t);
    assert!(code == 0 && out.contains("preflight: clean in"));
    let ran = std::fs::read_to_string(root.join("make-ran")).unwrap();
    assert!(
        ran.contains("docs")
            && ran.contains("glossary")
            && ran.contains("record CHECK=1")
            && ran.contains("quick FROM_PREFLIGHT=1")
    );
}

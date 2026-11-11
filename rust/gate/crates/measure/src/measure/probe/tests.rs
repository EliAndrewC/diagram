//! Every seed beside HEAD's, the pool by field, and HEAD rolled once per engine key.

use std::cell::RefCell;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::json;

use super::{cli, compare, drive, manifest_diff, mark, record_of, verdicts, Live, Runs, Verdicts};

fn sets(list: &[(i64, &[&str])]) -> Verdicts {
    list.iter()
        .map(|(s, f)| (*s, f.iter().map(|x| (*x).to_owned()).collect()))
        .collect()
}

#[test]
fn every_seed_is_printed_beside_head_s_and_a_new_failing_check_is_worse() {
    let head = sets(&[
        (1, &[]),
        (2, &["lane_knots[2]"]),
        (3, &["a[1]"]),
        (4, &[]),
        (5, &["b[1]"]),
    ]);
    let now = sets(&[
        (1, &[]),
        (2, &["lane_knots[2]"]),
        (3, &[]),
        (4, &["c[1]"]),
        (5, &["b[3]"]),
        (6, &[]),
    ]);
    let (lines, worse) = compare(&head, &now);
    let line = |s: &str| {
        lines
            .iter()
            .find(|l| l.trim_start().starts_with(s))
            .unwrap()
    };
    assert!(
        line("1 ").contains("same pass")
            && line("2 ").contains("same failure")
            && line("3 ").contains("FIXED")
            && line("4 ").contains("NEW FAILURE")
    );
    assert!(
        line("5 ").contains("changed failure") && line("6 ").contains("new seed") && worse == 1
    );
    let a = vec!["a[1]".to_owned()];
    assert_eq!(mark(Some(&vec![]), None), "not rolled");
    assert_eq!(
        mark(Some(&a), Some(&vec!["a[1]".to_owned(), "z[1]".to_owned()])),
        "NEW FAILURE"
    );
    assert!(lines.iter().any(|l| l.contains("HEAD: -")));
    let gone = compare(&sets(&[(9, &[])]), &sets(&[])).0;
    assert!(gone[0].contains("not rolled") && gone[0].contains("now: -"));
}

#[test]
fn a_manifest_s_moved_fields_are_listed_by_path_points_as_drawn() {
    let old =
        json!({"lanes": [{"pts": [[1.04, 2.0]], "w": 3}], "meta": {"x": 1}, "houses": [1, 2]});
    let new = json!({"lanes": [{"pts": [[1.0, 2.0]], "w": 5}], "meta": {"x": 1, "y": 2}, "houses": [1, 2, 3]});
    assert_eq!(
        manifest_diff(&old, &new),
        ["houses", "lanes[0].w", "meta.y"]
    );
    assert_eq!(manifest_diff(&json!(1), &json!(2)), ["(the manifest)"]);
}

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

fn repo(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    std::fs::create_dir_all(root.join("pool/hamlets/a")).unwrap();
    std::fs::write(root.join("pool/hamlets/a/a.gen.py"), "x\n").unwrap();
    std::fs::write(root.join("pool/hamlets/a/a.json"), "{\"lanes\": 1}\n").unwrap();
    std::fs::write(root.join("pool/hamlets/a/notes.txt"), "x\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    root
}

#[test]
fn a_cohort_s_record_is_read_from_the_clone_and_its_verdicts_kept() {
    let root = repo("probe-record");
    std::fs::create_dir_all(root.join("dev/cohort-log")).unwrap();
    std::fs::write(
        root.join("dev/cohort-log/r.json"),
        json!({"seeds": [{"seed": 3, "failures": ["b[1]", "a[2]"]}]}).to_string(),
    )
    .unwrap();
    let h = Fake::new(&root);
    let got = record_of(
        &h,
        "...\nrecord committed (fail): dev/cohort-log/r.json\n",
        &root,
    )
    .unwrap();
    assert_eq!(verdicts(&got), sets(&[(3, &["a[2]", "b[1]"])]));
    let abs = root.join("dev/cohort-log/r.json").display().to_string();
    assert!(record_of(&h, &format!("record committed (x): {abs}"), &root).is_ok());
    assert!(record_of(&h, "nothing", &root)
        .unwrap_err()
        .contains("wrote no record"));
    assert!(record_of(&h, "record committed (x): /no/such.json", &root).is_err());
}

/// Stands in for make and the gate: a cohort writes a record whose failing seeds are `failing`.
struct Fake {
    root: PathBuf,
    failing: RefCell<BTreeMap<String, Vec<i64>>>,
    rolls: RefCell<Vec<String>>,
    n: RefCell<u32>,
    record: RefCell<bool>,
}

impl Fake {
    fn new(root: &Path) -> Self {
        Self {
            root: root.to_path_buf(),
            failing: RefCell::new(BTreeMap::new()),
            rolls: RefCell::new(Vec::new()),
            n: RefCell::new(0),
            record: RefCell::new(true),
        }
    }
}

impl Runs for Fake {
    fn run(&self, cmd: &[String], dir: &Path) -> (i32, String) {
        if cmd[0] == "git" {
            if cmd.iter().any(|w| w == "worktree") {
                if cmd.iter().any(|w| w == "add") {
                    std::fs::create_dir_all(dir.join("x")).unwrap();
                }
                return (0, String::new());
            }
            let o = Command::new(&cmd[0]).args(&cmd[1..]).output().unwrap();
            return (0, String::from_utf8_lossy(&o.stdout).into_owned());
        }
        if cmd[1] == "cohort" {
            return (
                0,
                if cmd[2] == "fresh-seed" {
                    "700\n".to_owned()
                } else {
                    "k1\n".to_owned()
                },
            );
        }
        if cmd.iter().any(|w| w == "cohort") {
            let who = if dir.file_name().unwrap() == "head" {
                "head"
            } else {
                "now"
            };
            self.rolls.borrow_mut().push(who.to_owned());
            let seed: i64 = cmd
                .iter()
                .find_map(|a| a.strip_prefix("SEED="))
                .map_or(1, |s| s.parse().unwrap());
            *self.n.borrow_mut() += 1;
            let n = *self.n.borrow();
            let bad = self.failing.borrow().get(who).cloned().unwrap_or_default();
            let seeds: Vec<_> = [seed, seed + 1].iter().map(|s| json!({"seed": s, "failures": if bad.contains(s) { json!(["c[1]"]) } else { json!([]) }})).collect();
            let path = self.root.join(format!("dev/cohort-log/{n}.json"));
            std::fs::create_dir_all(path.parent().unwrap()).unwrap();
            std::fs::write(path, json!({"seeds": seeds}).to_string()).unwrap();
            if !*self.record.borrow() {
                return (0, "no record".to_owned());
            }
            return (
                0,
                format!("record committed (pass): dev/cohort-log/{n}.json"),
            );
        }
        (0, String::new())
    }
}

fn say(args: &[&str], root: &Path, h: &Fake) -> crate::Reply {
    let owned: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    drive(&owned, root, h)
}

#[test]
fn head_is_rolled_once_per_engine_key_and_the_probe_is_red_on_a_worse_seed() {
    let root = repo("probe-run");
    let h = Fake::new(&root);
    h.failing.borrow_mut().insert("now".to_owned(), vec![2]);
    h.failing.borrow_mut().insert("head".to_owned(), vec![700]);
    let got = say(&[], &root, &h);
    assert_eq!(got.code, 1);
    assert!(
        got.stdout.contains("NEW FAILURE")
            && got.stdout.contains("the pool against HEAD:")
            && got.stdout.contains("a: unchanged")
    );
    assert_eq!(h.rolls.borrow().iter().filter(|r| *r == "head").count(), 2);
    h.rolls.borrow_mut().clear();
    h.failing.borrow_mut().clear();
    std::fs::write(root.join("pool/hamlets/a/a.json"), "{\"lanes\": 2}\n").unwrap();
    let again = say(&["--exitfirst", "--jobs", "2"], &root, &h);
    assert_eq!(again.code, 0);
    assert_eq!(h.rolls.borrow().iter().filter(|r| *r == "head").count(), 0);
    assert!(again.stdout.contains("a: 1 field(s) moved - lanes"));
}

#[test]
fn a_cohort_that_writes_no_record_stops_the_probe_and_many_moved_fields_are_trimmed() {
    let root = repo("probe-none");
    let h = Fake::new(&root);
    *h.record.borrow_mut() = false;
    let got = say(&["--wt", root.to_str().unwrap()], &root, &h);
    assert!(got.code == 1 && got.stderr.contains("wrote no record"));
    *h.record.borrow_mut() = true;
    h.failing.borrow_mut().insert("now".to_owned(), vec![1]);
    let many: serde_json::Map<String, serde_json::Value> =
        (0..12).map(|n| (format!("k{n}"), json!(n))).collect();
    std::fs::write(
        root.join("pool/hamlets/a/a.json"),
        serde_json::Value::Object(many).to_string(),
    )
    .unwrap();
    let wide = say(&["--exitfirst"], &root, &h);
    assert!(wide.stdout.contains(" ...") && wide.stdout.contains("EXITFIRST stopped at the first"));
    let bad = say(&["--wt", "/no/such/tree"], &root, &h);
    assert_eq!(bad.code, 1);
}

#[test]
fn the_live_runner_runs_and_a_missing_program_answers_127() {
    let dir = crate::checks::scratch("probe-live");
    let (code, out) = Live.run(&["echo".to_owned(), "x".to_owned()], &dir);
    assert!(code == 0 && out.contains('x'));
    assert_eq!(Live.run(&["/no/such".to_owned()], &dir).0, 127);
    assert_eq!(cli(&[], &dir).code, 1);
}

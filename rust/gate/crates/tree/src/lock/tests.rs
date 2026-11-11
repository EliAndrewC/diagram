//! The gate's lock and the make a waiter waits for, over a process table of the test's own.

use std::path::Path;

use serde_json::json;

use super::{acquire, cli, held, own_make, own_make_cli, running_gate};
use crate::checks::scratch;

fn process(table: &Path, pid: u64, words: &[&str], cwd: Option<&Path>) {
    let dir = table.join(pid.to_string());
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("cmdline"), words.join("\0") + "\0").unwrap();
    if let Some(at) = cwd {
        std::os::unix::fs::symlink(at, dir.join("cwd")).unwrap();
    }
}

#[test]
fn a_second_gate_is_refused_while_the_first_lives_and_its_owner_never_is() {
    let (git, table) = (scratch("lock-git"), scratch("lock-proc"));
    process(
        &table,
        77,
        &["make", "--no-print-directory", "done", "FULL=1"],
        None,
    );
    assert_eq!(acquire(&git, 77, &table, 100.0), "");
    let why = acquire(&git, 4242, &table, 200.0);
    assert!(
        why.contains("already running in this clone (pid 77") && why.contains("started 00:01:40")
    );
    assert_eq!(acquire(&git, 77, &table, 300.0), "");
}

#[test]
fn a_dead_or_unrelated_owner_holds_nothing() {
    let (git, table) = (scratch("lock-git"), scratch("lock-proc"));
    std::fs::write(git.join("gate.lock"), json!({"pid": 5, "t": 1}).to_string()).unwrap();
    assert_eq!(acquire(&git, 4242, &table, 1.0), "");
    process(&table, 1, &["sleep", "30"], None);
    std::fs::write(git.join("gate.lock"), json!({"pid": 1, "t": 1}).to_string()).unwrap();
    assert_eq!(acquire(&git, 4242, &table, 1.0), "");
    std::fs::write(git.join("gate.lock"), "not json").unwrap();
    assert_eq!(acquire(&git, 4242, &table, 1.0), "");
    let text = std::fs::read_to_string(git.join("gate.lock")).unwrap();
    assert!(text.contains("\"pid\":4242"));
}

#[test]
fn the_running_gate_is_read_from_the_command_line() {
    let table = scratch("lock-proc");
    assert!(!running_gate(&table, 999));
    process(&table, 2, &["/usr/bin/gmake", "done"], None);
    process(&table, 3, &["python3", "make", "done"], None);
    process(&table, 4, &["make", "quick"], None);
    assert!(running_gate(&table, 2) && !running_gate(&table, 3) && !running_gate(&table, 4));
}

#[test]
fn held_says_whether_a_live_gate_owns_the_clone() {
    let (git, table) = (scratch("lock-git"), scratch("lock-proc"));
    let owned = |pid: u64| json!({"pid": pid, "t": 1}).to_string();
    assert!(!held(&git, &table));
    assert_eq!(
        cli(&["held".to_owned(), git.display().to_string()], &table).code,
        1
    );
    process(&table, 8, &["make", "done"], None);
    std::fs::write(git.join("gate.lock"), owned(8)).unwrap();
    assert!(held(&git, &table));
    assert_eq!(
        cli(&["held".to_owned(), git.display().to_string()], &table).code,
        0
    );
    std::fs::write(git.join("gate.lock"), owned(9)).unwrap();
    assert!(!held(&git, &table));
    std::fs::write(git.join("gate.lock"), "not json").unwrap();
    assert!(!held(&git, &table));
}

#[test]
fn the_command_line_acquires_refuses_and_says_how_to_use_it() {
    let (git, table) = (scratch("lock-git"), scratch("lock-proc"));
    let dir = git.display().to_string();
    process(&table, 8, &["make", "done"], None);
    let ask = |words: &[&str]| {
        cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &table,
        )
    };
    assert_eq!(ask(&["acquire", &dir, "8"]).code, 0);
    let refused = ask(&["acquire", &dir, "9"]);
    assert!(refused.code == 1 && refused.stderr.starts_with("\nGATE REFUSED: a `make done`"));
    assert_eq!(ask(&[]).code, 2);
}

#[test]
fn only_a_make_of_this_target_in_this_tree_counts() {
    let (table, top) = (scratch("own-proc"), scratch("own-top"));
    let sub = top.join("sub");
    std::fs::create_dir_all(&sub).unwrap();
    let other = scratch("own-other");
    process(&table, 1, &["make", "done"], Some(&sub));
    process(&table, 2, &["make", "map GEN=x"], Some(&other));
    process(&table, 3, &["bash", "-c", "make quick & until"], Some(&top));
    process(&table, 4, &["make quick x"], Some(&top));
    assert!(own_make(&table, &top, "done"));
    assert!(!own_make(&table, &top, "map GEN=x"), "another tree's");
    assert!(!own_make(&table, &top, "cohort"));
    assert!(own_make(&table, &top, "quick"));
    assert!(!own_make(&table, &top, "(["));
    process(&table, 5, &["bash", "-c", "make zed"], Some(&top));
    assert!(!own_make(&table, &top, "zed"));
}

#[test]
fn the_own_make_command_says_how_to_use_it() {
    let table = scratch("own-proc");
    assert_eq!(own_make_cli(&[], &table).code, 2);
    assert_eq!(own_make_cli(&["done".to_owned()], &table).code, 1);
}

#[test]
fn outside_a_repository_the_tree_is_where_it_was_asked() {
    assert!(super::top_of(Path::new(".")).is_absolute());
}

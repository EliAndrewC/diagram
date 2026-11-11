//! What is removed, what is refused, and what is none of this check's business.

use super::super::scratch;
use super::super::tests::put;
use super::{check, cli, only_bytecode, stale_dirs};

fn cache(dir: &std::path::Path, rel: &str) {
    put(dir, &format!("{rel}/__pycache__/m.cpython-314.pyc"), "x");
}

#[test]
fn it_removes_a_directory_holding_only_bytecode() {
    let dir = scratch("remove");
    cache(&dir, "l7r/diagram/gone");
    let done = check(&dir);
    assert_eq!(done.code, 0);
    assert!(
        done.stdout.contains("removed l7r/diagram/gone") && !dir.join("l7r/diagram/gone").exists()
    );
}

#[test]
fn it_refuses_a_stale_directory_holding_anything_but_bytecode() {
    let dir = scratch("refuse");
    put(&dir, "l7r/gone/__pycache__/notes.txt", "x");
    let done = check(&dir);
    assert_eq!(done.code, 1);
    assert!(
        done.stdout.contains("STALE DIRECTORIES")
            && done.stdout.contains("rm -rf l7r/gone")
            && dir.join("l7r/gone").exists()
    );
    std::fs::create_dir_all(dir.join("tests/g/__pycache__/sub")).unwrap();
    assert!(!only_bytecode(&dir.join("tests/g")));
}

#[test]
fn a_real_package_a_data_directory_a_fresh_clone_and_other_trees_are_left_alone() {
    let dir = scratch("alone");
    cache(&dir, "l7r/alive");
    put(&dir, "l7r/alive/mod.py", "x");
    put(&dir, "tests/data/fixture.json", "{}");
    std::fs::create_dir_all(dir.join("tests/empty")).unwrap();
    cache(&dir, "pool/leftover");
    cache(&dir, "l7r/.venv/x");
    assert_eq!(stale_dirs(&dir), Vec::<std::path::PathBuf>::new());
    assert_eq!(check(&dir), super::Outcome::out(String::new()));
}

#[test]
fn a_link_to_a_directory_is_not_descended() {
    let dir = scratch("link");
    cache(&dir, "elsewhere/stale");
    std::fs::create_dir_all(dir.join("l7r")).unwrap();
    put(&dir, "l7r/mod.py", "x");
    std::os::unix::fs::symlink(dir.join("elsewhere"), dir.join("l7r/link")).unwrap();
    assert_eq!(stale_dirs(&dir), Vec::<std::path::PathBuf>::new());
}

#[test]
fn the_command_line_takes_a_root_and_a_self_test() {
    let dir = scratch("cli");
    assert_eq!(cli(&[dir.display().to_string()]).code, 0);
    assert!(cli(&["--selftest".to_owned()])
        .stdout
        .contains("selftest ok"));
    assert_eq!(cli(&[]).code, 0);
}

#[test]
fn the_tree_is_clean() {
    let real = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    assert_eq!(check(&real).code, 0);
}

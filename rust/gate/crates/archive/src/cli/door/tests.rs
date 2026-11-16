//! The one door left (feature 449 T146; T147 retired the other eight with the Python that called them).

use super::cli;
use crate::testkit::{git, World};

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|a| (*a).to_owned()).collect()
}

#[test]
fn push_says_gits_complaint_or_nothing() {
    let w = World::new("door-push");
    let home = w.home.to_string_lossy().into_owned();
    let r = cli(&args(&["--home", &home]));
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", "/no/such.git"],
    );
    w.store()
        .put("x/T", &[("f".to_owned(), b"1".to_vec())], "one")
        .unwrap();
    let r = cli(&args(&["--home", &home]));
    assert_eq!(r.code, 0);
    assert!(!r.stdout.trim().is_empty());
    assert_eq!(cli(&args(&["--bogus"])).code, 2);
    // a push that goes through into a home whose counter cannot be written (a directory where the counter goes): the push's raise
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", &w.remote.to_string_lossy()],
    );
    let counter = w.home.join(crate::store::UNPUSHED);
    std::fs::remove_file(&counter).ok();
    std::fs::create_dir_all(&counter).unwrap();
    let r = cli(&args(&["--home", &home]));
    assert_eq!((r.code, r.stderr.split(':').next()), (1, Some("OSError")),);
}

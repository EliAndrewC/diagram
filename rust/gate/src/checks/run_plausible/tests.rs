//! A run too fast to have worked does not get to say it passed.

use super::{baseline, check, cli, dry_run, floor_for, ABSOLUTE_MIN};
use crate::checks::scratch;

fn root() -> std::path::PathBuf {
    let dir = scratch("plausible");
    std::fs::create_dir_all(dir.join("scripts/measure")).unwrap();
    std::fs::write(dir.join("scripts/measure/ratchet.py"), "RATCHETS = {\n    \"quick\": Ratchet(\n        target=\"quick\",\n        baseline=11,\n        hard=15,\n    ),\n    \"done\": Ratchet(\n        target=\"done\",\n        baseline=400,\n    ),\n    \"zero\": Ratchet(\n        baseline=0,\n    ),\n}\n").unwrap();
    dir
}

fn ask(dir: &std::path::Path, flags: &str, words: &[&str]) -> super::Outcome {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, dir, flags)
}

#[test]
fn a_dry_run_may_not_record_and_only_the_flag_word_says_so() {
    assert!(check(&root(), "done", 320.0, "n", "full")
        .unwrap()
        .contains("DRY RUN"));
    assert!(dry_run("n") && dry_run("nrR"));
    assert!(
        !dry_run("") && !dry_run("REASON=nothing") && !dry_run("-- REASON=iterating on Inashiro")
    );
}

#[test]
fn a_run_below_the_floor_may_not_record_and_an_incremental_run_has_the_absolute_floor() {
    let dir = root();
    assert!(check(&dir, "done", 4.0, "", "full")
        .unwrap()
        .contains("floor"));
    assert_eq!(check(&dir, "done", 320.0, "", "full"), None);
    assert_eq!(check(&dir, "done", 6.0, "", "incremental"), None);
    assert!(check(&dir, "done", 4.0, "", "incremental").is_some());
    assert_eq!(check(&dir, "no-such-target", 0.0, "", "full"), None);
}

#[test]
fn the_floor_is_derived_from_the_pinned_ratchet_baseline() {
    let dir = root();
    assert_eq!(floor_for(&dir, "done"), Some(40));
    assert_eq!(floor_for(&dir, "quick"), Some(ABSOLUTE_MIN));
    assert_eq!(baseline(&dir, "quick"), Some(11));
    assert_eq!(floor_for(&dir, "no-such-target"), None);
    assert_eq!(floor_for(&dir, "zero"), None);
    assert_eq!(baseline(&scratch("no-ratchet"), "done"), None);
}

#[test]
fn the_reuse_path_is_guarded_too_and_the_command_line_says_how_to_use_it() {
    let dir = root();
    let refused = ask(&dir, "n", &["--reuse", "done"]);
    assert!(refused.code == 1 && refused.stderr.contains("DRY RUN"));
    assert_eq!(ask(&dir, "", &["--reuse", "done"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "not-a-number"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "320"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "4", "incremental"]).code, 1);
    assert_eq!(ask(&dir, "", &[]).code, 2);
}

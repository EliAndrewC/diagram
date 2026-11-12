//! `make phase-read` and a phase task's held files (feature 449 T131, from `gates/phase_sources.py`).

use l7r_gate_core::ci::fixtures::put;
use serde_json::json;

use super::{cli, holds, phase_of, record, resolved};
use crate::tests::{repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_block_s_phase_and_old_code() {
    assert_eq!(phase_of("- [ ] T01 x\n"), (String::new(), Vec::new()));
    let (phase, extra) = phase_of(
        "- [ ] T01 x\n   phase: water_frame  \n   old-code: a/*.py  b.py\n  old-code: c\n",
    );
    assert_eq!(phase, "water_frame");
    assert_eq!(extra, vec!["a/*.py", "b.py", "c"]);
}

#[test]
fn a_held_file_is_let_through_for_ten_minutes_with_its_reason() {
    let dir = repo("phase-read");
    let root = root_of(&dir);
    let state = root.join(".git/phase-sources.json");
    let run = |args: &[&str]| cli(&words(args), &root);
    assert_eq!(
        run(&["deny"]).stderr,
        "usage: phase_sources.py allow <file> <why>\n"
    );
    assert_eq!(
        run(&["allow", "scripts/a.py", "two words"]).stderr,
        "phase-read: no phase task is started - nothing is held\n"
    );
    std::fs::write(
        &state,
        json!({"phase": "water_frame", "files": ["scripts/a.py"], "allow": []}).to_string(),
    )
    .unwrap();
    assert!(run(&["allow", "scripts/a.py", "one"])
        .stderr
        .contains("two words or more"));
    assert_eq!(
        run(&["allow", "scripts/b.py", "two words"]).stderr,
        "phase-read: scripts/b.py is not one of water_frame's held files - read it as usual\n"
    );
    let said = run(&["allow", "scripts/a.py", "the thin wrapper"]);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .starts_with("phase-read: scripts/a.py may be read until ")
            && said.stdout.ends_with(" UTC - the thin wrapper\n")
    );
    let kept = std::fs::read_to_string(&state).unwrap();
    assert!(kept.contains("\"why\": \"the thin wrapper\"") && kept.starts_with("{\n \"phase\""));
    // an absolute path inside the root is read relative to it; one outside raises
    let abs = root.join("scripts/a.py").to_string_lossy().into_owned();
    assert_eq!(run(&["allow", &abs, "by its path"]).code, 0);
    assert_eq!(run(&["allow", "/etc/hostname", "outside the root"]).code, 1);
    // each run recorded, a raise not
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert_eq!(usage.matches("\"tool\": \"phase_sources\"").count(), 6);
    assert!(
        usage.contains("\"outcome\": \"refused\"") && usage.contains("\"outcome\": \"passed\"")
    );
    // a state Python could not read raises
    for broken in [
        "{bad",
        "{\"phase\": \"x\", \"allow\": []}",
        "{\"files\": [\"scripts/b.py\"], \"allow\": []}",
        "{\"files\": 5, \"phase\": \"x\"}",
        "{\"files\": [\"scripts/a.py\"]}",
    ] {
        std::fs::write(&state, broken).unwrap();
        assert_eq!(run(&["allow", "scripts/a.py", "two words"]).code, 1);
    }
}

#[test]
fn python_s_in_reads_the_files_as_it_finds_them() {
    assert!(holds(Some(&json!(["a"])), "a").unwrap());
    assert!(holds(Some(&json!("xay")), "a").unwrap());
    assert!(holds(Some(&json!({"a": 1})), "a").unwrap());
    assert!(holds(None, "a").is_err());
    assert!(holds(Some(&json!(true)), "a").is_err());
}

#[test]
fn the_state_is_written_for_a_phase_task_and_cleared_for_another() {
    let dir = repo("phase-record");
    let root = root_of(&dir);
    let state = root.join(".git/phase-sources.json");
    assert_eq!(record(&root, "9001-x", "T01", "- [ ] T01 x\n").unwrap(), "");
    let line = record(
        &root,
        "9001-x",
        "T01",
        "- [ ] T01 x\n  phase: nothing_here\n  old-code: scripts/a.py scripts/a.py\n",
    )
    .unwrap();
    assert!(line.contains("1 file(s)"));
    assert_eq!(
        std::fs::read_to_string(&state).unwrap(),
        "{\n \"feature\": \"9001-x\",\n \"task\": \"T01\",\n \"phase\": \"nothing_here\",\n \"files\": [\n  \"scripts/a.py\"\n ],\n \"allow\": []\n}\n"
    );
    assert_eq!(record(&root, "9001-x", "T02", "").unwrap(), "");
    assert!(!state.exists());
    // the work budget's sources unreadable raise
    put(&root, "dev/work-budget/x.json", "{bad");
    assert!(record(&root, "9001-x", "T01", "  phase: water_frame\n").is_err());
}

#[test]
fn a_path_resolves_as_path_resolve_resolves_it() {
    let dir = repo("resolve");
    let root = root_of(&dir);
    let real = root.canonicalize().unwrap();
    std::os::unix::fs::symlink(&root, dir.join("link")).unwrap();
    assert_eq!(
        resolved(&dir.join("link/scripts/./a.py")),
        real.join("scripts/a.py")
    );
    assert_eq!(
        resolved(&dir.join("link/scripts/../none/x")),
        real.join("none/x")
    );
}

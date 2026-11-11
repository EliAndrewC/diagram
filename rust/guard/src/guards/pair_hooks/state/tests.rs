use std::path::Path;
use std::time::{Duration, UNIX_EPOCH};

use serde_json::{json, Value};

use super::{
    dumps, engine_key, gate_green, log_bypass, now, pairing_file, record_dispatch, record_round,
    round_number, wall, write_pairing,
};

fn clone(tag: &str) -> crate::shared::tempdir::TempDir {
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-state-{tag}"));
    std::fs::create_dir_all(d.join(".git")).unwrap();
    d
}

fn read(p: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap()
}

#[test]
fn json_is_written_as_pythons_indent_writes_it() {
    let v = json!({"b": [1, {}], "a": "x"});
    assert_eq!(
        dumps(&v, 2),
        "{\n  \"b\": [\n    1,\n    {}\n  ],\n  \"a\": \"x\"\n}"
    );
    assert_eq!(dumps(&json!({"k": []}), 1), "{\n \"k\": []\n}");
}

#[test]
fn the_pairing_state_keeps_its_other_fields() {
    let c = clone("pairing");
    std::fs::write(pairing_file(&c), "not json").unwrap();
    write_pairing(&c, "gate_key", "k1");
    write_pairing(&c, "review_dispatch_key", "k2");
    assert_eq!(
        read(&pairing_file(&c)),
        json!({"gate_key": "k1", "review_dispatch_key": "k2"})
    );
}

#[test]
fn the_clock_is_seamed_only_in_a_temporary_tree() {
    std::env::set_var("PAIR_NOW", "1234");
    assert_eq!(now(Path::new("/tmp/x")), 1234);
    assert_eq!(now(Path::new("/a/test-b")), 1234);
    assert!(now(Path::new("/home/c")) > 1_700_000_000);
    std::env::set_var("PAIR_NOW", "not a number");
    assert!(now(Path::new("/tmp/x")) > 1_700_000_000);
    std::env::remove_var("PAIR_NOW");
    assert!(wall() > 1_700_000_000);
}

#[test]
fn the_last_owed_dispatch_says_whether_they_went_out_together() {
    let c = clone("dispatch");
    let owed = ["m1".to_owned(), "m2".to_owned()];
    assert_eq!(record_dispatch(&c, "m1", "k", 100, &owed), "");
    assert_eq!(record_dispatch(&c, "m2", "k", 130, &owed), "parallel 30");
    assert_eq!(record_dispatch(&c, "m2", "k", 140, &owed), "");
    assert_eq!(record_dispatch(&c, "m1", "k2", 100, &owed), "");
    assert_eq!(
        record_dispatch(&c, "m2", "k2", 300, &owed),
        "serialized 200"
    );
    assert_eq!(record_dispatch(&c, "m1", "k", 0, &[]), "");
    assert_eq!(
        read(&pairing_file(&c))["dispatched"]["m1"],
        json!({"key": "k", "at": 0})
    );
}

#[test]
fn rounds_count_each_new_key_once_since_the_tasks_landed() {
    let c = clone("rounds");
    assert_eq!(round_number(&c, "u", "k1"), 1);
    record_round(&c, "u", "k1", 50);
    record_round(&c, "u", "k1", 60);
    assert_eq!(round_number(&c, "u", "k1"), 1);
    assert_eq!(round_number(&c, "u", "k2"), 2);
    std::fs::create_dir_all(c.join(".specify")).unwrap();
    std::fs::write(
        c.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/1-x"}"#,
    )
    .unwrap();
    record_round(&c, "u", "k3", 70);
    let d = read(&c.join(".git/review-rounds.json"));
    assert_eq!(
        (d["none"]["u"].clone(), d["specs/1-x"]["u"].clone()),
        (json!(["k1@50"]), json!(["k3@70"]))
    );
    std::fs::write(
        c.join(".git/review-rounds.json"),
        r#"{"specs/1-x": {"u": ["old", "k3@70"]}}"#,
    )
    .unwrap();
    assert_eq!(round_number(&c, "u", "k4"), 3);
}

#[test]
fn a_bypass_is_logged_only_where_the_clone_keeps_the_log() {
    let c = clone("bypass");
    let at = UNIX_EPOCH + Duration::from_secs(1_794_112_496);
    log_bypass(&c, "why", "what", at);
    assert!(!c.join("dev/bypass-log").exists());
    std::fs::create_dir_all(c.join("dev/bypass-log")).unwrap();
    log_bypass(&c, "named in the dispatch", "review alone", at);
    let month = c.join("dev/bypass-log/2026-11");
    let files: Vec<_> = std::fs::read_dir(&month)
        .unwrap()
        .filter_map(Result::ok)
        .map(|e| e.file_name().into_string().unwrap())
        .collect();
    assert_eq!(files.len(), 1);
    assert!(
        files[0].starts_with("20261108T043456Z-")
            && files[0].len() == "20261108T043456Z-123456.json".len()
    );
    let rec = read(&month.join(&files[0]));
    assert_eq!(
        rec,
        json!({"utc": "20261108T043456Z", "guard": "pair-hooks", "what": "review alone", "reason": "named in the dispatch"})
    );
    std::fs::remove_dir_all(&month).unwrap();
    std::fs::write(&month, "a file where the month folder goes").unwrap();
    log_bypass(&c, "why", "what", at);
}

#[test]
fn the_engine_key_is_the_cache_until_a_py_is_newer_and_then_makes_asks() {
    let c = clone("key");
    assert_eq!(engine_key(&c.join("missing")), "");
    std::fs::write(c.join("Makefile"), "engine-key:\n\t@printf ' abc def\\n'\n").unwrap();
    assert_eq!(engine_key(&c), "abcdef");
    assert_eq!(
        std::fs::read_to_string(c.join(".git/pairing-key")).unwrap(),
        "abcdef"
    );
    std::fs::write(c.join(".git/pairing-key"), "cached\n").unwrap();
    std::fs::create_dir_all(c.join("l7r/sub")).unwrap();
    std::fs::write(c.join("l7r/sub/a.txt"), "").unwrap();
    assert_eq!(engine_key(&c), "cached", "no newer .py: the cache");
    std::thread::sleep(Duration::from_millis(15));
    std::fs::write(c.join("l7r/sub/m.py"), "").unwrap();
    assert_eq!(engine_key(&c), "abcdef", "a newer .py: asked again");
    std::fs::write(c.join("Makefile"), "engine-key:\n\t@false\n").unwrap();
    std::thread::sleep(Duration::from_millis(15));
    std::fs::create_dir_all(c.join("pool")).unwrap();
    std::fs::write(c.join("pool/n.py"), "").unwrap();
    assert_eq!(engine_key(&c), "", "make answered nothing: nothing kept");
}

#[test]
fn a_green_gate_is_the_stamp_else_the_recorded_key() {
    let c = clone("green");
    assert!(!gate_green(&c, ""));
    std::fs::write(
        c.join(".git/verification-state.json"),
        r#"{"engine_key": "k"}"#,
    )
    .unwrap();
    assert!(gate_green(&c, "k") && !gate_green(&c, "other"));
    std::fs::create_dir_all(c.join("scripts/gates")).unwrap();
    std::fs::write(
        c.join("scripts/gates/l7r-gate.sh"),
        "[ \"$*\" = \"stamp --fresh diagram\" ]\n",
    )
    .unwrap();
    assert!(gate_green(&c, "other"));
}

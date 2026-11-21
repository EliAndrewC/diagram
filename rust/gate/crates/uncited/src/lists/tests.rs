//! The filter's lists and their one writer (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record).

use serde_json::json;

use super::*;
use crate::testkit::W;

fn s(list: &[&str]) -> Vec<String> {
    list.iter().map(|a| (*a).to_owned()).collect()
}

#[test]
fn a_line_takes_known_reasons_and_states() {
    let x = line(
        "https://www.e.org/p/",
        &s(&["off-topic", "duplicate"]),
        "rule",
        "n",
        "gone",
    )
    .unwrap();
    let keys: Vec<&String> = x.as_object().unwrap().keys().collect();
    assert_eq!(
        keys,
        ["url", "raw", "reasons", "note", "basis", "date", "feature", "access"]
    );
    assert_eq!(
        (x["url"].as_str(), x["feature"].as_str()),
        (Some("e.org/p"), Some("312"))
    );
    assert!(line("u", &s(&["off-topic"]), "b", "", "")
        .unwrap()
        .get("access")
        .is_none());
    assert_eq!(
        line("u", &s(&["nope", "duplicate"]), "b", "", "").unwrap_err().message,
        "u: reasons ['nope', 'duplicate'] - each one of off-topic, modern-only, unreliable-kind, no-substance, duplicate, unreadable, at least one"
    );
    assert_eq!(line("u", &[], "b", "", "").unwrap_err().kind, "ValueError");
    assert_eq!(
        line("u", &s(&["duplicate"]), "b", "", "lost")
            .unwrap_err()
            .message,
        "u: access 'lost' is not one of bot-refused, down, gone, paywalled"
    );
}

#[test]
fn the_writer_appends_under_the_lock_and_refuses_a_blocked_url() {
    let w = W::new("lists-write");
    write(w.root(), &[], NOT_KEPT).unwrap();
    assert_eq!(w.read(NOT_KEPT), "");
    write(
        w.root(),
        &[json!({"url": "e.org/日", "raw": "", "x": 1})],
        "specs/new/list.jsonl",
    )
    .unwrap();
    assert_eq!(
        w.read("specs/new/list.jsonl"),
        "{\"url\": \"e.org/日\", \"raw\": \"\", \"x\": 1}\n"
    );
    let blocked = write(
        w.root(),
        &[json!({"url": "u", "raw": "https://grokipedia.com/x"})],
        NOT_KEPT,
    )
    .unwrap_err();
    assert_eq!(blocked.kind, "Blocked");
    assert_eq!(
        write(w.root(), &[json!({"raw": ""})], NOT_KEPT)
            .unwrap_err()
            .message,
        "'url'"
    );
    assert_eq!(
        write(w.root(), &[json!({"url": "u"})], l7r_shared::attempts::LOG)
            .unwrap_err()
            .kind,
        "ValueError"
    );
    w.put("research/not-kept.jsonl/x", "");
    assert_eq!(
        write(
            w.root(),
            &[json!({"url": "u"})],
            "research/not-kept.jsonl/x/y"
        )
        .unwrap_err()
        .kind,
        "FileExistsError"
    );
    assert_eq!(
        write(w.root(), &[json!({"url": "u"})], "research/not-kept.jsonl")
            .unwrap_err()
            .kind,
        "IsADirectoryError"
    );
}

#[test]
fn a_not_kept_prehold_capture_loses_its_row() {
    let w = W::new("lists-notkept");
    let keyed = l7r_gate_archive::manifest::row_path(w.root(), "https://e.org/a");
    l7r_gate_archive::manifest::write_row(
        w.root(),
        "https://e.org/a",
        &json!({"url": "https://e.org/a", "keys": ["src-a"]}),
    )
    .unwrap();
    let bare = "https://e.org/bare";
    l7r_gate_archive::manifest::write_row(w.root(), bare, &json!({"url": bare, "keys": []}))
        .unwrap();
    not_kept(
        w.root(),
        &[
            line(bare, &s(&["off-topic"]), "b", "", "").unwrap(),
            line("https://e.org/a", &s(&["off-topic"]), "b", "", "").unwrap(),
        ],
    )
    .unwrap();
    assert!(!l7r_gate_archive::manifest::row_path(w.root(), bare).exists() && keyed.exists());
    assert_eq!(w.read(NOT_KEPT).lines().count(), 2);
    assert_eq!(
        not_kept(w.root(), &[json!({"url": "u"})])
            .unwrap_err()
            .message,
        "'raw'"
    );
    std::fs::write(&keyed, "{").unwrap();
    assert_eq!(
        not_kept(
            w.root(),
            &[line("https://e.org/a", &s(&["off-topic"]), "b", "", "").unwrap()]
        )
        .unwrap_err()
        .kind,
        "JSONDecodeError"
    );
    kept(w.root(), &s(&["https://www.k.org/1"]), "source-filter").unwrap();
    assert!(w.read(KEPT).starts_with("{\"url\": \"k.org/1\", \"raw\": \"https://www.k.org/1\", \"basis\": \"source-filter\", \"date\": \""));
}

#[test]
fn unkeep_and_the_requeue_rewrite_the_lists() {
    let w = W::new("lists-unkeep");
    w.lines(
        KEPT,
        &[
            json!({"url": "k.org/1", "raw": "https://k.org/1"}),
            json!({"url": "k.org/2", "raw": "https://k.org/2"}),
        ],
    );
    unkeep(
        w.root(),
        "https://k.org/1",
        &s(&["duplicate"]),
        "session",
        "why",
    )
    .unwrap();
    assert_eq!(
        w.read(KEPT),
        "{\"url\":\"k.org/2\",\"raw\":\"https://k.org/2\"}\n"
    );
    assert!(w
        .read(NOT_KEPT)
        .contains("\"reasons\": [\"duplicate\"], \"note\": \"why\", \"basis\": \"session\""));
    assert_eq!(
        unkeep(w.root(), "https://k.org/1", &s(&["duplicate"]), "s", "")
            .unwrap_err()
            .message,
        "https://k.org/1 is not on the kept list"
    );
    // the kept list rewritten before the reasons are checked, as the Python did
    assert_eq!(
        unkeep(w.root(), "https://k.org/2", &s(&["bad"]), "s", "")
            .unwrap_err()
            .kind,
        "ValueError"
    );
    assert_eq!(w.read(KEPT), "");
    std::fs::remove_file(w.root().join(KEPT)).unwrap();
    assert_eq!(
        unkeep(w.root(), "u", &s(&["duplicate"]), "s", "")
            .unwrap_err()
            .kind,
        "FileNotFoundError"
    );
    w.lines(
        KEPT,
        &[json!({"url": "zh.wikipedia.org/zh-tw/x", "raw": "https://zh.wikipedia.org/zh-tw/x"})],
    );
    w.put(NOT_KEPT, "\n{\"url\": \"other.org\"}\n");
    assert!(drop_verdicts(w.root(), "https://zh.wikipedia.org/wiki/x").unwrap());
    assert_eq!(
        (w.read(KEPT), w.read(NOT_KEPT)),
        (String::new(), "\n{\"url\": \"other.org\"}\n".to_owned())
    );
    assert!(!drop_verdicts(w.root(), "https://zh.wikipedia.org/wiki/x").unwrap());
    w.put(NOT_KEPT, "not json\n");
    assert_eq!(
        drop_verdicts(w.root(), "u").unwrap_err().kind,
        "JSONDecodeError"
    );
    w.put(NOT_KEPT, "[1]\n");
    assert_eq!(drop_verdicts(w.root(), "u").unwrap_err().kind, "TypeError");
    std::fs::remove_file(w.root().join(NOT_KEPT)).unwrap();
    std::fs::create_dir_all(w.root().join(NOT_KEPT)).unwrap();
    assert!(drop_verdicts(w.root(), "u").is_err());
}

#[test]
fn a_lines_reads() {
    let w = W::new("lists-read");
    assert!(read(w.root(), KEPT).unwrap().is_empty());
    w.put(KEPT, "{\"url\": \"a\"}\nnot json\n");
    assert_eq!(read(w.root(), KEPT).unwrap().len(), 1);
    assert_eq!(urls_of(&read(w.root(), KEPT).unwrap()).unwrap().len(), 1);
    std::fs::write(w.root().join(KEPT), [0xff]).unwrap();
    assert_eq!(read(w.root(), KEPT).unwrap_err().kind, "UnicodeDecodeError");
    assert_eq!(get(&json!({"a": 1}), "a").unwrap(), Some(&json!(1)));
    assert_eq!(
        get(&json!(null), "a").unwrap_err().message,
        "'NoneType' object has no attribute 'get'"
    );
}

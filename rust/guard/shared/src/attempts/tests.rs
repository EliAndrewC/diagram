//! The attempts log (feature 449 T145; each expected value `attempts.py`'s on the same input, 2026-11-16).

use std::path::{Path, PathBuf};

use serde_json::{json, Map, Value};

use super::{
    add, base, from_ledger, last_sought, line, old_ids, outcome, question_of, read, report, seed,
    seed_lines, seen, show, today, verdict, write, Ask, More, LOG,
};
use crate::consulted::VARS;
use crate::tempdir::TempDir;

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

fn set(name: &str, value: &str) {
    VARS.with(|v| v.borrow_mut().insert(name.to_owned(), value.to_owned()));
}

/// A clone with the blocked list and a ledger home beside it; the test thread's environment cleared.
fn world(tag: &str) -> (TempDir, PathBuf, PathBuf) {
    VARS.with(|v| v.borrow_mut().clear());
    let d = TempDir::new(&format!("attempts-{tag}"));
    let root = d.join("c");
    std::fs::create_dir_all(root.join("research/sources/040-uncited-works")).unwrap();
    std::fs::write(root.join("research/blocked-domains.json"), LIST).unwrap();
    let rec = root.join("research");
    (d, root, rec)
}

fn put(root: &Path, rel: &str, text: &str) {
    std::fs::write(root.join(rel), text).unwrap();
}

fn logged(root: &Path) -> Vec<Value> {
    read(root, LOG).unwrap()
}

#[test]
fn a_line_is_made_and_written() {
    let (_d, root, rec) = world("line");
    assert_eq!(base(&root), root);
    set("L7R_ATTEMPTS_ROOT", "/moved");
    assert_eq!(base(&root), Path::new("/moved"));
    set("L7R_ATTEMPTS_ROOT", "");
    let bad = line("u", &json!("q"), "s", "maybe", &More::default()).unwrap_err();
    assert_eq!(bad.message, "outcome 'maybe' is not one of found, partial, not-found, not-applicable, unreadable, unknown");
    set("SPECIFY_FEATURE", "3125-x");
    let x = line(
        "https://www.a.org/",
        &json!(""),
        "s",
        "found",
        &More::default(),
    )
    .unwrap();
    assert_eq!(x["question"], "unknown");
    assert_eq!(x["feature"], "312");
    assert_eq!(x["date"], today());
    assert_eq!(
        x.as_object().unwrap().keys().collect::<Vec<_>>(),
        ["url", "raw", "key", "question", "sought", "outcome", "date", "feature", "route"]
    );
    assert!(write(&root, &[], &rec).is_ok());
    assert_eq!(
        write(&root, &[json!({"raw": ""})], &rec).unwrap_err().kind,
        "KeyError"
    );
    assert_eq!(
        write(&root, &[json!({"url": "https://bad.example/x"})], &rec)
            .unwrap_err()
            .kind,
        "Blocked"
    );
    let more = More {
        key: "k",
        route: "r",
        feature: "",
        date: "2026-01-01",
    };
    let got = add(
        &root,
        "https://a.org/x",
        "0012",
        "the dike",
        "found",
        &more,
        &rec,
    )
    .unwrap();
    assert_eq!(
        (
            got["key"].as_str(),
            got["date"].as_str(),
            got["feature"].as_str()
        ),
        (Some("k"), Some("2026-01-01"), Some("3125"))
    );
    assert_eq!(logged(&root).len(), 1);
    std::fs::write(root.join("research/source-attempts.jsonl"), "").unwrap();
    std::fs::create_dir_all(root.join("dir/research/source-attempts.jsonl")).unwrap();
    set("L7R_ATTEMPTS_ROOT", &root.join("dir").to_string_lossy());
    assert_eq!(write(&root, &[got], &rec).unwrap_err().kind, "OSError");
    set(
        "L7R_ATTEMPTS_ROOT",
        &root.join("research/blocked-domains.json").to_string_lossy(),
    );
    assert_eq!(
        write(&root, &[json!({"url": "a"})], &rec).unwrap_err().kind,
        "OSError"
    );
}

#[test]
fn seen_reports_and_records_once_a_fetch() {
    let (_d, root, rec) = world("seen");
    let first = seen(
        &root,
        &["https://a.org/p&amp;q".to_owned()],
        "walls",
        "webfetch",
        true,
        &rec,
    )
    .unwrap();
    assert_eq!(
        first,
        vec![json!({"lines": [], "plain": "https://a.org/p&q"})]
    );
    let again = seen(
        &root,
        &["https://a.org/p&amp;q".to_owned()],
        "walls",
        "webfetch",
        false,
        &rec,
    )
    .unwrap();
    assert_eq!(
        again[0]["lines"][0],
        "attempts: https://a.org/p&amp;q - 1 earlier attempt(s):"
    );
    assert_eq!(logged(&root).len(), 1);
    // a write that fails never blocks the read
    seen(
        &root,
        &["https://bad.example/z".to_owned()],
        "x",
        "bash",
        true,
        &rec,
    )
    .unwrap();
    assert_eq!(logged(&root).len(), 1);
    put(&root, LOG, "[]\n");
    assert!(seen(
        &root,
        &["https://a.org/".to_owned()],
        "x",
        "bash",
        false,
        &rec
    )
    .is_err());
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "the seed's every reading of a ledger row, in the order the Python reads them"
)]
fn the_seed_maps_the_ledger_rows() {
    let (d, root, rec) = world("seed");
    assert!(old_ids(&root).unwrap().is_empty());
    put(
        &root,
        "research/moved-303.json",
        r#"{"numbers": {"cities fabric/104": "0104"}}"#,
    );
    let mapped = old_ids(&root).unwrap();
    assert_eq!(mapped["cities/fabric/104"], "0104");
    assert_eq!(question_of("0012", &mapped), (json!("0012"), String::new()));
    assert_eq!(question_of("0012\n", &mapped).0, json!("0012\n"));
    assert_eq!(question_of("cities/fabric/104", &mapped).0, json!("0104"));
    assert_eq!(
        question_of("towns/x/001", &mapped).0,
        json!("old:towns/x/001")
    );
    assert_eq!(
        question_of("what the dike holds", &mapped),
        (json!("unknown"), "what the dike holds".to_owned())
    );
    for (text, kind) in [
        ("[]", "AttributeError"),
        (r#"{"numbers": 3}"#, "AttributeError"),
        ("{", "JSONDecodeError"),
    ] {
        put(&root, "research/moved-303.json", text);
        assert_eq!(old_ids(&root).unwrap_err().kind, kind);
    }
    put(&root, "research/moved-303.json", "{}");
    assert!(old_ids(&root).unwrap().is_empty());
    std::fs::set_permissions(
        root.join("research/moved-303.json"),
        std::os::unix::fs::PermissionsExt::from_mode(0o000),
    )
    .unwrap();
    assert_eq!(old_ids(&root).unwrap_err().kind, "OSError");
    std::fs::remove_file(root.join("research/moved-303.json")).unwrap();
    std::fs::write(root.join("research/moved-303.json"), b"\xff").unwrap();
    assert_eq!(old_ids(&root).unwrap_err().kind, "UnicodeDecodeError");
    std::fs::remove_file(root.join("research/moved-303.json")).unwrap();
    std::fs::create_dir_all(root.join("research/moved-303.json/x")).unwrap();
    assert!(old_ids(&root).unwrap().is_empty());
    std::fs::remove_dir_all(root.join("research/moved-303.json")).unwrap();
    assert_eq!(
        from_ledger("cited: k-1 "),
        ("found", "k-1".to_owned(), String::new())
    );
    assert_eq!(
        from_ledger("rejected: off"),
        ("not-applicable", String::new(), "off".to_owned())
    );
    assert_eq!(
        from_ledger(" cited :x"),
        ("found", String::new(), String::new())
    );
    assert_eq!(from_ledger("weird").0, "unknown");
    let rows = vec![
        json!({"url": "a.org/p", "raw": "https://a.org/p", "utc": "2026-09-29T10:00:00+00:00", "feature": "288",
               "questions": ["0012", "why not"], "outcome": "rejected: off"}),
        json!({"url": "b.org", "questions": "x", "outcome": "nothing-found"}),
        json!({"url": "c.org", "outcome": "cited:c"}),
    ];
    let lines = seed_lines(&rows, &Map::new()).unwrap();
    assert_eq!(lines.len(), 4);
    assert_eq!(
        lines[0]["sought"],
        "unknown - recorded before feature 312 (rejected: off)"
    );
    assert_eq!(lines[1]["sought"], "why not (rejected: off)");
    assert_eq!(lines[3]["key"], "c");
    assert_eq!(lines[0]["seed"], "ledger-2026-10-02");
    for bad in [
        json!(1),
        json!({"url": "a", "questions": 5}),
        json!({"questions": ["0012"]}),
        json!({"outcome": 3}),
        json!({"url": 3, "questions": ["0012"]}),
        json!({"url": "a", "questions": [5]}),
    ] {
        assert!(seed_lines(&[bad.clone()], &Map::new()).is_err(), "{bad}");
    }
    let home = d.join(".specify");
    std::fs::create_dir_all(&home).unwrap();
    set("L7R_SOURCES_HOME", &home.to_string_lossy());
    std::fs::write(
        home.join("sources-consulted.jsonl"),
        format!(
            "{}\n{}\n{}\n",
            rows[0],
            json!({"url": "bad.example/q", "raw": "https://bad.example/q"}),
            json!({"url": ""})
        ),
    )
    .unwrap();
    let (out, _, n) = seed(&root, &home, &rec).unwrap();
    assert_eq!(
        (out.as_str(), n),
        ("attempts: 2 line(s) seeded from 1 ledger row(s)\n", 2)
    );
    let (_, err, n) = seed(&root, &home, &rec).unwrap();
    assert_eq!(
        (err.as_str(), n),
        (
            "attempts: every ledger row has an attempt line - nothing written\n",
            0
        )
    );
    put(&root, LOG, "{\"url\": \"elsewhere.org\"}\n");
    assert_eq!(seed(&root, &home, &rec).unwrap().2, 2);
    put(&root, LOG, "{}\n");
    assert_eq!(seed(&root, &home, &rec).unwrap_err().kind, "KeyError");
    put(&root, LOG, "");
    std::fs::write(home.join("sources-consulted.jsonl"), "[1]\n").unwrap();
    assert_eq!(seed(&root, &home, &rec).unwrap_err().kind, "AttributeError");
}

#[test]
fn an_outcome_carries_what_was_sought() {
    let (_d, root, rec) = world("outcome");
    assert_eq!(
        last_sought(&root, "https://a.org", "").unwrap(),
        "unknown - recorded before feature 312"
    );
    add(
        &root,
        "https://a.org",
        "unknown",
        "the walls",
        "unknown",
        &More::default(),
        &rec,
    )
    .unwrap();
    assert_eq!(last_sought(&root, "a.org", "").unwrap(), "the walls");
    assert_eq!(
        last_sought(&root, "a.org", "0001").unwrap(),
        "unknown - recorded before feature 312"
    );
    let got = outcome(&root, "https://a.org", "", "rejected: off topic", "", &rec).unwrap();
    assert_eq!(got["sought"], "the walls (rejected: off topic)");
    assert_eq!(got["outcome"], "not-applicable");
    let got = outcome(&root, "https://a.org", "0012", "cited:k", "given", &rec).unwrap();
    assert_eq!(
        (
            got["sought"].as_str(),
            got["key"].as_str(),
            got["route"].as_str()
        ),
        (Some("given"), Some("k"), Some("source-outcome"))
    );
    put(
        &root,
        LOG,
        "{\"url\": \"a.org\", \"question\": \"unknown\"}\n",
    );
    assert_eq!(
        last_sought(&root, "a.org", "").unwrap_err().kind,
        "KeyError"
    );
    put(
        &root,
        LOG,
        "{\"url\": \"a.org\", \"question\": \"unknown\", \"sought\": 3}\n",
    );
    assert_eq!(
        last_sought(&root, "a.org", "").unwrap_err().kind,
        "TypeError"
    );
}

#[test]
fn the_report_and_the_filter_verdict() {
    let (_d, root, rec) = world("report");
    let more = More {
        key: "k1",
        route: "r",
        feature: "312",
        date: "2026-10-02",
    };
    add(
        &root,
        "https://a.org/p",
        "0012",
        "the dike",
        "not-found",
        &more,
        &rec,
    )
    .unwrap();
    assert_eq!(
        report(&root, Ask::Url("https://a.org/p")).unwrap(),
        [
            "attempts: https://a.org/p - 1 earlier attempt(s):",
            "  2026-10-02 Q 0012: not-found - the dike",
        ]
    );
    assert_eq!(
        report(&root, Ask::Url("https://z.org")).unwrap(),
        ["attempts: https://z.org - no earlier attempt"]
    );
    assert_eq!(report(&root, Ask::Key("k1")).unwrap().len(), 2);
    assert_eq!(
        report(&root, Ask::Question("0012")).unwrap()[1],
        "  https://a.org/p\n  2026-10-02 Q 0012: not-found - the dike"
    );
    put(&root, "research/not-kept.jsonl", "{\"url\": \"z.org\", \"date\": \"d\", \"reasons\": [\"a\", \"b\"], \"note\": \"n\"}\n{\"url\": \"y.org\", \"reasons\": \"ab\"}\n{\"url\": \"x.org\"}\n");
    assert_eq!(
        verdict(&root, "https://z.org").unwrap(),
        "NOT KEPT d (a, b - n)"
    );
    assert_eq!(verdict(&root, "https://y.org").unwrap(), "NOT KEPT  (a, b)");
    assert_eq!(verdict(&root, "https://x.org").unwrap(), "NOT KEPT  ()");
    put(
        &root,
        "research/sources/040-uncited-works/0100-k.html",
        "<p>(https://w.org/a)</p>\r\n",
    );
    put(
        &root,
        "research/sources/040-uncited-works/notes.txt",
        "https://v.org",
    );
    assert_eq!(
        verdict(&root, "http://www.w.org/a/").unwrap(),
        "KEPT, uncited: 0100-k.html"
    );
    assert_eq!(verdict(&root, "https://v.org").unwrap(), "");
    assert_eq!(
        report(&root, Ask::Url("https://z.org")).unwrap()[1],
        "  filter verdict: NOT KEPT d (a, b - n)"
    );
    for (text, kind) in [
        ("{\"url\": \"z.org\", \"reasons\": [1]}\n", "TypeError"),
        ("{\"url\": \"z.org\", \"reasons\": 1}\n", "TypeError"),
        ("[]\n", "AttributeError"),
    ] {
        put(&root, "research/not-kept.jsonl", text);
        assert_eq!(verdict(&root, "https://z.org").unwrap_err().kind, kind);
    }
    put(&root, "research/not-kept.jsonl", "");
    std::fs::write(
        root.join("research/sources/040-uncited-works/0200-b.html"),
        b"\xff",
    )
    .unwrap();
    assert_eq!(
        verdict(&root, "https://q.org").unwrap_err().kind,
        "UnicodeDecodeError"
    );
    std::fs::remove_file(root.join("research/sources/040-uncited-works/0200-b.html")).unwrap();
    std::fs::create_dir_all(root.join("research/sources/040-uncited-works/0300-d.html")).unwrap();
    assert_eq!(verdict(&root, "https://q.org").unwrap_err().kind, "OSError");
    assert_eq!(show(&json!({"question": 12})), "   Q 12:  - ");
    put(&root, LOG, "{\"question\": \"0012\", \"raw\": \"\"}\n");
    assert_eq!(
        report(&root, Ask::Question("0012")).unwrap_err().kind,
        "KeyError"
    );
    put(
        &root,
        LOG,
        "{\"question\": \"0012\", \"raw\": \"\", \"url\": \"u\"}\n",
    );
    assert_eq!(
        report(&root, Ask::Question("0012")).unwrap()[1],
        "  u\n  Q 0012:  -"
    );
    put(&root, LOG, "5\n");
    assert_eq!(
        report(&root, Ask::Key("k")).unwrap_err().kind,
        "AttributeError"
    );
}

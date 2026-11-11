//! The tag's rules, on scratch trees.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{cli, every, load, row_state, tag, World};
use crate::checks::scratch;

fn owned(items: &[&str]) -> Vec<String> {
    items.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

const STATES: &str = r#"[{"id":"open"},{"id":"gm-full"},{"id":"gm-partial"},{"id":"paywalled"},{"id":"bot-refused"},{"id":"down"},{"id":"gone"},{"id":"never-read"}]"#;

fn tree(tag_name: &str, recorded: &str) -> PathBuf {
    let root = scratch(tag_name);
    put(
        &root,
        "research/source-access.json",
        &format!(r#"{{"_about":"é","states":{STATES},"recorded":{recorded}}}"#),
    );
    root
}

fn key_file(root: &Path, key: &str, reads: &[&str]) {
    let lines: Vec<String> = reads
        .iter()
        .map(|r| format!("<!-- READ {r} -->\n"))
        .collect();
    let notes = lines.concat();
    put(
        root,
        &format!("research/sources/010-works-cited/0010-{key}.html"),
        &format!("<h3 id=\"{key}\">x</h3>\n{notes}"),
    );
}

fn manifest(root: &Path, name: &str, row: &serde_json::Value) {
    put(
        root,
        &format!("research/archive/d/{name}.json"),
        &row.to_string(),
    );
}

const MARKED: &str =
    "- Mark: [x] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found";
const PARTIAL: &str =
    "- Mark: [ ] downloaded | [x] partial (abstract or excerpt) | [ ] paywalled | [ ] not found";
const PAYWALLED: &str =
    "- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [x] paywalled | [ ] not found";
const NOT_FOUND: &str =
    "- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [x] not found";
const BLANK: &str =
    "- Mark: [ ] downloaded | [ ] partial (abstract or excerpt) | [ ] paywalled | [ ] not found";

fn entry(id: &str, mark: &str, date: &str, body: &str) -> String {
    let recorded = if date.is_empty() {
        String::new()
    } else {
        format!("- Marks recorded {date}\n")
    };
    format!("### {id}. Title\n\n{mark}\n- [ ] Found elsewhere (only with downloaded or partial) - where:\n- Saved as (optional, the file's name):\n{recorded}{body}\n")
}

fn state_of(w: &World, key: &str) -> (String, Option<String>) {
    let t = tag(w, key);
    (t.state, t.date)
}

#[test]
fn a_manifest_row_gives_its_state() {
    let s = |o: &str, r: &str| row_state(&json!({"outcome": o, "reason": r}));
    assert_eq!(s("archived", ""), "open");
    assert_eq!(s("archived-earlier-snapshot", ""), "open");
    assert_eq!(s("archived-gm-copy", ""), "gm-full");
    assert_eq!(s("refused", "the page would not render whole: x"), "open");
    assert_eq!(s("refused", "got HTTP 404 there"), "gone");
    assert_eq!(s("refused", "HTTP 410"), "gone");
    assert_eq!(s("refused", "HTTP 503"), "down");
    assert_eq!(s("refused", "net::ERR timeout"), "down");
    assert_eq!(s("refused", "HTTP 403"), "bot-refused");
    assert_eq!(row_state(&json!({})), "bot-refused");
}

#[test]
fn the_most_open_row_stands_dated_by_its_capture() {
    let root = tree("rows", "{}");
    key_file(&root, "alpha", &["2020-01-01"]);
    manifest(
        &root,
        "a",
        &json!({"keys": ["alpha"], "outcome": "refused", "reason": "HTTP 403", "captured": "2026-01-01T00:00:00Z", "url": "u1"}),
    );
    manifest(
        &root,
        "b",
        &json!({"keys": ["alpha"], "outcome": "archived", "captured": "2025-01-01T10:00:00Z", "url": "u2"}),
    );
    manifest(
        &root,
        "c",
        &json!({"keys": ["alpha"], "outcome": "archived", "captured": "2025-06-01T10:00:00Z", "url": "u3"}),
    );
    manifest(
        &root,
        "d",
        &json!({"keys": ["alpha"], "outcome": "archived", "url": "u4"}),
    );
    manifest(
        &root,
        "e",
        &json!({"keys": ["beta"], "outcome": "refused", "reason": "x".repeat(100), "url": "u5", "final_url": "u6"}),
    );
    put(&root, "research/archive/.hidden/x.json", "not json");
    put(&root, "research/archive/d/.hidden.json", "not json");
    let w = load(&root).unwrap();
    let t = tag(&w, "alpha");
    assert_eq!(
        (t.state.as_str(), t.date.as_deref()),
        ("open", Some("2025-06-01"))
    );
    assert_eq!(t.basis, "the archive manifest: archived, u3");
    let beta = tag(&w, "beta");
    assert_eq!(beta.date, None);
    assert_eq!(
        beta.basis,
        format!("the archive manifest: refused ({}), u5", "x".repeat(80))
    );
    assert_eq!(state_of(&w, "gamma"), ("never-read".to_owned(), None));
}

#[test]
fn a_read_comment_without_a_row_is_open_and_none_is_never_read() {
    let root = tree("reads", "{}");
    key_file(&root, "alpha", &["2020-01-01", "2021-05-06"]);
    key_file(&root, "beta", &[]);
    let w = load(&root).unwrap();
    let alpha = tag(&w, "alpha");
    assert_eq!(
        (alpha.state.as_str(), alpha.date.as_deref()),
        ("open", Some("2021-05-06"))
    );
    assert!(alpha.basis.starts_with("a READ comment"));
    let beta = tag(&w, "beta");
    assert_eq!(beta.state, "never-read");
    assert!(beta.basis.starts_with("no READ"));
}

#[test]
fn a_gm_mark_wins_and_the_newest_most_open_mark_stands() {
    let root = tree(
        "marks",
        r#"{"alpha":[{"state":"open","date":"2030-01-01","reason":"a b"}]}"#,
    );
    key_file(&root, "alpha", &[]);
    key_file(&root, "beta", &[]);
    key_file(&root, "gamma", &[]);
    key_file(&root, "delta", &[]);
    key_file(&root, "epsilon", &[]);
    let list = [
        entry("1", PARTIAL, "2026-01-01", "`alpha`"),
        entry("2", MARKED, "2026-01-01", "`alpha` `beta`"),
        entry("3", PAYWALLED, "2026-02-01", "`beta`"),
        entry("4", NOT_FOUND, "2026-03-01", "`gamma`"),
        entry("5", BLANK, "", "`delta`"),
        entry("6", PARTIAL, "2026-01-01", "`gamma`"),
        entry("7", NOT_FOUND, "2026-01-01", "`epsilon`"),
    ]
    .join("\n");
    put(&root, "research/to-download.md", &list);
    let w = load(&root).unwrap();
    assert_eq!(
        state_of(&w, "alpha"),
        ("gm-full".to_owned(), Some("2026-01-01".to_owned()))
    );
    assert_eq!(
        tag(&w, "alpha").basis,
        "the GM's mark on entry 2, recorded 2026-01-01"
    );
    assert_eq!(
        state_of(&w, "beta"),
        ("paywalled".to_owned(), Some("2026-02-01".to_owned()))
    );
    // a not-found does not displace a mark that gives a state, and carries nothing where one stands
    assert_eq!(
        state_of(&w, "gamma"),
        ("gm-partial".to_owned(), Some("2026-01-01".to_owned()))
    );
    assert_eq!(state_of(&w, "delta"), ("never-read".to_owned(), None));
    let e = tag(&w, "epsilon");
    assert_eq!(
        (e.state.as_str(), e.basis.as_str()),
        (
            "never-read",
            "no READ in its registry entry and no archive row; the GM did not find it (entry 7)"
        )
    );
    assert_eq!(w.entry_keys["download:2"].len(), 2);
}

#[test]
fn a_hand_recorded_state_wins_on_the_same_date_or_later() {
    let root = tree(
        "hand",
        r#"{"alpha":[{"state":"gone","date":"2025-06-01","reason":"a b"},{"state":"down","date":"2024-01-01","reason":"c d"}],"beta":[{"state":"gone","date":"2024-01-01","reason":"e f"}],"gamma":[{"state":"gone","date":"2020-01-01","reason":"g h"}],"download:5":[{"state":"paywalled","date":"2020-01-01","reason":"i j"}]}"#,
    );
    for key in ["alpha", "beta", "gamma"] {
        key_file(&root, key, &["2025-06-01"]);
    }
    put(
        &root,
        "research/to-download.md",
        &(entry("5", BLANK, "", "no key") + &entry("6", NOT_FOUND, "2026-01-01", "`beta`")),
    );
    let w = load(&root).unwrap();
    let alpha = tag(&w, "alpha");
    assert_eq!(
        (alpha.state.as_str(), alpha.basis.as_str()),
        ("gone", "recorded by hand: a b")
    );
    assert_eq!(
        state_of(&w, "beta"),
        ("open".to_owned(), Some("2025-06-01".to_owned()))
    );
    assert!(tag(&w, "beta")
        .basis
        .ends_with("; the GM did not find it (entry 6)"));
    assert_eq!(
        state_of(&w, "gamma"),
        ("open".to_owned(), Some("2025-06-01".to_owned()))
    );
    assert_eq!(
        state_of(&w, "download:5"),
        ("paywalled".to_owned(), Some("2020-01-01".to_owned()))
    );
    assert_eq!(state_of(&w, "download:9"), ("never-read".to_owned(), None));
}

#[test]
fn an_entry_names_keys_by_tick_key_line_and_link() {
    let root = tree("names", "{}");
    for key in ["alpha", "beta", "gamma"] {
        key_file(&root, key, &[]);
    }
    manifest(
        &root,
        "a",
        &json!({"keys": ["gamma"], "url": "https://a.test/x", "final_url": "https://b.test/y", "outcome": "archived"}),
    );
    let list = [
        entry("1", BLANK, "", "`alpha` `nosuch`"),
        entry("2", BLANK, "", "- Key: beta, nosuch"),
        entry("3", BLANK, "", "- [link](https://a.test/x)"),
        entry(
            "4",
            BLANK,
            "",
            "- [link](https://b.test/y)\n- [no](https://other.test/)",
        ),
        entry("5", BLANK, "", "nothing"),
    ]
    .join("\n");
    put(&root, "research/to-download.md", &list);
    let w = load(&root).unwrap();
    let got = |id: &str| {
        w.entry_keys[&format!("download:{id}")]
            .iter()
            .cloned()
            .collect::<Vec<_>>()
    };
    assert_eq!(got("1"), ["alpha"]);
    assert_eq!(got("2"), ["beta"]);
    assert_eq!(got("3"), ["gamma"]);
    assert_eq!(got("4"), ["gamma"]);
    assert!(got("5").is_empty());
    assert_eq!(w.keyless, ["download:5"]);
}

#[test]
fn every_lists_sorted_keys_then_the_keyless_once() {
    let root = tree("every", "{}");
    key_file(&root, "beta", &[]);
    key_file(&root, "alpha", &[]);
    put(
        &root,
        "research/sources/010-works-cited/notes.txt",
        "ignored",
    );
    put(
        &root,
        "research/sources/010-works-cited/0020-nohead.html",
        "no heading",
    );
    put(
        &root,
        "research/to-download.md",
        &(entry("2", BLANK, "", "x") + &entry("2", BLANK, "", "y") + &entry("1", BLANK, "", "z")),
    );
    let w = load(&root).unwrap();
    let names: Vec<String> = every(&w).into_iter().map(|(k, _)| k).collect();
    assert_eq!(names, ["alpha", "beta", "download:2", "download:1"]);
}

#[test]
fn the_report_counts_and_prints_each_form() {
    let root = tree("report", "{}");
    key_file(&root, "alpha", &["2021-05-06"]);
    key_file(&root, "beta", &[]);
    put(
        &root,
        "research/to-download.md",
        &entry("5", BLANK, "", "no key"),
    );
    let run = |args: &[&str]| cli(&owned(args), &root);
    let all = run(&["report"]);
    assert_eq!(all.stdout, "access-tags: 2 registry keys and 1 keyless list entries\n  open         1\n  gm-full      0\n  gm-partial   0\n  paywalled    0\n  bot-refused  0\n  down         0\n  gone         0\n  never-read   2\n");
    let json_all = run(&["report", "--json"]);
    assert!(json_all
        .stdout
        .starts_with("{\n \"alpha\": {\n  \"state\": \"open\",\n  \"date\": \"2021-05-06\","));
    assert_eq!(
        run(&["report", "--key", "alpha"]).stdout,
        "alpha: open (2021-05-06) - a READ comment in its registry entry; no archive row\n"
    );
    assert_eq!(
        run(&["report", "--key=beta"]).stdout,
        "beta: never-read (no date) - no READ in its registry entry and no archive row\n"
    );
    assert_eq!(run(&["report", "--key", "alpha", "--json"]).stdout, "{\"alpha\": {\"state\": \"open\", \"date\": \"2021-05-06\", \"basis\": \"a READ comment in its registry entry; no archive row\"}}\n");
    assert_eq!(run(&["report", "--key", "download:5"]).code, 0);
    let none = run(&["report", "--key", "nope"]);
    assert_eq!((none.code, none.stderr.as_str()), (1, "access-tags: REFUSED - no registry key or list entry `nope` - an entry is `download:<id>`\n"));
    assert_eq!(run(&["report", "--bad"]).code, 2);
    assert_eq!(run(&["report", "--key"]).code, 2);
    assert_eq!(run(&[]).code, 2);
    assert_eq!(run(&["set", "a"]).code, 2);
    let keyed = run(&["entry-keys", "5"]);
    assert_eq!((keyed.code, keyed.stdout.as_str()), (0, "[]\n"));
    let missing = run(&["entry-keys", "99"]);
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (
            1,
            "archive: no download-list entry 99 in research/to-download.md\n"
        )
    );
    assert_eq!(run(&["entry-keys"]).code, 2);
    let empty = scratch("report-empty");
    let refused = cli(&owned(&["report"]), &empty);
    assert!(refused.code == 1 && refused.stderr.starts_with("access-tags: REFUSED - "));
    assert_eq!(cli(&owned(&["entry-keys", "1"]), &empty).code, 1);
    put(&empty, "research/source-access.json", "not json");
    assert_eq!(cli(&owned(&["report"]), &empty).code, 1);
    put(
        &empty,
        "research/source-access.json",
        &format!(r#"{{"states":{STATES}}}"#),
    );
    put(&empty, "research/archive/d/a.json", "not json");
    assert_eq!(cli(&owned(&["report"]), &empty).code, 1);
}

#[test]
fn set_records_a_state_or_refuses_naming_the_fix() {
    let root = tree(
        "set",
        r#"{"zeta":[{"state":"open","date":"2020-01-01","reason":"a b"}]}"#,
    );
    let run = |args: &[&str]| cli(&owned(args), &root);
    let done = run(&[
        "set",
        "alpha",
        "paywalled",
        "2026-01-02",
        "it needs a login",
    ]);
    assert_eq!(done.stdout, "access-tags: alpha recorded paywalled (2026-01-02) in research/source-access.json - commit it\n");
    let written = std::fs::read_to_string(root.join("research/source-access.json")).unwrap();
    assert!(written
        .starts_with("{\n \"_about\": \"é\",\n \"states\": [\n  {\n   \"id\": \"open\"\n  },"));
    assert!(written.find("\"alpha\"").unwrap() < written.find("\"zeta\"").unwrap());
    assert!(written.ends_with("}\n}\n"));
    run(&["set", "zeta", "gone", "2026-01-02", "two words"]);
    let w = load(&root).unwrap();
    assert_eq!(w.recorded["zeta"].as_array().unwrap().len(), 2);
    let bad = run(&["set", "a", "nope", "2026-01-02", "two words"]);
    assert!(
        bad.code == 1
            && bad
                .stderr
                .contains("`nope` is not a state - the states are open, gm-full")
    );
    assert!(run(&["set", "a", "open", "bad", "two words"])
        .stderr
        .contains("DATE='bad' - give the date"));
    assert!(run(&["set", "a", "open", "2026-01-02", "one"])
        .stderr
        .contains("REASON= says"));
    let empty = scratch("set-empty");
    assert_eq!(
        cli(
            &owned(&["set", "a", "open", "2026-01-02", "two words"]),
            &empty
        )
        .code,
        1
    );
}

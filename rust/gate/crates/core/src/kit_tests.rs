//! What the core holds for the other gate crates, tested here (feature 449 T92: 100% of a crate's lines by its own tests): the readers
//! and the kit other crates' tests call, which this crate's own modules never do.

use std::path::Path;

use serde_json::json;

use crate::record::args::{parse_with, Spec};
use crate::record::units::{Keyed, Record};

#[test]
fn the_fixtures_build_a_repository_a_python_stand_in_and_a_record_s_edits() {
    let dir = crate::ci::fixtures::repo("kit");
    let python = crate::ci::fixtures::python(&dir);
    assert!(Path::new(&python).is_file());
    let root = crate::record::testkit::record("kit-record");
    crate::record::testkit::edit_everything(&root);
    assert!(std::fs::read_to_string(
        root.join("research/sources/040-uncited-works/20501-key-c.html")
    )
    .unwrap()
    .contains("New."));
    crate::record::bundle::tests::state(&root, &json!({"open": []}));
    assert!(root.join(".git/checks-open.json").is_file());
    assert_eq!(crate::record::bundle::tests::args(&["a", "b"]), ["a", "b"]);
    assert_eq!(
        crate::record::bundle::default_root(),
        std::env::temp_dir().join("l7r-check-tests")
    );
    assert!(
        crate::record::repo::git_out(&root, &["rev-parse", "--is-inside-work-tree"])
            .starts_with("true")
    );
    assert_eq!(
        crate::record::repo::git_out(Path::new("/proc/nonexistent"), &["status"]),
        ""
    );
}

#[test]
fn the_content_id_s_readers_say_what_failed() {
    let dir = crate::checks::scratch("kit-codeid");
    let cache = crate::codeid::Cache::at(&dir);
    assert!(cache.kept("nothing kept").is_none());
    assert!(crate::codeid::parsed("{", "a table")
        .unwrap_err()
        .starts_with("a table: "));
    assert_eq!(crate::codeid::parsed("[1]", "a table").unwrap(), json!([1]));
    assert!(crate::codeid::script(&dir).ends_with("scripts/gates/codeid.py"));
}

#[test]
fn json_is_written_as_python_writes_it() {
    assert_eq!(
        crate::logs::py_dumps(&json!({"a": [1]}), 1, true),
        "{\n \"a\": [\n  1\n ]\n}"
    );
    assert_eq!(
        crate::logs::one_line_utf8(&json!("caf\u{e9}")),
        "\"caf\u{e9}\""
    );
}

#[test]
fn a_list_a_last_value_and_a_positional_are_read_as_argparse_reads_them() {
    let specs = [Spec::list("--keys"), Spec::value("--a"), Spec::value("--b")];
    let words: Vec<String> = [
        "pos", "--keys", "x", "y", "--a", "1", "--b", "2", "--a", "3",
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    let got = parse_with(&words, &specs, 1).unwrap();
    assert_eq!(got.positional, ["pos"]);
    assert_eq!(got.list("--keys"), ["x", "y"]);
    assert!(got.list("--none").is_empty());
    assert_eq!(got.last_of(&["--a", "--b"], "d"), "3");
    assert_eq!(got.last_of(&["--c"], "d"), "d");
    assert!(got.has("--b") && !got.has("--c"));
}

#[test]
fn the_kept_pages_start_again_past_their_cap_and_a_table_extends() {
    let mut files = Keyed::default();
    for n in 0..12 {
        files.insert(
            format!("{n:04}-kit.html"),
            format!("<h2>Page {n}</h2>\n<p>Body {n}.</p>\n"),
        );
    }
    let rec = Record::of(&files, &Keyed::default());
    assert!(rec.pages.contains("0011"));
    let mut table: Keyed<u32> = Keyed::default();
    table.extend([("a".to_owned(), 1), ("b".to_owned(), 2)]);
    assert_eq!(table.get("b"), Some(&2));
}

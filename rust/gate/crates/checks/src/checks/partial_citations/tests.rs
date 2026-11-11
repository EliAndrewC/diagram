//! The check, on scratch trees.

use std::path::Path;

use super::cli;
use crate::checks::scratch;

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn run(root: &Path) -> crate::checks::Outcome {
    cli(&[root.display().to_string()])
}

#[test]
fn a_tree_with_no_access_states_names_nothing() {
    let root = scratch("partial-none");
    put(
        &root,
        "research/questions/0001-a.notes.html",
        "<li data-note=\"n\"><code>alpha</code></li>",
    );
    assert_eq!(run(&root).code, 0);
    assert_eq!(cli(&["/no/such/tree".to_owned()]).code, 0);
}

#[test]
fn an_unconfirmed_footnote_on_an_unreadable_source_is_refused_each_once() {
    let root = scratch("partial");
    put(
        &root,
        "research/source-access.json",
        r#"{"states":[{"id":"open"},{"id":"paywalled"},{"id":"never-read"}],"recorded":{"beta":[{"state":"open","date":"2020-01-01","reason":"a b"}]}}"#,
    );
    put(
        &root,
        "research/sources/010-works-cited/0010-alpha.html",
        "<h3 id=\"alpha\">x</h3>",
    );
    put(
        &root,
        "research/sources/010-works-cited/0020-beta.html",
        "<h3 id=\"beta\">x</h3>",
    );
    put(&root, "research/questions/0001-a.notes.html", "<li data-note=\"n1\"><code>alpha</code> and <code>alpha</code>\n<code>beta</code> <code>unknown</code></li>");
    put(
        &root,
        "research/questions/0002-b.notes.html",
        "<li data-note=\"n2\"><code>alpha</code></li>",
    );
    put(
        &root,
        "research/questions/0002-b.html",
        "<li data-note=\"n9\"><code>alpha</code></li>",
    );
    let out = run(&root);
    assert_eq!(out.code, 1);
    assert_eq!(out.stderr, "check-partial-citations: 0001-a.notes.html#n1: cites `alpha` (never-read) with no confirmed passage - confirm it from the readable part (make quote-verbatim, then quote-check) and record it in partial-confirmations.jsonl, or make the note an absence note\ncheck-partial-citations: 0002-b.notes.html#n2: cites `alpha` (never-read) with no confirmed passage - confirm it from the readable part (make quote-verbatim, then quote-check) and record it in partial-confirmations.jsonl, or make the note an absence note\n");
    put(&root, "research/partial-confirmations.jsonl", "{\"key\": \"alpha\", \"note\": \"0001-a.notes.html#n1\"}\nnot json\n{\"key\": \"alpha\", \"note\": \"0002-b.notes.html#n2\"}\n");
    let out = run(&root);
    assert_eq!((out.code, out.stderr.as_str()), (0, ""));
}

#[test]
fn a_tree_the_tags_cannot_read_is_refused() {
    let root = scratch("partial-bad");
    put(&root, "research/source-access.json", "not json");
    let out = run(&root);
    assert!(out.code == 1 && out.stderr.starts_with("check-partial-citations: "));
}

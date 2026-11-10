//! The edit router, the fragment listing, and the two batch verbs, on scratch trees: `hm_record.py`'s selftest shapes and the hook's own payloads.

use std::path::Path;
use std::process::Command;

use serde_json::{json, Value};

use super::{
    abspath, americanize_cli, decide, edit_route, fragments_cli, fragments_for, moved_only_cli,
    page_dir_for, relpath,
};

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

fn tree(tag: &str) -> std::path::PathBuf {
    let root = crate::checks::scratch(tag);
    let q = root.join("research/questions");
    std::fs::create_dir_all(&q).unwrap();
    std::fs::write(
        q.join("0010-x.html"),
        "<h2 id='x'>X</h2>\nthe deck lands ten feet past the bank\n",
    )
    .unwrap();
    std::fs::write(
        q.join("0010-x.notes.html"),
        "<li data-note=\"k\">body</li>\n",
    )
    .unwrap();
    std::fs::write(
        q.join("0010-x.drawing.html"),
        "<h2 id='dx'>DX</h2>\nshared sentence\n",
    )
    .unwrap();
    std::fs::write(
        q.join("0020-y.html"),
        "<h2 id='y'>Y</h2>\nshared sentence\n",
    )
    .unwrap();
    root
}

#[test]
fn page_dirs_are_the_questions_or_the_registry_and_a_fragment_is_no_page() {
    let q = Some("research/questions".to_owned());
    assert_eq!(
        page_dir_for("research/SOURCES.html").as_deref(),
        Some("research/sources")
    );
    assert_eq!(
        page_dir_for("research/site/sources/fei-1939.html").as_deref(),
        Some("research/sources")
    );
    assert_eq!(page_dir_for("research/site/q/x.html"), q);
    assert_eq!(page_dir_for("research/site/all.html"), q);
    assert_eq!(page_dir_for("research/ways.html"), q);
    assert_eq!(page_dir_for("research/citations/ways.html"), q);
    assert_eq!(page_dir_for("research/questions/0010-x.html"), None);
    assert_eq!(page_dir_for("research/assets/record.js"), None);
    assert_eq!(page_dir_for("docs/guards.md"), None);
    assert_eq!(
        page_dir_for("l7r/diagram/interactive/assets/glossary.json").as_deref(),
        Some("l7r/diagram/interactive/assets/glossary")
    );
    assert_eq!(
        page_dir_for("clone/research/site/q/x.html").as_deref(),
        Some("clone/research/questions")
    );
}

#[test]
fn a_path_is_made_relative_in_its_text_alone() {
    let cwd = Path::new("/a/b");
    assert_eq!(abspath("../c/./d", cwd), ["a", "c", "d"]);
    assert_eq!(relpath("/a/b/c.html", "/a/b", cwd), "c.html");
    assert_eq!(relpath("/x/y.html", "/a/b", cwd), "../../x/y.html");
    assert_eq!(relpath("/a/b", "/a/b", cwd), ".");
}

#[test]
fn an_edit_goes_to_the_one_fragment_holding_its_text() {
    let root = tree("leaves-one");
    let site = root.join("research/site/q");
    std::fs::create_dir_all(&site).unwrap();
    let page = site.join("x.html");
    std::fs::write(&page, "the deck lands ten feet past the bank\n").unwrap();
    let got = decide(
        "Edit",
        &json!({"file_path": page, "old_string": "ten feet past the bank"}),
        &root.to_string_lossy(),
        Path::new("/"),
    );
    assert_eq!(got["verdict"], "rewrite");
    assert_eq!(got["fragment"], "research/questions/0010-x.html");
    assert_eq!(got["page"], "research/site/q/x.html");
}

#[test]
fn a_line_end_of_any_kind_reads_as_newline_and_undecodable_text_is_skipped() {
    let root = tree("leaves-crlf");
    let q = root.join("research/questions");
    std::fs::write(q.join("0030-crlf.html"), "first line\r\nsecond line\r\n").unwrap();
    std::fs::write(q.join("0040-binary.html"), b"first line\nsecond line\xff\n").unwrap();
    let page = root.join("research/all.html");
    let got = decide(
        "Edit",
        &json!({"file_path": page, "old_string": "first line\nsecond line"}),
        &root.to_string_lossy(),
        Path::new("/"),
    );
    assert_eq!(got["fragment"], "research/questions/0030-crlf.html");
}

#[test]
fn the_build_itself_is_no_holder_and_a_symlinked_directory_is_not_walked() {
    let root = tree("leaves-site");
    let q = root.join("research/questions");
    for skipped in ["site", ".site-tmp"] {
        std::fs::create_dir_all(q.join(skipped)).unwrap();
        std::fs::write(q.join(skipped).join("copy.html"), "unique words\n").unwrap();
    }
    std::os::unix::fs::symlink(q.join("site"), q.join("linked")).unwrap();
    std::fs::create_dir_all(q.join("deep")).unwrap();
    std::fs::write(q.join("deep/inner.html"), "unique words\n").unwrap();
    let got = decide(
        "Edit",
        &json!({"file_path": root.join("research/all.html"), "old_string": "unique words"}),
        &root.to_string_lossy(),
        Path::new("/"),
    );
    assert_eq!(got["fragment"], "research/questions/deep/inner.html");
}

#[test]
fn what_is_refused_names_the_rule_and_its_rebuild() {
    let root = tree("leaves-refuse");
    let r = root.to_string_lossy().into_owned();
    let page = root.join("research/site/q/x.html");
    let ask = |old: &str| {
        decide(
            "Edit",
            &json!({"file_path": page, "old_string": old}),
            &r,
            Path::new("/"),
        )
    };
    let several = ask("shared sentence");
    assert_eq!(several["rule"], "text-in-several-fragments");
    assert!(several["message"]
        .as_str()
        .unwrap()
        .contains("stands in 2 fragments"));
    assert_eq!(ask("nowhere at all")["rule"], "text-in-no-fragment");
    assert!(ask("nowhere at all")["message"]
        .as_str()
        .unwrap()
        .contains("footnote number"));
    assert_eq!(ask("")["rule"], "text-in-no-fragment");
    let null = decide(
        "Edit",
        &json!({"file_path": page, "old_string": null}),
        &r,
        Path::new("/"),
    );
    assert_eq!(null["rule"], "text-in-no-fragment");
    let write = decide("Write", &json!({"file_path": page}), &r, Path::new("/"));
    assert_eq!(write["rule"], "write-to-assembled-page");
    assert!(write["message"].as_str().unwrap().contains("`make record`"));
}

#[test]
fn the_glossary_is_a_page_of_the_same_kind() {
    let root = crate::checks::scratch("leaves-gloss");
    let terms = root.join("l7r/diagram/interactive/assets/glossary");
    std::fs::create_dir_all(&terms).unwrap();
    std::fs::write(
        terms.join("0010-girder.json"),
        "{\"def\": \"the main beam\"}",
    )
    .unwrap();
    let r = root.to_string_lossy().into_owned();
    let glossary = root.join("l7r/diagram/interactive/assets/glossary.json");
    let moved = decide(
        "Edit",
        &json!({"file_path": glossary, "old_string": "the main beam"}),
        &r,
        Path::new("/"),
    );
    assert!(moved["fragment"]
        .as_str()
        .unwrap()
        .ends_with("0010-girder.json"));
    let write = decide("Write", &json!({"file_path": glossary}), &r, Path::new("/"));
    assert!(write["message"].as_str().unwrap().contains("make glossary"));
    let none = decide(
        "Edit",
        &json!({"file_path": glossary, "old_string": "absent"}),
        &r,
        Path::new("/"),
    );
    assert!(none["message"].as_str().unwrap().contains("braces"));
}

#[test]
fn what_is_not_an_assembled_page_passes() {
    let root = tree("leaves-pass");
    let r = root.to_string_lossy().into_owned();
    let cwd = Path::new("/");
    let fragment = root.join("research/questions/0010-x.html");
    let got = decide(
        "Edit",
        &json!({"file_path": fragment, "old_string": "the deck"}),
        &r,
        cwd,
    );
    assert_eq!(got["verdict"], "pass");
    assert!(got["reason"].as_str().unwrap().contains("not an assembled"));
    assert_eq!(
        decide("Bash", &json!({}), &r, cwd),
        json!({"verdict": "pass"})
    );
    assert_eq!(
        decide("Edit", &json!({}), &r, cwd),
        json!({"verdict": "pass"})
    );
    let no_registry = root.join("research/SOURCES.html");
    assert_eq!(
        decide(
            "Edit",
            &json!({"file_path": no_registry, "old_string": "x"}),
            &r,
            cwd
        )["verdict"],
        "pass"
    );
}

#[test]
fn a_question_lists_its_pages_and_notes_by_number_or_name() {
    let root = tree("leaves-frag");
    let q = "research/questions";
    assert_eq!(
        fragments_for("0010", &root),
        [
            format!("{q}/0010-x.drawing.html"),
            format!("{q}/0010-x.html"),
            format!("{q}/0010-x.notes.html"),
        ]
    );
    assert_eq!(
        fragments_for("10, 0020-y.html", &root).last().unwrap(),
        &format!("{q}/0020-y.html")
    );
    assert_eq!(
        fragments_for("0010-x.drawing.html", &root),
        [format!("{q}/0010-x.drawing.html")]
    );
    assert!(fragments_for("nosuch", &root).is_empty());
    assert!(fragments_for("0010", &root.join("elsewhere")).is_empty());
    assert_eq!(fragments_for("10 10", &root).len(), 3);
}

#[test]
fn the_hook_payload_comes_back_as_a_python_json_line() {
    let root = tree("leaves-route");
    let site = root.join("research/site/q/x.html");
    let payload = json!({"cwd": root, "tool_name": "Edit", "tool_input": {
        "file_path": site, "old_string": "ten feet past the bank", "new_string": "N é"}});
    let got = edit_route(&mut payload.to_string().as_bytes(), Path::new("/"));
    assert_eq!(got.code, 0);
    assert!(got
        .stdout
        .starts_with("{\"verdict\": \"rewrite\", \"rule\""));
    assert!(got.stdout.contains("\\u00e9"));
    let line: Value = serde_json::from_str(&got.stdout).unwrap();
    let hook = &line["hook"]["hookSpecificOutput"];
    assert_eq!(hook["hookEventName"], "PreToolUse");
    assert_eq!(
        hook["updatedInput"]["file_path"],
        root.join("research/questions/0010-x.html")
            .to_string_lossy()
            .as_ref()
    );
    assert_eq!(hook["updatedInput"]["new_string"], "N é");
    assert!(hook["additionalContext"]
        .as_str()
        .unwrap()
        .contains("assembled from research/questions/ and is never hand-edited"));
    let refusal = json!({"cwd": root, "tool_name": "Write", "tool_input": {"file_path": site}});
    let got = edit_route(&mut refusal.to_string().as_bytes(), Path::new("/"));
    assert_eq!(
        serde_json::from_str::<Value>(&got.stdout).unwrap()["verdict"],
        "refuse"
    );
}

#[test]
fn a_payload_that_is_no_object_fails_as_the_python_did_and_an_empty_input_passes() {
    let cwd = Path::new("/");
    for bad in ["not json", "[1]"] {
        let got = edit_route(&mut bad.as_bytes(), cwd);
        assert_eq!((got.code, got.stdout.as_str()), (1, ""));
    }
    let got = edit_route(&mut "{\"tool_input\": \"x\"}".as_bytes(), cwd);
    assert_eq!((got.code, got.stdout.as_str()), (1, ""));
    for falsy in ["null", "false", "0", "\"\"", "[]", "{}"] {
        let body = format!("{{\"tool_name\": \"Edit\", \"tool_input\": {falsy}}}");
        let got = edit_route(&mut body.as_bytes(), cwd);
        assert_eq!(got.code, 0, "{falsy}");
        assert_eq!(got.stdout, "{\"verdict\": \"pass\"}\n");
    }
    let numbers = "{\"tool_name\": \"Edit\", \"cwd\": \"\", \"tool_input\": {\"file_path\": 7, \"old_string\": null}}";
    let got = edit_route(&mut numbers.as_bytes(), cwd);
    assert_eq!(got.code, 0);
}

#[test]
fn every_asked_question_is_answered_in_one_call() {
    let root = tree("leaves-cli");
    let args = ["--root".to_owned(), root.to_string_lossy().into_owned()];
    let got = fragments_cli(
        &args,
        &mut "[\"0020\", \"nosuch\"]".as_bytes(),
        Path::new("/"),
    );
    let found: Value = serde_json::from_str(&got.stdout).unwrap();
    assert_eq!(found["0020"], json!(["research/questions/0020-y.html"]));
    assert_eq!(found["nosuch"], json!([]));
    let inside = fragments_cli(&[], &mut "[\"0020\"]".as_bytes(), &root);
    assert!(inside.stdout.contains("0020-y.html"));
    let bad = fragments_cli(&[], &mut "not a list".as_bytes(), &root);
    assert_eq!((bad.code, bad.stdout.as_str()), (1, ""));
}

#[test]
fn the_moved_names_come_back_one_a_line() {
    let dir = crate::checks::scratch("leaves-moves");
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    std::fs::write(dir.join("old.md"), "same\n").unwrap();
    git(&dir, &["add", "-A"]);
    git(&dir, &["commit", "-qm", "c"]);
    std::fs::write(dir.join("new.md"), "same\n").unwrap();
    std::fs::write(dir.join("edited.md"), "different\n").unwrap();
    let args = [
        "--root".to_owned(),
        dir.to_string_lossy().into_owned(),
        "--base".to_owned(),
        "HEAD".to_owned(),
    ];
    let got = moved_only_cli(
        &args,
        &mut "new.md\nedited.md\ngone.md\n".as_bytes(),
        Path::new("/"),
    );
    assert_eq!((got.code, got.stdout.as_str()), (0, "new.md\n"));
    let usage = moved_only_cli(&[], &mut "".as_bytes(), Path::new("/"));
    assert_eq!((usage.code, usage.stdout.as_str()), (2, ""));
}

#[test]
fn the_verbs_are_reached_by_name() {
    let cwd = Path::new("/");
    assert_eq!(
        super::cli("edit-route", &[], &mut "{}".as_bytes(), cwd).code,
        0
    );
    assert_eq!(
        super::cli("fragments", &[], &mut "[]".as_bytes(), cwd).code,
        0
    );
    assert_eq!(
        super::cli("moved-only", &[], &mut "".as_bytes(), cwd).code,
        2
    );
    assert_eq!(
        super::cli("americanize", &[], &mut "[]".as_bytes(), cwd).code,
        0
    );
}

#[test]
fn every_string_is_styled_and_the_shape_is_kept() {
    let brit = format!("gr{}", "ey");
    let key = format!("col{}r", "ou");
    let body = format!(
        "{{\"{key}\": [\"a {brit} band\", 1, null, {{\"k\": \"`{brit}` is named\"}}], \"n\": 1.5}}"
    );
    let got = americanize_cli(&mut body.as_bytes());
    assert_eq!(
        got.stdout,
        format!("{{\"{key}\": [\"a gray band\", 1, null, {{\"k\": \"`{brit}` is named\"}}], \"n\": 1.5}}\n")
    );
    let bad = americanize_cli(&mut "not json".as_bytes());
    assert_eq!((bad.code, bad.stdout.as_str()), (1, ""));
}

//! Moving a question, on a scratch repository.

use std::path::Path;

use super::{cli, ensure, read_text, relocate, selftest_reply};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn get(root: &Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap()
}

fn git(root: &Path, args: &[&str]) {
    assert!(crate::cohort::git(root, args).0, "{args:?}");
}

fn repo(tag: &str, files: &[(&str, &str)]) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    for (rel, text) in files {
        put(&root, rel, text);
    }
    git(&root, &["init", "-q"]);
    git(&root, &["add", "-A"]);
    root
}

const A: &str = "research/questions/0001-a.html";
const B: &str = "research/questions/0002-b.html";

#[test]
fn the_selftest_passes_and_a_failure_is_exit_1() {
    let ok = cli(&words(&["--selftest"]));
    assert_eq!(ok.stderr, "");
    assert_eq!(
        (ok.stdout.as_str(), ok.code),
        ("fragment-move selftest ok\n", 0)
    );
    let failed = selftest_reply(ensure(false, "a check"));
    assert_eq!(failed.code, 1);
    assert!(failed.stderr.contains("selftest failed: a check"));
}

#[test]
fn the_command_line_reports_the_move_or_its_refusal() {
    let root = repo("fm-cli", &[(A, "<h2 id=\"a\">A</h2>")]);
    let at = root.display().to_string();
    let refused = cli(&words(&[
        "research/questions/0009-gone.html",
        B,
        "--root",
        &at,
    ]));
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.starts_with("fragment-move: FROM="));
    let done = cli(&words(&["--root", &at, A, B]));
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert_eq!(done.stdout, format!("fragment-move: {A} -> {B}; 1 file(s) changed:\n  {B}\nthen `make record` at the repository root, and commit\n"));
    assert_eq!(get(&root, B), "<h2 id=\"b\">A</h2>");
}

#[test]
fn a_wrong_shape_of_arguments_is_the_usage() {
    for args in [
        &[][..],
        &["only-one"][..],
        &["a", "b", "--root"][..],
        &["a", "b", "c"][..],
    ] {
        let got = cli(&words(args));
        assert_eq!(got.code, 2, "{args:?}");
        assert!(got.stderr.starts_with("usage: make fragment-move"));
    }
}

#[test]
fn the_root_defaults_to_here_and_a_root_that_is_not_there_refuses() {
    let got = cli(&words(&[A, B, "--root", "/nonexistent/place"]));
    assert_eq!(got.code, 1);
    let here = cli(&words(&["research/questions/9999-absent.html", B]));
    assert_eq!(here.code, 1);
}

#[test]
fn a_kept_slug_leaves_the_heading_and_an_anchor_of_a_drawing_only_question_moves() {
    let root = repo(
        "fm-slug",
        &[
            (
                "research/questions/0001-same.html",
                "<h2 id=\"same\">S</h2>",
            ),
            (
                "research/questions/0005-draw.drawing.html",
                "<h3 id=\"draw\">D</h3>",
            ),
            (
                "research/questions/0006-o.html",
                "<a href=\"0005-draw.drawing.html#draw\">x</a><a href=\"0001-same.html\">y</a>",
            ),
        ],
    );
    relocate(
        &root,
        "research/questions/0001-same.html",
        "research/questions/0002-same.html",
    )
    .unwrap();
    assert_eq!(
        get(&root, "research/questions/0002-same.html"),
        "<h2 id=\"same\">S</h2>"
    );
    assert!(get(&root, "research/questions/0006-o.html").contains("href=\"0002-same.html\""));
    relocate(
        &root,
        "research/questions/0005-draw.drawing.html",
        "research/questions/0005-drawn.drawing.html",
    )
    .unwrap();
    assert_eq!(
        get(&root, "research/questions/0005-drawn.drawing.html"),
        "<h3 id=\"drawn\">D</h3>"
    );
    assert!(get(&root, "research/questions/0006-o.html")
        .contains("href=\"0005-drawn.drawing.html#drawn\""));
}

#[test]
fn a_research_pages_anchor_on_its_drawing_link_stays() {
    let root = repo(
        "fm-anchor",
        &[
            ("research/questions/0001-a.html", "<h2 id=\"a\">A</h2>"),
            (
                "research/questions/0001-a.drawing.html",
                "<h2 id=\"d\">D</h2>",
            ),
            (
                "research/questions/0007-o.html",
                "<a href=\"0001-a.drawing.html#a\">x</a>",
            ),
        ],
    );
    relocate(&root, A, "research/questions/0001-z.html").unwrap();
    assert!(get(&root, "research/questions/0007-o.html").contains("href=\"0001-z.drawing.html#a\""));
}

#[test]
fn the_confusables_are_reaimed_or_a_malformed_file_stops_the_move() {
    let page = [(A, "<h2 id=\"a\">A</h2>")];
    let root = repo("fm-conf", &[page[0], ("research/confusables.json", "[{\"a\": \"0001-a.html\", \"b\": \"0001-a.html#a\"}, {\"a\": \"0009-x.html#x\", \"b\": \"caf\u{e9}.html#y\"}]")]);
    relocate(&root, A, B).unwrap();
    assert_eq!(
        get(&root, "research/confusables.json"),
        "[\n {\n  \"a\": \"0002-b.html#\",\n  \"b\": \"0002-b.html#b\"\n },\n {\n  \"a\": \"0009-x.html#x\",\n  \"b\": \"caf\u{e9}.html#y\"\n }\n]\n"
    );
    let kept = repo(
        "fm-conf2",
        &[
            page[0],
            (
                "research/confusables.json",
                "[{\"a\": \"0009-x.html#x\", \"b\": \"0010-y.html#y\"}]",
            ),
        ],
    );
    let changed = relocate(&kept, A, B).unwrap();
    assert!(!changed.iter().any(|c| c.contains("confusables")));
    for (tag, body) in [
        ("fm-bad1", "not json"),
        ("fm-bad2", "{}"),
        ("fm-bad3", "[{\"a\": \"x\"}]"),
    ] {
        let bad = repo(tag, &[page[0], ("research/confusables.json", body)]);
        assert!(relocate(&bad, A, B).is_err(), "{tag}");
    }
}

#[test]
fn the_mapping_moves_only_when_it_names_the_question() {
    let page = (A, "<h2 id=\"a\">A</h2>");
    let root = repo(
        "fm-map",
        &[
            page,
            (
                "research/moved-303.json",
                "{\"x\": \"questions/0001-a.html\", \"y\": \"questions/0001-a-b.html\"}",
            ),
        ],
    );
    let changed = relocate(&root, A, B).unwrap();
    assert!(changed.iter().any(|c| c == "research/moved-303.json"));
    assert_eq!(
        get(&root, "research/moved-303.json"),
        "{\"x\": \"questions/0002-b.html\", \"y\": \"questions/0001-a-b.html\"}"
    );
    let silent = repo("fm-map2", &[page, ("research/moved-303.json", "{}")]);
    assert!(!relocate(&silent, A, B)
        .unwrap()
        .iter()
        .any(|c| c.contains("moved-303")));
}

#[test]
fn tracked_files_are_repointed_only_where_a_whole_pointer_stands() {
    let root = repo(
        "fm-tracked",
        &[
            (A, "<h2 id=\"a\">A</h2>"),
            ("research/other.txt", "research/questions/0001-a.html"),
            ("docs/a.md", "see research/questions/0001-a.notes.html and /research/questions/0001-a.drawing.html\r\nand xresearch/questions/0001-a.html\n"),
            ("docs/plain.md", "0001-a alone\r\n"),
            ("docs/$weird.md", "research/questions/0001-a.html"),
            ("bin.dat", "x"),
            ("gone.md", "research/questions/0001-a.html"),
        ],
    );
    std::fs::write(root.join("bin.dat"), [0xff_u8, 0xfe, 0x00]).unwrap();
    std::fs::write(root.join("gone.md"), "").unwrap();
    git(&root, &["add", "-A"]);
    let gone = root.join("gone.md");
    let _ = std::fs::remove_file(&gone);
    let changed = relocate(&root, A, B).unwrap();
    assert!(changed.iter().any(|c| c == "docs/a.md"));
    assert!(!changed
        .iter()
        .any(|c| c == "docs/plain.md" || c == "research/other.txt"));
    assert_eq!(
        get(&root, "docs/a.md"),
        "see research/questions/0002-b.notes.html and /research/questions/0002-b.drawing.html\nand xresearch/questions/0001-a.html\n"
    );
    assert_eq!(get(&root, "docs/plain.md"), "0001-a alone\r\n");
    assert_eq!(
        get(&root, "research/other.txt"),
        "research/questions/0001-a.html"
    );
    assert!(gone.metadata().is_err());
}

#[test]
fn a_new_stem_with_a_dollar_is_taken_literally() {
    let root = repo(
        "fm-dollar",
        &[
            (A, "<h2 id=\"a\">A</h2>"),
            ("x.md", "research/questions/0001-a.html"),
        ],
    );
    let to = "research/questions/0002-$1b.html";
    relocate(&root, A, to).unwrap();
    assert_eq!(get(&root, "x.md"), "research/questions/0002-$1b.html");
    assert_eq!(get(&root, to), "<h2 id=\"$1b\">A</h2>");
}

#[test]
fn a_git_failure_or_an_unreadable_file_stops_the_move() {
    let plain = crate::checks::scratch("fm-nogit");
    put(&plain, A, "<h2 id=\"a\">A</h2>");
    assert!(relocate(&plain, A, B).unwrap_err().contains("git mv"));
    let root = repo(
        "fm-unreadable",
        &[(A, "<h2 id=\"a\">A</h2>"), ("sub/file.txt", "x")],
    );
    std::fs::remove_dir_all(root.join("sub")).unwrap();
    std::fs::write(root.join("sub"), "now a file").unwrap();
    assert!(relocate(&root, A, B)
        .unwrap_err()
        .starts_with("sub/file.txt"));
    let broken = repo(
        "fm-binary-page",
        &[
            (A, "<h2 id=\"a\">A</h2>"),
            ("research/questions/0003-c.html", "x"),
        ],
    );
    std::fs::write(broken.join("research/questions/0003-c.html"), [0xff_u8]).unwrap();
    assert!(relocate(&broken, A, B).is_err());
}

#[test]
fn the_selftests_seed_fails_when_its_root_cannot_be_made() {
    let root = crate::checks::scratch("fm-seed");
    put(&root, "a-file", "");
    assert!(super::seed(&root.join("a-file")).is_err());
}

#[test]
fn text_is_read_as_python_reads_it() {
    let root = crate::checks::scratch("fm-read");
    put(&root, "a", "a\r\nb\rc\n");
    assert_eq!(read_text(&root.join("a")).unwrap(), "a\nb\nc\n");
    std::fs::write(root.join("b"), [0xff_u8]).unwrap();
    assert_eq!(
        read_text(&root.join("b")).unwrap_err().kind(),
        std::io::ErrorKind::InvalidData
    );
    assert_eq!(
        read_text(&root.join("c")).unwrap_err().kind(),
        std::io::ErrorKind::NotFound
    );
    let (bad, why) = (super::read(&root.join("c")), "c:");
    assert!(bad.unwrap_err().contains(why));
    assert!(super::save(&root.join("no/such/dir/x"), "y").is_err());
}

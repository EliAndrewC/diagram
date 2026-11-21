//! An assert's message a format pass put on a line of its own (feature 451 T114): named by `make format`, where it is written.

use std::path::Path;

use super::{dispatch, two_crates, world_with};
use crate::rustc::assertline::{counted, created, listing, scan, Hit, FIX};

fn lines(text: &str) -> Vec<usize> {
    scan(text).iter().map(|h| h.line).collect()
}

/// T108's three asserts as `make format` left them (`git show 9a11c3b6a4^`: `wait/tests.rs` 324-327 and 352-356,
/// `house_style_hooks/tests.rs` 375-379), each message on a line of its own; its landing's cover named 326, 357 and 378.
const T108: &str = r#"    let said = String::from_utf8_lossy(&out.stdout);
    assert!(
        done.is_some_and(|s| s.success()),
        "the loop was not read in 10 s: {said}"
    );
        assert_eq!(
            super::cond_grammar(text).as_deref(),
            Some(&*want),
            "{text:?}"
        );
        assert_eq!(
            super::masked(&text),
            String::from_utf8_lossy(&bytes),
            "{text:?}"
        );
"#;

#[test]
fn t108_s_three_messages_are_named_and_its_fold_is_not() {
    let hits = scan(T108);
    let want = [
        (4, "assert", "\"the loop was not read in 10 s: {said}\""),
        (9, "assert_eq", "\"{text:?}\""),
        (14, "assert_eq", "\"{text:?}\""),
    ];
    let got: Vec<(usize, &str, &str)> = hits
        .iter()
        .map(|h| (h.line, h.mac, h.text.as_str()))
        .collect();
    assert_eq!(got, want);
    // T108's second commit: the values bound first, each assert one line
    let folded = "    let read = done.is_some_and(|s| s.success());\n    assert!(read, \"the loop was not read in 10 s: {said}\");\n    let got = super::cond_grammar(text);\n    assert_eq!(got.as_deref(), Some(&*want), \"{text:?}\");\n";
    assert!(scan(folded).is_empty());
}

#[test]
fn the_shapes_a_passing_assert_runs_are_not_named() {
    // assert!'s bare "{}" and a place (the fixture: lines 138-139 ran), a message beside its condition, an assert on one line
    let runs = "assert!(\n    r.stderr.len() == 1,\n    \"{}\",\n    r.stderr\n);\nassert!(\n    x.len() == 3, \"{x:?}\"\n);\nassert_eq!(a, b, \"{a}\");\nassert!(ok);\n";
    assert!(scan(runs).is_empty());
    // not counted: the debug_ forms, words that only name a macro, and an item the coverage build compiles out
    let unread = "debug_assert_eq!(\n    a,\n    b,\n    \"{a}\"\n);\n// assert_eq!(\nlet s = \"assert_eq!(\";\n#[cfg(feature = \"counters\")]\n#[test]\nfn counted_build() {\n    assert_eq!(\n        a,\n        b,\n        \"{a}\"\n    );\n}\n";
    assert!(scan(unread).is_empty());
}

#[test]
fn every_shape_the_fixture_found_unrun_is_named() {
    // assert!'s literal and its worded "{}" (fixture lines 41, 148); assert_eq!'s bare "{}" (159), and a call among the arguments (32)
    let text = "assert!(\n    ok,\n    \"plain\"\n);\nassert!(\n    ok,\n    \"text: {}\",\n    r.stderr\n);\nassert_ne!(\n    a,\n    b,\n    \"{}\",\n    r.stderr\n);\nassert!(\n    ok,\n    \"{}\",\n    x.len()\n);\n";
    assert_eq!(lines(text), [3, 7, 13, 19]);
    // two unrun pieces on one line are one line; an argument after a trailing comma is no argument
    let one_line = "assert_eq!(\n    a,\n    b,\n    \"{}\", x.len(),\n);\n";
    assert_eq!(
        scan(one_line),
        [Hit {
            line: 4,
            mac: "assert_eq",
            text: "\"{}\"".to_owned()
        }]
    );
}

#[test]
fn literals_comments_and_lifetimes_hide_no_bracket() {
    // a raw string, an escaped quote, a character literal of a bracket, a lifetime, a block comment: the message is still found
    let text = "fn f<'a>(x: &'a str) {\n    let c = ('(', '\\'', '\\u{1F600}', 'é');\n    /* ) , */\n    assert_eq!(\n        r#\"a\"(\"#,\n        \"b\\\")\",\n        \"{x}\"\n    );\n}\n";
    assert_eq!(lines(text), [7]);
    // what never closes ends the text: an unclosed raw string, block comment, escape, item and call find nothing more
    for open in [
        "r#\"never",
        "/* never",
        "'\\never",
        "#[cfg(feature = \"x\")]\nfn f() { assert_eq!(\n a,\n b,\n \"{a}\"\n",
        "assert_eq!(\n a,\n b,\n \"{a}\"\n",
        "#[cfg(feature = \"x\")]",
        "#[cfg(feature = \"x\")]\nmod m;\nassert!(\n ok,\n \"{m}\"\n);",
        "assert!()",
    ] {
        let got = lines(open);
        assert!(got.len() <= 1, "{open:?}: {got:?}");
    }
}

#[test]
fn only_a_message_the_pass_made_is_reported() {
    let split = "assert_eq!(\n    a,\n    b,\n    \"{a}\"\n);\n";
    assert!(created(split, split).is_empty());
    assert_eq!(created("assert_eq!(a, b, \"{a}\");\n", split).len(), 1);
    // a file under tests/ is not in the coverage report; a file named tests.rs is
    assert!(!counted(Path::new("/c"), Path::new("/c/src/x/tests/y.rs")));
    assert!(counted(Path::new("/c"), Path::new("/c/src/x/tests.rs")));
    let hit = Hit {
        line: 9,
        mac: "assert_eq",
        text: "\"{a}\"".to_owned(),
    };
    let said = listing(&[("rust/a/src/lib.rs".to_owned(), vec![hit])]);
    assert!(
        said.contains("  rust/a/src/lib.rs:9: assert_eq! message \"{a}\"\n"),
        "{said}"
    );
    assert!(said.ends_with(&format!("  fix: {FIX}\n")), "{said}");
    assert!(FIX.starts_with("bind the values to locals first so the assert fits one line"));
}

/// The one-line assert `make format` will split, and what the fake format pass writes in its place.
const ONE: &str = "fn t() {\n    assert_eq!(a, b, \"{a}\");\n}\n";
const SPLIT: &str =
    "fn t() {\n    assert_eq!(\n        a,\n        b,\n        \"{a}\"\n    );\n}\n";

#[test]
fn a_crate_format_names_the_line_it_made_and_its_fix() {
    let (root, ..) = two_crates();
    std::fs::write(root.join("rust/a/src/lib.rs"), ONE).unwrap();
    std::fs::create_dir_all(root.join("rust/a/tests")).unwrap();
    std::fs::write(root.join("rust/a/tests/t.rs"), ONE).unwrap();
    // a crate nested in this one's directory owns its own lines, and its own format run
    std::fs::create_dir_all(root.join("rust/a/inner/src")).unwrap();
    std::fs::write(root.join("rust/a/inner/Cargo.toml"), "[package]\n").unwrap();
    std::fs::write(root.join("rust/a/inner/src/lib.rs"), ONE).unwrap();
    let split = root.join("split.rs");
    std::fs::write(&split, SPLIT).unwrap();
    let to = |rel: &str| root.join(rel).display().to_string();
    let body = format!(
        "case \"$1\" in fmt) cp '{}' '{}'; cp '{}' '{}'; cp '{}' '{}';; esac; exit 0",
        split.display(),
        to("rust/a/src/lib.rs"),
        split.display(),
        to("rust/a/tests/t.rs"),
        split.display(),
        to("rust/a/inner/src/lib.rs")
    );
    let world = world_with(&root, &body);
    let done = dispatch(
        &world,
        &[
            "format".to_owned(),
            "--crate".to_owned(),
            "rust/a".to_owned(),
        ],
    );
    assert_eq!(done.code, 1, "{}{}", done.stdout, done.stderr);
    // the file is formatted all the same; its line is named, and the tests/ file the report leaves out is not
    assert_eq!(
        std::fs::read_to_string(root.join("rust/a/src/lib.rs")).unwrap(),
        SPLIT
    );
    let said = &done.stderr;
    let named = said.contains("  rust/a/src/lib.rs:5: assert_eq! message \"{a}\"\n");
    let unnamed = !said.contains("tests/t.rs") && !said.contains("inner");
    assert!(named && unnamed, "{said}");
    // run again, the pass makes nothing new: green
    let again = dispatch(
        &world,
        &[
            "format".to_owned(),
            "--crate".to_owned(),
            "rust/a".to_owned(),
        ],
    );
    assert_eq!(again.code, 0, "{}{}", again.stdout, again.stderr);
}

#[test]
fn a_file_format_names_the_line_it_made_and_its_fix() {
    let (root, ..) = two_crates();
    std::fs::write(root.join("rust/a/src/lib.rs"), ONE).unwrap();
    let world = world_with(&root, "exit 0");
    let split = root.join("split.rs");
    std::fs::write(&split, SPLIT).unwrap();
    crate::write_executable(
        &world.path_dir.join("rustfmt"),
        &format!("#!/bin/sh\ncat >/dev/null\ncat '{}'\n", split.display()),
    );
    let file = [
        "format".to_owned(),
        "--file".to_owned(),
        "rust/a/src/lib.rs".to_owned(),
    ];
    let done = dispatch(&world, &file);
    assert_eq!(done.code, 1, "{}{}", done.stdout, done.stderr);
    assert_eq!(
        std::fs::read_to_string(root.join("rust/a/src/lib.rs")).unwrap(),
        SPLIT
    );
    assert!(
        done.stderr
            .contains("  rust/a/src/lib.rs:5: assert_eq! message \"{a}\"\n"),
        "{}",
        done.stderr
    );
    assert!(done.stderr.contains(FIX), "{}", done.stderr);
}

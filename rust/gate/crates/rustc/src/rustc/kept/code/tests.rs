//! A Rust file's code: what a comment-only edit leaves the same, and what it does not.

use super::{code_text, interface_text};

#[test]
fn plain_comments_go_and_doc_comments_stay() {
    let text = "//! crate doc\n// a plain line\nfn f() {} // trailing\n/// item doc\n//// four slashes are plain\nfn g() {}\n";
    assert_eq!(
        code_text(text),
        "//! crate doc\nfn f() {}\n/// item doc\nfn g() {}\n"
    );
    // a blank line of its own stays, and the last line needs no newline
    assert_eq!(
        code_text("fn f() {}\n\nfn g() {}"),
        "fn f() {}\n\nfn g() {}"
    );
}

#[test]
fn a_comment_only_edit_leaves_the_code_the_same() {
    let before = "fn f() {\n    let x = 1; // one\n    x\n}\n";
    let after =
        "// added above\nfn f() {\n    // a new line\n    let x = 1; // one, reworded\n    x\n}\n";
    assert_eq!(code_text(before), code_text(after));
    assert_ne!(
        code_text(before),
        code_text("fn f() {\n    let x = 2;\n    x\n}\n")
    );
    assert_ne!(
        code_text(before),
        code_text("fn f() {\n\n    let x = 1;\n    x\n}\n")
    );
}

#[test]
fn block_comments_nest_and_doc_blocks_stay() {
    assert_eq!(
        code_text("a /* one /* two */ still */ b\n/* line one\nline two */\nc\n"),
        "a  b\nc\n"
    );
    assert_eq!(
        code_text("/** doc */ x\n/*! inner */ y\n/**/ z\n/*** plain */ w\n"),
        "/** doc */ x\n/*! inner */ y\n z\n w\n"
    );
    // an unclosed block runs to the end
    assert_eq!(code_text("a /* open"), "a");
}

#[test]
fn a_comment_marker_inside_a_literal_is_no_comment() {
    let text = "let s = \"a // b \\\" /* c\";\nlet r = r#\"x \" // y\"#;\nlet b = br\"// z\";\nlet q = '\"'; let e = '\\''; let l: &'a str = s; // gone\n";
    assert_eq!(
        code_text(text),
        "let s = \"a // b \\\" /* c\";\nlet r = r#\"x \" // y\"#;\nlet b = br\"// z\";\nlet q = '\"'; let e = '\\''; let l: &'a str = s;\n"
    );
    // a name ending in r, or a b or c inside a name, opens no raw string
    assert_eq!(
        code_text("bar \"s\" // x\nxbr\"q\"\n"),
        "bar \"s\"\nxbr\"q\"\n"
    );
    assert_eq!(code_text("cr\"// c string\"\n"), "cr\"// c string\"\n");
    assert_eq!(code_text("r#type // raw name\n"), "r#type\n");
    assert_eq!(code_text("let c = '/'; // slash\n"), "let c = '/';\n");
}

#[test]
fn an_unclosed_literal_runs_to_the_end() {
    assert_eq!(code_text("\"open // still"), "\"open // still");
    assert_eq!(code_text("r#\"open // still"), "r#\"open // still");
    assert_eq!(code_text("'\\u{4e00"), "'\\u{4e00");
    assert_eq!(code_text("\"\\"), "\"\\");
}

/// A private body goes; a body another crate can reach stays (T113).
#[test]
fn an_interface_keeps_what_another_crate_can_see() {
    let text = "/// doc\npub fn f(x: u8) -> u8 {\n    x + 1 // why\n}\nstruct S { f: fn(u8) -> u8 }\npub const fn c() -> u8 { 1 }\npub async fn a() { b() }\npub fn i() -> impl Copy { 1 }\nfn m() { impl S {} }\nfn n() { macro_rules! q { () => {} } }\nmacro_rules! r { () => { fn g() { 2 } } }\ntrait T { fn d(); fn e() { 3 } }\nconst K: &str = \"fn z() { }\";\nlet q = '{';\n";
    assert_eq!(
        interface_text(text),
        "/// doc\npub fn f(x: u8) -> u8 {}\nstruct S { f: fn(u8) -> u8 }\npub const fn c() -> u8 { 1 }\npub async fn a() { b() }\npub fn i() -> impl Copy { 1 }\nfn m() { impl S {} }\nfn n() { macro_rules! q { () => {} } }\nmacro_rules! r { () => { fn g() { 2 } } }\ntrait T { fn d(); fn e() {} }\nconst K: &str = \"fn z() { }\";\nlet q = '{';\n"
    );
    // a body-only edit leaves the interface the same; a signature edit does not
    assert_eq!(
        interface_text("pub fn f() { 1 }"),
        interface_text("pub fn f() { 2 }")
    );
    assert_ne!(
        interface_text("pub fn f() { 1 }"),
        interface_text("pub fn f(x: u8) { 1 }")
    );
    // a body with a char or a string holding a brace still closes where it does
    assert_eq!(
        interface_text("fn f() { let c = '}'; let s = \"}\"; let r = r\"{\"; }\nfn g() {}"),
        "fn f() {}\nfn g() {}"
    );
}

/// A text the lexer cannot read to its end keeps all its code (T113).
#[test]
fn an_unclosed_text_keeps_its_code() {
    for text in [
        "fn f() { open",
        "fn f(",
        "macro_rules! m { open",
        "macro_rules! m",
    ] {
        assert_eq!(interface_text(text), code_text(text), "{text}");
    }
}

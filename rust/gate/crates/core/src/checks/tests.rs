//! The shared text helpers: Python's line split and `repr`, the figure pattern, git's text, a scratch directory.

use super::{figure_pattern, git_text, has_ext, one_shot_pattern, py_lines, scratch};

#[test]
fn lines_end_where_python_ends_them() {
    assert_eq!(
        py_lines("a\nb\r\nc\x0cd\u{2028}e").collect::<Vec<_>>(),
        ["a", "b", "c", "d", "e"]
    );
    assert_eq!(py_lines("a\r\rb\n").collect::<Vec<_>>(), ["a", "", "b"]);
    assert_eq!(py_lines("").count(), 0);
}

#[test]
fn a_value_is_printed_as_python_prints_it() {
    use serde_json::json;
    assert_eq!(
        super::py_repr(&json!({"a": [1, null, true, false], "it's": "x'y\"z\\\n"})),
        r#"{'a': [1, None, True, False], "it's": 'x\'y"z\\\n'}"#
    );
}

#[test]
fn a_figure_an_observation_an_extension_and_git_are_read_as_the_checks_read_them() {
    assert!(figure_pattern().is_match("took 12 minutes").unwrap());
    assert!(!figure_pattern().is_match("2,179 px\u{b2}").unwrap());
    assert!(one_shot_pattern().is_match("observed 2026-11-11, method: x").unwrap());
    assert!(has_ext("a/b.rs", "rs") && !has_ext("a/b.rs", "py"));
    let dir = scratch("git-text");
    assert!(dir.is_dir());
    assert_eq!(git_text(&dir.join("none"), &["status"]), "");
}

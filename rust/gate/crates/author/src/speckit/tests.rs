use l7r_guard::shared::tempdir::TempDir;

use super::cli;

/// `speckit <verb>` on a file holding `text`: (exit, stdout).
fn run(d: &TempDir, verb: &str, text: &str) -> (i32, String) {
    let f = d.join("f.json");
    std::fs::write(&f, text).unwrap();
    let r = cli(&[verb.to_owned(), f.to_string_lossy().into_owned()]);
    (r.code, r.stdout)
}

#[test]
fn the_feature_directory_is_pythons_print_of_it() {
    let d = TempDir::new("author-speckit-fd");
    let fd = |t: &str| run(&d, "feature-dir", t);
    assert_eq!(
        fd(r#"{"feature_directory": "specs/449-x"}"#),
        (0, "specs/449-x\n".to_owned())
    );
    for none in [
        r"{}",
        r#"{"feature_directory": null}"#,
        r#"{"feature_directory": ""}"#,
        r#"{"feature_directory": 0}"#,
    ] {
        assert_eq!(fd(none), (0, "\n".to_owned()), "{none}");
    }
    assert_eq!(fd(r#"{"feature_directory": true}"#).1, "True\n");
    assert_eq!(fd(r#"{"feature_directory": [1, "a"]}"#).1, "[1, 'a']\n");
    assert_eq!(fd("[1]").0, 1, "no dict: the Python's AttributeError");
    assert_eq!(fd("not json").0, 1);
    let missing = cli(&[
        "feature-dir".to_owned(),
        d.join("none").to_string_lossy().into_owned(),
    ]);
    assert_eq!(missing.code, 1);
}

#[test]
fn the_presets_come_in_priority_order_the_disabled_left_out() {
    let d = TempDir::new("author-speckit-presets");
    let p = |t: &str| run(&d, "presets", t);
    assert_eq!(
        p(
            r#"{"presets": {"b": {"priority": 5}, "a": {}, "c": {"priority": 1, "enabled": false}, "d": {"priority": 5, "enabled": 0}, "e": 3}}"#
        ),
        (0, "b\nd\na\n".to_owned()),
        // stable on equal priorities; a non-dict counts 10 and is not printed
    );
    assert_eq!(p(r"{}"), (0, String::new()));
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": null}}}"#),
        (0, "x\n".to_owned()),
        // one item is never compared
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": null}, "y": {}}}"#).0,
        1,
        // None < int raises
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": "b"}, "y": {"priority": "a"}}}"#).1,
        "y\nx\n"
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": true}, "y": {"priority": 0.5}}}"#).1,
        "y\nx\n"
    );
    assert_eq!(p(r#"{"presets": {"x": {"priority": [1, 2]}, "y": {"priority": [1]}, "z": {"priority": [0, "a"]}}}"#).1, "z\ny\nx\n");
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": [1, {"a": 1}]}, "y": {"priority": [1, {"a": 1.0}]}}}"#)
            .1,
        "x\ny\n",
        // equal lists
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": [{}]}, "y": {"priority": [[]]}}}"#).0,
        1,
        // dict < list raises
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": [[1]]}, "y": {"priority": [[1, 2]]}}}"#).1,
        "x\ny\n"
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": [{"a": 1}, 1]}, "y": {"priority": [{"b": 1}, 0]}}}"#).0,
        1,
        // unequal dicts compare
    );
    assert_eq!(
        p(r#"{"presets": {"x": {"priority": [[1], 2]}, "y": {"priority": [[1], 1]}}}"#).1,
        "y\nx\n"
    );
    assert_eq!(p(r#"{"presets": [1]}"#).0, 1, "a list has no .items");
    assert_eq!(p(r#"{"presets": null}"#).0, 1);
    assert_eq!(p("[]").0, 1);
    assert_eq!(run(&d, "nonsense", "{}").0, 2);
    assert_eq!(cli(&[]).code, 2);
}

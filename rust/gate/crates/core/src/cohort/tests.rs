use serde_json::json;

use super::{git, int, percent, text, truthy};

#[test]
fn a_record_value_reads_as_the_python_read_it() {
    assert_eq!(int(&json!(3)), 3);
    assert_eq!(int(&json!("4")), 4);
    assert_eq!(int(&json!("x")), 0);
    let rec = json!({"a": "s", "b": 2, "c": null});
    assert_eq!(text(&rec, "a"), "s");
    assert_eq!(text(&rec, "b"), "2");
    assert_eq!(text(&rec, "c"), "None");
    assert_eq!(text(&rec, "d"), "None");
    for (v, t) in [
        (json!(null), false),
        (json!(true), true),
        (json!(0), false),
        (json!(1.5), true),
        (json!(""), false),
        (json!("x"), true),
        (json!([]), false),
        (json!([1]), true),
        (json!({}), false),
        (json!({"a": 1}), true),
    ] {
        assert_eq!(truthy(&v), t, "{v}");
    }
    assert!((percent(1, 4) - 25.0).abs() < 1e-9);
    assert!((percent(0, 0)).abs() < 1e-9);
}

#[test]
fn git_says_whether_it_ran() {
    let (ok, out) = git(std::path::Path::new("/proc/nonexistent"), &["status"]);
    assert!(!ok && out.is_empty());
    let (ok, _) = git(std::path::Path::new("."), &["--version"]);
    assert!(ok);
    let (ok, _) = git(std::path::Path::new("."), &["--no-such-flag-l7r"]);
    assert!(!ok);
}

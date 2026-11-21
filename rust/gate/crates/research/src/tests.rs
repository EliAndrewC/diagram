//! The crate's shared helpers (feature 449 T144).

use super::{digit_value, json, read, Error};

#[test]
fn an_error_prints_its_message_and_a_fault_becomes_one() {
    let e = Error::new("ValueError", "bad");
    assert_eq!(e.to_string(), "bad");
    let f: Error = l7r_shared::blocked::Fault::new("BlockedListError", "x".to_owned()).into();
    assert_eq!((f.kind, f.message.as_str()), ("BlockedListError", "x"));
    assert!(json("{").is_err());
    assert_eq!(json("[1]").unwrap(), serde_json::json!([1]));
    assert!(read(std::path::Path::new("/nonexistent/t144")).is_none());
    assert_eq!(
        [
            digit_value('7'),
            digit_value('\u{0663}'),
            digit_value('\u{1d7d8}'),
            digit_value('x')
        ],
        [Some(7), Some(3), Some(0), None]
    );
}

#[test]
fn a_path_resolves_as_python_resolves_it() {
    let d = l7r_shared::tempdir::TempDir::new("research-resolve");
    let real = std::fs::canonicalize(&d).unwrap();
    std::fs::create_dir_all(real.join("a")).unwrap();
    std::os::unix::fs::symlink(real.join("a"), real.join("link")).unwrap();
    assert_eq!(
        super::resolve(&real.join("link/./x/../y/z")),
        real.join("a/y/z")
    );
    assert_eq!(
        super::resolve(std::path::Path::new("/no/such/../path")),
        std::path::Path::new("/no/path")
    );
    assert!(super::resolve(std::path::Path::new("relative")).is_absolute());
    assert_eq!(super::resolve(&real.join("a")), real.join("a"));
}

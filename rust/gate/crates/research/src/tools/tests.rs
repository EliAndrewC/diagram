//! The commands' shared shape (feature 449 T148).

use super::{program_id, py_str, reply, said, tree_of, usage};
use crate::Error;

#[test]
fn an_uncaught_exception_prints_as_python_named_it() {
    assert_eq!(reply(Ok(said("o", "e", 3))).code, 3);
    let r = reply(Err(Error::new("KeyError", "no original stored")));
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (1, "KeyError: 'no original stored'\n")
    );
    for (kind, message, want) in [
        ("KeyError", "'b'", "'b'"),
        ("KeyError", "\"it's\"", "\"it's\""),
        ("KeyError", "'", "\"'\""),
        ("OSError", "x", "x"),
    ] {
        assert_eq!(py_str(&Error::new(kind, message)), want, "{message}");
    }
    assert_eq!(
        usage("site", "bad").stderr,
        "l7r-gate record site: error: bad\n"
    );
}

#[test]
fn the_tree_and_the_program() {
    let d = l7r_gate_core::checks::scratch("tools-tree");
    assert_eq!(tree_of(&d), d.to_path_buf());
    assert!(std::process::Command::new("git")
        .args(["init", "-q"])
        .current_dir(&*d)
        .status()
        .unwrap()
        .success());
    let sub = d.join("x");
    std::fs::create_dir_all(&sub).unwrap();
    assert_eq!(tree_of(&sub), std::fs::canonicalize(&*d).unwrap());
    assert!(program_id().contains('\0'));
}

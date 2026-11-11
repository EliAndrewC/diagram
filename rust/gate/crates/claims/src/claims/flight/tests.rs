//! A mark made, read live, gone stale, cleared; a path resolved as Python resolves it.

use std::path::Path;

use super::{clear, live, mark, now, resolved, MAX_AGE_S};
use crate::claims::tests::fixture;

#[test]
fn a_mark_is_live_until_cleared_or_stale() {
    let root = fixture("claims-flight");
    let bundle = root.join("b");
    std::fs::create_dir_all(&bundle).unwrap();
    mark(&root, &bundle).unwrap();
    let t = now();
    assert_eq!(
        live(&root, t).unwrap(),
        vec![bundle
            .canonicalize()
            .unwrap()
            .to_string_lossy()
            .into_owned()]
    );
    assert!(live(&root, t + MAX_AGE_S + 1.0).unwrap().is_empty());
    let d = root.join(".git/claims-in-flight");
    std::fs::write(d.join("bad.json"), "{").unwrap();
    std::fs::write(d.join("odd.json"), "{\"at\": 1e18, \"bundle\": 3}").unwrap();
    std::fs::write(d.join("bare.json"), "{\"at\": 1e18}").unwrap();
    std::fs::create_dir(d.join("dir.json")).unwrap();
    std::fs::write(d.join("note.txt"), "x").unwrap();
    let got = live(&root, 1e18).unwrap();
    assert_eq!(got, vec!["bare.json".to_owned(), "3".to_owned()]);
    clear(&root, &bundle);
    assert_eq!(
        live(&root, t).unwrap(),
        vec!["bare.json".to_owned(), "3".to_owned()]
    );
    std::fs::write(d.join("str.json"), "{\"at\": \" 1e18 \", \"bundle\": true}").unwrap();
    std::fs::write(d.join("tru.json"), "{\"at\": true}").unwrap();
    assert_eq!(
        live(&root, 1e18).unwrap(),
        vec!["bare.json".to_owned(), "3".to_owned(), "True".to_owned()]
    );
    std::fs::write(d.join("x.json"), "{\"at\": \"soon\"}").unwrap();
    assert!(live(&root, t).unwrap_err().starts_with("ValueError"));
    std::fs::write(d.join("x.json"), "{\"at\": null}").unwrap();
    assert!(live(&root, t).unwrap_err().starts_with("TypeError"));
    std::fs::write(d.join("x.json"), "[1]").unwrap();
    assert!(live(&root, t).unwrap_err().starts_with("AttributeError"));
    std::fs::remove_file(d.join("x.json")).unwrap();
    // a mark with no `at` reads as 0, as Python's `float(rec.get("at", 0))` does: live at time 0
    std::fs::write(d.join("noat.json"), "{}").unwrap();
    assert!(live(&root, 0.0).unwrap().contains(&"noat.json".to_owned()));
    std::fs::remove_file(d.join("noat.json")).unwrap();
    let outside = crate::checks::scratch("claims-flight-plain");
    assert_eq!(live(&outside, t).unwrap(), Vec::<String>::new());
    assert!(mark(Path::new("/proc/no/such"), &bundle).is_err());
    assert_eq!(
        resolved(&root.join("b/../b/./x/y")),
        bundle.canonicalize().unwrap().join("x/y")
    );
    assert_eq!(resolved(Path::new("/")), Path::new("/"));
}

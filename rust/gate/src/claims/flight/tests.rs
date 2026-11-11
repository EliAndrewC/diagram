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
        live(&root, t),
        vec![bundle
            .canonicalize()
            .unwrap()
            .to_string_lossy()
            .into_owned()]
    );
    assert!(live(&root, t + MAX_AGE_S + 1.0).is_empty());
    let d = root.join(".git/claims-in-flight");
    std::fs::write(d.join("bad.json"), "{").unwrap();
    std::fs::write(d.join("odd.json"), "{\"at\": 1e18, \"bundle\": 3}").unwrap();
    std::fs::write(d.join("bare.json"), "{\"at\": 1e18}").unwrap();
    std::fs::create_dir(d.join("dir.json")).unwrap();
    std::fs::write(d.join("note.txt"), "x").unwrap();
    let got = live(&root, 1e18);
    assert_eq!(got, vec!["bare.json".to_owned(), "3".to_owned()]);
    clear(&root, &bundle);
    assert_eq!(live(&root, t), vec!["bare.json".to_owned(), "3".to_owned()]);
    let outside = crate::checks::scratch("claims-flight-plain");
    assert_eq!(live(&outside, t), Vec::<String>::new());
    assert!(mark(Path::new("/proc/no/such"), &bundle).is_err());
    assert_eq!(
        resolved(&root.join("b/../b/./x/y")),
        bundle.canonicalize().unwrap().join("x/y")
    );
    assert_eq!(resolved(Path::new("/")), Path::new("/"));
}

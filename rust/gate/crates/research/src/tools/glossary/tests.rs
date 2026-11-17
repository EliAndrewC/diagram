//! `record glossary` (feature 449 T148): each answer `glossary_asset.py`'s on the same tree.

use super::{check, run};
use crate::fixture::{put, tree};

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_glossary_is_checked_assembled_and_written() {
    let t = tree();
    let r = check(&t).unwrap();
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (0, "glossary: in sync (2 terms)\n")
    );
    let r = run(&[], &t, &t).unwrap();
    assert_eq!(
        r.stdout,
        "glossary: assembled (2 terms) - `make record` derives the site's script from it\n"
    );
    let r = run(&args(&["--path", "g.js"]), &t, &t).unwrap();
    assert_eq!(r.stdout, "wrote g.js (2 terms)\n");
    assert!(std::fs::read_to_string(t.join("g.js"))
        .unwrap()
        .starts_with("// DERIVED FILE"));
    put(
        &t,
        "l7r/diagram/interactive/assets/glossary/0030-dike.json",
        "{\n \"term\": \"dike\",\n \"def\": \"A wall.\",\n \"variants\": [\n  \"dike\"\n ]\n}\n",
    );
    let r = check(&t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "glossary.json: STALE against its per-term files - run `make glossary` (assets/glossary.json, ../../../research/assets/glossary-variants.txt)\n"));
    let r = run(&[], &t, &t).unwrap();
    assert_eq!(
        r.stdout,
        "glossary: assembled (3 terms) - `make record` derives the site's script from it\n"
    );
    assert_eq!(check(&t).unwrap().code, 0);
    let r = run(&args(&["--split"]), &t, &t).unwrap();
    assert_eq!(
        r.stdout,
        "glossary: split into 3 term file(s); they assemble back to the same bytes\n"
    );
    assert_eq!(run(&args(&["--bogus"]), &t, &t).unwrap().code, 2);
    assert_eq!(
        run(&args(&["--path", "no/such/dir/g.js"]), &t, &t)
            .unwrap_err()
            .kind,
        "OSError"
    );
    put(
        &t,
        "l7r/diagram/interactive/assets/glossary/README",
        "stray",
    );
    assert_eq!(check(&t).unwrap_err().kind, "GlossaryError");
    put(&t, "l7r/diagram/interactive/assets/glossary.json", "{bad");
    assert_eq!(check(&t).unwrap_err().kind, "JSONDecodeError");
}

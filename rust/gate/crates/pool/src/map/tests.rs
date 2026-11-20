//! `make map`'s command (feature 449 T221): a map named by its folder, a file in it or its name; its line; a failure's exit.
//!
//! Research: the map command's tests - NONE: fixtures and assertions, deciding nothing about a map

use super::{cli, resolve, USAGE};
use crate::cache::tests::fixture;
use crate::walk::walk;

/// A folder (with or without its root, a trailing slash), a file in it and a bare name each name the map; anything else is refused with
/// the forms.
#[test]
fn a_map_is_named_by_its_folder_a_file_in_it_or_its_name() {
    let f = fixture("map-resolve");
    let w = walk(&f.root);
    for target in [
        "pool/magistracies/s".to_owned(),
        "pool/magistracies/s/".to_owned(),
        "pool/magistracies/s/s.svg".to_owned(),
        "s".to_owned(),
        f.root
            .join("pool/magistracies/s")
            .to_string_lossy()
            .into_owned(),
    ] {
        assert_eq!(
            resolve(&f.root, &w, &target).unwrap().rel(),
            "pool/magistracies/s"
        );
    }
    let err = resolve(&f.root, &w, "pool/nowhere/x").unwrap_err();
    assert!(err.contains("MAP=pool/<tier>/<map>"), "{err}");
}

/// The command draws, then serves, each map and says so; a frozen exhibit is FROZEN; an unclassified folder, a name no map bears, a
/// failed map and the cache unwritable each exit 1; no target or a flag is the usage.
#[test]
fn the_command_says_each_maps_verdict() {
    let mut f = fixture("map-cli");
    let opts = f.opts();
    let (out, err, code) = cli(&f.root, &["s", "v"], &mut f.stand, opts.clone());
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert!(out.starts_with("REGENERATED  pool/magistracies/s - no cache entry\nFROZEN       legacy-hand-authored-pool/villages/v - a frozen"), "{out}");
    let (out, _, code) = cli(&f.root, &["--all"], &mut f.stand, opts.clone());
    assert_eq!(code, 0);
    assert!(
        out.contains("CACHED       pool/magistracies/s\n")
            && out.contains("REGENERATED  pool/hamlets/h")
    );
    f.mode(&format!(
        "touch:{}",
        f.root.join("assets/page.css").display()
    ));
    std::fs::remove_dir_all(f.root.join(".gencache")).unwrap();
    let (out, _, _) = cli(&f.root, &["t"], &mut f.stand, opts.clone());
    assert!(out.contains("changed while its engine ran"), "{out}");
    f.mode("refuse");
    let (_, err, code) = cli(&f.root, &["t"], &mut f.stand, opts.clone());
    assert_eq!(code, 1);
    assert!(err.contains("ValueError: no\nmake map: pool/magistracies/t: its engine refused it"));
    let (_, err, code) = cli(&f.root, &["u"], &mut f.stand, opts.clone());
    assert!(code == 1 && err.contains("holds no map the pool walk can classify"));
    let (_, err, code) = cli(&f.root, &["zz"], &mut f.stand, opts.clone());
    assert!(code == 1 && err.contains("no pool map is named zz"));
    for bad in [&[][..], &["--x"]] {
        assert_eq!(
            cli(&f.root, bad, &mut f.stand, opts.clone()),
            (String::new(), USAGE.to_owned(), 2)
        );
    }
    std::fs::remove_dir_all(f.root.join(".gencache")).unwrap();
    crate::walk::tests::put(&f.root, ".gencache", "a file");
    let (_, err, code) = cli(&f.root, &["s"], &mut f.stand, opts);
    assert!(code == 1 && err.contains("make map: the generation cache: "));
}

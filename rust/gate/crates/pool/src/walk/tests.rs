use std::path::Path;

use super::{walk, Kind, Walk, DECLARATION, LEGACY, LIVE};

pub(crate) fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// The declaration a fixture tree carries: two tiers, and an object with none.
pub(crate) const TYPES: &str =
    r#"[{"tier": "magistracies"}, {"tier": "country-shrines"}, {"title": "no tier"}]"#;

/// A tree holding one folder of every kind and every way a folder is reported.
pub(crate) fn fixture(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = l7r_shared::tempdir::TempDir::new(&format!("pool-walk-{tag}"));
    put(&root, DECLARATION, TYPES);
    for rel in [
        "pool/CLAUDE.md",
        "pool/hamlets/a/a.spec.json",
        "pool/hamlets/a/a.json",
        "pool/hamlets/a/a.driver.svg",
        "pool/hamlets/a/a.notes.md",
        "pool/hamlets/old/old.json",
        "pool/magistracies/c/c.compound.json",
        "pool/magistracies/c/c.svg",
        "pool/magistracies/c/c.gen.py",
        "pool/magistracies/h/h.svg",
        "pool/magistracies/h/h.html",
        "pool/magistracies/h/h.png",
        "pool/magistracies/stray.txt",
        "pool/towns/u/u.svg",
        "legacy-hand-authored-pool/villages/v/v.json",
        "legacy-hand-authored-pool/villages/v/v.notes.md",
        "legacy-hand-authored-pool/villages/v/sub/CLAUDE.md",
        "legacy-hand-authored-pool/villages/w/w.svg",
    ] {
        put(&root, rel, "x");
    }
    root
}

fn kinds(w: &Walk) -> Vec<(String, Kind)> {
    w.maps.iter().map(|m| (m.rel(), m.kind)).collect()
}

/// Each folder is classified once by the precedence: a spec, then a program, then an svg in a declared tier, then (legacy only) a
/// manifest; anything else is reported with the fix, never guessed at.
#[test]
fn every_folder_is_classified_by_precedence_and_the_rest_reported() {
    let root = fixture("kinds");
    let w = walk(&root);
    assert_eq!(
        kinds(&w),
        [
            ("pool/hamlets/a".to_owned(), Kind::Hamlet),
            ("pool/hamlets/old".to_owned(), Kind::Report),
            ("pool/magistracies/c".to_owned(), Kind::Compound),
            ("pool/magistracies/h".to_owned(), Kind::HandSheet),
            ("pool/towns/u".to_owned(), Kind::Report),
            (
                "legacy-hand-authored-pool/villages/v".to_owned(),
                Kind::Frozen
            ),
            (
                "legacy-hand-authored-pool/villages/w".to_owned(),
                Kind::Report
            ),
        ]
    );
    assert_eq!(
        w.tiers.iter().map(String::as_str).collect::<Vec<_>>(),
        ["country-shrines", "magistracies"]
    );
    assert_eq!(w.reports.len(), 3);
    assert!(w.reports[0].starts_with("pool/hamlets/old: no old.spec.json (a hamlet)"));
    assert!(w.reports[0].contains("this tier is not declared"));
    assert!(
        w.reports[1].contains("pool/towns/u") && w.reports[1].contains("move it out of the pool")
    );
    assert!(w.reports[2].starts_with("legacy-hand-authored-pool/villages/w:"));
    let tags: Vec<&str> = [
        Kind::Hamlet,
        Kind::Compound,
        Kind::HandSheet,
        Kind::Frozen,
        Kind::Report,
    ]
    .iter()
    .map(|k| k.tag())
    .collect();
    assert_eq!(
        tags,
        ["hamlet", "compound", "hand-sheet", "frozen", "unclassified"]
    );
    assert!(Kind::Hamlet.is_live() && !Kind::Frozen.is_live() && !Kind::Report.is_live());
    assert!(Kind::Compound.is_sheet() && Kind::HandSheet.is_sheet() && !Kind::Hamlet.is_sheet());
}

/// A consumer asks the walk's listing, by name and suffix, and finds a folder by its name, the live pool first.
#[test]
fn a_folder_is_found_by_name_and_its_files_asked_of_its_listing() {
    let root = fixture("find");
    put(&root, "legacy-hand-authored-pool/villages/h/h.json", "x");
    let w = walk(&root);
    let h = w.folder("h").unwrap();
    assert_eq!((h.tree, h.tier.as_str()), (LIVE, "magistracies"));
    assert!(h.has(".html") && h.has(".svg") && !h.has(".json") && !h.has(".gen.py"));
    assert_eq!(h.file(".svg"), root.join("pool/magistracies/h/h.svg"));
    assert_eq!(h.files, ["h.html", "h.png", "h.svg"]);
    assert!(w.folder("nowhere").is_none());
    assert_eq!(w.in_tree(LEGACY).count(), 3);
    assert_eq!(w.in_tree(LIVE).count(), 5);
}

/// No declaration, or one that is not a list, declares no tier and is reported: an svg is then told no hand sheet. A tree that is not
/// there holds no maps.
#[test]
fn a_missing_or_unreadable_declaration_declares_no_tier_and_says_so() {
    let root = fixture("decl");
    std::fs::remove_file(root.join(DECLARATION)).unwrap();
    std::fs::remove_dir_all(root.join(LEGACY)).unwrap();
    let w = walk(&root);
    assert!(w.tiers.is_empty());
    assert!(w.reports[0].starts_with("l7r/diagram/buildings/types.json: not readable"));
    assert_eq!(w.folder("h").unwrap().kind, Kind::Report);
    assert_eq!(w.in_tree(LEGACY).count(), 0);
    put(&root, DECLARATION, "{\"tier\": \"magistracies\"}");
    let w = walk(&root);
    assert!(w.reports[0].contains("not a JSON list of building types"));
    assert_eq!(w.folder("h").unwrap().kind, Kind::Report);
}

/// A tier or a folder reached through a link is walked as a directory; a link to a file is an entry and no folder.
#[test]
fn a_linked_directory_is_walked_and_a_linked_file_is_not_a_folder() {
    let root = fixture("links");
    let away = root.join("away");
    put(&root, "away/z/z.spec.json", "x");
    std::os::unix::fs::symlink(&away, root.join("pool/elsewhere")).unwrap();
    std::os::unix::fs::symlink(root.join("pool/CLAUDE.md"), root.join("pool/hamlets/note"))
        .unwrap();
    let w = walk(&root);
    let z = w.folder("z").unwrap();
    assert_eq!((z.tier.as_str(), z.kind), ("elsewhere", Kind::Hamlet));
    assert!(w.folder("note").is_none());
    assert_eq!(z.dir, root.join("pool/elsewhere/z"));
}

/// The counted work on the fixture is exactly the derivation's terms: one listing a root, tier and folder; each name read once from
/// its listing; each folder entry matched once; one kind a folder; one lookup a tier; the declaration read once and parsed by the block,
/// charged to the live pool; and no git index asked.
#[cfg(feature = "counters")]
#[test]
fn the_walk_counts_the_derivations_terms_and_no_more() {
    let root = fixture("counts");
    put(&root, "pool/index.html", "x");
    let w = walk(&root);
    let blocks = TYPES.len().div_ceil(64) as u64;
    // the walk's kinds; the cache's (T221) are none of the walk's work
    let walked = [
        "dir_list",
        "dir_entry",
        "classify",
        "folder_kind",
        "tier_lookup",
        "tracked_lookup",
        "file_read",
        "parse_block",
        "index_row",
    ];
    for tree in [LIVE, LEGACY] {
        assert!(w
            .counts
            .of(tree)
            .iter()
            .all(|(k, n)| walked.contains(k) || *n == 0));
    }
    let of = |tree: &str| -> Vec<(&str, u64)> {
        w.counts
            .of(tree)
            .into_iter()
            .filter(|(k, _)| walked.contains(k))
            .collect()
    };
    assert_eq!(
        of(LIVE),
        [
            ("dir_list", 9),
            ("dir_entry", 23),
            ("classify", 12),
            ("folder_kind", 5),
            ("tier_lookup", 3),
            ("tracked_lookup", 0),
            ("file_read", 1),
            ("parse_block", blocks),
            ("index_row", 0),
        ]
    );
    assert_eq!(
        of(LEGACY),
        [
            ("dir_list", 4),
            ("dir_entry", 7),
            ("classify", 4),
            ("folder_kind", 2),
            ("tier_lookup", 1),
            ("tracked_lookup", 0),
            ("file_read", 0),
            ("parse_block", 0),
            ("index_row", 0),
        ]
    );
}

/// THE REAL POOL: every map folder of both trees is walked and classified - every live folder a hamlet, a generated compound or a hand
/// sheet, every legacy folder a frozen exhibit - and nothing is reported. Thirty maps on 2026-11-19 (5 hamlets, 2 compounds, 4 hand
/// sheets, 19 exhibits: the derivation's Bounds), where the index the walk replaces listed six.
#[test]
fn the_real_pool_is_walked_whole_and_nothing_in_it_is_unclassified() {
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let w = walk(&tree);
    assert_eq!(w.reports, Vec::<String>::new());
    // every folder two levels under each tree, listed here on its own
    let mut folders = 0;
    for t in super::TREES {
        for tier in std::fs::read_dir(tree.join(t)).unwrap().flatten() {
            if tier.path().is_dir() {
                folders += std::fs::read_dir(tier.path())
                    .unwrap()
                    .flatten()
                    .filter(|f| f.path().is_dir())
                    .count();
            }
        }
    }
    assert_eq!(w.maps.len(), folders);
    assert!(w.maps.len() >= 30);
    assert!(w.in_tree(LIVE).all(|m| m.kind.is_live()));
    assert!(w.in_tree(LEGACY).all(|m| m.kind == Kind::Frozen));
    for kind in [Kind::Hamlet, Kind::Compound, Kind::HandSheet] {
        assert_eq!((kind, w.maps.iter().any(|m| m.kind == kind)), (kind, true));
    }
}

/// A directory there but not listable is reported with its error's kind, and its maps left out; a tree not there is no report.
#[test]
fn a_directory_that_cannot_be_listed_is_reported() {
    use std::os::unix::fs::PermissionsExt as _;
    let root = fixture("unlisted");
    let tier = root.join("pool/magistracies");
    std::fs::set_permissions(&tier, std::fs::Permissions::from_mode(0o000)).unwrap();
    let w = walk(&root);
    std::fs::set_permissions(&tier, std::fs::Permissions::from_mode(0o755)).unwrap();
    assert_eq!(w.unlisted.len(), 1);
    assert_eq!(
        (w.unlisted[0].dir.clone(), w.unlisted[0].kind),
        (tier.clone(), std::io::ErrorKind::PermissionDenied)
    );
    assert!(w.unlisted[0].message.contains("ermission denied"));
    assert_eq!(w.unlisted[0].code, 13);
    assert!(w
        .reports
        .iter()
        .any(|r| r.ends_with("its maps are left out of this walk")));
    assert!(w.folder("h").is_none());
}

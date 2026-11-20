use super::cli;
use crate::walk::tests::{fixture, put};

fn run(root: &std::path::Path, words: &[&str]) -> super::Said {
    let args: Vec<String> = words.iter().map(|w| (*w).to_owned()).collect();
    cli(&args, root)
}

/// `index` writes the page, then finds it unchanged; what the walk could not classify goes to stderr; a page that cannot be written
/// exits 1 with the fix.
#[test]
fn index_writes_then_leaves_the_page_and_says_what_it_could_not_classify() {
    let root = fixture("cli-index");
    let (out, err, code) = run(&root, &["index"]);
    assert_eq!(
        (out.as_str(), code),
        ("pool index: pool/index.html written (7 maps)\n", 0)
    );
    assert_eq!(err.lines().count(), 3);
    assert!(err.starts_with("pool walk: pool/hamlets/old: no old.spec.json"));
    assert_eq!(
        run(&root, &["index"]).0,
        "pool index: pool/index.html unchanged (7 maps)\n"
    );
    put(&root, "pool/index.html.d/x", "x");
    std::fs::remove_file(root.join("pool/index.html")).unwrap();
    std::fs::rename(root.join("pool/index.html.d"), root.join("pool/index.html")).unwrap();
    let (out, err, code) = run(&root, &["index"]);
    assert_eq!((out.as_str(), code), ("", 1));
    assert!(
        err.contains("pool index: pool/index.html could not be written: ")
            && err.contains("from the repository's root")
    );
}

/// `find` names a map's kind and folder, or its file where the listing holds it; none is exit 1.
#[test]
fn find_names_a_maps_kind_folder_and_files() {
    let root = fixture("cli-find");
    assert_eq!(
        run(&root, &["find", "a"]),
        ("hamlet\tpool/hamlets/a\n".to_owned(), String::new(), 0)
    );
    assert_eq!(
        run(&root, &["find", "c", ".gen.py"]).0,
        "pool/magistracies/c/c.gen.py\n"
    );
    let (_, err, code) = run(&root, &["find", "h", ".gen.py"]);
    assert_eq!(
        (err.as_str(), code),
        ("pool find: pool/magistracies/h holds no h.gen.py\n", 1)
    );
    let (_, err, code) = run(&root, &["find", "zz"]);
    assert_eq!(
        (err.as_str(), code),
        ("pool find: no map folder named zz in either pool tree\n", 1)
    );
}

/// `list` prints every folder with its kind; anything else is the usage, exit 2.
#[test]
fn list_prints_every_folder_and_a_wrong_word_the_usage() {
    let root = fixture("cli-list");
    let (out, err, code) = run(&root, &["list"]);
    assert_eq!(code, 0);
    assert_eq!(out.lines().count(), 7);
    assert!(out.starts_with("pool\thamlets\ta\thamlet\n"));
    assert!(out.contains("legacy-hand-authored-pool\tvillages\tv\tfrozen\n"));
    assert_eq!(err.lines().count(), 3);
    let (_, err, code) = run(&root, &["nonsense"]);
    assert_eq!((err.starts_with("usage: pool index"), code), (true, 2));
}

/// `counts <tree>` (a counting build): the tree's counted work as one JSON line, the index composed but not written.
#[cfg(feature = "counters")]
#[test]
fn counts_prints_a_trees_work_and_writes_nothing() {
    let root = fixture("cli-counts");
    let (out, _, code) = run(&root, &["counts", "legacy-hand-authored-pool"]);
    assert_eq!(code, 0);
    let line: serde_json::Value = serde_json::from_str(out.trim()).unwrap();
    // 4 listings, 7 names, 4 entries matched, 2 kinds, 1 tier, 2 rows
    assert_eq!(line["total"], 20);
    assert_eq!(line["index_row"], 2);
    assert_eq!(line["tree"], "legacy-hand-authored-pool");
    assert!(!root.join("pool/index.html").exists());
    let (_, err, code) = run(&root, &["counts", "nowhere"]);
    assert_eq!(code, 2);
    assert!(err.contains("no tree nowhere"));
}

/// `map` with a name no map bears refuses before any engine is asked; the review gate's question answers no for a map with no cache,
/// a frozen exhibit and a name no map bears (feature 449 T221).
#[test]
fn map_refuses_an_unknown_name_and_is_current_answers_no_without_a_cache() {
    let root = fixture("cli-map");
    let (_, err, code) = run(&root, &["map", "zz"]);
    assert!(code == 1 && err.contains("no pool map is named zz"));
    for target in ["a", "v", "zz"] {
        assert!(!super::is_current(&root, target), "{target}");
    }
}

/// `counts pool` (a counting build): the second of two runs back to back, every map served - the derivation's all-hit run, nothing hashed;
/// a map the second run did not serve is named; a cache that cannot be written is the error.
#[cfg(feature = "counters")]
#[test]
fn counts_on_the_pool_are_the_second_runs_and_name_what_it_did_not_serve() {
    let mut f = crate::cache::tests::fixture("cli-counts-pool");
    let (out, err, code) = super::counts_cli(&f.root, "pool", &mut f.stand);
    assert_eq!((code, err.as_str()), (0, ""));
    let line: serde_json::Value = serde_json::from_str(out.trim()).unwrap();
    // nothing hashed but the stand-in engines, scripts with no build-id note, each whole once a run
    let script_blocks: u64 = ["engines/mode-a", "engines/hamlet"]
        .iter()
        .map(|e| {
            std::fs::metadata(f.root.join(e))
                .unwrap()
                .len()
                .div_ceil(64)
        })
        .sum();
    assert_eq!(
        (line["hash_block"].as_u64(), line["engine_run"].as_u64()),
        (Some(script_blocks), Some(0))
    );
    assert!(line["total"].as_u64().unwrap() > 0);
    f.mode("refuse");
    std::fs::remove_dir_all(f.root.join(".gencache")).unwrap();
    let (_, err, _) = super::counts_cli(&f.root, "pool", &mut f.stand);
    assert!(err.contains("did not serve pool/hamlets/h"), "{err}");
    std::fs::remove_dir_all(f.root.join(".gencache")).unwrap();
    crate::walk::tests::put(&f.root, ".gencache", "a file");
    let (_, err, code) = super::counts_cli(&f.root, "pool", &mut f.stand);
    assert!(
        code == 1 && err.starts_with("pool counts: the generation cache: "),
        "{err}"
    );
}

//! The source vocabulary derived into the contract (feature 449 T148): each answer `source_tags_contract.py`'s on the same tree.

use super::run;
use crate::fixture::{put, tree};

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_block_is_checked_and_rewritten() {
    let t = tree();
    let contract = t.join(super::CONTRACT);
    let r = run(&args(&["--check"]), &t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "source-tags-contract: the contract's vocabulary block is stale - run make source-tags-contract\n"));
    let r = run(&[], &t).unwrap();
    assert_eq!(
        r.stdout,
        format!(
            "source-tags-contract: rewrote the vocabulary block in {}\n",
            contract.display()
        )
    );
    assert!(std::fs::read_to_string(&contract)
        .unwrap()
        .contains("- `kind=web` - **Web <page>**: online\n"));
    let r = run(&args(&["--check"]), &t).unwrap();
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (
            0,
            "source-tags-contract: the contract's vocabulary block is current\n"
        )
    );
    put(&t, "other.md", "no markers\n");
    let r = run(
        &args(&["--contract", "other.md", "--research-dir", "research"]),
        &t,
    );
    // a relative path is read from the working directory, as Python's `open` reads it
    assert_eq!(r.unwrap_err().kind, "OSError");
    let other = t.join("other.md").display().to_string();
    let r = run(&args(&["--contract", &other]), &t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "source-tags-contract: the contract has no derived source-tags block - its two markers are missing\n"));
    put(&t, "research/source-tags.json", "{\"period\": []}");
    let r = run(&[], &t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "source-tags-contract: source-tags.json: holds exactly period, region, kind and canon\n"));
    std::fs::write(t.join("research/source-tags.json"), [0xff]).unwrap();
    assert_eq!(run(&[], &t).unwrap_err().kind, "UnicodeDecodeError");
    assert_eq!(run(&args(&["--bogus"]), &t).unwrap().code, 2);
}

#[test]
fn a_contract_it_cannot_write_is_the_pythons_uncaught_error() {
    let t = tree();
    std::fs::remove_file(t.join(super::CONTRACT)).unwrap();
    std::fs::create_dir_all(t.join(super::CONTRACT)).unwrap();
    assert_eq!(run(&[], &t).unwrap_err().kind, "OSError");
    std::fs::remove_dir_all(t.join(super::CONTRACT)).unwrap();
    let path = t.join(super::CONTRACT);
    put(&t, super::CONTRACT, "<!-- source-tags: DERIVED by make source-tags-contract from research/source-tags.json - edit the vocabulary, never here -->\n<!-- /source-tags -->\n");
    let mut perms = std::fs::metadata(&path).unwrap().permissions();
    std::os::unix::fs::PermissionsExt::set_mode(&mut perms, 0o444);
    std::fs::set_permissions(&path, perms).unwrap();
    assert_eq!(run(&[], &t).unwrap_err().kind, "OSError");
}

//! The world's checkout (feature 449 T169): a sparse clone at a revision, or at the working tree, made by the runner.

use std::collections::BTreeMap;
use std::path::Path;
use std::time::Duration;

use serde_json::json;

use super::Fx;
use crate::cases::load;
use crate::cases::{Checkout, Worlds};
use crate::checkout::{in_cone, make};
use crate::keys::{keys, Hasher};
use crate::runner::Opts;

fn git(repo: &Path, args: &[&str]) -> String {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(repo)
        .args([
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "commit.gpgsign=false",
        ])
        .args(args)
        .output()
        .unwrap();
    assert!(
        out.status.success(),
        "{}",
        String::from_utf8_lossy(&out.stderr)
    );
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

/// A repository of a root file and four directories, committed, with its working tree changed in and out of the cone `a`, `c/sub`.
pub(super) fn repo(fx: &Fx) -> (std::path::PathBuf, String) {
    for (name, text) in [
        ("repo/top.txt", "top\n"),
        ("repo/a/x.txt", "x\n"),
        ("repo/a/deep/y.txt", "y\n"),
        ("repo/a/d/inner.txt", "i\n"),
        ("repo/b/z.txt", "z\n"),
        ("repo/c/f.txt", "f\n"),
        ("repo/c/sub/w.txt", "w\n"),
        ("repo/c/other/v.txt", "v\n"),
    ] {
        fx.write(name, text);
    }
    let repo = fx.root().join("repo");
    git(&repo, &["init", "-q"]);
    git(&repo, &["add", "."]);
    git(&repo, &["commit", "-qm", "one"]);
    let sha = git(&repo, &["rev-parse", "HEAD"]);
    // in the cone: a change, a deletion, an untracked file and link; outside it: a change and an untracked file
    fx.write("repo/a/x.txt", "x changed\n");
    std::fs::remove_file(repo.join("a/deep/y.txt")).unwrap();
    fx.write("repo/a/new.txt", "new\n");
    std::os::unix::fs::symlink("x.txt", repo.join("a/link")).unwrap();
    // a directory of HEAD that the working tree holds as a file
    std::fs::remove_dir_all(repo.join("a/d")).unwrap();
    fx.write("repo/a/d", "now a file\n");
    fx.write("repo/b/z.txt", "z changed\n");
    fx.write("repo/b/out.txt", "out\n");
    (repo, sha)
}

fn files(dir: &Path) -> Vec<String> {
    let mut out = Vec::new();
    let mut stack = vec![dir.to_path_buf()];
    while let Some(d) = stack.pop() {
        for e in std::fs::read_dir(&d).unwrap().flatten() {
            let p = e.path();
            if e.file_name() == ".git" {
                continue;
            }
            if p.is_dir() && !p.is_symlink() {
                stack.push(p);
            } else {
                out.push(p.strip_prefix(dir).unwrap().display().to_string());
            }
        }
    }
    out.sort();
    out
}

#[test]
fn a_sparse_world_holds_its_cone_at_a_revision_or_at_the_working_tree() {
    let fx = Fx::new();
    let (_repo, sha) = repo(&fx);
    let env: Vec<(String, String)> = std::env::vars().collect();
    let vars = BTreeMap::from([("R".to_owned(), "repo".to_owned())]);
    let co = |rev: &str| Checkout {
        repo: "{R}".to_owned(),
        rev: rev.to_owned(),
        into: "c".to_owned(),
        sparse: vec!["a".to_owned(), "c/sub".to_owned()],
    };
    let at = |rev: &str, world: &str| {
        let world = fx.root().join(world);
        std::fs::create_dir_all(&world).unwrap();
        make(
            &co(rev),
            (fx.root(), &world),
            &vars,
            (&env, Duration::from_secs(10), Worlds::Sparse),
        )
        .map(|()| world.join("c"))
    };
    let old = at(&sha, "w-old").unwrap();
    // the cone: each named directory whole, and the files directly in the root and in a named directory's ancestor
    assert_eq!(
        files(&old),
        [
            "a/d/inner.txt",
            "a/deep/y.txt",
            "a/x.txt",
            "c/f.txt",
            "c/sub/w.txt",
            "top.txt"
        ]
    );
    let new = at("WORKTREE", "w-new").unwrap();
    assert_eq!(
        files(&new),
        [
            "a/d",
            "a/link",
            "a/new.txt",
            "a/x.txt",
            "c/f.txt",
            "c/sub/w.txt",
            "top.txt"
        ]
    );
    assert_eq!(
        std::fs::read_to_string(new.join("a/d")).unwrap(),
        "now a file\n"
    );
    assert_eq!(
        std::fs::read_to_string(new.join("a/x.txt")).unwrap(),
        "x changed\n"
    );
    assert_eq!(
        std::fs::read_link(new.join("a/link")).unwrap(),
        Path::new("x.txt")
    );
    let err = at("no-such-rev", "w-bad").unwrap_err();
    assert!(
        err.starts_with("world.checkout: `git -C ")
            && err.contains("checkout -q no-such-rev` exited"),
        "{err}"
    );
    // a working-tree file the checkout cannot copy is the world's failure, named
    let secret = fx.root().join("repo/a/secret.txt");
    fx.write("repo/a/secret.txt", "s\n");
    std::fs::set_permissions(&secret, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    let err = at("WORKTREE", "w-unreadable").unwrap_err();
    assert!(
        err.starts_with("world.checkout: the working tree's a/secret.txt: "),
        "{err}"
    );
    std::fs::remove_file(&secret).unwrap();
    // no cone named: the whole tree
    let whole = Checkout {
        sparse: Vec::new(),
        ..co(&sha)
    };
    let world = fx.root().join("w-whole");
    std::fs::create_dir_all(&world).unwrap();
    make(
        &whole,
        (fx.root(), &world),
        &vars,
        (&env, Duration::from_secs(10), Worlds::Sparse),
    )
    .unwrap();
    assert_eq!(files(&world.join("c")).len(), 8);
}

#[test]
fn the_cone_is_git_s() {
    let cone = ["a".to_owned(), "c/sub".to_owned()];
    for (rel, inside) in [
        ("top.txt", true),
        ("a/x.txt", true),
        ("a/deep/y.txt", true),
        ("c/f.txt", true),
        ("c/sub/w.txt", true),
        ("c/other/v.txt", false),
        ("b/z.txt", false),
        ("ab/x.txt", false),
    ] {
        assert_eq!(in_cone(rel, &cone), inside, "{rel}");
    }
    assert!(in_cone("b/z.txt", &[]));
}

#[test]
fn a_checkout_needs_no_setup_and_moves_both_keys() {
    let fx = Fx::new();
    let (_repo, sha) = repo(&fx);
    let mut v = Fx::base(&json!([{"name": "ls", "steps": [["sh", "-c", "cat a/x.txt; ls a"]]}]));
    v["world"] = json!({
        "checkout": {"repo": "repo", "rev": "{REV}", "into": "c", "sparse": ["a/"]},
        "cwd": "{WORLD}/c", "files": ["c/a"], "ignore": [".git"]
    });
    v["sides"]["old"]["vars"] = json!({"REV": sha});
    v["sides"]["new"]["vars"] = json!({"REV": "WORKTREE"});
    let (r, report) = fx.run(&v, &[]);
    assert_eq!(
        r.code, 1,
        "the working tree differs from the revision: {}",
        r.stdout
    );
    assert_eq!(report["differing"], json!(["ls"]));
    assert!(r.stdout.contains("x changed"), "{}", r.stdout);
    // the declaration is the world's, so a narrower cone moves both keys (read here, not by a second run: two worlds fewer, feature 449
    // T169's FR-008 measure)
    let keys_of = |v: &serde_json::Value, worlds: Worlds| {
        let cases = load(&fx.cases_file(v)).unwrap();
        keys(&cases, &cases.cases[0], &mut Hasher::default(), worlds).unwrap()
    };
    let wide = keys_of(&v, Worlds::Sparse);
    let whole = keys_of(&v, Worlds::Whole);
    v["world"]["checkout"]["sparse"] = json!(["a/deep"]);
    let narrow = keys_of(&v, Worlds::Sparse);
    assert!(wide.0 != narrow.0 && wide.1 != narrow.1);
    // no side kept from a sparse world keys a whole one, and a whole world's key does not read the list it ignores
    assert!(whole.0 != wide.0 && whole.1 != wide.1);
    assert_eq!(keys_of(&v, Worlds::Whole), whole);
    // a verify and an `--all` build whole worlds; the runs that iterate build sparse ones, and a file with no list builds whole
    let cases = load(&fx.cases_file(&v)).unwrap();
    let worlds = |o: Opts| o.worlds(&cases);
    assert_eq!(
        worlds(Opts {
            verify: true,
            ..Opts::default()
        }),
        Worlds::Whole
    );
    assert_eq!(
        worlds(Opts {
            all: true,
            ..Opts::default()
        }),
        Worlds::Whole
    );
    assert_eq!(
        worlds(Opts {
            twice: true,
            ..Opts::default()
        }),
        Worlds::Sparse
    );
    assert_eq!(worlds(Opts::default()), Worlds::Sparse);
    v["world"]["checkout"]["sparse"] = json!([]);
    let unsparse = load(&fx.cases_file(&v)).unwrap();
    assert_eq!(Opts::default().worlds(&unsparse), Worlds::Whole);
    for (why, value) in [
        ("world.checkout: an object", json!("x")),
        (
            "world.checkout.repo: a string",
            json!({"rev": "r", "into": "c"}),
        ),
        (
            "world.checkout.into: a directory under {WORLD}",
            json!({"repo": "r", "rev": "r", "into": "../c"}),
        ),
        (
            "world.checkout.sparse: each path relative",
            json!({"repo": "r", "rev": "r", "into": "c", "sparse": ["/a"]}),
        ),
    ] {
        v["world"]["checkout"] = value;
        let (r, _) = fx.run(&v, &[]);
        assert!(r.code == 2 && r.stderr.contains(why), "{why}: {}", r.stderr);
    }
}

/// The plan review's case (feature 449 T169): a path list too narrow for what a case reads fails both sides alike, which an incremental
/// run reads as SAME; a verify builds whole worlds, so the real difference shows, and it never reuses a side kept from a sparse world.
#[test]
fn a_too_narrow_cone_passes_sparse_but_a_verify_on_whole_worlds_tells_the_truth() {
    let fx = Fx::new();
    let (_repo, sha) = repo(&fx);
    // the case reads b/, which the cone `a` leaves out; the working tree changed b/z.txt
    let mut v = Fx::base(&json!([{"name": "reads b", "steps": [["cat", "b/z.txt"]]}]));
    v["world"] = json!({
        "checkout": {"repo": "repo", "rev": "{REV}", "into": "c", "sparse": ["a"]},
        "cwd": "{WORLD}/c", "files": ["c/a"], "ignore": [".git"]
    });
    v["sides"]["old"]["vars"] = json!({"REV": sha});
    v["sides"]["new"]["vars"] = json!({"REV": "WORKTREE"});
    let (r, report) = fx.run(&v, &[]);
    assert_eq!(
        r.code, 0,
        "both sides fail alike on the sparse world: {}",
        r.stdout
    );
    assert_eq!(report["worlds"], "sparse");
    assert!(r
        .stdout
        .contains("worlds: sparse (world.checkout.sparse) - for iterating only"));
    let (r, report) = fx.run(&v, &["--verify"]);
    assert_eq!(r.code, 1, "{}", r.stdout);
    assert_eq!(report["differing"], json!(["reads b"]));
    assert_eq!(report["worlds"], "whole");
    assert!(r
        .stdout
        .contains("worlds: whole, world.checkout.sparse ignored"));
    // both sides ran on whole worlds: the old side's sparse result was not reused
    assert_eq!(report["sides_rerun"].as_u64(), Some(2));
    // the whole worlds' results are kept apart: the sparse runs still keep their own, and the verify's old side stands for the next
    // verify (a second verify left out of this test, a world over FR-008's tenth of a second)
    assert_eq!(fx.run(&v, &[]).1["sides_rerun"].as_u64(), Some(0));
    let results = fx.root().join("cases.diff-run/results");
    let mut kept: Vec<String> = std::fs::read_dir(results)
        .unwrap()
        .flatten()
        .map(|e| {
            e.file_name()
                .to_string_lossy()
                .rsplit_once('-')
                .unwrap()
                .1
                .to_owned()
        })
        .collect();
    kept.sort();
    assert_eq!(kept.len(), 4);
    assert!(
        kept.iter().filter(|n| n.ends_with(".whole.json")).count() == 2,
        "{kept:?}"
    );
}

//! The command lines (feature 449 T138), with the world's working copy and the stand-in embedder.

use std::cell::RefCell;
use std::path::Path;

use l7r_gate_archive::store::Archive;
use l7r_gate_archive::testkit::World;

use super::{cli_with, py_int, search_with, Reach};
use crate::embed::Embed;
use crate::testkit::{corpus, q, Fake};
use crate::Reply;

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

struct Run<'w> {
    w: &'w World,
    said: RefCell<Vec<String>>,
    fail: bool,
}

impl Run<'_> {
    fn go(&self, search: bool, args: &[&str]) -> (Reply, Vec<String>) {
        self.said.borrow_mut().clear();
        let store = |_: &Path, _: bool| -> Archive { self.w.store() };
        let embed = |_: &Path, _: &Path| -> Box<dyn Embed> {
            Box::new(Fake {
                fail: self.fail,
                ..Fake::default()
            })
        };
        let say = |l: &str| self.said.borrow_mut().push(l.to_owned());
        let reach = Reach {
            store: &store,
            embed: &embed,
            say: &say,
            when: &|| (0, 0),
        };
        let reply = if search {
            search_with(&words(args), &self.w.root, &reach)
        } else {
            cli_with(&words(args), &self.w.root, &reach)
        };
        (reply, self.said.borrow().clone())
    }
}

/// The index built in process, uncommitted: the setup of a test of what reads it, without the commit and push the command's build
/// adds (feature 449 T167, FR-008; the command's build is `build_and_find_through_the_command_line`'s).
fn built(w: &World) {
    let dir = w.store().dir;
    corpus(&dir, &w.root);
    crate::index::build(
        &dir,
        &w.root,
        &mut Fake::default(),
        &[],
        0,
        (0, 0),
        &mut |_| (),
    )
    .unwrap();
}

#[test]
fn build_and_find_through_the_command_line() {
    let w = World::new("sem-cli");
    let run = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: false,
    };
    let (r, _) = run.go(false, &["find", "roofs"]);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            1,
            "semantic-find: no index yet - run `make semantic-index`\n"
        )
    );
    corpus(&w.store().dir, &w.root);
    let (r, said) = run.go(
        false,
        &["build", "--shard", "cd", "--sh", "ab", "--limit", " 1_0 "],
    );
    assert_eq!(r.code, 0);
    assert_eq!(
        said,
        [
            "semantic-index: ab - 2 passages, 2 embedded",
            "semantic-index: cd - 1 passages, 1 embedded",
            "semantic-index: 2 shard(s) written",
            "semantic-index: committed and pushed"
        ]
    );
    let (r, said) = run.go(false, &["build"]);
    assert_eq!((r.code, said.len()), (0, 5));
    let (r, _) = run.go(false, &["find", "Thatched roofs", "--k", "2"]);
    assert_eq!(r.code, 0);
    let lines: Vec<&str> = r.stdout.lines().collect();
    assert_eq!(lines.len(), 4);
    assert!(lines[0].ends_with("  cd/cde789/20260101T000000Z/text.txt [0:63]"));
    assert_eq!(
        lines[1],
        "       Thatched roofs were replaced every twenty years by the village."
    );
}

/// Argparse's refusals, the embedder's, and a file gone (split from the test above, feature 449 T167: the two parts on one archive took
/// 128 ms against FR-008's tenth of a second).
#[test]
fn build_and_find_refuse_as_argparse_did_and_name_what_failed() {
    let w = World::new("sem-cli-refused");
    let run = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: false,
    };
    built(&w);
    // refusals: argparse's, the embedder's, a file gone
    for (args, code) in [
        (&["build", "--limit", "x"][..], 2),
        (&["build", "--nope"], 2),
        (&["find"], 2),
        (&["find", "q", "--k", "1.5"], 2),
        (&["find", "q", "--zz"], 2),
        (&["nope"], 2),
        (&[], 2),
    ] {
        assert_eq!(run.go(false, args).0.code, code, "{args:?}");
    }
    let failing = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: true,
    };
    assert!(failing
        .go(false, &["find", "q"])
        .0
        .stderr
        .starts_with("semantic-find: "));
    corpus_change(&w);
    assert_eq!(failing.go(false, &["build"]).0.code, 1);
    std::fs::remove_file(w.store().dir.join("cd/cde789/20260101T000000Z/text.txt")).unwrap();
    assert!(run
        .go(false, &["find", "Thatched roofs", "--k", "1"])
        .0
        .stderr
        .contains("text.txt"));
    // the push refused: exit 1, its words said
    std::fs::remove_dir_all(&w.remote).unwrap();
    crate::testkit::put(&w.store().dir.join("ef/e/1/text.txt"), "a new text");
    let (r, said) = run.go(false, &["build"]);
    assert_eq!(r.code, 1);
    assert!(said
        .last()
        .unwrap()
        .starts_with("semantic-index: the push failed - "));
    std::fs::remove_dir_all(w.store().dir.join(".git")).unwrap();
    crate::testkit::put(&w.store().dir.join("ef/e/2/text.txt"), "another");
    assert!(run
        .go(false, &["build"])
        .0
        .stderr
        .starts_with("semantic-index: "));
}

fn corpus_change(w: &World) {
    crate::testkit::put(&w.store().dir.join("ab/abe/1/text.txt"), "changed");
}

#[test]
fn search_through_the_command_line() {
    let w = World::new("sem-cli-search");
    let run = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: false,
    };
    let (r, _) = run.go(true, &[]);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            2,
            "make research-search: Q=, Q_JA=, Q_ZH=, Q_KO= or TERMS= is required\n"
        )
    );
    assert_eq!(run.go(true, &["--q", "  ", "--terms", "|;| "]).0.code, 2);
    assert_eq!(
        run.go(true, &["--q", "roofs"]).0.stderr,
        "research-search: no index yet - run `make semantic-index`\n"
    );
    assert_eq!(
        run.go(true, &["--terms", "zzz"]).0.stdout,
        "research-search: 0 question(s), 1 term set(s) - 0 of 0 source(s)\n\n"
    );
}

/// A search over a built index, under a key and limits, and argparse's refusals (split from the test above, feature 449 T167: the three
/// parts on one archive took 158 ms against FR-008's tenth of a second, a third of it the measure pattern's one compile).
#[test]
fn a_search_over_a_built_index_through_the_command_line() {
    let w = World::new("sem-cli-built");
    let run = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: false,
    };
    built(&w);
    let (r, _) = run.go(
        true,
        &[
            "--q",
            "Thatched roofs",
            "--terms",
            "twenty|village;roofs",
            "--key",
            "it's",
            "--limit",
            "1",
            "--record-limit",
            "1",
        ],
    );
    assert_eq!(r.code, 0);
    let head = r.stdout.lines().next().unwrap();
    assert!(head.starts_with("research-search: 1 question(s), 2 term set(s) - 2 of "));
    assert!(head.contains(", 0 already shown under key \"it's\"; "));
    assert!(head.ends_with("more not printed - call again under KEY= for the next"));
    for args in [
        &["--limit", "x", "--q", "a"][..],
        &["--record-limit", "y", "--q", "a"],
        &["--nope"],
    ] {
        assert_eq!(run.go(true, args).0.code, 2);
    }
}

/// An embedder that fails, a page moved to its notes and a copy gone (split as above).
#[test]
fn a_search_whose_embedder_fails_or_whose_copy_is_gone() {
    let w = World::new("sem-cli-gone");
    let run = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: false,
    };
    built(&w);
    let failing = Run {
        w: &w,
        said: RefCell::new(Vec::new()),
        fail: true,
    };
    assert!(failing
        .go(true, &["--q", "roofs"])
        .0
        .stderr
        .starts_with("research-search: "));
    std::fs::remove_file(w.root.join(q("0102-roofs.html"))).unwrap();
    std::fs::write(w.root.join(q("0102-roofs.notes.html")), "twenty").unwrap();
    let (r, _) = run.go(true, &["--terms", "twenty"]);
    assert_eq!(r.code, 0);
    std::fs::remove_file(w.store().dir.join("gm-copies/book.txt")).unwrap();
    let (r, _) = run.go(true, &["--q", "charcoal yards"]);
    assert!(r.stdout.starts_with("research-search: ") && r.code == 1);
}

#[test]
fn argparse_s_int() {
    assert_eq!(py_int("--k", " +1_000 "), Ok(1000));
    assert_eq!(py_int("--k", "-3"), Ok(-3));
    for bad in ["", "_1", "1_", "1__0", "x", "+", "99999999999999999999"] {
        assert_eq!(
            py_int("--k", bad),
            Err(format!("argument --k: invalid int value: '{bad}'"))
        );
    }
}

//! The make check over a process table a test writes.

use std::collections::BTreeMap;
use std::path::Path;

use super::{compute, foreign_makefile, lexical, parent_of, refusal, Live, Procs};

#[derive(Default)]
struct Tree(BTreeMap<u32, (&'static str, &'static str, Vec<String>)>);

impl Procs for Tree {
    fn ancestry(&self) -> Vec<u32> {
        self.0.keys().copied().collect()
    }

    fn comm(&self, pid: u32) -> String {
        self.0[&pid].0.to_owned()
    }

    fn cwd(&self, pid: u32) -> String {
        self.0[&pid].1.to_owned()
    }

    fn cmdline(&self, pid: u32) -> Vec<String> {
        self.0[&pid].2.clone()
    }
}

fn argv(words: &[&str]) -> Vec<String> {
    words.iter().map(|s| (*s).to_owned()).collect()
}

const REPO: &str = "/repo";

#[test]
fn a_python_or_a_gate_between_make_and_this_process_changes_nothing() {
    let mut t = Tree::default();
    t.0.insert(1, ("l7r-gate", "/repo", argv(&["l7r-gate"])));
    t.0.insert(2, ("bash", "/repo", argv(&["bash"])));
    t.0.insert(3, ("make", "/repo/sub", argv(&["make", "ci-status"])));
    assert_eq!(compute(&t, Path::new(REPO)), (true, ""));
    assert_eq!(refusal(&t, Path::new(REPO), "op", "t"), None);
}

#[test]
fn no_make_a_make_elsewhere_and_a_foreign_makefile_are_refused() {
    let mut t = Tree::default();
    t.0.insert(1, ("bash", "/repo", argv(&["bash"])));
    assert_eq!(
        compute(&t, Path::new(REPO)),
        (false, "not invoked through make")
    );
    let text = refusal(&t, Path::new(REPO), "l7r.diagram.ci", "ci-status").unwrap();
    assert!(
        text.contains("REFUSED: l7r.diagram.ci was not run through make")
            && text.contains("make ci-status")
    );
    t.0.insert(2, ("make", "/elsewhere", argv(&["make"])));
    assert!(compute(&t, Path::new(REPO))
        .1
        .contains("does not belong to this repository"));
    t.0.insert(
        3,
        ("gmake", "/repo", argv(&["gmake", "-f", "/tmp/evil.mk"])),
    );
    assert!(!compute(&t, Path::new(REPO)).0);
}

#[test]
fn every_spelling_of_a_makefile_is_judged_where_make_stood() {
    let repo = Path::new(REPO);
    let foreign = |words: &[&str]| foreign_makefile(&argv(words), "/repo", repo);
    assert!(
        foreign(&["make", "-f", "/tmp/x"])
            && foreign(&["make", "--file=/tmp/x"])
            && foreign(&["make", "-f/tmp/x"])
            && foreign(&["make", "--makefile", "../../tmp/x"])
    );
    assert!(
        !foreign(&["make", "-f", "Makefile"])
            && !foreign(&["make"])
            && !foreign(&["make", "-f"])
            && !foreign(&["make", "--file=sub/Makefile"])
    );
    assert_eq!(lexical(Path::new("/a/./b/../c")), Path::new("/a/c"));
    assert_eq!(lexical(Path::new("./a")), Path::new("a"));
}

#[test]
fn the_live_process_table_reads_this_process() {
    let live = Live;
    let chain = live.ancestry();
    assert_eq!(chain[0], std::process::id());
    assert!(
        !live.comm(chain[0]).is_empty()
            && !live.cwd(chain[0]).is_empty()
            && !live.cmdline(chain[0]).is_empty()
    );
    assert_eq!(live.comm(u32::MAX), "");
    assert_eq!(live.cwd(u32::MAX), "");
    assert_eq!(parent_of("12 (a) b) S 34 x"), Some(34));
    assert_eq!(parent_of("garbage"), None);
}

//! The guard on a mirror with a clone and its pool: a hand-made worktree refused, the pool's trees and caches kept, a mention and a
//! scratch worktree passed.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{decide, refusal, verb, ADD, REMOVE};
use crate::protocol::{Answer, Event};
use crate::shared::builder_pool::{write, Tree};
use crate::shared::session::Session;

/// A mirror whose clone `c` has one pool tree, `c-t269` (adopted under its own name), and a home with the cache.
fn world(tag: &str) -> (crate::shared::tempdir::TempDir, PathBuf) {
    let dir = crate::shared::tempdir::TempDir::new(&format!("builder-pool-{tag}"));
    let main = dir.join("m");
    std::fs::create_dir_all(main.join(".clones/c/.git")).unwrap();
    let tree = Tree {
        tree: main.join(".clones/c-t269"),
        feature: String::new(),
        tasks: Vec::new(),
        since: String::new(),
    };
    write(&main.join(".clones/c/.git"), &[tree]).unwrap();
    (dir, main)
}

fn ask(cmd: &str, main: &Path) -> Option<&'static str> {
    let clone = main.join(".clones/c");
    refusal(
        cmd,
        &clone.to_string_lossy(),
        main,
        "/h",
        Path::new("/h/.cache/l7r-cargo-target"),
    )
}

#[test]
fn a_worktree_made_by_hand_under_the_clones_directory_is_refused() {
    let (_d, main) = world("add");
    let m = main.to_string_lossy();
    for cmd in [
        format!("git -C {m}/.clones/c worktree add --detach {m}/.clones/c-t286 HEAD"),
        format!("git worktree add -q --detach {m}/.clones/c-land HEAD"),
        "git worktree add ../c-b9".to_owned(),
        format!("W={m}/.clones/c-x; cd /tmp && git -C {m}/.clones/c worktree add \"$W\""),
    ] {
        assert_eq!(ask(&cmd, &main), Some(ADD), "{cmd}");
    }
    for cmd in [
        "git worktree add --detach /tmp/t285/wt HEAD".to_owned(),
        format!("git log --grep 'git worktree add {m}/.clones/c-x'"),
        format!("echo git worktree add {m}/.clones/c-x"),
        "git worktree list".to_owned(),
        "make builder-tree T=T285".to_owned(),
        "make land F=451 T=T285 NOTE=x".to_owned(),
    ] {
        assert_eq!(ask(&cmd, &main), None, "{cmd}");
    }
}

#[test]
fn a_pool_tree_and_its_build_cache_are_not_removed_by_hand() {
    let (_d, main) = world("remove");
    let m = main.to_string_lossy();
    for cmd in [
        format!("git -C {m}/.clones/c worktree remove --force {m}/.clones/c-t269"),
        format!("git worktree move {m}/.clones/c-t269 {m}/.clones/c-b1"),
        "rm -rf ~/.cache/l7r-cargo-target/c-t269".to_owned(),
        "rm -rf $HOME/.cache/l7r-cargo-target".to_owned(),
        format!("rm -rf {m}/.clones/c-t269"),
    ] {
        assert_eq!(ask(&cmd, &main), Some(REMOVE), "{cmd}");
    }
    for cmd in [
        // not the pool's: the landing's tree, another cache, a file inside the cache
        format!("git -C {m}/.clones/c worktree remove --force {m}/.clones/c-land"),
        "rm -rf ~/.cache/l7r-cargo-target/c-land".to_owned(),
        "rm -f ~/.cache/l7r-cargo-target/c-t269/guard.failed".to_owned(),
        "git worktree remove /tmp/t285/wt".to_owned(),
        "git worktree prune".to_owned(),
        "grep -rn 'rm -rf ~/.cache/l7r-cargo-target/c-t269' docs".to_owned(),
    ] {
        assert_eq!(ask(&cmd, &main), None, "{cmd}");
    }
    assert_eq!((verb("ls x"), verb("git status")), (None, None));
}

#[test]
fn the_guard_answers_logs_and_takes_its_escape_with_a_reason() {
    crate::shared::log::quiet();
    let (dir, main) = world("decide");
    crate::shared::env::set("HOME", dir.join("h"));
    let m = main.to_string_lossy();
    let run = |cmd: &str, cwd: &str| {
        let input = json!({"cwd": cwd, "tool_input": {"command": cmd}});
        let mut s = Session::from_input(&input);
        s.main_seam = Some(m.clone().into_owned());
        decide(
            &Event {
                name: "PreToolUse".to_owned(),
                input,
            },
            &s,
        )
    };
    let add = format!("git worktree add {m}/.clones/c-x");
    assert!(
        matches!(&run(&add, "")[..], [Answer::Refuse(t)] if t.contains("make builder-tree T=<task>"))
    );
    let cache = dir.join("h/.cache/l7r-cargo-target/c-t269");
    let rm = format!("rm -rf {}", cache.display());
    assert!(
        matches!(&run(&rm, &m)[..], [Answer::Refuse(t)] if t.contains("make builder-tree-drop TREE=<path> REASON="))
    );
    assert!(run(
        &format!("{add}  # BUILDER_TREE_OK: a fixture for a guard test"),
        ""
    )
    .is_empty());
    assert!(
        matches!(&run(&format!("{add}  # BUILDER_TREE_OK"), "")[..], [Answer::Refuse(t)] if t.contains("with no reason"))
    );
    assert!(
        run("ls", "").is_empty() && run("rm -rf /tmp/x", "").is_empty() && run("", "").is_empty()
    );
    // the cache's root named by its seam
    crate::shared::env::set("L7R_BUILDER_CACHE", "/elsewhere");
    assert!(run(&rm, &m).is_empty());
    assert!(matches!(
        &run("rm -rf /elsewhere/c-t269", &m)[..],
        [Answer::Refuse(_)]
    ));
}

/// What a command's head does to a tree: a worktree verb that changes none is no verb, and a head the shell's quoting rules
/// cannot split is still read by its words.
#[test]
fn a_head_is_read_by_its_verb() {
    assert_eq!(super::verb("git worktree list"), None);
    assert_eq!(super::verb("git status"), None);
    assert_eq!(super::verb("git worktree move a b"), Some("remove"));
    assert_eq!(super::verb("rm -rf 'unclosed"), Some("rm"));
    assert_eq!(super::verb("ls"), None);
}

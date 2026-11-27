//! THE BUILDER POOL'S REGISTRY (feature 451 T285; the GM, 2026-11-26: "we should make it so that whatever tooling we use to create
//! worktrees automatically enforces and performs the correct behavior without the opportunity for this kind of mistake in the
//! future"). A builder's worktree is one of a clone's standing pool, handed out and released by `make builder-tree` and never made or
//! removed by hand: on 2026-11-26 the coordinating session made a fresh worktree for each builder and deleted it and its build cache
//! after the landing, so 21 of 22 code builders ran cold, a first closing-checks run of 14-30 minutes against about one minute warm
//! (`docs/process-decisions.md`, "Two code builders at once").
//!
//! The registry is `<git common dir>/builder-pool.json`, `{"trees": [{"tree", "feature", "tasks", "since"}]}`: the pool's trees in
//! the order made, each free (`tasks` empty) or held by the tasks named. MEMBERSHIP IS THE REGISTRY, NOT A NAME: a new tree is
//! `<clone>-b<N>`, but the three trees of 2026-11-26 were adopted under their own names, because renaming a tree chills its cache
//! (measured 2026-11-26: `git worktree move` and the cache directory moved with it, the tool build went from 0.11 s to 66.5 s and the
//! guard's test build from 0.08 s to 41.7 s - cargo's fingerprints hold the workspace's absolute path; moved back, 68.3 s and
//! 41.7 s again). The gate's `builder-tree` writes it (`rust/gate/crates/task/src/builder_tree.rs`); the guard reads it
//! (`rust/guard/src/guards/builder_pool_hooks.rs`).
//!
//! A tree's build cache is `<cache root>/<the tree's directory name>` (`scripts/gates/l7r-gate.sh`, `scripts/hooks/l7r-guard.sh`).
// GUARD_EDIT_OK: feature 451 T285 - a new operation, the builder pool's registry, which the gate writes and the new guard reads

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

/// The registry's file, in the git common directory.
pub const FILE: &str = "builder-pool.json";
/// The most trees a clone's pool holds unless `L7R_BUILDER_POOL` says otherwise. GUESS: the largest count of builders at once that
/// was ever run (four, 2026-11-26's comment batches), each tree's cache about 9 GB; the count worth running is 451 T284's to measure.
pub const CAP: usize = 4;

/// THE LANE'S RESERVED HOLDER (feature 461 T13, plan D1): the landing lane's tree, `<clone>-land`, is in the registry held by this one
/// word as its task, no feature - so it is never free, no handout takes it, no landing frees it (a hold naming no feature), and the
/// cache sweep keeps it (`scratch_sweep_hooks/sweep/evict.rs`, 451 T526). It is no builder's: [`read`] leaves it out, so every count
/// of builders' trees - the queue's `alone` and idle rules, the sampler's - is a count of builders; [`read_all`] is the registry
/// whole, for its one writer and the sweep.
// GUARD_EDIT_OK: feature 461 T13 - a new operation, the lane's tree in the pool's registry under a reserved holder
pub const LANE: &str = "lane";

/// One pool tree: where it is, and the feature and tasks holding it since `since` (free since then where `tasks` is empty).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Tree {
    pub tree: PathBuf,
    pub feature: String,
    pub tasks: Vec<String>,
    pub since: String,
}

impl Tree {
    /// No task holds it.
    #[must_use]
    pub fn free(&self) -> bool {
        self.tasks.is_empty()
    }

    /// It is the landing lane's tree: held by [`LANE`] alone.
    #[must_use]
    pub fn lane(&self) -> bool {
        self.tasks.len() == 1 && self.tasks[0] == LANE
    }

    /// Who holds it, as a reader names it: `451 T285`, `T285` with no feature, `lane`, `free`.
    #[must_use]
    pub fn holder(&self) -> String {
        if self.free() {
            "free".to_owned()
        } else {
            format!("{} {}", self.feature, self.tasks.join(","))
                .trim()
                .to_owned()
        }
    }
}

/// The builders' trees of the clone whose git common directory is `common`, the lane's left out ([`LANE`]); empty where none was ever
/// made or the file cannot be read.
#[must_use]
pub fn read(common: &Path) -> Vec<Tree> {
    let mut trees = read_all(common);
    trees.retain(|t| !t.lane());
    trees
}

/// The registry whole, the lane's tree in its place: what its writer reads before it writes, and the sweep's kept trees.
#[must_use]
pub fn read_all(common: &Path) -> Vec<Tree> {
    let text = std::fs::read_to_string(common.join(FILE)).unwrap_or_default();
    let value: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    let text_of = |v: &Value| v.as_str().unwrap_or_default().to_owned();
    value["trees"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|t| Tree {
                    tree: PathBuf::from(text_of(&t["tree"])),
                    feature: text_of(&t["feature"]),
                    tasks: t["tasks"]
                        .as_array()
                        .map(|l| l.iter().map(text_of).collect())
                        .unwrap_or_default(),
                    since: text_of(&t["since"]),
                })
                .collect()
        })
        .unwrap_or_default()
}

/// The pool written whole, through a file beside it, so a reader never sees half of one.
///
/// # Errors
/// The file cannot be written or moved into place.
pub fn write(common: &Path, trees: &[Tree]) -> Result<(), String> {
    let list: Vec<Value> = trees
        .iter()
        .map(|t| json!({"tree": t.tree, "feature": t.feature, "tasks": t.tasks, "since": t.since}))
        .collect();
    let text = format!("{:#}\n", json!({ "trees": list }));
    let path = common.join(FILE);
    let tmp = common.join(format!("{FILE}.tmp"));
    std::fs::write(&tmp, text)
        .and_then(|()| std::fs::rename(&tmp, &path))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// Every pool tree of every clone under the clones directory (`<clones>/*/.git/builder-pool.json`): what the guard asks.
#[must_use]
pub fn pools(clones: &Path) -> Vec<Tree> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(clones)
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    dirs.sort();
    dirs.iter().flat_map(|d| read(&d.join(".git"))).collect()
}

/// The build cache of `tree` under the cache's root: named for the tree's directory.
#[must_use]
pub fn cache(root: &Path, tree: &Path) -> PathBuf {
    root.join(tree.file_name().unwrap_or_default())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_registry_round_trips_and_every_clone_s_pool_is_found() {
        let dir = crate::tempdir::TempDir::new("builder-pool");
        let common = dir.join("c1/.git");
        std::fs::create_dir_all(&common).unwrap();
        std::fs::create_dir_all(dir.join("c2/.git")).unwrap();
        std::fs::write(dir.join("a-file"), "").unwrap();
        assert!(read(&common).is_empty());
        let held = Tree {
            tree: dir.join("c1-b1"),
            feature: "451".to_owned(),
            tasks: vec!["T285".to_owned(), "T286".to_owned()],
            since: "2026-11-26T00:00:00Z".to_owned(),
        };
        let free = Tree {
            tree: dir.join("c1-b2"),
            feature: String::new(),
            tasks: Vec::new(),
            since: String::new(),
        };
        let bare = Tree {
            feature: String::new(),
            ..held.clone()
        };
        write(&common, &[held.clone(), free.clone()]).unwrap();
        assert_eq!(read(&common), vec![held.clone(), free.clone()]);
        assert_eq!(pools(&dir), vec![held.clone(), free.clone()]);
        assert!(pools(&dir.join("none")).is_empty());
        assert!(free.free() && !held.free());
        assert_eq!(
            (held.holder(), free.holder(), bare.holder()),
            (
                "451 T285,T286".to_owned(),
                "free".to_owned(),
                "T285,T286".to_owned()
            )
        );
        assert_eq!(
            cache(Path::new("/c"), &held.tree),
            PathBuf::from("/c/c1-b1")
        );
        // the lane's tree: in the registry whole, out of the builders' reading, named by its holder
        let lane = Tree {
            tree: dir.join("c1-land"),
            feature: String::new(),
            tasks: vec![LANE.to_owned()],
            since: String::new(),
        };
        write(&common, &[lane.clone(), held.clone()]).unwrap();
        assert_eq!(read_all(&common), vec![lane.clone(), held.clone()]);
        assert_eq!(read(&common), vec![held.clone()]);
        assert_eq!(pools(&dir), vec![held.clone()]);
        assert!(lane.lane() && !held.lane() && !free.lane() && lane.holder() == "lane");
        // a registry that cannot be written says where
        let err = write(&dir.join("gone"), &[]).unwrap_err();
        assert!(err.contains("builder-pool.json"), "{err}");
        // one that is not the registry's shape is an empty pool
        std::fs::write(common.join(FILE), "{\"trees\": 3}").unwrap();
        assert!(read(&common).is_empty());
    }
}

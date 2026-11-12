//! What one owed computation reads of the repository, read once and handed to each family (feature 449 T107): the revisions,
//! the delta's names and untracked files, and a revision's listing and blobs. Each family once asked for them again: 24 `git`
//! calls a computation on the owed tests' fixture, the base's question pages read by two `cat-file --batch` of 180 ms each on
//! the real record. Held by the computation and passed down, never kept between computations.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

use super::modals::{MODALS, MODAL_DIRS};
use super::owed::ENTRY_READS;
use super::repo::{cat_blobs, git};
use super::units::{QUESTIONS, SOURCE_DIRS};

/// The revisions the families diff against, each asked once and only when needed: HEAD and the merge base of it with
/// origin/main.
#[derive(Default)]
struct Revs {
    head: Option<String>,
    merge: Option<String>,
}

/// A revision's listing under [`Delta::LISTED`] and the blobs read of it so far, by path.
struct Tree {
    listing: String,
    blobs: HashMap<String, String>,
}

/// One computation's reads of the repository at `root`.
pub struct Delta {
    root: PathBuf,
    revs: Revs,
    common: Option<String>,
    status: HashMap<(String, Option<String>), String>,
    others: Option<String>,
    trees: HashMap<String, Tree>,
}

/// Whether a line git printed names a path under `spec`: the pathspec's own match, a directory taken whole; a quoted path
/// (a name git escapes) is matched on what follows its opening quote, its prefix being plain ASCII.
fn under(line: &str, spec: &str) -> bool {
    let path = line.strip_prefix('"').unwrap_or(line);
    let dir = spec.trim_end_matches('/');
    path == dir
        || path
            .strip_prefix(dir)
            .is_some_and(|rest| rest.starts_with('/'))
}

/// The lines of `text` under any of `specs`, each ended as git ends it.
fn filtered(text: &str, specs: &[&str]) -> String {
    text.lines()
        .filter(|l| specs.iter().any(|s| under(l, s)))
        .fold(String::new(), |out, l| out + l + "\n")
}

impl Delta {
    /// Every path a diff or untracked listing is asked about: entry-drift's reads hold the record's directories and the
    /// pop-ups' (`research/`, `l7r/diagram/interactive/`), so one listing over them answers every family.
    pub const WATCHED: [&str; 9] = ENTRY_READS;

    /// Every directory a revision's files are read from: the record's, translation's and the pop-ups'.
    pub const LISTED: [&str; 6] = [
        QUESTIONS,
        SOURCE_DIRS[0],
        SOURCE_DIRS[1],
        MODAL_DIRS[0],
        MODAL_DIRS[1],
        MODALS,
    ];

    #[must_use]
    pub fn new(root: &Path) -> Self {
        Self {
            root: root.to_path_buf(),
            revs: Revs::default(),
            common: None,
            status: HashMap::new(),
            others: None,
            trees: HashMap::new(),
        }
    }

    #[must_use]
    pub fn root(&self) -> &Path {
        &self.root
    }

    fn verify(&self, rev: &str) -> String {
        git(&self.root, &["rev-parse", "--verify", "-q", rev])
            .trim()
            .to_owned()
    }

    /// The merge base of HEAD with origin/main, "" where either is missing: a merge base found says both exist, so the
    /// common case asks nothing else.
    fn merge(&mut self) -> String {
        let root = &self.root;
        self.revs
            .merge
            .get_or_insert_with(|| {
                git(root, &["merge-base", "HEAD", "origin/main"])
                    .trim()
                    .to_owned()
            })
            .clone()
    }

    fn head(&mut self) -> String {
        if self.revs.head.is_none() {
            self.revs.head = Some(self.verify("HEAD"));
        }
        self.revs.head.clone().unwrap_or_default()
    }

    /// The merge base of HEAD with origin/main, else HEAD where origin/main is missing (`owed::merge_base`).
    pub fn merge_base(&mut self) -> String {
        let merge = self.merge();
        if merge.is_empty() && self.verify("origin/main").is_empty() {
            return self.head();
        }
        merge
    }

    /// The base `entry_owed` diffs against (`entry_owed.base_of`): the merge base where there is one, else HEAD.
    pub fn entry_base(&mut self) -> String {
        let merge = self.merge();
        if merge.is_empty() {
            return self.head();
        }
        merge
    }

    /// The base translation reads its pairs at: the merge base alone, "" where there is none (no HEAD fallback).
    pub fn translation_base(&mut self) -> String {
        self.merge()
    }

    /// The repository's git directory: `rev-parse --git-common-dir` under the root, `.git` where it says nothing.
    pub fn git_dir(&mut self) -> PathBuf {
        let root = &self.root;
        let common = self.common.get_or_insert_with(|| {
            git(root, &["rev-parse", "--git-common-dir"])
                .trim()
                .to_owned()
        });
        root.join(if common.is_empty() { ".git" } else { common })
    }

    /// The clone's answer records (`owed::store`): `RECORD_CHECKS_DIR`, else under [`Self::git_dir`].
    pub fn store(&mut self) -> PathBuf {
        super::owed::answers::store_in(std::env::var_os("RECORD_CHECKS_DIR"), &mut || {
            self.git_dir()
        })
    }

    /// What `git diff --name-only base [head] -- specs` prints (`specs` under [`Self::WATCHED`]), from one
    /// `--name-status --no-renames` over them all. Without rename detection each path stands alone, so the shared listing
    /// filtered is the narrow one wherever no rename was possible: a rename pairs a deleted path with an added one under
    /// the same pathspec, and where `specs` hold both, or a status other than A, D, M or T, the narrow diff runs itself.
    pub fn changed(&mut self, base: &str, head: Option<&str>, specs: &[&str]) -> String {
        let root = &self.root;
        let status = self
            .status
            .entry((base.to_owned(), head.map(str::to_owned)))
            .or_insert_with(|| {
                let mut args = vec!["diff", "--name-status", "--no-renames", base];
                args.extend(head);
                args.push("--");
                args.extend(Self::WATCHED);
                git(root, &args)
            });
        let (mut names, mut codes) = (String::new(), HashSet::new());
        for line in status.lines() {
            let (code, path) = line.split_once('\t').unwrap_or(("", line));
            if specs.iter().any(|s| under(path, s)) {
                codes.insert(code);
                names = names + path + "\n";
            }
        }
        let plain = codes.iter().all(|c| matches!(*c, "A" | "D" | "M" | "T"));
        if plain && !(codes.contains("A") && codes.contains("D")) {
            return names;
        }
        let mut args = vec!["diff", "--name-only", base];
        args.extend(head);
        args.push("--");
        args.extend(specs);
        git(root, &args)
    }

    /// What `git ls-files --others --exclude-standard -- specs` prints (`specs` under [`Self::WATCHED`]): untracked files
    /// pair with nothing, so one listing filtered is exact.
    pub fn others(&mut self, specs: &[&str]) -> String {
        let root = &self.root;
        let all = self.others.get_or_insert_with(|| {
            let mut args = vec!["ls-files", "--others", "--exclude-standard", "--"];
            args.extend(Self::WATCHED);
            git(root, &args)
        });
        filtered(all, specs)
    }

    fn tree(&mut self, rev: &str) -> &mut Tree {
        let root = &self.root;
        self.trees.entry(rev.to_owned()).or_insert_with(|| {
            let mut args = vec!["ls-tree", "-r", "--name-only", rev, "--"];
            args.extend(Self::LISTED);
            Tree {
                listing: git(root, &args),
                blobs: HashMap::new(),
            }
        })
    }

    /// What `git ls-tree -r --name-only rev -- specs` prints (`specs` under [`Self::LISTED`]), from one listing of them all.
    pub fn listing(&mut self, rev: &str, specs: &[&str]) -> String {
        filtered(&self.tree(rev).listing, specs)
    }

    /// Reads the files `names` at `rev` not read yet, by one `git cat-file --batch`: a caller about to ask for several
    /// families' files names them all here first.
    pub fn fetch(&mut self, rev: &str, names: &[String]) {
        let root = self.root.clone();
        let tree = self.tree(rev);
        let mut seen = HashSet::new();
        let missing: Vec<&String> = names
            .iter()
            .filter(|n| !tree.blobs.contains_key(*n) && seen.insert(*n))
            .collect();
        let objects: Vec<String> = missing.iter().map(|n| format!("{rev}:{n}")).collect();
        for (name, text) in missing.into_iter().zip(cat_blobs(&root, &objects)) {
            tree.blobs.insert(name.clone(), text);
        }
    }

    /// Each file's text at `rev`, as [`cat_blobs`] reads `rev:name`; a missing one is empty.
    pub fn texts(&mut self, rev: &str, names: &[String]) -> Vec<String> {
        self.fetch(rev, names);
        let tree = self.tree(rev);
        names
            .iter()
            .map(|n| tree.blobs.get(n).cloned().unwrap_or_default())
            .collect()
    }
}

#[cfg(test)]
mod tests;

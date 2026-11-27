//! What one owed computation reads of the repository, read once and handed to each family (feature 449 T107): the revisions,
//! the delta's names and untracked files, and a revision's listing and blobs. Each family once asked for them again: 24 `git`
//! calls a computation on the owed tests' fixture, the base's question pages read by two `cat-file --batch` of 180 ms each on
//! the real record. Held by the computation and passed down, never kept between computations. A file the working tree
//! holds unchanged from a revision is read from the tree, so a one-page delta asks git for that page alone (feature 451 T43).

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

use super::modals::MODALS;
use super::owed::ENTRY_READS;
use super::repo::{cat_blobs, git, universal, Fail};
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
    status: HashMap<(String, Option<String>), Result<String, Fail>>,
    others: Option<String>,
    trees: HashMap<String, Tree>,
    flagged: Option<Result<HashSet<String>, Fail>>,
    asked: usize,
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

/// A file git calls unchanged, read from the working tree as [`cat_blobs`] decodes its blob: None where it is no plain
/// file (a link, or absent as a sparse checkout leaves it) or holds a carriage return (an end-of-line conversion could make
/// its blob differ), so the blob is read instead.
fn unchanged(path: &Path) -> Option<String> {
    let plain = std::fs::symlink_metadata(path).is_ok_and(|m| m.is_file());
    let bytes = std::fs::read(path)
        .ok()
        .filter(|b| plain && !b.contains(&b'\r'))?;
    Some(String::from_utf8_lossy(&bytes).into_owned())
}

/// `git -C root args...`'s stdout as [`git`] reads it, else the refusal naming git's error: a diff or listing that printed
/// nothing because it could not run is no answer that nothing changed, and owing everything instead would flood the
/// checks (the session's ruling on T43, 2026-11-20).
fn ran(root: &Path, args: &[&str]) -> Result<String, Fail> {
    let (ok, out, err) = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map_or((false, Vec::new(), b"git could not be run".to_vec()), |o| {
            (o.status.success(), o.stdout, o.stderr)
        });
    if ok {
        return Ok(universal(&String::from_utf8_lossy(&out)));
    }
    Err(format!(
        "cannot tell what changed: git {} failed: {}; repair the index, e.g. git -C {} reset -q",
        args[0],
        String::from_utf8_lossy(&err).trim(),
        root.display()
    ))
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
    pub const WATCHED: [&str; 4] = ENTRY_READS;

    /// Every directory a revision's files are read from: the record's, translation's and the pop-ups'.
    pub const LISTED: [&str; 4] = [QUESTIONS, SOURCE_DIRS[0], SOURCE_DIRS[1], MODALS];

    #[must_use]
    pub fn new(root: &Path) -> Self {
        Self {
            root: root.to_path_buf(),
            revs: Revs::default(),
            common: None,
            status: HashMap::new(),
            others: None,
            trees: HashMap::new(),
            flagged: None,
            asked: 0,
        }
    }

    /// How many objects this computation has asked `git cat-file` for: the base read's cost (feature 451 T43).
    #[must_use]
    pub fn blobs_asked(&self) -> usize {
        self.asked
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
    /// common case asks nothing else. At a hand-in, the base it names (`l7r_gate_core::delta_base`, 461 T34).
    fn merge(&mut self) -> String {
        let root = &self.root;
        self.revs
            .merge
            .get_or_insert_with(|| {
                l7r_gate_core::delta_base::named(root).unwrap_or_else(|| {
                    git(root, &["merge-base", "HEAD", "origin/main"])
                        .trim()
                        .to_owned()
                })
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
        super::owed::answers::store_named(super::owed::answers::record_checks_dir(), &mut || {
            self.git_dir()
        })
    }

    /// What `git diff --name-only base [head] -- specs` prints (`specs` under [`Self::WATCHED`]), from one
    /// `--name-status --no-renames` over them all. Without rename detection each path stands alone, so the shared listing
    /// filtered is the narrow one wherever no rename was possible: a rename pairs a deleted path with an added one under
    /// the same pathspec, and where `specs` hold both, or a status other than A, D, M or T, the narrow diff runs itself.
    ///
    /// # Errors
    ///
    /// Where git cannot run the diff (a corrupt index): the refusal names git's error and the repair.
    pub fn changed(
        &mut self,
        base: &str,
        head: Option<&str>,
        specs: &[&str],
    ) -> Result<String, Fail> {
        let status = self.status(base, head)?;
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
            return Ok(names);
        }
        let mut args = vec!["diff", "--name-only", base];
        args.extend(head);
        args.push("--");
        args.extend(specs);
        ran(&self.root, &args)
    }

    /// `git diff --name-status --no-renames base [head] -- WATCHED`, asked once for each pair; the refusal where git failed
    /// in a repository (a corrupt index), and nothing where there is no repository at all (`rev-parse --git-dir` fails,
    /// asked only after a failed diff): nothing to judge, as before T43 (`land`'s replay runs the triage in a bare directory).
    fn status(&mut self, base: &str, head: Option<&str>) -> Result<&str, Fail> {
        let root = &self.root;
        self.status
            .entry((base.to_owned(), head.map(str::to_owned)))
            .or_insert_with(|| {
                let mut args = vec!["diff", "--name-status", "--no-renames", base];
                args.extend(head);
                args.push("--");
                args.extend(Self::WATCHED);
                ran(root, &args).or_else(|refused| {
                    if ran(root, &["rev-parse", "--git-dir"]).is_ok() {
                        Err(refused)
                    } else {
                        Ok(String::new())
                    }
                })
            })
            .as_deref()
            .map_err(Clone::clone)
    }

    /// What `git ls-files --others --exclude-standard -- specs` prints (`specs` under [`Self::WATCHED`]): untracked files
    /// pair with nothing, so one listing filtered is exact. A tree git cannot list (no repository at all) has none; a
    /// corrupt index is refused by [`Self::changed`], which every family asks first wherever there is a base.
    pub fn others(&mut self, specs: &[&str]) -> String {
        let root = &self.root;
        let all = self.others.get_or_insert_with(|| {
            let mut args = vec!["ls-files", "--others", "--exclude-standard", "--"];
            args.extend(Self::WATCHED);
            git(root, &args)
        });
        filtered(all, specs)
    }

    /// The tracked files under [`Self::LISTED`] whose working copy git does not compare (`ls-files -v` tags them other
    /// than `H`: assume-unchanged in lower case, skip-worktree `S`), so a diff's silence says nothing of them; None where
    /// git failed.
    fn flagged(&mut self) -> Option<&HashSet<String>> {
        let root = &self.root;
        self.flagged
            .get_or_insert_with(|| {
                let mut args = vec!["ls-files", "-v", "--"];
                args.extend(Self::LISTED);
                ran(root, &args).map(|out| {
                    out.lines()
                        .filter_map(|l| l.split_once(' '))
                        .filter(|(tag, _)| *tag != "H")
                        .map(|(_, path)| path.to_owned())
                        .collect()
                })
            })
            .as_ref()
            .ok()
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
    /// families' files names them all here first. A file `rev` lists that the working tree holds unchanged (no line of
    /// the cached diff of `rev` against the tree names it, nor does `ls-files -v` flag it) is read from the tree instead,
    /// as the same bytes: a one-page delta asked git for every page at the base, 1,951 blobs and 0.63-1.13 s of each
    /// 1.4-1.6 s computation on the real record, measured 2026-11-20 (451 T40, a `git` shim timing `cat-file`), where the
    /// tree's copies cost a file read each (feature 451 T43). Where the diff or `ls-files -v` failed, as a corrupt index
    /// fails both, nothing is called unchanged and every name goes to `cat-file`: their silence would read every page
    /// from the tree and owe nothing for the edits (the session's ruling on T43, 2026-11-20: failing closed).
    pub fn fetch(&mut self, rev: &str, names: &[String]) {
        let root = self.root.clone();
        let moved: Option<HashSet<String>> = self.status(rev, None).ok().map(|status| {
            status
                .lines()
                .map(|l| l.split_once('\t').map_or(l, |p| p.1).to_owned())
                .collect()
        });
        let moved = moved.and_then(|mut moved| {
            moved.extend(self.flagged()?.iter().cloned());
            Some(moved)
        });
        let tree = self.tree(rev);
        let listed: HashSet<&str> = tree.listing.lines().collect();
        let mut seen = HashSet::new();
        let mut missing = Vec::new();
        for name in names {
            if tree.blobs.contains_key(name) || !seen.insert(name) {
                continue;
            }
            let same = listed.contains(name.as_str())
                && moved.as_ref().is_some_and(|moved| !moved.contains(name));
            match same.then(|| unchanged(&root.join(name))).flatten() {
                Some(text) => drop(tree.blobs.insert(name.clone(), text)),
                None => missing.push(name.clone()),
            }
        }
        let objects: Vec<String> = missing.iter().map(|n| format!("{rev}:{n}")).collect();
        self.asked += objects.len();
        let read = cat_blobs(&root, &objects);
        let tree = self.tree(rev);
        for (name, text) in missing.into_iter().zip(read) {
            tree.blobs.insert(name, text);
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

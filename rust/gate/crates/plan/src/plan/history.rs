//! The earlier texts of a plan's blocks (feature 449 T066): the digests a verdict was written at, kept in the clone's git directory
//! (feature 405 T102, `plan_seen.py`), and plan.md's versions read from git newest first, in chunks, only as far back as a question
//! needs (D63). Where nothing can be read it knows nothing, and a block's earlier text found nowhere is no typo: the conservative side.
//!
//! EACH VERSION IS FETCHED AND PARSED ONCE A PROCESS (451 T457): a version, a commit's plan.md, never changes, so its blocks and task
//! sections are indexed by digest the first time any History reads it, kept for the thread's life and shared by every History and
//! question after. WHY: a landing's first pass asked 69 questions a task, each over a fresh History, and each question parsed every
//! version it walked again - a block whose earlier text is found nowhere walks all of them - so one task cost 16,773 parses of a 1 MB
//! plan.md with 477 versions (63 s), and a batch of 35 tasks 34 minutes, growing with every commit. A History's own list of versions
//! is never shared: the landing commits between its questions, and its callers read at different references.
//!
//! AND EACH VERSION'S DIGESTS ARE KEPT ON DISK FOR EVERY PROCESS AFTER (451 T465, `history/index.rs`): a walk over a commit the
//! index covers is a lookup, and only the version a question returns is fetched for its text, so a process reads from git only
//! the versions committed since the index last caught up, and those answers. WHY: after T457 the one indexing pass still cost
//! about 5 s in each process that asked - a landing's tick checks, `plan push`, the push table's plan row.

use std::cell::RefCell;
use std::collections::HashMap;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::rc::Rc;

use super::sections::{block_digest, digest, digests};
use crate::codeid::common_git_dir;
use index::Index;

mod index;

const DIR: &str = "plan-seen";
/// Versions of plan.md read per `cat-file --batch` while a block's earlier text is sought (D63).
const CHUNK: usize = 25;

fn store(plan: &Path) -> Option<PathBuf> {
    common_git_dir(plan.parent()?).map(|d| d.join(DIR))
}

/// Keep each (digest, text) a verdict was written at, whether or not that version was ever committed.
pub(super) fn keep(plan: &Path, pairs: &[(String, String)]) {
    if let Some(dir) = store(plan) {
        let _ = std::fs::create_dir_all(&dir);
        for (sha, text) in pairs {
            let _ = std::fs::write(dir.join(format!("{sha}.txt")), text);
        }
    }
}

fn recall(plan: &Path, sha: &str) -> Option<String> {
    if sha.is_empty() || !sha.chars().all(char::is_alphanumeric) {
        return None;
    }
    std::fs::read_to_string(store(plan)?.join(format!("{sha}.txt"))).ok()
}

/// One version of plan.md, indexed: each block's key -> (its block digest, its text), and each task -> (its section's digest, the
/// section), every string interned. Keys are unique within a version (`blocks` numbers a repeated heading `#2`), so a lookup is the
/// walk's `find`.
#[derive(Default)]
struct Version {
    blocks: HashMap<Rc<str>, (Rc<str>, Rc<str>)>,
    sections: HashMap<Rc<str>, (Rc<str>, Rc<str>)>,
    /// Whether it was read whole from git (451 T465): only such a version is kept in the index on disk.
    whole: bool,
}

impl Version {
    fn of(text: &str) -> Self {
        let (blocks, sections) = digests::of(text);
        let interned = |all: Vec<(String, String, String)>| {
            all.into_iter()
                .map(|(key, sha, text)| (intern(key), (intern(sha), intern(text))))
                .collect()
        };
        Version {
            blocks: interned(blocks),
            sections: interned(sections),
            whole: false,
        }
    }

    /// Its blocks when `block`, else its task sections.
    fn map(&self, block: bool) -> &HashMap<Rc<str>, (Rc<str>, Rc<str>)> {
        if block {
            &self.blocks
        } else {
            &self.sections
        }
    }

    /// The text at `key` (a block's key or a task) of `index` whose digest is `sha`.
    fn at(index: &HashMap<Rc<str>, (Rc<str>, Rc<str>)>, key: &str, sha: &str) -> Option<String> {
        index
            .get(key)
            .filter(|(at, _)| &**at == sha)
            .map(|(_, text)| String::from(&**text))
    }
}

thread_local! {
    /// Every version read on this thread, by its path in the repository and then its commit: a commit names one content.
    static VERSIONS: RefCell<HashMap<String, HashMap<String, Rc<Version>>>> = RefCell::new(HashMap::new());
    /// Each plan's list of versions by (its path, the commit its reference named), read by [`History::load_revisions`].
    static LISTS: RefCell<HashMap<(PathBuf, String), Listed>> = RefCell::new(HashMap::new());
    /// Each distinct string once: a key, digest, block or section unchanged across versions is held by all of them.
    static TEXTS: RefCell<std::collections::HashSet<Rc<str>>> = RefCell::new(std::collections::HashSet::new());
    /// The digest index of each plan path, by its file (451 T465): read from disk once a thread, and again where a walk meets a
    /// commit it does not cover.
    static INDEXES: RefCell<HashMap<PathBuf, Shared>> = RefCell::new(HashMap::new());
}

type Shared = Rc<RefCell<Index>>;

fn intern(text: String) -> Rc<str> {
    TEXTS.with(|texts| {
        let mut texts = texts.borrow_mut();
        if let Some(have) = texts.get(text.as_str()) {
            return Rc::clone(have);
        }
        let rc: Rc<str> = Rc::from(text);
        texts.insert(Rc::clone(&rc));
        rc
    })
}

fn cached(rel: &str, commit: &str) -> Option<Rc<Version>> {
    VERSIONS.with(|v| v.borrow().get(rel).and_then(|at| at.get(commit)).cloned())
}

fn remember(rel: &str, commit: &str, version: Version) -> Rc<Version> {
    let version = Rc::new(version);
    VERSIONS.with(|v| {
        let mut v = v.borrow_mut();
        let at = v.entry(rel.to_owned()).or_default();
        at.insert(commit.to_owned(), Rc::clone(&version));
    });
    version
}

/// (plan.md's commits at a reference, newest first; its path in the repository).
type Listed = Rc<(Vec<String>, String)>;

/// plan.md's earlier versions, newest first.
pub(super) struct History {
    path: PathBuf,
    reference: String,
    revisions: RefCell<Option<Listed>>,
    /// The index this History reads and its file (none outside a repository: an index of this History's own, never written).
    index: RefCell<Option<(Option<PathBuf>, Shared)>>,
    /// Whether this History has read the file again since it met a commit the index did not cover.
    reread: std::cell::Cell<bool>,
}

impl History {
    pub(super) fn new(plan: &Path, reference: &str) -> Self {
        Self {
            path: plan.to_owned(),
            reference: reference.to_owned(),
            revisions: RefCell::new(None),
            index: RefCell::new(None),
            reread: std::cell::Cell::new(false),
        }
    }

    pub(super) fn path(&self) -> &Path {
        &self.path
    }

    fn dir(&self) -> &Path {
        self.path.parent().unwrap_or(Path::new("."))
    }

    fn git(&self, args: &[&str]) -> String {
        let done = Command::new("git")
            .arg("-C")
            .arg(self.dir())
            .args(args)
            .output();
        done.map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
            .unwrap_or_default()
    }

    fn name(&self) -> String {
        self.path
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned()
    }

    /// The versions at the reference's commit: listed once a thread for each commit the reference names when asked (`git log` over
    /// the path walks the whole repository's history, 0.3 s at 19,603 commits, measured 2026-11-27, and the first pass made 70
    /// Histories), so a commit made between two Histories gives the second its own list.
    fn load_revisions(&self) {
        if self.revisions.borrow().is_some() {
            return;
        }
        let at = self.git(&[
            "rev-parse",
            "--verify",
            "-q",
            &format!("{}^{{commit}}", self.reference),
        ]);
        let key = (self.path.clone(), at.trim().to_owned());
        let listed = LISTS.with(|l| l.borrow().get(&key).cloned());
        let listed = listed.unwrap_or_else(|| {
            let listed = Rc::new(self.list());
            LISTS.with(|l| l.borrow_mut().insert(key, Rc::clone(&listed)));
            listed
        });
        *self.revisions.borrow_mut() = Some(listed);
    }

    /// (plan.md's commits at the reference, newest first; its path in the repository).
    fn list(&self) -> (Vec<String>, String) {
        let name = self.name();
        let mut rel = self
            .git(&["ls-files", "--full-name", "--", &name])
            .trim()
            .to_owned();
        if rel.is_empty() {
            rel = self.git(&["rev-parse", "--show-prefix"]).trim().to_owned() + &name;
        }
        let revs = self.git(&["log", "--format=%H", &self.reference, "--", &name]);
        (revs.split_whitespace().map(str::to_owned).collect(), rel)
    }

    /// The index of `rel` this History reads: the thread's, loaded from the clone's git directory on its first use there.
    fn index(&self, revs: &[String], rel: &str) -> (Option<PathBuf>, Shared) {
        if let Some(have) = &*self.index.borrow() {
            return have.clone();
        }
        let file = common_git_dir(self.dir()).map(|d| index::file(&d, rel));
        let shared = file.as_ref().map_or_else(Shared::default, |file| {
            let have = INDEXES.with(|i| i.borrow().get(file).cloned());
            have.unwrap_or_else(|| {
                let shared = Rc::new(RefCell::new(self.load(file, revs, rel)));
                INDEXES.with(|i| i.borrow_mut().insert(file.clone(), Rc::clone(&shared)));
                shared
            })
        });
        *self.index.borrow_mut() = Some((file, shared));
        self.index.borrow().clone().unwrap_or_default()
    }

    /// The index on disk at `file`, kept only where one commit it covers, parsed now, has the digests it records - the first of
    /// `revs` it covers, else the one it took last (the canary: a parser that digests differently drops the file, never answers
    /// from it; an index that covers nothing is kept).
    fn load(&self, file: &Path, revs: &[String], rel: &str) -> Index {
        let read = index::read(file);
        let probe = revs
            .iter()
            .map(String::as_str)
            .find(|r| read.covers(r).is_some());
        let Some(probe) = probe.or_else(|| read.last_added()).map(str::to_owned) else {
            return read;
        };
        let version = cached(rel, &probe).or_else(|| {
            let got = fetch(self.dir(), &[probe.as_str()], rel).pop().flatten()?;
            Some(remember(rel, &probe, got))
        });
        let id = read.covers(&probe).unwrap_or_default();
        match version {
            Some(version) if index::entries(&version) == read.entries_of(id) => read,
            _ => Index::default(),
        }
    }

    /// Read the versions of the chunk at `from` that neither this thread nor the index holds, in one `cat-file --batch`, into the
    /// thread's store and the index.
    fn load_chunk(&self, from: usize, revs: &[String], rel: &str, index: &Shared) {
        let chunk = &revs[from..(from + CHUNK).min(revs.len())];
        let unread: Vec<&str> = chunk
            .iter()
            .map(String::as_str)
            .filter(|c| cached(rel, c).is_none() && index.borrow().covers(c).is_none())
            .collect();
        let got = fetch(self.dir(), &unread, rel);
        for (commit, version) in unread.into_iter().zip(got) {
            match version {
                Some(version) => index
                    .borrow_mut()
                    .add(commit, &remember(rel, commit, version)),
                // a version that cannot be read is read as empty, as the walk read it, and never kept on disk: it may be a passing failure
                None => drop(remember(rel, commit, Version::of(""))),
            }
        }
    }

    /// The version at `commit` read from git alone (an index's hit: the text it returns), kept for the thread.
    fn one(&self, rel: &str, commit: &str) -> Rc<Version> {
        let got = fetch(self.dir(), &[commit], rel).pop().flatten();
        remember(rel, commit, got.unwrap_or(Version::of("")))
    }

    /// The text the first version, newest first, holding `key` (a block's key when `block`, else a task) at the digest `sha` had.
    fn first(&self, block: bool, key: &str, sha: &str) -> Option<String> {
        self.load_revisions();
        let store = self.revisions.borrow().clone()?;
        let (revs, rel) = &*store;
        let (file, index) = self.index(revs, rel);
        let mut found = None;
        let mut i = 0;
        while i < revs.len() {
            let commit = revs[i].as_str();
            let covered = index.borrow().covers(commit);
            let version = match (cached(rel, commit), covered) {
                (Some(version), covered) => {
                    // a version read for another reason (a canary, a dropped index) is caught up here
                    if version.whole && covered.is_none() {
                        index.borrow_mut().add(commit, &version);
                    }
                    version
                }
                (None, Some(id)) if !index.borrow().holds(block, key, sha, id) => {
                    i += 1;
                    continue;
                }
                (None, Some(_)) => {
                    let kept = file
                        .as_deref()
                        .and_then(|f| kept_text(f, commit, block, key, sha));
                    if kept.is_some() {
                        found = kept;
                        break;
                    }
                    self.one(rel, commit)
                }
                (None, None) => {
                    if let Some(file) = file.as_ref().filter(|_| !self.reread.replace(true)) {
                        // another process may have indexed it since this thread read the file
                        let on_disk = self.load(file, revs, rel);
                        index.borrow_mut().absorb(on_disk);
                        continue;
                    }
                    self.load_chunk(i, revs, rel, &index);
                    continue;
                }
            };
            found = Version::at(version.map(block), key, sha);
            if let Some(text) = &found {
                if let Some(path) = file.as_deref().filter(|_| version.whole) {
                    index::keep_text(&index::text_file(path, commit, block, key), text);
                }
                break;
            }
            i += 1;
        }
        if let Some(file) = file.filter(|_| index.borrow().dirty) {
            let on_disk = self.load(&file, revs, rel);
            index::save(&file, &mut index.borrow_mut(), on_disk);
        }
        found
    }

    /// The text a block had when its digest was `sha`, as its verdict kept it or from the plan's history.
    pub(super) fn block(&self, key: &str, sha: &str) -> Option<String> {
        if let Some(kept) = recall(&self.path, sha).filter(|k| block_digest(k) == sha) {
            return Some(kept);
        }
        self.first(true, key, sha)
    }

    pub(super) fn section(&self, task: &str, sha: &str) -> Option<String> {
        self.first(false, task, sha)
    }
}

/// The text kept beside the index `file` that `key` had at `commit`, where its digest is still `sha`.
fn kept_text(file: &Path, commit: &str, block: bool, key: &str, sha: &str) -> Option<String> {
    let path = index::text_file(file, commit, block, key);
    let text = std::fs::read_to_string(&path).ok()?;
    let at = if block {
        block_digest(&text)
    } else {
        digest(text.as_bytes())
    };
    // a hit is a read: touched, so the texts' prune keeps it (451 T478)
    (at == sha).then(|| index::touch(&path)).map(|()| text)
}

/// Each of `revs`' version of `rel`, read by one `cat-file --batch` and parsed; None for one that could not be read whole.
fn fetch(dir: &Path, revs: &[&str], rel: &str) -> Vec<Option<Version>> {
    let input: String = revs.iter().flat_map(|r| [r, ":", rel, "\n"]).collect();
    let got = batch(dir, &input).unwrap_or_default();
    #[cfg(test)]
    count(revs.len(), revs.len());
    let mut at = 0;
    let mut out = Vec::new();
    for _ in revs {
        let end = got[at..]
            .iter()
            .position(|b| *b == b'\n')
            .map_or(got.len(), |p| at + p);
        let head = String::from_utf8_lossy(&got[at..end]).into_owned();
        let size: Option<usize> = head.split_whitespace().nth(2).and_then(|s| s.parse().ok());
        let body = size.and_then(|size| got.get(end + 1..end + 1 + size));
        at = size.map_or(end + 1, |size| end + size + 2).min(got.len());
        out.push(body.map(|body| Version {
            whole: true,
            ..Version::of(&String::from_utf8_lossy(body))
        }));
    }
    out
}

#[cfg(test)]
thread_local! {
    static COUNTS: std::cell::Cell<(usize, usize)> = const { std::cell::Cell::new((0, 0)) };
}

/// (versions fetched, versions parsed) on this thread, for the tests (451 T457).
#[cfg(test)]
fn counted() -> (usize, usize) {
    COUNTS.with(std::cell::Cell::get)
}

#[cfg(test)]
fn count(fetched: usize, parsed: usize) {
    COUNTS.with(|c| c.set((c.get().0 + fetched, c.get().1 + parsed)));
}

fn batch(dir: &Path, input: &str) -> Option<Vec<u8>> {
    let spawned = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["cat-file", "--batch"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn();
    let mut child = spawned.ok()?;
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(input.as_bytes());
    }
    let done = child.wait_with_output().ok()?;
    Some(done.stdout)
}

#[cfg(test)]
mod tests;

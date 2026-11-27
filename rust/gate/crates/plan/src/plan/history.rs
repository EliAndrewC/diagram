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

use std::cell::RefCell;
use std::collections::HashMap;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::rc::Rc;

use super::sections::{block_digest, blocks, digest, task_sections};
use crate::codeid::common_git_dir;

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
}

impl Version {
    fn of(text: &str) -> Self {
        let mut version = Self::default();
        for (key, body, _) in blocks(text) {
            let sha = block_digest(&body);
            version
                .blocks
                .insert(intern(key), (intern(sha), intern(body)));
        }
        for (task, section) in task_sections(text) {
            let sha = digest(section.as_bytes());
            version
                .sections
                .insert(intern(task), (intern(sha), intern(section)));
        }
        version
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
    /// Every version read on this thread, by (commit, path in the repository): a commit names one content.
    static VERSIONS: RefCell<HashMap<(String, String), Rc<Version>>> = RefCell::new(HashMap::new());
    /// Each plan's list of versions by (its path, the commit its reference named), read by [`History::load_revisions`].
    static LISTS: RefCell<HashMap<(PathBuf, String), Listed>> = RefCell::new(HashMap::new());
    /// Each distinct string once: a key, digest, block or section unchanged across versions is held by all of them.
    static TEXTS: RefCell<std::collections::HashSet<Rc<str>>> = RefCell::new(std::collections::HashSet::new());
}

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

/// (plan.md's commits at a reference, newest first; its path in the repository).
type Listed = Rc<(Vec<String>, String)>;

/// plan.md's earlier versions, newest first.
pub(super) struct History {
    path: PathBuf,
    reference: String,
    revisions: RefCell<Option<Listed>>,
    versions: RefCell<Vec<Rc<Version>>>,
}

impl History {
    pub(super) fn new(plan: &Path, reference: &str) -> Self {
        Self {
            path: plan.to_owned(),
            reference: reference.to_owned(),
            revisions: RefCell::new(None),
            versions: RefCell::new(Vec::new()),
        }
    }

    pub(super) fn path(&self) -> &Path {
        &self.path
    }

    fn git(&self, args: &[&str]) -> String {
        let done = Command::new("git")
            .arg("-C")
            .arg(self.path.parent().unwrap_or(Path::new(".")))
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

    /// Take the next chunk of versions: those this thread has read from its store, the rest fetched in one `cat-file --batch`.
    fn load_chunk(&self, from: usize, revs: &[String], rel: &str) {
        let chunk = &revs[from..(from + CHUNK).min(revs.len())];
        let key = |r: &String| (r.clone(), rel.to_owned());
        let unread: Vec<&String> = VERSIONS.with(|v| {
            let v = v.borrow();
            chunk.iter().filter(|r| !v.contains_key(&key(r))).collect()
        });
        if !unread.is_empty() {
            let input: String = unread
                .iter()
                .flat_map(|r| [r.as_str(), ":", rel, "\n"])
                .collect();
            let got =
                batch(self.path.parent().unwrap_or(Path::new(".")), &input).unwrap_or_default();
            #[cfg(test)]
            count(unread.len(), unread.len());
            let mut at = 0;
            for r in unread {
                let end = got[at..]
                    .iter()
                    .position(|b| *b == b'\n')
                    .map_or(got.len(), |p| at + p);
                let head = String::from_utf8_lossy(&got[at..end]).into_owned();
                let size: Option<usize> =
                    head.split_whitespace().nth(2).and_then(|s| s.parse().ok());
                let version = if let Some(size) = size {
                    let body = got.get(end + 1..end + 1 + size).unwrap_or(&[]);
                    at = (end + size + 2).min(got.len());
                    Version::of(&String::from_utf8_lossy(body))
                } else {
                    // a version that cannot be read is read as empty, as the walk read it: its one block an empty preamble
                    at = (end + 1).min(got.len());
                    Version::of("")
                };
                VERSIONS.with(|v| v.borrow_mut().insert(key(r), Rc::new(version)));
            }
        }
        let mut versions = self.versions.borrow_mut();
        VERSIONS.with(|v| {
            let v = v.borrow();
            versions.extend(chunk.iter().filter_map(|r| v.get(&key(r)).cloned()));
        });
    }

    /// The first answer `ask` gives over the versions, newest first.
    fn first(&self, ask: &dyn Fn(&Version) -> Option<String>) -> Option<String> {
        self.load_revisions();
        let store = self.revisions.borrow().clone()?;
        let (revs, rel) = &*store;
        for i in 0..revs.len() {
            if i >= self.versions.borrow().len() {
                self.load_chunk(i, revs, rel);
            }
            let found = ask(&self.versions.borrow()[i]);
            if found.is_some() {
                return found;
            }
        }
        None
    }

    /// The text a block had when its digest was `sha`, as its verdict kept it or from the plan's history.
    pub(super) fn block(&self, key: &str, sha: &str) -> Option<String> {
        if let Some(kept) = recall(&self.path, sha).filter(|k| block_digest(k) == sha) {
            return Some(kept);
        }
        self.first(&|version| Version::at(&version.blocks, key, sha))
    }

    pub(super) fn section(&self, task: &str, sha: &str) -> Option<String> {
        self.first(&|version| Version::at(&version.sections, task, sha))
    }
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

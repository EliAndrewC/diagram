//! The earlier texts of a plan's blocks (feature 449 T066): the digests a verdict was written at, kept in the clone's git directory
//! (feature 405 T102, `plan_seen.py`), and plan.md's versions read from git newest first, in chunks, only as far back as a question
//! needs (D63). Where nothing can be read it knows nothing, and a block's earlier text found nowhere is no typo: the conservative side.

use std::cell::RefCell;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

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

/// plan.md's earlier versions, newest first.
pub(super) struct History {
    path: PathBuf,
    reference: String,
    revisions: RefCell<Option<(Vec<String>, String)>>,
    texts: RefCell<Vec<String>>,
}

impl History {
    pub(super) fn new(plan: &Path, reference: &str) -> Self {
        Self {
            path: plan.to_owned(),
            reference: reference.to_owned(),
            revisions: RefCell::new(None),
            texts: RefCell::new(Vec::new()),
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

    fn load_revisions(&self) {
        if self.revisions.borrow().is_some() {
            return;
        }
        let name = self.name();
        let mut rel = self
            .git(&["ls-files", "--full-name", "--", &name])
            .trim()
            .to_owned();
        if rel.is_empty() {
            rel = self.git(&["rev-parse", "--show-prefix"]).trim().to_owned() + &name;
        }
        let revs = self.git(&["log", "--format=%H", &self.reference, "--", &name]);
        *self.revisions.borrow_mut() =
            Some((revs.split_whitespace().map(str::to_owned).collect(), rel));
    }

    /// Read the next chunk of versions, in one `cat-file --batch`.
    fn load_chunk(&self, from: usize, revs: &[String], rel: &str) {
        let chunk = &revs[from..(from + CHUNK).min(revs.len())];
        let input: String = chunk
            .iter()
            .flat_map(|r| [r.as_str(), ":", rel, "\n"])
            .collect();
        let got = batch(self.path.parent().unwrap_or(Path::new(".")), &input).unwrap_or_default();
        let mut at = 0;
        let mut texts = self.texts.borrow_mut();
        for _ in chunk {
            let end = got[at..]
                .iter()
                .position(|b| *b == b'\n')
                .map_or(got.len(), |p| at + p);
            let head = String::from_utf8_lossy(&got[at..end]).into_owned();
            let size: Option<usize> = head.split_whitespace().nth(2).and_then(|s| s.parse().ok());
            let Some(size) = size else {
                texts.push(String::new());
                at = (end + 1).min(got.len());
                continue;
            };
            let body = got.get(end + 1..end + 1 + size).unwrap_or(&[]);
            texts.push(String::from_utf8_lossy(body).into_owned());
            at = (end + size + 2).min(got.len());
        }
    }

    /// The first answer `ask` gives over the versions, newest first.
    fn first(&self, ask: &dyn Fn(&str) -> Option<String>) -> Option<String> {
        self.load_revisions();
        let store = self.revisions.borrow();
        let (revs, rel) = store.as_ref()?;
        for i in 0..revs.len() {
            if i >= self.texts.borrow().len() {
                self.load_chunk(i, revs, rel);
            }
            let found = ask(&self.texts.borrow()[i]);
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
        self.first(&|text| {
            blocks(text)
                .into_iter()
                .find(|(k, body, _)| k == key && block_digest(body) == sha)
                .map(|(_, body, _)| body)
        })
    }

    pub(super) fn section(&self, task: &str, sha: &str) -> Option<String> {
        self.first(&|text| {
            task_sections(text)
                .remove(task)
                .filter(|sec| digest(sec.as_bytes()) == sha)
        })
    }
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

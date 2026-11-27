//! The digest index of plan.md's versions kept on disk (451 T465): for each commit it covers, which (key, digest) each block and
//! task section had, so a process that asks where an earlier text is reads one file where it fetched and parsed every version.
//!
//! WHY: after T457 each process still indexed every version its first far-walking question reached - about 5 s of 477 versions
//! in each of a landing's tick checks, `plan push` and the push table's plan row, measured 2026-11-27, growing with every commit.
//!
//! WHAT IT HOLDS: digests only, never a text. One line a commit (its id is its line's place), then one line a distinct (key,
//! digest) with the ids of the commits holding it as runs (`0-24,30`): a 1 MB plan.md of 477 versions is about 79,500 (key, digest)
//! entries but only a few thousand distinct ones, so the file stays small where a row a version and key would be about 12 MB. A text
//! is read from git only for the one version a question returns.
//!
//! WHY IT IS NEVER STALE: a commit's plan.md never changes, so an entry, once true, stays true; the index can only be incomplete,
//! and an incomplete one costs a fetch. Two things could break that, and each is closed: a version that could not be read (a
//! failed or truncated `cat-file`, a commit where the path is gone) is never written, so a passing failure is not kept; and a
//! parser that digests differently (a later `blocks`, `task_sections` or archive rule) is caught by the file's header, the stamp
//! of the code that computes a digest (451 T474, `sections/digests.rs`: the hash of that file and of the files it compiles in,
//! `Cargo.lock` among them, held to reaching nothing else by its test), so a file another digest code wrote is read as nothing -
//! never merged, never mixed (pool trees share the git directory). Each load also re-parses one commit the file covers (the
//! canary) and drops the file on any difference: a sample of what no stamp names (the toolchain, a dependency's features).
//!
//! WRITTEN by the reader, through a temporary file and a rename, after merging what is on disk then: two processes racing lose at
//! most the loser's additions, a re-index, never a wrong answer.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use super::super::sections::digest;
use super::Version;

const DIR: &str = "plan-index";
const HEADER: &str = "l7r plan-index 1";

/// The header line: the format and the stamp of the code that computes the digests.
fn header() -> &'static str {
    static LINE: std::sync::LazyLock<String> =
        std::sync::LazyLock::new(|| header_of(&super::super::sections::digests::stamp()));
    &LINE
}

/// The header an index written by the digest code stamped `stamp` carries.
fn header_of(stamp: &str) -> String {
    format!("{HEADER} {stamp}")
}

/// (key -> digest -> the ids of the commits holding it, ascending).
type Holders = HashMap<String, HashMap<String, Vec<u32>>>;

/// The covered commits and, for blocks and sections apart, which commits held each (key, digest).
#[derive(Default, Debug, PartialEq, Eq)]
pub(super) struct Index {
    commits: Vec<String>,
    ids: HashMap<String, u32>,
    blocks: Holders,
    sections: Holders,
    /// Whether this process added a commit the file on disk may not hold.
    pub(super) dirty: bool,
}

/// The file of the index of `rel` (plan.md's path in the repository) in the common git directory `git_dir`.
pub(super) fn file(git_dir: &Path, rel: &str) -> PathBuf {
    let name = rel.replace('%', "%25").replace('/', "%2F");
    git_dir.join(DIR).join(format!("{name}.idx"))
}

impl Index {
    fn holders(&self, block: bool) -> &Holders {
        if block {
            &self.blocks
        } else {
            &self.sections
        }
    }

    /// The id of `rev` where the index covers it.
    pub(super) fn covers(&self, rev: &str) -> Option<u32> {
        self.ids.get(rev).copied()
    }

    /// The commit added last.
    pub(super) fn last_added(&self) -> Option<&str> {
        self.commits.last().map(String::as_str)
    }

    /// Whether the version `id` held `key` (a block's key when `block`, else a task) at the digest `sha`.
    pub(super) fn holds(&self, block: bool, key: &str, sha: &str, id: u32) -> bool {
        self.holders(block)
            .get(key)
            .and_then(|shas| shas.get(sha))
            .is_some_and(|ids| ids.binary_search(&id).is_ok())
    }

    fn push(&mut self, rev: &str) -> u32 {
        let id = u32::try_from(self.commits.len()).unwrap_or(u32::MAX);
        self.commits.push(rev.to_owned());
        self.ids.insert(rev.to_owned(), id);
        id
    }

    /// Cover `rev`, read as `version`; a key that could not be written on its line leaves the commit out (an incomplete index).
    pub(super) fn add(&mut self, rev: &str, version: &Version) {
        let keys = version.blocks.keys().chain(version.sections.keys());
        if self.ids.contains_key(rev) || keys.into_iter().any(|k| k.contains('\n')) {
            return;
        }
        let id = self.push(rev);
        for (holders, entries) in [
            (&mut self.blocks, &version.blocks),
            (&mut self.sections, &version.sections),
        ] {
            for (key, (sha, _)) in entries {
                let shas = holders.entry(key.to_string()).or_default();
                shas.entry(sha.to_string()).or_default().push(id);
            }
        }
        self.dirty = true;
    }

    /// Take in every commit `other` covers that this does not; the new ids follow every id held, so each list stays ascending.
    pub(super) fn absorb(&mut self, other: Self) {
        let map: Vec<Option<u32>> = other
            .commits
            .iter()
            .map(|c| (!self.ids.contains_key(c)).then(|| self.push(c)))
            .collect();
        for (holders, theirs) in [
            (&mut self.blocks, other.blocks),
            (&mut self.sections, other.sections),
        ] {
            for (key, shas) in theirs {
                for (sha, ids) in shas {
                    let new: Vec<u32> = ids.iter().filter_map(|i| map[*i as usize]).collect();
                    if !new.is_empty() {
                        let mine = holders.entry(key.clone()).or_default();
                        mine.entry(sha).or_default().extend(new);
                    }
                }
            }
        }
    }

    /// Every (block?, key, digest) the version `id` held, sorted: what the canary compares.
    pub(super) fn entries_of(&self, id: u32) -> Vec<(bool, String, String)> {
        let mut out = Vec::new();
        for block in [true, false] {
            for (key, shas) in self.holders(block) {
                for (sha, ids) in shas {
                    if ids.binary_search(&id).is_ok() {
                        out.push((block, key.clone(), sha.clone()));
                    }
                }
            }
        }
        out.sort();
        out
    }

    pub(super) fn encode(&self) -> String {
        let mut out = format!("{}\n", header());
        for commit in &self.commits {
            let _ = writeln!(out, "c {commit}");
        }
        for (tag, block) in [("b", true), ("s", false)] {
            for (key, shas) in self.holders(block) {
                for (sha, ids) in shas {
                    let _ = writeln!(out, "{tag} {sha} {} {key}", runs(ids));
                }
            }
        }
        out
    }

    /// The index a file holds, or None for anything but what [`Index::encode`] writes.
    pub(super) fn decode(text: &str) -> Option<Self> {
        let mut lines = text.split('\n');
        if lines.next()? != header() {
            return None;
        }
        let mut index = Self::default();
        for line in lines.filter(|l| !l.is_empty()) {
            let (tag, rest) = line.split_once(' ')?;
            if tag == "c" {
                if index.ids.contains_key(rest) {
                    return None;
                }
                index.push(rest);
                continue;
            }
            let block = match tag {
                "b" => true,
                "s" => false,
                _ => return None,
            };
            let mut parts = rest.splitn(3, ' ');
            let (sha, runs, key) = (parts.next()?, parts.next()?, parts.next()?);
            let ids = unruns(runs, index.commits.len())?;
            let holders = if block {
                &mut index.blocks
            } else {
                &mut index.sections
            };
            let shas = holders.entry(key.to_owned()).or_default();
            if shas.insert(sha.to_owned(), ids).is_some() {
                return None;
            }
        }
        Some(index)
    }
}

/// Ascending ids as runs: `0-24,30`.
fn runs(ids: &[u32]) -> String {
    let mut out = String::new();
    let mut i = 0;
    while i < ids.len() {
        let mut j = i;
        while j + 1 < ids.len() && ids[j + 1] == ids[j] + 1 {
            j += 1;
        }
        let sep = if out.is_empty() { "" } else { "," };
        let _ = if i == j {
            write!(out, "{sep}{}", ids[i])
        } else {
            write!(out, "{sep}{}-{}", ids[i], ids[j])
        };
        i = j + 1;
    }
    out
}

/// The ids of `runs`, each below `count` and ascending, or None.
fn unruns(runs: &str, count: usize) -> Option<Vec<u32>> {
    let mut ids: Vec<u32> = Vec::new();
    for run in runs.split(',') {
        let (from, to) = run.split_once('-').unwrap_or((run, run));
        let (from, to): (u32, u32) = (from.parse().ok()?, to.parse().ok()?);
        if from > to || ids.last().is_some_and(|l| *l >= from) || to as usize >= count {
            return None;
        }
        ids.extend(from..=to);
    }
    Some(ids)
}

/// The index on disk at `path`; an empty one where none is, or none readable.
pub(super) fn read(path: &Path) -> Index {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|text| Index::decode(&text))
        .unwrap_or_default()
}

/// The file of the text `key` (a block's key when `block`, else a task) had at `commit`, beside the index `file`: a question's
/// answer, kept so that a later process reads no version for it. Its commit makes it immutable as the index is.
pub(super) fn text_file(file: &Path, commit: &str, block: bool, key: &str) -> PathBuf {
    let kind = if block { "b" } else { "s" };
    let plan = file.file_name().unwrap_or_default().to_string_lossy();
    let name = digest(format!("{plan}\0{commit}\0{kind}\0{key}").as_bytes());
    file.with_file_name("texts").join(format!("{name}.txt"))
}

/// Keep `text` at `path` where it is not kept already.
pub(super) fn keep_text(path: &Path, text: &str) {
    if std::fs::read_to_string(path).ok().as_deref() != Some(text) {
        put(path, text);
    }
}

/// Write `index` at `path` merged with what is there now, through a temporary file and a rename; a failure leaves the index
/// incomplete. The merge is checked by the caller's canary first (`on_disk`).
pub(super) fn save(path: &Path, index: &mut Index, on_disk: Index) {
    index.absorb(on_disk);
    index.dirty = false;
    put(path, &index.encode());
}

/// Write `contents` at `path` through a temporary file and a rename; a failure writes nothing.
fn put(path: &Path, contents: &str) {
    let Some(dir) = path.parent() else { return };
    let _ = std::fs::create_dir_all(dir);
    let tmp = dir.join(format!(
        ".{}.{}.{}.tmp",
        path.file_name().unwrap_or_default().to_string_lossy(),
        std::process::id(),
        unique()
    ));
    if std::fs::write(&tmp, contents).is_ok() && std::fs::rename(&tmp, path).is_err() {
        let _ = std::fs::remove_file(&tmp);
    }
}

/// A number no other temporary file of this process has had.
fn unique() -> u64 {
    static NEXT: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
}

/// The version's (block?, key, digest) entries, sorted, for the canary.
pub(super) fn entries(version: &Version) -> Vec<(bool, String, String)> {
    let mut out: Vec<(bool, String, String)> =
        [(true, &version.blocks), (false, &version.sections)]
            .into_iter()
            .flat_map(|(block, map)| {
                map.iter()
                    .map(move |(key, (sha, _))| (block, key.to_string(), sha.to_string()))
            })
            .collect();
    out.sort();
    out
}

#[cfg(test)]
mod tests;

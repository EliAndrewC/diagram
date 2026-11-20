//! A map's cache entry (feature 449 T221, from `specs/449-rust-codebase/derivations/T219-pipeline.md`, Keeps 4 and 5): its artifacts and
//! its META, which names the engine's id, whether the picture was skipped, the spec's record (its stat and digest), one record an artifact
//! and the entry's key. Its reads are not in it: they are the read table's rows, which name the map.
//!
//! PUBLISHED ATOMICALLY, META LAST: each artifact is renamed into the entry, the meta written to a temporary name, and the meta renamed
//! into place only after the read table names the map in each of its reads' rows - so a reader sees a whole entry or none, and an entry
//! that exists has every read it depends on watched. REMOVED DURABLY: the meta first (an entry without one is none), then the rest, then
//! the directory synced, so a row's new digest is never written over an entry still standing.
//!
//! Research: plumbing - NONE: the cache's bookkeeping, deciding nothing about a map

use std::os::unix::fs::MetadataExt as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::stat::Stat;

/// The meta's file name in an entry.
pub const META: &str = "meta.json";

/// A record of the map's spec: its path from the tree's root, its stat, when it was hashed and its digest.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Record {
    pub path: String,
    pub stat: Stat,
    pub hashed: i128,
    pub digest: String,
}

/// An artifact's record: its file name and what its file in the entry was when published - size, mtime and inode, which the map
/// folder's copy shares (a hard link of it). Its ctime is not held: linking a file moves its ctime, and the folder's link is made after.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Artifact {
    pub name: String,
    pub size: u64,
    pub mtime: i128,
    pub ino: u64,
}

impl Artifact {
    /// Whether `stat` is this artifact's file.
    #[must_use]
    pub fn is(&self, stat: &Stat) -> bool {
        matches!(stat, Stat::Present { size, mtime, ino, .. }
            if *size == self.size && *mtime == self.mtime && *ino == self.ino)
    }
}

/// An entry's meta.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Meta {
    /// The engine's name and its id this entry was drawn by.
    pub engine: String,
    pub engine_id: String,
    /// Whether the picture was skipped (`DIAGRAM_SKIP_RENDER=1`): such an entry serves only a run that skips it too.
    pub skip_render: bool,
    pub spec: Record,
    pub artifacts: Vec<Artifact>,
    /// The entry's identity: the engine id, the switch, the spec's digest, the font set and each read's path and digest, hashed.
    pub key: String,
    /// How many reads the engine reported (spec apart).
    pub reads: usize,
}

fn stat_json(s: &Stat) -> Value {
    json!(s.cells())
}

fn stat_of(v: &Value) -> Option<Stat> {
    let cells: Vec<&str> = v.as_array()?.iter().filter_map(Value::as_str).collect();
    Stat::from_cells(&cells)
}

impl Meta {
    /// The meta as its file holds it.
    #[must_use]
    pub fn json(&self) -> String {
        let artifacts: Vec<Value> = self
            .artifacts
            .iter()
            .map(|a| json!([a.name, a.size, a.mtime.to_string(), a.ino]))
            .collect();
        json!({
            "engine": self.engine, "engine_id": self.engine_id, "skip_render": self.skip_render,
            "spec": {"path": self.spec.path, "stat": stat_json(&self.spec.stat), "hashed": self.spec.hashed.to_string(),
                     "digest": self.spec.digest},
            "artifacts": artifacts, "key": self.key, "reads": self.reads,
        })
        .to_string()
    }

    /// The meta read from its file's text, or None where it does not read.
    #[must_use]
    pub fn parse(text: &str) -> Option<Self> {
        let v: Value = serde_json::from_str(text).ok()?;
        let s = v.get("spec")?;
        let artifacts = v
            .get("artifacts")?
            .as_array()?
            .iter()
            .map(|a| {
                Some(Artifact {
                    name: a.get(0)?.as_str()?.to_owned(),
                    size: a.get(1)?.as_u64()?,
                    mtime: a.get(2)?.as_str()?.parse().ok()?,
                    ino: a.get(3)?.as_u64()?,
                })
            })
            .collect::<Option<Vec<_>>>()?;
        Some(Self {
            engine: v.get("engine")?.as_str()?.to_owned(),
            engine_id: v.get("engine_id")?.as_str()?.to_owned(),
            skip_render: v.get("skip_render")?.as_bool()?,
            spec: Record {
                path: s.get("path")?.as_str()?.to_owned(),
                stat: stat_of(s.get("stat")?)?,
                hashed: s.get("hashed")?.as_str()?.parse().ok()?,
                digest: s.get("digest")?.as_str()?.to_owned(),
            },
            artifacts,
            key: v.get("key")?.as_str()?.to_owned(),
            reads: usize::try_from(v.get("reads")?.as_u64()?).ok()?,
        })
    }
}

/// `dir` synced, so a rename or removal in it is durable.
fn sync_dir(dir: &Path) -> std::io::Result<()> {
    std::fs::File::open(dir)?.sync_all()
}

/// `bytes` written at `path` atomically: a temporary file beside it, synced, renamed over it, the directory synced.
///
/// # Errors
/// The file or its directory cannot be written.
pub fn replace(path: &Path, bytes: &[u8]) -> std::io::Result<()> {
    let dir = path.parent().unwrap_or(Path::new("."));
    std::fs::create_dir_all(dir)?;
    let tmp = temp_beside(path);
    let mut f = std::fs::File::create(&tmp)?;
    std::io::Write::write_all(&mut f, bytes)?;
    f.sync_all()?;
    std::fs::rename(&tmp, path)?;
    sync_dir(dir)
}

/// A temporary name beside `path`: hidden, this process's.
#[must_use]
pub fn temp_beside(path: &Path) -> PathBuf {
    let name = path
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    path.with_file_name(format!(".{name}.{}.tmp", std::process::id()))
}

/// The meta of the entry at `dir`, or None where it has none that reads.
#[must_use]
pub fn read(dir: &Path) -> Option<Meta> {
    Meta::parse(&std::fs::read_to_string(dir.join(META)).ok()?)
}

/// The entry at `dir` removed durably: its meta first, then the rest, then its parent synced. Whether one stood there.
///
/// # Errors
/// The meta or the directory cannot be removed.
pub fn remove(dir: &Path) -> std::io::Result<bool> {
    let meta = dir.join(META);
    let stood = meta.exists();
    if stood {
        std::fs::remove_file(&meta)?;
        sync_dir(dir)?;
    }
    if dir.exists() {
        std::fs::remove_dir_all(dir)?;
        sync_dir(dir.parent().unwrap_or(dir))?;
    }
    Ok(stood)
}

/// `from` linked at `to`: a hard link made under a temporary name beside `to` and renamed over it, so a reader of `to` sees the old file or
/// the new, never none; a copy where the two cannot be linked (another filesystem).
///
/// # Errors
/// Neither a link nor a copy could be made, or the rename failed.
pub fn link(from: &Path, to: &Path) -> std::io::Result<()> {
    let tmp = temp_beside(to);
    let _ = std::fs::remove_file(&tmp);
    if std::fs::hard_link(from, &tmp).is_err() {
        std::fs::copy(from, &tmp)?;
    }
    std::fs::rename(&tmp, to)
}

/// An artifact's record from its file.
///
/// # Errors
/// The file cannot be read.
pub fn artifact(name: &str, path: &Path) -> std::io::Result<Artifact> {
    let m = std::fs::metadata(path)?;
    Ok(Artifact {
        name: name.to_owned(),
        size: m.size(),
        mtime: i128::from(m.mtime()) * 1_000_000_000 + i128::from(m.mtime_nsec()),
        ino: m.ino(),
    })
}

#[cfg(test)]
mod tests;

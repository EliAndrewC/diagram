//! THE GENERATION CACHE (feature 449 T221, the pipeline's phase, T157's third landing): rebuilt from
//! `specs/449-rust-codebase/derivations/T219-pipeline.md` (judged SOUND), never from the Python cache it replaces (`pipeline/gencache.py`,
//! `regen.py`, deleted). `make map MAP=<folder|spec>` asks it of one map, `make map MAP=--all` of every live map, and the review gate asks
//! [`is_current`] in process.
//!
//! WHAT RE-KEYS A MAP (Keep 1): its spec, any file its engine reported reading - a file it looked for and did not find among them (a miss is
//! a read: created later, it regenerates the map) - its engine's binary, and (a Mode A sheet) the font set. Served from the cache
//! otherwise. NEVER A STALE MAP (Keep 2), the contract's expensive failure:
//!
//! - every read is a row of ONE READ TABLE a clone ([`table`]), held once a run however many maps read it: its stat (size, mtime, ctime,
//!   inode) compared, its bytes hashed only when the stat moved or the file did not settle before its last hashing (the racy-file rule,
//!   held against the filesystem's own clock, [`stat`]); a digest that moved removes - durably, first - the entry of every map the row
//!   names, and only then does the row take the new digest (Keep 3);
//! - a published map is in the row of each of its reads before its meta is renamed: the run writes the table, THEN renames the metas;
//! - A READ FIRST REPORTED ON A MISS (the second judgment on the derivation, 2026-11-19) is hashed after the engine ran, so it is held by
//!   the racy-file rule against the ENGINE'S START, a file's time taken on the filesystem's clock just before the engine was started: a
//!   read (the spec among them) whose mtime or ctime is not older than that start, or an absent read whose nearest standing directory
//!   moved since, may have changed while the engine read it, and the entry is not published - its artifacts are linked into the map's
//!   folder, and the next run draws it again. No entry is recorded with a digest of content it was not built from;
//! - the engine is its binary's build id, taken once a run ([`engine`], Keep 4); an engine that cannot be named fresh draws nothing.
//!
//! PUBLISHED ATOMICALLY, META LAST ([`entry`], Keep 5): the engine draws into a staging folder, never into the map's; each artifact is
//! renamed into the entry and hard-linked into the map's folder under a temporary name renamed over the old file; the meta goes last. A
//! frozen exhibit is never keyed or regenerated (Keep 6); every map is found by the one pool walk (Keep 7); a spec edit alone re-keys its
//! map (Keep 8, the stale compound T157's scoping found). One run writes the table at a time: the run holds the table's lock throughout.
//!
//! THE TABLE IS THE ENTRIES' WATCH: a table that is gone, or that does not read, throws every entry away (a miss each), never trusting an
//! entry whose reads nothing watches.
//!
//! Research: plumbing - NONE: decides which maps are drawn again, never how a map is drawn

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use crate::counts::Counts;
use crate::walk::{Kind, Map, LIVE};
use engine::{Binaries, Engine};
use table::{Row, RowKind, Table};

mod draw;
pub mod engine;
pub mod entry;
pub mod fonts;
mod hold;
pub mod phases;
pub mod stat;
pub mod table;

/// The cache's directory under the tree's root (gitignored with `.gencache/`).
pub const DIR: &str = ".gencache/rust";
/// The read table's file in it.
pub const TABLE: &str = "reads.tsv";
/// The lock one run holds.
pub const LOCK: &str = "lock";
/// The entries' directory in it: `<tier>/<name>/` each.
pub const ENTRIES: &str = "entries";
/// The staging folders an engine draws into.
pub const STAGING: &str = "staging";

/// What became of a map.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Verdict {
    /// Served from its entry.
    Cached,
    /// Drawn again and published, with why it was owed.
    Regenerated(String),
    /// Drawn again, its artifacts in its folder, but not published: why.
    Unpublished(String),
    /// A frozen exhibit: never regenerated.
    Frozen,
    /// Not drawn: why.
    Failed(String),
}

/// One map's outcome: the map's folder from the root, its verdict, and what its engine said on stderr.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Outcome {
    pub map: String,
    pub verdict: Verdict,
    pub said: String,
}

/// How a run is set: whether the picture is skipped (`DIAGRAM_SKIP_RENDER=1`), the font roots ([`fonts::system_roots`] in a run), and
/// how long a run waits for another's lock, in seconds (an hour in a run).
#[derive(Clone, Debug)]
pub struct Options {
    pub skip_render: bool,
    pub font_roots: Vec<PathBuf>,
    pub lock_wait: f64,
    /// The environment each map's Phase lines are filed by (feature 451 T153, [`phases`]): the process's, a test's own.
    pub env: fn(&str) -> Option<String>,
}

/// No render switch, no fonts, no wait, no environment: a test's starting point.
impl Default for Options {
    fn default() -> Self {
        Self {
            skip_render: false,
            font_roots: Vec::new(),
            lock_wait: 0.0,
            env: |_| None,
        }
    }
}

impl Options {
    /// This process's: the render switch and the font roots as they stand.
    #[must_use]
    pub fn current() -> Self {
        Self {
            skip_render: matches!(std::env::var("DIAGRAM_SKIP_RENDER").as_deref(), Ok("1")),
            lock_wait: 3600.0,
            font_roots: fonts::system_roots(),
            env: l7r_shared::env::opt,
        }
    }
}

/// A map's name in the table and in the entries: `<tier>/<name>` (every live map is in the live tree).
#[must_use]
pub fn map_id(m: &Map) -> String {
    format!("{}/{}", m.tier, m.name)
}

/// The file a live map is drawn from: a hamlet's spec, a generated compound's program, a hand sheet's svg.
#[must_use]
pub fn spec_of(m: &Map) -> Option<PathBuf> {
    match m.kind {
        Kind::Hamlet => Some(m.file(".spec.json")),
        Kind::Compound => Some(m.file(".compound.json")),
        Kind::HandSheet => Some(m.file(".svg")),
        Kind::Frozen | Kind::Report => None,
    }
}

/// `path` as the table names it: from the root where it is under it, else whole.
fn rel(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

/// The file a table path names.
fn abs(root: &Path, path: &str) -> PathBuf {
    if path.starts_with('/') {
        PathBuf::from(path)
    } else {
        root.join(path)
    }
}

/// An I/O error said with the path it concerns: `.map_err(at(&path))`.
pub(crate) fn at(p: &Path) -> impl Fn(std::io::Error) -> String + '_ {
    move |e| format!("{}: {e}", p.display())
}

/// A file's digest and the blocks hashed for it: `-` for an absent one.
fn digest(path: &Path) -> (String, u64) {
    std::fs::read(path).map_or_else(
        |_| ("-".to_owned(), 0),
        |b| {
            (
                l7r_shared::sha256::hex(&b),
                (b.len() as u64).div_ceil(engine::BLOCK),
            )
        },
    )
}

/// One run over a set of maps: its table, lock and clock, the engines' ids, and what it removed and owes to publish.
struct Run<'a> {
    /// The run's make target, which each map's Phase lines name ([`phases`]).
    make: String,
    root: PathBuf,
    dir: PathBuf,
    table: Table,
    clock: i128,
    opts: Options,
    binaries: &'a mut dyn Binaries,
    ids: BTreeMap<Engine, Result<String, String>>,
    /// Each engine's binary, as its id was read from.
    paths: BTreeMap<Engine, PathBuf>,
    counts: &'a mut Counts,
    /// The read rows held this run (their digest stands for their file now).
    held: BTreeSet<String>,
    /// The maps whose entries the hold removed, with why.
    removed: BTreeMap<String, String>,
    /// The metas written under a temporary name, renamed after the table: (temporary, final).
    pending: Vec<(PathBuf, PathBuf)>,
}

impl Run<'_> {
    fn count(&mut self, kind: &'static str, n: usize) {
        self.counts.add(LIVE, kind, n);
    }

    fn entry_dir(&self, id: &str) -> PathBuf {
        self.dir.join(ENTRIES).join(id)
    }

    /// The engine's id, read once a run.
    fn id(&mut self, e: Engine) -> Result<String, String> {
        if let Some(id) = self.ids.get(&e) {
            return id.clone();
        }
        self.count("engine_id", 1);
        let id = self.binaries.binary(e).and_then(|b| {
            let (id, bytes) = engine::identity(&b)?;
            self.paths.insert(e, b);
            self.counts.add(
                LIVE,
                "hash_block",
                usize::try_from(bytes.div_ceil(engine::BLOCK)).unwrap_or(0),
            );
            Ok(id)
        });
        self.ids.insert(e, id.clone());
        id
    }

    /// The entry of `id` removed durably, and why remembered.
    fn remove_entry(&mut self, id: &str, why: &str) -> Result<(), String> {
        let dir = self.entry_dir(id);
        if entry::remove(&dir).map_err(at(&dir))? {
            self.count("entry_remove", 1);
        }
        self.removed
            .entry(id.to_owned())
            .or_insert_with(|| why.to_owned());
        Ok(())
    }

    /// The end of the run: the table written where a row changed, THEN each published meta renamed into place.
    fn finish(&mut self) -> Result<(), String> {
        if self.table.changed {
            self.count("row_write", self.table.rows.len());
            self.count("rename", 1);
            let table = self.dir.join(TABLE);
            self.table.write(&table).map_err(at(&table))?;
        }
        for (tmp, meta) in std::mem::take(&mut self.pending) {
            // an entry the run itself removed after drawing it (a read that moved under a later map) is not published
            if tmp.exists() {
                self.count("rename", 1);
                std::fs::rename(&tmp, &meta).map_err(at(&meta))?;
                if let Some(d) = meta.parent() {
                    let _ = std::fs::File::open(d).and_then(|f| f.sync_all());
                }
            }
        }
        Ok(())
    }
}

/// The table at `dir`, its rows counted as parsed: None where there is none that reads.
fn read_table(dir: &Path, counts: &mut Counts) -> Option<Table> {
    let text = std::fs::read_to_string(dir.join(TABLE)).ok()?;
    counts.add(LIVE, "file_read", 1);
    let t = Table::parse(&text)?;
    counts.add(LIVE, "record", t.rows.len());
    Some(t)
}

/// Draw or serve each of `maps` (the live ones; a frozen exhibit is reported, never keyed), with `every` true where they are every live
/// map of the pool (every row of the table is held then; otherwise only the rows naming them). The table's lock is held throughout.
///
/// # Errors
/// The cache's directory, lock, table or an entry cannot be written: nothing a map's engine said (that is its outcome).
pub fn run(
    root: &Path,
    maps: &[Map],
    every: bool,
    binaries: &mut dyn Binaries,
    counts: &mut Counts,
    opts: Options,
) -> Result<Vec<Outcome>, String> {
    let root = std::fs::canonicalize(root).map_err(at(root))?;
    let dir = root.join(DIR);
    let io = at(&dir);
    std::fs::create_dir_all(&dir).map_err(&io)?;
    let wait = opts.lock_wait;
    let lock = l7r_shared::tool::flock_within(&dir.join(LOCK), wait)
        .map_err(&io)?
        .ok_or_else(|| {
            format!(
                "{}: another run held the cache's lock past {wait} s",
                dir.display()
            )
        })?;
    counts.add(LIVE, "lock", 1);
    let clock = stat::fs_clock(&dir.join(LOCK)).map_err(&io)?;
    let table = if let Some(t) = read_table(&dir, counts) {
        t
    } else {
        // no table that reads: no entry is watched, so none is trusted
        let entries = dir.join(ENTRIES);
        if entries.exists() {
            std::fs::remove_dir_all(&entries).map_err(&io)?;
        }
        Table {
            rows: BTreeMap::new(),
            changed: true,
        }
    };
    let mut r = Run {
        make: l7r_shared::make::outermost_goal(Path::new("/proc"), std::process::id())
            .unwrap_or_default(),
        root,
        dir: dir.clone(),
        table,
        clock,
        opts,
        binaries,
        ids: BTreeMap::new(),
        paths: BTreeMap::new(),
        counts,
        held: BTreeSet::new(),
        removed: BTreeMap::new(),
        pending: Vec::new(),
    };
    let mut seen = BTreeSet::new();
    let maps: Vec<&Map> = maps.iter().filter(|m| seen.insert(m.rel())).collect();
    r.hold(&maps, every)?;
    if maps.iter().any(|m| m.kind.is_sheet()) {
        r.font_rows();
    }
    let mut out = Vec::new();
    for m in maps {
        out.push(r.map(m)?);
    }
    r.finish()?;
    drop(lock);
    Ok(out)
}

/// Whether the live map `m` would be served from the cache now, asked READ-ONLY (the review gate's question, feature 240 FR-005, in
/// process since T221): no lock, no row refreshed, no entry removed, no engine built; any doubt - no table, no entry, an engine that
/// cannot be named fresh, a read or font that moved, an artifact not in the map's folder - answers no.
#[must_use]
pub fn is_current(root: &Path, m: &Map, binaries: &mut dyn Binaries, skip_render: bool) -> bool {
    current(root, m, binaries, skip_render).unwrap_or(false)
}

fn current(root: &Path, m: &Map, binaries: &mut dyn Binaries, skip_render: bool) -> Option<bool> {
    let root = std::fs::canonicalize(root).ok()?;
    let dir = root.join(DIR);
    let table = Table::parse(&std::fs::read_to_string(dir.join(TABLE)).ok()?)?;
    let id = map_id(m);
    let meta = entry::read(&dir.join(ENTRIES).join(&id))?;
    let (engine_id, _) = engine::identity(&binaries.binary(Engine::of(m.kind)?).ok()?).ok()?;
    let spec = spec_of(m)?;
    let held = |path: &Path, s: &stat::Stat, hashed: i128, digest: &str| {
        let now = stat::stat(path);
        (now == *s && now.settled_before(hashed)) || self::digest(path).0 == digest
    };
    let fine = meta.engine_id == engine_id
        && meta.skip_render == skip_render
        && held(&spec, &meta.spec.stat, meta.spec.hashed, &meta.spec.digest)
        && meta
            .artifacts
            .iter()
            .all(|a| a.is(&stat::stat(&m.dir.join(&a.name))))
        && table
            .rows
            .iter()
            .filter(|(_, r)| r.names(&id))
            .all(|(p, r)| {
                let at = abs(&root, p);
                if r.kind.is_font() {
                    stat::stat(&at) == r.stat
                } else {
                    held(&at, &r.stat, r.hashed, &r.digest)
                }
            });
    Some(fine)
}

impl Run<'_> {
    /// The font rows: walked from the roots where the table holds none and a sheet is in the run (each directory listed, each name read).
    fn font_rows(&mut self) {
        if self.table.rows.values().any(|r| r.kind.is_font()) {
            return;
        }
        let (set, listed, names) = fonts::walk(&self.opts.font_roots);
        self.count("dir_list", listed);
        self.count("dir_entry", names);
        for (p, kind) in set {
            let path = p.to_string_lossy().into_owned();
            if table::holdable(&path) {
                let row = Row::new(kind, stat::stat(&p), self.clock, String::new());
                self.table.rows.insert(path, row);
                self.table.changed = true;
            }
        }
    }

    /// The font rows' share of a sheet's key: each row's path and stat, hashed.
    fn font_set_id(&self) -> String {
        let text = self
            .table
            .rows
            .iter()
            .filter(|(_, r)| r.kind.is_font())
            .fold(String::new(), |mut t, (p, r)| {
                let _ = writeln!(t, "{p}\t{}", r.stat.cells().join("\t"));
                t
            });
        l7r_shared::sha256::hex(text.as_bytes())
    }

    /// The rows of a read set, kept for the map `id`: each row added or refreshed, a row whose digest moves first removing every other
    /// map's entry it names (Keep 3), and the map added to its list; a sheet's to every font row too.
    fn keep_rows(
        &mut self,
        id: &str,
        reads: &[(String, stat::Stat, String)],
        t0: i128,
        sheet: bool,
    ) -> Result<(), String> {
        for (path, now, digest) in reads {
            let moved: Vec<String> = match self.table.rows.get(path) {
                Some(row) if row.digest != *digest => {
                    row.maps().iter().map(|m| (*m).to_owned()).collect()
                }
                _ => Vec::new(),
            };
            if !moved.is_empty() {
                self.count("list_read", 1);
            }
            for other in moved.iter().filter(|m| *m != id) {
                self.remove_entry(other, &format!("{path} changed"))?;
            }
            self.count("row_update", 1);
            let row = self
                .table
                .rows
                .entry(path.clone())
                .or_insert_with(|| Row::new(RowKind::Read, *now, t0, digest.clone()));
            if row.digest != *digest || row.stat != *now {
                if row.digest != *digest {
                    row.clear();
                }
                (row.stat, row.hashed, row.digest) = (*now, t0, digest.clone());
            }
            row.add(id);
            self.table.changed = true;
        }
        if sheet {
            for row in self.table.rows.values_mut().filter(|r| r.kind.is_font()) {
                self.counts.add(LIVE, "row_update", 1);
                self.table.changed |= row.add(id);
            }
        }
        Ok(())
    }
}

#[cfg(test)]
pub(crate) mod tests;

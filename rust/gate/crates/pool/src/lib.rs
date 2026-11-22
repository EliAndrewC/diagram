//! The pool walk and the pool index (feature 449 T220, the pipeline's phase, T157's second landing): rebuilt from
//! `specs/449-rust-codebase/derivations/T219-pipeline.md` (judged SOUND), never from the Python pipeline it replaces. One walk of both
//! pool trees ([`walk`]), which every consumer of the pool asks in place of listing it on its own (the derivation's Keep 7) - the review
//! tools, the probe, the model trial, the work-budget review, the review gate (through `l7r-gate pool find`), the Mode A engine's pool
//! sweep - and the index it writes ([`index`]); and (T221) the generation cache ([`cache`]: the read table, the entries, the engines' ids)
//! and the one driver every pool map is drawn by ([`map`], `make map MAP=<folder|spec>`).
//!
//! The commands, `l7r-gate pool <command>` in the gate and `l7r-pool <command>` as this crate's own program:
//!
//! - `index`: write `pool/index.html` where it differs; what the walk could not classify is printed on stderr.
//! - `find <map> [<suffix>]`: the map's kind tag and folder; with a suffix, the folder's `<map><suffix>` where the listing holds it.
//!   Exit 1 where there is none.
//! - `list`: every map folder, `tree tier name kind`, then what was reported.
//! - `map <target>... | map --all` (T221): the maps drawn or served by the generation cache, `CACHED`, `REGENERATED` or `FROZEN` each.
//! - `maps [--scope auto|reference|all] [--tier <row>]` (T252): `make maps`, the one self-scoping command over the tiers' draws and
//!   checks ([`maps`]), its scope read from how the last run went.
//! - `counts <tree>` (a counting build alone): the pipeline's counted work on that tree - the walk, the index and the cache over every
//!   live map - on the SECOND of two runs back to back (the derivation's warm all-hit run; the first publishes what was not cached), one
//!   JSON line with its `total`.
//!
//! Research: plumbing - NONE: finds the pool's maps and lists them, and decides nothing about a place

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

pub mod cache;
pub mod counts;
pub mod index;
pub mod map;
pub mod maps;
pub mod walk;

pub use walk::{walk, Kind, Map, Walk, DECLARATION, LEGACY, LIVE, TREES};

const USAGE: &str =
    "usage: pool index | find <map> [<suffix>] | list | map <map>... | map --all | maps [--scope auto|reference|all] [--tier <row>] | counts <tree> (a counting build)\n";

/// What a command says: `(stdout, stderr, exit code)`.
pub type Said = (String, String, i32);

/// Each report, a line.
fn reported(w: &Walk) -> String {
    w.reports.iter().fold(String::new(), |mut out, r| {
        let _ = writeln!(out, "pool walk: {r}");
        out
    })
}

/// `index`: the page written where it differs.
fn index_cli(root: &Path) -> Said {
    let mut w = walk(root);
    let n = w.maps.len();
    match index::write(root, &mut w) {
        Ok(written) => (
            format!(
                "pool index: {} ({n} maps)\n",
                if written {
                    format!("{} written", index::INDEX)
                } else {
                    format!("{} unchanged", index::INDEX)
                }
            ),
            reported(&w),
            0,
        ),
        Err(e) => (
            String::new(),
            format!(
                "{}pool index: {} could not be written: {e} - run it from the repository's root, where pool/ is\n",
                reported(&w),
                index::INDEX
            ),
            1,
        ),
    }
}

/// `find <map> [<suffix>]`.
fn find_cli(root: &Path, name: &str, suffix: Option<&str>) -> Said {
    let w = walk(root);
    let Some(map) = w.folder(name) else {
        return (
            String::new(),
            format!("pool find: no map folder named {name} in either pool tree\n"),
            1,
        );
    };
    match suffix {
        None => (
            format!("{}\t{}\n", map.kind.tag(), map.rel()),
            String::new(),
            0,
        ),
        Some(s) if map.has(s) => (format!("{}/{name}{s}\n", map.rel()), String::new(), 0),
        Some(s) => (
            String::new(),
            format!("pool find: {} holds no {name}{s}\n", map.rel()),
            1,
        ),
    }
}

/// `list`.
fn list_cli(root: &Path) -> Said {
    let w = walk(root);
    let out = w.maps.iter().fold(String::new(), |mut out, m| {
        let _ = writeln!(out, "{}\t{}\t{}\t{}", m.tree, m.tier, m.name, m.kind.tag());
        out
    });
    (out, reported(&w), 0)
}

/// One run of the whole pipeline, as the counting run does it: the walk, the index's rows composed and compared (nothing written), and
/// the cache over every live map; the run's counts, and the maps it did not serve from the cache.
#[cfg(feature = "counters")]
fn pipeline_pass(
    root: &Path,
    binaries: &mut dyn cache::engine::Binaries,
) -> Result<(counts::Counts, Vec<String>), String> {
    let mut w = walk(root);
    let _ = index::compare(root, &mut w);
    let live: Vec<Map> = w
        .in_tree(LIVE)
        .filter(|m| m.kind.is_live())
        .cloned()
        .collect();
    let outcomes = cache::run(
        root,
        &live,
        true,
        binaries,
        &mut w.counts,
        cache::Options::current(),
    )?;
    let missed = outcomes
        .into_iter()
        .filter(|o| o.verdict != cache::Verdict::Cached)
        .map(|o| format!("{} ({:?})", o.map, o.verdict))
        .collect();
    Ok((w.counts, missed))
}

/// `counts <tree>`: the pipeline run twice back to back and the SECOND run's counts on that tree (the derivation's warm all-hit run: the
/// first publishes whatever was not cached); a map the second did not serve is named on stderr.
#[cfg(feature = "counters")]
fn counts_cli(root: &Path, tree: &str, binaries: &mut dyn cache::engine::Binaries) -> Said {
    if !TREES.contains(&tree) {
        return (
            String::new(),
            format!("pool counts: no tree {tree} - the trees are {LIVE} and {LEGACY}\n"),
            2,
        );
    }
    let second = pipeline_pass(root, binaries).and_then(|_| pipeline_pass(root, binaries));
    let (counts, missed) = match second {
        Ok(c) => c,
        Err(why) => {
            return (
                String::new(),
                format!("pool counts: the generation cache: {why}\n"),
                1,
            )
        }
    };
    let kinds = counts.of(tree);
    let total: u64 = kinds.iter().map(|(_, n)| n).sum();
    let mut line = serde_json::Map::new();
    line.insert("tree".to_owned(), tree.into());
    line.insert("total".to_owned(), total.into());
    for (k, n) in kinds {
        line.insert(k.to_owned(), n.into());
    }
    let err = if missed.is_empty() {
        String::new()
    } else {
        format!("pool counts: the second run did not serve {} from the cache - its count is not the all-hit run's\n", missed.join(", "))
    };
    (format!("{}\n", serde_json::Value::Object(line)), err, 0)
}

/// Whether the map `target` names (its folder, a file in it, or its name) is served by the generation cache now: the review gate's
/// question, asked read-only and building no engine ([`cache::is_current`]); a frozen exhibit or a name no map bears is not.
#[must_use]
pub fn is_current(root: &Path, target: &str) -> bool {
    Currency::new(root).of(target)
}

/// [`is_current`] asked of many maps in one process (449 T231): the pool walked once and each engine's launcher asked once, where a
/// call of [`is_current`] each walks the pool and starts the launcher again - `reviews owed` asks it of every live map on every push.
pub struct Currency {
    root: PathBuf,
    walk: Walk,
    binaries: Remembered,
}

impl Currency {
    /// Over the tree at `root`, its engines named by the launcher, building none.
    #[must_use]
    pub fn new(root: &Path) -> Self {
        Self::with(
            root,
            Box::new(cache::engine::Launcher {
                root: root.to_path_buf(),
                build: false,
            }),
        )
    }

    /// Over the tree at `root`, its engines named by `binaries`.
    #[must_use]
    pub fn with(root: &Path, binaries: Box<dyn cache::engine::Binaries>) -> Self {
        Self {
            root: root.to_path_buf(),
            walk: walk(root),
            binaries: Remembered {
                inner: binaries,
                known: BTreeMap::new(),
            },
        }
    }

    /// Whether the map `target` names is served by the generation cache now.
    pub fn of(&mut self, target: &str) -> bool {
        let skip = cache::Options::current().skip_render;
        map::resolve(&self.root, &self.walk, target).is_ok_and(|m| {
            m.tree == LIVE
                && m.kind.is_live()
                && cache::is_current(&self.root, m, &mut self.binaries, skip)
        })
    }
}

/// Each engine's binary as `inner` first named it (or failed to), asked once a run.
struct Remembered {
    inner: Box<dyn cache::engine::Binaries>,
    known: BTreeMap<cache::engine::Engine, Result<PathBuf, String>>,
}

impl cache::engine::Binaries for Remembered {
    fn binary(&mut self, engine: cache::engine::Engine) -> Result<PathBuf, String> {
        let inner = &mut self.inner;
        self.known
            .entry(engine)
            .or_insert_with(|| inner.binary(engine))
            .clone()
    }
}

/// The command line, from the tree at `root`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> Said {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words[..] {
        ["index"] => index_cli(root),
        ["find", name] => find_cli(root, name, None),
        ["find", name, suffix] => find_cli(root, name, Some(suffix)),
        ["list"] => list_cli(root),
        ["maps", ref rest @ ..] => maps::cli(root, rest),
        ["map", ref rest @ ..] => map::cli(
            root,
            rest,
            &mut cache::engine::Launcher {
                root: root.to_path_buf(),
                build: true,
            },
            cache::Options::current(),
        ),
        #[cfg(feature = "counters")]
        ["counts", tree] => counts_cli(
            root,
            tree,
            &mut cache::engine::Launcher {
                root: root.to_path_buf(),
                build: true,
            },
        ),
        _ => (String::new(), USAGE.to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;

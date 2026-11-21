//! "Did my change move this map's drawing, against HEAD?" - the comparison a wave records (feature 429 FR-004, D170; feature 449 T77, from
//! `maps_moved.py`; its ground moved by T230).
//!
//! Answered against HEAD, never against a scratch copy: feature 328 wave 68 (2026-10-09) copied the manifests after a gate test had already
//! regenerated them and recorded four hamlets unchanged while Sawada's board had moved 76 degrees.
//!
//! WHAT A DRAWING IS NOW (449 T230): a live map's drawing is what the generation cache published for it - its entry's artifacts, hard-linked
//! into the map's folder (a hamlet's gitignored `.driver.json` and `.driver.svg`, a sheet's `.svg`, `.html` and `.png`). The comparison
//! this replaced diffed tracked `.json` manifests against HEAD, but a hamlet's tracked `<name>.json` is the deleted Python's, never
//! rewritten, and no sheet's drawing is tracked at all, so it said unchanged for every map whatever moved (a check passing the bad,
//! constitution XIV).
//!
//! HEAD'S DRAWING IS THE MIRROR'S: no tree keeps a drawing per commit, and drawing HEAD again means building HEAD's engines in a detached
//! worktree (a cold render-sync - the engines built in a new target directory, every live map drawn, the index and the site - took
//! 171 s, measured by T222). But `render-sync` draws every live map in the mirror
//! (the clone's `..` of `.clones/`) at the mirror's HEAD after each landing, so its drawing of a map IS HEAD's wherever HEAD's inputs for that
//! map are the mirror's: the engines' sources (the whole of `rust/`, compared as git trees - a key broader than the engine only makes a
//! miss), the map's spec, and each file its engine reported reading (the mirror's read table), compared as git objects; the mirror's tracked
//! files its HEAD's; and the mirror's entry current (`is_current`, read-only, no engine built). Anything else is NOT COMPARED with its
//! reason - never "unchanged".
//!
//! Research: plumbing - NONE: reports which drawings moved, deciding nothing about a map

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_gate_pool::cache::engine::{Binaries, Engine, Launcher};
use l7r_gate_pool::cache::{self, entry, table::Table};
use l7r_gate_pool::{Map, Walk, LIVE};

use super::reply;
use crate::cohort::git;

/// What became of one map's drawing against HEAD.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Answer {
    /// It moved: the artifacts that differ (or why it counts as moved).
    Moved(Vec<String>),
    Unchanged,
    /// Not compared, and why.
    NotCompared(String),
}

/// An engine's binary asked once a tree, however many maps ask it: the launcher is a process a call.
struct Once {
    launcher: Launcher,
    got: BTreeMap<Engine, Result<PathBuf, String>>,
}

impl Once {
    fn at(root: &Path) -> Self {
        Self {
            launcher: Launcher {
                root: root.to_path_buf(),
                build: false,
            },
            got: BTreeMap::new(),
        }
    }
}

impl Binaries for Once {
    fn binary(&mut self, engine: Engine) -> Result<PathBuf, String> {
        self.got
            .entry(engine)
            .or_insert_with(|| self.launcher.binary(engine))
            .clone()
    }
}

/// One tree's side: its walk and its engines.
struct Side {
    root: PathBuf,
    walk: Walk,
    engines: Once,
}

impl Side {
    fn of(root: &Path) -> Self {
        Self {
            root: root.to_path_buf(),
            walk: l7r_gate_pool::walk(root),
            engines: Once::at(root),
        }
    }

    fn map(&self, rel: &str) -> Option<&Map> {
        self.walk.maps.iter().find(|m| m.rel() == rel)
    }

    /// The map's entry, when the tree has drawn it, and whether that drawing is of the tree as it stands.
    fn drawing(&mut self, rel: &str) -> Option<(entry::Meta, bool)> {
        let m = self.walk.maps.iter().find(|m| m.rel() == rel)?;
        let meta = entry::read(
            &self
                .root
                .join(cache::DIR)
                .join(cache::ENTRIES)
                .join(cache::map_id(m)),
        )?;
        let current = cache::is_current(&self.root, m, &mut self.engines, meta.skip_render);
        Some((meta, current))
    }
}

/// The object each `HEAD:<path>` names in `root`, asked of git in one `cat-file --batch-check`: its id, or `missing`. The paths are fed
/// from another thread, so a full pipe cannot deadlock the two.
fn objects(root: &Path, paths: &[String]) -> Vec<String> {
    let input = paths.iter().fold(String::new(), |mut s, p| {
        let _ = writeln!(s, "HEAD:{p}");
        s
    });
    let out = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["cat-file", "--batch-check"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .and_then(|mut child| {
            let mut stdin = child.stdin.take();
            let feeder =
                std::thread::spawn(move || stdin.as_mut().map(|s| s.write_all(input.as_bytes())));
            let out = child.wait_with_output();
            let _ = feeder.join();
            out
        })
        .map(|o| o.stdout)
        .unwrap_or_default();
    String::from_utf8_lossy(&out)
        .lines()
        .map(|l| {
            if l.ends_with(" missing") {
                "missing"
            } else {
                l.split(' ').next().unwrap_or_default()
            }
            .to_owned()
        })
        .collect()
}

fn line(root: &Path, args: &[&str]) -> Option<String> {
    let (ok, out) = git(root, args);
    ok.then(|| out.trim().to_owned())
}

/// Why no map of this tree can be compared against the mirror, or None.
fn whole_tree(clone: &Path, main: &Path) -> Option<String> {
    let same = std::fs::canonicalize(clone).ok() == std::fs::canonicalize(main).ok();
    if same {
        return Some(
            "this tree is the mirror: HEAD's drawing is the mirror's own, kept by no other tree - run it in a clone".to_owned(),
        );
    }
    let Some(theirs) = line(main, &["rev-parse", "HEAD:rust"]) else {
        return Some(format!(
            "no mirror at {} holds HEAD's drawing (a clone's mirror is the directory above its .clones/)",
            main.display()
        ));
    };
    if line(clone, &["rev-parse", "HEAD:rust"]).as_deref() != Some(theirs.as_str()) {
        return Some(format!(
            "HEAD's engine sources (rust/) are not the mirror's (at {}), so no drawing of HEAD is kept - sync with main if it is ahead; \
             else comparing means drawing HEAD's engines in a worktree (a cold render-sync - the engines built, every live map drawn, the index and the site - took 171 s, T222)",
            line(main, &["rev-parse", "--short", "HEAD"]).unwrap_or_default()
        ));
    }
    let dirty = line(
        main,
        &[
            "--no-optional-locks",
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
    )
    .unwrap_or_default();
    dirty.lines().next().map(|first| {
        format!("the mirror's tracked files are not its HEAD's ({first}), so its drawings are not HEAD's")
    })
}

/// One map's answer, the mirror's walk and engines shared across maps.
fn one(clone: &mut Side, main: &mut Side, rel: &str) -> Answer {
    use self::Answer::NotCompared;
    let Some(spec) = clone.map(rel).and_then(cache::spec_of) else {
        return NotCompared("a frozen exhibit, never drawn again".to_owned());
    };
    let spec = spec
        .strip_prefix(&clone.root)
        .unwrap_or(&spec)
        .display()
        .to_string();
    let Some((mine, current)) = clone.drawing(rel) else {
        return NotCompared(format!(
            "this tree has not drawn it - `make map MAP={rel}` draws it"
        ));
    };
    if !current {
        return NotCompared(format!(
            "this tree's drawing is not current - `make map MAP={rel}` draws it again"
        ));
    }
    if objects(&clone.root, std::slice::from_ref(&spec))
        .first()
        .is_none_or(|o| o == "missing")
    {
        return Answer::Moved(vec!["a map HEAD does not have".to_owned()]);
    }
    let Some((theirs, current)) = main.drawing(rel) else {
        return NotCompared(
            "the mirror has not drawn it (its render-sync is behind or failed: .clones/.render-sync.log)".to_owned(),
        );
    };
    if !current {
        return NotCompared(
            "the mirror's drawing of it is not current (its render-sync is behind or failed: .clones/.render-sync.log)".to_owned(),
        );
    }
    let id = main.map(rel).map(cache::map_id).unwrap_or_default();
    let table = std::fs::read_to_string(main.root.join(cache::DIR).join(cache::TABLE))
        .ok()
        .and_then(|t| Table::parse(&t))
        .unwrap_or_default();
    let mut inputs = vec![spec];
    inputs.extend(
        table
            .rows
            .iter()
            .filter(|(p, r)| !r.kind.is_font() && r.names(&id) && !Path::new(p).is_absolute())
            .map(|(p, _)| p.clone()),
    );
    let (ours, held) = (objects(&clone.root, &inputs), objects(&main.root, &inputs));
    for (i, path) in inputs.iter().enumerate() {
        let (a, b) = (ours.get(i), held.get(i));
        if b.is_some_and(|o| o == "missing") && main.root.join(path).exists() {
            return NotCompared(format!(
                "it reads {path}, which git does not track, so the mirror's drawing cannot be shown to be HEAD's"
            ));
        }
        if a.is_none() || a != b {
            return NotCompared(format!(
                "HEAD's {path} is not the mirror's, so the mirror's drawing is not HEAD's - comparing means drawing HEAD's engines in a \
                 worktree (a cold render-sync - the engines built, every live map drawn, the index and the site - took 171 s, T222)"
            ));
        }
    }
    let names = |m: &entry::Meta| {
        m.artifacts
            .iter()
            .map(|a| a.name.clone())
            .collect::<BTreeSet<_>>()
    };
    let (a, b) = (names(&mine), names(&theirs));
    let digest = |root: &Path, name: &str| {
        std::fs::read(root.join(rel).join(name)).map(|bytes| l7r_shared::sha256::hex(&bytes))
    };
    // A PICTURE SKIPPED ON ONE SIDE (`DIAGRAM_SKIP_RENDER=1`) is no move: only what both drew is compared
    let moved: Vec<String> = a
        .union(&b)
        .filter(|n| {
            if a.contains(*n) && b.contains(*n) {
                digest(&clone.root, n).ok() != digest(&main.root, n).ok()
            } else {
                mine.skip_render == theirs.skip_render
            }
        })
        .cloned()
        .collect();
    if moved.is_empty() {
        Answer::Unchanged
    } else {
        Answer::Moved(moved)
    }
}

/// Each live map's answer against HEAD (or the one `only` names, as `make map MAP=` names it), in the walk's order.
///
/// # Errors
/// `only` names no pool map: the message says how to name one.
pub fn moved(
    clone: &Path,
    main: &Path,
    only: Option<&str>,
) -> Result<Vec<(String, Answer)>, String> {
    let mut ours = Side::of(clone);
    let rels: Vec<String> = match only {
        Some(o) => vec![l7r_gate_pool::map::resolve(clone, &ours.walk, o)?.rel()],
        None => ours
            .walk
            .maps
            .iter()
            .filter(|m| m.tree == LIVE && m.kind.is_live())
            .map(Map::rel)
            .collect(),
    };
    if let Some(why) = whole_tree(clone, main) {
        return Ok(rels
            .into_iter()
            .map(|rel| (rel, Answer::NotCompared(why.clone())))
            .collect());
    }
    let mut theirs = Side::of(main);
    Ok(rels
        .into_iter()
        .map(|rel| {
            let answer = one(&mut ours, &mut theirs, &rel);
            (rel, answer)
        })
        .collect())
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

/// `l7r-gate measure maps-moved [--root DIR] [--only <map: its folder, a file in it, or its name>]`.
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let only = flag(args, "--only");
    let root = flag(args, "--root").map_or(root, Path::new);
    let main = l7r_gate_core::record::repo::mirror_of(root);
    let answers = match moved(root, &main, only) {
        Ok(a) => a,
        Err(why) => return reply(String::new(), why + "\n", 2),
    };
    let mut out = String::new();
    let mut tally = [0usize; 3];
    for (rel, answer) in &answers {
        let _ = match answer {
            Answer::Moved(what) => {
                tally[0] += 1;
                writeln!(out, "moved against HEAD: {rel} ({})", what.join(", "))
            }
            Answer::Unchanged => {
                tally[1] += 1;
                writeln!(out, "unchanged against HEAD: {rel}")
            }
            Answer::NotCompared(why) => {
                tally[2] += 1;
                writeln!(out, "NOT COMPARED: {rel} - {why}")
            }
        };
    }
    if only.is_none() {
        let _ = writeln!(
            out,
            "maps-moved: {} moved, {} unchanged, {} not compared, against the mirror's drawing of HEAD",
            tally[0], tally[1], tally[2]
        );
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;

//! IS THIS TEST BUILD ONE CRATE ALONE (feature 451 T347)? Told before the build starts, so that it takes the small lane and never
//! one of the wide build slots (`slot.rs`). Measured 2026-11-26 (`dev/measurements/2026-11-26/small-build-memory/results.md`): a
//! test build whose dependencies are all fresh compiles the crate's library and its tests and nothing else - two rustc at once,
//! 0.19-0.64 GiB anonymous after a body edit, 1.42 GiB at the most - where the builds the slot is for run a dozen.
//!
//! THE TELLING, two tests, both needed:
//!
//! 1. THE KEY: the content id of every file of the crates this one builds from by path (and the files those compile in), the
//!    workspace's manifests, lockfile and `.cargo/config.toml`, the crate's own `Cargo.toml`, the compiler, the build's words (its
//!    features) and the `RUSTFLAGS` it inherits - NOT the crate's own sources, which are what a build of the crate alone compiles,
//!    and not what its tests read at run time. It is kept in the target directory the build writes
//!    (`<target>/l7r-alone/<crate>-<check>`), so a new or wiped one holds none and a cold build is never told small.
//! 2. THE TIMES: every one of those files is older than the key's file, whose time is the START of the build that kept it (it is
//!    written beside itself before the build and moved into place when the build passes; a rename keeps the time). Content alone
//!    is not enough: cargo judges a path crate by its files' times, and a dependency's file put back by `git checkout` at its
//!    committed content made `land` recompile `reviews` (4 rustc) at an unchanged content key (the record's run `w`). A file at
//!    the key's own instant counts as newer.
//!
//! Where both hold, cargo finds every dependency's unit fresh. Anything else - a dependency edited or rewritten, a manifest, the
//! first build in a target directory, a fresh run or one outside a repository, which ask no binary key - is a wide slot, as before.
//!
//! ONE TELLING A CRATE A RUN, asked beside the binary key's build (`Verdict::ask`) and kept on the verdict, so the second asking
//! of a red build (`stepped`) runs in the same lane by construction. A build told alone leaves the key as it is, pass or fail: no
//! dependency moved, so it is still true, and a red build's next run is told alone again. A wide build that passes keeps its key;
//! one that fails keeps none of its own. The pre-warm's passing test build keeps the same key (`keeping`, feature 451 T367), so
//! a builder's first test build after a handout is told alone.
//!
//! A LINT PASS IS TOLD THE SAME WAY, BY A KEY OF ITS OWN (feature 451 T355, `lint.rs`): clippy's check units have their own
//! fingerprints, which a test build does not freshen, and one pass's are not another's, so each pass keeps a key named by its words
//! (`<crate>-lint--all-targets`) and is told alone only by what that pass last built - a checks' lint or the pre-warm's (451 T411).
//!
//! Each telling writes a `Phase` line, `slot-tell`: its span is the telling's cost (some milliseconds: one `stat` a dependency's
//! file), its code 0 where the build was told alone and 1 where not. With no lane (`L7R_BUILD_SLOTS_SMALL=0`, no wide slots)
//! nothing is told and no key is kept.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

use l7r_shared::sha256;

use super::super::{cargo, cargo_small, phase, shown, Ran, World};
use super::{depended, rel_dir, relative, Kept, WORKSPACE};

/// The keys' directory, under the target directory a build writes.
pub(in crate::rustc) const DIR: &str = "l7r-alone";
/// A telling's `Phase` step.
pub(in crate::rustc) const STEP: &str = "slot-tell";

/// What a crate's test build was told before it started.
pub(in crate::rustc) struct Told {
    /// Where its key is kept; none for a build nothing told.
    at: Option<PathBuf>,
    key: String,
    alone: bool,
}

/// The files a test build of `manifest`'s crate reads beside the crate's own sources, each with its content id: every file of the
/// crates it builds from by path and what those compile in, the workspace's files and its own manifest.
fn inputs<'a>(root: &Path, manifest: &Path, kept: &'a Kept) -> Vec<(&'a str, &'a str)> {
    let others: Vec<String> = depended(root, manifest, &kept.all)
        .iter()
        .map(|m| rel_dir(m, root))
        .collect();
    let dirs: Vec<String> = kept.all.iter().map(|m| rel_dir(m, root)).collect();
    let own = relative(manifest, root);
    // a path is the crate's whose directory holds it most nearly, as the verdict key reads it (`super::inputs`)
    let owner = |p: &str| {
        dirs.iter()
            .filter(|d| p.starts_with(d.as_str()))
            .max_by_key(|d| d.len())
    };
    let mut keyed: Vec<(&str, &str)> = kept
        .ids
        .iter()
        .filter(|(path, _)| {
            **path == own
                || WORKSPACE.contains(&path.as_str())
                || owner(path).is_some_and(|o| others.contains(o))
        })
        .map(|(p, i)| (p.as_str(), i.as_str()))
        .collect();
    let compiled_in: Vec<(&str, &str)> = keyed
        .iter()
        .filter_map(|(p, _)| kept.includes.get(*p))
        .flatten()
        .map(|p| (p.as_str(), kept.ids.get(p).map_or("", String::as_str)))
        .collect();
    keyed.extend(compiled_in);
    keyed.sort_unstable();
    keyed.dedup();
    keyed
}

fn key(world: &World, compiler: &str, args: &[&str], files: &[(&str, &str)]) -> String {
    let mut text = format!("alone\n{compiler}\n{}\n", args.join(" "));
    for flags in ["RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"] {
        let _ = writeln!(text, "{flags}={}", world.root.var(flags));
    }
    for (path, id) in files {
        let _ = writeln!(text, "{path} {id}");
    }
    sha256::hex(text.as_bytes())
}

fn modified(path: &Path) -> Option<SystemTime> {
    std::fs::metadata(path).and_then(|m| m.modified()).ok()
}

/// Does the key kept at `at` stand: it is `key`, and every file is older than it (a file that is gone is in the key as gone)?
fn stands(root: &Path, at: &Path, key: &str, files: &[(&str, &str)]) -> bool {
    let kept = std::fs::read_to_string(at).ok().filter(|k| k == key);
    let Some(when) = kept.and_then(|_| modified(at)) else {
        return false;
    };
    files
        .iter()
        .all(|(path, id)| id.is_empty() || modified(&root.join(path)).is_some_and(|t| t < when))
}

impl Told {
    /// A build nothing told: a wide slot, and no key kept.
    pub(in crate::rustc) fn wide() -> Self {
        Self {
            at: None,
            key: String::new(),
            alone: false,
        }
    }

    /// The telling of `cmd`'s build of `manifest`'s crate, whose words are `args`: a test build (`test`, `test-counters`) or one pass
    /// of the lint (`lint--all-targets`, ...); `cmd` names the key's file.
    pub(in crate::rustc) fn of(
        world: &World,
        cmd: &str,
        manifest: &Path,
        kept: &Kept,
        args: &[&str],
    ) -> Self {
        if world.small.count == 0 {
            return Self::wide();
        }
        let began = SystemTime::now();
        let target = world
            .target_override
            .as_ref()
            .map_or_else(|| world.target.clone(), PathBuf::from);
        let name = format!("{}-{cmd}", shown(world, manifest).replace('/', "_"));
        let at = target.join(DIR).join(name);
        let files = inputs(&world.root, manifest, kept);
        let key = key(world, &kept.compiler, args, &files);
        let alone = stands(&world.root, &at, &key, &files);
        phase::wrote(world, STEP, &[manifest], began, i32::from(!alone));
        Self {
            at: Some(at),
            key,
            alone,
        }
    }

    /// Was the build told to compile its crate alone?
    #[cfg(test)]
    pub(in crate::rustc) fn alone(&self) -> bool {
        self.alone
    }

    /// The build, in the lane it was told: the small lane where it compiles its crate alone, its key left as it is; a wide slot
    /// otherwise, its key written before it starts and kept where it passes.
    pub(in crate::rustc) fn cargo(&self, world: &World, args: &[&str], manifest: &Path) -> Ran {
        self.cargo_with(world, args, manifest, &[])
    }

    /// `cargo`, with the words `after` handed on to what cargo runs (a lint pass's `-D warnings`, feature 451 T355).
    pub(in crate::rustc) fn cargo_with(
        &self,
        world: &World,
        args: &[&str],
        manifest: &Path,
        after: &[&str],
    ) -> Ran {
        if self.alone {
            return cargo_small(world, args, manifest, after);
        }
        self.keeping("new", || {
            let ran = cargo(world, args, manifest, after);
            let passed = ran.code == 0;
            (ran, passed)
        })
    }

    /// The build `go` runs, which says whether it passed, its key kept as a wide build keeps it: written beside itself
    /// (`<key>.<beside>`) before `go` starts and moved into place where it passed, so the key's time is the build's start. Told
    /// alone, or told nothing, it keeps nothing. The checks' own builds (`cargo_with`) and the pre-warm's (`prewarm.rs`, feature 451
    /// T367, T411: so a builder's first test build and lint after a handout are told alone) - each beside the key by its own name,
    /// since the pre-warm joins no run lock and a run's build of the same crate can start while its own is in flight.
    pub(in crate::rustc) fn keeping<T>(&self, beside: &str, go: impl FnOnce() -> (T, bool)) -> T {
        let Some(at) = self.at.as_ref().filter(|_| !self.alone) else {
            return go().0;
        };
        let new = PathBuf::from(format!("{}.{beside}", at.display()));
        let _ = std::fs::create_dir_all(new.parent().unwrap_or(&new));
        let _ = std::fs::write(&new, &self.key);
        let (done, passed) = go();
        let _ = if passed {
            std::fs::rename(&new, at)
        } else {
            std::fs::remove_file(&new)
        };
        done
    }
}

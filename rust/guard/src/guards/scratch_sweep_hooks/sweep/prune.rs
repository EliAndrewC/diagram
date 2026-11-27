//! THE PRUNE INSIDE A LIVE BUILD DIRECTORY (451 T515; the GM 2026-11-27: "we are reusing builder worktrees for efficiency, then maybe
//! that means that a lot of the cleanup that we are relying on never actually happens"). Measured 2026-11-27 (`make disk-audit`): the
//! build cache at 246.9 GB against its 100 GB budget and the low-disk eviction freeing 0.0 GB, because the eviction (`evict.rs`) takes
//! only whole profiles idle past `L7R_CACHE_IDLE_HOURS`, never a pool tree's, and the clone's and the landing tree's profiles are
//! rebuilt at every landing; the variants rule (`cargo.rs`, a crate's builds past its newest sixteen) left 53 `l7r_mode_a` incremental
//! directories in the clone's `debug/` alone; and both stand down while any cargo runs anywhere (both audits of the day: "evict: a
//! build runs").
//!
//! The rule, per PROFILE (a directory holding `.fingerprint/`: `debug`, `tool`, `cover-gate/target/debug`, ...): a UNIT - one crate
//! built one way: its `.fingerprint/<crate>-<hash>/`, its `deps/` files of that hash and its `build/<crate>-<hash>/` - and an
//! `incremental/<crate>-<id>/` directory each go when (a) nothing read or wrote it in the `L7R_CACHE_STALE_HOURS` before the profile's
//! own last use, and (b) it is not the newest of its kind in the profile (a unit: its crate and its fingerprint's kind, `lib-serde`,
//! `test-lib-l7r_mode_a`, ...; an incremental directory: its crate). A profile a live process holds a path under (a cargo's
//! `.cargo-lock`, a rustc's output: `cargo::in_use`'s first half, at the profile) and a build directory whose run record names a live
//! member (its second half) are skipped whole. A build running ELSEWHERE holds nothing here, unlike the cache's other shares, and a
//! pool tree's profiles are pruned like any other's: the rule takes no profile, only what the profile's own recent builds did not
//! read (451 T285 keeps a pool tree's whole profiles out of the budget, "the variants rule inside a live build directory ... unchanged
//! and takes no profile").
//!
//! HOW "NOT READ" IS TOLD, measured on the real cache 2026-11-27 by stat alone (`dev/measurements/2026-11-27/t515-prune/results.md`):
//! a file's mtime says when it was built, never when a no-op build used it, while cargo reads a unit's fingerprint (`lib-<crate>`,
//! `dep-lib-<crate>`) at every build whose graph holds it, fresh or not, and rustc reads a dependency's `rlib`/`rmeta` - so the last
//! use is the newest mtime of anything in the entry and the newest atime of any file in it but a `.json` (cargo reads a fingerprint's
//! `.json` only to explain a rebuild, and one scan on 2026-11-26 at 14:31 moved every one, masking 15.4 GB). By mtime alone the rule
//! takes 86.9 GB, by this signal 85.0 GB: the 1.9 GB between is units no-op builds still read. The dep-info `.d` files name sources,
//! never a dependency's hash, so they cannot tell a stale hash. A directory's atime is never read: a listing (this sweep's own) moves
//! it. The disk is mounted `relatime`, so an atime lags a read by up to a day: the knob is floored at 25 hours (`FLOOR`). Measured
//! "before the profile's own last use", not "before now", so a profile no one has built for a while keeps its working set whole (the
//! eviction's to take): judged against now, the rule would take 92.2 GB, the 7.2 GB more from profiles idle for hours.
//!
//! Cost: a unit taken that a later build wants is that unit rebuilt; an incremental directory taken is its crate compiled from
//! scratch once, on its next edit. A build starting in the profile after the plan is met by `still_stale` at removal: a stale file's
//! atime is over a day old, so `relatime` moves it at the build's first read, and the entry is kept.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use super::{children, Config};

/// Why an entry the prune takes goes; `take` reads it to let the entry go while a build runs elsewhere.
pub(crate) const WHY: &str =
    "a crate's stale build in a live profile, unread in the knob's hours before the profile's last use";
/// The knob's floor: past the day `relatime` can let an atime lag a read.
const FLOOR: Duration = Duration::from_secs(25 * 3600);
/// How deep under a build directory a profile is looked for (`cover-gate/target/debug` is three down).
const DEPTH: usize = 4;
/// The stores a unit spans; `incremental/` is judged apart (its names carry no unit's hash).
const UNIT_STORES: [&str; 3] = ["deps", ".fingerprint", "build"];

/// One entry of a profile's stores, a unit or an incremental directory: its paths, its last use, whether something in it could not
/// be read (then it is kept), and its fingerprint's kind.
#[derive(Default)]
struct Entry {
    paths: Vec<PathBuf>,
    last: Option<SystemTime>,
    unread: bool,
    kind: String,
}

/// The knob in force: `L7R_CACHE_STALE_HOURS`, never under the floor.
fn knob(c: &Config) -> Duration {
    c.stale.max(FLOOR)
}

/// Every stale unit's and incremental directory's paths, in every profile no live process holds, each with why.
pub(super) fn plan(c: &Config, held: &[PathBuf]) -> Vec<(PathBuf, &'static str)> {
    let mut out = Vec::new();
    for (target, _, meta) in children(&c.cargo) {
        if !meta.is_dir() || super::cargo::run_member_alive(&target, 3, &c.proc) {
            continue;
        }
        let mut profiles = Vec::new();
        profiles_in(&target, DEPTH, &mut profiles);
        for profile in profiles {
            if !held.iter().any(|h| h.starts_with(&profile)) {
                out.extend(stale(&profile, knob(c)).into_iter().map(|p| (p, WHY)));
            }
        }
    }
    out
}

/// Every profile at most `depth` below `dir`: a directory holding `.fingerprint/`, never looked inside.
fn profiles_in(dir: &Path, depth: usize, out: &mut Vec<PathBuf>) {
    for (path, _, meta) in children(dir) {
        if !meta.is_dir() {
            continue;
        }
        if path.join(".fingerprint").is_dir() {
            out.push(path);
        } else if depth > 1 {
            profiles_in(&path, depth - 1, out);
        }
    }
}

/// The paths of a profile's stale entries.
fn stale(profile: &Path, knob: Duration) -> Vec<PathBuf> {
    let mut units: BTreeMap<String, Entry> = BTreeMap::new();
    for store in UNIT_STORES {
        for (path, name, _) in children(&profile.join(store)) {
            let key = if store == "deps" {
                unit_of(&name)
            } else {
                name
            };
            let unit = units.entry(key).or_default();
            if store == ".fingerprint" {
                unit.kind = kind_of(&path);
            }
            add(unit, path);
        }
    }
    let mut entries: Vec<(String, Entry)> = units
        .into_iter()
        .map(|(key, e)| (format!("u {} {}", crate_of(&key), e.kind), e))
        .collect();
    for (path, name, _) in children(&profile.join("incremental")) {
        let mut e = Entry::default();
        add(&mut e, path);
        entries.push((format!("i {}", crate_of(&name)), e));
    }
    let latest = entries
        .iter()
        .filter_map(|(_, e)| e.last)
        .max()
        .unwrap_or(UNIX_EPOCH);
    let mut newest: BTreeMap<&str, SystemTime> = BTreeMap::new();
    for (key, e) in &entries {
        let t = e.last.unwrap_or(UNIX_EPOCH);
        let n = newest.entry(key).or_insert(t);
        *n = t.max(*n);
    }
    entries
        .iter()
        .filter(|(key, e)| {
            e.last
                .is_some_and(|t| !e.unread && t + knob < latest && t < newest[key.as_str()])
        })
        .flat_map(|(_, e)| e.paths.iter().cloned())
        .collect()
}

/// Add one path to an entry: its last use folded in, or the entry marked unread.
fn add(e: &mut Entry, path: PathBuf) {
    match last_use(&path) {
        Some(t) => e.last = Some(e.last.map_or(t, |l| l.max(t))),
        None => e.unread = true,
    }
    e.paths.push(path);
}

/// The newest mtime at or under `path` and the newest atime of any regular file there but a `.json`, never through a symlink and
/// never a directory's atime; None where anything there cannot be read.
fn last_use(path: &Path) -> Option<SystemTime> {
    let m = std::fs::symlink_metadata(path).ok()?;
    let mut t = m.modified().ok()?;
    if m.is_dir() {
        for e in std::fs::read_dir(path).ok()? {
            t = t.max(last_use(&e.ok()?.path())?);
        }
    } else if m.is_file()
        && path
            .extension()
            .is_none_or(|x| !x.eq_ignore_ascii_case("json"))
    {
        t = t.max(m.accessed().ok()?);
    }
    Some(t)
}

/// A `deps/` file's unit, `<crate>-<hash>`: `libserde-ab12.rlib` -> `serde-ab12`, `l7r_gate-0f.d` -> `l7r_gate-0f`, a test binary as
/// it is.
fn unit_of(name: &str) -> String {
    let (stem, ext) = name.rsplit_once('.').unwrap_or((name, ""));
    let lib = matches!(ext, "rlib" | "rmeta" | "so" | "a");
    let unit = if lib { stem.strip_prefix("lib") } else { None };
    unit.unwrap_or(stem).to_owned()
}

/// A unit's or an incremental directory's crate: its name less the trailing `-<hash>`.
fn crate_of(name: &str) -> &str {
    name.rsplit_once('-').map_or(name, |(c, _)| c)
}

/// A fingerprint's kind: the first of its files that holds the unit's hash (`lib-serde`, `test-lib-x`, `run-build-script-...`) - not
/// its `.json`, dep-info, output or timestamp; empty where there is none.
fn kind_of(fingerprint: &Path) -> String {
    let mut kinds: Vec<String> = children(fingerprint)
        .into_iter()
        .filter(|(p, _, _)| {
            p.extension()
                .is_none_or(|x| !x.eq_ignore_ascii_case("json"))
        })
        .map(|(_, n, _)| n)
        .filter(|n| {
            !(n.starts_with("dep-") || n.starts_with("output-") || n == "invoked.timestamp")
        })
        .collect();
    kinds.sort();
    kinds.into_iter().next().unwrap_or_default()
}

/// At removal: the entry, and for a unit's `deps/` or `build/` path its fingerprint too, still unread for the knob's hours before
/// `now` - a freshness check begun since the plan reads the fingerprint, never the artifacts, so the fingerprint's atime is what moves.
pub(crate) fn still_stale(c: &Config, path: &Path, now: SystemTime) -> bool {
    let idle = |p: &Path| last_use(p).is_some_and(|t| t + knob(c) < now);
    let store = path.parent().and_then(Path::file_name);
    let fingerprint = match (
        store,
        path.parent().and_then(Path::parent),
        path.file_name(),
    ) {
        (Some(s), Some(profile), Some(name)) if s == "deps" || s == "build" => {
            let unit = unit_of(&name.to_string_lossy());
            Some(profile.join(".fingerprint").join(unit))
        }
        _ => None,
    };
    idle(path) && fingerprint.is_none_or(|f| !f.exists() || idle(&f))
}

#[cfg(test)]
mod tests;

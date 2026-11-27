//! The cargo target cache's share of the sweep (feature 449 T102, FR-013; the GM 2026-11-11: "Fix those leaks as well"). Every tree
//! that builds gets its own `~/.cache/l7r-cargo-target/<tree name>/` (`scripts/gates/l7r-gate.sh`), and nothing removed one: a scratch
//! clone's or a worktree's outlived it, and inside a live clone's, cargo keeps one variant of a crate per path and flag set it was ever
//! built with (`deps/`, `incremental/`, `.fingerprint/`, `build/`), a source edit making none but a moved path or a changed flag making a
//! new one each time - 3,407 `l7r_fixture` variants, ~5.6 GB, in one clone's `debug/` (observed 2026-11-11, method: `ls | grep -c` and
//! `du -ch` on that target). 54 GB in 56 directories in all.
//!
//! Two rules: (a) a build directory named for no live tree - neither the mirror nor any clone under the clones directory - goes once
//! proven dead (below), with no idle wait since 451 T245 (a removed worktree's build directory goes with it); the mirror's and every
//! clone's are never removed whole (past the budget, a live tree's idle profiles go instead: `evict.rs`) (the guard hook runs the mirror's
//! kept binary); (b) inside every directory kept, each crate's variants in a store beyond its newest four go once each is idle past the
//! threshold. Sixteen (451 T158; four before it): a crate's live variants are not three - one landing's gate (12:10-12:16, 2026-11-22)
//! touched 13 `l7r_mode_a` variants in the landing target's `debug/incremental` (its lib, its binary, its test builds, each built and
//! linted; method: the store's entries with an mtime in the window, counted by name less hash), so four took live ones from a crate idle
//! past the threshold; one wrongly taken costs only its rebuild. Where the clones directory cannot be read, no build directory is
//! removed whole.
//!
//! PROVEN DEAD (451 T158, the GM's condition, no loss of performance): a build directory goes whole only once no current code path
//! builds into its name and every tree its dep-info names is gone; one whose dep-info cannot be read is kept. "No worktree of that
//! name" was no proof: `rc` (11 GB) was a plain scratch clone's (`/tmp/t94/rc`), and `clone`, `tree` and `main-tree` are names the
//! hooks suites, a mirror stand-in and the model trial build into (`BUILT_INTO`).
//!
//! THE LIVE TREES (451 T158): a tree's build directory is named for its basename, so a worktree made outside the clones directory
//! (`git -C <clone> worktree add /tmp/t33/wt`) builds into `wt`, shared by every tree of that name; a name any registered worktree of
//! the mirror or a clone still has is live, and so is `<clone>-land-tooling`, the tooling landing's guard build
//! (`scripts/land-tooling.sh`). A build directory a live process holds (its cwd, binary or an open file under it, cargo's build lock
//! among them) or whose run record (`rust-checks-run.json`, `l7r-gate rust`'s run lock, 451 T23) names a live member is kept whole,
//! nothing inside it removed.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

use super::{children, newest, Config};

/// The newest variants of a crate a store always keeps.
const KEPT: usize = 16;
/// The stores where cargo keeps one entry a variant.
const STORES: [&str; 4] = ["deps", "incremental", ".fingerprint", "build"];
/// The names a current code path builds into whatever tree last used them (451 T158, by every `CARGO_TARGET_DIR` and `${TREE##*/}`
/// user, 2026-11-22): `clone`, the hooks suites' fixture clones that run the real wrapper (`clone/build.log` named
/// `/tmp/l7r-hooks-suite-pair-hooks.sh-*/clone`), a `git clone -q . $T/clone` standing in the mirror (451 T79) and a review
/// snapshot's side; `tree` and `main-tree`, the model trial's own clones (`trials/src/measure/model_trial/case.rs`).
pub(crate) const BUILT_INTO: [&str; 3] = ["clone", "tree", "main-tree"];
/// A clone's landing trees beside it: `make land`'s worktree (`scripts/land-alone.sh`, its target "built once and kept"), the tooling
/// landing's worktree (`scripts/land-tooling.sh`, the gate's build) and that landing's guard build.
const LANDING: [&str; 3] = ["-land", "-tooling", "-land-tooling"];
/// How deep under a build directory a store is looked for (`cover-gate/target/debug/deps` is four down).
const DEPTH: usize = 5;

/// What the cache's sweep removes, each with why.
pub(super) fn plan(
    c: &Config,
    cutoff: SystemTime,
    held: &[PathBuf],
    budget: Budget,
) -> Vec<(PathBuf, &'static str)> {
    let mut out = Vec::new();
    if !std::fs::symlink_metadata(&c.cargo).is_ok_and(|m| m.is_dir()) {
        return out;
    }
    let live = trees(c);
    let mut kept = Vec::new();
    for (target, name, meta) in children(&c.cargo) {
        if !meta.is_dir() || in_use(&target, held, &c.proc) {
            continue;
        }
        // no idle wait (451 T245: a removed worktree's build directory goes with it, at the next sweep, where the day's trials left
        // 13-14 GB each until removed by hand): proven dead, nothing builds into it again, and a build running in it is `in_use`
        if dead(&target, &name, live.as_deref()) {
            out.push((
                target,
                "a build directory proven dead (no code path builds into its name, every tree it was built from gone)",
            ));
        } else {
            kept.push(target);
        }
    }
    // past the budget, an idle profile of a live tree's (451 T245, `evict.rs`), for what the dead ones leave short
    let dead: u64 = out.iter().map(|(p, _)| super::bytes(p)).sum();
    let profiles = super::evict::choose(c, budget.need.saturating_sub(dead), budget.idle, held);
    for target in kept {
        let mut stores = Vec::new();
        find_stores(&target, DEPTH, &mut stores);
        for store in stores {
            if !profiles.iter().any(|(p, _)| store.starts_with(p)) {
                out.extend(stale_variants(&store, cutoff));
            }
        }
    }
    out.extend(profiles);
    out
}

/// A build directory proven dead: no live tree has its name (None, the clones directory unread: none is), no code path builds into
/// it, and every tree its dep-info names is gone.
pub(super) fn dead(target: &Path, name: &str, live: Option<&[String]>) -> bool {
    live.is_some_and(|l| !l.iter().any(|n| n == name))
        && !BUILT_INTO.contains(&name)
        && built_from(target).is_some_and(|trees| trees.iter().all(|t| !t.exists()))
}

/// What the cache's budget asks of a plan (451 T245): the bytes to free (0 within the budget), and the time before which a live tree's
/// profile counts idle.
#[derive(Clone, Copy)]
pub(crate) struct Budget {
    pub need: u64,
    pub idle: SystemTime,
}

/// The names of the trees whose build directories are never removed whole: the mirror's and every clone's; None where the clones
/// directory cannot be read.
pub(super) fn trees(c: &Config) -> Option<Vec<String>> {
    let clones = std::fs::read_dir(&c.clones).ok()?;
    let mut names: Vec<String> = clones
        .flatten()
        .filter(|e| e.file_type().is_ok_and(|t| t.is_dir()))
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    let tooling: Vec<String> = names
        .iter()
        .flat_map(|n| LANDING.iter().map(move |s| format!("{n}{s}")))
        .collect();
    names.extend(tooling);
    names.extend(
        c.mirror
            .file_name()
            .map(|n| n.to_string_lossy().into_owned()),
    );
    names.extend(
        worktrees(c)
            .into_iter()
            .filter_map(|w| w.tree.file_name().map(|n| n.to_string_lossy().into_owned())),
    );
    Some(names)
}

/// The trees a build directory was built from, read from its profiles' top dep-info (`<target>/<profile>/*.d` and one more level,
/// `cover-gate/target`'s, never a store): each source path's part before `/rust/`. None where none reads, so a build directory that
/// cannot be proven dead is kept (451 T158: `rc`, 11 GB, its tree `/tmp/t94/rc` a plain clone no worktree list names).
fn built_from(target: &Path) -> Option<Vec<PathBuf>> {
    let mut deps = Vec::new();
    dep_info(target, 3, &mut deps);
    let mut trees: Vec<PathBuf> = Vec::new();
    for d in deps {
        let text = std::fs::read_to_string(&d).unwrap_or_default();
        let sources = text.split_once(": ").map_or("", |(_, s)| s);
        for word in sources.split_whitespace() {
            if let Some((tree, _)) = word.split_once("/rust/") {
                let tree = PathBuf::from(tree);
                if tree.is_absolute() && !trees.contains(&tree) {
                    trees.push(tree);
                }
            }
        }
    }
    (!trees.is_empty()).then_some(trees)
}

fn dep_info(dir: &Path, depth: usize, out: &mut Vec<PathBuf>) {
    for (path, name, meta) in children(dir) {
        if meta.is_dir() && depth > 1 && !STORES.contains(&name.as_str()) {
            dep_info(&path, depth - 1, out);
        } else if meta.is_file() && path.extension().is_some_and(|e| e == "d") {
            out.push(path);
        }
    }
}

/// A registered worktree of the mirror or a clone whose tree still exists: the tree, the repository it belongs to, and its
/// administrative directory (`<repo>/.git/worktrees/<id>`).
pub(crate) struct Worktree {
    pub tree: PathBuf,
    pub repo: PathBuf,
    pub admin: PathBuf,
}

/// Every registered worktree of the mirror and of each clone (`.git/worktrees/*/gitdir`, its tree the `.git` file's directory), the
/// ones whose tree is gone left out (`git worktree prune`'s to drop).
pub(crate) fn worktrees(c: &Config) -> Vec<Worktree> {
    let repos = std::fs::read_dir(&c.clones)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .chain(std::iter::once(c.mirror.clone()));
    let mut out = Vec::new();
    for repo in repos {
        for (admin, _, _) in children(&repo.join(".git/worktrees")) {
            let gitdir = std::fs::read_to_string(admin.join("gitdir")).unwrap_or_default();
            let tree = Path::new(gitdir.trim()).parent().unwrap_or(Path::new(""));
            if tree.is_dir() {
                out.push(Worktree {
                    tree: tree.to_path_buf(),
                    repo: repo.clone(),
                    admin,
                });
            }
        }
    }
    out
}

/// A build directory something uses now: a live process holds a path under it, or a run record in it (`rust-checks-run.json`, at
/// most three down: the target's own and a coverage family's `view/<crate>`) names a member whose process still runs.
pub(super) fn in_use(target: &Path, held: &[PathBuf], proc: &Path) -> bool {
    held.iter().any(|h| h.starts_with(target)) || run_member_alive(target, 3, proc)
}

pub(super) fn run_member_alive(dir: &Path, depth: usize, proc: &Path) -> bool {
    let record = std::fs::read_to_string(dir.join("rust-checks-run.json")).unwrap_or_default();
    let v: serde_json::Value = serde_json::from_str(&record).unwrap_or_default();
    let members = v["members"].as_array().map_or(&[][..], Vec::as_slice);
    let live = members.iter().any(|m| {
        let pid = m["pid"].as_u64().unwrap_or(0);
        pid > 0 && started(proc, pid).is_some_and(|s| Some(s) == m["start"].as_u64())
    });
    live || (depth > 1
        && children(dir)
            .into_iter()
            .any(|(p, _, m)| m.is_dir() && run_member_alive(&p, depth - 1, proc)))
}

/// A process's start in clock ticks since boot (`/proc/<pid>/stat`'s 22nd field), None where it does not run.
pub(super) fn started(proc: &Path, pid: u64) -> Option<u64> {
    let stat = std::fs::read_to_string(proc.join(pid.to_string()).join("stat")).ok()?;
    stat.rsplit_once(") ")?
        .1
        .split_whitespace()
        .nth(19)?
        .parse()
        .ok()
}

/// Every store at most `depth` below `dir`, never through a symlink and never into a store.
fn find_stores(dir: &Path, depth: usize, out: &mut Vec<PathBuf>) {
    for (path, name, meta) in children(dir) {
        if !meta.is_dir() {
            continue;
        }
        if STORES.contains(&name.as_str()) {
            out.push(path);
        } else if depth > 1 {
            find_stores(&path, depth - 1, out);
        }
    }
}

/// A store's entries beyond each crate's newest `KEPT`, idle past `cutoff`; an entry whose age cannot be read is kept.
fn stale_variants(store: &Path, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    let mut groups: BTreeMap<String, Vec<(SystemTime, PathBuf)>> = BTreeMap::new();
    for (path, name, _) in children(store) {
        if let Some(t) = newest(&path) {
            groups.entry(variant_of(&name)).or_default().push((t, path));
        }
    }
    let mut out = Vec::new();
    for mut variants in groups.into_values() {
        variants.sort_by(|a, b| b.0.cmp(&a.0));
        out.extend(
            variants
                .into_iter()
                .skip(KEPT)
                .filter(|(t, _)| *t < cutoff)
                .map(|(_, p)| (p, "an old build variant of a crate")),
        );
    }
    out
}

/// What makes entries variants of one another: the name without its trailing `-<hash>`, with its extension (`libserde-ab12.rlib`
/// -> `libserde.rlib`, `l7r_gate-0hjj` -> `l7r_gate.`).
fn variant_of(name: &str) -> String {
    let (stem, ext) = match name.rsplit_once('.') {
        Some((s, e)) if !s.is_empty() && !e.contains('-') => (s, e),
        _ => (name, ""),
    };
    let base = stem.rsplit_once('-').map_or(stem, |(b, _)| b);
    format!("{base}.{ext}")
}

#[cfg(test)]
mod tests;

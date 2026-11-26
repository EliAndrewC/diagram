//! THE RENDERINGS, A TREE AT A TIME (feature 451 T281). The store of rendered messages sat in the git COMMON directory beside the
//! suites' stamps, so every worktree of a clone read and wrote one set: a tree's run replaced another's renderings (its
//! `make guard-messages BUNDLE=1` then said "nothing owed" for the wordings its own red `make hooks-test` had just named), and a
//! tree's check read the renderings of a guard only another tree holds (both reproduced with two worktree fixtures, 2026-11-26:
//! `tests/hooks/test-parts.3.sh`). Now two places:
//!
//! - THE TREE'S STORE, `<the tree's own git dir>/hooks-test/messages/<job>.jsonl` ([`store`]; a linked worktree's `.git` is a
//!   file, so git is asked for the directory, as 451 T254 and T267 did): what this tree's last `make hooks-test` held for each
//!   suite of ITS roster. Every reader reads it - the hooks-test check, `make guard-messages` and its bundle.
//! - THE KEYED RENDERINGS, `<common dir>/hooks-test/rendered/<job>@<key>.jsonl`, beside the shared stamps: a green job's
//!   rendering named by the suite key it ran at (`hookrun.sh` writes it, one a job).
//!
//! WHY the second, where the task asked only for a store keyed by tree: the stamps STAY shared - a fresh worktree off main
//! reran 5 suites of 46 where it had rerun all (83 s against 151 s, measured 2026-10-12, commit d7456c4c8d) - and a suite
//! skipped on another tree's stamp has rendered nothing here. [`gather`] fills the tree's store for such a suite from the
//! rendering at the stamp's key, which is what this tree's own run would render (the key is the suite's inputs); a tree store
//! alone would have rerun every suite in a fresh tree, or kept a stale rendering where another tree stamped this tree's new key.
//!
//! ```text
//! l7r-guard messages store <dir>                                   the store of the tree holding <dir>
//! l7r-guard messages gather <rendered dir> <tree store> <list>     after a run's suites: fill and prune the tree's store
//! ```

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use crate::protocol::Reply;

/// The store of the tree holding `dir`: `hooks-test/messages` under the tree's OWN git directory; none outside a repository.
#[must_use]
pub fn store(dir: &Path) -> Option<PathBuf> {
    let own = crate::shared::checks::git_stdout(dir, &["rev-parse", "--absolute-git-dir"]);
    (!own.is_empty()).then(|| Path::new(&own).join("hooks-test/messages"))
}

/// `messages store <dir>`: the path, a line.
pub(super) fn store_cli(dir: &str) -> Reply {
    match store(Path::new(dir)) {
        Some(p) => super::reply(format!("{}\n", p.display()), String::new(), 0),
        None => super::reply(
            String::new(),
            format!("guard-messages: {dir} is in no git repository, so it has no store of rendered messages\n"),
            1,
        ),
    }
}

/// The guard of a store file among `roster`: `<guard>.jsonl`, or a shard's `<guard>.<k>.jsonl`.
fn owner<'a>(job: &str, roster: &BTreeSet<&'a str>) -> Option<&'a str> {
    let unsplit = job
        .rsplit_once('.')
        .filter(|(_, k)| !k.is_empty() && k.bytes().all(|b| b.is_ascii_digit()))
        .map_or(job, |(guard, _)| guard);
    roster.get(job).or_else(|| roster.get(unsplit)).copied()
}

/// The `.jsonl` files of `dir`, each with its name less the extension, sorted.
fn jobs(dir: &Path) -> Vec<(String, PathBuf)> {
    let mut out: Vec<(String, PathBuf)> = std::fs::read_dir(dir)
        .map_or_else(
            |_| Vec::<PathBuf>::new(),
            |d| d.filter_map(Result::ok).map(|e| e.path()).collect(),
        )
        .into_iter()
        .filter_map(|p| {
            let name = p.file_name()?.to_str()?.strip_suffix(".jsonl")?.to_owned();
            Some((name, p))
        })
        .collect();
    out.sort();
    out
}

/// `messages gather`: the tree's store made this run's. `list` holds a line a suite of the run's roster - `<guard> <key>` for a
/// suite SKIPPED as unchanged, the key its stamp holds, and `<guard>` alone for one that ran (its green job wrote the store
/// itself; a red one keeps its last green rendering, as before T281). A skipped suite's files are replaced by the renderings at
/// its key; a file of no suite on the list is removed, so a guard this tree does not hold - another tree's, or one deleted - is
/// never judged here. A skipped suite with no rendering at its key (another tree's run replaced it since the skip was decided)
/// fails the run by name: its store would be stale, and the next run reruns it.
pub(super) fn gather(rendered: &Path, tree: &Path, list: &Path) -> Reply {
    let text = std::fs::read_to_string(list).unwrap_or_default();
    let lines: Vec<(&str, Option<&str>)> = text
        .lines()
        .filter_map(|l| {
            let mut w = l.split_whitespace();
            Some((w.next()?, w.next()))
        })
        .collect();
    let roster: BTreeSet<&str> = lines.iter().map(|(g, _)| *g).collect();
    let _ = std::fs::create_dir_all(tree);
    let keyed = jobs(rendered);
    let mut gone = Vec::new();
    for (guard, key) in lines.iter().filter_map(|(g, k)| k.map(|k| (*g, k))) {
        let at_key: Vec<(&str, &PathBuf)> = keyed
            .iter()
            .filter_map(|(name, p)| Some((name.strip_suffix(key)?.strip_suffix('@')?, p)))
            .filter(|(job, _)| owner(job, &roster) == Some(guard))
            .collect();
        // written whole beside its place, then moved: a reader beside this run never meets half a file
        let filled = !at_key.is_empty()
            && at_key.iter().all(|(job, p)| {
                let part = tree.join(format!(".{job}.part"));
                std::fs::copy(p, &part).is_ok()
                    && std::fs::rename(&part, tree.join(format!("{job}.jsonl"))).is_ok()
            });
        if !filled {
            gone.push(guard);
        }
        // a shard the suite no longer has keeps no rendering
        for (job, p) in jobs(tree) {
            if filled
                && owner(&job, &roster) == Some(guard)
                && !at_key.iter().any(|(j, _)| *j == job)
            {
                let _ = std::fs::remove_file(p);
            }
        }
    }
    for (job, p) in jobs(tree) {
        if owner(&job, &roster).is_none() {
            let _ = std::fs::remove_file(p);
        }
    }
    if gone.is_empty() {
        return super::reply(String::new(), String::new(), 0);
    }
    super::reply(
        String::new(),
        format!(
            "guard-messages: {} skipped as unchanged, but no rendering at its stamp's key is left in {} - another worktree's run \
             replaced it since\n  fix: make hooks-test again, which reruns it\n",
            gone.join(", "),
            rendered.display()
        ),
        1,
    )
}

#[cfg(test)]
mod tests;

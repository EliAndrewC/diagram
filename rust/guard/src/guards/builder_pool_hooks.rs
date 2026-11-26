//! `builder-pool-hooks` (feature 451 T285; the GM, 2026-11-26: "we should make it so that whatever tooling we use to create
//! worktrees automatically enforces and performs the correct behavior without the opportunity for this kind of mistake in the
//! future"): A BUILDER'S WORKTREE COMES FROM THE POOL AND NOTHING ELSE. On 2026-11-26 the coordinating session made each builder a
//! fresh worktree by hand (`git -C <clone> worktree add --detach /diagram/.clones/<clone>-<tag> HEAD`) and removed it and its build
//! cache after the landing, against the reused-worktrees rule it had recorded that morning, so every builder's first closing checks
//! compiled everything: 14-30 minutes against about one (`docs/process-decisions.md`, "Two code builders at once").
//!
//! Refused, each naming the pool's command (`make builder-tree`, `rust/gate/crates/task/src/builder_tree.rs`):
//! - `git worktree add` of a tree under the clones directory (`<mirror>/.clones/`). The trees the tooling makes there - the
//!   landing's (`scripts/land-alone.sh`), the tooling landing's (`scripts/land-tooling.sh`), the review's
//!   (`scripts/gates/review-tree.sh`) and the pool's own - are made inside those programs, which no hook reads: they are exempt by
//!   where the call is made, not by a name a hand command could take. A scratch worktree outside the clones directory passes.
//! - `git worktree remove` or `move` of a pool tree (a move chills its cache as a removal does: measured 2026-11-26, 0.11 s to
//!   66.5 s), and an `rm` whose operand is a pool tree, its build cache or a directory holding either.
//!
//! A pool tree is one a clone's registry names (`shared::builder_pool`, `<clone>/.git/builder-pool.json`), never a name's shape.
//! The command is read by the shared walk (`shared::tree::walk`: each write with where it lands, its variables and `cd`s followed),
//! so a mention - a `grep`, an `echo`, a commit message - is no invocation. `BUILDER_TREE_OK` with a reason of two words or more is
//! the escape, checked first.

use std::path::{Path, PathBuf};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::builder_pool;
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::shape::shlex;
use crate::shared::state::field;
use crate::shared::tree::walk;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "builder-pool-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

const ADD: &str = "BLOCKED (builder-pool): don't make a worktree under the clones directory by hand. A cold tree's first closing checks take 14-30 minutes, not about 1.

Run: make builder-tree T=<task> [F=<feature>] (prints the path; make land frees it).
A scratch worktree for a measurement goes outside the clones directory. Otherwise append `# BUILDER_TREE_OK: <reason, two words or more>`.";

const REMOVE: &str = "BLOCKED (builder-pool): don't remove or move a pool tree or its build cache by hand; they keep the next builder's first closing checks warm (cold: 14-30 min, not about 1).

To free a tree: make builder-tree-release T=<task> (keeps the cache; make land does it for a landed task).
To remove one for real: make builder-tree-drop TREE=<path> REASON=\"<two words or more>\".
Otherwise append `# BUILDER_TREE_OK: <reason, two words or more>`.";

/// What a write's command does to a tree: `add`, `remove` (`git worktree remove` or `move`) or `rm`; None for any other.
fn verb(head: &str) -> Option<&'static str> {
    let toks = shlex(head).unwrap_or_else(|| head.split_whitespace().map(str::to_owned).collect());
    let name = |t: &String| t.rsplit('/').next().unwrap_or_default().to_owned();
    match toks.first().map(name).as_deref() {
        Some("rm") => Some("rm"),
        Some("git") => {
            let at = toks.iter().position(|t| t == "worktree")?;
            match toks.get(at + 1).map(String::as_str) {
                Some("add") => Some("add"),
                Some("remove" | "move") => Some("remove"),
                _ => None,
            }
        }
        _ => None,
    }
}

/// The refusal `cmd` earns, run from `dir` with the mirror at `main`: the first of its writes that makes a worktree under the
/// clones directory, or removes a pool tree or its build cache under `cache`.
pub(crate) fn refusal(
    cmd: &str,
    dir: &str,
    main: &Path,
    home: &str,
    cache: &Path,
) -> Option<&'static str> {
    let clones = main.join(".clones");
    let pool = builder_pool::pools(&clones);
    walk(cmd, Some(dir), &main.to_string_lossy(), home)
        .targets
        .iter()
        .find_map(|t| {
            let path = PathBuf::from(t.path.as_deref()?);
            match verb(&t.head)? {
                "add" => (path.starts_with(&clones) && path != clones).then_some(ADD),
                "remove" => pool.iter().any(|p| p.tree == path).then_some(REMOVE),
                _ => pool
                    .iter()
                    .any(|p| {
                        p.tree.starts_with(&path)
                            || builder_pool::cache(cache, &p.tree).starts_with(&path)
                    })
                    .then_some(REMOVE),
            }
        })
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let home = crate::shared::env::var("HOME");
    let cache = crate::shared::env::opt("L7R_BUILDER_CACHE").map_or_else(
        || Path::new(&home).join(".cache/l7r-cargo-target"),
        PathBuf::from,
    );
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if !cmd.contains("worktree") && !cmd.contains("rm") {
        return Vec::new();
    }
    let shown: String = cmd.chars().take(200).collect();
    match escape_or_refuse(cmd, "BUILDER_TREE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "builder-pool",
                "escaped",
                &why,
                "builder-tree-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "builder-pool",
                "blocked",
                &shown,
                "BUILDER_TREE_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    let dir = if session.cwd.is_empty() {
        "/"
    } else {
        &session.cwd
    };
    let Some(text) = refusal(cmd, dir, session.main(), &home, &cache) else {
        return Vec::new();
    };
    let rule = if text == ADD {
        "hand-made-worktree"
    } else {
        "pool-tree-removed"
    };
    log::fire(
        "builder-pool",
        "blocked",
        &shown,
        rule,
        &event.input,
        session,
    );
    vec![Answer::Refuse(text.to_owned())]
}

#[cfg(test)]
mod tests;
// GUARD_EDIT_OK: feature 451 T285 - adding a guard, the builder pool's

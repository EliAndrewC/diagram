//! What a take answers before any tree is touched (`make builder-tree`, split out of `builder_tree.rs` for its size by 461 T22): the
//! tree the tasks already hold, or why none is handed out yet - the clone's own commits unpushed from phase 2's base (plan D13), or
//! the task's own done commit not yet carried.

use l7r_gate_core::Reply;
use l7r_shared::builder_pool::Tree;

use super::{holds, refused, text, Env, Pool};
use crate::{git, reply};

/// THE COORDINATOR'S OWN COMMITS GO OUT FIRST (461 plan D13, T22): from phase 2's base a hand-in applies onto `origin/main`, so a
/// tree handed out on a clone HEAD ahead of it would build on work - a plan stub `make task-add` wrote, say - that its hand-in's
/// base lacks. Why a handout is refused: the count of the clone's commits `origin/main` lacks, with the DIRECT push that sends
/// them; or `origin/main` unreadable. Read from the clone's own `origin/main` with no fetch (the prompt hook's `sync-in` fetches
/// each turn; a fetch a handout would cost a network round): the easier route, the record silent.
pub(super) fn unpushed(p: &Pool, env: &Env) -> Option<String> {
    if !env.origin {
        return None;
    }
    let (rc, out) = git(&p.clone, &["rev-list", "--count", "origin/main..HEAD"]);
    let n = text(&out);
    if rc != Some(0) {
        return Some(format!("builder-tree: refused - no tree handed out: origin/main cannot be read in {} (git rev-list origin/main..HEAD failed), and from phase 2's base (HAND_IN_BASE origin, 461 D13) a handout waits until the clone's HEAD holds nothing origin/main lacks: git -C {} fetch origin, then make builder-tree again\n", p.clone.display(), p.clone.display()));
    }
    (n != "0").then(|| format!("builder-tree: refused - no tree handed out: the clone's HEAD holds {n} commit(s) origin/main lacks, and from phase 2's base (HAND_IN_BASE origin, 461 D13) a builder's hand-in applies onto origin/main, which would lack them - push them first: {}/scripts/sync-with-main.sh done, then make builder-tree again\n", p.clone.display()))
}

/// What a take answers before any tree is touched: the tree the tasks already hold, or why none is handed out yet.
pub(super) fn settled(
    p: &Pool,
    trees: &[Tree],
    tasks: &[String],
    feature: &str,
    env: &Env,
) -> Option<Reply> {
    if let Some(t) = trees.iter().find(|t| holds(t, tasks, feature)) {
        return Some(reply(
            format!("{}\n", t.tree.display()),
            format!(
                "builder-tree: {} already holds it (since {})\n",
                t.holder(),
                t.since
            ),
            0,
        ));
    }
    // the clone's own commits unpushed from phase 2's base (461 D13); the task's own done commit not yet carried: the handout
    // builds on it (461 T09, D14, `builder_done::build_on`), or with no apply program known its next builder would start without
    // it, and waits (451 T398)
    if let Some(why) =
        unpushed(p, env).or_else(|| crate::builder_done::handout_waits(p, tasks, feature, env))
    {
        return Some(refused(why));
    }
    None
}

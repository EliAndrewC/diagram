//! THE ONE ROUTE TO LAND (feature 461 T29, plan D11 phase 4; FR-001, FR-003): `make land` runs only in the landing lane's tree - the
//! tree the pool's registry holds under the reserved holder `lane` (`builder_pool::LANE`, 461 T13), matched by its canonical path - so
//! no gate runs in the coordinator's clone (FR-001, by where gates run: plan D10) and every landing is the lane's (FR-003). Anywhere
//! else it is refused before anything runs, naming the route: the work handed in by `make builder-done`, the lane started by
//! `make lane-start`. WHY a tree and not a variable: `L7R_LANE_BATCH` and `L7R_LAND_ALONE` are plain exports anyone can set, so
//! letting either through would be an unrecorded escape (as the red-gate tripwire's stand-down reads the tree too, `tree/src/state.rs`'s
//! `lane_run`). The lane's runner (`lane/src/runner/run.rs`, step 3) and `scripts/land-alone.sh`'s inner landing (step 6, in
//! `<clone>-land`, the tree D1 adopted as the lane's) both run in that tree and pass unasked.
//!
//! THE ESCAPE, `LAND_HERE_OK="<reason>"`, for the lane's own failure (D11: on 2026-11-28 the coordinator landed by hand while the lane
//! was learning to handle failures - halving, T25's conflict repair, T90's build-half rule): read first, held to the reason floor
//! (`escape::enough`), and recorded either way in the guard log as `land-here` (`make guard-log GUARD=land-here`). A landing let
//! through outside the lane goes on as before - a dirty clone still lands alone until T30 retires that route.

use std::path::{Path, PathBuf};

use l7r_shared::env::Rooted;
use l7r_shared::escape::enough;
use l7r_shared::log::Entry;
use l7r_shared::py_text::strip;
use serde_json::Value;

/// The escape: a landing outside the lane's tree, for the lane's own failure.
pub(super) const ESCAPE: &str = "LAND_HERE_OK";
/// The guard-log name its firings are recorded under.
pub(super) const GUARD: &str = "land-here";

/// What the route rules of a landing: in the lane's tree, let through by the escape (with the line to print), or refused.
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Route {
    Lane,
    Escaped(String),
    Refused(String),
}

/// The lane's tree as the registry of the clone whose common git directory is `common` names it, if one is adopted.
fn lane_tree(common: &Path) -> Option<PathBuf> {
    l7r_shared::builder_pool::read_all(common)
        .into_iter()
        .find(l7r_shared::builder_pool::Tree::lane)
        .map(|t| t.tree)
}

/// Is `root` the lane's tree: the registry's lane entry, both paths canonical.
fn in_lane(root: &Path, lane: Option<&Path>) -> bool {
    let canon = |p: &Path| std::fs::canonicalize(p).ok();
    lane.is_some_and(|l| canon(l).is_some() && canon(l) == canon(root))
}

/// The route of a landing of `tasks` of `feature` from `root`, recorded where it is not the lane's.
pub(super) fn rule(root: &Rooted, feature: &str, tasks: &[String]) -> Route {
    let lane = lane_tree(&l7r_shared::checks::common_dir(root));
    if in_lane(root, lane.as_deref()) {
        return Route::Lane;
    }
    let here = root.display();
    let t = tasks.join(" ");
    let why = strip(&root.var(ESCAPE)).to_owned();
    if !why.is_empty() {
        if !enough(&why) {
            record(root, "blocked", &why, "LAND_HERE_OK-no-reason");
            return Route::Refused(format!("land: refused - {ESCAPE} needs a REASON, not just a value - two words and eight characters; say why the lane cannot land {t}"));
        }
        record(
            root,
            "escaped",
            &format!("{feature} {t} in {here}: {why}"),
            "land-here-ok",
        );
        return Route::Escaped(format!(
            "land: {ESCAPE} - landing outside the lane's tree, recorded: {why}"
        ));
    }
    record(
        root,
        "blocked",
        &format!("{feature} {t} in {here}"),
        "outside-the-lane",
    );
    let lane = lane.map_or_else(
        || "no lane tree is adopted yet (make builder-tree-adopt TREE=<clone>-land)".to_owned(),
        |l| format!("its tree is {}", l.display()),
    );
    Route::Refused(format!(
        "land: refused - nothing ran: a landing runs only in the landing lane's tree, not {here}; {lane} (461 T29).\n  \
         Hand the work in: make builder-done T=<task> F={feature} MSG=\"<subject>\" - make lane-start starts the lane, which lands it.\n  \
         Only where the lane itself cannot land: {ESCAPE}=\"<why the lane cannot>\" make land F={feature} T=\"{t}\" NOTE=\"<what was verified>\" (recorded)"
    ))
}

/// One guard-log entry of the route, into the root's environment's `GUARD_LOG_DIR` where it names one, else the log's own; never fails.
fn record(root: &Rooted, event: &str, detail: &str, rule: &str) {
    let detail: String = detail.chars().take(400).collect();
    let dir = root
        .opt("GUARD_LOG_DIR")
        .filter(|d| !d.is_empty())
        .map_or_else(l7r_shared::log::dir, PathBuf::from);
    let _ = l7r_shared::log::write_at(
        &dir,
        &Entry {
            guard: GUARD,
            event,
            detail: &detail,
            rule,
            context: None,
            input: &Value::Null,
            session_name: "",
        },
        std::time::SystemTime::now(),
    );
}

#[cfg(test)]
pub(super) mod tests;

//! THE DISK AND THE BUILD CACHE (feature 451 T158; the GM 2026-11-22: "make sure that we clean up after ourselves in terms of the file
//! system to not have 30 gigs of stuff suddenly get eaten without us realizing it"). On 2026-11-22 the disk (461 GB) reached 100% at
//! about 17:05, 485 MB free, and every builder's coverage run failed "No space left on device": `~/.cache/l7r-cargo-target` held the
//! clone's 86 GB, the landing worktree's 31 GB and ~30 GB of idle scratch worktrees' targets, which the session removed by hand. The
//! day's sweep (`sweep/cargo.rs`) had removed none of it: its threshold is three days, and the scratch targets were hours old.
//!
//! 451 T245 added `audit` (`make disk-audit`, `disk/audit.rs`), and `evict` / `evict-dry`, the low-disk trigger's eviction
//! (`disk/low.rs`), which a prompt starts below `L7R_DISK_FREE_PCT` free.
//!
//! The modes of `--scratch-sweep`:
//! - `floor`: `make done`, `make land` and `make closing-checks` refuse first when the cache's disk has less free than the floor,
//!   naming the free space, the largest build directories, what `make cache-clean` would free and the scratch worktrees to remove.
//! - `cache` / `cache-dry`: `make cache-clean`, the cache's share of the sweep alone, idle past `L7R_CACHE_IDLE_HOURS` (not three
//!   days), and nothing at all while any cargo, rustc or clippy process runs.
//! - `landed <feature> <task-starts.jsonl> <task>...`: `make land`'s last step once it lands, the landed tasks' own `/tmp/t<N>`
//!   scratch removed (`sweep/tmp.rs`) and their directories in the git directory holding `task-starts.jsonl` - `t<N>...` and
//!   `l7r-handoffs/T<N>-...` (451 T246, `sweep/leftovers.rs`) - and every clean scratch worktree idle past the scratch threshold
//!   (`sweep/trees.rs`).
//! - `trees`: the scratch worktrees (a registered worktree of a clone or the mirror outside the clones directory), each with the
//!   command that removes it; `make land` prints the ones left at its end (a modified or untracked file, a commit no ref holds,
//!   touched lately, or held), so a builder's hand-made worktree is named when its task lands.

use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::json;

use super::sweep::{self, Item};
use super::{locked_by, record, report, Config};
use crate::protocol::Reply;

/// THE FLOOR (GUESS, a knob: `L7R_DISK_FLOOR_GB`): above what one gate run writes with another builder's beside it. Measured
/// 2026-11-22: one landing's warm gate (12:10-12:16) left 4.56 GB of new files in the landing target (method: `find -newermt` over
/// the window, blocks summed), and that target took 24.77 GB since midnight; a cold coverage build of every crate is the landing
/// target's 31 GB. Fifteen is three warm gates side by side; a cold full run needs more, which the refusal's listing frees.
pub(super) const FLOOR_GB: f64 = 15.0;
/// How long a dead tree's build directory or a crate's old variant sits idle before `make cache-clean` takes it (GUESS, a knob:
/// `L7R_CACHE_IDLE_HOURS`): half a day, past any one builder's run (the longest closing run 601 s, 451 T55's measurement), short
/// enough that a scratch tree's target from the morning is gone by the evening.
pub(super) const IDLE_HOURS: f64 = 12.0;
/// THE CACHE'S SIZE BUDGET (GUESS, a knob: `L7R_CACHE_BUDGET_GB`), from the day's figures (2026-11-22): the warm landing target, a
/// full set of every crate's test, coverage and tool builds kept across a day of landings, is 31 GB; the clone's holds the same set
/// plus its builders' variants (86 GB before the prune, 14 GB of it variants past the sixteen idle a day); the mirror's 5 GB and the
/// research archive's 3 GB - a working set near 80 GB, and 20 over it for a cold build in flight. The other 37 GB that day was dead
/// trees' targets and old variants.
pub(super) const BUDGET_GB: f64 = 100.0;
/// How long before its profile's last use a crate's build inside a live profile goes unread before the prune takes it (GUESS, a knob:
/// `L7R_CACHE_STALE_HOURS`, 451 T515; floored at 25 h, `sweep/prune.rs`): two days, twice the day a `relatime` atime can lag a read.
/// Measured 2026-11-27 on the real cache, stat alone: 30 h would take 111.6 GB, 48 h 85.0 GB, 72 h 76.5 GB.
pub(super) const STALE_HOURS: f64 = 48.0;
/// How long a `/tmp` scratch entry or a task output sits idle before the sweep takes it (GUESS, a knob: `SCRATCH_SWEEP_TMP_HOURS`,
/// `SCRATCH_SWEEP_OUTPUT_HOURS`): a day - the host's measurement split 63 GB of scratch at "idle over a day" (27 GB), and a builder
/// back at a trial's scratch after a night still finds it.
pub(super) const TMP_HOURS: f64 = 24.0;
/// THE LOW-DISK TRIGGER (451 T245, GUESS, a knob: `L7R_DISK_FREE_PCT`, the GM's "a certain percentage of free space"): below this
/// share of the disk free, the next prompt starts the cache's eviction. Twenty percent of the 461 GB disk is 92 GB: six of the cold
/// 14 GB trial builds of 2026-11-25 side by side, or two cold full coverage builds (31 GB each, 2026-11-22), before the floor (15 GB).
pub(super) const FREE_PCT: f64 = 20.0;
/// How long a review snapshot without the review tree's `tree.json` sits idle before the sweep takes it, in days (451 T246, GUESS, a
/// knob: `SCRATCH_SWEEP_SNAPSHOT_DAYS`): a week, 16 times the oldest read measured - 245 review dispatches, each at most 10.6 h after
/// its unit's snapshot was taken (2026-11-25, the transcripts; `sweep/leftovers.rs`).
pub(super) const SNAPSHOT_DAYS: f64 = 7.0;
/// How many of the largest build directories the refusal names.
const NAMED: usize = 6;

mod audit;
mod low;
pub(super) use audit::audit;
pub(super) use low::{evict, note, trigger};

/// The size and free bytes of the filesystem holding `dir` (`df -B1 --output=size,avail`); None where df cannot say.
pub(super) fn df(dir: &Path) -> Option<(u64, u64)> {
    let out = Command::new("df")
        .args(["-B1", "--output=size,avail"])
        .arg(dir)
        .output()
        .ok()?;
    let text = String::from_utf8_lossy(&out.stdout);
    let mut words = text.lines().last()?.split_whitespace();
    Some((words.next()?.parse().ok()?, words.next()?.parse().ok()?))
}

/// The free bytes of the filesystem holding `dir` (`df -B1 --output=avail`); None where df cannot say.
pub(super) fn free(dir: &Path) -> Option<u64> {
    let out = Command::new("df")
        .args(["-B1", "--output=avail"])
        .arg(dir)
        .output()
        .ok()?;
    String::from_utf8_lossy(&out.stdout)
        .lines()
        .last()?
        .trim()
        .parse()
        .ok()
}

/// `floor`: silent above the floor; below it, refused with what to clear; unchecked (said, not refused) where df cannot say.
pub(super) fn floor(c: &Config, free: Option<u64>, now: SystemTime) -> Reply {
    let say = |stderr: String, code: i32| Reply {
        stdout: String::new(),
        stderr,
        code,
    };
    match free {
        None => say(
            format!(
                "disk floor: the free space of {} could not be read (df); not checked\n",
                c.cargo.display()
            ),
            0,
        ),
        Some(f) if f >= c.floor => say(String::new(), 0),
        Some(f) => say(refusal(c, f, now), 1),
    }
}

fn refusal(c: &Config, free: u64, now: SystemTime) -> String {
    let mut out = vec![
        format!(
            "REFUSED: {} free on the build cache's disk, below the {} floor (L7R_DISK_FLOOR_GB, a GUESS knob; 451 T158) - a gate run \
             writes gigabytes, and on 2026-11-22 a full disk failed every builder's coverage run.",
            gb(free),
            gb(c.floor)
        ),
        format!("The largest build directories under {}:", c.cargo.display()),
    ];
    for t in sweep::targets(c).into_iter().take(NAMED) {
        let whose = if t.live {
            "a live tree's: old variants pruned, idle profiles taken past the budget"
        } else {
            "no live tree's: removed whole once proven dead"
        };
        out.push(format!(
            "  {:>9}  {}  ({whose}; idle {})",
            gb(t.bytes),
            t.name,
            hours(now, t.newest)
        ));
    }
    let cutoff = now.checked_sub(c.cache_age).unwrap_or(UNIX_EPOCH);
    let (plan, build) = sweep::cache_plan(c, cutoff, now, 0);
    out.push(format!(
        "make cache-clean frees {} now ({} entries idle {} h or more, or stale in a live profile; DRY=1 lists them, HOURS=<n> moves \
         the threshold).",
        gb(plan.iter().map(|i| i.bytes).sum()),
        plan.len(),
        c.cache_age.as_secs() / 3600
    ));
    if let Some(build) = build {
        out.push(format!(
            "The rest waits for the build that runs now ({build}); run make cache-clean again once that build ends."
        ));
    }
    out.extend(trees(c, now));
    out.push(
        "Free space (make cache-clean; a scratch worktree by the command above), then run this again. Past the floor knowingly: \
         DISK_OK=\"<reason>\", recorded."
            .to_owned(),
    );
    out.join("\n") + "\n"
}

/// `cache` / `cache-dry`: the cache's share of the sweep, idle past `cache_age`, refused while a build runs or another sweep holds
/// the lock; each removal and the total on the guard log; the scratch worktrees named after.
pub(super) fn cache(c: &Config, now: SystemTime, dry: bool) -> Reply {
    let cutoff = now.checked_sub(c.cache_age).unwrap_or(UNIX_EPOCH);
    let run = || -> (String, Option<String>) {
        let (plan, build) = sweep::cache_plan(c, cutoff, now, 0);
        if dry {
            return (report(&plan, "would remove"), build);
        }
        let removed: Vec<Item> = plan.into_iter().filter(|i| sweep::take(c, i)).collect();
        let input = json!({ "session_id": c.keep });
        for item in &removed {
            record(
                &input,
                "removed",
                &item.path.to_string_lossy(),
                json!({ "bytes": item.bytes, "why": item.why, "by": "cache-clean" }),
            );
        }
        let total: u64 = removed.iter().map(|i| i.bytes).sum();
        record(
            &input,
            "swept",
            &format!(
                "cache-clean: {} removed, {} freed",
                removed.len(),
                gb(total)
            ),
            json!({ "count": removed.len(), "bytes": total, "by": "cache-clean" }),
        );
        (report(&removed, "removed"), build)
    };
    let result = if dry { Some(run()) } else { locked_by(c, run) };
    let tail: String = trees(c, now).into_iter().map(|t| t + "\n").collect();
    match result {
        Some((text, None)) => Reply {
            stdout: text + &tail,
            stderr: String::new(),
            code: 0,
        },
        // the prune inside live profiles runs beside a build elsewhere (451 T515); the rest waits for it
        Some((text, Some(build))) => Reply {
            stdout: text + &tail,
            stderr: format!(
                "cache-clean: a build runs ({build}), so only the stale builds in live profiles were taken: run it again once \
                 that build ends\n"
            ),
            code: 1,
        },
        None => Reply {
            stdout: tail,
            stderr: "cache-clean: another sweep holds the lock; run it again once it ends\n"
                .to_owned(),
            code: 1,
        },
    }
}

/// `landed <feature> <task-starts.jsonl> <task>...` (`make land`'s last step, after a landing that pushed): the landed tasks' own
/// `/tmp/t<N>` scratch removed, each and the total on the guard log; a number another feature started within the day said and left.
pub(super) fn landed(c: &Config, args: &[String], now: SystemTime) -> Reply {
    let (Some(feature), Some(starts)) = (args.first(), args.get(1)) else {
        return Reply {
            stdout: String::new(),
            stderr:
                "usage: l7r-guard --scratch-sweep landed <feature> <task-starts.jsonl> <task>...\n"
                    .to_owned(),
            code: 2,
        };
    };
    let numbers: Vec<u64> = args[2..]
        .iter()
        .flat_map(|a| a.split([',', ' ']))
        .filter_map(|t| t.trim().trim_start_matches('T').parse().ok())
        .collect();
    let (gone, shared) = sweep::landed_plan(c, feature, &numbers, Path::new(starts), now);
    // ...and their scratch in the clone's git directory, the one `task-starts.jsonl` is in (451 T246, `sweep/leftovers.rs`)
    let ours: Vec<u64> = numbers
        .iter()
        .copied()
        .filter(|n| !shared.contains(n))
        .collect();
    let git = Path::new(starts).parent().unwrap_or(Path::new(""));
    // ...and their started-task marks, beside it (451 T254): a landed task is no longer being worked in any tree
    let ids: Vec<String> = args[2..]
        .iter()
        .flat_map(|a| a.split([',', ' ']))
        .map(str::trim)
        .filter(|t| t.starts_with('T'))
        .map(str::to_owned)
        .collect();
    crate::shared::speckit::marks::remove(git, feature, &ids);
    let removed: Vec<Item> = gone
        .into_iter()
        .chain(sweep::landed_leftovers(c, git, &ours))
        .filter(sweep::remove)
        .collect();
    let input = json!({ "session_id": c.keep });
    for item in &removed {
        record(
            &input,
            "removed",
            &item.path.to_string_lossy(),
            json!({ "bytes": item.bytes, "why": item.why, "by": "land" }),
        );
    }
    let mut text = if removed.is_empty() {
        String::new()
    } else {
        report(&removed, "removed")
    };
    // the clean scratch worktrees idle past the scratch threshold (451 T158's plan review): removed, not only named
    let cleaned = sweep::clean_trees(c, now);
    for tree in &cleaned {
        record(
            &input,
            "removed",
            &tree.to_string_lossy(),
            json!({ "why": "a clean scratch worktree, idle, its HEAD on a ref", "by": "land" }),
        );
        let _ = writeln!(
            text,
            "removed the clean scratch worktree {} (idle, its HEAD on a ref; git worktree remove)",
            tree.display()
        );
    }
    // ...and each one's build directory with it (451 T245)
    for item in sweep::gone_targets(c, &cleaned)
        .into_iter()
        .filter(|i| sweep::take(c, i))
    {
        record(
            &input,
            "removed",
            &item.path.to_string_lossy(),
            json!({ "bytes": item.bytes, "why": item.why, "by": "land" }),
        );
        let _ = writeln!(
            text,
            "removed {} ({}, {})",
            item.path.display(),
            gb(item.bytes),
            item.why
        );
    }
    for n in shared {
        let _ = writeln!(
            text,
            "left /tmp/t{n}* to the sweep's age rule: another feature started a T{n} within the day"
        );
    }
    Reply {
        stdout: text,
        stderr: String::new(),
        code: 0,
    }
}

/// One line a scratch worktree - a registered worktree of a clone or the mirror whose tree is outside the clones directory and is
/// not the mirror - with its idle time, the build directory its name shares, and the command that removes it.
pub(super) fn trees(c: &Config, now: SystemTime) -> Vec<String> {
    let all = sweep::worktrees(c);
    let name = |p: &Path| p.file_name().map(|n| n.to_string_lossy().into_owned());
    all.iter()
        .filter(|w| !w.tree.starts_with(&c.clones) && w.tree != c.mirror)
        .map(|w| {
            let shared = all
                .iter()
                .filter(|o| name(&o.tree) == name(&w.tree))
                .count();
            let idle = sweep::newest(&w.admin).unwrap_or(UNIX_EPOCH);
            format!(
                "scratch worktree {} (of {}, idle {}; builds into {}/{}, a name {shared} registered tree(s) share): once its task has \
                 landed, remove it with  git -C {} worktree remove --force {}  - then make cache-clean takes its build directory",
                w.tree.display(),
                w.repo.display(),
                hours(now, idle),
                c.cargo.display(),
                name(&w.tree).unwrap_or_default(),
                w.repo.display(),
                w.tree.display()
            )
        })
        .collect()
}

/// Bytes as gigabytes, to one place.
fn gb(bytes: u64) -> String {
    let tenths = bytes / 100_000_000;
    format!("{}.{} GB", tenths / 10, tenths % 10)
}

/// How long since `then`, in hours to one place (0 for a time ahead of `now`).
fn hours(now: SystemTime, then: SystemTime) -> String {
    let tenths = now.duration_since(then).map_or(0, |d| d.as_secs() / 360);
    format!("{}.{} h", tenths / 10, tenths % 10)
}

#[cfg(test)]
mod tests;

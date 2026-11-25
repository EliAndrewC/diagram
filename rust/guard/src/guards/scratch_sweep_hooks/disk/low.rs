//! THE LOW-DISK TRIGGER (451 T245; the GM 2026-11-25: "we might even want to trigger something automatically if our disk space ever
//! drops below a certain percentage of free space"). A prompt reads the cache's disk (`df`, one process: the hook stays cheap); below
//! `L7R_DISK_FREE_PCT` free it starts `--scratch-sweep evict`, detached, at most once an hour (`EVERY`: a disk with nothing the eviction
//! may take would otherwise walk the 180 GB cache on every prompt). The eviction takes what `make cache-clean` takes, and live trees'
//! idle profiles (`sweep/evict.rs`) until the cache is within its budget and the disk back at the share free, whichever asks more; it
//! writes one line of what it freed, which the next prompt says and removes. A build running anywhere holds it, its stamp removed so
//! the next prompt tries again.

use std::fs::File;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::json;

use super::super::{locked_by, record, sweep, Config};
use super::gb;
use crate::protocol::Reply;

/// At most one eviction this often (GUESS, a constant): an eviction's walk of the measured cache took 23 s (2026-11-25, `time make
/// cache-clean DRY=1`); an hour lets a disk filling under a day's builds be caught within it.
const EVERY: Duration = Duration::from_secs(3600);

fn stamp(c: &Config) -> PathBuf {
    c.state.join("evict-stamp")
}

fn said(c: &Config) -> PathBuf {
    c.state.join("evicted")
}

/// The bytes short of the free-space share; 0 at or above it, or where the disk cannot be read.
fn short(c: &Config) -> u64 {
    c.disk().map_or(0, |(size, free)| {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            clippy::cast_precision_loss,
            reason = "a share of a disk's bytes, finite and non-negative"
        )]
        let want = (size as f64 * c.free_at) as u64;
        want.saturating_sub(free)
    })
}

/// The hook's half: below the share free and no eviction within the hour, start one, detached; whether it started.
pub(in super::super) fn trigger(c: &Config, keep: &str, now: SystemTime) -> bool {
    if short(c) == 0 {
        return false;
    }
    let recent = std::fs::metadata(stamp(c))
        .and_then(|m| m.modified())
        .is_ok_and(|t| now.duration_since(t).is_ok_and(|d| d < EVERY));
    if recent || std::fs::create_dir_all(&c.state).is_err() {
        return false;
    }
    let _ = File::create(stamp(c)).and_then(|f| f.set_modified(now));
    let _ = Command::new("setsid")
        .arg("-f")
        .arg(&c.exe)
        .args(["--scratch-sweep", "evict", "--keep", keep])
        .current_dir("/")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    true
}

/// The line the last eviction wrote, said once: read and removed.
pub(in super::super) fn note(c: &Config) -> Option<String> {
    let text = std::fs::read_to_string(said(c)).ok()?;
    std::fs::remove_file(said(c)).ok()?;
    Some(text.trim().to_owned()).filter(|t| !t.is_empty())
}

/// `evict` (the trigger's) and `evict-dry` (what it would take): the cache's plan with the disk's shortfall, under the sweep's lock.
pub(in super::super) fn evict(c: &Config, now: SystemTime, dry: bool) -> Reply {
    let short = short(c);
    let cutoff = now.checked_sub(c.cache_age).unwrap_or(UNIX_EPOCH);
    // the age shares first (451 T246: the amendment's "an age sweep ... at session start and at the low-disk trigger"), a build
    // running or not; the cache's share then, which a build holds
    let run = || -> (Vec<sweep::Item>, Result<String, String>) {
        let removed = |plan: Vec<sweep::Item>| -> Vec<sweep::Item> {
            if dry {
                return plan;
            }
            let gone: Vec<sweep::Item> = plan.into_iter().filter(|i| sweep::take(c, i)).collect();
            let input = json!({ "session_id": c.keep });
            for item in &gone {
                record(
                    &input,
                    "removed",
                    &item.path.to_string_lossy(),
                    json!({ "bytes": item.bytes, "why": item.why, "by": "low-disk" }),
                );
            }
            gone
        };
        let mut items = removed(sweep::aged_plan(c, now));
        let verb = if dry { "would remove" } else { "removed" }.to_owned();
        match sweep::cache_plan(c, cutoff, now, short) {
            Ok(plan) => {
                items.extend(removed(plan));
                (items, Ok(verb))
            }
            Err(build) => (items, Err(build)),
        }
    };
    let result = if dry { Some(run()) } else { locked_by(c, run) };
    let pct = (c.free_at * 100.0).round();
    let (stdout, code) = match result {
        Some((items, Ok(verb))) => {
            let total: u64 = items.iter().map(|i| i.bytes).sum();
            // `make disk-audit` asks this dry with the disk above the share too: not "under" then (451 T246)
            let disk = if short > 0 { "under" } else { "at or above" };
            let line = if items.is_empty() {
                format!(
                    "disk {disk} {pct}% free (L7R_DISK_FREE_PCT): the eviction found nothing it may take - every build directory \
                     in use or built within {} h; make disk-audit lists what holds the disk",
                    c.cache_age.as_secs() / 3600
                )
            } else {
                format!(
                    "disk {disk} {pct}% free (L7R_DISK_FREE_PCT): the eviction {verb} {} of the idle scratch and the build cache \
                     ({} entries; make disk-audit lists the rest)",
                    gb(total),
                    items.len()
                )
            };
            // "nothing it may take" said once until an eviction frees something again: the disk can stay under the share with
            // nothing evictable (2026-11-25: 62 GB free, 30.5 GB evictable, 18.7% after), and an hourly repeat says nothing new
            let quiet = c.state.join("evict-nothing");
            if !dry {
                if !items.is_empty() || !quiet.exists() {
                    let _ = std::fs::write(said(c), format!("{line}\n"));
                }
                if items.is_empty() {
                    let _ = File::create(&quiet);
                } else {
                    let _ = std::fs::remove_file(&quiet);
                }
            }
            (super::super::report(&items, &verb) + &line + "\n", 0)
        }
        Some((items, Err(build))) => {
            // a build holds the cache's share: tried again at the next prompt, not in an hour
            if !dry {
                let _ = std::fs::remove_file(stamp(c));
            }
            let aged = if items.is_empty() {
                String::new()
            } else {
                super::super::report(&items, if dry { "would remove" } else { "removed" })
            };
            (
                format!(
                    "{aged}evict: a build runs ({build}); nothing of the build cache removed\n"
                ),
                1,
            )
        }
        None => ("evict: another sweep holds the lock\n".to_owned(), 1),
    };
    Reply {
        stdout,
        stderr: String::new(),
        code,
    }
}

#[cfg(test)]
mod tests;

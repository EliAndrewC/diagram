//! The backfill (`archive.py backfill`, `make archive-sources`; ported by feature 449 T146): every cited URL with no row archived, in
//! lanes that never ask one host twice at once, each lane its own browser; the Python's lanes were processes, these are threads, each
//! holding its own `l7r-browser serve`.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::{Arc, Mutex};

use l7r_gate_research::record::archive::Cited;
use serde_json::Value;

use crate::client::netloc;
use crate::fetch::Client;
use crate::manifest::{archive_url, owed, report, settle, LOCK_WAIT};
use crate::store::Archive;
use crate::{Error, Result};

/// The backfill pushes once this much is committed and unpushed (plan D9: far under GitHub's 2 GB push limit, and a stopped run loses at
/// most one batch's push - the captures stay in the working copy for the next run).
pub const PUSH_EVERY: u64 = 200 * (1 << 20);
/// A backfill lane starts a fresh browser this often, so a lane's memory stays bounded: the containers share a 10 GB cap, and two
/// lanes' browsers had grown to 1.8 GB (one renderer 0.7 GB) partway through the first backfill (observed 2026-10-02 at the host's
/// low-memory warning).
#[cfg(not(test))]
pub const RECYCLE_EVERY: usize = 25;
/// ...and every third in the crate's own tests, whose lane test archived 26 URLs to reach one recycle, a push tried after each - 140 ms of
/// git against FR-008's tenth of a second (feature 449 T167, observed 2026-11-17). The uncited crate builds against the 25.
#[cfg(test)]
pub const RECYCLE_EVERY: usize = 3;

/// `urls` dealt into `n` lanes, every URL of one host in one lane (plan D8: never two requests to a host at once).
#[must_use]
pub fn lanes(urls: &[String], n: usize) -> Vec<Vec<String>> {
    let mut by_host: Vec<(String, Vec<String>)> = Vec::new();
    for u in urls {
        let host = netloc(u);
        match by_host.iter_mut().find(|(h, _)| *h == host) {
            Some((_, v)) => v.push(u.clone()),
            None => by_host.push((host, vec![u.clone()])),
        }
    }
    by_host.sort_by_key(|(_, v)| std::cmp::Reverse(v.len()));
    let mut out: Vec<Vec<String>> = vec![Vec::new(); n.max(1)];
    for (_, host_urls) in by_host {
        if let Some(lane) = out.iter_mut().min_by_key(|l| l.len()) {
            lane.extend(host_urls);
        }
    }
    out.into_iter().filter(|l| !l.is_empty()).collect()
}

/// What a lane needs: the repository, who cites each URL, how a browser starts, and where each outcome line goes.
pub struct Lane<'a> {
    pub root: &'a Path,
    pub who: &'a [(String, Cited)],
    pub start: &'a (dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync),
    pub say: &'a (dyn Fn(&str) + Sync),
}

/// One lane: each URL archived unpushed, its outcome line said, a fresh browser every [`RECYCLE_EVERY`], and a push whenever the
/// unpushed bytes pass [`PUSH_EVERY`].
///
/// # Errors
/// The first URL the Python would have raised on.
pub fn lane(
    how: &Lane<'_>,
    urls: &[String],
    store: &Archive,
) -> Result<Vec<serde_json::Map<String, Value>>> {
    let mut client = (how.start)(how.root)?;
    let mut out = Vec::new();
    for (n, url) in urls.iter().enumerate() {
        if (n + 1) % RECYCLE_EVERY == 0 {
            // a long-lived browser grows: two lanes held 1.8 GB after ~600 pages (2026-10-02)
            drop(client);
            client = (how.start)(how.root)?;
        }
        let who = how
            .who
            .iter()
            .find(|(u, _)| u == url)
            .map(|(_, c)| c.clone())
            .unwrap_or_default();
        let row = archive_url(how.root, url, &who, client.as_mut(), store, false)?;
        let outcome = row
            .get("outcome")
            .map_or_else(String::new, l7r_shared::pyjson::py_str);
        (how.say)(&format!("{outcome:26} {url}"));
        out.push(row);
        if store.unpushed() >= PUSH_EVERY {
            let _held = store.locked(LOCK_WAIT)?;
            // asked again under the lock: another lane may have pushed while this one waited
            let failure = (store.unpushed() >= PUSH_EVERY)
                .then(|| store.push())
                .transpose()?
                .unwrap_or_default();
            if !failure.is_empty() {
                (how.say)(&format!("push failed: {failure}"));
            }
        }
    }
    Ok(out)
}

/// `make archive-sources`: the owed URLs in up to `workers` lanes, the last push, the held rows settled, then the coverage table.
///
/// # Errors
/// A lane's error, as the Python's pool re-raised it; the record's refusal.
pub fn backfill(
    root: &Path,
    workers: usize,
    start: &(dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync),
    out: &(dyn Fn(&str) + Sync),
    err: &mut String,
    store: &Archive,
) -> Result<i32> {
    let todo = owed(root)?;
    out(&format!(
        "archive: {} cited URL(s) owed a copy, in up to {workers} lane(s)",
        todo.len()
    ));
    {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
    }
    let who = l7r_gate_research::record::archive::cited(&root.join("research"))?;
    let mut urls: Vec<String> = todo.into_iter().map(|(u, _)| u).collect();
    urls.sort();
    let jobs = lanes(&urls, workers);
    let first_error: Arc<Mutex<Option<Error>>> = Arc::new(Mutex::new(None));
    std::thread::scope(|s| {
        for job in &jobs {
            let (who, first_error) = (&who, Arc::clone(&first_error));
            s.spawn(move || {
                let how = Lane {
                    root,
                    who,
                    start,
                    say: out,
                };
                if let Err(e) = lane(&how, job, store) {
                    if let Ok(mut f) = first_error.lock() {
                        f.get_or_insert(e);
                    }
                }
            });
        }
    });
    if let Some(e) = first_error.lock().ok().and_then(|mut f| f.take()) {
        return Err(e);
    }
    let failure = {
        let _held = store.locked(LOCK_WAIT)?;
        store.push()?
    };
    if !failure.is_empty() {
        let _ = writeln!(
            err,
            "archive: the final push failed - {failure}; the captures wait in {}",
            store.dir.display()
        );
        return Ok(1);
    }
    settle(root)?;
    let mut table = String::new();
    let code = report(root, &mut table)?;
    out(table.trim_end_matches('\n'));
    Ok(code)
}

#[cfg(test)]
mod tests;

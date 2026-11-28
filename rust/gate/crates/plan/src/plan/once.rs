//! ONE READ OF EACH FILE A CALL (462 T543): inside [`held`], a file read through this module is read from disk once and served from
//! memory after, the review record parsed once; outside it every read goes to disk, as before. WHY: `make plan-delta` read 451's
//! plan-done.md eleven times a call (40,017,934 bytes of a 3,637,994-byte file) and plan-review.json twice (10,052,046 bytes), its
//! helpers each reading the records afresh - the earlier-text check of every changed block read all of plan-done.md (observed
//! 2026-11-27, an `LD_PRELOAD` read counter on a copy, `dev/measurements/2026-11-27/t536-record-readers/results.md`).
//!
//! Only `plan delta` holds its reads: it writes none of the files it reads (its bundle goes under the bundles root, an escape it takes
//! to the guard log), so nothing it serves is stale. A caller that writes a record between its reads (decide, tick, record) holds
//! nothing, and its reads through here are plain reads.

use std::cell::RefCell;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

use serde_json::{json, Value};

use super::status::RECORD;

/// The texts read while held, by path (`None`: no file there, or not text), and the review records parsed, by feature directory.
#[derive(Default)]
struct Held {
    texts: HashMap<PathBuf, Option<String>>,
    records: HashMap<PathBuf, Rc<Value>>,
}

thread_local! {
    static HELD: RefCell<Option<Held>> = const { RefCell::new(None) };
}

#[cfg(test)]
thread_local! {
    /// Each path's reads from disk through this module on this thread, for the tests.
    static READS: RefCell<HashMap<PathBuf, usize>> = RefCell::new(HashMap::new());
}

/// Ends the hold, a panic's unwinding included, and puts back the one it replaced.
struct Release(Option<Held>);

impl Drop for Release {
    fn drop(&mut self) {
        let before = self.0.take();
        HELD.with(|h| *h.borrow_mut() = before);
    }
}

/// `f`'s value, every read through this module during it held: each file read from disk once.
pub(super) fn held<T>(f: impl FnOnce() -> T) -> T {
    let before = HELD.with(|h| h.borrow_mut().replace(Held::default()));
    let _release = Release(before);
    f()
}

/// The text of `path`, or None where it cannot be read as text.
pub(super) fn read(path: &Path) -> Option<String> {
    if let Some(have) = HELD.with(|h| {
        h.borrow()
            .as_ref()
            .and_then(|held| held.texts.get(path).cloned())
    }) {
        return have;
    }
    #[cfg(test)]
    READS.with(|r| *r.borrow_mut().entry(path.to_owned()).or_default() += 1);
    let got = std::fs::read_to_string(path).ok();
    HELD.with(|h| {
        if let Some(held) = h.borrow_mut().as_mut() {
            held.texts.insert(path.to_owned(), got.clone());
        }
    });
    got
}

/// The text of `path`, or "".
pub(super) fn text(path: &Path) -> String {
    read(path).unwrap_or_default()
}

/// Every archived plan section of `dir` (`archive::plan_done`, its parts and flat file read through here).
pub(super) fn plan_done(dir: &Path) -> String {
    use l7r_shared::speckit::archive;
    archive::text(&|rel| read(&dir.join(rel)), archive::PLAN_DONE)
}

/// The archived tasks of `dir`, or "" (`tasks::done_text`, its parts and flat file read through here).
pub(super) fn tasks_done(dir: &Path) -> String {
    use l7r_shared::speckit::{archive, tasks};
    if dir.join(archive::DIR).is_dir() {
        return archive::text(&|rel| read(&dir.join(rel)), tasks::DONE);
    }
    text(&dir.join(tasks::DONE))
}

/// `dir`'s review record, parsed (an empty object where it is missing or no JSON).
pub(super) fn record(dir: &Path) -> Rc<Value> {
    if let Some(have) = HELD.with(|h| {
        h.borrow()
            .as_ref()
            .and_then(|held| held.records.get(dir).cloned())
    }) {
        return have;
    }
    let parsed =
        Rc::new(serde_json::from_str(&text(&dir.join(RECORD))).unwrap_or_else(|_| json!({})));
    HELD.with(|h| {
        if let Some(held) = h.borrow_mut().as_mut() {
            held.records.insert(dir.to_owned(), Rc::clone(&parsed));
        }
    });
    parsed
}

/// This thread's reads from disk through this module, by path, since the last call; the count is cleared.
#[cfg(test)]
pub(super) fn reads() -> HashMap<PathBuf, usize> {
    READS.with(|r| std::mem::take(&mut *r.borrow_mut()))
}

#[cfg(test)]
mod tests;

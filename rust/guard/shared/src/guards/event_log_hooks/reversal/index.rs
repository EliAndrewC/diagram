//! The reversal tripwire's DERIVED INDEX of a feature's log (feature 451 T443): every `PreToolUse` Edit line's path and `old`, kept
//! beside the log by the READER alone, so the tripwire reads the index and the log's tail since it instead of the whole log.
//!
//! THE INVARIANT: the answer is the index's rows for the bytes it covers plus the full read's scan ([`super::scan`]) of the rest, on
//! ONE open file, so an index that is stale, lost, torn or another log's costs a rebuild - time - and never a line. No writer keeps it in
//! step (`write_line`, the gate's `append_row*`, `make events-refile`, its retask and `state-sync.sh`'s merge write the log as before),
//! which is why T392 declined a side file kept by the writers: a line missing there is a missed reversal.
//!
//! WHAT TIES AN INDEX TO ITS LOG: the log's device and inode (refile's temporary file and rename, a rotation, `sed -i`, a new file of
//! the same name - each a new inode), the length it covers (a truncation is shorter), and the first and last [`WINDOW`] bytes of what
//! it covers, read back from the log at those offsets (a rewrite in place, same inode, changes them). Any disagreement, a header that
//! does not parse, a body of the wrong length or row count, is a rebuild by a full scan. WHAT IT CANNOT SEE (a deliberate limit): a
//! file with the same device and inode NUMBER (in place, or a new file given a freed inode's number), at least `covered` long, whose
//! first and last [`WINDOW`] bytes of the covered prefix are the index's, and whose bytes between them differ - seeing it would mean
//! reading the whole covered prefix, the cost this removes. No writer makes one: `write_line` and state-sync's merge append, and refile
//! replaces by rename a file whose dropped or moved lines shift the last window, and its retask changes a line's task, never its `path`
//! or `old`, so an index kept over it still answers as the full read (observed 2026-11-27, method: each writer's
//! code read, `event_log_hooks.rs` `write_line`, `refile.rs` `write_back`, `scripts/state-sync.sh` `merge_in`).
//!
//! WHERE IT LIVES: `<events dir>/reversal/<feature>.idx`, a DIRECTORY inside the log's own, under the common git dir, so never a file
//! a commit carries. Not a file beside the logs: `state-sync.sh`'s `commit` pushes every regular file of the events directory as a log
//! and its `merge_in` line-merges them back, which would append another clone's rows to an index; and `events.rs`' `lines_of` reads
//! every name there as a log. Both pass a directory over, as they pass `samples/` (451 T274).
//!
//! WHEN IT IS WRITTEN: on a rebuild, and when the log has grown more than [`STALE`] past what the index covers; otherwise the hook only
//! reads. Through a temporary file of the process's own and a rename, so a reader never meets half an index and two hooks racing to
//! write lose at most one's work: either index is whole and true of the log.

use std::fs::File;
use std::io::Read;
use std::os::unix::fs::{FileExt, MetadataExt};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use memchr::memmem::Finder;
use serde_json::Value;

use super::{scan, EDIT};

/// The event a kept line names, as its JSON holds it (451 T458): the build's second screen, after [`EDIT`]. A SUPERSET of the parse's
/// lines on the argument [`EDIT`] rests on: `PreToolUse` is printable ASCII with no quote and no backslash, so a writer that escapes no
/// more than JSON asks spells it one way, whatever it puts round the colon. Every writer of a log does: `write_line` and refile's moved
/// lines serialize through serde's compact `to_string`, which escapes only a quote, a backslash and a control character, and refile's
/// kept lines and `state-sync.sh`'s merge copy lines byte for byte (observed 2026-11-27, method: `write_line`, `refile.rs` and
/// `merge_in` read; all 9,176 `PreToolUse` Edit lines of the 34 real logs spell it `"ev":"PreToolUse"`). WHAT IT CANNOT SEE (a
/// deliberate limit, as [`EDIT`]'s): a line whose `ev` a writer spelled with a `\u` escape, kept by the parse, dropped here.
const PRE: &str = "\"PreToolUse\"";

/// The index's first word and version: a file without them is no index of this form, and is rebuilt.
const MAGIC: &str = "l7r-reversal-index 1";

/// The bytes at each end of the covered prefix the index keeps and checks against the log (a GUESS knob, 451 T443): 4 KiB holds the
/// last 10 to 15 lines of a log whose lines run 250 to 400 bytes (observed 2026-11-27, the 451 log's 169,220 lines over 44.4 MB).
const WINDOW: u64 = 4096;

/// How far the log may grow past the index before a hook rewrites it (a GUESS knob, 451 T443): the tail is scanned on every call
/// either way, about 0.5 ms a MB (`t392-results.md`), so this trades that scan against a write of the index.
const STALE: u64 = 1024 * 1024;

/// How old a temporary index file must be before a write sweeps it (a GUESS knob, 451 T459): a hook killed between [`store`]'s write
/// and its rename leaves one that nothing else removes; a running writer's is milliseconds to seconds old (a rebuild scans the whole
/// log between them: about 12 ms for the 451 log's 44.4 MB read a chunk at a time, measured 2026-11-27, `t392-results.md`), so an
/// hour is far past any writer still alive.
const SWEEP_AGE: std::time::Duration = std::time::Duration::from_secs(3600);

/// The index of a log at `log`: `<its directory>/reversal/<its stem>.idx`; None for a path with no directory or name.
pub(super) fn index_path(log: &Path) -> Option<PathBuf> {
    let stem = log.file_stem()?.to_string_lossy();
    Some(log.parent()?.join("reversal").join(format!("{stem}.idx")))
}

/// What ties an index to its log: the file's identity, the bytes it covers, and the bytes at each end of them.
#[derive(Debug, PartialEq)]
struct Tie {
    dev: u64,
    ino: u64,
    covered: u64,
    head: Vec<u8>,
    tail: Vec<u8>,
}

impl Tie {
    /// The tie of the open log's first `covered` bytes as the log holds them now; None where a window cannot be read.
    fn of(log: &File, covered: u64) -> Option<Tie> {
        let m = log.metadata().ok()?;
        let n = covered.min(WINDOW);
        let at = |from: u64| -> Option<Vec<u8>> {
            let mut b = vec![0; usize::try_from(n).ok()?];
            log.read_exact_at(&mut b, from).ok()?;
            Some(b)
        };
        Some(Tie {
            dev: m.dev(),
            ino: m.ino(),
            covered,
            head: at(0)?,
            tail: at(covered - n)?,
        })
    }
}

/// One row of the index: the path's JSON and the `old` digest's JSON (serde's compact text, which holds no raw tab or newline).
fn row(rows: &mut Vec<u8>, path: &Value, old: &Value) {
    rows.extend_from_slice(path.to_string().as_bytes());
    rows.push(b'\t');
    rows.extend_from_slice(old.to_string().as_bytes());
    rows.push(b'\n');
}

/// A log line's row where the full read would keep it for its path: valid UTF-8, a `PreToolUse` Edit with a `path` key (a line with
/// none matches no path, a null one included), its `old` Null where it has none - [`super::Kept::line`]'s test, for every path at once.
/// Whether the line was parsed, for the tests that count the build's parses. The scan hands over only lines holding [`EDIT`]; a line
/// is parsed only if it also holds [`PRE`] (451 T458), so a `PostToolUse` Edit line is dropped as text, not parsed.
fn indexed(line: &[u8], rows: &mut Vec<u8>) -> bool {
    if memchr::memmem::find(line, PRE.as_bytes()).is_none() {
        return false;
    }
    let Ok(l) = std::str::from_utf8(line) else {
        return false;
    };
    if !l.contains(EDIT) {
        return false;
    }
    let Ok(e) = serde_json::from_str::<Value>(l.trim()) else {
        return true;
    };
    if e.get("ev") == Some(&Value::from("PreToolUse"))
        && e.get("tool") == Some(&Value::from("Edit"))
    {
        if let Some(p) = e.get("path") {
            row(rows, p, e.get("old").unwrap_or(&Value::Null));
        }
    }
    true
}

/// The `old` of each row of `rows` whose path is `path`, in order: a string path compared as its one serialized spelling, any other
/// parsed and compared as the full read compares it.
fn matching(rows: &[u8], path: &Value, out: &mut Vec<Value>) {
    let spelled = path.is_string().then(|| path.to_string());
    for r in rows.split(|&b| b == b'\n').filter(|r| !r.is_empty()) {
        let Some(tab) = memchr::memchr(b'\t', r) else {
            continue;
        };
        let (p, old) = (&r[..tab], &r[tab + 1..]);
        let hit = match &spelled {
            Some(s) => p == s.as_bytes(),
            None => serde_json::from_slice::<Value>(p).is_ok_and(|v| v == *path),
        };
        if hit {
            out.push(serde_json::from_slice(old).unwrap_or(Value::Null));
        }
    }
}

/// The index's text: its header, the two windows and the rows.
fn encode(tie: &Tie, rows: &[u8]) -> Vec<u8> {
    let rows_n = memchr::memchr_iter(b'\n', rows).count();
    let mut out = format!(
        "{MAGIC} {} {} {} {} {} {} {rows_n}\n",
        tie.dev,
        tie.ino,
        tie.covered,
        tie.head.len(),
        tie.tail.len(),
        rows.len()
    )
    .into_bytes();
    out.extend_from_slice(&tie.head);
    out.extend_from_slice(&tie.tail);
    out.extend_from_slice(rows);
    out
}

/// An index's tie and rows; None for any text [`encode`] did not write whole.
fn decode(text: &[u8]) -> Option<(Tie, &[u8])> {
    let nl = memchr::memchr(b'\n', text)?;
    let header = std::str::from_utf8(&text[..nl]).ok()?.strip_prefix(MAGIC)?;
    let n: Vec<u64> = header
        .split(' ')
        .skip(1)
        .map(str::parse)
        .collect::<Result<_, _>>()
        .ok()?;
    let [dev, ino, covered, head, tail, len, rows_n] = n[..] else {
        return None;
    };
    let body = &text[nl + 1..];
    let (head, tail, len) = (
        usize::try_from(head).ok()?,
        usize::try_from(tail).ok()?,
        usize::try_from(len).ok()?,
    );
    if body.len() != head.checked_add(tail)?.checked_add(len)? {
        return None;
    }
    let rows = &body[head + tail..];
    if memchr::memchr_iter(b'\n', rows).count() as u64 != rows_n
        || rows.last().is_some_and(|&b| b != b'\n')
    {
        return None;
    }
    let tie = Tie {
        dev,
        ino,
        covered,
        head: body[..head].to_vec(),
        tail: body[head..head + tail].to_vec(),
    };
    Some((tie, rows))
}

/// The index at `idx` where it is true of the open log: its tie the log's own now. None for no index, an unreadable or torn one, or
/// one of another file or of bytes the log no longer holds.
fn load(idx: &Path, log: &File) -> Option<(u64, Vec<u8>)> {
    let text = std::fs::read(idx).ok()?;
    let (tie, rows) = decode(&text)?;
    let size = log.metadata().ok()?.len();
    (tie.covered <= size && Tie::of(log, tie.covered).as_ref() == Some(&tie))
        .then(|| (tie.covered, rows.to_vec()))
}

/// The open log read from an offset by position, so the file's own offset is never moved.
struct From<'a> {
    log: &'a File,
    at: u64,
}

impl Read for From<'_> {
    fn read(&mut self, out: &mut [u8]) -> std::io::Result<usize> {
        let n = self.log.read_at(out, self.at)?;
        self.at += n as u64;
        Ok(n)
    }
}

/// Every index's temporary file in `dir`, `.<name>.idx.<pid>.<n>.tmp`, older than [`SWEEP_AGE`], removed (451 T459): the one a hook
/// killed between [`store`]'s write and its rename leaves, which nothing else removes. Every feature's, not only the one being written:
/// the directory holds the indexes alone, and a feature whose index is never written again would keep its own for good. A file of
/// any other name, or one whose age cannot be read, is left.
fn sweep(dir: &Path) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for e in entries.map_while(Result::ok) {
        let name = e.file_name();
        let name = name.to_string_lossy();
        let temp = name
            .strip_prefix('.')
            .and_then(|n| n.strip_suffix(".tmp"))
            .and_then(|n| n.rsplit_once(".idx."))
            .is_some_and(|(stem, n)| {
                !stem.is_empty()
                    && n.split_once('.').is_some_and(|(pid, seq)| {
                        [pid, seq]
                            .iter()
                            .all(|d| !d.is_empty() && d.bytes().all(|b| b.is_ascii_digit()))
                    })
            });
        let old = e
            .metadata()
            .and_then(|m| m.modified())
            .ok()
            .and_then(|t| t.elapsed().ok())
            .is_some_and(|age| age > SWEEP_AGE);
        if temp && old {
            let _ = std::fs::remove_file(e.path());
        }
    }
}

/// The index written over `idx` through a temporary file of this process's own and a rename; a failure leaves what was there.
fn store(idx: &Path, tie: &Tie, rows: &[u8]) {
    static SEQ: AtomicU64 = AtomicU64::new(0);
    let (Some(dir), Some(name)) = (idx.parent(), idx.file_name()) else {
        return;
    };
    let tmp = dir.join(format!(
        ".{}.{}.{}.tmp",
        name.to_string_lossy(),
        std::process::id(),
        SEQ.fetch_add(1, Ordering::Relaxed)
    ));
    sweep(dir);
    let ok =
        std::fs::create_dir_all(dir).is_ok() && std::fs::write(&tmp, encode(tie, rows)).is_ok();
    if !(ok && std::fs::rename(&tmp, idx).is_ok()) {
        let _ = std::fs::remove_file(&tmp);
    }
}

/// The `old` digest of each earlier Edit of `path` in the open log at `log`, in the log's order: [`super::replaced`]'s answer, read
/// from the index for the bytes it covers and by the full read's scan, `chunk` bytes at a time, for the rest. The index is rebuilt
/// where it is not true of the log, and rewritten where the log has grown past it by more than [`STALE`].
pub(super) fn olds(log: &File, at: &Path, path: &Value, chunk: usize) -> Vec<Value> {
    let idx = index_path(at);
    let kept = idx.as_deref().and_then(|i| load(i, log));
    let fresh = kept.is_none();
    let (start, mut rows) = kept.unwrap_or_default();
    let mut partial = Vec::new();
    let key = Finder::new(EDIT.as_bytes());
    let tail = From { log, at: start };
    let read = scan(tail, &key, chunk, |l, whole| {
        indexed(l, if whole { &mut rows } else { &mut partial });
    });
    let covered = start + read.whole;
    if read.to_end && (fresh || read.whole > STALE) {
        if let (Some(i), Some(tie)) = (&idx, Tie::of(log, covered)) {
            store(i, &tie, &rows);
        }
    }
    let mut out = Vec::new();
    matching(&rows, path, &mut out);
    matching(&partial, path, &mut out);
    out
}

#[cfg(test)]
mod tests;

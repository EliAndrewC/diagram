//! The Bash hooks' prefilters' read of the check state (feature 451 T508): whether `checks-open.json` holds one key, asked on every
//! Bash call by record-edit-hooks (`"plan_holds":` with a non-empty object after it) and checks-hooks (`"plan_snaps"` anywhere).
//!
//! WHY A STREAM AND NOT A STRING: each prefilter read the whole 2.6 MB state into one string to find one key - 2.7 ms and 641 page
//! faults - and record-edit-hooks then searched it with `split_once` (1.9 ms where `contains` takes 0.25 on the same bytes): 4.8 ms of
//! a 7.1 ms `PreToolUse` and 2.7 of a 4.7 ms `PostToolUse` on every Bash call, measured 2026-11-27
//! (`dev/measurements/2026-11-27/t507-part-cost/results.md`). The file is now read [`CHUNK`] bytes at a time into one reused buffer
//! and the key found by `memchr`'s `memmem` over the bytes. Priced against the other two routes on the same arms
//! (`dev/measurements/2026-11-27/t508-prefilter-stream/results.md`), this saved the most outside a hold, the case of nearly every
//! Bash call. The key is searched in the WHOLE file, never a prefix: the writer sorts the top-level keys, so `plan_holds` and
//! `plan_snaps` sit after `dispatches`, the bulk of the file (byte 1,999,829 of 2,618,222 on 2026-11-27), and a key's place moves
//! with every other key's size.
//!
//! THE ANSWER IS THE WHOLE-STRING READ'S on every file: the first `"plan_holds":` is the one tested, what follows it is trimmed as
//! `str::trim_start` trims, and every byte is checked to be UTF-8 as it is read, since `read_to_string` failed (no hold, no snapshot)
//! on a file with one bad byte anywhere. So the read stops early only on a no; a yes reads on to the end to check the rest. Not
//! checking it was measured to change an outcome: on a state with a bad byte, checks-hooks' `handle` then ran and wrote its empty
//! reading over the file (451 T508, `t508-nonutf8.txt`).

use std::io::Read;
use std::path::Path;

use memchr::memmem::Finder;

/// The bytes read at a time: a GUESS knob (451 T508), small enough to stay in cache, large enough that the read calls are few.
pub const CHUNK: usize = 64 * 1024;

/// What is asked of the text after the key: its UTF-8 prefix as read so far and whether the read is at its end; None reads more.
pub type Decide = dyn Fn(&str, bool) -> Option<bool>;

/// UTF-8 checked a piece at a time: the bytes of a character the last piece cut, held for the next.
#[derive(Default)]
struct Utf8 {
    open: Vec<u8>,
}

impl Utf8 {
    /// Whether `bytes`, after what came before, can still be UTF-8.
    fn feed(&mut self, mut bytes: &[u8]) -> bool {
        while !self.open.is_empty() {
            let Some((&b, rest)) = bytes.split_first() else {
                return true;
            };
            self.open.push(b);
            bytes = rest;
            match std::str::from_utf8(&self.open) {
                Ok(_) => self.open.clear(),
                Err(e) if e.error_len().is_some() => return false,
                Err(_) => {}
            }
        }
        match std::str::from_utf8(bytes) {
            Ok(_) => true,
            Err(e) if e.error_len().is_some() => false,
            Err(e) => {
                self.open = bytes[e.valid_up_to()..].to_vec();
                true
            }
        }
    }
}

/// Whether `r` is UTF-8, holds `needle` and `decide` says yes to the text after its first place; a read that fails is no.
pub fn after_first(r: &mut dyn Read, needle: &[u8], chunk: usize, decide: &Decide) -> bool {
    let finder = Finder::new(needle);
    let keep = needle.len().saturating_sub(1);
    let mut utf8 = Utf8::default();
    let mut buf: Vec<u8> = Vec::with_capacity(chunk + keep);
    loop {
        let Some(n) = more(r, &mut buf, chunk) else {
            return false;
        };
        if !utf8.feed(&buf[buf.len() - n..]) {
            return false;
        }
        if let Some(at) = finder.find(&buf) {
            let tail = buf.split_off(at + needle.len());
            return decided(r, tail, n < chunk, chunk, decide, &mut utf8);
        }
        if n < chunk {
            return false;
        }
        // the last `keep` bytes may open the key: a key cut by the chunk's edge is found whole on the next read
        buf.drain(..buf.len() - keep.min(buf.len()));
    }
}

/// Up to `chunk` more bytes appended to `buf`: how many, None where the read failed.
fn more(r: &mut dyn Read, buf: &mut Vec<u8>, chunk: usize) -> Option<usize> {
    r.take(chunk as u64).read_to_end(buf).ok()
}

/// `decide` asked of the text after the key, reading on until it answers; a yes then reads to the end, checking the rest.
fn decided(
    r: &mut dyn Read,
    mut tail: Vec<u8>,
    mut end: bool,
    chunk: usize,
    decide: &Decide,
    utf8: &mut Utf8,
) -> bool {
    loop {
        let valid = std::str::from_utf8(&tail).map_or_else(|e| e.valid_up_to(), str::len);
        if let Some(v) = decide(std::str::from_utf8(&tail[..valid]).unwrap_or_default(), end) {
            return v
                && (if end {
                    utf8.open.is_empty()
                } else {
                    rest_utf8(r, tail, chunk, utf8)
                });
        }
        if end {
            return false;
        }
        let held = tail.len();
        let Some(n) = more(r, &mut tail, chunk) else {
            return false;
        };
        if !utf8.feed(&tail[held..]) {
            return false;
        }
        end = n < chunk;
    }
}

/// Whether the rest of `r` is UTF-8, read through `buf`.
fn rest_utf8(r: &mut dyn Read, mut buf: Vec<u8>, chunk: usize, utf8: &mut Utf8) -> bool {
    loop {
        buf.clear();
        let Some(n) = more(r, &mut buf, chunk) else {
            return false;
        };
        if !utf8.feed(&buf) {
            return false;
        }
        if n < chunk {
            return utf8.open.is_empty();
        }
    }
}

/// After `"plan_holds":`, a non-empty object, as `hm_checks._handle` asks (the key stays, empty, after every hold).
#[must_use]
pub fn held_after(rest: &str, end: bool) -> Option<bool> {
    let r = rest.trim_start();
    if r.is_empty() {
        return end.then_some(false);
    }
    let Some(inner) = r.strip_prefix('{') else {
        return Some(false);
    };
    let inner = inner.trim_start();
    if inner.is_empty() {
        return end.then_some(true);
    }
    Some(!inner.starts_with('}'))
}

/// The snapshot prefilter's ask: the key alone.
#[expect(
    clippy::unnecessary_wraps,
    reason = "a `Decide`, whose answer is an Option"
)]
fn found(_: &str, _: bool) -> Option<bool> {
    Some(true)
}

/// Whether a plan review holds text in the state at `path`: its first `"plan_holds":` a non-empty object.
#[must_use]
pub fn holds(path: &Path) -> bool {
    std::fs::File::open(path)
        .is_ok_and(|mut f| after_first(&mut f, b"\"plan_holds\":", CHUNK, &held_after))
}

/// Whether the state at `path` holds a plan snapshot: `"plan_snaps"` anywhere in it.
#[must_use]
pub fn snaps(path: &Path) -> bool {
    std::fs::File::open(path)
        .is_ok_and(|mut f| after_first(&mut f, b"\"plan_snaps\"", CHUNK, &found))
}

#[cfg(test)]
mod tests;

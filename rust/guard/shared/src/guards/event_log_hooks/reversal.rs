//! The reversal tripwire's read of a feature's log (feature 451 T383, T392): whether an Edit puts back text an earlier Edit of the
//! same file replaced (A -> B -> A), asked on every Edit's `PreToolUse`.
//!
//! WHY A SCREEN BEFORE THE PARSE: the read parsed every line of the log as JSON to keep the few that are earlier Edits of this path -
//! 333 ms of every Edit's hook on 2026-11-26, the log 41.0 MB and 156,753 lines, growing 8.1 ms for each MB
//! (`dev/measurements/2026-11-26/edit-hook/t373-results.md`). Each line is now tested as text first ([`candidate`]) and only a
//! line that could be such an Edit is parsed; what a parsed line must say is unchanged, so the screen can only cost a line by
//! dropping it, never add one.
//!
//! THE TRIPWIRE MUST NOT MISS A REVERSAL, so the screen is a SUPERSET of the parse's lines by construction, not by trusting one
//! writer's spelling: JSON spells one string several ways (a quote as `\"` or `"`, `é` raw or as `é`), the parse reads them
//! all as equal, and a search for text does not. So the path's own text is searched for only where it has ONE spelling in every
//! writer that escapes no more than JSON asks or a non-ASCII character - a path of printable ASCII with no quote and no backslash
//! ([`needle`]). Any other path (a quote, a backslash, a control character, non-ASCII, or a path that is no string) is screened by
//! the Edit tool's name alone and its lines parsed as before.
//!
//! WHY THE LOG IS STREAMED AS BYTES (451 T392): after the screen, the read of the whole log into one string was most of what was
//! left - 78 to 81 ms of an Edit's hook, growing with the log. Priced 2026-11-27 on a copy of the 44.4 MB 451 log
//! (`dev/measurements/2026-11-27/edit-hook/t392-results.md`): the whole-file read alone took about 33 ms and its UTF-8 check only
//! a few more, while the same bytes read [`CHUNK`] at a time took about 12 ms - the cost is the one large buffer, not the decode. So
//! the log is read a chunk at a time, only its whole lines searched (a line is never cut by a chunk's edge), the rarer of the two
//! texts found by `memchr`'s `memmem` over the bytes, and only a line holding it decoded, screened and parsed as before. Every line is
//! still read: no second file or kept offset (the options priced against this) can drift from the log, so a line missed is
//! impossible by construction. A line that is not UTF-8 is passed over alone, where the whole-string read lost the log's every line.

use std::io::{ErrorKind, Read};
use std::path::Path;

use memchr::memmem::Finder;
use serde_json::Value;

use super::truthy;

/// The Edit tool's name as a line's JSON holds it, whatever the writer puts around the colon.
const EDIT: &str = "\"Edit\"";

/// The bytes read from the log at a time (a GUESS knob, 451 T392): 64, 256 and 1,024 KiB read the 44.4 MB log in 10.7 to 17.2 ms
/// alone, within the noise of one another, against 33 to 59 ms for the whole file at once, measured 2026-11-27
/// (`t392-pricing.tsv`); any size reads the same lines.
const CHUNK: usize = 256 * 1024;

/// The text every log line naming `path` holds, where the path has one JSON spelling; None where it may have several.
fn needle(path: &Value) -> Option<String> {
    let plain = |b: u8| (0x20..0x7f).contains(&b) && b != b'"' && b != b'\\';
    path.as_str()
        .filter(|p| p.bytes().all(plain))
        .map(|p| format!("\"{p}\""))
}

/// Whether a log line could be an Edit of the path whose [`needle`] this is: the screen, before any parse.
fn candidate(line: &str, needle: Option<&str>) -> bool {
    line.contains(EDIT) && needle.is_none_or(|n| line.contains(n))
}

/// What a read of the log keeps: the `old` digest of each earlier Edit of the path, and how many lines were parsed to find them.
struct Kept<'a> {
    path: &'a Value,
    needle: Option<String>,
    olds: Vec<Value>,
    parsed: usize,
}

impl Kept<'_> {
    /// One line of the log: decoded, screened and, if it passes, parsed as the read before the screen parsed every line.
    fn line(&mut self, bytes: &[u8]) {
        let Ok(l) = std::str::from_utf8(bytes) else {
            return;
        };
        if !candidate(l, self.needle.as_deref()) {
            return;
        }
        self.parsed += 1;
        let Ok(e) = serde_json::from_str::<Value>(l.trim()) else {
            return;
        };
        if e.get("ev") == Some(&Value::from("PreToolUse"))
            && e.get("tool") == Some(&Value::from("Edit"))
            && e.get("path") == Some(self.path)
        {
            self.olds.push(e.get("old").cloned().unwrap_or(Value::Null));
        }
    }

    /// Whole lines of the log (no line cut at either end): each line holding `key` handed to [`Kept::line`] once.
    fn lines(&mut self, key: &Finder, text: &[u8]) {
        let mut done = 0;
        for at in key.find_iter(text) {
            if at < done {
                continue;
            }
            let start = memchr::memrchr(b'\n', &text[..at]).map_or(0, |i| i + 1);
            done = memchr::memchr(b'\n', &text[at..]).map_or(text.len(), |i| at + i);
            self.line(&text[start..done]);
        }
    }
}

/// The text each earlier Edit of `path` replaced (its `old` digest), from a log read `chunk` bytes at a time, and how many lines were
/// parsed to find them. A read that fails ends it with what its whole lines held.
fn replaced(mut log: impl Read, path: &Value, chunk: usize) -> (Vec<Value>, usize) {
    let mut kept = Kept {
        path,
        needle: needle(path),
        olds: Vec::new(),
        parsed: 0,
    };
    // the rarer text of the two a candidate holds: the path's where it has one spelling, else the tool's
    let key = kept.needle.clone().unwrap_or_else(|| EDIT.to_owned());
    let key = Finder::new(key.as_bytes()).into_owned();
    let mut buf: Vec<u8> = Vec::new();
    loop {
        let held = buf.len();
        buf.resize(held + chunk, 0);
        let read = log.read(&mut buf[held..]);
        buf.truncate(held + *read.as_ref().unwrap_or(&0));
        match read {
            Ok(0) => {
                kept.lines(&key, &buf);
                break;
            }
            Ok(_) => {
                // the new bytes' last newline ends the whole lines held; what follows it waits for the next chunk
                if let Some(end) = memchr::memrchr(b'\n', &buf[held..]) {
                    kept.lines(&key, &buf[..held + end]);
                    buf.drain(..=held + end);
                }
            }
            Err(e) if e.kind() == ErrorKind::Interrupted => {}
            Err(_) => break,
        }
    }
    (kept.olds, kept.parsed)
}

/// Whether an Edit of `path` puts back text an earlier Edit of that file replaced (`hm_arbiter.reversal`).
pub(super) fn reversal(log: &Path, path: &Value, old: &Value, new: &Value) -> bool {
    truthy(new)
        && new != old
        && std::fs::File::open(log).is_ok_and(|f| replaced(f, path, CHUNK).0.contains(new))
}

#[cfg(test)]
mod tests;

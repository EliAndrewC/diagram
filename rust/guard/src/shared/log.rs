//! The guard log (`scripts/hooks/lib/guardlog.sh`'s `guard_log`): one JSON file a firing, `<UTC to the microsecond>-<pid>.json` in
//! `GUARD_LOG_DIR` (else `~/.claude/guard-log`), written to a temporary beside it and renamed into place, its fields those
//! `make audit` and `make guard-log` read. A write that fails is silent: an entry must never cost the guard its answer.
//!
//! ONE WRITER FOR THE GUARDS AND THE SHELL (feature 449 T143, `ask:449-phase4-slices` Q12): `guard_log`'s inline Python is this module's
//! [`write_entry`], which the shell reaches through `l7r-gate log guard`, so an entry is the same text whoever writes it - Python's
//! `json.dumps(indent=2)`, every non-ASCII character escaped, each field `payload.get(k) or ""` as the Python wrote it.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::{json, Map, Value};

use crate::shared::pyjson::{dumps, truthy};

/// One firing: the guard, its event (`blocked`, `escaped`, `rewrote`, ...), the detail (cut at 200 characters), the rule (the event
/// where none is given), the guard's own decision inputs, the hook input and the session's name and id.
pub struct Entry<'a> {
    pub guard: &'a str,
    pub event: &'a str,
    pub detail: &'a str,
    pub rule: &'a str,
    pub context: Option<Value>,
    pub input: &'a Value,
    pub session_name: &'a str,
}

/// The log's directory: `GUARD_LOG_DIR`, else `~/.claude/guard-log`.
#[must_use]
pub fn dir() -> PathBuf {
    dir_from(
        std::env::var("GUARD_LOG_DIR").ok(),
        &std::env::var("HOME").unwrap_or_default(),
    )
}

/// The log's directory given the environment's `GUARD_LOG_DIR` and `HOME`, read as the shell's `${GUARD_LOG_DIR:-$HOME/.claude/guard-log}`
/// reads them: an empty seam is no seam, so an entry never lands in the working directory (feature 449 T143).
fn dir_from(seam: Option<String>, home: &str) -> PathBuf {
    match seam.filter(|d| !d.is_empty()) {
        Some(d) => PathBuf::from(d),
        None => PathBuf::from(format!("{home}/.claude/guard-log")),
    }
}

/// The civil date and time of `secs` past the epoch, UTC: (year, month, day, hour, minute, second).
#[must_use]
pub fn civil(secs: u64) -> (i64, u32, u32, u64, u64, u64) {
    let days = i64::try_from(secs / 86_400).unwrap_or(0);
    let rem = secs % 86_400;
    // days to a civil date (Howard Hinnant's algorithm)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let day_of_era = z.rem_euclid(146_097);
    let year_of_era =
        (day_of_era - day_of_era / 1460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let mp = (5 * day_of_year + 2) / 153;
    let d = u32::try_from(day_of_year - (153 * mp + 2) / 5 + 1).unwrap_or(1);
    let m = u32::try_from(if mp < 10 { mp + 3 } else { mp - 9 }).unwrap_or(1);
    let y = year_of_era + era * 400 + i64::from(m <= 2);
    (y, m, d, rem / 3600, rem % 3600 / 60, rem % 60)
}

/// Write `e` into `dir` at `now`; the path written, or None where the write failed.
#[must_use]
pub fn write_at(dir: &Path, e: &Entry, now: SystemTime) -> Option<PathBuf> {
    write_entry(dir, e, "", now)
}

/// Write `e` into `dir` at `now`, `sid` the session the caller's environment names where the input names none (the shell's
/// `${SID:-unknown}`; "" for a guard) - `guard_log`'s Python, field for field (feature 449 T143): the input read as a dict only when it
/// is one, `tool_input` likewise, each field `payload.get(k) or ""` with a value that is not a string written as it is, the session
/// `payload.get("session_id") or sid or "unknown"` (`sid` neither `unknown` nor `nosession`), the name `name or session`.
#[must_use]
pub fn write_entry(dir: &Path, e: &Entry, sid: &str, now: SystemTime) -> Option<PathBuf> {
    let since = now.duration_since(UNIX_EPOCH).ok()?;
    let (year, month, day, hour, min, sec) = civil(since.as_secs());
    let empty = Value::Object(Map::new());
    let payload = if e.input.is_object() { e.input } else { &empty };
    let given = |v: Option<&Value>| v.filter(|v| truthy(v)).cloned();
    let field = |k: &str| given(payload.get(k)).unwrap_or_else(|| json!(""));
    let ti = payload
        .get("tool_input")
        .filter(|v| v.is_object())
        .unwrap_or(&empty);
    let command = given(ti.get("command"))
        .or_else(|| given(ti.get("file_path")))
        .unwrap_or_else(|| json!(""));
    let session = given(payload.get("session_id"))
        .or_else(|| (!matches!(sid, "" | "unknown" | "nosession")).then(|| json!(sid)))
        .unwrap_or_else(|| json!("unknown"));
    let name = if e.session_name.is_empty() {
        session.clone()
    } else {
        json!(e.session_name)
    };
    let entry = json!({
        "utc": format!("{year:04}-{month:02}-{day:02}T{hour:02}:{min:02}:{sec:02}Z"), "guard": e.guard, "event": e.event,
        "rule": if e.rule.is_empty() { e.event } else { e.rule }, "session": session, "session_name": name, "cwd": field("cwd"),
        "tool": field("tool_name"), "transcript": field("transcript_path"), "detail": e.detail.chars().take(200).collect::<String>(),
        "command": command, "context": e.context.clone().unwrap_or(Value::Null),
    });
    place(dir, &python_surrogates(&dumps(&entry, Some(2), true)), now)
}

/// The first stand-in of [`surrogate_escaped`]: the byte `0x80` is `U+10FF80`, `0xff` is `U+10FFFF`.
const STAND_IN: u32 = 0x0010_FF00;

/// Bytes as Python decodes an argument under this container's `C.UTF-8` locale, with `surrogateescape` (feature 449 T143): each byte UTF-8
/// cannot take is one character, here the stand-in `U+10FF00` plus the byte, which [`write_entry`] writes as the `\udcXX` Python wrote.
/// A gate's detail is `head -c 400` of its output, which can cut a character in two.
#[must_use]
pub fn surrogate_escaped(raw: &[u8]) -> String {
    let mut out = String::with_capacity(raw.len());
    let mut rest = raw;
    while !rest.is_empty() {
        match std::str::from_utf8(rest) {
            Ok(text) => {
                out += text;
                break;
            }
            Err(e) => {
                let (good, bad) = rest.split_at(e.valid_up_to());
                out += std::str::from_utf8(good).unwrap_or_default();
                let n = e.error_len().unwrap_or(bad.len());
                out.extend(
                    bad[..n]
                        .iter()
                        .filter_map(|b| char::from_u32(STAND_IN + u32::from(*b))),
                );
                rest = &bad[n..];
            }
        }
    }
    out
}

/// JSON text with each stand-in's escape (`\udbff\udfXX`, the pair `ensure_ascii` writes for `U+10FFXX`) written as the lone surrogate
/// `\udcXX` Python's `json.dumps` wrote for a `surrogateescape` byte. It walks the escapes in order, so an escaped backslash followed by
/// the same letters is left alone.
fn python_surrogates(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut rest = text;
    while let Some(at) = rest.find('\\') {
        out += &rest[..at];
        let tail = &rest[at..];
        let byte = tail
            .strip_prefix("\\udbff\\udf")
            .and_then(|h| h.get(..2))
            .filter(|h| h.as_bytes()[0] >= b'8');
        if let Some(hex) = byte {
            out += "\\udc";
            out += hex;
            rest = &tail[12..];
        } else {
            let step = tail.chars().take(2).map(char::len_utf8).sum::<usize>();
            out += &tail[..step];
            rest = &tail[step..];
        }
    }
    out + rest
}

/// One entry's text put into `dir` at `now`: `<UTC to the microsecond>-<pid>.json`, written to a temporary beside it and renamed into
/// place; the path, or None where a step failed. The one writer of the file's name and its rename, which the gate's `escape take`
/// (`escape_log.py`'s port, feature 449 T137) shares with [`write_at`].
#[must_use]
pub fn place(dir: &Path, text: &str, now: SystemTime) -> Option<PathBuf> {
    let since = now.duration_since(UNIX_EPOCH).ok()?;
    let (year, month, day, hour, min, sec) = civil(since.as_secs());
    let path = dir.join(format!(
        "{year:04}{month:02}{day:02}T{hour:02}{min:02}{sec:02}{:06}-{}.json",
        since.subsec_micros(),
        std::process::id()
    ));
    std::fs::create_dir_all(dir).ok()?;
    let tmp = path.with_extension("json.tmp");
    std::fs::write(&tmp, text).ok()?;
    std::fs::rename(&tmp, &path).ok()?;
    Some(path)
}

/// Write `e` into the log now (`guard_log`).
#[must_use]
pub fn write(e: &Entry) -> Option<PathBuf> {
    write_at(&dir(), e, SystemTime::now())
}

/// Record a firing of `guard` on this hook input, the session's clone name beside it (`guard_log <guard> <event> <detail> <rule>`).
pub fn fire(
    guard: &str,
    event: &str,
    detail: &str,
    rule: &str,
    input: &Value,
    session: &crate::shared::session::Session,
) {
    let _ = write(&Entry {
        guard,
        event,
        detail,
        rule,
        context: None,
        input,
        session_name: &session.name(),
    });
}

/// The tests' guard log: one directory for the whole crate, set once before any test logs - each module setting its own raced
/// another's read of the variable (T009, 2026-11-08).
#[cfg(test)]
pub(crate) fn quiet() {
    static ONCE: std::sync::Once = std::sync::Once::new();
    // the process's shared directory (`beside_binary`): nothing set once for the whole process is dropped to remove it, so it lives in the
    // run's own temp directory, which `make rust-test` removes whole when the run ends (feature 449 T101)
    ONCE.call_once(|| {
        std::env::set_var(
            "GUARD_LOG_DIR",
            crate::shared::tempdir::beside_binary("guard-tests-log"),
        );
    });
}

#[cfg(test)]
mod tests;

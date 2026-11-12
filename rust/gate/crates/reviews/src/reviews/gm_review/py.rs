//! What `scripts/gm_review.py` took from Python itself, read as Python reads it (feature 449 T91, `ask:449-T82-claims`): a row's
//! `in` and `.get`, a value's truth and `str()`, `int()` on a row number, a slice by code points, `textwrap.wrap` with its hyphen
//! rule, `shutil.get_terminal_size`'s columns, and the message a broken file's bytes raise. Each answers as the Python did, so the
//! port's output and its refusals are the same bytes (FR-002).

use std::fmt;
use std::io::IsTerminal;
use std::path::Path;
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{is_space, repr, strip};
use serde_json::Value;

/// How the Python left `main`: a `ValueError` it caught (`gm-review: refused - ...`), a `SystemExit` with its text, or an uncaught raise.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Raised {
    Refused(String),
    Exit(String),
    Trace(String),
}

impl fmt::Display for Raised {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Refused(m) | Self::Exit(m) | Self::Trace(m) => f.write_str(m),
        }
    }
}

pub type R<T> = Result<T, Raised>;

/// `key in r`: a dict's key, a list's element, a string's substring; any other value raised `TypeError`.
pub(super) fn has(r: &Value, key: &str) -> R<bool> {
    match r {
        Value::Object(m) => Ok(m.contains_key(key)),
        Value::Array(items) => Ok(items.iter().any(|v| v.as_str() == Some(key))),
        Value::String(s) => Ok(s.contains(key)),
        other => Err(Raised::Trace(format!(
            "TypeError: argument of type '{}' is not a container or iterable",
            type_name(other)
        ))),
    }
}

/// `r.get(key)`: only a dict has one; any other row raised `AttributeError`.
pub(super) fn get<'a>(r: &'a Value, key: &str) -> R<Option<&'a Value>> {
    match r {
        Value::Object(m) => Ok(m.get(key)),
        other => Err(Raised::Trace(format!(
            "AttributeError: '{}' object has no attribute 'get'",
            type_name(other)
        ))),
    }
}

/// `str(r.get(key, ""))`.
pub(super) fn text(r: &Value, key: &str) -> R<String> {
    Ok(get(r, key)?.map_or_else(String::new, py_str))
}

/// `str(value)`.
#[must_use]
pub(super) fn py_str(v: &Value) -> String {
    l7r_guard::shared::pyjson::py_str(v)
}

/// The type name Python's message gives.
pub(super) fn type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// A value's truth: `None`, `False`, zero and an empty string, list or dict are false; a missing key reads as false.
#[must_use]
pub(super) fn truthy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null | Value::Bool(false)) => false,
        Some(Value::Number(n)) => n.as_f64().is_some_and(|f| f != 0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(m)) => !m.is_empty(),
        Some(Value::Bool(true)) => true,
    }
}

/// `int(s)` in base 10: Python's whitespace around it, a sign, single underscores between digits; its `ValueError` otherwise.
pub(super) fn py_int(s: &str) -> R<i128> {
    let bad = || {
        Raised::Refused(format!(
            "invalid literal for int() with base 10: {}",
            repr(s)
        ))
    };
    let body = strip(s);
    let (neg, digits) = match body.as_bytes().first() {
        Some(b'-') => (true, &body[1..]),
        Some(b'+') => (false, &body[1..]),
        _ => (false, body),
    };
    if digits.is_empty()
        || digits.starts_with('_')
        || digits.ends_with('_')
        || digits.contains("__")
        || !digits.chars().all(|c| c.is_ascii_digit() || c == '_')
    {
        return Err(bad());
    }
    let n: i128 = digits.replace('_', "").parse().map_err(|_| bad())?;
    Ok(if neg { -n } else { n })
}

/// `s[:n]` by code points, a negative `n` counting from the end.
#[must_use]
pub(super) fn head(s: &str, n: i128) -> String {
    let len = i128::try_from(s.chars().count()).unwrap_or(i128::MAX);
    let take = if n < 0 { (len + n).max(0) } else { n.min(len) };
    s.chars().take(usize::try_from(take).unwrap_or(0)).collect()
}

/// `s.rstrip()`.
#[must_use]
pub(super) fn rstrip(s: &str) -> &str {
    s.trim_end_matches(is_space)
}

/// The length Python's `len` gives a string: code points.
#[must_use]
pub(super) fn len(s: &str) -> usize {
    s.chars().count()
}

/// A file read as `Path.read_text(encoding="utf-8")` reads it: its bytes decoded (bad bytes raise `UnicodeDecodeError`, a
/// `ValueError` the command caught), `\r\n` and `\r` read as `\n`.
pub(super) fn read_text(path: &Path) -> R<String> {
    let bytes = std::fs::read(path)
        .map_err(|e| Raised::Trace(format!("OSError: {e}: {}", path.display())))?;
    let t = String::from_utf8(bytes)
        .map_err(|e| Raised::Refused(decode_error(e.as_bytes(), &e.utf8_error())))?;
    Ok(crate::record::repo::universal(&t))
}

/// `UnicodeDecodeError`'s text for the first bad bytes of `bytes`.
#[must_use]
pub(super) fn decode_error(bytes: &[u8], e: &std::str::Utf8Error) -> String {
    let at = e.valid_up_to();
    let first = bytes[at];
    let (count, why) = match e.error_len() {
        None => (bytes.len() - at, "unexpected end of data"),
        Some(n) if matches!(first, 0x80..=0xc1 | 0xf5..=0xff) => (n, "invalid start byte"),
        Some(n) => (n, "invalid continuation byte"),
    };
    if count == 1 {
        format!("'utf-8' codec can't decode byte 0x{first:02x} in position {at}: {why}")
    } else {
        format!(
            "'utf-8' codec can't decode bytes in position {at}-{}: {why}",
            at + count - 1
        )
    }
}

/// A write that raised: the command's uncaught `OSError`.
pub(super) fn wrote(path: &Path, done: std::io::Result<()>) -> R<()> {
    done.map_err(|e| Raised::Trace(format!("OSError: {e}: {}", path.display())))
}

/// `shutil.get_terminal_size((fallback, 24)).columns`: `COLUMNS` when it is a positive number, else the width of the terminal stdout
/// is, else `fallback`. `probe` is asked only when stdout is a terminal.
pub(super) fn columns_of(
    env: Option<&str>,
    tty: bool,
    probe: fn() -> Option<usize>,
    fallback: usize,
) -> usize {
    let given = env.and_then(|c| py_int(c).ok()).unwrap_or(0);
    if given > 0 {
        return usize::try_from(given).unwrap_or(fallback);
    }
    tty.then(probe)
        .flatten()
        .filter(|c| *c > 0)
        .unwrap_or(fallback)
}

/// The columns of this process's stdout: `stty size` asked of the terminal stdout is (`os.get_terminal_size(stdout)`).
#[must_use]
pub(super) fn stdout_columns() -> Option<usize> {
    stty_columns(std::fs::File::open("/proc/self/fd/1").ok()?)
}

/// `stty size`'s second number, its input the terminal asked of; None where it is no terminal.
#[must_use]
pub(super) fn stty_columns(input: std::fs::File) -> Option<usize> {
    let o = Command::new("stty")
        .arg("size")
        .stdin(input)
        .stderr(Stdio::null())
        .output()
        .ok()?;
    second_number(&String::from_utf8_lossy(&o.stdout))
}

/// The columns in what `stty size` printed (`<rows> <columns>`).
pub(super) fn second_number(said: &str) -> Option<usize> {
    said.split_whitespace().nth(1)?.parse().ok()
}

/// This process's own columns, `fallback` when stdout is no terminal and `COLUMNS` is unset.
#[must_use]
pub(super) fn columns(fallback: usize) -> usize {
    columns_of(
        std::env::var("COLUMNS").ok().as_deref(),
        std::io::stdout().is_terminal(),
        stdout_columns,
        fallback,
    )
}

/// `textwrap.TextWrapper.wordsep_re` (Python 3.14), `break_on_hyphens`: whitespace, an em-dash between words, or a word whose
/// hyphen between letters ends a chunk. The text it splits holds no whitespace but spaces (`_munge_whitespace`).
static WORDSEP: LazyLock<Regex> = LazyLock::new(|| {
    let (ws, nws, wp, lt) = (
        r"[\t\n\x0b\x0c\r ]",
        r"[^\t\n\x0b\x0c\r ]",
        r#"[\w!"'&.,?]"#,
        r"[^\d\W]",
    );
    Regex::new(&format!(
        r"({ws}+|(?<={wp})-{{2,}}(?=\w)|{nws}+?(?:-(?:(?<={lt}{lt}-)|(?<={lt}-{lt}-))(?={lt}-?{lt})|(?={ws}|\z)|(?<={wp})(?=-{{2,}}\w)))"
    ))
    .unwrap_or_else(|_| unreachable!("a fixed pattern"))
});

/// `text.expandtabs(8)`, then every one of `textwrap`'s six whitespace characters a space.
fn munge(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut col = 0usize;
    for c in text.chars() {
        match c {
            '\t' => {
                let n = 8 - col % 8;
                out.extend(std::iter::repeat_n(' ', n));
                col += n;
            }
            '\n' | '\r' => {
                out.push(' ');
                col = 0;
            }
            '\x0b' | '\x0c' => {
                out.push(' ');
                col += 1;
            }
            other => {
                out.push(other);
                col += 1;
            }
        }
    }
    out
}

/// `textwrap.wrap(text, width, initial_indent=, subsequent_indent=)` with every other option at its default. Its `ValueError` on a width
/// under one is not kept: every width here is one or more (`columns_of` answers a positive number, the listing at least 80).
pub(super) fn wrap(text: &str, width: i128, initial: &str, subsequent: &str) -> Vec<String> {
    let text = munge(text);
    let mut chunks: Vec<String> = Vec::new();
    let mut at = 0;
    for m in WORDSEP.find_iter(&text).flatten() {
        chunks.push(text[at..m.start()].to_owned());
        chunks.push(m.as_str().to_owned());
        at = m.end();
    }
    chunks.push(text[at..].to_owned());
    chunks.retain(|c| !c.is_empty());
    chunks.reverse();
    wrap_chunks(chunks, width, initial, subsequent)
}

fn wide(n: usize) -> i128 {
    i128::try_from(n).unwrap_or(i128::MAX)
}

/// `_wrap_chunks`, with `max_lines` unset.
fn wrap_chunks(
    mut chunks: Vec<String>,
    width: i128,
    initial: &str,
    subsequent: &str,
) -> Vec<String> {
    let mut lines: Vec<String> = Vec::new();
    while !chunks.is_empty() {
        let mut cur: Vec<String> = Vec::new();
        let mut cur_len: i128 = 0;
        let indent = if lines.is_empty() {
            initial
        } else {
            subsequent
        };
        let room = width - wide(len(indent));
        if !lines.is_empty() && chunks.last().is_some_and(|c| strip(c).is_empty()) {
            chunks.pop();
        }
        while let Some(c) = chunks.last() {
            let l = wide(len(c));
            if cur_len + l > room {
                break;
            }
            cur_len += l;
            cur.extend(chunks.pop());
        }
        if chunks.last().is_some_and(|c| wide(len(c)) > room) {
            long_word(&mut chunks, &mut cur, cur_len, room);
        }
        if cur.last().is_some_and(|c| strip(c).is_empty()) {
            cur.pop();
        }
        if !cur.is_empty() {
            lines.push(format!("{indent}{}", cur.concat()));
        }
    }
    lines
}

/// `_handle_long_word`: a chunk longer than a line broken where it fits, after a hyphen where one falls inside. Its last branch (an
/// empty line taking the whole chunk) needs no space left with nothing on the line, which `room < 1` turning into one space rules out.
fn long_word(chunks: &mut Vec<String>, cur: &mut Vec<String>, cur_len: i128, room: i128) {
    let space_left = if room < 1 { 1 } else { room - cur_len };
    if space_left > 0 {
        let chunk: Vec<char> = chunks.pop().unwrap_or_default().chars().collect();
        let left = usize::try_from(space_left).unwrap_or(usize::MAX);
        let mut end = left.min(chunk.len());
        if chunk.len() > left {
            if let Some(h) = chunk[..left].iter().rposition(|c| *c == '-') {
                if h > 0 && chunk[..h].iter().any(|c| *c != '-') {
                    end = h + 1;
                }
            }
        }
        cur.push(chunk[..end].iter().collect());
        chunks.push(chunk[end..].iter().collect());
    }
}

#[cfg(test)]
mod tests;
